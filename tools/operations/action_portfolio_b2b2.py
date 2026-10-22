"""Week 8 B2b2: frozen future-fill branch and coupled-offer exposure audit.

Deterministic READ-ONLY structural evidence. No MC is run, no manager behavior
probabilities are invented, and no transaction recommendation is authorized.
Neither a conditional FREEAGENT state nor two standalone MC gains certify a
joint portfolio. All observed inputs must be prospective frozen sources.
"""
from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
from pathlib import Path
from typing import Any

from action_frontier import build_frontier, canonical_sha256, CertificationBlocked
from action_predictive_b2 import _safe_option

CONTRACT = 'WEEK8_FROZEN_TRADE_FILL_PORTFOLIO_B2B2_V1'
MAX_OFFERS = 12
MAX_PAIR_CANDIDATES = 66  # 12 choose 2
MAX_FILLS_PER_OFFER = 4
POSITIONS = frozenset(('QB', 'RB', 'WR', 'TE', 'DST', 'K'))


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise CertificationBlocked(reason)


def _team(snapshot: dict[str, Any], tid: int) -> dict[str, Any]:
    teams = [t for t in (snapshot.get('espn') or {}).get('teams') or []
             if type(t.get('team_id')) is int and t['team_id'] == tid]
    need(len(teams) == 1, 'FROZEN_TEAM_ID_MISSING_OR_AMBIGUOUS')
    return teams[0]


def _owned(team: dict[str, Any]) -> dict[int, dict[str, Any]]:
    roster = team.get('roster')
    need(isinstance(roster, list) and roster, 'FROZEN_TEAM_ROSTER_UNAVAILABLE')
    need(all(isinstance(p, dict) and type(p.get('espn_id')) is int and p['espn_id'] >= 0
             and str(p.get('position') or '').upper() in POSITIONS for p in roster),
         'FROZEN_ROSTER_IDENTITIES_OR_POSITIONS_UNSUPPORTED')
    out = {p['espn_id']:p for p in roster}
    need(len(out) == len(roster), 'DUPLICATE_FROZEN_ROSTER_IDENTITIES')
    return out


