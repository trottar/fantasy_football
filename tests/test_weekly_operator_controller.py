"""Synthetic immutable-phase and protected-native-MC tests; never ESPN/network."""
from __future__ import annotations
import copy
from datetime import datetime,timezone,timedelta
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

HERE=Path(__file__).parent
S=importlib.util.spec_from_file_location('weekly_controller_m1a',HERE.parent/'tools/operations/weekly_operator_controller.py')
mod=importlib.util.module_from_spec(S); S.loader.exec_module(mod)
NOW=datetime(2026,10,22,15,0,tzinfo=timezone.utc)

class FakeReview:
    from hashlib import sha256 as _unused
    import hashlib
    @staticmethod
    def uid(v): return int(v) if v is not None else None
    @staticmethod
    def utc(v):
        a=datetime.fromisoformat(v.replace('Z','+00:00'))
        return a.astimezone(timezone.utc) if a.tzinfo else None
    @staticmethod
    def jload(p): return json.loads(p.read_text(encoding='utf-8'))
    @staticmethod
    def sha(b):
        import hashlib
        return hashlib.sha256(b).hexdigest()
    @staticmethod
    def _canon(o):
        import hashlib
        return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    @staticmethod
    def discover(rt,now,verify_capture=None,canonical=None):
        # Local synthetic acceptance only, not a substitute for the real module.
        rp=next((rt/'data/season_decisions').glob('weekly_decision_receipt_*.json'))
        return None,None,None,{'receipt_sha256':FakeReview.sha(rp.read_bytes())}

def tree(tmp_path, *, has_snapshot=True, has_capture=True, has_receipt=True,
         source_health=True, wrong_binding=False):
    root=tmp_path/'fantasy_football';rt=root/'fantasy_season_v0_36_repack1'
    for rel in ('data/season_snapshots/clock','data/season_predictions/closure','data/season_decisions'):
        (rt/rel).mkdir(parents=True)
    if not has_snapshot: return root,rt,None,None
    snap={'snapshot_utc':'2026-10-22T14:00:00+00:00','espn':{'season':2026,'week':7},
      'source_status':{p:{'ok':source_health} for p in ('espn','sleeper','nflverse_rosters','nflverse_matchups','nfl_official_rosters','nfl_official')}}
    snap['source_status']['nfl_official_rosters']={'complete':source_health}
    (rt/'data/season_snapshots/latest.json').write_text(json.dumps(snap))
    (rt/'data/season_snapshots/clock/snapshot.json').write_text(json.dumps(snap))
    cap=None
    if has_capture:
        cap={'captured_utc':'2026-10-22T14:01:00+00:00',
             'snapshot_utc':snap['snapshot_utc'],'season':2026,'week':7,
             'measurement_contract':'A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
             'behavioral_observation_state':{'snapshot_sha256': 'bad' if wrong_binding else FakeReview._canon(snap)},
             'pre_data_firewall':{'2026_game_outcomes_used_for_tuning':False,'automatic_refit':False,'automatic_calibration':False}}
        (rt/'data/season_predictions/closure/pregame_2026_w07_clock.json').write_text(json.dumps(cap))
    if has_receipt:
        (rt/'data/season_decisions/weekly_decision_receipt_clock.json').write_text(json.dumps(
            {'provenance':{'snapshot_utc':snap['snapshot_utc']}}))
    return root,rt,snap,cap

def test_no_snapshot_requests_new_epoch(tmp_path):
    root,_,_,_=tree(tmp_path,has_snapshot=False)
    assert mod.inspect(root,now=NOW,review_module=FakeReview)['phase']=='NEW_SNAPSHOT_REQUIRED'

def test_snapshot_only_requires_capture(tmp_path):
    root,_,_,_=tree(tmp_path,has_capture=False,has_receipt=False)
    assert mod.inspect(root,now=NOW,review_module=FakeReview)['phase']=='CAPTURE_REQUIRED'

def test_snapshot_health_failure_blocks(tmp_path):
    root,_,_,_=tree(tmp_path,source_health=False)
    with pytest.raises(mod.Blocked,match='SIX_PROVIDER_SNAPSHOT_HEALTH_BLOCKED'):
        mod.inspect(root,now=NOW,review_module=FakeReview)

