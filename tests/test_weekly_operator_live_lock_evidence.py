"""Fail-closed synthetic pre-refresh live owned lock contract (no network)."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib
from pathlib import Path
import sys
import pytest

OPS = Path(__file__).resolve().parents[1] / 'tools' / 'operations'
if str(OPS) not in sys.path:
    sys.path.insert(0, str(OPS))
m = importlib.import_module('weekly_operator_live_lock_evidence')
from test_weekly_operator_calendar_evidence import fixture as cal_fixture, NOW


def fixture(*, old=False, near=False):
    snap, league, public = cal_fixture(old=old, near=near)
    snap['espn']['league_id'] = 18
    snap['espn']['teams'][0]['team_id'] = 3
    live = deepcopy(snap['espn'])
    return snap, league, public, live


def classify(snap, league, public, live, *, now=NOW, public_age=5, live_age=2):
    return m.classify(snap, league, public, live, now=now,
                      public_fetched_at=now - timedelta(seconds=public_age),
                      live_fetched_at=now - timedelta(seconds=live_age), week=7)


def test_live_roster_calendar_consistent_never_refresh_authority():
    snap, league, public, live = fixture()
    out = classify(snap, league, public, live)
    assert out['status'] == 'READONLY_LIVE_CALENDAR_LOCK_CORROBORATED'
    assert (out['live_game_records'], out['live_bye_records']) == (2, 1)
    assert (out['owned_added'], out['owned_removed'], out['owned_changed']) == (0, 0, 0)
    assert out['future_unlocked_records'] == 2
    assert out['market_and_claim_cutoffs_verified'] is False
    assert (out['refresh_authority'], out['capture_authority'], out['action_authority']) == ('NONE',) * 3
    assert out['fresh_authenticated_espn_gets'] == 1 and out['espn_writes'] is False
    assert all(k not in repr(out) for k in ('espn_id', 'league_id', 'Synthetic'))


def test_stale_snapshot_not_upgraded_by_live_get():
    snap, league, public, live = fixture(old=True)
    out = classify(snap, league, public, live)
    assert out['frozen_snapshot_stale'] is True
    assert out['status'] == 'READONLY_LIVE_CALENDAR_LOCK_CORROBORATED'
    assert out['refresh_authority'] == 'NONE'


def test_owned_added_and_removed_classified_without_private_id():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][1]['espn_id'] = 990
    out = classify(snap, league, public, live)
    assert out['status'] == 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'
    assert (out['owned_added'], out['owned_removed']) == (1, 1)
    assert '990' not in repr(out)


def test_owned_position_or_slot_drift_is_material():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][1]['lineup_slot'] = 'BENCH'
    out = classify(snap, league, public, live)
    assert out['owned_changed'] == 1
    assert out['status'] == 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'


def test_unknown_future_live_lock_fails_closed():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][1]['lineup_locked'] = None
    out = classify(snap, league, public, live)
    assert out['unknown_live_lock_records'] == 1
    assert out['status'] == 'BLOCKED_UNKNOWN_LIVE_LOCK'


def test_explicitly_locked_future_requires_partial_scoping():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][1]['lineup_locked'] = True
    out = classify(snap, league, public, live)
    assert out['explicit_locked_future_records'] == 1
    assert out['status'] == 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'
    assert out['future_unlocked_records'] == 1


def test_insufficient_eighty_minute_lead_is_blocker():
    snap, league, public, live = fixture(near=True)
    out = classify(snap, league, public, live)
    assert out['status'] == 'BLOCKED_INSUFFICIENT_PROTECTED_LEAD'
    assert out['refresh_authority'] == 'NONE'


def test_elapsed_individual_game_cannot_be_reentered_as_future():
    snap, league, public, live = fixture()
    event = next(e for e in public['events'] if any(
        s['team']['abbreviation'] == 'NE' for s in e['competitions'][0]['competitors']))
    event['date'] = '2026-10-22T15:00:00Z'
    for side in event['competitions'][0]['competitors']:
        team = side['team']['abbreviation']
        snap['matchup_context']['team_week'][team]['7']['gameday'] = '2026-10-22'
        snap['matchup_context']['team_week'][team]['7']['gametime'] = '11:00AM'
    out = classify(snap, league, public, live)
    assert out['elapsed_game_records'] == 1
    assert out['status'] == 'READONLY_PARTIAL_SCOPE_CALENDAR_LOCK_CORROBORATED'
    assert out['future_unlocked_records'] == 1


def test_wrong_league_and_owner_and_public_epoch_block():
    snap, league, public, live = fixture()
    live['league_id'] = 19
    with pytest.raises(m.Blocked, match='LIVE_LEAGUE_ID_MISMATCH'):
        classify(snap, league, public, live)
    snap, league, public, live = fixture()
    live['teams'][0]['team_id'] = 9
    with pytest.raises(m.Blocked, match='LIVE_OWNER_TEAM_ID_MISMATCH'):
        classify(snap, league, public, live)
    snap, league, public, live = fixture()
    public['week']['number'] = 8
    with pytest.raises(m.Blocked, match='INDEPENDENT_CALENDAR_NOT_CORROBORATED'):
        classify(snap, league, public, live)


def test_live_team_public_nflverse_mismatch_blocks():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][2]['nfl_team'] = 'XYZ'
    with pytest.raises(m.Blocked, match='UNKNOWN_NFL_TEAM_LIVE_ROSTER'):
        classify(snap, league, public, live)
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][2]['nfl_team'] = 'ARI'
    snap['matchup_context']['team_week']['ARI']['7']['opponent'] = 'BUF'
    with pytest.raises(m.Blocked, match='LIVE_TEAM_PUBLIC_NFLVERSE_DISAGREEMENT'):
        classify(snap, league, public, live)


def test_duplicate_live_asset_and_unknown_bool_block():
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][2]['espn_id'] = live['teams'][0]['roster'][1]['espn_id']
    with pytest.raises(m.Blocked, match='DUPLICATE_OR_MISSING_ID_LIVE_ROSTER'):
        classify(snap, league, public, live)
    snap, league, public, live = fixture()
    live['teams'][0]['roster'][1]['lineup_locked'] = 0
    assert classify(snap, league, public, live)['status'] == 'BLOCKED_UNKNOWN_LIVE_LOCK'


def test_stale_public_or_live_network_read_blocks():
    snap, league, public, live = fixture()
    with pytest.raises(m.Blocked, match='PUBLIC_FETCH_TOO_OLD'):
        classify(snap, league, public, live, public_age=121)
    with pytest.raises(m.Blocked, match='LIVE_ROSTER_FETCH_TOO_OLD'):
        classify(snap, league, public, live, public_age=61, live_age=61)
    with pytest.raises(m.Blocked, match='FETCH_CHRONOLOGY_INVALID'):
        classify(snap, league, public, live, public_age=1, live_age=2)


def test_all_live_nonbye_locked_has_no_future_scope():
    snap, league, public, live = fixture()
    for row in live['teams'][0]['roster']:
        row['lineup_locked'] = True
    out = classify(snap, league, public, live)
    assert out['status'] == 'BLOCKED_NO_FUTURE_UNLOCKED_OWNED_GAME'
    assert out['future_unlocked_records'] == 0
