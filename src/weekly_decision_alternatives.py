"""Bounded presentation evidence for evaluated (not merely actionable) MC frontiers.

This pure, observational projection NEVER scores, simulates, reclassifies, filters
football actions, or authorizes ESPN transactions. It preserves the native
classification and original MC sample stage for each already-evaluated row.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

LIMIT_PER_CLASS = 6


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        val = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return val if math.isfinite(val) else None


def _name(value: Any) -> str | None:
    if not isinstance(value, str) or not (1 <= len(value) <= 150):
        return None
    if not value.isprintable() or '\n' in value or '\r' in value:
        return None
    return value


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return min(value, 1000000)


def player_alternatives(report: Mapping[str, Any]) -> dict[str, Any]:
    """Retain evaluated add/drop response by ESPN acquisition state, with holds.

    The count 'candidate_pool_evaluated' is cheap PRESELECTION, not paired MC.
    Rows missing a native classification are not promoted to an actionable item.
    """
    result: dict[str, Any] = {
        'schema': 'EVALUATED_PLAYER_FRONTIER_PRESENTATION_V1',
        'authority': 'OBSERVATION_ONLY', 'screen_is_not_authority': True,
        'candidate_pool_preselected': _count(report.get('candidate_pool_evaluated')),
        'screen_actions_total': _count(report.get('screen_actions_total')),
        'predictive_actions_evaluated': _count(report.get('predictive_actions_evaluated')),
        'predictive_actions_final_stage': _count(report.get('predictive_actions_final_stage')),
        'predictive_mc_stopped_for_futility': bool(report.get('predictive_mc_stopped_for_futility')),
        'groups': [],
    }
    for status, key in (('FREEAGENT', 'free_agent_actions'), ('WAIVERS', 'waiver_actions')):
        rows = report.get(key) or []
        if not isinstance(rows, list):
            rows = []
        ranked = sorted(
            (row for row in rows if isinstance(row, Mapping)),
            key=lambda r: (_number(r.get('expected_delta_utility')) is not None,
                           _number(r.get('expected_delta_utility')) if _number(r.get('expected_delta_utility')) is not None else float('-inf')),
            reverse=True,
        )
        bounded = []
        for row in ranked[:LIMIT_PER_CLASS]:
            native = _name(row.get('combined_action_classification') or row.get('action_classification'))
            bounded.append({
                'add': _name(row.get('add_name')),
                'drop': _name(row.get('drop_name')),
                'classification': native or 'UNCLASSIFIED_NATIVE_ROW',
                'expected_delta_utility': _number(row.get('expected_delta_utility')),
                'paired_mean_delta_utility': _number(row.get('delta_utility')),
                'paired_mean_interval_p16': _number(row.get('delta_total_utility_p16')),
                'paired_mean_interval_p84': _number(row.get('delta_total_utility_p84')),
                'p_better_if_acquired': _number(row.get('p_utility_better_if_acquired')),
                'p_acquire': _number(row.get('p_acquire')),
                'mc_scenarios': _count(row.get('mc_scenarios')),
                'mc_stage': _name(row.get('mc_stage')),
                'futility_stop': row.get('mc_futility_stop') is True,
                'transaction_authority': 'NONE',
            })
        result['groups'].append({
            'acquisition_state': status,
            'native_reported_count': len(rows),
            'retained_count': len(bounded),
            'truncated': len(rows) > len(bounded),
            'alternatives': bounded,
        })
    return result


def trade_alternatives(rows: Sequence[Mapping[str, Any]], *, family: str) -> dict[str, Any]:
    """Preserve evaluated native trade diagnoses without reclassifying any offer."""
    ranked = sorted(
        (row for row in rows if isinstance(row, Mapping)),
        key=lambda r: (_number(r.get('expected_offer_value')) is not None,
                       _number(r.get('expected_offer_value')) if _number(r.get('expected_offer_value')) is not None else float('-inf')),
        reverse=True,
    )
    out = []
    for row in ranked[:LIMIT_PER_CLASS]:
        out.append({
            'give': _name(row.get('give_name')),
            'receive': _name(row.get('receive_name')),
            'partner': _name(row.get('partner_name')),
            'package_family': _name(row.get('package_family')),
            'classification': _name(row.get('classification')) or 'UNCLASSIFIED_NATIVE_ROW',
            'expected_offer_value': _number(row.get('expected_offer_value')),
            'our_delta_season_ppg': _number(row.get('our_delta_season_ppg')),
            'partner_delta_season_ppg': _number(row.get('partner_delta_season_ppg')),
            'our_delta_complete_state_utility': _number(row.get('our_delta_complete_state_utility')),
            'partner_delta_complete_state_utility': _number(row.get('partner_delta_complete_state_utility')),
            'p_accept': _number(row.get('p_accept')),
            'mc_scenarios': _count(row.get('mc_scenarios')),
            'transaction_authority': 'NONE',
        })
    return {
        'schema': 'EVALUATED_TRADE_FRONTIER_PRESENTATION_V1',
        'authority': 'OBSERVATION_ONLY', 'screen_is_not_authority': True,
        'family': family, 'native_reported_count': len(rows),
        'retained_count': len(out), 'truncated': len(rows) > len(out),
        'alternatives': out,
    }
