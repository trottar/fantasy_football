"""M1b public schedule / frozen nflverse / NFL published byes source bridge."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
from pathlib import Path
import sys

import pytest

OPS = Path(__file__).resolve().parents[1] / 'tools' / 'operations'
if str(OPS) not in sys.path:
    sys.path.insert(0, str(OPS))
m = importlib.import_module('weekly_operator_calendar_evidence')
NOW = datetime(2026, 10, 22, 16, 0, tzinfo=timezone.utc)


def fixture(*, old=False, near=False):
    away = sorted(set(m.TEAMS) - {t for t, w in m.OFFICIAL_2026_BYES.items() if w == 7})
    events = []
    frozen_games = {}
    kickoff = '2026-10-22T16:30:00Z' if near else '2026-10-25T17:00:00Z'
    for i in range(0, len(away), 2):
        a, b = away[i], away[i + 1]
        events.append({'id': str(i + 1), 'date': kickoff,
                       'season': {'year': 2026, 'type': 2}, 'week': {'number': 7},
                       'competitions': [{'competitors': [
                           {'homeAway': 'home', 'team': {'abbreviation': a}},
                           {'homeAway': 'away', 'team': {'abbreviation': b}}]}]})
        for team, opponent in ((a, b), (b, a)):
            frozen_games[team] = {'7': {'gameday': '2026-10-22' if near else '2026-10-25',
                                        'gametime': '12:30PM' if near else '1:00PM',
                                        'opponent': opponent}}
    # First asset is on official bye, second and third have actual games.
    rows = [
        {'espn_id': 1, 'position': 'DST', 'nfl_team': 'BUF', 'lineup_locked': False},
        {'espn_id': 2, 'position': 'QB', 'nfl_team': 'NE', 'lineup_locked': False},
        {'espn_id': 3, 'position': 'K', 'nfl_team': 'KC', 'lineup_locked': False},
    ]
    snap = {'snapshot_utc': (NOW - timedelta(hours=4) if old else NOW - timedelta(minutes=8)).isoformat(),
            'espn': {'season': 2026, 'week': 7, 'teams': [{'name': 'Synthetic', 'roster': rows}]},
            'source_status': {name: {'ok': True, 'complete': True} for name in m.PROVIDERS},
            'matchup_context': {'team_week': frozen_games}}
    league = {'season': 2026, 'user_team_name': 'Synthetic',
              'bye_weeks_2026': dict(m.OFFICIAL_2026_BYES)}
    cal = {'season': {'year': 2026, 'type': 2}, 'week': {'number': 7}, 'events': events}
    return snap, league, cal


def test_corroborated_bye_and_games_still_no_refresh_authority():
    snap, league, cal = fixture()
    out = m.compare(snap, league, cal, now=NOW, week=7)
    assert out['status'] == 'CORROBORATED_CALENDAR_LIVE_OWNED_ROSTER_STILL_REQUIRED'
    assert (out['owned_records'], out['corroborated_kickoff_records'], out['corroborated_bye_records']) == (3, 2, 1)
    assert (out['league_games'], out['league_bye_teams']) == (14, 4)
    assert out['refresh_authority'] == out['action_authority'] == 'NONE'
    assert out['espn_authenticated_access'] is False
    assert all(s not in repr(out) for s in ('espn_id', 'league_id', 'Synthetic'))


def test_stale_frozen_roster_not_upgraded_by_fresh_public_feed():
    snap, league, cal = fixture(old=True)
    out = m.compare(snap, league, cal, now=NOW, week=7)
    assert out['status'] == 'CORROBORATED_CALENDAR_STALE_FROZEN_ROSTER'
    assert out['snapshot_age_seconds'] == 14400
    assert out['refresh_authority'] == 'NONE'


def test_near_first_lock_cannot_pass_80_minute_budget():
    snap, league, cal = fixture(near=True)
    out = m.compare(snap, league, cal, now=NOW, week=7)
    assert out['status'] == 'CORROBORATED_CALENDAR_INSUFFICIENT_PLANNING_LEAD'


def test_all_assets_locked_future_does_not_authorize_actions():
    snap, league, cal = fixture()
    for row in snap['espn']['teams'][0]['roster']:
        row['lineup_locked'] = True
    out = m.compare(snap, league, cal, now=NOW, week=7)
    assert out['locked_or_elapsed_records'] == 2
    assert out['status'] == 'CORROBORATED_CALENDAR_NO_FUTURE_OWNED_LOCK'


def test_public_schedule_removes_one_game_fails_closed():
    snap, league, cal = fixture()
    cal['events'].pop()
    with pytest.raises(m.Blocked, match='PUBLIC_SCOREBOARD_GAME_COUNT_MISMATCH'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_public_duplicate_team_fails_closed():
    snap, league, cal = fixture()
    t = cal['events'][0]['competitions'][0]['competitors'][0]['team']['abbreviation']
    cal['events'][1]['competitions'][0]['competitors'][0]['team']['abbreviation'] = t
    with pytest.raises(m.Blocked, match='PUBLIC_TEAM_DUPLICATE_OR_UNKNOWN'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_nflverse_opponent_disagreement_fails_closed():
    snap, league, cal = fixture()
    snap['matchup_context']['team_week']['NE']['7']['opponent'] = 'NYJ' if snap['matchup_context']['team_week']['NE']['7']['opponent'] != 'NYJ' else 'PIT'
    with pytest.raises(m.Blocked, match='INDEPENDENT_NFLVERSE_GAME_OR_KICKOFF_DISAGREEMENT'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_nflverse_kickoff_disagreement_fails_closed():
    snap, league, cal = fixture()
    snap['matchup_context']['team_week']['KC']['7']['gametime'] = '4:25PM'
    with pytest.raises(m.Blocked, match='INDEPENDENT_NFLVERSE_GAME_OR_KICKOFF_DISAGREEMENT'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_official_bye_playing_is_blocked():
    snap, league, cal = fixture()
    cal['events'][0]['competitions'][0]['competitors'][0]['team']['abbreviation'] = 'BUF'
    with pytest.raises(m.Blocked, match='PUBLIC_SCOREBOARD_LEAGUE_COVERAGE_MISMATCH'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_configured_bye_table_mismatch_blocks():
    snap, league, cal = fixture()
    league['bye_weeks_2026']['BUF'] = 8
    with pytest.raises(m.Blocked, match='LEAGUE_OFFICIAL_BYE_TABLE_DISAGREEMENT'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_frozen_kickoff_for_bye_blocks():
    snap, league, cal = fixture()
    snap['matchup_context']['team_week']['BUF'] = {'7': {'gameday': '2026-10-25', 'gametime': '1:00PM', 'opponent': 'KC'}}
    with pytest.raises(m.Blocked, match='FROZEN_GAME_FOR_OFFICIAL_BYE'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_public_epoch_mismatch_blocks():
    snap, league, cal = fixture()
    cal['week']['number'] = 8
    with pytest.raises(m.Blocked, match='PUBLIC_SCOREBOARD_EPOCH_MISMATCH'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_duplicate_owned_roster_id_blocks():
    snap, league, cal = fixture()
    snap['espn']['teams'][0]['roster'][1]['espn_id'] = 1
    with pytest.raises(m.Blocked, match='OWNED_ASSET_ID_INVALID'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_provider_health_blocks():
    snap, league, cal = fixture()
    snap['source_status']['nflverse_matchups']['ok'] = False
    with pytest.raises(m.Blocked, match='FROZEN_PROVIDER_HEALTH_BLOCKED:nflverse_matchups'):
        m.compare(snap, league, cal, now=NOW, week=7)


def test_scoreboard_uses_only_public_single_get(monkeypatch):
    snap, league, payload = fixture()
    raw = __import__('json').dumps(payload).encode()
    calls = []

    class Response:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return False
        def read(self, size):
            assert size == m.MAX_SCOREBOARD_BYTES + 1
            return raw

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, timeout))
        return Response()

    monkeypatch.setattr(m, 'urlopen', fake_urlopen)
    obj, digest = m.public_scoreboard(season=2026, week=7)
    assert obj == payload and len(digest) == 64
    assert calls == [('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week=7&seasontype=2&season=2026', 25)]