def test_valid_frozen_missing_mc_can_resume_without_rerunning_sync(tmp_path):
    root,_,_,_=tree(tmp_path,has_receipt=False)
    got=mod.inspect(root,now=NOW,review_module=FakeReview,verifier=lambda c:True)
    assert got['phase']=='MC_READY_TO_GUARD' and not got['native_mc_started']
    assert got['snapshot_sha256'] and got['capture_sha256']

def test_existing_complete_receipt_reused(tmp_path):
    root,_,_,_=tree(tmp_path)
    got=mod.inspect(root,now=NOW,review_module=FakeReview)
    assert got['phase']=='NATIVE_RECEIPT_READY' and got['no_repeat_mc']

def test_marker_blocks_relaunch_after_uncertain_mc(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    a=mod.inspect(root,now=NOW,review_module=FakeReview)
    marker=rt/'data/season_decisions/week7_thu_decision_nine_mc_launch_dummy.json'
    marker.write_text(json.dumps({'snapshot_sha256':a['snapshot_sha256'],'capture_sha256':a['capture_sha256']}))
    b=mod.inspect(root,now=NOW,review_module=FakeReview)
    assert b['phase']=='MC_OUTCOME_UNCERTAIN' and b['no_repeat_mc']

def test_wrong_snapshot_binding_blocks(tmp_path):
    root,_,_,_=tree(tmp_path,wrong_binding=True)
    with pytest.raises(mod.Blocked,match='CAPTURE_SNAPSHOT_BINDING_INVALID'):
        mod.inspect(root,now=NOW,review_module=FakeReview)

def test_request_next_week_never_reuses_old_week(tmp_path):
    root,_,_,_=tree(tmp_path)
    r=mod.inspect(root,now=NOW,week=8,review_module=FakeReview)
    assert r['phase']=='NEW_SNAPSHOT_REQUIRED' and r['week']==8

def test_ambiguous_snapshot_refused(tmp_path):
    root,rt,_,_=tree(tmp_path)
    d=rt/'data/season_snapshots/duplicate';d.mkdir()
    (d/'snapshot.json').write_bytes((rt/'data/season_snapshots/clock/snapshot.json').read_bytes())
    with pytest.raises(mod.Blocked,match='LATEST_IMMUTABLE_SNAPSHOT_IDENTITY_AMBIGUOUS'):
        mod.inspect(root,now=NOW,review_module=FakeReview)

def test_ambiguous_capture_refused(tmp_path):
    root,rt,_,_=tree(tmp_path)
    source=rt/'data/season_predictions/closure/pregame_2026_w07_clock.json'
    (source.parent/'pregame_2026_w07_repeat.json').write_bytes(source.read_bytes())
    with pytest.raises(mod.Blocked,match='AMBIGUOUS_CAPTURE_FOR_LATEST_EPOCH'):
        mod.inspect(root,now=NOW,review_module=FakeReview)

def test_missing_mc_must_not_run_without_explicit_resume(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    g=SimpleNamespace(validate_root=lambda r:rt)
    x=mod.run(root,now=NOW,mode='review',review_module=FakeReview,guarded_module=g)
    assert x['phase']=='MC_READY_TO_GUARD' and not list((rt/'data/season_decisions').glob('*mc_launch*'))

def test_existing_mc_invokes_review_once_without_native_mc(tmp_path):
    root,rt,_,_=tree(tmp_path)
    g=SimpleNamespace(validate_root=lambda r:rt)
    used=[]
    x=mod.run(root,now=NOW,mode='review',review_module=FakeReview,guarded_module=g,
              review_run=lambda r:(used.append('review') or {'operator_state':'SCOPED_REVIEW_REQUIRED','queue':[{'state':'HOLD'}]}))
    assert used==['review'] and x['phase']=='READONLY_DECISION_REVIEW' and x['no_repeat_mc']

def test_unknown_prior_launch_blocks_explicit_resume(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    a=mod.inspect(root,now=NOW,review_module=FakeReview)
    (rt/'data/season_decisions/legacy_mc_launch.json').write_text(json.dumps({'snapshot_sha256':a['snapshot_sha256'],'capture_sha256':a['capture_sha256']}))
    with pytest.raises(mod.Blocked,match='MC_LAUNCH_BLOCKED_BY_PHASE'):
        mod.execute_existing_mc(root,NOW,mod.inspect(root,now=NOW,review_module=FakeReview),review_module=FakeReview)

def test_never_backdate_now(tmp_path):
    root,_,_,_=tree(tmp_path)
    with pytest.raises(mod.Blocked,match='LATEST_SNAPSHOT_EPOCH_INVALID'):
        mod.inspect(root,now=NOW-timedelta(hours=2),review_module=FakeReview)

def test_exact_identity_pair_requires_fresh_receipts(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    with pytest.raises(mod.Blocked,match='EVIDENCE_REQUIRED'):
        mod._identity_pair(rt,NOW,FakeReview.jload)

def test_cli_wrong_root_returns_blocked(capsys):
    assert mod.main(['--project-root','/nonsense','--mode','status'])==3
    assert 'ACTION_AUTHORITY=NONE' in capsys.readouterr().out

def test_old_unlaunched_capture_not_prospective_run_authority(tmp_path):
    root,_,_,_=tree(tmp_path,has_receipt=False)
    out=mod.inspect(root,now=NOW+timedelta(hours=4),review_module=FakeReview)
    assert out['phase']=='CAPTURE_REQUIRED' and 'DO_NOT_BACKFILL' in out['reason']

def test_old_complete_mc_still_reused_only_as_scoped_evidence(tmp_path):
    root,_,_,_=tree(tmp_path)
    out=mod.inspect(root,now=NOW+timedelta(hours=4),review_module=FakeReview)
    assert out['phase']=='NATIVE_RECEIPT_READY'

def test_explicit_mc_resume_creates_exclusive_marker_before_native(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    plan=mod.inspect(root,now=NOW,review_module=FakeReview)
    d=rt/'data/season_decisions'
    (d/'week7_thu_commissioned_identity_stamp.json').write_text(json.dumps({'commissioned':True,'verified_utc':NOW.isoformat()}))
    (d/'week7_thu_memory_health_stamp.json').write_text(json.dumps({'strict':True,'status':'PASS','checked_utc':NOW.isoformat()}))
    effects=[]
    def fake_native(root,runtime,paths,deadline,evidence,child=None):
        assert (d/(mod.MARKER_PREFIX+plan['capture_sha256']+'.json')).is_file()
        effects.append('native')
        return {'receipt_sha256':'e'*64,'action_window':'RECHECK_REQUIRED'}
    g=SimpleNamespace(validate_root=lambda r:rt,
        inspect=lambda *args:(dict(deadline=NOW+timedelta(hours=8)),
                              {'snapshot_sha256':plan['snapshot_sha256'],'capture_sha256':plan['capture_sha256']}),
        evaluate_timing=lambda *args:{'classification':'READY_TO_START_MC_NOT_ACTION_AUTHORITY'},
        execute=fake_native)
    got=mod.execute_existing_mc(root,NOW,plan,review_module=FakeReview,guard_module=g)
    assert effects==['native'] and got['native_mc_started']
    assert mod.inspect(root,now=NOW,review_module=FakeReview)['phase']=='MC_OUTCOME_UNCERTAIN'
    with pytest.raises(mod.Blocked,match='MC_LAUNCH_BLOCKED_BY_PHASE'):
        mod.execute_existing_mc(root,NOW,mod.inspect(root,now=NOW,review_module=FakeReview),
                                review_module=FakeReview,guard_module=g)
    assert effects==['native']

def test_near_deadline_never_creates_launch_marker(tmp_path):
    root,rt,_,_=tree(tmp_path,has_receipt=False)
    plan=mod.inspect(root,now=NOW,review_module=FakeReview)
    d=rt/'data/season_decisions'
    (d/'commissioned_identity_stamp.json').write_text(json.dumps({'commissioned':True,'verified_utc':NOW.isoformat()}))
    (d/'memory_health_stamp.json').write_text(json.dumps({'strict':True,'status':'PASS','checked_utc':NOW.isoformat()}))
    g=SimpleNamespace(validate_root=lambda r:rt,
        inspect=lambda *args:(dict(deadline=NOW+timedelta(minutes=30)),
                              {'snapshot_sha256':plan['snapshot_sha256'],'capture_sha256':plan['capture_sha256']}),
        evaluate_timing=lambda *args:{'classification':'BLOCKED_TOO_LATE'})
    with pytest.raises(mod.Blocked,match='INSUFFICIENT_PROTECTED_MC_WINDOW'):
        mod.execute_existing_mc(root,NOW,plan,review_module=FakeReview,guard_module=g)
    assert not list(d.glob(mod.MARKER_PREFIX+'*'))
