"""Synthetic source-binding/restart-safety tests.  No network, MC, or ESPN writes."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

owner = module('tools/operations/weekly_operator_source_evidence_owner.py', 'm1b_source_owner')
auth = module('tools/operations/weekly_operator_deadline_authority.py', 'm1b_deadline_auth')
NOW = datetime(2026, 10, 23, 15, 0, tzinfo=timezone.utc)


@pytest.fixture
def env(tmp_path):
    root = tmp_path / 'fantasy_football'
    ops = root / 'tools/operations'
    ops.mkdir(parents=True)
    for relative in owner.DEPENDENCY_BLOBS:
        target = root / relative
        target.write_bytes((ROOT / relative).read_bytes())
    runtime = root / 'fantasy_season_v0_36_repack1'
    epoch = runtime / 'data/season_snapshots/20261023T140000Z'
    epoch.mkdir(parents=True)
    payload = {'snapshot_utc': '2026-10-23T14:00:00+00:00',
               'espn': {'season': 2026, 'week': 7},
               'source_status': {}}
    raw = (json.dumps(payload, sort_keys=True) + '\n').encode()
    (epoch / 'snapshot.json').write_bytes(raw)
    (epoch.parent / 'latest.json').write_bytes(raw)
    return root, runtime, hashlib.sha256(raw).hexdigest()


def live(snap_sha, status='READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'):
    return {'phase': 'M1B_PRE_REFRESH_LIVE_OWNED_LOCK_READONLY',
            'status': status, 'season': 2026, 'week': 7,
            'calendar_corrob_source': auth.ESPN_PUBLIC_NFLVERSE,
            'fresh_authenticated_espn_gets': 1,
            'public_calendar_check_age_seconds': 3,
            'live_roster_check_age_seconds': 0,
            'frozen_snapshot_sha256': snap_sha,
            'unknown_live_lock_records': 0,
            'future_unlocked_records': 10,
            'earliest_future_unlocked_kickoff_utc': (NOW+timedelta(hours=5)).isoformat(),
            'action_authority': 'NONE', 'espn_writes': False,
            'private_cookie': 'must_not_escape', 'espn_id': 999999}


def execute(env, *, live_result=None, times=None, reader=None, root=None,
            runtime_validator=None, classifier=None):
    root0, runtime, digest = env
    root = root or root0
    values = iter(times or [NOW, NOW + timedelta(seconds=2)])
    reader = reader or (lambda base, week: live_result or live(digest))
    validator = runtime_validator or (lambda base: runtime)
    return owner.audit(root, week=7, clock=lambda: next(values),
                       live_reader=reader, runtime_validator=validator,
                       deadline_classifier=classifier or auth.classify)


def test_source_pure_audit_healthy_proves_only_observation(env):
    result = execute(env)
    assert result['phase'] == 'M1B_SOURCE_BOUND_LIVE_EVIDENCE_READONLY'
    assert result['lineup_window'] == 'GAME_LOCK_WINDOW_OBSERVED_NOT_ACTION_AUTHORITY'
    assert result['planning_status'] == 'BLOCKED_REFRESH_MEASUREMENT_MISSING'
    assert result['refresh_receipt_source'] == 'UNAVAILABLE_NOT_YET_COMMISSIONED'
    assert result['waiver_window'] == 'BLOCKED_EXACT_CUTOFF_UNVERIFIED'
    assert result['trade_window'] == 'BLOCKED_EXACT_CUTOFF_UNVERIFIED'
    assert result['snapshot_sha256'] == env[2]
    assert result['action_authority'] == result['capture_authority'] == result['refresh_authority'] == 'NONE'
    assert result['espn_writes'] is False and result['native_mc_started'] is False
    assert 'must_not_escape' not in str(result) and '999999' not in str(result)


def test_frozen_roster_drift_is_not_transaction_authority(env):
    result = execute(env)
    assert result['live_status'] == 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'
    assert result['automatic_refresh_or_capture'] is False


def test_missing_live_owned_lock_blocks_window(env):
    l = live(env[2]); l['unknown_live_lock_records'] = 1
    result = execute(env, live_result=l)
    assert result['lineup_window'] == 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE'
    assert result['planning_status'] == 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE'


def test_unrecognized_source_status_never_echoes_private_content(env):
    l = live(env[2], 'SECRET_MANAGER_ID_AND_COOKIE')
    result = execute(env, live_result=l)
    assert result['live_status'] == 'UNRECOGNIZED_OR_BLOCKED'
    assert 'SECRET_MANAGER_ID_AND_COOKIE' not in json.dumps(result)


def test_wrong_root_rejected(env):
    with pytest.raises(owner.Blocked, match='WRONG_CONTROL_ROOT'):
        execute(env, root=env[0].parent)


def test_wrong_runtime_rejected(env):
    with pytest.raises(owner.Blocked, match='COMMISSIONED_RUNTIME_IDENTITY_INVALID'):
        execute(env, runtime_validator=lambda r: r / 'other')


def test_source_tamper_rejected_before_live_get(env):
    p = env[0] / 'tools/operations/weekly_operator_deadline_authority.py'
    p.write_bytes(p.read_bytes()+b'\n# unexpected change\n')
    calls = []
    with pytest.raises(owner.Blocked, match='SOURCE_DEPENDENCY_BLOB_MISMATCH'):
        execute(env, reader=lambda r, week: calls.append(1))
    assert not calls


def test_live_reader_source_tamper_rejected(env):
    p = env[0] / 'tools/operations/weekly_operator_live_lock_evidence.py'
    p.write_bytes(p.read_bytes()+b'\n# unexpected change\n')
    with pytest.raises(owner.Blocked, match='SOURCE_DEPENDENCY_BLOB_MISMATCH'):
        execute(env)


def test_snapshot_missing_rejected(env):
    (env[1] / 'data/season_snapshots/latest.json').unlink()
    with pytest.raises(owner.Blocked, match='LATEST_SNAPSHOT_MISSING'):
        execute(env)


def test_latest_immutable_copy_mismatch_rejected(env):
    p = env[1] / 'data/season_snapshots/latest.json'
    p.write_bytes(p.read_bytes()+b' ')
    with pytest.raises(owner.Blocked, match='IMMUTABLE_SNAPSHOT_COPY_NOT_UNIQUE'):
        execute(env)


def test_duplicate_immutable_copy_rejected(env):
    base = env[1] / 'data/season_snapshots'
    duplicate = base / '20261023T140001Z'
    duplicate.mkdir()
    (duplicate / 'snapshot.json').write_bytes((base / 'latest.json').read_bytes())
    with pytest.raises(owner.Blocked, match='IMMUTABLE_SNAPSHOT_COPY_NOT_UNIQUE'):
        execute(env)


def test_live_probe_stale_frozen_hash_rejected(env):
    with pytest.raises(owner.Blocked, match='LIVE_RESULT_SNAPSHOT_BINDING_MISMATCH'):
        execute(env, live_result=live('a'*64))


def test_live_result_wrong_week_rejected(env):
    l = live(env[2]); l['week'] = 8
    with pytest.raises(owner.Blocked, match='LIVE_RESULT_WEEK_MISMATCH'):
        execute(env, live_result=l)


def test_snapshot_changes_during_live_read_rejected(env):
    p = env[1] / 'data/season_snapshots/latest.json'
    def mutate(root, week):
        p.write_bytes(p.read_bytes()+b' ')
        return live(env[2])
    with pytest.raises(owner.Blocked, match='IMMUTABLE_SNAPSHOT_COPY_NOT_UNIQUE|FROZEN_SNAPSHOT_CHANGED'):
        execute(env, reader=mutate)


def test_dependency_changes_during_live_read_rejected(env):
    p = env[0] / 'tools/operations/weekly_operator_deadline_authority.py'
    def mutate(root, week):
        p.write_bytes(p.read_bytes()+b'\n# drift')
        return live(env[2])
    with pytest.raises(owner.Blocked, match='SOURCE_DEPENDENCY_BLOB_MISMATCH|SOURCE_CHANGED'):
        execute(env, reader=mutate)


def test_slow_live_probe_rejected(env):
    with pytest.raises(owner.Blocked, match='LIVE_OBSERVATION_DURATION_UNBOUNDED'):
        execute(env, times=[NOW, NOW+timedelta(seconds=61)])


def test_reversed_observation_chronology_rejected(env):
    with pytest.raises(owner.Blocked, match='LIVE_OBSERVATION_DURATION_UNBOUNDED'):
        execute(env, times=[NOW, NOW-timedelta(seconds=1)])


def test_naive_clock_rejected(env):
    with pytest.raises(owner.Blocked, match='NAIVE_OR_INVALID_OBSERVATION_CLOCK'):
        execute(env, times=[NOW.replace(tzinfo=None)])


def test_classification_must_not_promote_authority(env):
    def counterfeit(**kw):
        res=auth.classify(**kw); res['action_authority']='APPROVED'; return res
    with pytest.raises(owner.Blocked, match='CLASSIFIER_AUTHORITY_BOUNDARY_CHANGED'):
        execute(env, classifier=counterfeit)


def test_classification_must_not_promote_transaction_cutoff(env):
    def counterfeit(**kw):
        res=auth.classify(**kw); res['waiver_window']['classification']='CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'; return res
    with pytest.raises(owner.Blocked, match='UNVERIFIED_TRANSACTION_WINDOW_PROMOTED'):
        execute(env, classifier=counterfeit)


@pytest.mark.parametrize('starting_representation', ('checkout', 'existing_bom_crlf'))
def test_source_guard_git_normalized_bom_and_crlf(env, starting_representation):
    p = env[0]/'tools/operations/weekly_operator_deadline_authority.py'
    # Git checkout bytes are platform-specific. Construct a single BOM + CRLF
    # from canonical content, rather than prepend a second BOM or double CRs.
    raw = p.read_bytes()
    canonical = raw.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    if starting_representation == 'existing_bom_crlf':
        p.write_bytes(b'\xef\xbb\xbf' + canonical.replace(b'\n', b'\r\n'))
    checkout = p.read_bytes()
    normalized = checkout.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    p.write_bytes(b'\xef\xbb\xbf' + normalized.replace(b'\n', b'\r\n'))
    result = execute(env)
    assert result['source_binding'] == 'EXACT_SOURCE_BLOBS_AND_IMMUTABLE_SNAPSHOT'


def test_invalid_json_is_sanitized(env):
    p = env[1] / 'data/season_snapshots/latest.json'
    p.write_text('{ SECRET stuff',encoding='utf-8')
    with pytest.raises(owner.Blocked, match='SNAPSHOT_JSON_INVALID'):
        execute(env)


def test_an_unexpected_live_exception_is_never_logged_as_raw_payload(env, capsys, monkeypatch):
    # CLI-level sanitization: a provider error may contain a credential or URI.
    monkeypatch.setattr(owner, 'audit', lambda *a,**kw: (_ for _ in ()).throw(RuntimeError('secret-cookie=ABC')))
    assert owner.main(['--week','7']) == 3
    output = capsys.readouterr().out
    assert 'RuntimeError' in output and 'secret-cookie' not in output


def test_valid_live_source_requires_auth_reader_exact_once(env):
    calls=[]
    def probe(base,week):
        calls.append((base,week))
        return live(env[2])
    result=execute(env,reader=probe)
    assert calls==[(env[0],7)]
    assert result['authenticated_espn_gets']==1
