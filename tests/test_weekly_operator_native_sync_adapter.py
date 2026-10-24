"""Synthetic-only native adapter tests; no runtime import/provider GET."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import importlib.util
import hashlib
import pytest

SOURCE=Path(__file__).resolve().parents[1]/'tools/operations/weekly_operator_native_sync_adapter.py'
S=importlib.util.spec_from_file_location('m1b_native_adapter',SOURCE)
a=importlib.util.module_from_spec(S);S.loader.exec_module(a)

@pytest.fixture
def fixture(tmp_path):
    root=tmp_path/'fantasy_football';root.mkdir()
    runtime=root/'fantasy_season_v0_36_repack1';runtime.mkdir()
    src=runtime/'src';src.mkdir()
    (src/'season_snapshot.py').write_text('# test only')
    native=Mock(return_value=('synthetic_snapshot',src/'season_snapshot.py'))
    mod=SimpleNamespace(__file__=str(src/'season_snapshot.py'),sync_season_snapshot=native)
    observed=[]
    receipt={'action_authority':'NONE','capture_authority':'NONE',
             'refresh_authority':'NONE','automatic_sync_or_mc':False}
    class Observer:
        def measure_authorized_sync(self,root,*,week,sync_call,buffer_seconds):
            observed.append((root,week,buffer_seconds))
            sync_call()
            return receipt
    checks=[]
    def bound(root):
        checks.append(root);return runtime
    return root,runtime,native,mod,observed,checks,bound,Observer(),receipt

def run(env,**kwargs):
    root,runtime,native,mod,observed,checks,bound,observer,receipt=env
    args=dict(root=root,week=7,buffer_seconds=600,execution_approved=True,
              boundary_check=bound,module_loader=lambda _:mod,observer=observer)
    args.update(kwargs)
    return a.observe_approved_sync_once(**args)

def test_approved_single_native_call_fixed_full_providers(fixture):
    x=run(fixture)
    assert x is fixture[-1] and len(fixture[4])==1
    assert len(fixture[5])==2
    fixture[2].assert_called_once_with(secrets_path=None,
      out_root=fixture[1]/'data/season_snapshots',week=7,
      include_sleeper=True,include_nfl=True)

@pytest.mark.parametrize('approved',[False,None,0,'true'])
def test_no_approval_no_import_or_sync(fixture,approved):
    load=Mock(side_effect=AssertionError('must not import'))
    with pytest.raises(a.Blocked,match='EXPLICIT_REFRESH_APPROVAL_REQUIRED'):
        run(fixture,execution_approved=approved,module_loader=load)
    load.assert_not_called();fixture[2].assert_not_called();assert not fixture[5]

@pytest.mark.parametrize('week',[True,0,19,7.0])
def test_wrong_week_never_launches(fixture,week):
    with pytest.raises(a.Blocked,match='INVALID_WEEK'):run(fixture,week=week)
    fixture[2].assert_not_called()

@pytest.mark.parametrize('margin',[0,60.0,True,3601])
def test_wrong_buffer_never_launches(fixture,margin):
    with pytest.raises(a.Blocked,match='EXPLICIT_REFRESH_MARGIN_REQUIRED'):
        run(fixture,buffer_seconds=margin)
    fixture[2].assert_not_called()

def test_module_location_mismatch_blocks_before_sync(fixture):
    fake=SimpleNamespace(__file__='/untrusted/season_snapshot.py',
                         sync_season_snapshot=fixture[2])
    with pytest.raises(a.Blocked,match='NATIVE_MODULE_ORIGIN_MISMATCH'):
        run(fixture,module_loader=lambda _:fake)
    fixture[2].assert_not_called()

def test_missing_native_callable_blocks_before_sync(fixture):
    wrong=SimpleNamespace(__file__=str(fixture[1]/'src/season_snapshot.py'))
    with pytest.raises(a.Blocked,match='NATIVE_SYNC_CALLABLE_MISSING'):
        run(fixture,module_loader=lambda _:wrong)
    fixture[2].assert_not_called()

def test_wrong_runtime_boundary_blocks_before_sync(fixture):
    with pytest.raises(a.Blocked,match='RUNTIME_BOUNDARY_INVALID'):
        run(fixture,boundary_check=lambda _:fixture[0])
    fixture[2].assert_not_called()

def test_native_exception_never_retried(fixture):
    fixture[2].side_effect=RuntimeError('private provider error')
    with pytest.raises(RuntimeError,match='private provider error'):
        run(fixture)
    fixture[2].assert_called_once()

def test_post_sync_native_identity_change_blocks(fixture):
    calls=iter([fixture[1],fixture[0]])
    with pytest.raises(a.Blocked,match='NATIVE_SOURCE_CHANGED_DURING_SYNC'):
        run(fixture,boundary_check=lambda _:next(calls))
    fixture[2].assert_called_once()

def test_no_authority_escalation(fixture):
    fixture[-1]['action_authority']='YES'
    with pytest.raises(a.Blocked,match='MEASUREMENT_AUTHORITY_ESCALATION'):
        run(fixture)
    fixture[2].assert_called_once()

def test_import_has_no_runtime_or_network_side_effects():
    assert callable(a.boundary) and callable(a.observe_approved_sync_once)
    assert a.NATIVE_SYNC_BLOB=='eabcbee3ea2a06e7f68dfea5cbe0e4a2eb768609'

def test_exact_published_observer_blob():
    target=SOURCE.parent/'weekly_operator_refresh_duration_receipt.py'
    assert a.blob(target.read_bytes())==a.OBSERVER_BLOB


def test_native_loader_accepts_owned_namespace_src(monkeypatch,fixture):
    from types import ModuleType
    import sys
    runtime=fixture[1]
    pkg=ModuleType('src');pkg.__file__=None;pkg.__path__=[str(runtime/'src')]
    target=ModuleType('src.season_snapshot')
    target.__file__=str(runtime/'src/season_snapshot.py')
    target.sync_season_snapshot=fixture[2]
    monkeypatch.setitem(sys.modules,'src',pkg)
    monkeypatch.setitem(sys.modules,'src.season_snapshot',target)
    assert a._load_native(runtime) is target


def test_native_loader_blocks_foreign_namespace_src(monkeypatch,fixture):
    from types import ModuleType
    import sys
    pkg=ModuleType('src');pkg.__file__=None;pkg.__path__=['/wrong/src']
    monkeypatch.setitem(sys.modules,'src',pkg)
    with pytest.raises(a.Blocked,match='FOREIGN_SRC_MODULE_ALREADY_LOADED'):
        a._load_native(fixture[1])


def test_boundary_rejects_missing_runtime(fixture):
    with pytest.raises(a.Blocked,match='COMMISSIONED_RUNTIME_MISSING'):
        a.boundary(Path('/tmp/fantasy_football'))


def test_boundary_rejects_malformed_version_before_import(fixture):
    runtime=fixture[1]
    (runtime/'VERSION').write_text('unknown')
    with pytest.raises(a.Blocked,match='COMMISSIONED_VERSION_MISMATCH'):
        a.boundary(fixture[0])
