"""M1b source-only cutoff/refresh planning boundary, no network or runtime."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pathlib import Path
import importlib.util
import pytest

MODULE = Path(__file__).resolve().parents[1] / 'tools/operations/weekly_operator_deadline_authority.py'
SPEC = importlib.util.spec_from_file_location('weekly_operator_deadline_authority', MODULE)
auth = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(auth)
NOW = datetime(2026, 10, 23, 14, 0, tzinfo=timezone.utc)
DIGEST = 'a' * 64


def lock(now=NOW, minutes=300):
    return {'phase': 'M1B_PRE_REFRESH_LIVE_OWNED_LOCK_READONLY',
            'status': 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED',
            'calendar_corrob_source': auth.ESPN_PUBLIC_NFLVERSE,
            'season': 2026, 'week': 7, 'fresh_authenticated_espn_gets': 1,
            'unknown_live_lock_records': 0, 'future_unlocked_records': 14,
            'earliest_future_unlocked_kickoff_utc': (now+timedelta(minutes=minutes)).isoformat(),
            'public_calendar_check_age_seconds': 8, 'live_roster_check_age_seconds': 0,
            'espn_writes': False, 'action_authority': 'NONE', 'owned_changed': 4}


def shape():
    return {'source': 'ESPN_PRIVATE_MSETTINGS', 'probe':'M1B_PRIVATE_ESPN_RULE_FIELD_SHAPES_V3',
            'cutoff_certification': {'source_shape_only': True}, 'action_authority':'NONE',
            'acquisitionSettings': {'fields': {'waiverProcessHour':'INTEGER',
                                                 'waiverProcessDays':'ARRAY'}}}


def measure(now=NOW, duration=600, buffer=600):
    return {'source':'LOCAL_MEASURED_SIX_PROVIDER_SYNC', 'runtime_version':'0.36',
            'receipt_sha256': DIGEST, 'measured_at_utc': now.isoformat(),
            'duration_seconds': duration,'buffer_seconds': buffer}


def proof(kind, now=NOW, offset=150, effective_offset=200):
    out={'family':kind, 'source':'LIVE_ESPN_ACTION_SCREEN',
         'source_sha256':DIGEST,'candidate_scope_sha256':'b'*64,
         'observed_at_utc':now.isoformat(),
         'cutoff_utc':(now+timedelta(minutes=offset)).isoformat()}
    if kind=='trade':out['effective_utc']=(now+timedelta(minutes=effective_offset)).isoformat()
    return out


def run(**kw):
    data={'now':NOW,'live_lock_result':lock(), 'live_observed_at_utc': NOW.isoformat(),
          'rule_source_shapes':shape(),'refresh_measurement':measure()}
    data.update(kw)
    return auth.classify(**data)


def test_valid_provisional_budget_is_not_authority():
    r=run()
    assert r['planning_status']=='PROVISIONAL_PLANNING_WINDOW_NOT_REFRESH_AUTHORITY'
    assert r['minimum_after_refresh_minutes']==80
    assert r['measured_refresh_plus_buffer_minutes']==20
    assert r['total_planning_minutes']==100
    assert r['lineup_window']=='GAME_LOCK_WINDOW_OBSERVED_NOT_ACTION_AUTHORITY'
    assert r['waiver_window']['classification']=='BLOCKED_EXACT_CUTOFF_UNVERIFIED'
    assert r['trade_window']['classification']=='BLOCKED_EXACT_CUTOFF_UNVERIFIED'
    assert r['refresh_authority']==r['capture_authority']==r['action_authority']=='NONE'
    assert r['espn_writes'] is False and r['native_mc_started'] is False


def test_shape_proves_no_transaction_cutoffs():
    r=run(rule_source_shapes=shape())
    assert r['transaction_source_shapes_observed'] is True
    assert r['transaction_source_shapes_are_cutoffs'] is False
    assert r['waiver_window']['classification'].startswith('BLOCKED')

@pytest.mark.parametrize('bad', [None, {}, {'source':'ESPN_PRIVATE_MSETTINGS', 'probe':'M1B_PRIVATE_ESPN_RULE_FIELD_SHAPES_V2'},
                                 {'source':'ESPN_PRIVATE_MSETTINGS','probe':'M1B_PRIVATE_ESPN_RULE_FIELD_SHAPES_V3','cutoff_certification':{'source_shape_only': False}},
                                 {'source':'ESPN_PRIVATE_MSETTINGS','probe':'M1B_PRIVATE_ESPN_RULE_FIELD_SHAPES_V3','cutoff_certification':None}])
def test_invalid_or_absent_shapes_do_not_change_lineup_window(bad):
    r=run(rule_source_shapes=bad)
    assert r['transaction_source_shapes_observed'] is False
    assert r['lineup_window']=='GAME_LOCK_WINDOW_OBSERVED_NOT_ACTION_AUTHORITY'

@pytest.mark.parametrize('bad', [None, {}, {'source':'LOCAL_MEASURED_SIX_PROVIDER_SYNC', 'duration_seconds':600},
                                 measure(duration=0), measure(buffer=0),measure(duration=True),measure(duration=7201)])
def test_missing_or_invalid_refresh_measurement_blocks_planning(bad):
    r=run(refresh_measurement=bad)
    assert r['planning_status'].startswith('BLOCKED_REFRESH')
    assert r['measured_refresh_plus_buffer_minutes'] is None


def test_stale_refresh_receipt_blocks():
    m=measure();m['measured_at_utc']=(NOW-timedelta(days=15)).isoformat()
    assert run(refresh_measurement=m)['planning_status']=='BLOCKED_REFRESH_MEASUREMENT_UNVERIFIED'

@pytest.mark.parametrize('minutes', [100, 99, 0, -1])
def test_positive_slack_required_not_equal(minutes):
    r=run(live_lock_result=lock(minutes=minutes))
    assert r['planning_status'].startswith('BLOCKED_')

@pytest.mark.parametrize('field,value', [
    ('status','BLOCKED_UNKNOWN_LIVE_LOCK'),('unknown_live_lock_records',1),
    ('fresh_authenticated_espn_gets',0),('calendar_corrob_source','UNCERTIFIED'),
    ('espn_writes',True),('action_authority','ACTION'),
    ('public_calendar_check_age_seconds',121),('live_roster_check_age_seconds',61),
    ('future_unlocked_records',0),('week',True)])
def test_live_source_guard_blocks(field,value):
    p=lock();p[field]=value
    r=run(live_lock_result=p)
    assert r['planning_status']=='BLOCKED_LIVE_GAME_LOCK_EVIDENCE'
    assert r['waiver_window']['classification']=='BLOCKED_LIVE_GAME_LOCK_EVIDENCE'


def test_live_evidence_requires_independent_current_timestamp():
    r=run(live_observed_at_utc=(NOW-timedelta(seconds=61)).isoformat())
    assert r['planning_status']=='BLOCKED_LIVE_GAME_LOCK_EVIDENCE'
    r=run(live_observed_at_utc=(NOW+timedelta(seconds=1)).isoformat())
    assert r['planning_status']=='BLOCKED_LIVE_GAME_LOCK_EVIDENCE'


def test_unknown_or_naive_now_fails():
    with pytest.raises(auth.EvidenceInvalid, match='NOW_OR_LIVE_RESULT_INVALID'):
        run(now=datetime(2026,10,23))
    with pytest.raises(auth.EvidenceInvalid):
        run(live_lock_result=None)


def test_waiver_provenance_not_guaranteed_from_settings():
    r=run(cutoff_proofs={'waiver':proof('waiver')})
    assert r['waiver_window']['classification']=='CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'
    assert r['waiver_window']['action_authority']=='NONE'
    assert r['trade_window']['classification']=='BLOCKED_EXACT_CUTOFF_UNVERIFIED'


def test_trade_envelope_independent_from_waiver():
    r=run(cutoff_proofs={'trade':proof('trade')})
    assert r['trade_window']['classification']=='CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'
    assert r['trade_window']['effective_utc'] is not None
    assert r['waiver_window']['classification']=='BLOCKED_EXACT_CUTOFF_UNVERIFIED'


def test_waiver_cutoff_passed_and_lead_insufficient():
    assert run(cutoff_proofs={'waiver':proof('waiver',offset=-1)})['waiver_window']['classification']=='BLOCKED_CLAIM_OR_SUBMISSION_CUTOFF_PASSED'
    assert run(cutoff_proofs={'waiver':proof('waiver',offset=100)})['waiver_window']['classification']=='BLOCKED_INSUFFICIENT_CUTOFF_LEAD'


def test_missing_refresh_lead_blocks_even_with_cutoff_proof():
    r=run(cutoff_proofs={'trade':proof('trade')},refresh_measurement=None)
    assert r['trade_window']['classification']=='BLOCKED_REFRESH_LEAD_UNKNOWN'

@pytest.mark.parametrize('key,val', [('source','ESPN_SETTINGS'),('source_sha256','bad'),('candidate_scope_sha256','bad'),('family','trade'),('observed_at_utc',(NOW-timedelta(seconds=62)).isoformat())])
def test_proof_fails_closed(key,val):
    p=proof('waiver');p[key]=val
    assert run(cutoff_proofs={'waiver':p})['waiver_window']['classification']=='BLOCKED_CUTOFF_PROOF_PROVENANCE'


def test_trade_effect_time_unresolved_or_earlier_blocks():
    p=proof('trade');p.pop('effective_utc')
    assert run(cutoff_proofs={'trade':p})['trade_window']['classification']=='BLOCKED_CUTOFF_TIMESTAMP_UNKNOWN'
    p=proof('trade',offset=160,effective_offset=150)
    assert run(cutoff_proofs={'trade':p})['trade_window']['classification']=='CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'
    p=proof('trade',offset=160,effective_offset=-1)
    assert run(cutoff_proofs={'trade':p})['trade_window']['classification']=='BLOCKED_TRADE_EFFECT_ALREADY_ELAPSED'


def test_no_private_fields_leak_and_no_io_in_public_api():
    p=lock();p.update({'league_id':12345,'owner':'PRIVATE_OWNER','cookie':'PRIVATE_SECRET'})
    result=run(live_lock_result=p)
    assert 'PRIVATE_' not in repr(result) and '12345' not in repr(result)
    assert result['automatic_refresh_or_capture'] is False


def test_timestamp_parser_rejects_naive_and_accepts_offset():
    assert auth.utc('2026-10-23T10:00:00-04:00')==NOW
    assert auth.utc('2026-10-23T14:00:00Z')==NOW
    assert auth.utc('2026-10-23T10:00:00') is None
    assert auth.utc('not a date') is None
