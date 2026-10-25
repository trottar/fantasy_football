"""Week 8 B2b3: conditional fill-branch two-manager predictive diagnostic.

Explicit opt-in, read-only frozen-state MC. Success/failure states of a FUTURE
free-agent acquisition are hypotheses, NOT transaction/acquisition forecasts.
The commissioned P / DST / K kernels are called unchanged, and manager behavior
is not fed into football utility. No branch is a certified ESPN action.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

from action_portfolio_b2b2 import audit as structural_audit, MAX_FILLS_PER_OFFER
from action_partner_b2b import partner_drop_proof
from action_predictive_b2 import (CertificationBlocked, MAX_SCENARIOS,
    canonical_sha256, paired_summary, require, verify_runtime)

CONTRACT = 'WEEK8_B2B3_CONDITIONAL_FILL_TWO_MANAGER_PAIRED_MC_V1'
MAX_BRANCHES = 1 << MAX_FILLS_PER_OFFER


def select_branch_frontier(snapshot: dict, capture: dict, receipt: dict,
                           league: dict, offer_id: str, drop_ids: list[int]) -> tuple[dict, dict, dict]:
    """B2b2 owns the complete frozen structural lattice and input integrity."""
    report = structural_audit(snapshot, capture, receipt, league)
    offers = [x for x in report['offers'] if x['offer_id'] == offer_id]
    require(len(offers) == 1, 'B2B3_OFFER_NOT_UNIQUE_OR_MISSING')
    options = [x for x in offers[0]['options'] if x['drop_ids'] == drop_ids]
    require(len(options) == 1, 'B2B3_DROP_OPTION_NOT_UNIQUE_OR_MISSING')
    require(1 <= len(options[0]['branches']) <= MAX_BRANCHES, 'B2B3_BRANCH_LATTICE_INVALID')
    # Re-join to B1 offer by the same immutable B2b2 frontier. Never substitute
    # names for asset IDs or synthesize an alternate native normalization.
    from action_frontier import build_frontier
    candidates = [x for x in build_frontier(snapshot, capture, receipt)['offers']
                  if x['offer_id'] == offer_id]
    require(len(candidates) == 1, 'B2B3_FROZEN_OFFER_REJOIN_FAILED')
    return candidates[0], offers[0], options[0]


def _frozen_fill_rows(snapshot: dict, offer: dict, branch: dict) -> dict[int, dict]:
    """Never insert an unowned/waiver/unknown asset as a successful future fill."""
    available = (snapshot.get('espn') or {}).get('available_players')
    require(isinstance(available, list), 'FROZEN_MARKET_REQUIRED_FOR_FILL_BRANCH')
    by_id = {}
    for row in available:
        require(isinstance(row, dict), 'FROZEN_MARKET_ROW_INVALID')
        pid = row.get('espn_id')
        if type(pid) is int:
            require(pid not in by_id, 'DUPLICATE_FROZEN_MARKET_ASSET')
            by_id[pid] = row
    assignments = {}
    for outcome in branch['fill_outcomes']:
        if not outcome['conditional_success']:
            continue
        pid = outcome['id']
        require(type(pid) is int and pid not in assignments,
                'B2B3_DUPLICATE_CONDITIONAL_FILL')
        row = by_id.get(pid)
        require(row is not None and row.get('fantasy_status') == 'FREEAGENT' and
                outcome.get('materialized_from_frozen_market') is True,
                'UNPROVEN_CONDITIONAL_FREEAGENT_FILL')
        assignments[pid] = copy.deepcopy(row)
    return assignments


def _native_pair(snapshot: dict, league: dict, model: dict, values_path: Path,
                 offer: dict, option: dict, branch: dict, team_id: int,
                 scenarios: int, runtime: Path, cache: dict | None):
    """Reconstruct a *conditional* complete-roster state using the same v0.36
    native evaluator as B2b1, including effective-week temporal splicing.

    CRN applies within each manager across branches via reused frozen baseline.
    Different managers' scenario indices are NOT a joint probabilistic draw.
    """
    import numpy as np
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from src import specialist_trade as st
    from src.market_manager import roster_is_legal
    from src.trade_timing import splice_effective_week

    espn = snapshot.get('espn') or {}
    week = espn.get('week')
    hours = (espn.get('transaction_settings') or {}).get('trade_review_hours')
    require(type(week) is int and 1 <= week <= 17 and
            type(hours) is int and hours > 0,
            'UNVERIFIED_POSITIVE_REVIEW_EFFECTIVE_WEEK')
    effect_week = min(18, week + 1)
    teams = {t['team_id']: t for t in espn.get('teams') or []
             if type(t.get('team_id')) is int}
    partner_id = offer['partner_team_id']
    require(team_id != partner_id and team_id in teams and partner_id in teams,
            'B2B3_TRADE_TEAM_IDENTITY_INVALID')
    before = {tid: list(teams[tid]['roster']) for tid in (team_id, partner_id)}
    outgoing = {team_id: set(offer['give_ids']), partner_id: set(offer['receive_ids'])}
    incoming = {team_id: set(offer['receive_ids']), partner_id: set(offer['give_ids'])}
    drops = {team_id: set(option['drop_ids']),
             partner_id: set(offer['modeled_partner_auto_drop_ids'])}
    assignments = _frozen_fill_rows(snapshot, offer, branch)
    conditional = {team_id: [], partner_id: []}
    for outcome in branch['fill_outcomes']:
        if outcome['conditional_success']:
            conditional[team_id if outcome['side'] == 'user' else partner_id].append(outcome['id'])
    require(len(set(conditional[team_id] + conditional[partner_id])) ==
            len(conditional[team_id]) + len(conditional[partner_id]),
            'FILL_ASSIGNED_TO_TWO_MANAGERS')
    finalized = {}
    for tid, other in ((team_id, partner_id), (partner_id, team_id)):
        rows = [copy.deepcopy(p) for p in before[tid]
                if p['espn_id'] not in outgoing[tid] | drops[tid]]
        rows += [copy.deepcopy(p) for p in before[other]
                 if p['espn_id'] in incoming[tid]]
        rows += [copy.deepcopy(assignments[pid]) for pid in conditional[tid]]
        require(roster_is_legal(rows, league, target_size=len(before[tid])),
                'CONDITIONAL_' + ('USER' if tid == team_id else 'PARTNER') + '_ROSTER_ILLEGAL')
        st._assert_supported_trade_specialist_state(rows,
            side='user' if tid == team_id else 'partner')
        finalized[tid] = st._normalize_incoming_assignments(before[tid], rows,
            team_id=tid, incoming_ids=incoming[tid] | set(conditional[tid]),
            outgoing_ids=outgoing[tid])
    final = st._snapshot_with_rosters(snapshot, finalized)
    hybrid = st._hybrid_player_snapshot(snapshot, final, (team_id, partner_id))
    # The simulated acquired free agent cannot simultaneously remain market-
    # available in that conditional state. Change only deep-copied model inputs.
    for state in (final, hybrid):
        market = (state.get('espn') or {}).get('available_players')
        if isinstance(market, list):
            state['espn']['available_players'] = [p for p in market
                if p.get('espn_id') not in assignments]
    baselines = dict(cache or {})
    response = {}
    for tid in (team_id, partner_id):
        if tid not in baselines:
            baselines[tid] = st._baseline_state(snapshot, league, model, values_path,
                tid, scenarios, progress_label='B2b3 frozen baseline')
        base_ctx, base_u, base_weekly, base_opp = baselines[tid]
        ctx, _, after_weekly, after_opp = st._composed_after_state(
            hybrid, final, league, model, values_path, tid, scenarios,
            progress_label='B2b3 conditional fill response')
        delayed_weekly = splice_effective_week(np.asarray(base_weekly),
                                              np.asarray(after_weekly), effect_week)
        delayed_opp = splice_effective_week(np.asarray(base_opp),
                                           np.asarray(after_opp), effect_week)
        after_u = st._scenario_h2h_utility_against(delayed_weekly, delayed_opp, ctx)
        response[tid] = (np.asarray(base_u, dtype=float), np.asarray(after_u, dtype=float))
    return response, baselines


def evaluate(snapshot: dict, capture: dict, receipt: dict, league: dict,
             model: dict, values_path: Path, runtime: Path, offer_id: str,
             drop_ids: list[int], *, scenarios: int = 32, kernel=None) -> dict:
    require(type(scenarios) is int and 16 <= scenarios <= MAX_SCENARIOS,
            'B2B3_SCENARIO_BUDGET_INVALID')
    require(isinstance(drop_ids, list) and all(type(x) is int for x in drop_ids)
            and len(set(drop_ids)) == len(drop_ids), 'B2B3_DROP_SELECTION_INVALID')
    offer, structural, option = select_branch_frontier(snapshot, capture, receipt,
                                                        league, offer_id, drop_ids)
    source_hashes = tuple(canonical_sha256(x) for x in
                          (snapshot, capture, receipt, league, model))
    # Permission and lock evidence for each forced drop are independent of the
    # boolean fill lattice. This check must not rely on the native choice flag.
    chosen = [x for x in offer['structural_options'] if x['drop_ids'] == drop_ids]
    require(len(chosen) == 1, 'B2B3_B1_DROP_REJOIN_FAILED')
    base_evidence = chosen[0]['feasibility_evidence']
    drop_blockers = [x for x in ('FROZEN_ESPN_DROPPABLE_NOT_TRUE',
                               'FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED')
                     if x in base_evidence]
    drop_blockers += partner_drop_proof(snapshot, offer)
    user_id, partner_id = receipt['team_id'], offer['partner_team_id']
    native = kernel if kernel is not None else _native_pair
    cache = None
    outcomes = {}
    results = []
    for index, branch in enumerate(option['branches']):
        key = tuple((x['side'], x['id'], bool(x['conditional_success']))
                    for x in branch['fill_outcomes'])
        # B2b2 deliberately classifies even an assumed-success branch as
        # unverified *future execution*. B2b3 may value that conditional
        # hypothesis without claiming the acquisition will occur. All other
        # unverified source, identity, or roster issues still block MC.
        assumptions = [x for x in branch['unresolved']
                       if x.startswith('FUTURE_FILL_AT_PROCESSING_UNVERIFIED:')]
        blockers = sorted(set([x for x in branch['unresolved']
                               if x not in assumptions] + drop_blockers))
        static_legal = all(branch[side]['frozen_static_constraints_pass']
                           for side in ('user', 'partner'))
        row = {'branch_index': index, 'conditional_fill_state': [
            {'side': x['side'], 'asset_id': x['id'], 'assumed_success':bool(x['conditional_success'])}
            for x in branch['fill_outcomes']],
            'state': 'BLOCKED', 'blockers': blockers,
            'conditional_assumptions_not_proven': assumptions,
            'future_acquisition_probability': 'UNVERIFIED',
            'action_authority': 'NONE'}
        if static_legal and not blockers:
            try:
                paired, cache = native(snapshot, league, model, values_path,
                    offer, chosen[0], branch, user_id, scenarios, runtime, cache)
                require(type(paired) is dict and set(paired) == {user_id, partner_id},
                        'B2B3_TWO_MANAGER_PAIRED_RESPONSE_REQUIRED')
                row['user'] = paired_summary(*paired[user_id])
                row['partner'] = paired_summary(*paired[partner_id])
                row['state'] = 'CONDITIONAL_MC_NOT_TRANSACTION_CERTIFIED'
                outcomes[key] = paired
            except (CertificationBlocked, ValueError, RuntimeError, TypeError, KeyError) as exc:
                row['blockers'].append(str(exc) if isinstance(exc, CertificationBlocked)
                                       else 'NATIVE_MC_ERROR:' + type(exc).__name__)
        results.append(row)
    # Compare branches using identical per-manager baselines, NOT independent
    # cross-manager draws. The no-fill branch may be structurally illegal.
    empty_key = tuple((x['side'], x['id'], False)
                      for x in option['branches'][0]['fill_outcomes'])
    if empty_key in outcomes:
        for row in results:
            key = tuple((x['side'], x['asset_id'], x['assumed_success'])
                        for x in row['conditional_fill_state'])
            if key in outcomes and key != empty_key:
                row['versus_no_fill_conditional'] = {
                    label: paired_summary(outcomes[empty_key][tid][1], outcomes[key][tid][1])
                    for label, tid in (('user', user_id), ('partner', partner_id))}
    require(tuple(canonical_sha256(x) for x in
                  (snapshot, capture, receipt, league, model)) == source_hashes,
            'B2B3_FROZEN_INPUT_OR_CONFIG_MUTATED')
    return {'contract': CONTRACT, 'offer_id':offer_id, 'drop_ids':list(drop_ids),
            'frozen_sha256': dict(zip(('snapshot','capture','receipt','league','model'),source_hashes)),
            'scenarios_requested': scenarios, 'future_fill_success_probabilities':'UNKNOWN',
            'total_conditional_branches': len(results),
            'branches_evaluated': sum(x['state'].startswith('CONDITIONAL_MC_') for x in results),
            'branches':results,
            'no_fill_reference_evaluated': empty_key in outcomes,
            'unresolved': ['NO_CALIBRATED_FUTURE_ACQUISITION_OR_CORRELATION_PROBABILITY',
                           'CONDITIONAL_SCENARIOS_NOT_WEIGHTED_OR_JOINT_MANAGER_DRAWS',
                           'LIVE_ESPN_PROCESSING_AND_ACTION_SCREEN_LEGALITY_UNVERIFIED',
                           'INJURY_AND_MANAGER_BEHAVIOR_UNCERTAINTY_NOT_COMPLETE',
                           'PORTFOLIO_SEQUENTIAL_MC_AND_FIELD_RESPONSE_NOT_CERTIFIED',
                           'POSITIVE_REVIEW_EFFECT_WEEK_IS_MODELED_NOT_APP_PROVEN'],
            'state':'BLOCKED_B2B3_CONDITIONAL_FILL_MC_ONLY',
            'certified_actions':0, 'espn_action_authority':'NONE'}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('snapshot','capture','receipt','league','model','values','runtime'):
        parser.add_argument('--'+arg, required=True, type=Path)
    parser.add_argument('--offer-id',required=True)
    parser.add_argument('--drop-id',action='append',type=int,default=[])
    parser.add_argument('--scenarios',type=int,default=32)
    parser.add_argument('--execute-native',action='store_true')
    parser.add_argument('--out',type=Path)
    args=parser.parse_args(argv)
    print('WEEK8 B2B3 CONDITIONAL FILL PAIRED MC DIAGNOSTIC',flush=True)
    try:
        docs=[json.loads(p.read_text(encoding='utf-8-sig'))
              for p in (args.snapshot,args.capture,args.receipt,args.league)]
        offer, structural, option=select_branch_frontier(*docs,args.offer_id,args.drop_id)
        if not args.execute_native:
            print('BRANCHES='+str(len(option['branches']))+
                  ';MODE=CHECK_ONLY;MC_NOT_STARTED=TRUE;ACTION_AUTHORITY=NONE',flush=True)
            return 0
        runtime=args.runtime.resolve()
        verify_runtime(runtime)
        model=json.loads(args.model.read_text(encoding='utf-8-sig'))
        result=evaluate(*docs,model,args.values.resolve(),runtime,args.offer_id,args.drop_id,
                        scenarios=args.scenarios)
        if args.out is not None:
            out=args.out.resolve()
            require(out.is_relative_to(runtime/'data') and not out.exists(),
                    'PRIVATE_OUTPUT_MUST_BE_NEW_RUNTIME_DATA_FILE')
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('x',encoding='utf-8') as f:
                json.dump(result,f,indent=2,sort_keys=True)
                f.write('\n')
        print('CONDITIONAL_BRANCHES='+str(result['total_conditional_branches'])+
              ';EVALUATED='+str(result['branches_evaluated'])+
              ';CERTIFIED_ACTIONS=0;ESPN_WRITES=NONE',flush=True)
        print('STATE='+result['state']+';ACTION_AUTHORITY=NONE',flush=True)
        return 0
    except (CertificationBlocked,OSError,ValueError,TypeError,KeyError,RuntimeError) as exc:
        code=str(exc) if isinstance(exc,CertificationBlocked) else type(exc).__name__
        print('B2B3_BLOCKED='+code+';ESPN_WRITES=NONE;ACTION_AUTHORITY=NONE',flush=True)
        return 3

if __name__=='__main__':
    raise SystemExit(main())
