"""M1b observational source owner: rebind fresh live locks to immutable bytes.

Only the existing published live-lock reader may fetch ESPN.  No refresh,
capture, MC, ESPN transactions, or cutoffs are initiated or inferred.  An
explicitly separate future writer must supply measured refresh/transaction
receipts before the published deadline classifier can evaluate those windows.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

# Git-blob identities from the exact published source checkpoint.  This is a
# source identity guard, not a signature/authentication primitive.
DEPENDENCY_BLOBS = {
    'tools/operations/weekly_operator_live_lock_evidence.py': 'fec304904c060f4b0890f8d993160b2a15bbc370',
    'tools/operations/weekly_operator_deadline_authority.py': '36d587d5110a2e4ea27cbd9cb7cc460d245046af',
    'tools/operations/weekly_operator_lock_preflight.py': '6aac22bd4c2bee80d992be8f3d4fbbfbb25e981f',
    'tools/operations/weekly_operator_calendar_evidence.py': 'b5d488ebc6b476629a38f610c122ed57c6aec779',
}
MAX_PROBE_SECONDS = 60
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024


class Blocked(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Blocked(reason)


def aware(value: Any) -> datetime:
    need(isinstance(value, datetime) and value.tzinfo is not None and
         value.utcoffset() is not None, 'NAIVE_OR_INVALID_OBSERVATION_CLOCK')
    return value.astimezone(timezone.utc)


def git_blob(raw: bytes) -> str:
    data = raw.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def source_guard(root: Path) -> dict[str, str]:
    observed = {}
    for rel, expected in DEPENDENCY_BLOBS.items():
        file = root / rel
        need(file.is_file() and not file.is_symlink(), 'SOURCE_DEPENDENCY_MISSING_OR_SYMLINK')
        digest = git_blob(file.read_bytes())
        need(digest == expected, 'SOURCE_DEPENDENCY_BLOB_MISMATCH')
        observed[rel] = digest
    return observed


def exact_snapshot(runtime: Path, week: int) -> tuple[dict, str]:
    base = runtime / 'data/season_snapshots'
    latest = base / 'latest.json'
    need(latest.is_file() and not latest.is_symlink(), 'LATEST_SNAPSHOT_MISSING')
    size = latest.stat().st_size
    need(0 < size <= MAX_SNAPSHOT_BYTES, 'SNAPSHOT_SIZE_OUT_OF_BOUNDS')
    raw = latest.read_bytes()
    try:
        snap = json.loads(raw.decode('utf-8-sig'))
    except (ValueError, UnicodeError) as exc:
        raise Blocked('SNAPSHOT_JSON_INVALID') from exc
    need(isinstance(snap, dict) and isinstance(snap.get('espn'), dict), 'SNAPSHOT_SHAPE_INVALID')
    need(snap['espn'].get('season') == 2026 and snap['espn'].get('week') == week,
         'FROZEN_SNAPSHOT_WEEK_MISMATCH')
    ident = hashlib.sha256(raw).hexdigest()
    matches = []
    for path in base.glob('*/snapshot.json'):
        if path.is_file() and not path.is_symlink() and path.stat().st_size == len(raw):
            if path.read_bytes() == raw:
                matches.append(path)
    need(len(matches) == 1, 'IMMUTABLE_SNAPSHOT_COPY_NOT_UNIQUE')
    return snap, ident


def audit(root: Path, *, week: int, clock: Callable[[], datetime] | None = None,
          runtime_validator: Callable[[Path], Path] | None = None,
          live_reader: Callable[..., dict] | None = None,
          deadline_classifier: Callable[..., dict] | None = None) -> dict:
    """Read-only source-bound observation.  Injected collaborators are test-only.

    In production, the pre-existing validated reader performs one public and
    one private ESPN GET; no other network operation is introduced here.
    The result is *not* an action or a refresh authorization.
    """
    need(root.name.casefold() == 'fantasy_football', 'WRONG_CONTROL_ROOT')
    need(type(week) is int and 1 <= week <= 18, 'INVALID_WEEK')
    deps_before = source_guard(root)
    if runtime_validator is None or live_reader is None or deadline_classifier is None:
        ops = str(root / 'tools/operations')
        if ops not in sys.path:
            sys.path.insert(0, ops)
        if runtime_validator is None:
            from guarded_weekly_cycle import validate_root
            runtime_validator = validate_root
        if live_reader is None:
            from weekly_operator_live_lock_evidence import run as live_run
            live_reader = live_run
        if deadline_classifier is None:
            from weekly_operator_deadline_authority import classify
            deadline_classifier = classify
    runtime = runtime_validator(root)
    need(isinstance(runtime, Path) and runtime.resolve() ==
         (root / 'fantasy_season_v0_36_repack1').resolve(), 'COMMISSIONED_RUNTIME_IDENTITY_INVALID')
    _snap, snap_sha = exact_snapshot(runtime, week)
    now = clock or (lambda: datetime.now(timezone.utc))
    started = aware(now())
    live = live_reader(root, week=week)
    ended = aware(now())
    need(isinstance(live, dict), 'LIVE_RESULT_INVALID')
    need(timedelta(0) <= ended-started <= timedelta(seconds=MAX_PROBE_SECONDS),
         'LIVE_OBSERVATION_DURATION_UNBOUNDED')
    _snap_after, snap_after = exact_snapshot(runtime, week)
    need(snap_after == snap_sha, 'FROZEN_SNAPSHOT_CHANGED_DURING_OBSERVATION')
    need(source_guard(root) == deps_before, 'SOURCE_CHANGED_DURING_OBSERVATION')
    need(live.get('frozen_snapshot_sha256') == snap_sha, 'LIVE_RESULT_SNAPSHOT_BINDING_MISMATCH')
    need(live.get('season') == 2026 and live.get('week') == week,
         'LIVE_RESULT_WEEK_MISMATCH')
    # Explicitly omit caller-provided cutoff envelopes and synthetic refresh
    # durations.  We have no commissioned source producer for either yet.
    plan = deadline_classifier(now=ended, live_lock_result=live,
                               live_observed_at_utc=ended,
                               rule_source_shapes=None,
                               refresh_measurement=None, cutoff_proofs=None)
    need(isinstance(plan, dict) and plan.get('action_authority') == 'NONE'
         and plan.get('refresh_authority') == 'NONE'
         and plan.get('capture_authority') == 'NONE'
         and plan.get('espn_writes') is False
         and plan.get('native_mc_started') is False
         and plan.get('automatic_refresh_or_capture') is False,
         'CLASSIFIER_AUTHORITY_BOUNDARY_CHANGED')
    need(plan.get('transaction_source_shapes_are_cutoffs') is False,
         'CLASSIFIER_CUTOFF_BOUNDARY_CHANGED')
    need(plan.get('waiver_window', {}).get('classification') not in
         {'CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'}
         and plan.get('trade_window', {}).get('classification') not in
         {'CUTOFF_WINDOW_STRUCTURALLY_ATTESTED_NOT_TRANSACTION_CERTIFIED'},
         'UNVERIFIED_TRANSACTION_WINDOW_PROMOTED')
    return {
        'phase': 'M1B_SOURCE_BOUND_LIVE_EVIDENCE_READONLY',
        'source_binding': 'EXACT_SOURCE_BLOBS_AND_IMMUTABLE_SNAPSHOT',
        'snapshot_sha256': snap_sha, 'season': 2026, 'week': week,
        'observation_utc': ended.isoformat(),
        'live_status': live.get('status') if live.get('status') in
            {'READONLY_LIVE_CALENDAR_LOCK_CORROBORATED',
             'READONLY_PARTIAL_SCOPE_CALENDAR_LOCK_CORROBORATED',
             'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED',
             'BLOCKED_UNKNOWN_LIVE_LOCK',
             'BLOCKED_NO_FUTURE_UNLOCKED_OWNED_GAME',
             'BLOCKED_INSUFFICIENT_PROTECTED_LEAD'} else 'UNRECOGNIZED_OR_BLOCKED',
        'planning_status': plan.get('planning_status'),
        'lineup_window': plan.get('lineup_window'),
        'refresh_receipt_source': 'UNAVAILABLE_NOT_YET_COMMISSIONED',
        'waiver_cutoff_source': 'UNAVAILABLE_NOT_YET_COMMISSIONED',
        'trade_cutoff_source': 'UNAVAILABLE_NOT_YET_COMMISSIONED',
        'waiver_window': plan['waiver_window']['classification'],
        'trade_window': plan['trade_window']['classification'],
        'public_espn_gets': 1, 'authenticated_espn_gets': 1,
        'refresh_authority': 'NONE', 'capture_authority': 'NONE',
        'action_authority': 'NONE', 'espn_writes': False,
        'automatic_refresh_or_capture': False, 'native_mc_started': False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default='.')
    p.add_argument('--week', type=int, required=True)
    opts = p.parse_args(argv)
    print('M1B SOURCE-BOUND LIVE EVIDENCE OWNER READONLY', flush=True)
    try:
        result = audit(Path(opts.project_root).resolve(), week=opts.week)
        print('SOURCE_EVIDENCE_RESULT=' + json.dumps(result, sort_keys=True,
              separators=(',', ':')), flush=True)
        print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
        return 0
    except Blocked as exc:
        print('SOURCE_EVIDENCE_BLOCKED=' + str(exc), flush=True)
    except Exception as exc:
        # Never leak authenticated backend errors, URLs, cookies or payloads.
        print('SOURCE_EVIDENCE_BLOCKED_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
