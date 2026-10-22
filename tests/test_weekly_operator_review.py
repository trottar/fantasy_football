"""Deterministic synthetic evidence; no ESPN network or football MC."""
import copy
from datetime import datetime,timezone,timedelta
import importlib.util
import json
from pathlib import Path
import pytest

SRC=Path(__file__).parents[1]/'tools/operations/weekly_operator_review.py'
spec=importlib.util.spec_from_file_location('weekly_operator_review',SRC)
op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
NOW=datetime(2026,10,22,15,0,tzinfo=timezone.utc)
SNAP_UTC='2026-10-22T14:00:00+00:00'
CAP_UTC='2026-10-22T14:01:00+00:00'
REC_UTC='2026-10-22T14:45:00+00:00'

def player(pid,name,slot,*,status='ACTIVE',team='ABC'):
    return dict(espn_id=pid,name=name,position='QB' if pid in (10,11) else 'DST',nfl_team=team,
                lineup_slot=slot,injury_status=status,active=True,lineup_locked=False,
                eligible_slots=[0,7],droppable=True,on_team_id=1)

def fixtures():
    ro=[player(10,'QB A','QB'),player(11,'QB B','BENCH',status='QUESTIONABLE'),player(12,'DST C','DST')]
    espn={'season':2026,'week':7,'league_id':42,'teams':[{'team_id':1,'roster':ro},
          {'team_id':2,'roster':[player(21,'Player C','BENCH')]}],
          'available_players':[dict(player(31,'Market D','BENCH'),fantasy_status='FREEAGENT')],
          'transactions':[{'id':7,'type':'TRADE','status':'COMPLETE'}],
          'transaction_settings':{'review_days':2}}
    snap={'snapshot_utc':SNAP_UTC,'espn':espn}
    cap={'captured_utc':CAP_UTC,'snapshot_utc':SNAP_UTC,'season':2026,'week':7,'team_id':1,
         'measurement_contract':'A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
         'league_player_predictions':{'records':[{'espn_id':10,'kickoff_utc':'2026-10-25T17:00:00+00:00'},
                                {'espn_id':11,'kickoff_utc':'2026-10-25T17:00:00+00:00'}]},
         'specialist_predictions':{'records':[{'espn_id':12,'kickoff_utc':'2026-10-23T00:15:00+00:00'}]},
         'behavioral_observation_state':{'snapshot_sha256':op._canon(snap)}}
    channels=[{'key':k,'status':'PASS / HOLD:'+k,'evidence':{}} for k in op.CHANNELS]
    channels[0]['status']='PASS / ACTION';channels[0]['evidence']={'selected_espn_ids':[11,12],
        'current_starter_espn_ids':[10,12],'lineup_legality_complete':True,'action_required':True}
    channels[6]['status']='PASS / ACTION';channels[6]['action']={'offers':[{'classification':'ACTIONABLE_OFFER'}]}
    rec={'team_id':1,'season':2026,'week':7,'generated_utc':REC_UTC,
         'overall_state':'COMPLETE / ACTION_REQUIRED',
         'provenance':{'snapshot_utc':SNAP_UTC},'operational_health':{'status':'PASS','items':[{'key':'runtime_identity','evidence':{'expected_dependencies':{'league_config':op.sha(b'league'),'model_config':op.sha(b'model'),'player_values':op.sha(b'values')}}}]},'channels':channels}
    return snap,cap,rec,copy.deepcopy(espn),copy.deepcopy(espn['available_players'])

def test_questionable_player_is_not_action_authority():
    s,c,r,e,m=fixtures();o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='CONDITIONAL_INJURY_RECHECK_REQUIRED'
    assert o['queue'][-2]['state']=='BLOCKED_UNCERTIFIED_END_TO_END_TRADE'
    assert o['action_authority']=='NONE'
    assert {x['direction'] for x in o['queue'][0]['proposals']}=={'START','BENCH'}
    assert any(x['state']=='PENDING_INJURY_STATUS' for x in o['queue'][0]['proposals'])

def test_live_injury_change_blocks_stale_lineup():
    s,c,r,e,m=fixtures();e['teams'][0]['roster'][1]['injury_status']='OUT'
    o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='CAPTURE_REQUIRED_OWNED_OR_SLOT_DRIFT'
    assert o['operator_state']=='CAPTURE_REQUIRED_OWNED_DRIFT'

def test_only_market_drift_does_not_fake_lineup_action_authority():
    s,c,r,e,m=fixtures();m[0]['fantasy_status']='WAIVERS';o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='CONDITIONAL_INJURY_RECHECK_REQUIRED'
    assert o['queue'][3]['state']=='CAPTURE_REQUIRED_MARKET_DRIFT'
    assert o['queue'][4]['state']=='CAPTURE_REQUIRED_MARKET_ROSTER_OR_PARTNER_DRIFT'

