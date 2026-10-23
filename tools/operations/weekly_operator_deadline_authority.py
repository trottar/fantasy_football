"""M1b pure read-only deadline/refresh planning evidence classifier.

This is NOT a transaction deadline resolver, refresh launcher, or ESPN action
certificate. It refuses to infer a waiver claim cutoff from waiverProcessHour,
waiverProcessDays or waiverHours, or a trade effect from deadlineDate/revisionHours.
A supplied proof is only structurally checked; independent source authentication,
asset-specific app legality and post-MC reconciliation remain separate gates.
No network, I/O, durable writes, football calculation or runtime imports.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
import re
from typing import Any, Mapping

LIVE_MAX_SECONDS = 60
PUBLIC_MAX_SECONDS = 120
CUTOFF_PROOF_MAX_SECONDS = 60
REFRESH_MEASUREMENT_MAX_DAYS = 14
MC_MINUTES = 40
LIVE_VERIFICATION_MINUTES = 15
APPROVAL_MINUTES = 15
SAFETY_MINUTES = 10
MINIMUM_AFTER_REFRESH_MINUTES = (MC_MINUTES + LIVE_VERIFICATION_MINUTES
                                 + APPROVAL_MINUTES + SAFETY_MINUTES)
VALID_LIVE_STATUSES = frozenset({
    'READONLY_LIVE_CALENDAR_LOCK_CORROBORATED',
    'READONLY_PARTIAL_SCOPE_CALENDAR_LOCK_CORROBORATED',
    'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED',
})
ESPN_PUBLIC_NFLVERSE = 'PUBLIC_ESPN_SCOREBOARD_PLUS_PUBLISHED_NFL_BYES_PLUS_FROZEN_NFLVERSE'
SHA256 = re.compile(r'^[0-9a-f]{64}$')


class EvidenceInvalid(ValueError):
    """Malformed required input; do not attempt to repair by inference."""


def utc(value: Any) -> datetime | None:
    """Accept aware datetimes or aware ISO strings; never local/naive clocks."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, OverflowError):
            return None
    else:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo and dt.utcoffset() is not None else None


def _age(now: datetime, prior: Any, seconds: int) -> bool:
    ts = utc(prior)
    return ts is not None and timedelta(0) <= now - ts <= timedelta(seconds=seconds)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _refresh_lead(measurement: Any, now: datetime) -> tuple[int | None, str]:
    if not isinstance(measurement, Mapping):
        return None, 'BLOCKED_REFRESH_MEASUREMENT_MISSING'
    if (measurement.get('source') != 'LOCAL_MEASURED_SIX_PROVIDER_SYNC'
            or measurement.get('runtime_version') != '0.36'
            or not _sha(measurement.get('receipt_sha256'))
            or not _age(now, measurement.get('measured_at_utc'),
                        REFRESH_MEASUREMENT_MAX_DAYS * 86400)):
        return None, 'BLOCKED_REFRESH_MEASUREMENT_UNVERIFIED'
    duration = measurement.get('duration_seconds')
    buffer = measurement.get('buffer_seconds')
    if (type(duration) is not int or not 0 < duration <= 7200
            or type(buffer) is not int or not 60 <= buffer <= 3600):
        return None, 'BLOCKED_REFRESH_DURATION_OR_BUFFER_INVALID'
    return ceil((duration + buffer) / 60), 'REFRESH_LEAD_MEASURED_NOT_COMMISSIONED'


def _cutoff_shape(family: str, proof: Any, now: datetime,
                  planning_minutes: int | None) -> dict[str, Any]:
    """An explicit action-screen envelope is NOT a verified ESPN action."""
    required = ('cutoff_utc',) if family == 'waiver' else ('cutoff_utc', 'effective_utc')
    base: dict[str, Any] = {'classification': 'BLOCKED_EXACT_CUTOFF_UNVERIFIED',
                            'source_kind': 'NONE', 'action_authority': 'NONE'}
    if not isinstance(proof, Mapping):
        return base
    if (proof.get('source') != 'LIVE_ESPN_ACTION_SCREEN'
            or proof.get('family') != family
            or not _sha(proof.get('source_sha256'))
            or not _sha(proof.get('candidate_scope_sha256'))
            or not _age(now, proof.get('observed_at_utc'), CUTOFF_PROOF_MAX_SECONDS)):
        return {**base, 'classification': 'BLOCKED_CUTOFF_PROOF_PROVENANCE'}
    times = {key: utc(proof.get(key)) for key in required}
    if any(value is None for value in times.values()):
        return {**base, 'classification': 'BLOCKED_CUTOFF_TIMESTAMP_UNKNOWN'}
    if family == 'trade' and times['effective_utc'] <= now:
        # Effect may legally precede the league's final submission deadline.
        # Only a past/elapsed effect contradicts a new prospective submission.
        return {**base, 'classification': 'BLOCKED_TRADE_EFFECT_ALREADY_ELAPSED'}
    cutoff = times['cutoff_utc']
    if cutoff <= now:
        state = 'BLOCKED_CLAIM_OR_SUBMISSION_CUTOFF_PASSED'
    elif planning_minutes is None:
        state = 'BLOCKED_REFRESH_LEAD_UNKNOWN'
    elif cutoff <= now + timedelta(minutes=planning_minutes):
        state = 'BLOCKED_INSUFFICIENT_CUTOFF_LEAD'
    else:
        state = 'CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'
    return {**base, 'classification': state,
            'source_kind': 'LIVE_ESPN_ACTION_SCREEN_UNVERIFIED_ENVELOPE',
            'cutoff_utc': cutoff.isoformat(),
            'effective_utc': times['effective_utc'].isoformat() if family == 'trade' else None}