def _available(snapshot: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = (snapshot.get('espn') or {}).get('available_players')
    # A snapshot without a populated available pool cannot prove acquisition.
    # Preserve no-fill evidence and label every claimed fill as unverified.
    if not isinstance(rows, list):
        return {}
    known: dict[int, dict[str, Any]] = {}
    for p in rows:
        need(isinstance(p, dict), 'FROZEN_AVAILABLE_PLAYER_INVALID')
        i = p.get('espn_id')
        if type(i) is int:
            need(i not in known, 'DUPLICATE_FROZEN_AVAILABLE_ID')
            known[i] = p
    return known


def _league(league: dict[str, Any]) -> tuple[dict[str,int], dict[str,int]]:
    # Exact frozen league settings are needed; the native roster legality
    # routine checks these same minima/maxima. This is still NOT app legality.
    need(isinstance(league, dict) and isinstance(league.get('roster'), dict)
         and isinstance(league.get('position_maximums'), dict),
         'LEAGUE_ROSTER_MIN_MAX_UNVERIFIED')
    minima, maxima = {}, {}
    for position in POSITIONS:
        mn = league['roster'].get(position, 0)
        mx = league['position_maximums'].get(position)
        need(type(mn) is int and mn >= 0, 'INVALID_LEAGUE_MINIMUM:' + position)
        need(mx is None or (type(mx) is int and mx >= mn),
             'INVALID_LEAGUE_MAXIMUM:' + position)
        minima[position] = mn
        if mx is not None:
            maxima[position] = mx
    return minima,maxima


def _state(rows: dict[int, dict[str, Any]], target: int,
           minima: dict[str,int], maxima: dict[str,int]) -> dict[str, Any]:
    counts = Counter(str(p['position']).upper() for p in rows.values())
    deficits = {pos:minima[pos]-counts[pos] for pos in sorted(POSITIONS)
                if counts[pos] < minima[pos]}
    excess = {pos:counts[pos]-maxima[pos] for pos in sorted(maxima)
              if counts[pos] > maxima[pos]}
    return {'owned_count': len(rows), 'target_count':target,
            'open_slots':max(0,target-len(rows)),
            'position_counts':{k:counts[k] for k in sorted(POSITIONS)},
            'minimum_deficits':deficits, 'maximum_excess':excess,
            'over_capacity':len(rows)>target,
            'frozen_static_constraints_pass':not deficits and not excess and len(rows)<=target}


def _future_fill_rows(snapshot: dict[str,Any],
                      fills: list[tuple[str,int]], frozen_owned: set[int]) -> tuple[dict[int,dict[str,Any]],list[str]]:
    available = _available(snapshot)
    proven, blockers = {}, []
    if fills and not isinstance((snapshot.get('espn') or {}).get('available_players'), list):
        blockers.append('FROZEN_AVAILABLE_POOL_NOT_PRESENT_UNVERIFIED')
    for side,pid in fills:
        need(type(pid) is int and pid >= 0, 'FUTURE_FILL_ID_INVALID')
        if pid in frozen_owned:
            blockers.append('NATIVE_FILL_ALREADY_OWNED:' + side)
        elif pid not in available:
            blockers.append('FUTURE_FILL_NOT_IN_FROZEN_AVAILABLE_POOL:' + side)
        elif str(available[pid].get('fantasy_status') or '').upper() != 'FREEAGENT':
            blockers.append('FUTURE_FILL_NOT_FROZEN_FREEAGENT:' + side)
        elif str(available[pid].get('position') or '').upper() not in POSITIONS:
            blockers.append('FUTURE_FILL_POSITION_UNVERIFIED:' + side)
        else:
            proven[pid] = available[pid]
    return proven,sorted(set(blockers))


def _offer_branches(offer: dict[str,Any], snapshot: dict[str,Any], user_team_id:int,
                    minima:dict[str,int],maxima:dict[str,int]) -> dict[str,Any]:
    partner_id=offer['partner_team_id']
    orig={'user':_owned(_team(snapshot,user_team_id)),
          'partner':_owned(_team(snapshot,partner_id))}
    # Model-dropped assets require frozen proof; B2b1's legality gate is reused
    # in spirit here without asserting future (post-review) lock state.
    partner_drops=offer['modeled_partner_auto_drop_ids']
    reasons=[]
    for i in partner_drops:
        if i in offer['receive_ids']:
            reasons.append('PARTNER_DROP_ALREADY_OUTGOING')
        elif i not in orig['partner']:
            reasons.append('PARTNER_DROP_NOT_OWNED')
        elif orig['partner'][i].get('droppable') is not True or orig['partner'][i].get('lineup_locked') is not False:
            reasons.append('PARTNER_DROP_NOT_FROZEN_PROVEN_UNLOCKED')
    fills=[('user',int(i)) for i in offer['modeled_native_auto_add_ids']]
    fills += [('partner',int(i)) for i in offer['modeled_partner_auto_add_ids']]
    need(len(fills)<=MAX_FILLS_PER_OFFER,'FILL_BRANCH_BUDGET_EXCEEDED')
    need(len({i for _,i in fills})==len(fills),'FUTURE_FILL_ASSET_DOUBLE_ASSIGNED')
    frozen_owned=set(orig['user'])|set(orig['partner'])
    proven,fill_blockers=_future_fill_rows(snapshot,fills,frozen_owned)
    rows=[]
    for option in offer['structural_options']:
        _,opt_reasons=_safe_option(offer,option)
        original_user=set(orig['user']);original_partner=set(orig['partner'])
        after_user={i:p for i,p in orig['user'].items() if i not in
                    set(offer['give_ids'])|set(option['drop_ids'])}
        after_user.update({i:orig['partner'][i] for i in offer['receive_ids']})
        after_partner={i:p for i,p in orig['partner'].items() if i not in
                       set(offer['receive_ids'])|set(partner_drops)}
        after_partner.update({i:orig['user'][i] for i in offer['give_ids']})
        # The no-fill state is an explicit branch, even if currently illegal.
        cases=[]
        for bits in itertools.product((False,True), repeat=len(fills)):
            selected=[(side,i) for (side,i),on in zip(fills,bits) if on]
            user=dict(after_user);partner=dict(after_partner)
            for side,i in selected:
                if i in proven:
                    (user if side=='user' else partner)[i]=proven[i]
            failures=[('FUTURE_FILL_AT_PROCESSING_UNVERIFIED:' + side) for side,i in selected]
            failures += [b for b in fill_blockers if any((side+':') in b for side,_ in selected)]
            user_state=_state(user,len(original_user),minima,maxima)
            partner_state=_state(partner,len(original_partner),minima,maxima)
            cases.append({'fill_outcomes':[{'side':side,'id':i,'conditional_success':on,
                                           'materialized_from_frozen_market': bool(on and i in proven)}
                                           for (side,i),on in zip(fills,bits)],
                          'user':user_state,'partner':partner_state,
                          'frozen_static_constraints_pass':user_state['frozen_static_constraints_pass']
                             and partner_state['frozen_static_constraints_pass'] and not failures and not reasons and not opt_reasons,
                          'unresolved':sorted(set(failures+reasons+opt_reasons))})
        rows.append({'drop_ids':option['drop_ids'],
                     'native_selected':option['native_selected_normalization'],
                     'branches':cases,
                     'future_fill_acquisition_probabilities':'UNKNOWN_NOT_ESTIMATED',
                     'paired_mc_for_all_fill_branches':'NOT_RUN',
                     'action_authority':'NONE'})
    return {'offer_id':offer['offer_id'],'partner_team_id':partner_id,
            'fill_variable_count':len(fills), 'options':rows,
            'future_fill_sources_unverified':fill_blockers,
            'state':'CONDITIONAL_FILL_BRANCHES_ONLY'}


def _portfolios(offers:list[dict[str,Any]]) -> list[dict[str,Any]]:
    output=[]
    for a,b in itertools.combinations(offers,2):
        give=set(a['give_ids'])&set(b['give_ids'])
        receive=set(a['receive_ids'])&set(b['receive_ids'])
        # Dropping an asset in one trade may invalidate the other offer.
        drops=(set(a['modeled_native_auto_drop_ids'])&set(b['give_ids'])) | \
              (set(b['modeled_native_auto_drop_ids'])&set(a['give_ids']))
        same_partner=a['partner_team_id']==b['partner_team_id']
        conflict=bool(give or receive or drops)
        output.append({'offer_ids':sorted((a['offer_id'],b['offer_id'])),
                       'direct_conflicting_player_ids':sorted(give|receive|drops),
                       'same_partner':same_partner,
                       'status':'MUTUALLY_EXCLUSIVE_AT_FROZEN_ASSET_STATE' if conflict else
                            'COUPLED_JOINT_ROSTER_AND_EFFECTIVE_TIME_MC_REQUIRED',
                       'joint_utility':'NOT_COMPUTED_NO_ADDITIVE_STANDALONE_MC',
                       'joint_acceptance_probability':'UNKNOWN',
                       'joint_espn_legality':'UNVERIFIED'})
    return output


def audit(snapshot:dict[str,Any],capture:dict[str,Any],receipt:dict[str,Any],
          league:dict[str,Any],*,max_offers:int=MAX_OFFERS) -> dict[str,Any]:
    need(type(max_offers) is int and 1<=max_offers<=MAX_OFFERS,'INVALID_OFFER_BUDGET')
    frozen=tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league))
    frontier=build_frontier(snapshot,capture,receipt)
    minima,maxima=_league(league)
    offers=sorted(frontier['offers'],key=lambda r:r['offer_id'])
    need(len(offers)<=max_offers,'OFFER_FRONTIER_TOO_LARGE_NO_SILENT_TRUNCATION')
    need(all(not o['structural_options_truncated'] for o in offers),
         'STRUCTURAL_OPTION_FRONTIER_TRUNCATED')
    need(len(offers)<=MAX_OFFERS,'GLOBAL_OFFER_BUDGET_EXCEEDED')
    user_id=receipt['team_id']
    need(type(user_id) is int,'FROZEN_USER_TEAM_INVALID')
    rows=[_offer_branches(o,snapshot,user_id,minima,maxima) for o in offers]
    pairs=_portfolios(offers)
    need(len(pairs)<=MAX_PAIR_CANDIDATES,'PAIR_ENUMERATION_LIMIT_EXCEEDED')
    need(tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league))==frozen,
         'FROZEN_INPUT_MUTATED_DURING_PORTFOLIO_AUDIT')
    return {'contract':CONTRACT,'source_snapshot_sha256':frozen[0],
            'source_capture_sha256':frozen[1],'source_receipt_sha256':frozen[2],
            'league_sha256':frozen[3], 'offer_count':len(offers),'offers':rows,
            'hold':{'state':'REFERENCE_NO_TRADE_NO_FUTURE_FILL'},
            'pair_count':len(pairs),'pairs':pairs,
            'nonindependence':'NO_STANDALONE_MC_ADDITION_OR_MANAGER_PROBABILITY_MULTIPLICATION',
            'unresolved':['PROCESSING_TIME_FREEAGENT_ELIGIBILITY_NOT_VERIFIED',
                          'WAIVER_SUCCESS_CORRELATION_AND_MARKET_COMPETITION_NOT_MODELED',
                          'FILL_BRANCHES_HAVE_NO_NATIVE_MC_UTILITY',
                          'LEAGUE_SETTINGS_SUPPLIED_NOT_RECEIPT_BOUND',
                          'JOINT_ROSTER_AND_FIELD_RESPONSE_NOT_MODELED',
                          'INJURY_AND_TRADE_EFFECTIVE_TIMING_NOT_RECONCILED',
                          'LIVE_ESPN_ACTION_SCREEN_LEGALITY_NOT_VERIFIED',
                          'PARTNER_ACCEPTANCE_MANAGER_BEHAVIOR_NOT_MODELED'],
            'state':'BLOCKED_B2B2_FROZEN_FILL_AND_PORTFOLIO_FRONTIER_ONLY',
            'eligible_for_approval_count':0,'espn_action_authority':'NONE'}


