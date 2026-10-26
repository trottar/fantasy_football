"""Source-only integration checks: workflow never upgrades MC into transaction authority."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

PATH = Path(__file__).resolve().parents[1] / 'tools/operations/weekly_operator_v2.py'
spec = importlib.util.spec_from_file_location('week8_integrated_operator_isolated', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ET = timezone(timedelta(hours=-4))
EST = timezone(timedelta(hours=-5))
W8 = datetime(2026, 10, 27, 8, 0, tzinfo=ET)


def test_correct_week7_to_week8_to_week9_calendar():
    assert m.selected_week(datetime(2026,10,25,21,37,tzinfo=ET)) == 7
    assert m.selected_week(datetime(2026,10,26,0,1,tzinfo=ET)) == 8
    assert m.selected_week(datetime(2026,11,1,23,59,tzinfo=EST)) == 8
    assert m.selected_week(datetime(2026,11,2,0,0,tzinfo=EST)) == 9


def test_naive_clock_and_outside_2026_season_block():
    with pytest.raises(m.Blocked,match='CLOCK_NOT_AWARE'):
        m.selected_week(datetime(2026,10,25))
    with pytest.raises(m.Blocked,match='OUTSIDE_2026_FANTASY_CALENDAR'):
        m.selected_week(datetime(2026,8,25,tzinfo=ET))


def test_schedule_slots_do_not_invent_waiver_cutoffs():
    assert m.planned_slot(W8,8) == 'TUE'
    assert m.planned_slot(W8+timedelta(days=1),8) == 'WED'
    assert m.planned_slot(W8+timedelta(days=4),8) == 'SAT'
    assert m.planned_slot(W8+timedelta(days=2),8) == 'PASSIVE'
    with pytest.raises(m.Blocked,match='CALENDAR_WEEK_DISAGREEMENT'):
        m.planned_slot(W8,9)


def scoreboard(monkeypatch,kickoff=None):
    from types import ModuleType
    cal=ModuleType('weekly_operator_calendar_evidence')
    cal.independent_schedule=lambda obj,**kw:{'A':('B',kickoff or W8+timedelta(days=2)),'B':('A',kickoff or W8+timedelta(days=2))}
    monkeypatch.setitem(sys.modules,'weekly_operator_calendar_evidence',cal)
    return cal


def test_first_game_lead_is_real_and_strict(monkeypatch):
    scoreboard(monkeypatch)
    ok=m.public_lock_preflight(now=W8,week=8,scoreboard={})
    assert ok['lead_minutes']>80 and ok['week']==8
    scoreboard(monkeypatch,kickoff=W8+timedelta(minutes=79))
    with pytest.raises(m.Blocked,match='NEXT_GAME_PROSPECTIVE_LEAD_MISSING'):
        m.public_lock_preflight(now=W8,week=8,scoreboard={})



def test_saturday_partial_capture_scope_excludes_thursday(monkeypatch):
    cal=scoreboard(monkeypatch)
    sat=datetime(2026,10,31,9,tzinfo=ET)
    thurs=datetime(2026,10,29,20,15,tzinfo=ET)
    sun=datetime(2026,11,1,13,tzinfo=timezone(timedelta(hours=-5)))
    cal.independent_schedule=lambda obj,**kw:{'T':('U',thurs),'U':('T',thurs),
                                            'V':('W',sun),'W':('V',sun)}
    result=m.public_lock_preflight(now=sat,week=8,scoreboard={})
    assert result['already_elapsed_game_records']==2
    assert result['prospective_scope']=='FUTURE_GAMES_ONLY_NOT_RETROSPECTIVE_BACKFILL'
    assert result['lead_minutes']>80
    with pytest.raises(m.Blocked,match='NO_REMAINING_FUTURE_NFL_GAME'):
        m.public_lock_preflight(now=sun+timedelta(days=1),week=8,scoreboard={})

def test_native_cli_captures_output_and_never_forwards_private_content(capsys,tmp_path):
    calls=[]
    def fake(cmd,**kw):
        calls.append((cmd,kw))
        return SimpleNamespace(returncode=0,stdout='VERY_PRIVATE_TOKEN',stderr='PRIVATE_RESPONSE')
    m.run_native_cli(tmp_path,'season-sync','--week','8',launcher=fake)
    assert len(calls)==1 and calls[0][0][-3:] == ['season-sync','--week','8']
    assert capsys.readouterr().out == ''
    def bad(cmd,**kw):return SimpleNamespace(returncode=2,stdout='SECRET',stderr='SECRET')
    with pytest.raises(m.Blocked,match='NATIVE_STAGE_FAILED_season-sync'):
        m.run_native_cli(tmp_path,'season-sync',launcher=bad)
    assert 'SECRET' not in capsys.readouterr().out


def test_native_backend_exceptions_redacted(tmp_path):
    def bad(cmd,**kw):raise RuntimeError('private cookie contents')
    with pytest.raises(m.Blocked,match='NATIVE_STAGE_EXCEPTION_RuntimeError') as exc:
        m.run_native_cli(tmp_path,'season-sync',launcher=bad)
    assert 'cookie' not in str(exc.value)


def test_snapshot_six_provider_and_archive_identity(tmp_path):
    rt=tmp_path/'runtime'; folder=rt/'data/season_snapshots'; archived=folder/'frozen'
    archived.mkdir(parents=True)
    snap={'snapshot_utc':W8.astimezone(timezone.utc).isoformat(),'espn':{'season':2026,'week':8},
          'source_status':{key:{'ok':True} for key in ('espn','sleeper','nflverse_rosters',
                 'nflverse_matchups','nfl_official_rosters','nfl_official')}}
    raw=json.dumps(snap).encode()
    (folder/'latest.json').write_bytes(raw)
    (archived/'snapshot.json').write_bytes(raw)
    result=m.snapshot_identity(rt,8,now=W8+timedelta(seconds=10))
    assert result['sha256']==hashlib.sha256(raw).hexdigest()
    snap['source_status']['sleeper']['ok']=False
    (folder/'latest.json').write_text(json.dumps(snap))
    (archived/'snapshot.json').write_text(json.dumps(snap))
    with pytest.raises(m.Blocked,match='FRESH_PROVIDER_UNHEALTHY_SLEEPER'):
        m.snapshot_identity(rt,8,now=W8+timedelta(seconds=10))


def test_capture_exact_snapshot_binding_not_only_same_week(tmp_path):
    rt=tmp_path/'runtime'; folder=rt/'data/season_predictions/closure';folder.mkdir(parents=True)
    ts=W8.isoformat()
    snap={'timestamp':ts}
    raw={'snapshot_utc':ts,'captured_utc':(W8+timedelta(minutes=1)).isoformat(),
         'measurement_contract':'A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034','season':2026,'week':8}
    (folder/'pregame_2026_w08_test.json').write_text(json.dumps(raw))
    assert m.capture_identity(rt,snap,8)['path'].endswith('test.json')
    raw['snapshot_utc']=(W8-timedelta(seconds=1)).isoformat()
    (folder/'pregame_2026_w08_test.json').write_text(json.dumps(raw))
    with pytest.raises(m.Blocked,match='CAPTURE_MISSING_OR_AMBIGUOUS_FOR_SNAPSHOT'):
        m.capture_identity(rt,snap,8)


def test_private_receipt_create_only(tmp_path):
    f=tmp_path/'private.json'
    m.atomic_private_json(f,{'contract':m.CONTRACT})
    with pytest.raises(FileExistsError):m.atomic_private_json(f,{'contract':m.CONTRACT})
    assert json.loads(f.read_text())['contract']==m.CONTRACT


def test_report_never_certifies_positive_transaction():
    r=m.safe_report(Path('/test'),Path('/test'),week=8,slot='WED',state='INCOMPLETE_COVERAGE',
       stages=list(m.PHASES[:-1]),blocker='ACTION_CERTIFICATION_PENDING',
       observation_utc=W8.isoformat(),queue=[{'candidate':'SIMULATED'}])
    assert not r['recommendation_certified'] and r['transaction_authority']=='NONE'
    assert r['espn_writes'] is False and r['operator_state']=='INCOMPLETE_COVERAGE'
    with pytest.raises(m.Blocked,match='UNRECOGNIZED_REPORT_STATE'):
        m.safe_report(Path('.'),Path('.'),week=8,slot='WED',state='COMPLETE_READY',
           stages=[],blocker=None,observation_utc=W8.isoformat())


def setup_activation(tmp_path,monkeypatch):
    root=tmp_path/'fantasy_football';root.mkdir()
    rt=root/m.NATIVE_RUNTIME
    (rt/'data/season_decisions').mkdir(parents=True)
    monkeypatch.setattr(m,'preflight',lambda root,now,week:rt)
    monkeypatch.setattr(m,'write_verified_mc_evidence',lambda *a,**kw:{'operator_v2_commissioned':False})
    activation=rt/'data/season_decisions/weekly_operator_v2_commissioning.json'
    activation.write_text(json.dumps({'contract':m.CONTRACT,'commissioned':True,
       'operator_source_sha256':m.digest(PATH),'runtime_version':'0.36'}))
    return root,rt,activation


def test_no_live_read_before_commissioning(tmp_path,monkeypatch):
    root,rt,activation=setup_activation(tmp_path,monkeypatch)
    activation.unlink();seen=[]
    with pytest.raises(m.Blocked,match='V2_WORKFLOW_NOT_COMMISSIONED'):
        m.execute(root,now=W8,scoreboard_fetch=lambda:seen.append(1))
    assert not seen


def test_wrong_activation_cannot_launch_provider_or_write(tmp_path,monkeypatch):
    root,rt,activation=setup_activation(tmp_path,monkeypatch)
    activation.write_text(json.dumps({'contract':m.CONTRACT,'commissioned':True,
       'operator_source_sha256':'wrong','runtime_version':'0.36'}))
    with pytest.raises(m.Blocked,match='V2_ACTIVATION_IDENTITY_INVALID'):
        m.execute(root,now=W8)
    assert not list((rt/'data/season_decisions').glob('*.launch.json'))


def test_complete_routing_never_yields_uncertified_action(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    call=[]
    monkeypatch.setattr(m,'run_native_cli',lambda runtime,*args,**kw:call.append(args[0]))
    monkeypatch.setattr(m,'snapshot_identity',lambda rt,week,**kw:{'timestamp':W8.isoformat(),'sha256':'sha'})
    monkeypatch.setattr(m,'capture_identity',lambda rt,snap,week:{'sha256':'cap','path':'capture.json'})
    controller=SimpleNamespace(run=lambda root,**kw:{'phase':'READONLY_DECISION_REVIEW',
                   'authority':'NONE','queue':[{'kind':'TRADE'}],
                   'receipt_sha256':'a'*64})
    a=m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=controller)
    assert call==['season-sync','closure-capture']
    assert a['completed_phases']==['CALENDAR','SYNC','CAPTURE','MC','REVIEW']
    assert a['operator_state']=='INCOMPLETE_COVERAGE'
    assert a['blocker']=='FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED'
    again=m.execute(root,now=W8,scoreboard_fetch=lambda:pytest.fail('DUPLICATE_FETCH'))
    assert again==a


def test_uncertain_started_slot_never_auto_replays(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    monkeypatch.setattr(m,'run_native_cli',lambda runtime,*args,**kw: (_ for _ in ()).throw(m.Blocked('SYNC_DOWN')))
    a=m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                controller=SimpleNamespace())
    assert a['operator_state']=='BLOCKED_HEALTH' and a['espn_writes'] is False
    assert a['completed_phases']==['CALENDAR']
    # No second sync within the same trigger; only stored failure is reused.
    assert m.execute(root,now=W8,scoreboard_fetch=lambda:pytest.fail('SHOULD_REUSE')) == a


def test_direct_source_never_posts_transactions():
    code=PATH.read_text('utf-8')
    assert all(token not in code for token in ('requests.post(', 'requests.patch(',
                 'requests.delete(', 'fetch_private_league(', 'modify_lineup(',
                 'submit_waiver(', 'sync_season_snapshot(', 'evaluate_trade('))


def _fake_frozen_phase_evidence(monkeypatch):
    monkeypatch.setattr(m,'snapshot_identity',lambda rt,week,**kw:
                        {'timestamp':W8.astimezone(timezone.utc).isoformat(),
                         'sha256':'a'*64,'week':week})
    monkeypatch.setattr(m,'capture_identity',lambda rt,snap,week:
                        {'sha256':'b'*64,'path':'data/season_predictions/closure/pregame_2026_w08_x.json',
                         'captured_utc':W8.astimezone(timezone.utc).isoformat()})
    monkeypatch.setattr(m,'snapshot_reuse',lambda rt,week,**kw:
                        m.snapshot_identity(rt,week))
    monkeypatch.setattr(m,'capture_reuse',lambda rt,snap,week,**kw:
                        m.capture_identity(rt,snap,week))


def _mc_ok(*args, **kwargs):
    return {'phase':'READONLY_DECISION_REVIEW','authority':'NONE','queue':[],
            'receipt_sha256':'c'*64}


def test_crash_after_capture_resumes_without_repeat_sync_capture(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    _fake_frozen_phase_evidence(monkeypatch)
    native=[]
    monkeypatch.setattr(m,'run_native_cli',lambda rt,*args,**kwargs:native.append(args[0]))
    def crash(*args,**kwargs):raise KeyboardInterrupt('simulated process termination')
    with pytest.raises(KeyboardInterrupt):
        m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                  controller=SimpleNamespace(run=crash))
    assert native==['season-sync','closure-capture']
    out=m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                  controller=SimpleNamespace(run=_mc_ok))
    assert native==['season-sync','closure-capture']
    assert out['completed_phases']==['CALENDAR','SYNC','CAPTURE','MC','REVIEW']
    assert out['operator_state']=='INCOMPLETE_COVERAGE'
    receipts=list((rt/'data/season_decisions').glob('*.done.json'))
    assert len(receipts)==3
    assert {json.loads(f.read_text())['phase'] for f in receipts}=={'SYNC','CAPTURE','MC'}
    assert m.execute(root,now=W8,scoreboard_fetch=lambda:pytest.fail('DUPLICATE_GET'))==out


def test_crash_during_sync_blocks_new_sync(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    native=[]
    def die(rt,*args,**kwargs):
        native.append(args[0]);raise KeyboardInterrupt('process stopped')
    monkeypatch.setattr(m,'run_native_cli',die)
    with pytest.raises(KeyboardInterrupt):
        m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=SimpleNamespace())
    assert native==['season-sync']
    result=m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=SimpleNamespace())
    assert result['blocker']=='PHASE_OUTCOME_UNCERTAIN_SYNC'
    assert native==['season-sync'] and result['completed_phases']==['CALENDAR']
    assert result['transaction_authority']=='NONE'


def test_crash_during_capture_does_not_reinvoke_capture(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    _fake_frozen_phase_evidence(monkeypatch)
    native=[]
    def launch(rt,*args,**kwargs):
        native.append(args[0])
        if args[0]=='closure-capture':raise KeyboardInterrupt('capture interrupted')
    monkeypatch.setattr(m,'run_native_cli',launch)
    with pytest.raises(KeyboardInterrupt):
        m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=SimpleNamespace())
    result=m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=SimpleNamespace())
    assert native==['season-sync','closure-capture']
    assert result['blocker']=='PHASE_OUTCOME_UNCERTAIN_CAPTURE'
    assert result['completed_phases']==['CALENDAR','SYNC']


def test_corrupted_sync_phase_receipt_rejected_on_resume(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    _fake_frozen_phase_evidence(monkeypatch)
    monkeypatch.setattr(m,'run_native_cli',lambda rt,*a,**k:None)
    with pytest.raises(KeyboardInterrupt):
        m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                  controller=SimpleNamespace(run=lambda *a,**k:(_ for _ in ()).throw(KeyboardInterrupt())))
    receipt=next((rt/'data/season_decisions').glob('*.sync.done.json'))
    raw=json.loads(receipt.read_text())
    raw['facts']['sha256']='x'*64
    receipt.write_text(json.dumps(raw))
    result=m.execute(root,now=W8,scoreboard_fetch=lambda:{},controller=SimpleNamespace(run=_mc_ok))
    assert result['blocker']=='PHASE_RESULT_IDENTITY_CHANGED_SYNC'
    assert result['completed_phases']==['CALENDAR']


def test_phase_begin_rejects_source_or_dependency_identity_change(tmp_path):
    folder=tmp_path/'private';folder.mkdir()
    begin,first=m.phase_begin(folder,'w8','SYNC',launch_sha256='a'*64,
                               dependencies={'week':8},source_sha256='b'*64)
    assert first and begin.exists()
    same,again=m.phase_begin(folder,'w8','SYNC',launch_sha256='a'*64,
                               dependencies={'week':8},source_sha256='b'*64)
    assert not again and same==begin
    with pytest.raises(m.Blocked,match='PHASE_BEGIN_IDENTITY_CHANGED_SYNC'):
        m.phase_begin(folder,'w8','SYNC',launch_sha256='a'*64,
                      dependencies={'week':9},source_sha256='b'*64)
    m.phase_complete(folder,'w8','SYNC',begin=begin,facts={'sha256':'c'*64})
    with pytest.raises(m.Blocked,match='PHASE_RESULT_IDENTITY_CHANGED_SYNC'):
        m.phase_complete(folder,'w8','SYNC',begin=begin,facts={'sha256':'d'*64})


def test_saved_phase_max_age_and_tampered_snapshot(tmp_path):
    rt=tmp_path/'runtime';base=rt/'data/season_snapshots';archive=base/'epoch'
    archive.mkdir(parents=True)
    snap={'snapshot_utc':W8.astimezone(timezone.utc).isoformat(),
          'espn':{'season':2026,'week':8},
          'source_status':{k:{'ok':True} for k in
             ('espn','sleeper','nflverse_rosters','nflverse_matchups',
              'nfl_official_rosters','nfl_official')}}
    raw=json.dumps(snap).encode();(archive/'snapshot.json').write_bytes(raw)
    (base/'latest.json').write_bytes(raw)
    assert m.snapshot_reuse(rt,8,now=W8+timedelta(minutes=60))['sha256'] == hashlib.sha256(raw).hexdigest()
    with pytest.raises(m.Blocked,match='SAVED_SYNC_TOO_OLD'):
        m.snapshot_reuse(rt,8,now=W8+timedelta(hours=3))
    (base/'latest.json').write_bytes(b'{}')
    with pytest.raises(m.Blocked,match='FRESH_SNAPSHOT_WRONG_WEEK'):
        m.snapshot_reuse(rt,8,now=W8+timedelta(minutes=5))


def test_native_mc_receipt_required_before_done_phase(tmp_path,monkeypatch):
    root,rt,_=setup_activation(tmp_path,monkeypatch)
    scoreboard(monkeypatch)
    _fake_frozen_phase_evidence(monkeypatch)
    monkeypatch.setattr(m,'run_native_cli',lambda *a,**k:None)
    def no_receipt(*a,**k):return {'phase':'READONLY_DECISION_REVIEW','authority':'NONE','queue':[]}
    result=m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                     controller=SimpleNamespace(run=no_receipt))
    assert result['blocker']=='NATIVE_MC_RECEIPT_IDENTITY_MISSING'
    assert not list((rt/'data/season_decisions').glob('*.mc.done.json'))
    assert result['transaction_authority']=='NONE'


def test_trial_entrypoint_requires_explicit_ack(monkeypatch,capsys):
    seen=[]
    monkeypatch.setattr(m, 'execute',lambda *args,**kw:seen.append(kw))
    # Avoid mixing real current week with the pinned 2026 week fixture.
    monkeypatch.setattr(m,'selected_week',lambda now:8)
    assert m.main(['--week','8','--mode','trial'])==3
    assert not seen
    assert 'EXPLICIT_LIVE_TRIAL_ACK_REQUIRED' in capsys.readouterr().out


def test_trial_executes_without_fabricated_v2_activation(tmp_path,monkeypatch):
    root,rt,activation=setup_activation(tmp_path,monkeypatch)
    activation.unlink()
    scoreboard(monkeypatch)
    _fake_frozen_phase_evidence(monkeypatch)
    invoked=[]
    monkeypatch.setattr(m,'run_native_cli',lambda rt,*args,**kw:invoked.append(args[0]))
    result=m.execute(root,now=W8,scoreboard_fetch=lambda:{},
                     controller=SimpleNamespace(run=_mc_ok),commissioning_trial=True)
    assert result['commissioning_trial'] is True
    assert result['operator_state']=='INCOMPLETE_COVERAGE'
    assert result['recommendation_certified'] is False
    assert result['transaction_authority']=='NONE'
    assert result['completed_phases']==list(m.PHASES[:-1])
    assert invoked==['season-sync','closure-capture']
    assert not activation.exists()
    assert any('trial' in p.name for p in (rt/'data/season_decisions').glob('*.launch.json'))
    assert m.execute(root,now=W8,scoreboard_fetch=lambda:pytest.fail('SECOND_NETWORK_CALL'),
                     commissioning_trial=True)==result
    activation.write_text(json.dumps({'contract':m.CONTRACT,'commissioned':True,
       'operator_source_sha256':m.digest(PATH),'runtime_version':'0.36'}))
    with pytest.raises(m.Blocked,match='TRIAL_SLOT_EXISTS_NO_PRODUCTION_DOUBLE_RUN'):
        m.execute(root,now=W8)


def test_verified_m1a_evidence_from_fresh_runtime_and_memory(tmp_path,monkeypatch):
    import types
    root=tmp_path/'fantasy_football';root.mkdir()
    rt=root/m.NATIVE_RUNTIME
    decision_dir=rt/'data/season_decisions';decision_dir.mkdir(parents=True)
    config=rt/'config/league.json';config.parent.mkdir(parents=True)
    config.write_text('public safe config fixture')
    expected_module=root/'tools/operations/guarded_weekly_cycle.py'
    expected_module.parent.mkdir(parents=True);expected_module.write_text('# guard fixture')
    guard=types.ModuleType('guarded_weekly_cycle')
    guard.__file__=str(expected_module)
    guard.DEPENDENCIES={'league_config':'config/league.json'}
    guard.EXPECTED_SOURCE_CHECKPOINT='validated_fixture_release'
    guard.EXPECTED_VERSION='0.36'
    guard.validate_root=lambda root_:rt
    monkeypatch.setitem(sys.modules,'guarded_weekly_cycle',guard)
    called=[]
    def fake_subprocess(*args,**kwargs):
        called.append(args[0])
        return SimpleNamespace(returncode=0,stdout=json.dumps({'healthy':True,'issues':[]}))
    monkeypatch.setattr(m.subprocess,'run',fake_subprocess)
    out=m.write_verified_mc_evidence(root,rt,now=datetime.now(timezone.utc),slot_id='week8')
    assert out['operator_v2_commissioned'] is False
    ids=list(decision_dir.glob('*commissioned_identity.json'))
    mem=list(decision_dir.glob('*memory_health.json'))
    assert len(ids)==len(mem)==1
    item=json.loads(ids[0].read_text())
    assert item['dependencies']['league_config']==hashlib.sha256(config.read_bytes()).hexdigest()
    assert item['source_checkpoint']=='validated_fixture_release' and item['commissioned'] is True
    assert item['operator_v2_commissioned'] is False
    memory=json.loads(mem[0].read_text())
    assert memory['strict'] is True
    assert memory['source_checkpoint']==item['source_checkpoint']=='validated_fixture_release'
    # The commissioned Gate A contract requires both identity and strict
    # memory receipts to carry the same exact v0.36 source checkpoint.
    assert memory['operator_v2_commissioned'] is False
    assert called and any('check_memory_health.py' in str(x) for x in called[0])


def test_m1a_evidence_failure_never_creates_identity(tmp_path,monkeypatch):
    import types
    root=tmp_path/'fantasy_football';root.mkdir(); rt=root/m.NATIVE_RUNTIME
    (rt/'data/season_decisions').mkdir(parents=True)
    guard=types.ModuleType('guarded_weekly_cycle')
    p=root/'tools/operations/guarded_weekly_cycle.py';p.parent.mkdir(parents=True);p.touch()
    guard.__file__=str(p);guard.validate_root=lambda _:rt
    guard.DEPENDENCIES={};guard.EXPECTED_SOURCE_CHECKPOINT='fixture';guard.EXPECTED_VERSION='0.36'
    monkeypatch.setitem(sys.modules,'guarded_weekly_cycle',guard)
    monkeypatch.setattr(m.subprocess,'run',lambda *args,**kwargs:
                        SimpleNamespace(returncode=1,stdout='{}',stderr='SECRET'))
    with pytest.raises(m.Blocked,match='HEALTH_STRICT_MEMORY_COMMAND_FAILED'):
        m.write_verified_mc_evidence(root,rt,now=datetime.now(timezone.utc),slot_id='w8')
    assert not list((rt/'data/season_decisions').glob('*commissioned_identity.json'))


def test_trial_success_exit_is_not_transaction_approval(monkeypatch,capsys):
    monkeypatch.setattr(m,'selected_week',lambda now:8)
    monkeypatch.setattr(m,'execute',lambda *args,**kw: {
        'contract':m.CONTRACT,'season':2026,'week':8,'slot':'MON',
        'operator_state':'INCOMPLETE_COVERAGE',
        'completed_phases':list(m.PHASES[:-1]),
        'blocker':'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED',
        'transaction_authority':'NONE','commissioning_trial':True})
    assert m.main(['--week','8','--mode','trial','--ack-live-readonly'])==0
    output=capsys.readouterr().out
    assert 'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED' in output
    assert 'ESPN_ACTION_AUTHORITY=NONE' in output


def test_native_operational_health_contract_rejects_missing_checkpoint(monkeypatch):
    from src import weekly_operational_health as gate_a
    monkeypatch.setattr(gate_a,'capture_integrity_state',lambda cap:(True,[]))
    expected='validated_fixture_release'
    identity={'commissioned':True,'source_checkpoint':expected,'runtime_version':'0.36',
              'dependencies':{'league_config':'a'*64}}
    common=dict(snapshot={'source_status':{
                p:({'complete':True} if p=='nfl_official_rosters' else {'ok':True})
                for p in gate_a.REQUIRED_PROVIDER_KEYS}}, capture={'present':True},
                commissioning_identity=identity, observed_dependencies={'league_config':'a'*64},
                observed_runtime_version='0.36',persistence_state=SimpleNamespace(failed=False))
    valid=gate_a.build_operational_health_receipt(**common,memory_health={
            'status':'PASS','strict':True,'source_checkpoint':expected})
    assert valid.status=='PASS'
    invalid=gate_a.build_operational_health_receipt(**common,memory_health={
            'status':'PASS','strict':True})
    assert invalid.status=='BLOCKED_HEALTH'
    assert any(str(x).startswith('memory_health:') for x in invalid.blockers)
    assert all(not str(x).startswith('memory_health:') for x in valid.blockers)
