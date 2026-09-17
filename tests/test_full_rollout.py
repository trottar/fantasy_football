import numpy as np
import pandas as pd

from src.draft_state import DraftState
from src.full_rollout import (
    PreparedRollout,
    _starter_and_bench_utility,
    evaluate_candidates_full_rollout,
)


def _league():
    return {
        "teams": 2,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1,"BENCH":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3},
    }


def _model():
    return {
        "draft_value": {
            "expected_rostered_counts": {"QB":4,"RB":12,"WR":12,"TE":4},
            "scarcity_lookahead_players": 3,
        },
        "live_draft": {
            "random_seed": 7,
            "scarcity_weight": 0.25,
            "opponent_need_strength": 0.35,
        },
        "roster_utility": {
            "bench_option_weight": 0.25,
            "bench_depth_decay": 0.60,
            "candidate_floor_per_position": 2,
        },
        "full_rollout": {
            "fast_simulations": 12,
            "deep_simulations": 6,
            "candidate_limit": 6,
            "policy_candidates_per_position": 2,
            "policy_urgency_weight": 0.18,
            "bench_coverage_weight": 0.35,
            "bench_depth_decay": 0.55,
            "starter_risk_penalty": 0.0,
            "objective_sd_penalty": 0.08,
            "deep_market_queue_lookahead": 6,
            "deep_queue_temperature": 4.0,
        },
    }


def _board(n_per_pos=12):
    rows = []
    pid = 1
    for pos, base in [("QB",22),("RB",18),("WR",17),("TE",13)]:
        for i in range(n_per_pos):
            rows.append({
                "espn_id": pid,
                "name": f"{pos}{i+1}",
                "position": pos,
                "nfl_team": "X",
                "draft_eligible": True,
                "latent_mean_ppg": base - i*0.35,
                "latent_mean_sd_ppg": 1.5,
                "espn_adp": float(pid),
                "espn_rank": float(pid),
                "market_pick_mean": float(pid),
                "market_pick_sigma": 5.0,
                "tier": 1,
            })
            pid += 1
    return pd.DataFrame(rows)


def test_final_bench_coverage_prefers_wr_depth_to_third_te_at_equal_vorp():
    # Same starting lineup and equal bench-player VORP. WR depth should carry
    # more final-roster utility than TE depth because this league starts two WR
    # plus FLEX but only one TE plus FLEX share.
    positions = np.array(["QB","RB","RB","WR","WR","TE","RB","TE","TE","WR","WR"])
    vorp = np.array([8,10,9,9,8,6,7,5,4,5,4], dtype=float)
    n = len(positions)
    prep = PreparedRollout(
        ids=np.arange(1,n+1),
        names=np.array([f"P{i}" for i in range(n)]),
        positions=positions,
        pos_codes=np.array([{"QB":0,"RB":1,"WR":2,"TE":3}[p] for p in positions]),
        ppg=vorp + 10.0,
        sd=np.zeros(n),
        vorp=vorp,
        means=np.arange(1,n+1,dtype=float),
        sigmas=np.ones(n)*4,
        adp=np.arange(1,n+1,dtype=float),
        eligible=np.ones(n,dtype=bool),
        id_to_index={i+1:i for i in range(n)},
        replacement={"QB":10,"RB":10,"WR":10,"TE":10},
    )
    model = _model()
    league = _league()

    # Base 7 starters, then compare two TE depth slots vs two WR depth slots.
    base = list(range(7))
    te_roster = base + [7,8]
    wr_roster = base + [9,10]
    te_total = _starter_and_bench_utility(prep, te_roster, league, model)[0]
    wr_total = _starter_and_bench_utility(prep, wr_roster, league, model)[0]
    assert wr_total > te_total


def test_full_rollout_returns_final_roster_fields_and_is_reproducible():
    state = DraftState(2, 8, 1)  # user is on pick 1
    board = _board()
    out1 = evaluate_candidates_full_rollout(
        board, state, _league(), _model(),
        simulations=8, seed=11, candidate_limit=4, deep=False,
    )
    out2 = evaluate_candidates_full_rollout(
        board, state, _league(), _model(),
        simulations=8, seed=11, candidate_limit=4, deep=False,
    )
    assert len(out1) == 4
    for col in [
        "final_roster_utility_mean", "final_roster_utility_sd",
        "final_starter_value_mean", "final_bench_value_mean",
        "expected_final_QB", "expected_final_RB",
        "expected_final_WR", "expected_final_TE",
    ]:
        assert col in out1.columns
        assert out1[col].notna().all()
    assert set(out1["engine"]) == {"FAST-FULL"}
    assert out1["name"].tolist() == out2["name"].tolist()
    np.testing.assert_allclose(out1["mc_objective"], out2["mc_objective"])


def test_deep_full_uses_same_final_roster_objective():
    state = DraftState(2, 8, 1)
    out = evaluate_candidates_full_rollout(
        _board(), state, _league(), _model(),
        simulations=4, seed=13, candidate_limit=4, deep=True,
    )
    assert len(out) == 4
    assert set(out["engine"]) == {"DEEP-FULL"}
    assert out["final_roster_utility_mean"].notna().all()


def test_full_rollout_can_reuse_persisted_market_order_ids():
    state = DraftState(2, 8, 1)
    board = _board()
    base, scenario_ids = evaluate_candidates_full_rollout(
        board, state, _league(), _model(),
        simulations=4, seed=21, candidate_limit=4, deep=True,
        return_scenarios=True,
    )
    reused = evaluate_candidates_full_rollout(
        board, state, _league(), _model(),
        simulations=4, seed=99, candidate_limit=4, deep=False,
        market_order_ids=scenario_ids,
    )
    assert len(base) == 4
    assert scenario_ids.shape[0] == 4
    assert len(reused) == 4
    assert (reused["simulations"] == 4).all()
