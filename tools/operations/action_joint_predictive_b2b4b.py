"""Week 8 B2b4b: source-bound ordered joint-roster predictive experiment.

The B2b4a structural lattice controls all ownership, sequential/drop and fill
legality. Optional native v0.36 MC evaluates each final *joint* league state,
never a sum of standalone trade deltas. Manager behavior and future released-
asset acquisition are unknown. No transaction authority or ESPN access.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

from action_frontier import CertificationBlocked, canonical_sha256
from action_joint_state_b2b4a import audit as structural_audit, _frozen_state
from action_predictive_b2 import MAX_SCENARIOS, paired_summary, require, verify_runtime

CONTRACT = 'WEEK8_B2B4B_JOINT_ORDERED_PAIRED_RESPONSE_V1'
MAX_CASES = 32  # 2 orders * 16 coupled conditional states
MAX_NATIVE_SCENARIOS = min(128, MAX_SCENARIOS)


def _reconstruct(snapshot: dict, case: dict) -> tuple[dict[int, list[dict]], list[dict], list[int]]:
    """Reconstruct the *whole* league. Released assets are not free agents."""
    owned, market = _frozen_state(snapshot)
    original = {pid: row for roster in owned.values() for pid, row in roster.items()}
    universe = dict(original)
    universe.update(market)
    reported = case['final_owned_ids_by_team']
    require(type(reported) is dict and set(reported) == {str(x) for x in owned},
            'B2B4B_FINAL_TEAM_SET_INVALID')
    final = {}
    final_ids: set[int] = set()
    for tid in sorted(owned):
        ids = reported[str(tid)]
        require(type(ids) is list and all(type(pid) is int for pid in ids)
                and len(ids) == len(set(ids)), 'B2B4B_FINAL_ROSTER_IDS_INVALID')
        require(not final_ids.intersection(ids) and set(ids).issubset(universe),
                'B2B4B_FINAL_OWNERSHIP_COLLISION_OR_UNKNOWN_ASSET')
        final_ids.update(ids)
        final[tid] = [copy.deepcopy(universe[pid]) for pid in ids]
    market_ids = case['final_market_asset_ids']
    released = case['released_to_field_ids']
    require(type(market_ids) is list and type(released) is list and
            all(type(pid) is int for pid in market_ids + released) and
            len(market_ids) == len(set(market_ids)) and
            len(released) == len(set(released)), 'B2B4B_MARKET_OR_RELEASE_IDENTITIES_INVALID')
    released_set = set(released)
    final_market = set(market_ids)
    require(final_ids.isdisjoint(final_market) and
            final_ids | final_market == set(universe) and
            released_set == final_market - set(market) and
            released_set.issubset(original), 'B2B4B_FIELD_LEDGER_NOT_CONSERVED')
    # Newly released players do not inherit frozen FREEAGENT permissions.
    # Only frozen market records not consumed by a conditional fill survive.
    frozen_available = (snapshot.get('espn') or {}).get('available_players')
    require(type(frozen_available) is list, 'B2B4B_FROZEN_MARKET_REQUIRED')
    available = [copy.deepcopy(row) for row in frozen_available
                 if row.get('espn_id') in final_market]
    require({row.get('espn_id') for row in available} == final_market & set(market),
            'B2B4B_MARKET_STATUS_RECONSTRUCTION_FAILED')
    return final, available, sorted(released_set)


def _native_joint(snapshot: dict, league: dict, model: dict, values: Path,
                  runtime: Path, case: dict, team_ids: tuple[int, ...],
                  scenarios: int, baselines: dict | None):
    """Use unchanged specialist_trade P/D/K composition on the joint state.

    Each manager compares its own shared MC scenario axis against its cached
    baseline. Cross-manager scenario indices are not a joint distribution.
    """
    import numpy as np
    verify_runtime(runtime)
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from src import specialist_trade as st
    from src.market_manager import roster_is_legal
    from src import trade_timing as trade_timing_module
    from src import market_manager as market_module
    from src.trade_timing import splice_effective_week

    # The source-identity guard is not sufficient if an earlier import resolved
    # `src` from the control root or another release. Refuse mixed kernels.
    for module in (st, market_module, trade_timing_module):
        origin = getattr(module, '__file__', None)
        require(isinstance(origin, str) and
                Path(origin).resolve().is_relative_to(runtime.resolve()),
                'B2B4B_NATIVE_IMPORTED_OUTSIDE_VERIFIED_RUNTIME')

    espn = snapshot.get('espn') or {}
    week = espn.get('week')
    hours = (espn.get('transaction_settings') or {}).get('trade_review_hours')
    require(type(week) is int and 1 <= week <= 17 and
            type(hours) is int and hours > 0,
            'B2B4B_FUTURE_EFFECTIVE_WEEK_NOT_PROVEN')
    modeled_effect_week = min(18, week + 1)
    original, _ = _frozen_state(snapshot)
    final, available, released = _reconstruct(snapshot, case)
    normalized = {}
    for tid, rows in final.items():
        before = list(original[tid].values())
        incoming = {p['espn_id'] for p in rows} - set(original[tid])
        outgoing = set(original[tid]) - {p['espn_id'] for p in rows}
        require(roster_is_legal(rows, league, target_size=len(before)),
                'B2B4B_NATIVE_FINAL_LEAGUE_ROSTER_ILLEGAL')
        st._assert_supported_trade_specialist_state(rows, side='joint_manager')
        normalized[tid] = st._normalize_incoming_assignments(
            before, rows, team_id=tid, incoming_ids=incoming, outgoing_ids=outgoing)
    final_snapshot = st._snapshot_with_rosters(snapshot, normalized)
    hybrid = st._hybrid_player_snapshot(snapshot, final_snapshot, sorted(normalized))
    for state in (final_snapshot, hybrid):
        state['espn']['available_players'] = copy.deepcopy(available)
    cache = dict(baselines or {})
    responses = {}
    for tid in team_ids:
        if tid not in cache:
            cache[tid] = st._baseline_state(snapshot, league, model, values, tid,
                             scenarios, progress_label='B2b4b frozen joint baseline')
        base_ctx, base_utility, base_weekly, base_opponent = cache[tid]
        after_ctx, _, after_weekly, after_opponent = st._composed_after_state(
            hybrid, final_snapshot, league, model, values, tid, scenarios,
            progress_label='B2b4b conditional joint roster response')
        spliced_w = splice_effective_week(np.asarray(base_weekly),
                                         np.asarray(after_weekly), modeled_effect_week)
        spliced_o = splice_effective_week(np.asarray(base_opponent),
                                         np.asarray(after_opponent), modeled_effect_week)
        # This opponent-reference shift includes the entire *joint* roster
        # response, not an inferred post-release pickup by a third manager.
        opponent_base_ppg = st._scenario_season_ppg(base_opponent, base_ctx)
        opponent_final_ppg = st._scenario_season_ppg(spliced_o, after_ctx)
        responses[tid] = {
            'hold': np.asarray(base_utility, dtype=float),
            'joint': np.asarray(st._scenario_h2h_utility_against(
                spliced_w, spliced_o, after_ctx), dtype=float),
            'hold_opponent_reference': np.asarray(opponent_base_ppg, dtype=float),
            'joint_opponent_reference': np.asarray(opponent_final_ppg, dtype=float),
        }
    return responses, cache


def _validated_response(raw: dict, team_ids: tuple[int, ...],
                        scenarios: int) -> dict[int, dict[str, Any]]:
    require(type(raw) is dict and set(raw) == set(team_ids),
            'B2B4B_ALL_AFFECTED_MANAGERS_REQUIRED')
    import numpy as np
    checked = {}
    for tid in team_ids:
        payload = raw[tid]
        require(type(payload) is dict and set(payload) == {
            'hold', 'joint', 'hold_opponent_reference', 'joint_opponent_reference'},
            'B2B4B_RESPONSE_CHANNELS_INCOMPLETE')
        checked[tid] = {}
        for key, value in payload.items():
            a = np.asarray(value, dtype=float)
            require(a.ndim == 1 and a.shape == (scenarios,) and
                    np.isfinite(a).all(), 'B2B4B_RESPONSE_SHAPE_OR_FINITE_INVALID')
            checked[tid][key] = a.copy()
    return checked


def evaluate(snapshot: dict, capture: dict, receipt: dict, league: dict,
             model: dict, values: Path, runtime: Path,
             first_offer_id: str, second_offer_id: str,
             first_drop_ids: list[int], second_drop_ids: list[int],
             *, scenarios: int = 16, kernel=None) -> dict:
    """Evaluate only B2b4a structural PASS branches; never grant authority."""
    require(type(scenarios) is int and 16 <= scenarios <= MAX_NATIVE_SCENARIOS,
            'B2B4B_MC_BUDGET_INVALID')
    source = (snapshot, capture, receipt, league, model)
    hashes = tuple(canonical_sha256(x) for x in source)
    structural = structural_audit(snapshot, capture, receipt, league,
                                  first_offer_id, second_offer_id,
                                  first_drop_ids, second_drop_ids)
    cases = structural['cases']
    require(structural['orders'] == 2 and type(cases) is list and
            1 <= len(cases) <= MAX_CASES and len(cases) ==
            2 * structural['branch_pairs_per_order'],
            'B2B4B_STRUCTURAL_CASE_SET_INVALID')
    # Both partner IDs derive from the exact B1/B2b4a source offer identities;
    # B2b4a records partner identity with successful applied steps only.
    affected = {receipt['team_id']}
    for case in cases:
        for step in case['steps']:
            affected.add(step['partner_team_id'])
    require(all(type(tid) is int for tid in affected) and
            (len(affected) >= 2 or not any(
                c['state'] == 'CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED' for c in cases)),
            'B2B4B_AFFECTED_MANAGER_IDENTITIES_MISSING')
    team_ids = tuple(sorted(affected))
    native = kernel if kernel is not None else _native_joint
    cache = None
    rows = []
    valid = {}
    for index, case in enumerate(cases):
        item = {'case_index':index, 'offer_order':copy.deepcopy(case['offer_order']),
                'fill_states':copy.deepcopy(case['fill_states']),
                'released_to_field_ids':copy.deepcopy(case['released_to_field_ids']),
                'structural_state':case['state'], 'state':'BLOCKED',
                'blockers':list(case['blockers']),
                'joint_acquisition_probability':'UNKNOWN',
                'released_asset_future_acquisition_response':'NOT_PREDICTED',
                'espn_action_authority':'NONE'}
        if case['state'] == 'CONDITIONAL_ORDERED_STATIC_PASS_NOT_CERTIFIED':
            try:
                # Check universe conservation BEFORE native machinery or a mock.
                _reconstruct(snapshot, case)
                raw, candidate_cache = native(snapshot, league, model, values,
                         runtime, copy.deepcopy(case), team_ids, scenarios, cache)
                values_checked = _validated_response(raw, team_ids, scenarios)
                cache = candidate_cache
                require(type(cache) is dict, 'B2B4B_BASELINE_CACHE_INVALID')
                item['affected_managers'] = {
                    str(tid): {
                        'joint_complete_roster_delta':paired_summary(values_checked[tid]['hold'],
                                                                      values_checked[tid]['joint']),
                        'opponent_reference_shift':paired_summary(
                            values_checked[tid]['hold_opponent_reference'],
                            values_checked[tid]['joint_opponent_reference'])
                    } for tid in team_ids}
                item['state'] = 'CONDITIONAL_JOINT_MC_NOT_CERTIFIED'
                valid[index] = values_checked
            except (CertificationBlocked, ValueError, RuntimeError, KeyError,
                    TypeError, AssertionError, ImportError, OSError) as exc:
                item['blockers'].append(str(exc) if isinstance(exc,CertificationBlocked)
                                         else 'NATIVE_JOINT_MC_ERROR:' + type(exc).__name__)
        rows.append(item)
    # Identical frozen fill outcomes may permit both orders; per-manager arrays
    # can then be directly contrasted, with no manager probabilities mixed in.
    for i, left in enumerate(rows):
        if i not in valid:
            continue
        for j in range(i + 1, len(rows)):
            right = rows[j]
            if j not in valid or left['offer_order'] == right['offer_order'] or \
                    left['fill_states'] != right['fill_states']:
                continue
            left['other_order_case_index'] = j
            right['other_order_case_index'] = i
            left['versus_other_order'] = {str(tid):paired_summary(
                valid[j][tid]['joint'],valid[i][tid]['joint']) for tid in team_ids}
            right['versus_other_order'] = {str(tid):paired_summary(
                valid[i][tid]['joint'],valid[j][tid]['joint']) for tid in team_ids}
    require(tuple(canonical_sha256(x) for x in source) == hashes,
            'B2B4B_FROZEN_INPUT_OR_CONFIG_MUTATED')
    return {'contract':CONTRACT, 'frozen_sha256':dict(zip(
                ('snapshot','capture','receipt','league','model'), hashes)),
            'first_offer_id':first_offer_id, 'second_offer_id':second_offer_id,
            'affected_manager_ids':list(team_ids), 'scenarios':scenarios,
            'structural_cases':len(rows),
            'joint_mc_cases_evaluated':sum(r['state'].startswith('CONDITIONAL_JOINT_MC_') for r in rows),
            'cases':rows,
            'future_acquisition_joint_probability':'UNKNOWN',
            'released_asset_field_exposure':'LEDGER_ONLY_NO_REACQUISITION_MODEL',
            'unresolved':['CORRELATED_ACQUISITION_AND_TRADE_ACCEPTANCE_UNESTIMATED',
                          'RELEASED_ASSET_POST_PROCESSING_STATUS_AND_REACQUISITION_UNKNOWN',
                          'FUTURE_EFFECTIVE_TIME_AND_ESPN_ACTION_SCREENS_UNVERIFIED',
                          'THIRD_PARTY_FIELD_ACQUISITION_NOT_MODELED',
                          'INJURY_DOWNSIDE_AND_COMPLETE_WEEKLY_ACTION_COVERAGE_UNCERTIFIED'],
            'state':'BLOCKED_B2B4B_CONDITIONAL_JOINT_MC_ONLY',
            'certified_actions':0, 'espn_action_authority':'NONE'}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('snapshot','capture','receipt','league'):
        ap.add_argument('--' + name, type=Path, required=True)
    for name in ('model','values','runtime'):
        ap.add_argument('--' + name, type=Path)
    ap.add_argument('--first-offer-id',required=True)
    ap.add_argument('--second-offer-id',required=True)
    ap.add_argument('--first-drop-id',action='append',type=int,default=[])
    ap.add_argument('--second-drop-id',action='append',type=int,default=[])
    ap.add_argument('--scenarios',type=int,default=16)
    ap.add_argument('--execute-native',action='store_true')
    ap.add_argument('--out',type=Path)
    a = ap.parse_args(argv)
    print('WEEK8 B2B4B JOINT PAIRED RESPONSE DIAGNOSTIC',flush=True)
    try:
        docs = [json.loads(getattr(a, key).read_text(encoding='utf-8-sig'))
                for key in ('snapshot','capture','receipt','league')]
        if not a.execute_native:
            report = structural_audit(*docs,a.first_offer_id,a.second_offer_id,
                                      a.first_drop_id,a.second_drop_id)
            print('MODE=CHECK_ONLY;CASES='+str(len(report['cases']))+
                  ';NATIVE_MC_NOT_STARTED=TRUE;ESPN_GETS=NONE;ESPN_WRITES=NONE',flush=True)
            print('ACTION_AUTHORITY=NONE',flush=True)
            return 0
        require(all(x is not None for x in (a.model,a.values,a.runtime)),
                'B2B4B_NATIVE_INPUT_PATHS_REQUIRED')
        runtime = a.runtime.resolve()
        verify_runtime(runtime)
        model = json.loads(a.model.read_text(encoding='utf-8-sig'))
        result = evaluate(*docs,model,a.values.resolve(),runtime,
                  a.first_offer_id,a.second_offer_id,a.first_drop_id,a.second_drop_id,
                  scenarios=a.scenarios)
        if a.out is not None:
            out = a.out.resolve()
            require(out.parent == (runtime / 'data').resolve() and not out.exists(),
                    'B2B4B_PRIVATE_NEW_RUNTIME_DATA_FILE_ONLY')
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('x',encoding='utf-8') as f:
                json.dump(result,f,sort_keys=True,indent=2)
                f.write('\n')
        print('JOINT_CASES='+str(result['structural_cases'])+
              ';NATIVE_EVALUATED='+str(result['joint_mc_cases_evaluated'])+
              ';CERTIFIED_ACTIONS=0;ESPN_GETS=NONE;ESPN_WRITES=NONE',flush=True)
        print('STATE='+result['state']+';ACTION_AUTHORITY=NONE',flush=True)
        return 0
    except (CertificationBlocked, OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        reason = str(exc) if isinstance(exc, CertificationBlocked) else type(exc).__name__
        print('B2B4B_BLOCKED='+reason+';ACTION_AUTHORITY=NONE;ESPN_WRITES=NONE',flush=True)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
