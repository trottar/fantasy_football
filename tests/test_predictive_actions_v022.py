from __future__ import annotations

import pandas as pd

from src.transaction_manager import evaluate_actions


def _league():
    return {
        "teams": 2,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "fantasy_season": {"regular_season_weeks": list(range(1, 14))},
        "bye_weeks_2026": {},
    }


def _model():
    return {
        "weekly_manager": {"status_active_probability": {"ACTIVE": 1.0}},
        "season_utility": {"active_probability_nonbye": {"QB": 1.0, "RB": 1.0, "WR": 1.0, "TE": 1.0, "K": 1.0, "DST": 1.0}},
        "weekly_yield": {"espn_week_anchor_weight": 0.35, "espn_season_anchor_weight": 0.15},
        "transaction_manager": {
            "availability_scenarios": 2,
            "predictive_mc_scenarios": 32,
            "predictive_mc_screen_per_status": 20,
            "random_seed": 19,
            "candidate_limit": 10,
            "candidate_floor_per_position": 1,
            "replacement_available_rank": {"QB": 1, "RB": 1, "WR": 1, "TE": 1, "K": 1, "DST": 1},
            "waiver_p_acquire_default": 0.35,
            "waiver_p_acquire_floor": 0.02,
            "opponent_roster_target": {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1},
        },
    }


def _p(pid, name, pos, pts, fantasy_status="ROSTERED"):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": "PIT",
        "weekly_projection": pts,
        "season_projection": pts * 17,
        "injury_status": "ACTIVE",
        "fantasy_status": fantasy_status,
        "droppable": True,
        "lineup_locked": False,
        "percent_owned": 50.0,
    }


def _roster(offset=0):
    return [
        _p(offset+1, "QB", "QB", 20),
        _p(offset+2, "RB1", "RB", 17), _p(offset+3, "RB2", "RB", 15), _p(offset+4, "RB3", "RB", 7),
        _p(offset+5, "WR1", "WR", 17), _p(offset+6, "WR2", "WR", 14), _p(offset+7, "WR3", "WR", 6),
        _p(offset+8, "TE1", "TE", 10), _p(offset+9, "TE2", "TE", 5),
        _p(offset+10, "K", "K", 8), _p(offset+11, "DST", "DST", 7),
    ]


def test_v022_action_report_contains_paired_mc_and_prediction_audit(tmp_path):
    add = _p(900, "Upgrade", "WR", 19, fantasy_status="FREEAGENT")
    snap = {
        "snapshot_utc": "2026-08-31T12:00:00+00:00",
        "espn": {
            "season": 2026, "week": 1,
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": 2, "roster": _roster(0)},
                {"team_id": 2, "name": "Them", "waiver_rank": 1, "roster": _roster(100)},
            ],
            "matchups": [{"week": 1, "home_team_id": 1, "away_team_id": 2}],
            "available_players": [add],
        },
    }
    values = tmp_path / "values.csv"
    ids = [p["espn_id"] for p in _roster(0) + _roster(100)] + [900]
    pd.DataFrame([
        {"espn_id": pid, "latent_mean_ppg": 19.0 if pid == 900 else 10.0,
         "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 4.0}
        for pid in ids
    ]).to_csv(values, index=False)

    report = evaluate_actions(snap, _league(), _model(), values, team_name="Us")
    assert report["schema_version"] == 12
    assert report["predictive_mc_scenarios"] == 32
    assert report["predictive_actions_evaluated"] > 0
    assert report["baseline"]["mc_scenarios"] == 32
    assert report["prediction_snapshot"]["model_version"] == "0.23"
    assert report["prediction_snapshot"]["kinematic_model"] == "NFLVERSE_SHRUNK_ACCEPTANCE_V023"
    assert report["prediction_snapshot"]["interaction_model"] == "DATA_MC_INTERACTION_GRID_V028"
    top = report["free_agent_actions"][0]
    assert top["mc_scenarios"] == 32
    assert 0.0 <= top["p_utility_better_if_acquired"] <= 1.0
    assert 0.0 <= top["p_utility_tie_if_acquired"] <= 1.0
    assert 0.0 <= top["p_utility_worse_if_acquired"] <= 1.0
    assert abs(
        top["p_utility_better_if_acquired"]
        + top["p_utility_tie_if_acquired"]
        + top["p_utility_worse_if_acquired"]
        - 1.0
    ) < 1e-12
    assert top["delta_h2h_p16"] <= top["delta_h2h_p84"]
    assert top["candidate_espn_anchor_kind"] == "ESPN_WEEKLY"
    assert top["candidate_model_mean_ppg"] == 19.0