def classify(*, now: datetime, live_lock_result: Mapping[str, Any],
             live_observed_at_utc: Any, rule_source_shapes: Any = None,
             refresh_measurement: Any = None, cutoff_proofs: Any = None) -> dict[str, Any]:
    """Pure sanitized aggregate planning state; *never* authorizes an action.

    Caller must independently prove actual evidence provenance; this API only
    enforces shape, consistency, chronology, source labels and bounded timing.
    No future timestamp, marker or proof here can grant ESPN execution.
    """
    now_utc = utc(now)
    if now_utc is None or not isinstance(live_lock_result, Mapping):
        raise EvidenceInvalid('NOW_OR_LIVE_RESULT_INVALID')
    live = live_lock_result
    # A previous report's 'check_age_seconds' alone can never be treated as
    # current. The independent observation timestamp is mandatory.
    status = live.get('status')
    owner_ok = (status in VALID_LIVE_STATUSES
                and live.get('phase') == 'M1B_PRE_REFRESH_LIVE_OWNED_LOCK_READONLY'
                and live.get('calendar_corrob_source') == ESPN_PUBLIC_NFLVERSE
                and live.get('season') == 2026
                and type(live.get('week')) is int and 1 <= live['week'] <= 18
                and live.get('fresh_authenticated_espn_gets') == 1
                and live.get('unknown_live_lock_records') == 0
                and type(live.get('future_unlocked_records')) is int
                and live['future_unlocked_records'] > 0
                and live.get('espn_writes') is False
                and live.get('action_authority') == 'NONE'
                and _age(now_utc, live_observed_at_utc, LIVE_MAX_SECONDS)
                and type(live.get('public_calendar_check_age_seconds')) in (int, float)
                and 0 <= live['public_calendar_check_age_seconds'] <= PUBLIC_MAX_SECONDS
                and type(live.get('live_roster_check_age_seconds')) in (int, float)
                and 0 <= live['live_roster_check_age_seconds'] <= LIVE_MAX_SECONDS)
    earliest = utc(live.get('earliest_future_unlocked_kickoff_utc')) if owner_ok else None
    if earliest is None or earliest <= now_utc:
        owner_ok = False
    cutoff_block = (rule_source_shapes.get('cutoff_certification')
                    if isinstance(rule_source_shapes, Mapping) else None)
    shapes_only = (isinstance(rule_source_shapes, Mapping)
                   and isinstance(cutoff_block, Mapping)
                   and rule_source_shapes.get('source') == 'ESPN_PRIVATE_MSETTINGS'
                   and rule_source_shapes.get('probe') == 'M1B_PRIVATE_ESPN_RULE_FIELD_SHAPES_V3'
                   and cutoff_block.get('source_shape_only') is True
                   and rule_source_shapes.get('action_authority') == 'NONE')
    refresh_minutes, refresh_state = _refresh_lead(refresh_measurement, now_utc)
    planning_minutes = MINIMUM_AFTER_REFRESH_MINUTES + refresh_minutes if refresh_minutes is not None else None
    if not owner_ok:
        plan = 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE'
    elif refresh_minutes is None:
        plan = refresh_state
    elif earliest <= now_utc + timedelta(minutes=planning_minutes):
        plan = 'BLOCKED_INSUFFICIENT_PROTECTED_LEAD'
    else:
        plan = 'PROVISIONAL_PLANNING_WINDOW_NOT_REFRESH_AUTHORITY'
    evidence = cutoff_proofs if isinstance(cutoff_proofs, Mapping) else {}
    return {
        'phase': 'M1B_DEADLINE_AUTHORITY_SOURCE_ONLY',
        'planning_status': plan,
        'lineup_window': ('GAME_LOCK_WINDOW_OBSERVED_NOT_ACTION_AUTHORITY'
                          if owner_ok else 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE'),
        'waiver_window': _cutoff_shape('waiver', evidence.get('waiver'), now_utc,
                                       planning_minutes) if owner_ok else
                         {'classification': 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE', 'action_authority': 'NONE'},
        'trade_window': _cutoff_shape('trade', evidence.get('trade'), now_utc,
                                      planning_minutes) if owner_ok else
                        {'classification': 'BLOCKED_LIVE_GAME_LOCK_EVIDENCE', 'action_authority': 'NONE'},
        'transaction_source_shapes_observed': shapes_only,
        'transaction_source_shapes_are_cutoffs': False,
        'earliest_future_owned_game_utc': earliest.isoformat() if owner_ok else None,
        'minimum_after_refresh_minutes': MINIMUM_AFTER_REFRESH_MINUTES,
        'measured_refresh_plus_buffer_minutes': refresh_minutes,
        'total_planning_minutes': planning_minutes,
        'elapsed_or_unknown_assets_must_be_excluded': True,
        'unresolved_asset_specific_legality': True,
        'refresh_authority': 'NONE', 'capture_authority': 'NONE',
        'action_authority': 'NONE', 'automatic_refresh_or_capture': False,
        'native_mc_started': False, 'espn_writes': False,
    }
