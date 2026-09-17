from pathlib import Path
import pandas as pd

from src.player_master import build_player_master


def test_player_master_exact_espn_id_join(tmp_path: Path):
    espn = tmp_path / "espn.csv"
    nfl = tmp_path / "players.csv"
    priors = tmp_path / "priors.csv"
    out = tmp_path / "master.csv"

    pd.DataFrame([{
        "espn_id": 42, "name": "Example", "position": "RB",
        "nfl_team": "PIT", "espn_adp": 10.0
    }]).to_csv(espn, index=False)

    pd.DataFrame([{
        "gsis_id": "00-0000042", "espn_id": 42,
        "display_name": "Example", "position": "RB"
    }]).to_csv(nfl, index=False)

    pd.DataFrame([{
        "gsis_id": "00-0000042",
        "historical_prior_mean_ppg": 15.5
    }]).to_csv(priors, index=False)

    df = build_player_master(espn, nfl, priors, out)
    row = df.iloc[0]
    assert row["gsis_id"] == "00-0000042"
    assert row["historical_prior_mean_ppg"] == 15.5
    assert bool(row["has_nflverse_id"])
    assert bool(row["has_historical_prior"])
