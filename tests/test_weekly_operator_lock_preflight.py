"""Pure synthetic tests for the M1b read-only first-lock gate."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'operations' / 'weekly_operator_lock_preflight.py'
spec = importlib.util.spec_from_file_location('weekly_operator_lock_preflight', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = datetime(2026, 10, 22, 16, 0, tzinfo=timezone.utc)


def fixture(*, kickoff='2026-10-24', gametime='1:00PM'):
    rows = [
        {'espn_id': 101, 'nfl_team': 'PIT', 'position': 'QB', 'lineup_locked': False},
        {'espn_id': 102, 'nfl_team': 'BUF', 'position': 'DST', 'lineup_locked': False},
        {'espn_id': 103, 'nfl_team': 'KC', 'position': 'K', 'lineup_locked': False},
    ]
    snap = {'snapshot_utc': (NOW - timedelta(minutes=5)).isoformat(),
            'espn': {'season': 2026, 'week': 7,
                     'teams': [{'name': 'Synthetic Team', 'roster': rows}]},
            'source_status': {x: {'ok': True, 'complete': True} for x in m.PROVIDERS},
            'matchup_context': {'team_week': {n: {'7': {'gameday': kickoff, 'gametime': gametime}}
                                               for n in ('PIT', 'BUF', 'KC')}}}
    league = {'season': 2026, 'user_team_name': 'Synthetic Team', 'bye_weeks_2026': {}}
    return snap, league


def test_safe_readonly_success_includes_all_three_channels():
    snap, league = fixture()
    out = m.classify(snap, league, now=NOW, week=7)
    assert out['status'] == 'READONLY_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY'
    assert out['position_counts'] == {'DST': 1, 'K': 1, 'QB': 1}
    assert out['known_kickoff_records'] == 3
    assert out['espn_writes'] is False and out['native_mc_started'] is False
    assert 'player_id' not in out and 'league_id' not in out


def test_unknown_kickoff_blocks_no_inferred_sunday():
    snap, league = fixture()
    del snap['matchup_context']['team_week']['KC']['7']
    out = m.classify(snap, league, now=NOW)
    assert out['status'] == 'BLOCKED_UNVERIFIED_OWNED_LOCK_OR_BYE'
    assert out['unknown_lock_records'] == 1


def test_configured_bye_not_assumed_independently_verified():
    snap, league = fixture()
    del snap['matchup_context']['team_week']['BUF']['7']
    league['bye_weeks_2026']['BUF'] = 7
    out = m.classify(snap, league, now=NOW)
    assert out['configured_bye_unverified_records'] == 1
    assert out['status'] == 'BLOCKED_UNVERIFIED_OWNED_LOCK_OR_BYE'


def test_missing_provider_blocks():
    snap, league = fixture()
    snap['source_status']['nflverse_matchups']['ok'] = False
    with pytest.raises(m.Blocked, match='SIX_PROVIDER_HEALTH_BLOCKED:nflverse_matchups'):
        m.classify(snap, league, now=NOW)


def test_expired_snapshot_blocks():
    snap, league = fixture()
    snap['snapshot_utc'] = (NOW - timedelta(hours=3)).isoformat()
    assert m.classify(snap, league, now=NOW)['status'] == 'BLOCKED_STALE_SNAPSHOT'


def test_early_lock_blocks_protected_mc_budget():
    snap, league = fixture(kickoff='2026-10-22', gametime='1:00PM')
    assert m.classify(snap, league, now=NOW)['status'] == 'BLOCKED_INSUFFICIENT_LEAD'


def test_all_past_lock_blocks():
    snap, league = fixture(kickoff='2026-10-22', gametime='10:00AM')
    out = m.classify(snap, league, now=NOW)
    assert out['status'] == 'BLOCKED_NO_FUTURE_OWNED_LOCK'
    assert out['locked_or_elapsed_records'] == 3


def test_week_and_owner_boundaries():
    snap, league = fixture()
    with pytest.raises(m.Blocked, match='WEEK_NOT_CURRENT'):
        m.classify(snap, league, now=NOW, week=8)
    league['user_team_name'] = 'Other'
    with pytest.raises(m.Blocked, match='OWNED_TEAM_NAME_UNRESOLVED'):
        m.classify(snap, league, now=NOW)


def test_duplicates_and_missing_game_time_fail_closed():
    snap, league = fixture()
    snap['espn']['teams'][0]['roster'][1]['espn_id'] = 101
    with pytest.raises(m.Blocked, match='ROSTER_PLAYER_ID_MISSING_OR_DUPLICATED'):
        m.classify(snap, league, now=NOW)
    snap, league = fixture(gametime='TBD')
    out = m.classify(snap, league, now=NOW)
    assert out['status'] == 'BLOCKED_UNVERIFIED_OWNED_LOCK_OR_BYE'
    assert out['unknown_lock_records'] == 3


def test_future_dated_snapshot_rejected():
    snap, league = fixture()
    snap['snapshot_utc'] = (NOW + timedelta(minutes=1)).isoformat()
    with pytest.raises(m.Blocked, match='SNAPSHOT_CHRONOLOGY_INVALID'):
        m.classify(snap, league, now=NOW)


def test_espn_locked_future_asset_is_excluded_from_actionable_locks():
    snap, league = fixture()
    for row in snap['espn']['teams'][0]['roster']:
        row['lineup_locked'] = True
    out = m.classify(snap, league, now=NOW)
    assert out['locked_or_elapsed_records'] == 3
    assert out['earliest_future_owned_lock_utc'] is None
    assert out['status'] == 'BLOCKED_NO_FUTURE_OWNED_LOCK'


def test_existing_locked_player_does_not_grant_whole_roster_budget_pass():
    snap, league = fixture()
    snap['espn']['teams'][0]['roster'][0]['lineup_locked'] = True
    out = m.classify(snap, league, now=NOW)
    assert out['locked_or_elapsed_records'] == 1
    assert out['status'] == 'READONLY_PARTIAL_SCOPE_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY'
