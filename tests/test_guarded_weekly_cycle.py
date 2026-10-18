from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util
import json
import subprocess

import pytest

HERE = Path(__file__).resolve().parent
MODULE = (HERE.parent / "tools/operations/guarded_weekly_cycle.py") if (HERE.parent / "tools/operations/guarded_weekly_cycle.py").is_file() else (HERE / "guarded_weekly_cycle.py")
REF = (HERE.parent / "tools/operations/deadline_budget.py") if (HERE.parent / "tools/operations/deadline_budget.py").is_file() else (HERE / "ref_deadline_budget.py")

spec = importlib.util.spec_from_file_location("guarded_weekly_cycle_under_test", MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def now():
    return datetime(2026, 10, 21, 16, 0, tzinfo=timezone.utc)


def rows(offset=180, unknown=False, locked=False):
    ts = None if unknown else (now() + timedelta(minutes=-5 if locked else offset)).isoformat()
    return [{"espn_id": 11, "position": "WR", "side": "US", "kickoff_utc": ts}]


def test_future_mixed_unowned_unknown():
    cap = {"team_id": 1, "league_player_predictions": {"records": rows() +
           [{"espn_id": 5, "position": "RB", "side": "OPP", "kickoff_utc": None}]},
           "specialist_predictions": {"records": [{"position": "K", "espn_id": 20,
           "owner_team_id": 1, "kickoff_utc": (now()+timedelta(minutes=210)).isoformat()}]}}
    report = g._lock_candidates(cap, now())
    assert report["unknown_all"] == 1
    assert report["owned_records"] == 2
    assert report["deadline"] == now()+timedelta(minutes=180)


@pytest.mark.parametrize("bad", ["unknown", "expired", "no_user", "no_rows"])
def test_bad_owned_lock(bad):
    records = rows(unknown=bad == "unknown", locked=bad == "expired")
    if bad == "no_user": records[0]["side"] = "OPP"
    if bad == "no_rows": records = []
    cap = {"team_id": 1, "league_player_predictions": {"records": records},
           "specialist_predictions": {"records": [{"position":"DST", "owner_team_id":2,
           "kickoff_utc": (now()+timedelta(minutes=200)).isoformat()}]}}
    with pytest.raises(g.Blocked):
        g._lock_candidates(cap, now())


def test_budget_boundaries(tmp_path):
    (tmp_path / 'tools/operations').mkdir(parents=True)
    (tmp_path / 'tools/operations/deadline_budget.py').write_bytes(REF.read_bytes())
    for m, expected in [(15,'BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME'),
                        (80,'BLOCKED_INSUFFICIENT_RUN_AND_ACTION_TIME'),
                        (81,'READY_TO_START_MC_NOT_ACTION_AUTHORITY')]:
        r = g.evaluate_timing(tmp_path, now(), now()+timedelta(minutes=m))
        assert r['classification'] == expected


def fixture(tmp_path):
    root = tmp_path/'fantasy_football'
    runtime = root/g.EXPECTED_RUNTIME
    (runtime/'data/season_snapshots/one').mkdir(parents=True)
    (runtime/'data/season_predictions/closure').mkdir(parents=True)
    (runtime/'data/season_decisions').mkdir(parents=True)
    (root/'tools/operations').mkdir(parents=True)
    (root/'tools/operations/deadline_budget.py').write_bytes(REF.read_bytes())
    (runtime/'VERSION').write_text(g.EXPECTED_VERSION)
    cap_time=(now()-timedelta(minutes=4)).isoformat()
    snap_time=(now()-timedelta(minutes=5)).isoformat()
    source={key:{'complete':True} if key=='nfl_official_rosters' else {'ok':True} for key in g.PROVIDERS}
    snap={'snapshot_utc':snap_time,'espn':{'week':7,'season':2026},'source_status':source}
    (runtime/'data/season_snapshots/one/snapshot.json').write_text(json.dumps(snap))
    capture={'season':2026,'week':7,'model_version':g.EXPECTED_VERSION,
         'measurement_contract':'A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
         'captured_utc':cap_time,'snapshot_utc':snap_time,'team_id':1,
         'league_player_predictions':{'records':rows()},
         'specialist_predictions':{'records':[{'position':'K','owner_team_id':1,
               'kickoff_utc':(now()+timedelta(minutes=200)).isoformat()}]},
         'behavioral_observation_state':{'snapshot_sha256':g._canon(snap)},
         'pre_data_firewall':{'2026_game_outcomes_used_for_tuning':False,
                             'automatic_refit':False,'automatic_calibration':False}}
    capture['integrity']={'canonical_payload_sha256':g._canon(capture)}
    (runtime/'data/season_predictions/closure/capture.json').write_text(json.dumps(capture))
    dependencies = {}
    for key, rel in g.DEPENDENCIES.items():
        candidate=runtime/rel
        candidate.parent.mkdir(parents=True,exist_ok=True)
        candidate.write_bytes((key + ' test data\n').encode())
        dependencies[key]=g._sha256(candidate.read_bytes())
    identity={'commissioned':True,'source_checkpoint':g.EXPECTED_SOURCE_CHECKPOINT,
              'runtime_version':g.EXPECTED_VERSION,'verified_utc':cap_time,'dependencies':dependencies}
    memory={'status':'PASS','strict':True,'checked_utc':cap_time}
    (runtime/'data/season_decisions/ident.json').write_text(json.dumps(identity))
    (runtime/'data/season_decisions/memory.json').write_text(json.dumps(memory))
    return root, runtime, ('data/season_snapshots/one/snapshot.json','data/season_predictions/closure/capture.json',
        'data/season_decisions/ident.json','data/season_decisions/memory.json')


def test_snapshot_integrity_and_health(tmp_path):
    root, rt, args=fixture(tmp_path)
    locks, evidence=g.inspect(root,rt,*args,now())
    assert locks['owned_records']==2
    assert len(evidence['capture_sha256']) == 64
    cp=rt/args[1]
    c=json.loads(cp.read_text());c['integrity']['canonical_payload_sha256']='0'*64
    cp.write_text(json.dumps(c))
    with pytest.raises(g.Blocked, match='CAPTURE_INTEGRITY_INVALID'):
        g.inspect(root,rt,*args,now())


def test_unknown_owned_rejects_before_run(tmp_path):
    root,rt,args=fixture(tmp_path)
    cp=rt/args[1]
    cap=json.loads(cp.read_text());cap['league_player_predictions']['records'][0]['kickoff_utc']=None
    cap['integrity']['canonical_payload_sha256']=g._canon({k:v for k,v in cap.items() if k!='integrity'})
    cp.write_text(json.dumps(cap))
    with pytest.raises(g.Blocked,match='UNKNOWN_OWNED_PLAYER_LOCK'):
        g.inspect(root,rt,*args,now())


def test_snap_binding_reject(tmp_path):
    root,rt,args=fixture(tmp_path)
    snap=rt/args[0]; data=json.loads(snap.read_text());data['snapshot_utc']=(now()-timedelta(minutes=6)).isoformat()
    snap.write_text(json.dumps(data))
    with pytest.raises(g.Blocked,match='CAPTURE_SNAPSHOT_TIME_MISMATCH'):
        g.inspect(root,rt,*args,now())


def test_mc_not_started_when_budget_expired(tmp_path):
    root,rt,args=fixture(tmp_path)
    locks, evidence=g.inspect(root,rt,*args,now())
    def unexpected(*a,**k): raise AssertionError('MC must never be invoked')
    with pytest.raises(g.Blocked,match='DEADLINE_EXPIRED_BEFORE_MC_LAUNCH'):
        g.execute(root,rt,args,now()+timedelta(minutes=20),evidence,
                  now_fn=now,child=unexpected)


def test_mc_success_is_still_not_action_authority(tmp_path):
    root,rt,args=fixture(tmp_path)
    locks,evidence=g.inspect(root,rt,*args,now())
    def child(cmd,**kwargs):
        assert cmd[1:3]==['fantasy.py','weekly-cycle']
        path=rt/'data/season_decisions/weekly_decision_receipt_fake.json'
        path.write_text(json.dumps({'provenance':{'snapshot_utc':evidence['snapshot']['snapshot_utc']},
                                    'overall_state':'INCOMPLETE_COVERAGE'}))
        return subprocess.CompletedProcess(cmd,0,'','')
    timestamps=iter([now(),now()+timedelta(minutes=145)])
    result=g.execute(root,rt,args,locks['deadline'],evidence,now_fn=lambda: next(timestamps),child=child)
    assert result['native_overall']=='INCOMPLETE_COVERAGE'
    assert result['action_window']=='LOCK_PASSED_OR_INSUFFICIENT_ACTION_TIME'


def test_native_failure_redacts_private_output(tmp_path):
    root,rt,args=fixture(tmp_path)
    locks,evidence=g.inspect(root,rt,*args,now())
    def child(cmd,**kwargs):return subprocess.CompletedProcess(cmd,1,'private ID/owner','secret')
    with pytest.raises(g.Blocked,match='NATIVE_MC_FAILED_EXIT_1;PRIVATE_LOG=') as err:
        g.execute(root,rt,args,locks['deadline'],evidence,now_fn=now,child=child)
    assert 'private ID' not in str(err.value)
    assert len(list((rt/'data/season_decisions').glob('guarded_mc_failure_*.log'))) == 1


def test_no_mutation_in_check_only(tmp_path):
    root,rt,args=fixture(tmp_path)
    before=sorted((str(p),p.read_bytes()) for p in rt.rglob('*') if p.is_file())
    g.inspect(root,rt,*args,now())
    after=sorted((str(p),p.read_bytes()) for p in rt.rglob('*') if p.is_file())
    assert before==after


def test_post_mc_requires_only_action_budget(tmp_path):
    root, rt, args = fixture(tmp_path)
    locks, evidence = g.inspect(root, rt, *args, now())
    def child(cmd, **kwargs):
        (rt/'data/season_decisions/weekly_decision_receipt_ok.json').write_text(
          json.dumps({'provenance':{'snapshot_utc':evidence['snapshot']['snapshot_utc']},
                      'overall_state':'INCOMPLETE_COVERAGE'}))
        return subprocess.CompletedProcess(cmd,0,'','')
    # Before MC, 180 minutes. After MC, 50 minutes to lock. This suffices
    # for validation/action/safety (40) but NOT a second 40-minute MC.
    timestamps=iter([now(),now()+timedelta(minutes=130)])
    result=g.execute(root,rt,args,locks['deadline'],evidence,now_fn=lambda: next(timestamps),child=child)
    assert result['action_window']=='RECHECK_REQUIRED'


def test_missing_provider_fails_before_run(tmp_path):
    root, rt, args = fixture(tmp_path)
    snap_path=rt/args[0]
    snap=json.loads(snap_path.read_text())
    snap['source_status']['espn']['ok']=False
    snap_path.write_text(json.dumps(snap))
    with pytest.raises(g.Blocked,match='PROVIDER_HEALTH_INCOMPLETE:espn'):
        g.inspect(root,rt,*args,now())


def test_old_capture_blocks(tmp_path):
    root, rt, args=fixture(tmp_path)
    cp=rt/args[1]
    cap=json.loads(cp.read_text());cap['captured_utc']=(now()-timedelta(hours=3)).isoformat()
    cap['integrity']['canonical_payload_sha256']=g._canon({k:v for k,v in cap.items() if k!='integrity'})
    cp.write_text(json.dumps(cap))
    with pytest.raises(g.Blocked,match='CAPTURE_CHRONOLOGY_INVALID|CAPTURE_TOO_OLD_FOR_PROTECTED_RUN'):
        g.inspect(root,rt,*args,now())


def test_untrusted_local_paths_reject(tmp_path):
    root, rt, args=fixture(tmp_path)
    for p in ['../secrets','data/season_decisions/ident.json','C:\\other.json','data/season_snapshots/../season_decisions/ident.json']:
        with pytest.raises(g.Blocked):
            g.safe_file(rt,p,'data/season_snapshots')


def test_commissioning_identity_mismatch_blocks(tmp_path):
    root,rt,args=fixture(tmp_path)
    identity=rt/args[2];j=json.loads(identity.read_text());j['source_checkpoint']='0'*40
    identity.write_text(json.dumps(j))
    with pytest.raises(g.Blocked,match='COMMISSIONING_IDENTITY_INVALID'):
        g.inspect(root,rt,*args,now())


def test_post_mc_fails_on_mutated_capture(tmp_path):
    root,rt,args=fixture(tmp_path)
    locks,evidence=g.inspect(root,rt,*args,now())
    def child(cmd,**kwargs):
        (rt/'data/season_decisions/weekly_decision_receipt_mutated.json').write_text(
          json.dumps({'provenance':{'snapshot_utc':evidence['snapshot']['snapshot_utc']}}))
        (rt/args[1]).write_text((rt/args[1]).read_text()+' ')
        return subprocess.CompletedProcess(cmd,0,'','')
    with pytest.raises(g.Blocked,match='IMMUTABLE_EVIDENCE_CHANGED_DURING_MC'):
        g.execute(root,rt,args,locks['deadline'],evidence,now_fn=now,child=child)


def test_dependency_mismatch_blocks_before_mc(tmp_path):
    root,rt,args=fixture(tmp_path)
    (rt/g.DEPENDENCIES['model_config']).write_text('MUTATED')
    with pytest.raises(g.Blocked,match='COMMISSIONED_DEPENDENCY_MISMATCH:model_config'):
        g.inspect(root,rt,*args,now())
