import json

import numpy as np
import pandas as pd

from src.draft_state import DraftState
from src.fast_recommend import (
    evaluate_candidates_fast,
    sample_conditional_draft_times,
    turn_geometry,
)


def _league():
    return {
        "teams": 12,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3},
    }


def _model():
    return {
        "draft_value": {
            "expected_rostered_counts": {"QB": 18, "RB": 60, "WR": 60, "TE": 18},
            "scarcity_lookahead_players": 5,
        },
        "live_draft": {
            "simulations": 4000,
            "random_seed": 20260830,
            "candidate_limit": 20,
            "opponent_need_strength": 0.35,
            "market_hazard_floor": 1e-8,
            "replacement_weight": 1.0,
            "scarcity_weight": 0.25,
            "survival_option_weight": 0.35,
            "risk_penalty": 0.1,
        },
        "fast_engine": {
            "candidate_limit": 8,
            "long_simulations": 100,
        },
    }


def _board(n=120):
    rows = []
    positions = ["RB", "WR", "TE", "QB"]
    for i in range(n):
        pos = positions[i % 4]
        rows.append({
            "espn_id": 10000 + i,
            "name": f"{pos}{i}",
            "position": pos,
            "nfl_team": "PIT",
            "draft_eligible": True,
            "latent_mean_ppg": 24.0 - 0.05 * i + (1.5 if pos == "QB" else 0.0),
            "latent_mean_sd_ppg": 1.5,
            "espn_adp": 1.0 + i,
            "espn_rank": 1.0 + i,
            "market_pick_mean": 1.0 + i,
            "market_pick_sigma": 5.0,
            "tier": 1,
        })
    return pd.DataFrame(rows)


def _state_at_pick(pick):
    s = DraftState(12, 16, 2)
    positions = ["RB", "WR", "TE", "QB"]
    for i in range(pick - 1):
        pos = positions[i % 4]
        s.record_pick(str(-i - 1), f"Taken{i}", pos, "X", espn_id=-i - 1)
    return s


def test_short_turn_geometry_and_engine():
    state = _state_at_pick(71)
    geom = turn_geometry(state)
    assert geom.opponent_picks == (72, 73)
    assert geom.is_short

    out = evaluate_candidates_fast(
        _board(), state, _league(), _model(),
        simulations=100, candidate_limit=6, seed=7,
    )
    assert len(out) == 6
    assert set(out["engine"]) == {"SHORT-EXACT+FULL"}
    assert (out["simulations"] == 100).all()
    assert out["mc_objective"].notna().all()
    assert out["final_roster_utility_mean"].notna().all()
    assert out["p_most_common_best_next"].between(0, 1).all()
    assert "contingency_1_name" in out.columns


def test_long_turn_uses_vectorized_market_engine():
    state = _state_at_pick(50)
    geom = turn_geometry(state)
    assert geom.gap == 20
    assert not geom.is_short

    out1 = evaluate_candidates_fast(
        _board(), state, _league(), _model(),
        simulations=80, candidate_limit=5, seed=11,
    )
    out2 = evaluate_candidates_fast(
        _board(), state, _league(), _model(),
        simulations=80, candidate_limit=5, seed=11,
    )
    assert set(out1["engine"]) == {"FAST-FULL"}
    assert (out1["simulations"] == 80).all()
    assert out1["name"].tolist() == out2["name"].tolist()
    np.testing.assert_allclose(out1["mc_objective"], out2["mc_objective"])


def test_conditional_draft_time_samples_respect_current_pick():
    rng = np.random.default_rng(3)
    means = np.array([5.0, 50.0, 100.0])
    sigmas = np.array([4.0, 8.0, 12.0])
    samples = sample_conditional_draft_times(
        rng, means, sigmas, current_pick=71, simulations=500
    )
    assert samples.shape == (500, 3)
    assert np.all(samples >= 70.5 - 1e-8)


def test_fast_labels_conditioned_deep_bank_scenarios():
    state = DraftState(12, 16, 2)
    # Advance to user pick 2 while keeping the synthetic board untouched.
    state.record_pick("-1", "Taken", "RB", "X", espn_id=-1)
    board = _board()
    # Deterministic full player-ID order, repeated as four posterior particles.
    ids = board["espn_id"].astype(int).to_numpy()
    market_order_ids = np.stack([ids, np.roll(ids, 1), np.roll(ids, 2), np.roll(ids, 3)])
    out = evaluate_candidates_fast(
        board, state, _league(), _model(),
        simulations=4, candidate_limit=4, seed=9,
        market_order_ids=market_order_ids,
        bank_info={
            "particles": 160, "ess": 121.0, "ess_fraction": 121/160,
            "anchor_pick": 1, "conditioned_through": 1,
            "selected_branch_name": None, "degraded": False,
            "fresh_fraction": 0.25,
        },
    )
    assert len(out) == 4
    assert all("CONDITIONED" in x for x in out["engine"])
    assert (out["deep_bank_particles"] == 160).all()
    assert (out["deep_bank_ess"] == 121.0).all()
