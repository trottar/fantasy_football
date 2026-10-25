"""Week 8 B2b4c: retrospective *supplied* event-order evidence audit.

Pure read-only post-freeze observation versus hypothetical ordered trade cases.
A supplied receipt label/hash is NOT independent proof of ESPN provenance; an
actual source-bound collector and app-specific action proof are still absent.
No event is used as a pre-event prediction or to fit manager probabilities.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from action_frontier import canonical_sha256, CertificationBlocked
from action_joint_state_b2b4a import audit as structural_audit

CONTRACT = 'WEEK8_B2B4C_SUPPLIED_EVENT_SEQUENCE_EVIDENCE_V1'
MAX_EVENTS = 64
SHA = re.compile(r'^[0-9a-f]{64}$')
SOURCE = 'SUPPLIED_ESPN_TRANSACTION_EVENT_NOT_INDEPENDENTLY_ATTESTED'
KINDS = frozenset(('TRADE_PROCESSED', 'RELEASE_STATUS', 'THIRD_PARTY_ACQUIRED'))
STATUSES = frozenset(('FREEAGENT', 'WAIVERS', 'ROSTERED', 'UNKNOWN'))


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise CertificationBlocked(reason)


def utc(value: Any, code: str) -> datetime:
    need(isinstance(value, str), code)
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, OverflowError) as exc:
        raise CertificationBlocked(code) from exc
    need(stamp.tzinfo is not None and stamp.utcoffset() is not None, code)
    return stamp.astimezone(timezone.utc)


def _claim(value: Any, case_count: int, frozen: datetime,
           observed_as_of: datetime, snapshot_hash: str) -> dict:
    need(type(value) is dict, 'B2B4C_EVENT_NOT_MAPPING')
    need(value.get('source_kind') == SOURCE and
         isinstance(value.get('source_sha256'), str) and SHA.fullmatch(value['source_sha256']) and
         value.get('frozen_snapshot_sha256') == snapshot_hash,
         'B2B4C_EVENT_SOURCE_OR_FROZEN_BINDING_INVALID')
    kind = value.get('kind')
    need(kind in KINDS and type(value.get('case_index')) is int and
         0 <= value['case_index'] < case_count, 'B2B4C_EVENT_KIND_OR_CASE_INDEX_INVALID')
    event = utc(value.get('event_at_utc'), 'B2B4C_EVENT_TIME_UNRESOLVED')
    observed = utc(value.get('observed_at_utc'), 'B2B4C_OBSERVATION_TIME_UNRESOLVED')
    need(frozen < event <= observed <= observed_as_of,
         'B2B4C_POST_FREEZE_EVENT_CHRONOLOGY_INVALID')
    raw = {'kind':kind, 'case_index':value['case_index'], 'event':event,
           'observed':observed}
    if kind == 'TRADE_PROCESSED':
        need(type(value.get('step_index')) is int and value['step_index'] in (0, 1) and
             isinstance(value.get('offer_id'), str) and bool(value['offer_id']),
             'B2B4C_TRADE_PROCESS_STEP_INVALID')
        raw.update(step=value['step_index'], offer_id=value['offer_id'])
    else:
        need(type(value.get('asset_id')) is int and value['asset_id'] >= 0,
             'B2B4C_RELEASE_ASSET_ID_INVALID')
        raw['asset_id'] = value['asset_id']
        if kind == 'RELEASE_STATUS':
            need(value.get('market_status') in STATUSES,
                 'B2B4C_RELEASE_MARKET_STATUS_INVALID')
            raw['market_status'] = value['market_status']
        else:
            need(type(value.get('actor_team_id')) is int and value['actor_team_id'] >= 0,
                 'B2B4C_ACQUIRER_ID_INVALID')
            raw['actor_team_id'] = value['actor_team_id']
    return raw


def _case_audit(case: dict, events: list[dict], snapshot_team_ids: set[int], user_team_id: int) -> dict:
    result = {'offer_order':copy.deepcopy(case['offer_order']),
              'structural_state':case['state'], 'observed_processing_steps':0,
              'release_status_events_supplied':0,
              'third_party_acquisitions_supplied':0,
              'event_order':'UNKNOWN_FUTURE_PROCESSING_OR_NOT_OBSERVED',
              'release_field_status':'UNKNOWN',
              'source_authentication':'NOT_INDEPENDENTLY_ATTESTED',
              'field_response':'NOT_PREDICTED',
              'acquisition_probability':'UNKNOWN', 'action_authority':'NONE'}
    if case['state'] != 'CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED':
        need(not events, 'B2B4C_EVENT_CLAIM_ATTACHED_TO_BLOCKED_CASE')
        result['event_order']='BLOCKED_STRUCTURAL_CASE'
        return result
    need(type(case['steps']) is list and len(case['steps']) == 2 and
         all(step['offer_id'] == case['offer_order'][i] for i,step in enumerate(case['steps'])),
         'B2B4C_STRUCTURAL_STEPS_INCONSISTENT')
    trades = {}
    statuses: dict[int,list[dict]] = {}
    acquisitions: dict[int,list[dict]] = {}
    releases: dict[int,int] = {}
    for idx,step in enumerate(case['steps']):
        for pid in step['released_to_field_ids']:
            need(type(pid) is int and pid not in releases,
                 'B2B4C_DUPLICATE_RELEASE_PROVENANCE')
            releases[pid] = idx
    need(set(case['released_to_field_ids']) == set(releases),
         'B2B4C_RELEASE_LEDGER_MISMATCH')
    for record in events:
        if record['kind']=='TRADE_PROCESSED':
            idx = record['step']
            need(record['offer_id']==case['steps'][idx]['offer_id'] and idx not in trades,
                 'B2B4C_TRADE_PROCESS_IDENTITY_OR_DUPLICATE')
            trades[idx] = record
        else:
            pid = record['asset_id']
            need(pid in releases, 'B2B4C_UNRELATED_RELEASE_EVENT_ASSET')
            if record['kind']=='RELEASE_STATUS':
                statuses.setdefault(pid, []).append(record)
            else:
                participants = {user_team_id} | {step['partner_team_id'] for step in case['steps']}
                need(record['actor_team_id'] in snapshot_team_ids and
                     record['actor_team_id'] not in participants,
                     'B2B4C_THIRD_PARTY_ACTOR_INVALID')
                acquisitions.setdefault(pid, []).append(record)
    result['observed_processing_steps'] = len(trades)
    result['release_status_events_supplied'] = sum(map(len,statuses.values()))
    result['third_party_acquisitions_supplied'] = sum(map(len,acquisitions.values()))
    if len(trades)==2:
        need(trades[0]['event'] < trades[1]['event'],
             'B2B4C_SUPPLIED_PROCESSING_ORDER_CONTRADICTS_CASE')
        result['event_order']='SUPPLIED_ORDER_CONSISTENT_POST_FREEZE_NOT_PREDICTIVE'
    elif trades:
        result['event_order']='PARTIAL_SUPPLIED_PROCESSING_NOT_DECISION_TIME_PROOF'
    for pid,records in statuses.items():
        need(releases[pid] in trades, 'B2B4C_RELEASE_STATUS_WITHOUT_PROCESSING_EVENT')
        need(len({r['event'] for r in records})==len(records),
             'B2B4C_DUPLICATE_RELEASE_STATUS_TIME')
        need(all(r['event'] >= trades[releases[pid]]['event'] for r in records),
             'B2B4C_RELEASE_STATUS_PRECEDES_PROCESSING')
    for pid, records in acquisitions.items():
        need(len(records)==1 and releases[pid] in trades,
             'B2B4C_ACQUISITION_UNBOUNDED_OR_DUPLICATED')
        acquired=records[0]
        need(acquired['event'] > trades[releases[pid]]['event'],
             'B2B4C_ACQUISITION_PRECEDES_RELEASE')
        prior=[r for r in statuses.get(pid,[]) if r['event'] <= acquired['event']]
        need(prior and max(prior, key=lambda r:r['event'])['market_status']=='FREEAGENT',
             'B2B4C_ACQUISITION_LACKS_SUPPLIED_FREEAGENT_TRANSITION')
    if statuses:
        result['release_field_status']='SUPPLIED_STATUS_ONLY_NOT_FUTURE_MARKET_CERTIFICATE'
    if acquisitions:
        result['release_field_status']='SUPPLIED_DOWNSTREAM_UPTAKE_POST_FREEZE_NOT_CAUSAL_PREDICTION'
    return result


def audit(snapshot:dict, capture:dict, receipt:dict, league:dict,
          first_offer_id:str, second_offer_id:str,
          first_drop_ids:list[int], second_drop_ids:list[int],
          event_evidence:dict|None=None) -> dict:
    """Classify observed-supplied claims AFTER frozen decision time, not value them."""
    source=(snapshot,capture,receipt,league)
    before=tuple(canonical_sha256(x) for x in source)
    frozen=utc(snapshot.get('snapshot_utc'), 'B2B4C_FROZEN_SNAPSHOT_CLOCK_MISSING')
    structural=structural_audit(*source,first_offer_id,second_offer_id,
                                first_drop_ids,second_drop_ids)
    cases=structural['cases']
    need(type(cases) is list and structural['orders']==2 and
         len(cases)==2*structural['branch_pairs_per_order'] and
         1<=len(cases)<=32, 'B2B4C_SOURCE_CASE_SET_INVALID')
    espn=snapshot.get('espn') or {}
    tids={x['team_id'] for x in espn.get('teams') or []
          if type(x) is dict and type(x.get('team_id')) is int}
    need(tids and type(receipt.get('team_id')) is int and receipt['team_id'] in tids,
         'B2B4C_FROZEN_TEAM_PROVENANCE_MISSING')
    provided=event_evidence if event_evidence is not None else {
        'frozen_snapshot_sha256':before[0],
        'observed_as_of_utc':frozen.isoformat(),'events':[]}
    need(type(provided) is dict and provided.get('frozen_snapshot_sha256')==before[0],
         'B2B4C_EVIDENCE_FROZEN_HASH_MISMATCH')
    as_of=utc(provided.get('observed_as_of_utc'), 'B2B4C_AS_OF_CLOCK_INVALID')
    need(as_of>=frozen,'B2B4C_AS_OF_PRECEDES_FREEZE')
    records=provided.get('events')
    need(type(records) is list and len(records)<=MAX_EVENTS,
         'B2B4C_EVENT_BUDGET_OR_SHAPE_INVALID')
    grouped={idx:[] for idx in range(len(cases))}
    for record in records:
        checked=_claim(record,len(cases),frozen,as_of,before[0])
        grouped[checked['case_index']].append(checked)
    result=[_case_audit(case,grouped[i],tids,receipt['team_id'])
            for i,case in enumerate(cases)]
    need(tuple(canonical_sha256(x) for x in source)==before,
         'B2B4C_FROZEN_SOURCE_MUTATED')
    need(event_evidence is None or provided==event_evidence,
         'B2B4C_SUPPLIED_EVENTS_MUTATED')
    return {'contract':CONTRACT, 'frozen_sha256':dict(zip(
                ('snapshot','capture','receipt','league'),before)),
            'evidence_as_of_utc':as_of.isoformat(),
            'observation_is_post_freeze_not_prospective':True,
            'source_authentication':'NOT_INDEPENDENTLY_ATTESTED',
            'cases':result,'cases_seen':len(cases),'supplied_events':len(records),
            'conditional_joint_acquisition_probability':'UNKNOWN',
            'release_acquisition_field_utility':'NOT_COMPUTED',
            'unresolved':['INDEPENDENT_ESPN_EVENT_SOURCE_PRODUCER_NOT_COMMISSIONED',
                          'EXACT_TRADE_PROCESSING_AND_RELEASE_STATUS_NOT_PROSPECTIVELY_KNOWN',
                          'CORRELATED_MANAGER_BEHAVIOR_AND_MARKET_ACQUISITION_UNKNOWN',
                          'POST_RELEASE_FIELD_UTILITY_AND_ESPN_ACTION_LEGALITY_UNVERIFIED'],
            'state':'BLOCKED_B2B4C_SUPPLIED_EVENT_PROVENANCE_ONLY',
            'certified_actions':0,'espn_action_authority':'NONE'}


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('snapshot','capture','receipt','league'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--first-offer-id',required=True)
    p.add_argument('--second-offer-id',required=True)
    p.add_argument('--first-drop-id',action='append',type=int,default=[])
    p.add_argument('--second-drop-id',action='append',type=int,default=[])
    p.add_argument('--event-evidence',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args(argv)
    print('WEEK8 B2B4C EVENT PROVENANCE DIAGNOSTIC',flush=True)
    try:
        vals=[json.loads(getattr(a,k).read_text(encoding='utf-8-sig'))
              for k in ('snapshot','capture','receipt','league')]
        evidence=json.loads(a.event_evidence.read_text(encoding='utf-8-sig')) if a.event_evidence else None
        report=audit(*vals,a.first_offer_id,a.second_offer_id,
                     a.first_drop_id,a.second_drop_id,event_evidence=evidence)
        if a.out is not None:
            out=a.out.resolve()
            need(out.parent.name=='data' and
                 out.parent.parent.name.casefold()=='fantasy_season_v0_36_repack1' and
                 not out.exists(),'B2B4C_PRIVATE_RUNTIME_NEW_OUTPUT_ONLY')
            with out.open('x',encoding='utf-8') as f:
                json.dump(report,f,sort_keys=True,indent=2); f.write('\n')
        print('CASES='+str(report['cases_seen'])+';SUPPLIED_EVENTS='+str(report['supplied_events'])+
              ';PREDICTIVE_MC=NONE;ESPN_GETS=NONE;ESPN_WRITES=NONE;CERTIFIED_ACTIONS=0',flush=True)
        print('STATE='+report['state']+';ACTION_AUTHORITY=NONE',flush=True)
        return 0
    except (CertificationBlocked,OSError,ValueError,TypeError,KeyError) as exc:
        reason=str(exc) if isinstance(exc,CertificationBlocked) else type(exc).__name__
        print('B2B4C_BLOCKED='+reason+';ACTION_AUTHORITY=NONE',flush=True)
        return 3

if __name__=='__main__':
    raise SystemExit(main())