def test_no_lineup_difference_hold():
    s,c,r,e,m=fixtures();r['channels'][0]['status']='PASS / HOLD:LINEUP_AVAILABILITY'
    r['channels'][0]['evidence']['selected_espn_ids']=[10,12]
    o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='HOLD_CURRENT_STARTERS'

def test_inactive_candidate_cannot_appear_approved():
    s,c,r,e,m=fixtures();s['espn']['teams'][0]['roster'][1]['injury_status']='ACTIVE';e['teams'][0]['roster'][1]['injury_status']='ACTIVE';
    s['espn']['teams'][0]['roster'][1]['active']=False;e['teams'][0]['roster'][1]['active']=False
    o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='CONDITIONAL_INJURY_RECHECK_REQUIRED'

def test_missing_kickoff_fails_closed():
    s,c,r,e,m=fixtures();c['league_player_predictions']['records']=[x for x in c['league_player_predictions']['records'] if x['espn_id']!=11]
    o=op.decide(s,c,r,e,m,now=NOW)
    assert o['lineup_state']=='BLOCKED_LOCK_OR_KICKOFF'

def test_locked_candidate_fails_closed():
    s,c,r,e,m=fixtures();s['espn']['teams'][0]['roster'][1]['lineup_locked']=True;e['teams'][0]['roster'][1]['lineup_locked']=True
    assert op.decide(s,c,r,e,m,now=NOW)['lineup_state']=='BLOCKED_LOCK_OR_KICKOFF'

def test_unknown_starter_does_not_pass():
    s,c,r,e,m=fixtures();r['channels'][0]['evidence']['selected_espn_ids']=[999]
    with pytest.raises(op.Blocked,match='LINEUP_RECEIPT_IDENTITIES_INVALID'):
        op.decide(s,c,r,e,m,now=NOW)

def test_duplicate_owned_record_blocks():
    s,c,r,e,m=fixtures();e['teams'][0]['roster'].append(e['teams'][0]['roster'][0])
    with pytest.raises(op.Blocked,match='DUPLICATE_OR_MISSING_ID:LIVE_OWNED'):
        op.decide(s,c,r,e,m,now=NOW)

def test_missing_channel_blocks():
    s,c,r,e,m=fixtures();r['channels'].pop()
    with pytest.raises(op.Blocked,match='NINE_CHANNEL_MATRIX_INCOMPLETE'):
        op.decide(s,c,r,e,m,now=NOW)

def test_changed_partner_always_blocks_trade():
    s,c,r,e,m=fixtures();e['teams'][1]['roster'][0]['injury_status']='QUESTIONABLE'
    o=op.decide(s,c,r,e,m,now=NOW)
    assert o['live_drift']['partner_state_changed'] is True
    assert o['queue'][4]['state'].startswith('CAPTURE_REQUIRED')

def test_unknown_transaction_history_blocks_trades():
    s,c,r,e,m=fixtures();e['transactions']=[]
    assert op.decide(s,c,r,e,m,now=NOW)['queue'][4]['state'].startswith('CAPTURE_REQUIRED')

def test_missing_latest_capture_blocks(tmp_path):
    s,c,r,e,m=fixtures(); rt=tmp_path/'runtime';(rt/'data/season_snapshots/clock').mkdir(parents=True)
    (rt/'data/season_snapshots/clock/snapshot.json').write_text(json.dumps(s))
    (rt/'data/season_snapshots/latest.json').write_text(json.dumps(s))
    (rt/'data/season_predictions/closure').mkdir(parents=True)
    with pytest.raises(op.Blocked,match='CAPTURE_REQUIRED_FOR_LATEST_SNAPSHOT'):
        op.discover(rt,NOW,verify_capture=lambda x:True,canonical=op._canon)

def test_full_latest_pairing_and_mutated_capture_guard(tmp_path):
    s,c,r,e,m=fixtures();rt=tmp_path/'runtime'
    for part in ('data/season_snapshots/clock','data/season_predictions/closure','data/season_decisions'):
        (rt/part).mkdir(parents=True)
    for path,obj in [('data/season_snapshots/clock/snapshot.json',s),
       ('data/season_snapshots/latest.json',s),('data/season_predictions/closure/pregame_2026_w07_x.json',c),
       ('data/season_decisions/weekly_decision_receipt_x.json',r)]:
        (rt/path).write_text(json.dumps(obj))
    for path,raw in [('config/league.json',b'league'),('config/model.json',b'model'),
                     ('data/processed/player_values_2026.csv',b'values')]:
        (rt/path).parent.mkdir(parents=True,exist_ok=True)
        (rt/path).write_bytes(raw)
    out=op.discover(rt,NOW,verify_capture=lambda x:True,canonical=op._canon)
    assert out[-1]['week']==7
    c['behavioral_observation_state']['snapshot_sha256']='bad'
    (rt/'data/season_predictions/closure/pregame_2026_w07_x.json').write_text(json.dumps(c))
    with pytest.raises(op.Blocked,match='SNAPSHOT_CAPTURE_BINDING_INVALID'):
        op.discover(rt,NOW,verify_capture=lambda x:True,canonical=op._canon)

