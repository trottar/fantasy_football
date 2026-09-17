import numpy as np
import pandas as pd

from src.draft_state import DraftState
from src.forecast import (
    forecast_next_user_pick_conditioned,
    forecast_next_user_pick_fast,
    forecast_next_user_pick_deep,
    forecast_next_user_pick_deep_conditioned,
    next_user_pick_from_state,
)


def _board(n=40):
    positions = ["RB", "WR", "TE", "QB"]
    rows = []
    for i in range(n):
        pos = positions[i % len(positions)]
        rows.append({
            "espn_id": i + 1,
            "name": f"P{i+1}",
            "position": pos,
            "nfl_team": "PIT",
            "draft_eligible": True,
            "latent_mean_ppg": 24.0 - 0.2 * i,
            "latent_mean_sd_ppg": 1.5,
            "espn_adp": float(i + 1),
            "espn_rank": float(i + 1),
            "market_pick_mean": float(i + 1),
            "market_pick_sigma": 4.0,
            "tier": 1,
        })
    return pd.DataFrame(rows)


def _league():
    return {
        "teams": 12,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3},
    }


def _model():
    return {
        "draft_value": {
            "expected_rostered_counts": {"QB":18,"RB":60,"WR":60,"TE":18},
            "scarcity_lookahead_players": 5,
        },
        "live_draft": {
            "random_seed": 123,
            "scarcity_weight": 0.25,
            "opponent_need_strength": 0.35,
            "market_hazard_floor": 1e-8,
        },
    }


def _off_turn_state():
    # Pick 1 is recorded. Pick 2 belongs to user slot 2, so record it too.
    # State is now at pick 3, with next user pick 23.
    s = DraftState(12, 4, 2)
    s.record_pick("9001", "Pick1", "RB", "DET", espn_id=9001)
    s.record_pick("9002", "UserPick2", "WR", "DET", espn_id=9002)
    return s


def test_next_user_pick_off_turn():
    s = _off_turn_state()
    assert s.next_overall == 3
    assert next_user_pick_from_state(s) == 23


def test_fast_forecast_runs_between_user_turns():
    out = forecast_next_user_pick_fast(
        _board(), _off_turn_state(), _league(), _model(),
        simulations=200, seed=1, candidate_limit=8,
    )
    assert len(out) == 8
    assert set(out["analysis_mode"]) == {"forecast"}
    assert set(out["target_pick"]) == {23}
    assert ((out["p_available_target"] >= 0) & (out["p_available_target"] <= 1)).all()
    assert ((out["p_best_target"] >= 0) & (out["p_best_target"] <= 1)).all()


def test_deep_forecast_runs_between_user_turns():
    out = forecast_next_user_pick_deep(
        _board(), _off_turn_state(), _league(), _model(),
        simulations=5, seed=2, candidate_limit=6,
    )
    assert len(out) == 6
    assert set(out["analysis_mode"]) == {"forecast"}
    assert set(out["engine"]) == {"DEEP-FORECAST"}
    assert set(out["target_pick"]) == {23}


def test_short_horizon_fast_forecast():
    # Construct state at pick 24; user next picks 26.
    s = DraftState(12, 4, 2)
    for i in range(23):
        s.record_pick(str(1000+i), f"D{i}", "RB" if i % 2 else "WR", "X", espn_id=1000+i)
    assert s.next_overall == 24
    assert next_user_pick_from_state(s) == 26

    out = forecast_next_user_pick_fast(
        _board(), s, _league(), _model(),
        simulations=300, seed=3, candidate_limit=5,
    )
    assert len(out) == 5
    assert set(out["engine"]) == {"SHORT-FORECAST"}
    assert set(out["opponent_picks_to_target"]) == {2}



def test_conditioned_fast_forecast_uses_deep_bank_orders():
    board = _board()
    ids = board["espn_id"].astype(int).to_numpy()
    orders = np.stack([np.roll(ids, i) for i in range(12)])
    out = forecast_next_user_pick_conditioned(
        board, _off_turn_state(), _league(), _model(),
        orders,
        {
            "particles": 160, "ess": 110.0, "ess_fraction": 110/160,
            "anchor_pick": 2, "conditioned_through": 2,
            "selected_branch_name": "P2", "degraded": False,
            "fresh_fraction": 0.25,
        },
        seed=4, candidate_limit=8,
    )
    assert len(out) == 8
    assert set(out["engine"]) == {"FAST-CONDITIONED-FORECAST"}
    assert (out["deep_bank_particles"] == 160).all()
    assert out["p_available_target"].between(0, 1).all()



def test_conditioned_deep_forecast_uses_posterior_orders():
    board = _board()
    ids = board["espn_id"].astype(int).to_numpy()
    orders = np.stack([np.roll(ids, i) for i in range(3)])
    out = forecast_next_user_pick_deep_conditioned(
        board, _off_turn_state(), _league(), _model(),
        orders,
        {
            "particles": 160, "ess": 120.0, "ess_fraction": 0.75,
            "anchor_pick": 2, "conditioned_through": 2,
            "selected_branch_name": "P2", "degraded": False,
            "reused_fraction": 0.5,
        },
        seed=5, candidate_limit=6,
    )
    assert len(out) == 6
    assert set(out["engine"]) == {"DEEP-CONDITIONED-FORECAST"}
    assert (out["simulations"] == 3).all()
    assert out["p_available_target"].between(0, 1).all()
