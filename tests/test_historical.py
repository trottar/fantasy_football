import json
from pathlib import Path
import pandas as pd

from src.historical import build_historical_priors


def test_historical_prior_build(tmp_path: Path):
    rows = []
    # Player A: 2 games in 2024 at 10 PPR, 2 games in 2025 at 20 PPR.
    for season, points in [(2024, 10.0), (2025, 20.0)]:
        for week in [1, 2]:
            rows.append({
                "player_id": "A",
                "player_display_name": "Player A",
                "position": "WR",
                "season": season,
                "week": week,
                "season_type": "REG",
                "fantasy_points_ppr": points,
            })
    # Population peer
    for week in [1, 2]:
        rows.append({
            "player_id": "B",
            "player_display_name": "Player B",
            "position": "WR",
            "season": 2025,
            "week": week,
            "season_type": "REG",
            "fantasy_points_ppr": 15.0,
        })

    stats = tmp_path / "stats.csv"
    pd.DataFrame(rows).to_csv(stats, index=False)

    cfg = {
        "historical_prior": {
            "seasons": [2024, 2025],
            "season_weights": {"2024": 0.25, "2025": 0.75},
            "shrinkage_games": {"WR": 2.0},
        }
    }
    cfg_path = tmp_path / "model.json"
    cfg_path.write_text(json.dumps(cfg))
    out_path = tmp_path / "priors.csv"

    out = build_historical_priors(stats, cfg_path, out_path)
    a = out[out["gsis_id"] == "A"].iloc[0]

    # Recency-weighted raw mean before shrinkage = 17.5.
    assert abs(a["historical_raw_ppg"] - 17.5) < 1e-9
    assert 0.0 < a["shrinkage_lambda"] < 1.0
    assert out_path.exists()
