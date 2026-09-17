from pathlib import Path

import pandas as pd

from src.mock_calibration import (
    calibration_inventory,
    mock_draft_summary,
    parse_espn_mock_markdown,
)


def test_mock_parser_handles_dst_and_round_geometry():
    text = """
1. Player One / DET RB
R1, P1 - Team A
2. [image](x)
Texans D/ST / HOU D/ST
R1, P2 - Team B
"""
    df = parse_espn_mock_markdown(text, num_teams=2)
    assert len(df) == 2
    assert df.iloc[0]["player_name"] == "Player One"
    assert df.iloc[1]["position"] == "DST"
    assert df.iloc[1]["overall"] == 2


def test_packaged_full_mock_is_complete_and_has_16_user_picks():
    root = Path(__file__).parents[1]
    path = root / "data" / "mock_drafts" / "mock_20260830_full.csv"
    df = pd.read_csv(path)
    assert len(df) == 192
    assert int(df["round"].max()) == 16
    user = df[df["fantasy_team_name"].eq("I'm sorry Wilson!")]
    assert len(user) == 16
    assert user["overall"].tolist() == [2,23,26,47,50,71,74,95,98,119,122,143,146,167,170,191]
    summary = mock_draft_summary(df)
    assert summary["position_counts"]["DST"] >= 1
    assert summary["position_counts"]["K"] >= 1


def test_mock_inventory_sees_first_calibration_sample():
    root = Path(__file__).parents[1]
    info = calibration_inventory(root / "data" / "mock_drafts")
    assert info["draft_count"] == 2
    assert info["drafts"][0]["picks"] == 192
