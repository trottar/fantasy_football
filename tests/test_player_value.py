import json
from pathlib import Path

import pandas as pd

from src.player_value import build_player_values, robust_sigma


def _cfg():
    return {
        "latent_value": {
            "season_games": 17.0,
            "historical_mean_floor_ppg": {"QB": 1.5, "RB": 1.5, "WR": 1.5, "TE": 1.25},
            "projection_sigma_floor_ppg": {"QB": 2.0, "RB": 2.25, "WR": 2.25, "TE": 1.75},
            "weekly_sd_fallback_ppg": {"QB": 8.0, "RB": 7.5, "WR": 8.0, "TE": 6.5},
            "rookie_epistemic_multiplier": 1.35,
            "limited_history_games": 10.0,
            "limited_history_multiplier": 1.15,
            "minimum_calibration_players": 1,
            "transition_calibration": {
                "seasons": [2023, 2024, 2025],
                "minimum_games_per_season": 1,
                "minimum_pairs_per_position": 1,
                "transition_sigma_floor_ppg": {
                    "QB": 2.5, "RB": 2.5, "WR": 2.25, "TE": 2.0
                }
            },
        }
    }


def test_robust_sigma():
    s = robust_sigma([1, 2, 3, 4, 5])
    assert s > 0


def test_build_player_values(tmp_path: Path):
    rows = []
    for i in range(4):
        rows.append({
            "name": f"Veteran {i}", "position": "WR", "nfl_team": "PIT",
            "espn_adp": 10 + i, "espn_rank": 10 + i,
            "espn_proj_points": (18 + i) * 17,
            "historical_prior_mean_ppg": 16 + i,
            "historical_prior_sd_weekly": 8.0,
            "historical_games": 34,
            "has_historical_prior": True,
            "years_of_experience": 3,
        })
    rows.append({
        "name": "Rookie", "position": "WR", "nfl_team": "DET",
        "espn_adp": 25, "espn_rank": 22,
        "espn_proj_points": 15 * 17,
        "historical_prior_mean_ppg": None,
        "historical_prior_sd_weekly": None,
        "historical_games": None,
        "has_historical_prior": False,
        "years_of_experience": 0,
    })
    rows.append({
        "name": "History Only", "position": "WR", "nfl_team": "DAL",
        "espn_adp": 100, "espn_rank": 95,
        "espn_proj_points": None,
        "historical_prior_mean_ppg": 12.0,
        "historical_prior_sd_weekly": 7.0,
        "historical_games": 30,
        "has_historical_prior": True,
        "years_of_experience": 4,
    })

    master = tmp_path / "master.csv"
    pd.DataFrame(rows).to_csv(master, index=False)

    # Consecutive-season data for transition calibration.
    hist_rows = []
    for player_i in range(3):
        for season, ppg in [(2023, 10 + player_i), (2024, 13 + player_i), (2025, 11 + player_i)]:
            for week in [1, 2]:
                hist_rows.append({
                    "player_id": f"P{player_i}",
                    "player_display_name": f"P{player_i}",
                    "position": "WR",
                    "season": season,
                    "week": week,
                    "season_type": "REG",
                    "fantasy_points_ppr": ppg,
                })
    stats = tmp_path / "stats.csv"
    pd.DataFrame(hist_rows).to_csv(stats, index=False)

    cfg = tmp_path / "model.json"
    cfg.write_text(json.dumps(_cfg()))
    out = tmp_path / "values.csv"
    cal = tmp_path / "cal.json"
    transition = tmp_path / "transition.json"

    df, calibration = build_player_values(
        master, cfg, out, cal,
        stats_path=stats,
        transition_path=transition,
    )
    vet = df[df["name"] == "Veteran 0"].iloc[0]
    rookie = df[df["name"] == "Rookie"].iloc[0]
    hist = df[df["name"] == "History Only"].iloc[0]

    assert vet["model_status"] == "history+projection"
    assert 16.0 < vet["latent_mean_ppg"] < 18.0
    assert vet["historical_transition_sigma_ppg"] >= 2.25
    assert 0.0 < vet["projection_weight"] < 1.0
    assert rookie["model_status"] == "projection_only"
    assert abs(rookie["latent_mean_ppg"] - 15.0) < 1e-12
    assert bool(rookie["rookie_like"])
    assert hist["model_status"] == "history_only"
    assert abs(hist["latent_mean_ppg"] - 12.0) < 1e-12
    assert out.exists()
    assert cal.exists()
    assert transition.exists()
    assert "WR" in calibration
