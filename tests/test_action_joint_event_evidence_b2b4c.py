"""B2b4c contract: supplied post-freeze event claims never become prospective truth."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

PATH=Path(__file__).resolve().parents[1]/'tools/operations/action_joint_event_evidence_b2b4c.py'
FREEZE='2026-10-25T18:00:00+00:00'
H=lambda v: hashlib.sha256(repr(v).encode()).hexdigest()


def prepare(monkeypatch, *, blocked=False, source_mutation=False):
    cases=[]
    for order in (['A','B'],['B','A']):
        steps=[{'offer_id':oid, 'partner_team_id':2 if oid=='A' else 3,
                'released_to_field_ids':[71 if oid=='A' else 72]} for oid in order]
        cases.append({'offer_order':order,'steps':steps,
             'released_to_field_ids':[71,72],
             'state':'BLOCKED' if blocked else 'CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED'})
    def upstream(s,c,r,l,*args):
        if source_mutation:s['espn']['week']=9
        return {'orders':2,'branch_pairs_per_order':1,'cases':copy.deepcopy(cases)}
    mod=types.ModuleType('action_frontier')
    mod.canonical_sha256=H
    mod.CertificationBlocked=ValueError
    monkeypatch.setitem(sys.modules,'action_frontier',mod)
    mod2=types.ModuleType('action_joint_state_b2b4a')
    mod2.audit=upstream
    monkeypatch.setitem(sys.modules,'action_joint_state_b2b4a',mod2)
    spec=importlib.util.spec_from_file_location('test_b2b4c_isolated',PATH)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    data=({'snapshot_utc':FREEZE,'espn':{'week':8,
            'teams':[{'team_id':1},{'team_id':2},{'team_id':3},{'team_id':4}]}},
          {'capture':True},{'team_id':1},{'roster':{}})
    return obj,data


def envelope(data,events=None,asof='2026-10-27T18:00:00Z'):
    return {'frozen_snapshot_sha256':H(data[0]),'observed_as_of_utc':asof,
            'events':events or []}


def event(mod,data,kind,case=0,time='2026-10-26T12:00:00Z',
          observed='2026-10-26T12:01:00Z',**other):
    return dict(kind=kind,case_index=case,event_at_utc=time,observed_at_utc=observed,
                source_kind=mod.SOURCE,source_sha256='a'*64,
                frozen_snapshot_sha256=H(data[0]),**other)


def evaluate(mod,data,evidence=None):
    return mod.audit(*data,'A','B',[],[],event_evidence=evidence)


def test_no_event_is_unknown_and_not_future_probability(monkeypatch):
    mod,data=prepare(monkeypatch)
    copy_data=copy.deepcopy(data)
    report=evaluate(mod,data)
    assert report['cases_seen']==2 and report['supplied_events']==0
    assert all(x['event_order'].startswith('UNKNOWN_') for x in report['cases'])
    assert all(x['release_field_status']=='UNKNOWN' for x in report['cases'])
    assert report['conditional_joint_acquisition_probability']=='UNKNOWN'
    assert report['release_acquisition_field_utility']=='NOT_COMPUTED'
    assert report['certified_actions']==0 and report['espn_action_authority']=='NONE'
    assert data==copy_data


def test_two_processed_steps_are_post_freeze_not_prospective(monkeypatch):
    mod,data=prepare(monkeypatch)
    ev=[event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A'),
        event(mod,data,'TRADE_PROCESSED',step_index=1,offer_id='B',
              time='2026-10-26T13:00:00Z', observed='2026-10-26T13:01:00Z')]
    got=evaluate(mod,data,envelope(data,ev))
    assert got['cases'][0]['event_order']=='SUPPLIED_ORDER_CONSISTENT_POST_FREEZE_NOT_PREDICTIVE'
    assert got['cases'][1]['event_order'].startswith('UNKNOWN_')
    assert got['source_authentication']=='NOT_INDEPENDENTLY_ATTESTED'
    assert got['observation_is_post_freeze_not_prospective'] is True


def test_reverse_processing_is_not_silently_swapped(monkeypatch):
    mod,data=prepare(monkeypatch)
    ev=[event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A',
              time='2026-10-26T13:00:00Z',observed='2026-10-26T13:01:00Z'),
        event(mod,data,'TRADE_PROCESSED',step_index=1,offer_id='B')]
    with pytest.raises(ValueError,match='PROCESSING_ORDER_CONTRADICTS_CASE'):
        evaluate(mod,data,envelope(data,ev))


def test_supplied_release_status_and_pickup_not_market_forecast(monkeypatch):
    mod,data=prepare(monkeypatch)
    events=[event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A'),
      event(mod,data,'RELEASE_STATUS',asset_id=71,market_status='WAIVERS',
            time='2026-10-26T12:02:00Z',observed='2026-10-26T12:03:00Z'),
      event(mod,data,'RELEASE_STATUS',asset_id=71,market_status='FREEAGENT',
            time='2026-10-26T12:04:00Z',observed='2026-10-26T12:05:00Z'),
      event(mod,data,'THIRD_PARTY_ACQUIRED',asset_id=71,actor_team_id=4,
            time='2026-10-26T12:06:00Z',observed='2026-10-26T12:07:00Z')]
    original=copy.deepcopy(events)
    got=evaluate(mod,data,envelope(data,events))
    row=got['cases'][0]
    assert row['third_party_acquisitions_supplied']==1
    assert row['release_field_status']=='SUPPLIED_DOWNSTREAM_UPTAKE_POST_FREEZE_NOT_CAUSAL_PREDICTION'
    assert row['event_order']=='PARTIAL_SUPPLIED_PROCESSING_NOT_DECISION_TIME_PROOF'
    assert events==original


def test_waiver_or_missing_transition_not_assumed_success(monkeypatch):
    mod,data=prepare(monkeypatch)
    base=[event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A')]
    uptake=event(mod,data,'THIRD_PARTY_ACQUIRED',asset_id=71,actor_team_id=4,
                 time='2026-10-26T12:04:00Z',observed='2026-10-26T12:05:00Z')
    with pytest.raises(ValueError,match='LACKS_SUPPLIED_FREEAGENT'):
        evaluate(mod,data,envelope(data,base+[uptake]))
    waiver=event(mod,data,'RELEASE_STATUS',asset_id=71,market_status='WAIVERS',
                 time='2026-10-26T12:02:00Z',observed='2026-10-26T12:03:00Z')
    with pytest.raises(ValueError,match='LACKS_SUPPLIED_FREEAGENT'):
        evaluate(mod,data,envelope(data,base+[waiver,uptake]))


def test_release_cannot_appear_before_process_or_without_it(monkeypatch):
    mod,data=prepare(monkeypatch)
    release=event(mod,data,'RELEASE_STATUS',asset_id=71,market_status='FREEAGENT')
    with pytest.raises(ValueError,match='WITHOUT_PROCESSING'):
        evaluate(mod,data,envelope(data,[release]))
    processed=event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A',
          time='2026-10-26T13:00:00Z', observed='2026-10-26T13:01:00Z')
    with pytest.raises(ValueError,match='PRECEDES_PROCESSING'):
        evaluate(mod,data,envelope(data,[processed,release]))


def test_wrong_source_binding_and_future_event_rejected(monkeypatch):
    mod,data=prepare(monkeypatch)
    t=event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A')
    t['source_sha256']='impossible'
    with pytest.raises(ValueError,match='SOURCE_OR_FROZEN_BINDING'):
        evaluate(mod,data,envelope(data,[t]))
    t=event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A',
            time='2026-10-28T12:00:00Z',observed='2026-10-28T12:01:00Z')
    with pytest.raises(ValueError,match='POST_FREEZE_EVENT_CHRONOLOGY'):
        evaluate(mod,data,envelope(data,[t]))


def test_duplicate_event_and_wrong_asset_and_blocked_case(monkeypatch):
    mod,data=prepare(monkeypatch)
    e=event(mod,data,'TRADE_PROCESSED',step_index=0,offer_id='A')
    with pytest.raises(ValueError,match='DUPLICATE'):
        evaluate(mod,data,envelope(data,[e,copy.deepcopy(e)]))
    bad=event(mod,data,'RELEASE_STATUS',asset_id=999,market_status='FREEAGENT')
    with pytest.raises(ValueError,match='UNRELATED_RELEASE_EVENT_ASSET'):
        evaluate(mod,data,envelope(data,[bad]))
    blocked,docs=prepare(monkeypatch,blocked=True)
    with pytest.raises(ValueError,match='ATTACHED_TO_BLOCKED'):
        evaluate(blocked,docs,envelope(docs,[event(blocked,docs,'TRADE_PROCESSED',step_index=0,offer_id='A')]))


def test_participants_cannot_masquerade_as_third_party(monkeypatch):
    mod,data=prepare(monkeypatch)
    for actor in (1,2,3):
        claim=event(mod,data,'THIRD_PARTY_ACQUIRED',asset_id=71,actor_team_id=actor)
        with pytest.raises(ValueError,match='THIRD_PARTY_ACTOR_INVALID'):
            evaluate(mod,data,envelope(data,[claim]))

def test_adversarial_upstream_mutation_detected(monkeypatch):
    mod,data=prepare(monkeypatch,source_mutation=True)
    with pytest.raises(ValueError,match='FROZEN_SOURCE_MUTATED'):
        evaluate(mod,data)


def test_budget_and_identity_and_aware_clock(monkeypatch):
    mod,data=prepare(monkeypatch)
    with pytest.raises(ValueError,match='EVENT_BUDGET'):
        evaluate(mod,data,envelope(data,[{}]*65))
    evidence=envelope(data)
    evidence['frozen_snapshot_sha256']='0'*64
    with pytest.raises(ValueError,match='EVIDENCE_FROZEN_HASH'):
        evaluate(mod,data,evidence)
    data[0]['snapshot_utc']='2026-10-25T18:00:00'
    with pytest.raises(ValueError,match='FROZEN_SNAPSHOT_CLOCK'):
        evaluate(mod,data)


def test_no_native_mc_or_provider_or_action_write():
    raw=PATH.read_text(encoding='utf-8')
    for token in ('--execute-native','requests.post(', 'urlopen(', 'fetch_private_league(',
                  'subprocess.run(', 'create_trade(', 'os.system('):
        assert token not in raw
    assert 'ACTION_AUTHORITY=NONE' in raw
