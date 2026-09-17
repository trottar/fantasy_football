from pathlib import Path
import pandas as pd

from src.transition import calibrate_year_to_year_transition


def test_transition_calibration(tmp_path: Path):
    rows = []
    for p in range(4):
        for season, ppg in [(2023, 10 + p), (2024, 12 + p), (2025, 9 + p)]:
            for week in [1, 2]:
                rows.append({
                    "player_id": f"P{p}",
                    "player_display_name": f"P{p}",
                    "position": "WR",
                    "season": season,
                    "week": week,
                    "season_type": "REG",
                    "fantasy_points_ppr": ppg,
                })
    path = tmp_path / "stats.csv"
    pd.DataFrame(rows).to_csv(path, index=False)

    result, pairs = calibrate_year_to_year_transition(
        path,
        seasons=[2023, 2024, 2025],
        minimum_games_per_season=1,
        minimum_pairs_per_position=1,
        sigma_floors={"WR": 1.0},
    )
    assert len(pairs) == 8
    assert result["WR"]["pairs"] == 8
    assert result["WR"]["transition_sigma_ppg"] >= 1.0
