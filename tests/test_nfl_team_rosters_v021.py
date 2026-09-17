from __future__ import annotations

from src.data_sources.nfl_team_rosters import parse_team_roster_html
from src.season_snapshot import _annotate_nfl_official_rosters


def test_parse_team_roster_html_extracts_status_and_team():
    html = '''
    <table>
      <thead><tr><th>Player</th><th>No</th><th>Pos</th><th>Status</th><th>Experience</th></tr></thead>
      <tbody>
        <tr><td>Active Player</td><td>10</td><td>WR</td><td>ACT</td><td>3</td></tr>
        <tr><td>Reserve Player</td><td>11</td><td>WR</td><td>RLS</td><td>6</td></tr>
      </tbody>
    </table>
    '''
    rows = parse_team_roster_html(html, "SF")
    assert rows == [
        {"name": "Active Player", "team": "SF", "position": "WR", "status": "ACT", "number": "10"},
        {"name": "Reserve Player", "team": "SF", "position": "WR", "status": "RLS", "number": "11"},
    ]


def test_official_roster_annotation_overrides_team_only_for_active():
    players = [
        {"espn_id": 1, "name": "Moved Player", "position": "WR", "nfl_team": "NE"},
        {"espn_id": 2, "name": "Left Squad", "position": "WR", "nfl_team": "SF"},
    ]
    matched = _annotate_nfl_official_rosters(players, [
        {"name": "Moved Player", "team": "WAS", "status": "ACT", "source_url": "u1"},
        {"name": "Left Squad", "team": "SF", "status": "RLS", "source_url": "u2"},
    ])
    assert matched == 2
    assert players[0]["nfl_team"] == "WAS"
    assert players[0]["nfl_team_source"] == "NFL_OFFICIAL_ROSTER"
    assert players[1]["nfl_team"] == "SF"
    assert players[1]["official_roster_status"] == "RLS"


def test_official_roster_annotation_maps_rsr_to_current_week_ir():
    players = [{"espn_id": 3, "name": "Designated Return", "position": "RB", "nfl_team": "ARI"}]
    matched = _annotate_nfl_official_rosters(players, [
        {"name": "Designated Return", "team": "ARI", "status": "RSR", "source_url": "u3"},
    ])
    assert matched == 1
    assert players[0]["official_roster_status"] == "RSR"
    assert players[0]["official_roster_availability_status"] == "IR"
