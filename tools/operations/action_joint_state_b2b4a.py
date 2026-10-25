"""Week 8 B2b4a: two-offer ordered conditional state/field-exposure audit.

Deterministic frozen structural experiment only. This neither runs predictive MC
nor estimates correlated acquisition/manager behavior. An ordered joint roster
cannot be inferred by adding two separate trade utilities. No ESPN authority.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
from pathlib import Path
from typing import Any

from action_frontier import build_frontier, canonical_sha256, CertificationBlocked
from action_portfolio_b2b2 import (audit as structural_audit, _league, _owned,
                                   _state, _available, POSITIONS)

CONTRACT = 'WEEK8_B2B4A_ORDERED_JOINT_FROZEN_STATE_V1'
MAX_TOTAL_FILLS = 4
MAX_BRANCH_PAIRS = 1 << MAX_TOTAL_FILLS


def need(ok: bool, code: str) -> None:
    if not ok:
        raise CertificationBlocked(code)


def _choose(rows: list[dict], oid: str, drops: list[int]) -> tuple[dict, dict]:
    matches = [x for x in rows if x['offer_id'] == oid]
    need(len(matches) == 1, 'B2B4A_OFFER_NOT_UNIQUE_OR_MISSING')
    chosen = [x for x in matches[0]['options'] if x['drop_ids'] == drops]
    need(len(chosen) == 1, 'B2B4A_DROP_OPTION_NOT_UNIQUE_OR_MISSING')
    return matches[0], chosen[0]



def _lattice_variables(branches: list[dict]) -> tuple[tuple[str,int],...]:
    need(isinstance(branches,list) and bool(branches), 'B2B4A_FILL_LATTICE_EMPTY')
    first=branches[0]['fill_outcomes']
    need(isinstance(first,list), 'B2B4A_FILL_LATTICE_MALFORMED')
    keys=tuple((x['side'],x['id']) for x in first)
    need(len(set(keys))==len(keys), 'B2B4A_DUPLICATE_FILL_VARIABLE')
    need(len(branches)==(1<<len(keys)), 'B2B4A_FILL_LATTICE_NOT_EXHAUSTIVE')
    signatures=set()
    for branch in branches:
        outcomes=branch.get('fill_outcomes')
        need(isinstance(outcomes,list) and
             tuple((x['side'],x['id']) for x in outcomes)==keys,
             'B2B4A_FILL_LATTICE_IDENTITY_DRIFT')
        need(all(type(x.get('conditional_success')) is bool for x in outcomes),
             'B2B4A_FILL_LATTICE_BOOLEAN_INVALID')
        bits=tuple(x['conditional_success'] for x in outcomes)
        need(bits not in signatures,'B2B4A_FILL_LATTICE_DUPLICATE_OUTCOME')
        signatures.add(bits)
    return keys

def _frozen_state(snapshot: dict) -> tuple[dict[int, dict[int,dict]], dict[int,dict]]:
    espn = snapshot.get('espn') or {}
    teams = espn.get('teams')
    need(isinstance(teams, list) and bool(teams), 'FROZEN_TEAMS_MISSING')
    rosters: dict[int,dict[int,dict]] = {}
    universe: set[int] = set()
    for team in teams:
        need(isinstance(team, dict) and type(team.get('team_id')) is int,
             'INVALID_TEAM_ID_OR_RECORD')
        tid = team['team_id']
        need(tid not in rosters, 'DUPLICATE_FROZEN_TEAM_ID')
        owned = _owned(team)
        need(not (universe & owned.keys()), 'DUPLICATE_LEAGUE_WIDE_OWNERSHIP')
        universe.update(owned)
        rosters[tid] = copy.deepcopy(owned)
    market = copy.deepcopy(_available(snapshot))
    need(not (universe & market.keys()), 'FROZEN_MARKET_ASSET_ALREADY_OWNED')
    return rosters, market


def _evidence(branch: dict) -> tuple[list[tuple[str,int]],list[str],list[str]]:
    # B2a's no-future-fill screen flags even a structurally necessary,
    # *conditionally successful* fill. Keep those as assumptions, never as
    # proof of acquisition. The current state still has to pass _state().
    def hypothetical(value: str) -> bool:
        return value.startswith('FUTURE_FILL_AT_PROCESSING_UNVERIFIED:') or value in {
            'FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE',
            'FUTURE_USER_FILL_ASSUMPTION'}
    assumptions = sorted(set(str(x) for x in branch['unresolved']
                             if hypothetical(str(x))))
    other = sorted(set(str(x) for x in branch['unresolved'] if not hypothetical(str(x))))
    fills = []
    for x in branch['fill_outcomes']:
        need(isinstance(x, dict) and x.get('side') in ('user','partner') and
             type(x.get('id')) is int and type(x.get('conditional_success')) is bool,
             'B2B4A_MALFORMED_FILL_OUTCOME')
        if x['conditional_success']:
            need(x.get('materialized_from_frozen_market') is True,
                 'FROZEN_FREEAGENT_IDENTITY_NOT_PROVEN')
            fills.append((x['side'],x['id']))
    return fills, assumptions, other


def _apply(rosters:dict[int,dict[int,dict]], market:dict[int,dict],
           offer:dict, selected:dict, branch:dict, user:int,
           target:dict[int,int], minima:dict, maxima:dict) -> dict:
    partner = offer['partner_team_id']
    need(type(partner) is int and partner != user and user in rosters and partner in rosters,
         'B2B4A_PARTNER_STATE_UNAVAILABLE')
    give, receive = set(offer['give_ids']), set(offer['receive_ids'])
    drops = {user: set(selected['drop_ids']),
             partner: set(offer['modeled_partner_auto_drop_ids'])}
    need(give and receive and give <= rosters[user].keys() and receive <= rosters[partner].keys(),
         'SEQUENTIAL_TRADE_PARTICIPANT_OWNERSHIP_CHANGED')
    need(not(drops[user] & give) and not(drops[partner] & receive),
         'DROP_OF_OUTGOING_ASSET')
    for tid in (user,partner):
        for pid in drops[tid]:
            row=rosters[tid].get(pid)
            need(row is not None, 'SEQUENTIAL_DROP_NOT_CURRENTLY_OWNED')
            need(row.get('droppable') is True and row.get('lineup_locked') is False,
                 'SEQUENTIAL_DROP_PERMISSION_OR_LOCK_UNPROVEN')
    fills, assumptions, other = _evidence(branch)
    need(not other, 'B2B2_BRANCH_UNRESOLVED:' + ','.join(other))
    orig_user = rosters[user]
    orig_partner = rosters[partner]
    moved_user = {pid:copy.deepcopy(orig_user[pid]) for pid in give}
    moved_partner = {pid:copy.deepcopy(orig_partner[pid]) for pid in receive}
    new_user = {i:copy.deepcopy(p) for i,p in orig_user.items() if i not in give | drops[user]}
    new_partner = {i:copy.deepcopy(p) for i,p in orig_partner.items() if i not in receive | drops[partner]}
    new_user.update(moved_partner)
    new_partner.update(moved_user)
    released = {i:copy.deepcopy(orig_user[i]) for i in drops[user]}
    released.update({i:copy.deepcopy(orig_partner[i]) for i in drops[partner]})
    need(not (set(released) & market.keys()), 'RELEASED_ASSET_MARKET_COLLISION')
    pending_market = copy.deepcopy(market)
    applied_fills = []
    for side,pid in fills:
        tid = user if side == 'user' else partner
        need(pid in pending_market and pending_market[pid].get('fantasy_status') == 'FREEAGENT' and
             str(pending_market[pid].get('position') or '').upper() in POSITIONS,
             'CONDITIONAL_FILL_NOT_FROZEN_FREEAGENT_OR_ALREADY_CONSUMED')
        need(not any(pid in x for x in rosters.values()), 'CONDITIONAL_FILL_ALREADY_OWNED')
        dest = new_user if tid == user else new_partner
        need(pid not in dest, 'CONDITIONAL_FILL_DUPLICATE_FINAL_ASSET')
        dest[pid] = copy.deepcopy(pending_market.pop(pid))
        applied_fills.append(pid)
    # Validate both sides before committing this hypothetical operation to the
    # copied state. An illegal partner must not leave a partial user transfer.
    for tid, rows in ((user,new_user),(partner,new_partner)):
        state = _state(rows, target[tid], minima, maxima)
        need(state['frozen_static_constraints_pass'],
             ('USER' if tid==user else 'PARTNER') + '_SEQUENTIAL_STATIC_ROSTER_ILLEGAL')
    for tid, rows in ((user,new_user),(partner,new_partner)):
        for pid,row in rows.items():
            row['on_team_id']=tid
            row['fantasy_status']='ROSTERED'
        rosters[tid] = rows
    for pid,row in released.items():
        row['fantasy_status']='RELEASED_PROCESSING_UNKNOWN'
        row['on_team_id']=None
        pending_market[pid] = row
    market.clear()
    market.update(pending_market)
    return {'offer_id':offer['offer_id'], 'partner_team_id':partner,
            'released_to_field_ids':sorted(released),
            'conditional_fills_from_frozen_freeagent_pool':sorted(applied_fills),
            'hypothetical_future_fill_assumptions': assumptions,
            'current_legality':'NOT_ESPN_VERIFIED'}


def audit(snapshot:dict,capture:dict,receipt:dict,league:dict,
          first_offer_id:str, second_offer_id:str,
          first_drop_ids:list[int],second_drop_ids:list[int]) -> dict:
    need(isinstance(first_offer_id,str) and bool(first_offer_id) and
         isinstance(second_offer_id,str) and bool(second_offer_id) and
         first_offer_id != second_offer_id, 'B2B4A_DISTINCT_OFFER_IDS_REQUIRED')
    for selection in (first_drop_ids,second_drop_ids):
        need(isinstance(selection,list) and all(type(x) is int and x >= 0 for x in selection)
             and len(set(selection)) == len(selection),'B2B4A_EXPLICIT_DROP_IDS_INVALID')
    frozen = tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league))
    source = structural_audit(snapshot,capture,receipt,league)
    frontier = build_frontier(snapshot,capture,receipt)
    need(source['offer_count'] == frontier['offer_count'], 'B2B4A_FRONTIER_COUNT_MISMATCH')
    report_rows=[]
    selection_map={}
    for oid,drops in ((first_offer_id,first_drop_ids),(second_offer_id,second_drop_ids)):
        _,row = _choose(source['offers'], oid,drops)
        raw = [x for x in frontier['offers'] if x['offer_id']==oid]
        need(len(raw)==1 and not raw[0]['structural_options_truncated'],
             'B2B4A_B1_OFFER_REJOIN_OR_TRUNCATION')
        matched=[x for x in raw[0]['structural_options'] if x['drop_ids']==drops]
        need(len(matched)==1, 'B2B4A_B1_EXACT_DROP_MISMATCH')
        # An option with proven lock/drop failure is never called a legal path.
        bad = set(matched[0]['feasibility_evidence']) & {
            'FROZEN_ESPN_DROPPABLE_NOT_TRUE','FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED'}
        need(not bad,'B2B4A_FROZEN_DROP_PERMISSION_BLOCKED')
        selection_map[oid]=(raw[0],row)
        report_rows.append(row)
    keys=[_lattice_variables(row['branches']) for row in report_rows]
    fill_id_list=[ident for key in keys for _,ident in key]
    need(len(fill_id_list)<=MAX_TOTAL_FILLS, 'B2B4A_FILL_VARIABLE_BUDGET_EXCEEDED')
    need(len(fill_id_list)==len(set(fill_id_list)),
         'SHARED_FUTURE_FILL_REQUIRES_COUPLED_ACQUISITION_STATE')
    combinations=len(report_rows[0]['branches'])*len(report_rows[1]['branches'])
    need(combinations<=MAX_BRANCH_PAIRS, 'B2B4A_BRANCH_PAIR_BUDGET_EXCEEDED')
    initial,market=_frozen_state(snapshot)
    user = receipt['team_id']
    need(type(user) is int and user in initial, 'B2B4A_USER_IDENTITY_INVALID')
    minima,maxima=_league(league)
    target={tid:len(rows) for tid,rows in initial.items()}
    output=[]
    for order in ((first_offer_id,second_offer_id),(second_offer_id,first_offer_id)):
        for branch_a,branch_b in itertools.product(report_rows[0]['branches'],report_rows[1]['branches']):
            branch_by_id={first_offer_id:branch_a,second_offer_id:branch_b}
            roster=copy.deepcopy(initial)
            pool=copy.deepcopy(market)
            steps=[]
            blockers=[]
            for oid in order:
                offer,option=selection_map[oid]
                try:
                    steps.append(_apply(roster,pool,offer,option,branch_by_id[oid],user,
                                        target,minima,maxima))
                except (CertificationBlocked, KeyError,TypeError,ValueError) as exc:
                    blockers.append(str(exc) if isinstance(exc,CertificationBlocked)
                                    else 'INVALID_SEQUENTIAL_STATE:'+type(exc).__name__)
                    break
            # League-wide uniqueness is necessary, not sufficient, for future ESPN legality.
            owners=[i for rows in roster.values() for i in rows]
            if len(owners)!=len(set(owners)) or (set(owners)&pool.keys()):
                blockers.append('JOINT_FINAL_OWNERSHIP_OR_MARKET_COLLISION')
            output.append({'offer_order':list(order),
                           'fill_states':[{ 'offer_id':oid,
                             'success_ids':sorted(x['id'] for x in branch_by_id[oid]['fill_outcomes']
                                                   if x['conditional_success'])}
                             for oid in (first_offer_id,second_offer_id)],
                           'steps_applied':len(steps), 'steps':steps,
                           'final_owned_ids_by_team':{str(tid):sorted(rows) for tid,rows in sorted(roster.items())},
                           'released_to_field_ids':sorted({i for step in steps
                                                       for i in step['released_to_field_ids']}),
                           'final_market_asset_ids':sorted(pool),
                           'state':'CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED'
                                   if not blockers and len(steps)==2 else 'BLOCKED',
                           'blockers':sorted(set(blockers)),
                           'joint_football_utility':'NOT_COMPUTED',
                           'conditional_fill_joint_probability':'UNKNOWN',
                           'field_response':'RELEASE_IDENTITIES_ONLY_NOT_PREDICTED',
                           'espn_action_authority':'NONE'})
    need(tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league))==frozen,
         'B2B4A_FROZEN_INPUT_MUTATED')
    return {'contract':CONTRACT,'frozen_sha256':dict(zip(
               ('snapshot','capture','receipt','league'), frozen)),
            'offers':[first_offer_id,second_offer_id],
            'joint_fill_variables':len(fill_id_list),
            'orders':2,'branch_pairs_per_order':combinations,
            'cases':output,'cases_conditional_static_pass':sum(x['state'].startswith('CONDITIONAL_') for x in output),
            'unresolved':['FUTURE_FREEAGENT_PROCESSING_AVAILABILITY_UNVERIFIED',
                          'CORRELATED_ACQUISITION_AND_MANAGER_BEHAVIOR_NOT_ESTIMATED',
                          'TRADE_EFFECTIVE_EVENT_ORDER_AND_ESPN_LEGALITY_UNVERIFIED',
                          'JOINT_COMPLETE_ROSTER_PAIRED_MC_NOT_RUN',
                          'RELEASED_PLAYER_FIELD_RESPONSE_NOT_PREDICTED',
                          'INJURY_CONTINGENCIES_AND_TIMING_NOT_CERTIFIED'],
            'state':'BLOCKED_B2B4A_ORDERED_STRUCTURAL_ONLY',
            'certified_actions':0,'espn_action_authority':'NONE'}


def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('snapshot','capture','receipt','league'):
        ap.add_argument('--'+k,type=Path,required=True)
    ap.add_argument('--first-offer-id',required=True)
    ap.add_argument('--second-offer-id',required=True)
    ap.add_argument('--first-drop-id',action='append',default=[],type=int)
    ap.add_argument('--second-drop-id',action='append',default=[],type=int)
    ap.add_argument('--out',type=Path)
    args=ap.parse_args(argv)
    print('WEEK8 B2B4A ORDERED JOINT STRUCTURAL DIAGNOSTIC',flush=True)
    try:
        docs=[json.loads(x.read_text(encoding='utf-8-sig')) for x in
              (args.snapshot,args.capture,args.receipt,args.league)]
        result=audit(*docs,args.first_offer_id,args.second_offer_id,
                     args.first_drop_id,args.second_drop_id)
        if args.out is not None:
            out=args.out.resolve()
            need(out.parent.name=='data' and
                 out.parent.parent.name.casefold()=='fantasy_season_v0_36_repack1' and
                 not out.exists(), 'PRIVATE_RUNTIME_DATA_NEW_OUTPUT_ONLY')
            with out.open('x',encoding='utf-8') as f:
                json.dump(result,f,sort_keys=True,indent=2)
                f.write('\n')
        print('ORDERS=2;CASES='+str(len(result['cases']))+
              ';STATIC_PASS='+str(result['cases_conditional_static_pass'])+
              ';NATIVE_MC=NONE;ESPN_GETS=NONE;ESPN_WRITES=NONE;CERTIFIED_ACTIONS=0',flush=True)
        print('STATE='+result['state']+';ACTION_AUTHORITY=NONE',flush=True)
        return 0
    except (CertificationBlocked, OSError, ValueError, TypeError, KeyError) as exc:
        code=str(exc) if isinstance(exc, CertificationBlocked) else type(exc).__name__
        print('B2B4A_BLOCKED='+code+';ACTION_AUTHORITY=NONE',flush=True)
        return 3

if __name__=='__main__':
    raise SystemExit(main())
