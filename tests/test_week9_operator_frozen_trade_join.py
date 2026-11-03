"""Source-only, fail-closed existing v2 frozen trade-risk join regressions."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import pytest

ROOT=Path(__file__).resolve().parents[1]
OP=ROOT/'tools/operations/weekly_operator_v2.py'
CERT=ROOT/'tools/operations/action_certification.py'
sp=importlib.util.spec_from_file_location('week9_v2_operator_cert_join',OP)
operator=importlib.util.module_from_spec(sp)
sp.loader.exec_module(operator)
cp=importlib.util.spec_from_file_location('week9_existing_certifier',CERT)
cert=importlib.util.module_from_spec(cp)
cp.loader.exec_module(cert)

CHANNELS=('lineup_availability','player_waiver_free_agent','dst_waiver_free_agent',
          'kicker_waiver_free_agent','ir_reserve_open_slot_injury_replacement',
          'trade_one_for_one_player','trade_multi_player_unequal',
          'trade_specialist_inclusive','prospective_capture_provenance')


def fixture(tmp_path):
    root=tmp_path/'fantasy_football'
    operations=root/'tools/operations'
    operations.mkdir(parents=True)
    shutil.copyfile(CERT,operations/'action_certification.py')
    runtime=root/'fantasy_season_v0_36_repack1'
    snappath=runtime/'data/season_snapshots/latest.json'
    cappath=runtime/'data/season_predictions/closure/pregame_2026_w09_fixture.json'
    recpath=runtime/'data/season_decisions/weekly_decision_receipt_fixture.json'
    for p in (snappath,cappath,recpath):p.parent.mkdir(parents=True,exist_ok=True)
    snapshot={'snapshot_utc':'2026-11-02T12:00:00+00:00',
              'espn':{'season':2026,'week':9,'transaction_settings':{'trade_review_hours':48},
                      'teams':[{'team_id':1,'roster':[
                        {'espn_id':11,'name':'QB A','position':'QB','injury_status':'ACTIVE'},
                        {'espn_id':12,'name':'QB B','position':'QB','injury_status':'QUESTIONABLE'}]},
                        {'team_id':2,'roster':[{'espn_id':21,'name':'WR C','position':'WR'}]}]}}
    capture={'season':2026,'week':9,'snapshot_utc':snapshot['snapshot_utc'],
             'behavioral_observation_state':{'snapshot_sha256':cert.canonical_sha256(snapshot)}}
    capture['integrity']={'canonical_payload_sha256':cert.canonical_sha256(capture)}
    offer={'classification':'ACTIONABLE_OFFER','give_ids':[11], 'receive_ids':[21],
           'give_names':['QB A'],'receive_names':['WR C'],'receive_positions':['WR'],
           'user_auto_drop_ids':[],'user_auto_add_ids':[],'partner_auto_add_ids':[]}
    channel_rows=[{'key':k,'status':'PASS / HOLD:SCOPED'} for k in CHANNELS]
    channel_rows[6]={'key':CHANNELS[6],'status':'PASS / ACTION',
                     'action':{'offers':[offer]}}
    native={'season':2026,'week':9,'team_id':1,
            'overall_state':'COMPLETE / ACTION_REQUIRED',
            'provenance':{'snapshot_utc':snapshot['snapshot_utc'],'capture_integrity_ok':True},
            'channels':channel_rows}
    for path,obj in ((snappath,snapshot),(cappath,capture),(recpath,native)):
        path.write_text(json.dumps(obj,sort_keys=True)+'\n',encoding='utf-8')
    snap={'week':9,'sha256':operator.digest(snappath)}
    cap={'sha256':operator.digest(cappath),'path':cappath.relative_to(runtime).as_posix()}
    rh=operator.digest(recpath)
    return root,runtime,snap,cap,rh,snappath,recpath


def test_one_native_trade_remains_blocked_with_nine_channel_statuses(tmp_path,monkeypatch):
    root,runtime,snap,cap,rh,_,_=fixture(tmp_path)
    # Existing published reviewer remains the exact nine-channel semantic owner.
    monkeypatch.syspath_prepend(str(ROOT/'tools/operations'))
    report=operator.frozen_trade_risk_join(root,runtime,snap=snap,cap=cap,receipt_sha=rh)
    assert report['state']=='FROZEN_SCOPE_ONLY'
    assert report['trade_candidate_count']==1
    assert len(report['native_channel_statuses'])==9
    assert report['trade_blocker_counts']['NO_FRESH_ESPN_ACTION_SCREEN_OR_POST_MC_RECONCILIATION']==1
    assert report['certified_action_count']==0 and report['action_authority']=='NONE'


def test_tampered_frozen_snapshot_rejected(tmp_path):
    root,rt,snap,cap,rh,sp,_=fixture(tmp_path)
    sp.write_bytes(sp.read_bytes()+b' ')
    with pytest.raises(operator.Blocked,match='FROZEN_TRADE_SNAPSHOT_IDENTITY_CHANGED'):
        operator.frozen_trade_risk_join(root,rt,snap=snap,cap=cap,receipt_sha=rh)


def test_duplicate_native_receipt_rejected(tmp_path):
    root,rt,snap,cap,rh,_,rp=fixture(tmp_path)
    (rp.parent/'weekly_decision_receipt_copy.json').write_bytes(rp.read_bytes())
    with pytest.raises(operator.Blocked,match='FROZEN_TRADE_RECEIPT_JOIN_NOT_UNIQUE'):
        operator.frozen_trade_risk_join(root,rt,snap=snap,cap=cap,receipt_sha=rh)


def test_unpinned_certificate_source_rejected(tmp_path):
    root,rt,snap,cap,rh,_,_=fixture(tmp_path)
    (root/'tools/operations/action_certification.py').write_text('x=1\n',encoding='utf-8')
    with pytest.raises(operator.Blocked,match='FROZEN_TRADE_CERTIFICATION_SOURCE_DRIFT'):
        operator.frozen_trade_risk_join(root,rt,snap=snap,cap=cap,receipt_sha=rh)


def test_missing_native_receipt_rejected(tmp_path):
    root,rt,snap,cap,rh,_,rp=fixture(tmp_path)
    rp.unlink()
    with pytest.raises(operator.Blocked,match='FROZEN_TRADE_RECEIPT_JOIN_NOT_UNIQUE'):
        operator.frozen_trade_risk_join(root,rt,snap=snap,cap=cap,receipt_sha=rh)


def test_private_report_adds_scoped_summary_without_approving():
    report=operator.safe_report(Path('/fake'),Path('/fake'),week=9,slot='MON',
       state='INCOMPLETE_COVERAGE',stages=['CALENDAR','SYNC','CAPTURE','MC','REVIEW'],
       blocker='FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED',observation_utc='2026-11-02T12:00:00Z',
       frozen_trade_risk={'state':'FROZEN_SCOPE_ONLY','action_authority':'NONE'})
    assert report['frozen_trade_risk']['state']=='FROZEN_SCOPE_ONLY'
    assert report['transaction_authority']=='NONE'
    assert report['recommendation_certified'] is False
    assert report['espn_writes'] is False


def test_module_does_not_add_network_or_mc_or_escalated_authority():
    data=OP.read_text(encoding='utf-8')
    assert "'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED'" in data
    assert "'recommendation_certified': False, 'transaction_authority': 'NONE'" in data
    assert "'state': 'FROZEN_SCOPE_ONLY'" in data
