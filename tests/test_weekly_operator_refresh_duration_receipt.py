"""M1b six-provider measurement: injected authorized callbacks only, no network."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import pytest

MODULE = Path(__file__).resolve().parents[1]/'tools/operations/weekly_operator_refresh_duration_receipt.py'
SPEC = importlib.util.spec_from_file_location('m1b_refresh_receipt',MODULE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
START = datetime(2026,10,23,15,0,tzinfo=timezone.utc)

@pytest.fixture
def env(tmp_path):
    root = tmp_path/'fantasy_football';root.mkdir()
    runtime = root/'fantasy_season_v0_36_repack1';runtime.mkdir()
    base = runtime/'data/season_snapshots';base.mkdir(parents=True)
    (runtime/'data/season_decisions').mkdir(parents=True)
    seq = iter((START, START+timedelta(seconds=2)))
    ticks = iter((1_000_000_000,3_000_000_000))
    calls = []
    observer = []
    def callback():
        calls.append(1)
        snapshot = {'espn':{'season':2026,'week':7},
                    'source_status':{x:({'complete':True} if x=='nfl_official_rosters' else {'ok':True})
                                     for x in mod.PROVIDERS},
                    'snapshot_utc':(START+timedelta(seconds=1)).isoformat()}
        folder=base/'capture_epoch';folder.mkdir(exist_ok=True)
        file=folder/'snapshot.json'
        payload=(json.dumps(snapshot,indent=2)+'\n').encode()
        file.write_bytes(payload)
        (base/'latest.json').write_bytes(payload)
        return snapshot,file
    def guard(root):
        observer.append(True)
        return 'unchanged-source'
    def execute(**overrides):
        kwargs=dict(root=root,week=7,sync_call=callback,buffer_seconds=600,
                    runtime_validator=lambda _:runtime,source_verifier=guard,
                    clock=lambda:next(seq),monotonic_ns=lambda:next(ticks))
        kwargs.update(overrides)
        return mod.measure_authorized_sync(**kwargs)
    return root,runtime,calls,observer,execute,callback


def test_measured_epoch_binds_providers_and_snapshot(env):
    root,runtime,calls,guards,execute,_=env
    data=execute()
    assert len(calls)==1 and len(guards)==2
    assert data['duration_seconds']==2 and data['buffer_seconds']==600
    assert data['provider_count']==6 and data['runtime_version']=='0.36'
    assert data['source_binding']=='PUBLISHED_OWNER_AND_COMMISSIONED_RUNTIME'
    assert data['refresh_authority']==data['capture_authority']==data['action_authority']=='NONE'
    assert data['automatic_sync_or_mc'] is False and data['espn_writes_by_observer'] is False
    assert not list((runtime/'data/season_decisions').iterdir())
    assert len(data['snapshot_sha256'])==64
    assert 'roster' not in json.dumps(data).lower() and str(root) not in json.dumps(data)


def test_private_immutable_receipt_and_structural_envelope(env):
    _,runtime,_,_,execute,_=env
    data=execute()
    result=mod.persist_private(runtime,data)
    assert result['receipt_sha256'] and result['duration_seconds']==2
    saved=list((runtime/'data/season_decisions').glob('weekly_operator_m1b_sync_duration_*.json'))
    assert len(saved)==1 and mod.sha(saved[0].read_bytes())==result['receipt_sha256']
    assert json.loads(saved[0].read_text())==data
    with pytest.raises(mod.Blocked,match='DUPLICATE_MEASURED_EPOCH_NO_OVERWRITE'):
        mod.persist_private(runtime,data)


def test_source_guard_changes_between_calls(env):
    _,_,calls,_,execute,_=env
    states=iter(('valid','tampered'))
    with pytest.raises(mod.Blocked,match='SYNC_OBSERVER_SOURCE_CHANGED'):
        execute(source_verifier=lambda _:next(states))
    assert len(calls)==1


def test_wrong_control_root_prevents_sync(env):
    _,_,calls,_,execute,_=env
    with pytest.raises(mod.Blocked,match='WRONG_CONTROL_ROOT'):
        execute(root=Path('/tmp/random_not_project'))
    assert not calls


@pytest.mark.parametrize('week', (0,19,True,7.0))
def test_invalid_week_blocks_before_sync(env,week):
    _,_,calls,_,execute,_=env
    with pytest.raises(mod.Blocked,match='INVALID_WEEK'):
        execute(week=week)
    assert not calls


@pytest.mark.parametrize('buffer',(0,59,3601,True,600.0))
def test_invalid_buffer_blocks_before_sync(env,buffer):
    _,_,calls,_,execute,_=env
    with pytest.raises(mod.Blocked,match='REFRESH_BUFFER_NOT_EXPLICIT'):
        execute(buffer_seconds=buffer)
    assert not calls


def test_invalid_runtime_blocks_before_sync(env):
    _,_,calls,_,execute,_=env
    with pytest.raises(mod.Blocked,match='RUNTIME_IDENTITY_MISMATCH'):
        execute(runtime_validator=lambda _:Path('/bad/path'))
    assert not calls


def test_callback_failure_is_not_retried(env):
    root,_,_,_,execute,_=env
    attempts=[]
    def bad():
        attempts.append(1)
        raise RuntimeError('PROVIDER_SYNC_FAILED')
    with pytest.raises(RuntimeError,match='PROVIDER_SYNC_FAILED'):
        execute(sync_call=bad)
    assert len(attempts)==1


def test_wrong_result_snapshot_path_blocks(env):
    _,_,_,_,execute,original=env
    def wrong():
        data,path=original()
        return data,path.parent/'missing.json'
    with pytest.raises(mod.Blocked,match='SYNC_RESULT_SNAPSHOT_PATH_UNBOUND'):
        execute(sync_call=wrong)


def test_provider_unhealthy_blocks(env):
    _,_,_,_,execute,original=env
    def bad():
        data,path=original()
        data['source_status']['sleeper']['ok']=False
        payload=(json.dumps(data)+'\n').encode()
        path.write_bytes(payload)
        (path.parent.parent/'latest.json').write_bytes(payload)
        return data,path
    with pytest.raises(mod.Blocked,match='SIX_PROVIDER_HEALTH_INCOMPLETE'):
        execute(sync_call=bad)


def test_snapshot_week_mismatch_blocks(env):
    _,_,_,_,execute,original=env
    def bad():
        data,path=original()
        data['espn']['week']=8
        payload=(json.dumps(data)+'\n').encode()
        path.write_bytes(payload)
        (path.parent.parent/'latest.json').write_bytes(payload)
        return data,path
    with pytest.raises(mod.Blocked,match='SNAPSHOT_SEASON_WEEK_INVALID'):
        execute(sync_call=bad)


def test_snapshot_not_bound_to_latest_blocks(env):
    _,_,_,_,execute,original=env
    def bad():
        data,path=original()
        (path.parent.parent/'latest.json').write_text('{}')
        return data,path
    with pytest.raises(mod.Blocked,match='LATEST_SNAPSHOT_BYTES_MISMATCH'):
        execute(sync_call=bad)


def test_duplicate_immutable_epoch_blocks(env):
    _,_,_,_,execute,original=env
    def bad():
        data,path=original()
        second=path.parent.parent/'second';second.mkdir()
        (second/'snapshot.json').write_bytes(path.read_bytes())
        return data,path
    with pytest.raises(mod.Blocked,match='IMMUTABLE_SNAPSHOT_NOT_UNIQUE'):
        execute(sync_call=bad)


def test_clock_reversal_blocks(env):
    root,runtime,_,_,execute,_=env
    times=iter((START+timedelta(seconds=5),START+timedelta(seconds=2)))
    with pytest.raises(mod.Blocked,match='MEASURED_ELAPSED_CLOCK_INVALID'):
        execute(clock=lambda:next(times))


def test_monotonic_reversal_blocks(env):
    times=iter((100,99))
    with pytest.raises(mod.Blocked,match='MONOTONIC_END_INVALID'):
        env[4](monotonic_ns=lambda:next(times))


def test_clock_drift_blocks(env):
    times=iter((START,START+timedelta(seconds=30)))
    with pytest.raises(mod.Blocked,match='MEASURED_ELAPSED_CLOCK_INVALID'):
        env[4](clock=lambda:next(times))


def test_snapshot_timestamp_outside_observation_blocks(env):
    _,_,_,_,execute,original=env
    def bad():
        data,path=original()
        data['snapshot_utc']=(START-timedelta(minutes=1)).isoformat()
        payload=(json.dumps(data)+'\n').encode()
        path.write_bytes(payload)
        (path.parent.parent/'latest.json').write_bytes(payload)
        return data,path
    with pytest.raises(mod.Blocked,match='SNAPSHOT_CHRONOLOGY_NOT_MEASURED'):
        execute(sync_call=bad)


def test_persist_rejects_unverified_envelope(env):
    _,runtime,_,_,execute,_=env
    data=execute();data['action_authority']='YES'
    with pytest.raises(mod.Blocked,match='RECEIPT_NOT_OBSERVED'):
        mod.persist_private(runtime,data)


def test_real_bound_source_identity_matches_published_fixture():
    base=Path(__file__).resolve().parents[1]/'tools/operations'
    owner=base/'weekly_operator_source_evidence_owner.py'
    # New receipt producer cannot silently accept a changed predecessor owner.
    assert mod.git_blob(owner.read_bytes())==mod.SOURCE_OWNER_BLOB


def test_private_receipt_verified_against_immutable_snapshot(env):
    _,runtime,_,_,execute,_=env
    data=execute();envelope=mod.persist_private(runtime,data)
    verified=mod.verify_private(runtime,snapshot_sha256=envelope['snapshot_sha256'],
        receipt_sha256=envelope['receipt_sha256'],now=START+timedelta(hours=1))
    assert verified==envelope


def test_private_receipt_tamper_fails(env):
    _,runtime,_,_,execute,_=env
    data=execute();envelope=mod.persist_private(runtime,data)
    p=next((runtime/'data/season_decisions').glob('*.json'))
    p.write_bytes(p.read_bytes().replace(b'"buffer_seconds":600',b'"buffer_seconds":601'))
    with pytest.raises(mod.Blocked,match='PRIVATE_RECEIPT_HASH_MISMATCH'):
        mod.verify_private(runtime,snapshot_sha256=envelope['snapshot_sha256'],
                           receipt_sha256=envelope['receipt_sha256'],now=START+timedelta(hours=1))


def test_private_receipt_stale_fails(env):
    _,runtime,_,_,execute,_=env
    data=execute();envelope=mod.persist_private(runtime,data)
    with pytest.raises(mod.Blocked,match='PRIVATE_RECEIPT_CLOCK_STALE_OR_INCONSISTENT'):
        mod.verify_private(runtime,snapshot_sha256=envelope['snapshot_sha256'],
                           receipt_sha256=envelope['receipt_sha256'],now=START+timedelta(days=15))


def test_private_snapshot_bytes_tamper_fails(env):
    _,runtime,_,_,execute,_=env
    data=execute();envelope=mod.persist_private(runtime,data)
    p=next((runtime/'data/season_snapshots').glob('*/snapshot.json'))
    p.write_text('{}')
    with pytest.raises(mod.Blocked,match='MEASURED_SNAPSHOT_MISSING_OR_AMBIGUOUS'):
        mod.verify_private(runtime,snapshot_sha256=envelope['snapshot_sha256'],
                           receipt_sha256=envelope['receipt_sha256'],now=START+timedelta(hours=1))