def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('snapshot','capture','receipt','league'):
        ap.add_argument('--'+k,required=True,type=Path)
    ap.add_argument('--out',type=Path,help='New private local JSON result only')
    args=ap.parse_args(argv)
    print('WEEK8 B2B2 FROZEN FILL AND TRADE PORTFOLIO AUDIT')
    try:
        docs=[json.loads(p.read_text(encoding='utf-8-sig')) for p in
              (args.snapshot,args.capture,args.receipt,args.league)]
        result=audit(*docs)
        if args.out is not None:
            output=args.out.resolve()
            need(output.parent.name=='data' and
                 output.parent.parent.name.casefold()=='fantasy_season_v0_36_repack1',
                 'PRIVATE_RUNTIME_DATA_OUTPUT_ONLY')
            with output.open('x',encoding='utf-8') as out:
                json.dump(result,out,indent=2,sort_keys=True)
                out.write('\n')
        print('OFFERS='+str(result['offer_count'])+';PAIR_DEPENDENCIES='+str(result['pair_count'])+
              ';NATIVE_MC_NOT_RUN=TRUE;ESPN_WRITES=NONE;ACTION_AUTHORITY=NONE')
        print('STATE='+result['state'])
        return 0
    except (CertificationBlocked,OSError,ValueError,KeyError,TypeError) as exc:
        print('B2B2_BLOCKED='+ (str(exc) if isinstance(exc,CertificationBlocked) else type(exc).__name__)
              +';ACTION_AUTHORITY=NONE')
        return 3

if __name__=='__main__':
    raise SystemExit(main())
