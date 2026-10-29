"""B2b6: conditional two-manager *paired* MC across every frozen legal drop.

An explicit opt-in diagnostic, not a weekly MC replay or transaction certificate.
Compare each structurally legal post-trade drop under an *identical* conditional
future-fill state, preserving P/D/K complete-roster composition in the native
v0.36 kernels. No acquisition/acceptance probabilities are inferred and no
condition is promoted to ESPN transaction authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

from action_frontier import CertificationBlocked, canonical_sha256
from action_fill_predictive_b2b3 import select_branch_frontier, _native_pair
from action_partner_b2b import partner_drop_proof
from action_predictive_b2 import paired_summary, require, verify_runtime

CONTRACT = 'WEEK8_B2B6_MATCHED_FILL_ALTERNATE_DROP_PAIRED_RESPONSE_V1'
MAX_DROP_OPTIONS = 24
MAX_CONDITIONAL_CASES = 128
MAX_SCENARIOS = 128
SOURCE_BLOBS = {
    'tools/operations/action_frontier.py': '675aad726a966bd0ccc2addc5b6ce068f9421b1f',
    'tools/operations/action_fill_predictive_b2b3.py': '46ef614b639b09b02c588cb3d70ea86b70f030d6',
    'tools/operations/action_predictive_b2.py': '6b8352590eb7b898483c335b1f4532ed0860c62d',
    'tools/operations/action_partner_b2b.py': 'd6ae2e3d1fb811638a0c36054fd86da14416df53',
    'tools/operations/action_portfolio_b2b2.py': '1dc736a6edf0cd766a8477071a10ca980d731a45',
    'tools/operations/action_certification.py': '4780d467874920333141f55ddf65ed20fb02ba61',
}


def _blob(data: bytes) -> str:
    raw = data.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def check_source(root: Path) -> None:
    require(root.name.lower() == 'fantasy_football', 'B2B6_WRONG_CONTROL_ROOT')
    for rel, expected in SOURCE_BLOBS.items():
        p = root / rel
        require(p.is_file() and not p.is_symlink() and _blob(p.read_bytes()) == expected,
                'B2B6_DEPENDENCY_SOURCE_DRIFT:' + rel)


def _signature(branch: dict) -> tuple[tuple[str, int, bool], ...]:
    rows = branch.get('fill_outcomes')
    require(type(rows) is list, 'B2B6_FILL_STATE_INVALID')
    signature = []
    for x in rows:
        require(type(x) is dict and x.get('side') in ('user', 'partner') and
                type(x.get('id')) is int and x['id'] != 0 and
                type(x.get('conditional_success')) is bool,
                'B2B6_FILL_IDENTITY_INVALID')
        signature.append((x['side'], x['id'], x['conditional_success']))
    require(len({(side, pid) for side,pid,_ in signature}) == len(signature),
            'B2B6_DUPLICATE_FILL_ASSET')
    return tuple(signature)


def _conditional_rebalance_success(offer: dict, branch: dict) -> bool:
    """Gate only *hypothetical* success of frozen specialist position repair.

    This never certifies acquiring the specialist. B2b2's recorded no-guarantee
    warning is retained in its source receipt. Failure/unproven branches and
    unrelated future-fill paths continue to obey the existing blocker rule.
    """
    evidence = offer.get('blocking_evidence')
    additions = offer.get('modeled_native_auto_add_ids')
    if (type(evidence) is not list or
            'NATIVE_POSITION_REBALANCE_CONDITIONAL_FROZEN_FILL' not in evidence or
            type(additions) is not list or not additions or
            any(type(pid) is not int or pid == 0 for pid in additions) or
            len(set(additions)) != len(additions) or
            offer.get('required_user_drops_by_count') != 0 or
            offer.get('required_user_fills_by_count') != 0):
        return False
    outcomes = branch.get('fill_outcomes')
    if type(outcomes) is not list:
        return False
    if any(type(x) is not dict or
           x.get('side') not in ('user', 'partner') or
           type(x.get('id')) is not int or
           type(x.get('conditional_success')) is not bool or
           type(x.get('materialized_from_frozen_market')) is not bool
           for x in outcomes):
        return False
    user_rows = [x for x in outcomes if x['side'] == 'user']
    return (len(user_rows) == len(additions) and
            {x['id'] for x in user_rows} == set(additions) and
            all(x['conditional_success'] and x['materialized_from_frozen_market']
                for x in user_rows) and
            all(not x['conditional_success'] or x['materialized_from_frozen_market']
                for x in outcomes))


def _checked_response(response: dict, user: int, partner: int, count: int) -> dict:
    import numpy as np
    require(type(response) is dict and set(response) == {user, partner},
            'B2B6_TWO_MANAGER_RESPONSE_REQUIRED')
    out = {}
    for tid in (user, partner):
        value = response[tid]
        require(type(value) is tuple and len(value) == 2, 'B2B6_PAIRED_RESPONSE_INVALID')
        base, after = (np.asarray(x, dtype=float) for x in value)
        require(base.shape == after.shape == (count,) and np.isfinite(base).all() and
                np.isfinite(after).all(), 'B2B6_PAIRED_RESPONSE_SHAPE_OR_FINITE_INVALID')
        out[tid] = (base.copy(), after.copy())
    return out


def _mean_ci(baseline: Any, alternative: Any, *, seed: str) -> dict:
    """Deterministic resampled 68% interval of a *paired mean*, no retuning."""
    import numpy as np
    delta = np.asarray(alternative, dtype=float) - np.asarray(baseline, dtype=float)
    require(delta.ndim == 1 and 16 <= delta.size <= MAX_SCENARIOS and np.isfinite(delta).all(),
            'B2B6_INTERVAL_ARRAY_INVALID')
    rng = np.random.default_rng(int(hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16], 16))
    indices = rng.integers(0, delta.size, size=(512, delta.size))
    means = np.mean(delta[indices], axis=1)
    return {'paired_mean_interval_p16': float(np.quantile(means, .16)),
            'paired_mean_interval_p84': float(np.quantile(means, .84))}


def _summary(base: Any, alternative: Any, *, seed: str) -> dict:
    return {**paired_summary(base, alternative), **_mean_ci(base, alternative, seed=seed)}


def evaluate(snapshot: dict, capture: dict, receipt: dict, league: dict,
             model: dict, values: Path, runtime: Path, offer_id: str,
             *, scenarios: int = 32, kernel: Callable | None = None,
             frontier_provider: Callable | None = None) -> dict:
    """Evaluate all frozen drop choices, with matched future-fill branches.

    `kernel` and `frontier_provider` injection exist for synthetic tests only.
    Production entrypoint performs exact origin and installed-kernel checks.
    """
    require(type(scenarios) is int and 16 <= scenarios <= MAX_SCENARIOS,
            'B2B6_SCENARIO_BUDGET_INVALID')
    require(type(offer_id) is str and len(offer_id) == 24 and
            all(x in '0123456789abcdef' for x in offer_id), 'B2B6_OFFER_ID_INVALID')
    hashes = tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league,model))
    provider = frontier_provider or select_branch_frontier
    # Exact B2b2 structural frontier, B1 receipt binding, partner identity.
    # We request the native option to discover the complete offer; B2b2 options
    # can then be matched by drop IDs for each alternative.
    from action_frontier import build_frontier
    primary = build_frontier(snapshot,capture,receipt)
    found = [r for r in primary['offers'] if r['offer_id'] == offer_id]
    require(len(found) == 1, 'B2B6_OFFER_NOT_UNIQUE_OR_MISSING')
    offer = found[0]
    require(not offer['structural_options_truncated'],
            'B2B6_TRUNCATED_DROP_FRONTIER_NOT_CERTIFIABLE')
    options = offer['structural_options']
    require(type(options) is list and 1 <= len(options) <= MAX_DROP_OPTIONS,
            'B2B6_ALL_DROP_OPTIONS_EXCEED_BUDGET')
    require(len({tuple(x['drop_ids']) for x in options}) == len(options),
            'B2B6_DUPLICATE_DROP_OPTIONS')
    native_drop = tuple(offer['modeled_native_auto_drop_ids'])
    require(sum(tuple(x['drop_ids']) == native_drop and
                x['native_selected_normalization'] is True for x in options) == 1 and
            sum(x['native_selected_normalization'] is True for x in options) == 1,
            'B2B6_NATIVE_DROP_REFERENCE_MISSING_OR_DUPLICATE')
    require(type(receipt.get('team_id')) is int and type(offer.get('partner_team_id')) is int,
            'B2B6_MANAGER_IDENTITY_INVALID')
    user, partner = receipt['team_id'],offer['partner_team_id']
    partner_proof = partner_drop_proof(snapshot, offer)
    kernel_impl = kernel or _native_pair
    if kernel is None:
        verify_runtime(runtime)
    frozen_groups: dict[tuple, dict] = {}
    reference_signatures: set | None = None
    rows=[]
    cache=None
    baseline_arrays: dict[int, Any] = {}
    evaluated=0
    seen_cases=0
    for opt in options:
        selected = provider(snapshot,capture,receipt,league,offer_id,list(opt['drop_ids']))
        require(type(selected) is tuple and len(selected)==3,
                'B2B6_STRUCTURAL_JOIN_INVALID')
        joined, structural, material = selected
        require(joined['offer_id']==offer_id and structural['offer_id']==offer_id and
                material['drop_ids']==opt['drop_ids'], 'B2B6_DROP_JOIN_IDENTITY_CHANGED')
        branches = material['branches']
        require(type(branches) is list and branches, 'B2B6_EMPTY_FILL_LATTICE')
        signatures = [_signature(b) for b in branches]
        require(len(signatures)==len(set(signatures)), 'B2B6_FILL_LATTICE_DUPLICATES')
        if reference_signatures is None:
            reference_signatures = set(signatures)
        else:
            require(set(signatures)==reference_signatures,
                    'B2B6_DROP_COMPARISON_FILL_STATES_DIFFER')
        for branch in branches:
            seen_cases += 1
            require(seen_cases<=MAX_CONDITIONAL_CASES,
                    'B2B6_CONDITIONAL_CASE_BUDGET_EXCEEDED')
            sig = _signature(branch)
            # Frozen static and drop proof must be affirmative to run the native
            # kernel; hypothetical fills never become guaranteed acquisitions.
            conditional_rebalance = _conditional_rebalance_success(offer, branch)
            # Waive only the *blanket no-guarantee* warning for an expressly
            # assumed-success, frozen-market specialist repair. All other
            # unresolved source/position/permission blockers stay fail-closed.
            notes = [str(b) for b in branch['unresolved']]
            blockers = [b for b in notes if not (
                b.startswith('FUTURE_FILL_AT_PROCESSING_UNVERIFIED:') or
                (conditional_rebalance and
                 b == 'FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE'))]
            blockers += partner_proof
            blockers += [x for x in ('FROZEN_ESPN_DROPPABLE_NOT_TRUE',
                       'FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED')
                         if x in opt['feasibility_evidence']]
            if not all(branch[side]['frozen_static_constraints_pass'] for side in ('user','partner')):
                blockers.append('B2B6_FROZEN_STATIC_ROSTER_NOT_LEGAL')
            row={'drop_ids': list(opt['drop_ids']), 'native_selected':bool(opt['native_selected_normalization']),
                 'fill_state': [{'side':s,'asset_id':i,'conditional_success':yes} for s,i,yes in sig],
                 'state':'BLOCKED', 'blockers':sorted(set(blockers)),
                 'hypothetical_future_fill':any(yes for _,_,yes in sig),
                 'future_fill_probability':'UNKNOWN', 'espn_action_authority':'NONE',
                 'conditional_rebalance_success_assumed': conditional_rebalance}
            if not row['blockers']:
                try:
                    raw,cache_candidate=kernel_impl(snapshot,league,model,values,joined,opt,branch,
                                                  user,scenarios,runtime,cache)
                    checked=_checked_response(raw,user,partner,scenarios)
                    import numpy as np
                    for tid in (user, partner):
                        if tid in baseline_arrays:
                            require(np.array_equal(baseline_arrays[tid],checked[tid][0]),
                                    'B2B6_COMMON_BASELINE_SCENARIO_AXIS_DRIFT')
                        else:
                            baseline_arrays[tid]=checked[tid][0].copy()
                    require(type(cache_candidate) is dict,'B2B6_BASELINE_CACHE_INVALID')
                    cache=cache_candidate
                    row['hold_comparison'] = {
                        label:_summary(*checked[tid],seed=hashes[2]+offer_id+str(tid)+str(sig)+str(opt['drop_ids']))
                        for label,tid in (('user',user),('partner',partner))}
                    row['state']='CONDITIONAL_MC_VS_NO_ACTION_NOT_CERTIFIED'
                    evaluated+=1
                    group=frozen_groups.setdefault(sig, {'rows':[]})
                    group['rows'].append((row,checked))
                except (CertificationBlocked,ValueError,RuntimeError,TypeError,KeyError,ImportError,OSError) as exc:
                    row['blockers'].append(str(exc) if isinstance(exc,CertificationBlocked)
                                           else 'NATIVE_MC_EXCEPTION:'+type(exc).__name__)
            rows.append(row)
    # Every comparison shares the same manager/branch and baseline; no mixing
    # conditional fill states and no cross-manager random-vector subtraction.
    for signature, group in frozen_groups.items():
        base = [pair for pair in group['rows'] if pair[0]['native_selected']]
        if len(base) != 1:
            for row,_ in group['rows']:
                row['drop_comparison']={'status':'BLOCKED_NATIVE_DROP_REFERENCE_NOT_EVALUATED'}
            continue
        benchmark = base[0][1]
        for row,response in group['rows']:
            row['versus_native_drop_same_fill_state'] = {
                label:_summary(benchmark[tid][1],response[tid][1],
                    seed=hashes[2]+offer_id+'alternate'+str(tid)+str(signature)+str(row['drop_ids']))
                for label,tid in (('user',user),('partner',partner))}
    require(tuple(canonical_sha256(x) for x in (snapshot,capture,receipt,league,model)) == hashes,
            'B2B6_FROZEN_INPUTS_CHANGED_DURING_EVALUATION')
    return {'contract':CONTRACT,'offer_id':offer_id,'frozen_sha256':dict(zip(
                ('snapshot','capture','receipt','league','model'),hashes)),
            'drop_options_total':len(options),'conditional_cases_total':len(rows),
            'native_mc_cases_evaluated':evaluated,'scenarios_per_case':scenarios,
            'options':rows,'comparisons_crossing_fill_states':'PROHIBITED',
            'cross_manager_draw_pairing':'PROHIBITED',
            'future_fill_joint_probability':'UNKNOWN',
            'unresolved':['ACTUAL_TRADE_EFFECTIVE_TIME_AND_ESPN_LEGALITY_UNVERIFIED',
                          'PREDICTIVE_INJURY_CONTINGENCY_STRESS_TEST_NOT_COMPLETE',
                          'FUTURE_FILL_AND_MANAGER_ACCEPTANCE_CORRELATION_UNESTIMATED',
                          'JOINT_OFFER_PORTFOLIO_PAIRED_UTILITY_NOT_CERTIFIED',
                          'RELEASED_ASSET_FIELD_REACQUISITION_NOT_MODELED'],
            'state':'BLOCKED_B2B6_CONDITIONAL_PAIRED_DROP_MC_ONLY',
            'certified_actions':0,'espn_action_authority':'NONE'}


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path('.'))
    for field in ('snapshot','capture','receipt','league','model','values','runtime'):
        parser.add_argument('--'+field,required=True,type=Path)
    parser.add_argument('--offer-id',required=True)
    parser.add_argument('--scenarios',type=int,default=32)
    parser.add_argument('--out',type=Path,required=True,help='New private JSON output under runtime/data')
    args=parser.parse_args(argv)
    print('B2B6 CONDITIONAL MATCHED-FILL ALTERNATE-DROP PAIRED MC')
    try:
        root=args.project_root.resolve()
        check_source(root)
        runtime=args.runtime.resolve()
        out=args.out.resolve()
        require(out.parent == (runtime/'data').resolve() and not out.exists(),
                'B2B6_PRIVATE_NEW_RUNTIME_DATA_OUTPUT_REQUIRED')
        docs=[]
        for field in ('snapshot','capture','receipt','league','model'):
            p=getattr(args,field).resolve()
            require(p.is_file() and not p.is_symlink() and 0<p.stat().st_size<=64*1024*1024,
                    'B2B6_INPUT_NOT_SAFE:'+field)
            docs.append(json.loads(p.read_text(encoding='utf-8-sig')))
        result=evaluate(*docs,args.values.resolve(),runtime,args.offer_id,scenarios=args.scenarios)
        raw=(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode('utf-8')
        require(len(raw)<8*1024*1024,'B2B6_OUTPUT_SIZE_BUDGET')
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('xb') as f:
            f.write(raw)
        print('STATUS='+result['state']+';DROP_OPTIONS='+str(result['drop_options_total'])+
              ';CONDITIONAL_CASES='+str(result['conditional_cases_total'])+
              ';MC_CASES_EVALUATED='+str(result['native_mc_cases_evaluated']))
        print('ESPN_GETS=NONE;ESPN_WRITES=NONE;NATIVE_WEEKLY_MC=NOT_REPEATED;ACTION_AUTHORITY=NONE')
        return 0
    except (CertificationBlocked,ValueError,TypeError,KeyError,OSError) as exc:
        reason=str(exc) if isinstance(exc,CertificationBlocked) else type(exc).__name__
        print('B2B6_BLOCKED='+reason+';ACTION_AUTHORITY=NONE')
        return 3


if __name__=='__main__':
    raise SystemExit(main())
