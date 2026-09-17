from pathlib import Path

import pandas as pd

from src.diagnostics import build_data_diagnostics


def test_data_diagnostics(tmp_path: Path):
    master = tmp_path / "master.csv"
    pd.DataFrame([
        {
            "espn_id": 1, "gsis_id": "A", "name": "Alpha", "position": "WR",
            "nfl_team": "PIT", "espn_adp": 10.0, "espn_rank": 8.0,
            "espn_proj_points": 250.0, "historical_prior_mean_ppg": 15.0,
            "historical_prior_sd_weekly": 5.0, "historical_games": 40,
            "has_nflverse_id": True, "has_historical_prior": True,
        },
        {
            "espn_id": 2, "gsis_id": None, "name": "Beta", "position": "RB",
            "nfl_team": "DET", "espn_adp": 20.0, "espn_rank": 18.0,
            "espn_proj_points": None, "historical_prior_mean_ppg": None,
            "historical_prior_sd_weekly": None, "historical_games": None,
            "has_nflverse_id": False, "has_historical_prior": False,
        },
    ]).to_csv(master, index=False)

    result = build_data_diagnostics(master, out_dir=tmp_path / "diag", top_n=10)
    assert result["summary"]["master_rows"] == 2
    assert result["summary"]["coverage"]["espn_adp"] == 2
    assert result["summary"]["coverage"]["espn_proj_points"] == 1
    assert result["summary"]["unmatched_espn_players"] == 1
    assert (tmp_path / "diag" / "summary.json").exists()
    assert (tmp_path / "diag" / "coverage_by_position.csv").exists()