def test_discover_rejects_multiple_receipts(tmp_path):
    s,c,r,e,m=fixtures();rt=tmp_path/'runtime'
    for part in ('data/season_snapshots/clock','data/season_predictions/closure','data/season_decisions'):
        (rt/part).mkdir(parents=True)
    for path,obj in [('data/season_snapshots/clock/snapshot.json',s),
       ('data/season_snapshots/latest.json',s),('data/season_predictions/closure/pregame_2026_w07_x.json',c),
       ('data/season_decisions/weekly_decision_receipt_x.json',r),
       ('data/season_decisions/weekly_decision_receipt_y.json',r)]:
        (rt/path).write_text(json.dumps(obj))
    with pytest.raises(op.Blocked,match='NATIVE_NINE_CHANNEL_RECEIPT_REQUIRED_OR_AMBIGUOUS'):
        op.discover(rt,NOW,verify_capture=lambda x:True,canonical=op._canon)

def test_cli_invalid_root_fail_closed(capsys):
    code=op.main(['--project-root','/nonexistent'])
    assert code==3
    assert 'ESPN_ACTION_AUTHORITY=NONE' in capsys.readouterr().out

def test_readonly_full_operator_path_with_injected_espn(tmp_path):
    s,c,r,e,m=fixtures();rt=tmp_path/'fantasy_football'/'fantasy_season_v0_36_repack1'
    for part in ('data/season_snapshots/clock','data/season_predictions/closure',
                 'data/season_decisions','config','data/processed'):
        (rt/part).mkdir(parents=True,exist_ok=True)
    for path,obj in [('data/season_snapshots/clock/snapshot.json',s),
       ('data/season_snapshots/latest.json',s),('data/season_predictions/closure/pregame_2026_w07_x.json',c),
       ('data/season_decisions/weekly_decision_receipt_x.json',r)]:
        (rt/path).write_text(json.dumps(obj))
    for path,raw in [('config/league.json',b'league'),('config/model.json',b'model'),
                     ('data/processed/player_values_2026.csv',b'values')]:
        (rt/path).write_bytes(raw)
    before={p.relative_to(rt).as_posix():op.sha(p.read_bytes()) for p in rt.rglob('*') if p.is_file()}
    result=op.run(rt.parent,now=NOW,fetch=lambda:(e,m),
       runtime_guard=lambda root:rt,verify_capture=lambda x:True,canonical=op._canon,
       memory_guard=lambda root:None)
    after={p.relative_to(rt).as_posix():op.sha(p.read_bytes()) for p in rt.rglob('*') if p.is_file()}
    assert before==after
    assert result['lineup_state']=='CONDITIONAL_INJURY_RECHECK_REQUIRED'
    assert result['next_check_utc']=='2026-10-25T15:30:00+00:00'
    assert result['provenance']['receipt_sha256']==before['data/season_decisions/weekly_decision_receipt_x.json']


def test_dependency_drift_never_produces_decision(tmp_path):
    s,c,r,e,m=fixtures();rt=tmp_path/'runtime'
    for part in ('data/season_snapshots/clock','data/season_predictions/closure',
                 'data/season_decisions','config','data/processed'):
        (rt/part).mkdir(parents=True,exist_ok=True)
    for path,obj in [('data/season_snapshots/clock/snapshot.json',s),
       ('data/season_snapshots/latest.json',s),('data/season_predictions/closure/pregame_2026_w07_x.json',c),
       ('data/season_decisions/weekly_decision_receipt_x.json',r)]:
        (rt/path).write_text(json.dumps(obj))
    for path,raw in [('config/league.json',b'league'),('config/model.json',b'WRONG'),
                     ('data/processed/player_values_2026.csv',b'values')]:
        (rt/path).write_bytes(raw)
    with pytest.raises(op.Blocked,match='COMMISSIONED_DEPENDENCY_DRIFT:model_config'):
        op.discover(rt,NOW,verify_capture=lambda x:True,canonical=op._canon)
