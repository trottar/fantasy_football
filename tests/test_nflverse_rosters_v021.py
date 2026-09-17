from __future__ import annotations

from src.data_sources.nflverse_rosters import build_roster_index, parse_roster_csv
from src.season_snapshot import _annotate_nflverse_rosters


def test_roster_index_prefers_active_row_when_same_latest_week():
    text = """season,team,position,status,full_name,espn_id,week,gsis_id\n2026,PIT,WR,RET,Old Name,123,1,00-1\n2026,NE,WR,ACT,Old Name,123,1,00-1\n"""
    idx = build_roster_index(parse_roster_csv(text))
    assert idx[123]["team"] == "NE"
    assert idx[123]["status"] == "ACT"


def test_active_roster_annotation_corrects_stale_espn_team():
    players = [{"espn_id": 123, "name": "Player", "position": "WR", "nfl_team": "PIT"}]
    matched = _annotate_nflverse_rosters(players, {
        123: {"team": "NE", "status": "ACT", "week": 1, "gsis_id": "00-1"}
    })
    assert matched == 1
    assert players[0]["espn_nfl_team_original"] == "PIT"
    assert players[0]["nfl_team"] == "NE"
    assert players[0]["nfl_team_source"] == "NFLVERSE_ROSTER"
    assert players[0]["nflverse_roster_status"] == "ACT"


def test_retired_roster_annotation_does_not_resurrect_team():
    players = [{"espn_id": 124, "name": "Retired", "position": "WR", "nfl_team": "PIT"}]
    _annotate_nflverse_rosters(players, {
        124: {"team": "PIT", "status": "RET", "week": 1, "gsis_id": "00-2"}
    })
    assert players[0]["nfl_team"] == "PIT"
    assert players[0]["nflverse_roster_status"] == "RET"
    assert players[0]["nflverse_availability_status"] == "OUT"
