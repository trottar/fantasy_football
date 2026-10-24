"""M1b in-process six-provider sync-duration observer; no sync launcher or CLI.

Only a separately authorized caller can supply its existing real sync callable.
The observer invokes it once, binds elapsed monotonic time to the resulting
snapshot's actual bytes and provider state, and returns a sanitized receipt.
No capture, MC, ESPN transactions, calibration, or refresh authority.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from math import ceil, isfinite
from pathlib import Path
from typing import Any, Callable, Mapping
import hashlib
import json
import time

SOURCE_OWNER_BLOB = 'f3381bad44763573e1b996ab6ffb14dce65cbfc5'
PROVIDERS = ('espn', 'sleeper', 'nflverse_rosters', 'nflverse_matchups',
             'nfl_official_rosters', 'nfl_official')
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
MAX_SYNC_SECONDS = 7200
MAX_CLOCK_SKEW_SECONDS = 5
PREFIX = 'weekly_operator_m1b_sync_duration_'

class Blocked(ValueError):
    """A measurement is unverified. No receipt may be promoted."""


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Blocked(reason)


def aware(value: Any) -> datetime:
    need(isinstance(value, datetime) and value.tzinfo is not None and
         value.utcoffset() is not None, 'NAIVE_MEASUREMENT_CLOCK')
    return value.astimezone(timezone.utc)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(raw: bytes) -> str:
    clean = raw.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha1(b'blob ' + str(len(clean)).encode('ascii') + b'\0' + clean).hexdigest()


def bound_sources(root: Path) -> tuple[str, str]:
    """Source guard only; run-time identity is independently checked below."""
    own = root/'tools/operations/weekly_operator_source_evidence_owner.py'
    need(own.is_file() and not own.is_symlink() and git_blob(own.read_bytes()) == SOURCE_OWNER_BLOB,
         'PUBLISHED_OWNER_SOURCE_MISMATCH')
    import importlib.util
    spec = importlib.util.spec_from_file_location('m1b_bound_owner', own)
    need(spec is not None and spec.loader is not None, 'SOURCE_IMPORT_UNAVAILABLE')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.source_guard(root)
    return (SOURCE_OWNER_BLOB, sha(json.dumps(mod.DEPENDENCY_BLOBS, sort_keys=True).encode()))


def snapshot_identity(runtime: Path, *, week: int, expected_path: Path,
                      returned: Mapping[str, Any], started: datetime, finished: datetime) -> tuple[str,str]:
    base = (runtime/'data/season_snapshots').resolve()
    path = expected_path.resolve()
    need(path.parent.parent == base and path.name == 'snapshot.json' and
         path.is_file() and not expected_path.is_symlink(), 'SYNC_RESULT_SNAPSHOT_PATH_UNBOUND')
    need(0 < path.stat().st_size <= MAX_SNAPSHOT_BYTES, 'SNAPSHOT_SIZE_INVALID')
    raw = path.read_bytes()
    try:
        item = json.loads(raw.decode('utf-8-sig'))
    except (UnicodeError, ValueError) as exc:
        raise Blocked('SNAPSHOT_PARSE_INVALID') from exc
    need(isinstance(item, dict) and item == returned, 'SYNC_RETURN_SNAPSHOT_MISMATCH')
    espn = item.get('espn')
    need(isinstance(espn, dict) and espn.get('season') == 2026 and espn.get('week') == week,
         'SNAPSHOT_SEASON_WEEK_INVALID')
    status = item.get('source_status')
    need(isinstance(status, dict), 'PROVIDER_STATUS_MISSING')
    for provider in PROVIDERS:
        state = status.get(provider)
        healthy = (state.get('complete') if provider == 'nfl_official_rosters' and
                   isinstance(state,dict) and state.get('complete') is not None
                   else state.get('ok') if isinstance(state,dict) else None)
        need(healthy is True, 'SIX_PROVIDER_HEALTH_INCOMPLETE')
    ts = item.get('snapshot_utc')
    try:
        observed = datetime.fromisoformat(ts.replace('Z','+00:00')) if isinstance(ts,str) else None
    except ValueError:
        observed = None
    need(observed is not None and observed.tzinfo is not None, 'SNAPSHOT_TIMESTAMP_INVALID')
    observed = observed.astimezone(timezone.utc)
    need(started <= observed <= finished, 'SNAPSHOT_CHRONOLOGY_NOT_MEASURED')
    latest = base/'latest.json'
    need(latest.is_file() and not latest.is_symlink() and latest.read_bytes() == raw,
         'LATEST_SNAPSHOT_BYTES_MISMATCH')
    copies = [p for p in base.glob('*/snapshot.json') if p.is_file() and p.read_bytes() == raw]
    need(len(copies) == 1 and copies[0].resolve() == path, 'IMMUTABLE_SNAPSHOT_NOT_UNIQUE')
    return sha(raw), observed.isoformat()


def measure_authorized_sync(root: Path, *, week: int, sync_call: Callable[[],tuple],
                            buffer_seconds: int,
                            runtime_validator: Callable[[Path],Path] | None = None,
                            source_verifier: Callable[[Path],Any] | None = None,
                            clock: Callable[[],datetime] | None = None,
                            monotonic_ns: Callable[[],int] | None = None) -> dict:
    """Observe ONE call provided by an external, explicitly authorized actor.

    Has no CLI and does not import, schedule or authorize any refresh itself.
    The callback may perform I/O; never retry it when a receipt is rejected.
    Does not persist a receipt; a caller must explicitly call persist_private().
    """
    need(root.name.casefold() == 'fantasy_football', 'WRONG_CONTROL_ROOT')
    need(type(week) is int and 1 <= week <= 18, 'INVALID_WEEK')
    need(type(buffer_seconds) is int and 60 <= buffer_seconds <= 3600,
         'REFRESH_BUFFER_NOT_EXPLICIT')
    need(callable(sync_call), 'AUTHORIZED_SYNC_CALLBACK_MISSING')
    verifier = source_verifier or bound_sources
    before = verifier(root)
    if runtime_validator is None:
        import sys
        ops = str(root/'tools/operations')
        if ops not in sys.path:
            sys.path.insert(0, ops)
        from guarded_weekly_cycle import validate_root
        runtime_validator = validate_root
    runtime = runtime_validator(root)
    need(isinstance(runtime,Path) and runtime.resolve() ==
         (root/'fantasy_season_v0_36_repack1').resolve(), 'RUNTIME_IDENTITY_MISMATCH')
    utc_clock = clock or (lambda: datetime.now(timezone.utc))
    tick = monotonic_ns or time.monotonic_ns
    start_utc = aware(utc_clock())
    start_tick = tick()
    need(type(start_tick) is int and start_tick >= 0, 'MONOTONIC_START_INVALID')
    # Exactly one externally authorized sync. Exceptions propagate; no receipt.
    result = sync_call()
    end_tick = tick()
    end_utc = aware(utc_clock())
    need(type(end_tick) is int and end_tick > start_tick, 'MONOTONIC_END_INVALID')
    seconds = (end_tick-start_tick)/1_000_000_000
    wall = (end_utc-start_utc).total_seconds()
    need(isfinite(seconds) and 0 < seconds <= MAX_SYNC_SECONDS and wall >= 0 and
         abs(wall-seconds) <= MAX_CLOCK_SKEW_SECONDS, 'MEASURED_ELAPSED_CLOCK_INVALID')
    need(isinstance(result,tuple) and len(result)==2 and isinstance(result[0],Mapping)
         and isinstance(result[1],Path), 'SYNC_RESULT_SHAPE_INVALID')
    ident, stamp = snapshot_identity(runtime, week=week, expected_path=result[1],
                                     returned=result[0], started=start_utc, finished=end_utc)
    need(verifier(root) == before, 'SYNC_OBSERVER_SOURCE_CHANGED')
    # No private player/owner data, absolute paths, source URLs or secrets stored.
    return {'schema_version':1, 'source':'LOCAL_MEASURED_SIX_PROVIDER_SYNC',
            'runtime_version':'0.36','season':2026,'week':week,
            'started_at_utc':start_utc.isoformat(),'measured_at_utc':end_utc.isoformat(),
            'duration_seconds':max(1,ceil(seconds)), 'buffer_seconds':buffer_seconds,
            'snapshot_sha256':ident,'snapshot_utc':stamp,
            'source_binding':'PUBLISHED_OWNER_AND_COMMISSIONED_RUNTIME',
            'provider_count':6, 'refresh_authority':'NONE',
            'capture_authority':'NONE','action_authority':'NONE',
            'automatic_sync_or_mc':False, 'espn_writes_by_observer':False}


def persist_private(runtime: Path, measurement: Mapping[str,Any]) -> dict:
    """Explicit private, exclusive receipt creation. Never overwrite or leak data."""
    need(isinstance(measurement, Mapping), 'MEASUREMENT_MISSING')
    need(measurement.get('source') == 'LOCAL_MEASURED_SIX_PROVIDER_SYNC'
         and measurement.get('source_binding') == 'PUBLISHED_OWNER_AND_COMMISSIONED_RUNTIME'
         and measurement.get('action_authority') == 'NONE'
         and measurement.get('automatic_sync_or_mc') is False, 'RECEIPT_NOT_OBSERVED')
    identifier = measurement.get('snapshot_sha256')
    need(isinstance(identifier,str) and len(identifier)==64 and
         all(c in '0123456789abcdef' for c in identifier), 'RECEIPT_SNAPSHOT_HASH_INVALID')
    folder = runtime/'data/season_decisions'
    need(folder.is_dir() and not folder.is_symlink(), 'PRIVATE_RECEIPT_DIRECTORY_MISSING')
    target = folder/(PREFIX+identifier+'.json')
    payload = (json.dumps(dict(measurement),sort_keys=True,separators=(',',':'),
                          ensure_ascii=True)+'\n').encode('utf-8')
    try:
        with target.open('xb') as f:
            f.write(payload)
            f.flush()
            import os
            os.fsync(f.fileno())
    except FileExistsError as exc:
        raise Blocked('DUPLICATE_MEASURED_EPOCH_NO_OVERWRITE') from exc
    return {'source':'LOCAL_MEASURED_SIX_PROVIDER_SYNC',
            'runtime_version':'0.36','measured_at_utc':measurement['measured_at_utc'],
            'duration_seconds':measurement['duration_seconds'],
            'buffer_seconds':measurement['buffer_seconds'],
            'receipt_sha256':sha(payload),
            'snapshot_sha256':identifier, 'action_authority':'NONE'}


def verify_private(runtime: Path, *, snapshot_sha256: str, receipt_sha256: str,
                   now: datetime) -> dict:
    """Recheck existing private bytes before downstream *planning* consumption.

    The receipt is a local integrity record, not an external signature. A valid
    measurement neither certifies actual refresh authorization nor executes it.
    """
    def hex64(value):
        return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
    need(hex64(snapshot_sha256) and hex64(receipt_sha256), 'RECEIPT_IDENTITY_INVALID')
    now = aware(now)
    folder = runtime/'data/season_decisions'
    path = folder/(PREFIX+snapshot_sha256+'.json')
    need(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size <= 8192,
         'PRIVATE_RECEIPT_NOT_FOUND_OR_UNBOUNDED')
    raw = path.read_bytes()
    need(sha(raw) == receipt_sha256, 'PRIVATE_RECEIPT_HASH_MISMATCH')
    try:
        obj = json.loads(raw.decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise Blocked('PRIVATE_RECEIPT_JSON_INVALID') from exc
    need(isinstance(obj,dict) and obj.get('schema_version')==1
         and obj.get('source')=='LOCAL_MEASURED_SIX_PROVIDER_SYNC'
         and obj.get('runtime_version')=='0.36'
         and obj.get('source_binding')=='PUBLISHED_OWNER_AND_COMMISSIONED_RUNTIME'
         and obj.get('snapshot_sha256')==snapshot_sha256
         and type(obj.get('week')) is int and 1<=obj['week']<=18
         and obj.get('season')==2026 and obj.get('provider_count')==6
         and obj.get('refresh_authority')==obj.get('capture_authority')==
             obj.get('action_authority')=='NONE'
         and obj.get('automatic_sync_or_mc') is False
         and obj.get('espn_writes_by_observer') is False,
         'PRIVATE_RECEIPT_PROVENANCE_INVALID')
    duration = obj.get('duration_seconds');buffer = obj.get('buffer_seconds')
    need(type(duration) is int and 1<=duration<=MAX_SYNC_SECONDS
         and type(buffer) is int and 60<=buffer<=3600,
         'PRIVATE_RECEIPT_DURATION_INVALID')
    try:
        started = aware(datetime.fromisoformat(obj['started_at_utc']))
        finished = aware(datetime.fromisoformat(obj['measured_at_utc']))
    except (KeyError,ValueError,TypeError) as exc:
        raise Blocked('PRIVATE_RECEIPT_CLOCK_INVALID') from exc
    delta=(finished-started).total_seconds()
    need(0<delta<=MAX_SYNC_SECONDS and abs(duration-delta)<=MAX_CLOCK_SKEW_SECONDS+1
         and timedelta(0)<=now-finished<=timedelta(days=14),
         'PRIVATE_RECEIPT_CLOCK_STALE_OR_INCONSISTENT')
    base=runtime/'data/season_snapshots'
    matches=[p for p in base.glob('*/snapshot.json') if p.is_file() and not p.is_symlink()
             and 0<p.stat().st_size<=MAX_SNAPSHOT_BYTES and sha(p.read_bytes())==snapshot_sha256]
    need(len(matches)==1, 'MEASURED_SNAPSHOT_MISSING_OR_AMBIGUOUS')
    try:
        snap=json.loads(matches[0].read_bytes().decode('utf-8-sig'))
    except (UnicodeError,ValueError) as exc:
        raise Blocked('MEASURED_SNAPSHOT_JSON_INVALID') from exc
    need(isinstance(snap,dict) and isinstance(snap.get('espn'),dict)
         and snap['espn'].get('season')==2026 and snap['espn'].get('week')==obj['week']
         and snap.get('snapshot_utc')==obj.get('snapshot_utc'),
         'MEASURED_SNAPSHOT_PROVENANCE_MISMATCH')
    source=snap.get('source_status')
    need(isinstance(source,dict), 'MEASURED_PROVIDER_STATUS_MISSING')
    for provider in PROVIDERS:
        row=source.get(provider)
        status=(row.get('complete') if provider=='nfl_official_rosters' and
                isinstance(row,dict) and row.get('complete') is not None
                else row.get('ok') if isinstance(row,dict) else None)
        need(status is True,'MEASURED_PROVIDER_STATUS_INCOMPLETE')
    return {'source':'LOCAL_MEASURED_SIX_PROVIDER_SYNC',
            'runtime_version':'0.36','measured_at_utc':obj['measured_at_utc'],
            'duration_seconds':duration,'buffer_seconds':buffer,
            'receipt_sha256':receipt_sha256, 'snapshot_sha256':snapshot_sha256,
            'action_authority':'NONE'}
