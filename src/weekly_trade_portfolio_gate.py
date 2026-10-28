"""Fail-closed, read-only assembly of frozen native trades and Slice-A blockers.

This is a certificate *status* compositor, not a valuation kernel or ESPN action
certificate. A standalone native ACTIONABLE_OFFER is never a portfolio decision.
No HTTP, Monte Carlo, persistence or runtime mutation occurs here.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

CONTRACT = 'WEEK8_B2B5_FROZEN_TRADE_PORTFOLIO_GATE_V1'
TRADE_CHANNELS = ('trade_one_for_one_player', 'trade_multi_player_unequal',
                  'trade_specialist_inclusive')
MAX_CANDIDATES = 32
MAX_PAIRS = 496

class GateBlocked(ValueError):
    pass

def need(ok: bool, reason: str) -> None:
    if not ok:
        raise GateBlocked(reason)

def _ids(row: Mapping[str, Any], key: str) -> set[int]:
    v = row.get(key)
    need(isinstance(v, list) and all(type(x) is int for x in v),
         'NATIVE_IDS_UNAVAILABLE:' + key)
    need(len(v) == len(set(v)), 'NATIVE_DUPLICATE_ASSET:' + key)
    return set(v)

def _text(value: Any) -> str:
    need(isinstance(value, str) and 0 < len(value) <= 150 and
         value.isprintable() and '\n' not in value and '\r' not in value,
         'NATIVE_ASSET_NAME_INVALID')
    return value

def _labels(raw: Mapping[str, Any], side: str) -> list[str]:
    names = raw.get(side + '_names')
    if isinstance(names, list) and names:
        need(len(names) <= 2, 'NATIVE_ASSET_LIST_UNBOUNDED')
        return [_text(x) for x in names]
    name = raw.get(side + '_name')
    need(isinstance(name, str), 'NATIVE_ASSET_NAMES_MISSING')
    return [_text(name)]

def assemble(cert: Mapping[str, Any], receipt: Mapping[str, Any],
             trial: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble exact frozen candidate conflicts; never infer joint MC value.

    `cert` must be the output of the repository's existing provenance-verified
    action_certification.certify_receipt(snapshot, capture, receipt).
    """
    need(cert.get('contract') == 'WEEKLY_ACTION_CERTIFICATION_READONLY_SCAFFOLD_V1',
         'SLICE_A_CONTRACT_INVALID')
    need(cert.get('frozen_input_integrity') == 'PASS' and
         cert.get('certified_action_count') == 0 and
         cert.get('espn_action_authority') == 'NONE', 'SLICE_A_AUTHORITY_INVALID')
    need(receipt.get('week') == cert.get('week') and receipt.get('season') == cert.get('season'),
         'CERTIFICATION_EPOCH_INVALID')
    need(trial.get('week') == receipt.get('week') and trial.get('season') == receipt.get('season')
         and trial.get('transaction_authority') == 'NONE'
         and trial.get('commissioning_trial') is True,
         'TRIAL_NOT_SCOPED_OBSERVATION')
    channels = receipt.get('channels')
    need(isinstance(channels, list), 'NATIVE_CHANNELS_INVALID')
    native = []
    keys = []
    for c in channels:
        need(isinstance(c, dict) and isinstance(c.get('key'), str), 'NATIVE_CHANNEL_SHAPE_INVALID')
        if c['key'] not in TRADE_CHANNELS:
            continue
        keys.append(c['key'])
        action = c.get('action') or {}
        need(isinstance(action, dict) and isinstance(action.get('offers') or [], list),
             'NATIVE_OFFERS_SHAPE_INVALID')
        for row in action.get('offers') or []:
            need(isinstance(row, dict), 'NATIVE_OFFER_SHAPE_INVALID')
            native.append((c['key'], row))
    need(sorted(keys) == sorted(TRADE_CHANNELS), 'NATIVE_TRADE_CHANNEL_COVERAGE_INVALID')
    candidates = cert.get('candidates')
    need(isinstance(candidates, list) and len(candidates) == len(native)
         and len(candidates) <= MAX_CANDIDATES and cert.get('candidate_count') == len(native),
         'CANDIDATE_MAPPING_COUNT_INVALID')
    started = set()
    for q in trial.get('queue') or []:
        if isinstance(q, dict) and q.get('family') == 'LINEUP':
            for p in q.get('proposals') or []:
                if isinstance(p, dict) and p.get('direction') == 'START' and isinstance(p.get('player'), dict):
                    name = p['player'].get('name')
                    if isinstance(name, str): started.add(name)
    prepared = []
    for idx, ((channel, raw), row) in enumerate(zip(native, candidates)):
        need(isinstance(row, dict) and row.get('channel') == channel
             and row.get('final_decision') == 'BLOCKED'
             and row.get('espn_action_authority') == 'NONE',
             'SLICE_A_ROW_AUTHORITY_INVALID')
        give = _labels(raw, 'give')
        receive = _labels(raw, 'receive')
        need(give == row.get('give') and receive == row.get('receive'),
             'NATIVE_CERTIFIED_ASSET_ORDER_MISMATCH')
        g = _ids(raw, 'give_ids')
        r = _ids(raw, 'receive_ids')
        d = _ids(raw, 'user_auto_drop_ids')
        a = _ids(raw, 'user_auto_add_ids')
        need(bool(g) and bool(r) and not(g & r) and not(g & d) and
             all(type(x) is int for x in g | r | d | a), 'OFFER_STATE_INVALID')
        blockers = set(row.get('blockers') or [])
        need(bool(blockers) and all(isinstance(x, str) and x for x in blockers),
             'CERTIFICATE_BLOCKERS_MISSING')
        if set(give) & started:
            blockers.add('TRADE_REMOVES_FROZEN_PROPOSED_STARTER')
        if d:
            blockers.add('MANDATORY_DROP_ALTERNATIVES_NOT_PAIRED_CERTIFIED')
        if a:
            blockers.add('FUTURE_FILL_NOT_GUARANTEED')
        blockers.add('NO_ACTION_VS_BEST_FEASIBLE_JOINT_STRATEGY_NOT_CERTIFIED')
        prepared.append({'ordinal': idx + 1, 'channel': channel,
                         'give': give, 'receive': receive,
                         'give_label': ' + '.join(give), 'receive_label': ' + '.join(receive),
                         'native_classification': row.get('native_classification'),
                         'mandatory_user_drops': list(row.get('mandatory_user_drops') or []),
                         'remaining_qbs': list(row.get('remaining_qbs') or []),
                         'post_trade_qb_count_if_native_drops_executed': row.get('post_trade_qbs_count_if_native_drops_executed'),
                         'modeled_earliest_effective_week': row.get('modeled_earliest_effective_week'),
                         'blockers': sorted(blockers), 'final_decision': 'BLOCKED',
                         'espn_action_authority': 'NONE'})
    pairs = []
    for i, (achannel, a) in enumerate(native):
        for j in range(i + 1, len(native)):
            b = native[j][1]
            direct = _ids(a, 'give_ids') & _ids(b, 'give_ids')
            direct |= _ids(a, 'receive_ids') & _ids(b, 'receive_ids')
            drops = (_ids(a, 'user_auto_drop_ids') & _ids(b, 'give_ids')) | \
                    (_ids(b, 'user_auto_drop_ids') & _ids(a, 'give_ids'))
            fills = (_ids(a, 'user_auto_add_ids') & _ids(b, 'user_auto_add_ids'))
            same_partner = (type(a.get('partner_team_id')) is int and
                            a.get('partner_team_id') == b.get('partner_team_id'))
            if direct or drops or fills or same_partner:
                pairs.append({'first_ordinal': i + 1, 'second_ordinal': j + 1,
                              'kind': 'DIRECT_ASSET_CONFLICT' if direct or drops or fills else
                                      'SHARED_PARTNER_SEQUENTIAL_RESPONSE_UNKNOWN',
                              'joint_mc_certified': False})
    need(len(pairs) <= MAX_PAIRS, 'PORTFOLIO_PAIR_BUDGET_EXCEEDED')
    return {'contract': CONTRACT, 'week': receipt.get('week'),
            'slot': trial.get('slot'), 'candidate_count': len(prepared),
            'candidates': prepared, 'conflicts': pairs, 'conflict_count': len(pairs),
            'joint_portfolio_value': 'NOT_COMPUTED',
            'approved_recommendation_count': 0,
            'final_state': 'BLOCKED_PENDING_COMPLETE_PORTFOLIO_AND_LIVE_ESPN_CERTIFICATION',
            'espn_action_authority': 'NONE', 'espn_writes': False}
