"""Week 8 B2b4d: optional live ESPN transaction-source *coverage* probe.

A single authenticated read uses the commissioned ESPN league reader's existing
mTransactions2 view. No events become certified processing times, no inference
from proposedDate/processDate, no cutoff/action-screen claims, no persistence.
Only sanitized aggregate shape/capability metadata may reach stdout.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

CONTRACT = 'WEEK8_B2B4D_LIVE_TRANSACTION_SOURCE_SHAPE_V1'
DEPENDENCY_BLOBS = {
    'tools/operations/action_joint_event_evidence_b2b4c.py': '4a2659d3ce6332773c3dc7170ba3ce376b6c92b3',
    'src/data_sources/espn_league.py': '081cacdc913529497bf0070aa7845a27da7f388b',
    'tools/operations/weekly_operator_source_evidence_owner.py': 'f3381bad44763573e1b996ab6ffb14dce65cbfc5',
}
MAX_FROZEN_BYTES = 32 * 1024 * 1024
MAX_RESPONSE_SECONDS = 60
MAX_TRANSACTIONS = 10000
ALLOWED_VIEWS = ('mSettings', 'mTeam', 'mTransactions2')


class Blocked(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Blocked(reason)


def aware(value: Any) -> datetime:
    if isinstance(value, datetime):
        timestamp = value
    elif isinstance(value, str):
        try:
            timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, OverflowError) as exc:
            raise Blocked('OBSERVATION_CLOCK_INVALID') from exc
    else:
        raise Blocked('OBSERVATION_CLOCK_INVALID')
    need(timestamp.tzinfo is not None and timestamp.utcoffset() is not None,
         'OBSERVATION_CLOCK_NAIVE')
    return timestamp.astimezone(timezone.utc)


def git_blob(data: bytes) -> str:
    raw = data.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def source_guard(root: Path) -> None:
    for rel, expected in DEPENDENCY_BLOBS.items():
        target = root / rel
        need(target.is_file() and not target.is_symlink(), 'SOURCE_DEPENDENCY_MISSING')
        need(git_blob(target.read_bytes()) == expected, 'SOURCE_DEPENDENCY_DRIFT')


def frozen_snapshot(runtime: Path, week: int) -> tuple[dict, str]:
    base = runtime / 'data/season_snapshots'
    path = base / 'latest.json'
    need(path.is_file() and not path.is_symlink(), 'FROZEN_LATEST_MISSING')
    need(0 < path.stat().st_size <= MAX_FROZEN_BYTES, 'FROZEN_SNAPSHOT_SIZE_INVALID')
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode('utf-8-sig'))
    except (ValueError, UnicodeError) as exc:
        raise Blocked('FROZEN_SNAPSHOT_JSON_INVALID') from exc
    need(type(data) is dict and type(data.get('espn')) is dict and
         data['espn'].get('season') == 2026 and data['espn'].get('week') == week and
         type(data['espn'].get('league_id')) is int,
         'FROZEN_EPOCH_OR_LEAGUE_INVALID')
    matches = 0
    for candidate in base.glob('*/snapshot.json'):
        if (candidate.is_file() and not candidate.is_symlink() and
                candidate.stat().st_size == len(raw) and candidate.read_bytes() == raw):
            matches += 1
    need(matches == 1, 'IMMUTABLE_FROZEN_COPY_NOT_UNIQUE')
    return data, hashlib.sha256(raw).hexdigest()


def summarize(*, frozen: dict, raw: dict, started: datetime, ended: datetime,
              now: datetime, week: int) -> dict:
    """Pure shape comparison: even a successful authenticated GET is not an event certificate."""
    started, ended, now = aware(started), aware(ended), aware(now)
    need(timedelta(0) <= ended-started <= timedelta(seconds=MAX_RESPONSE_SECONDS),
         'AUTHENTICATED_READ_DURATION_INVALID')
    need(timedelta(0) <= now-ended <= timedelta(seconds=MAX_RESPONSE_SECONDS),
         'AUTHENTICATED_READ_FRESHNESS_INVALID')
    need(type(week) is int and 1 <= week <= 18 and type(frozen) is dict and
         type(frozen.get('espn')) is dict, 'FROZEN_INPUT_SHAPE_INVALID')
    fe = frozen['espn']
    need(fe.get('season') == 2026 and fe.get('week') == week and
         type(fe.get('league_id')) is int, 'FROZEN_EPOCH_INVALID')
    frozen_at = aware(frozen.get('snapshot_utc'))
    need(frozen_at <= started, 'FROZEN_SNAPSHOT_AFTER_AUTHENTICATED_READ')
    need(type(raw) is dict and type(raw.get('id')) is int and
         raw['id'] == fe['league_id'] and
         raw.get('seasonId', 2026) == 2026 and
         raw.get('scoringPeriodId', week) == week,
         'PRIVATE_ESPN_RESPONSE_EPOCH_MISMATCH')
    # The request includes mTransactions2, but ESPN may omit the response's
    # transactions key, cap history, or return incomplete/ambiguous dates.
    txs = raw.get('transactions')
    if txs is None:
        shape = 'MTRANSACTIONS2_ROWS_ABSENT_NO_EVENT_COVERAGE'
        txs = []
    else:
        need(type(txs) is list and len(txs) <= MAX_TRANSACTIONS,
             'MTRANSACTIONS2_ROWS_INVALID_OR_UNBOUNDED')
        shape = ('MTRANSACTIONS2_ROWS_PRESENT_COMPLETENESS_UNKNOWN'
                 if txs else 'MTRANSACTIONS2_EMPTY_COMPLETENESS_UNKNOWN')
    ids = set()
    proposed_count = processed_count = items_count = unknown_items = 0
    for row in txs:
        need(type(row) is dict and type(row.get('id')) is int and
             row['id'] not in ids, 'TRANSACTION_ID_SHAPE_OR_DUPLICATE')
        ids.add(row['id'])
        for key in ('proposedDate', 'processDate'):
            field = row.get(key)
            if field is None:
                continue
            need(type(field) is int and 946684800000 <= field < 4102444800000,
                 'TRANSACTION_REPORTED_TIME_SHAPE_INVALID')
            if key == 'proposedDate':
                proposed_count += 1
            else:
                processed_count += 1
        items = row.get('items')
        if items is None:
            unknown_items += 1
        else:
            need(type(items) is list and len(items) <= 128 and
                 all(type(i) is dict for i in items), 'TRANSACTION_ITEM_SHAPE_INVALID')
            items_count += len(items)
    settings = raw.get('settings')
    trade = settings.get('tradeSettings') if type(settings) is dict else None
    acq = settings.get('acquisitionSettings') if type(settings) is dict else None
    trade = trade if type(trade) is dict else {}
    acq = acq if type(acq) is dict else {}
    # Aggregate counts are allowed. No private IDs, raw rows, opaque hashes,
    # timestamps from ESPN, exact setting values or action text are emitted.
    return {
        'contract': CONTRACT, 'season': 2026, 'week': week,
        'source': 'ONE_DIRECT_AUTHENTICATED_PRIVATE_ESPN_LEAGUE_GET',
        'requested_views': list(ALLOWED_VIEWS), 'source_read_fresh': True,
        'source_epoch_identity': 'MATCHED_FROZEN_LEAGUE_AND_WEEK',
        'transaction_shape': shape, 'transactions_count': len(txs),
        'reported_proposed_dates_count': proposed_count,
        'reported_process_dates_count': processed_count,
        'item_records_count': items_count, 'transactions_missing_items_count': unknown_items,
        'trade_settings_shape_present': bool(trade),
        'acquisition_settings_shape_present': bool(acq),
        'trade_deadline_field_present': 'deadlineDate' in trade,
        'review_hours_field_present': 'revisionHours' in trade,
        'waiver_hour_field_present': 'waiverProcessHour' in acq,
        'source_completeness_attested': False,
        'reported_process_date_is_verified_effective_time': False,
        'claim_cutoff_verified': False, 'trade_cutoff_verified': False,
        'released_asset_market_status_verified': False,
        'b2b4c_event_envelope_produced': False,
        'downstream_reacquisition_probability': 'UNKNOWN',
        'status': 'BLOCKED_B2B4D_SOURCE_SHAPES_ONLY',
        'action_authority': 'NONE', 'refresh_authority': 'NONE',
        'capture_authority': 'NONE', 'native_mc_started': False,
        'espn_gets': 1, 'espn_writes': False, 'persistent_evidence_writes': False,
    }


def probe(root: Path, week: int, *, runtime_validator: Callable | None = None,
          fetcher: Callable | None = None, secret_loader: Callable | None = None,
          clock: Callable[[], datetime] | None = None) -> dict:
    need(root.name.casefold() == 'fantasy_football', 'WRONG_CONTROL_ROOT')
    need(type(week) is int and 1 <= week <= 18, 'WEEK_INVALID')
    source_guard(root)
    if runtime_validator is None:
        from guarded_weekly_cycle import validate_root
        runtime_validator = validate_root
    runtime = runtime_validator(root)
    need(isinstance(runtime, Path) and runtime.resolve() ==
         (root/'fantasy_season_v0_36_repack1').resolve(),
         'COMMISSIONED_RUNTIME_IDENTITY_INVALID')
    frozen, initial_hash = frozen_snapshot(runtime, week)
    if fetcher is None or secret_loader is None:
        # Only the commissioned runtime may supply the network-capable client.
        if str(runtime) not in sys.path:
            sys.path.insert(0, str(runtime))
        from src.data_sources import espn_league as reader
        from src.data_sources import secrets as secrets_module
        for mod in (reader, secrets_module):
            need(Path(mod.__file__).resolve().is_relative_to(runtime.resolve()),
                 'UNVERIFIED_ESPN_IMPORT_ROOT')
        if fetcher is None:
            fetcher = reader.fetch_private_league
        if secret_loader is None:
            secret_loader = secrets_module.load_espn_secrets
    candidates = [p for p in (root/'config/secrets.json',runtime/'config/secrets.json')
                  if p.is_file() and not p.is_symlink()]
    need(bool(candidates), 'PRIVATE_ESPN_CREDENTIAL_FILE_MISSING')
    sec = secret_loader(candidates[0])
    need(sec.season == 2026 and sec.league_id == frozen['espn']['league_id'],
         'PRIVATE_ESPN_CREDENTIAL_LEAGUE_MISMATCH')
    clock = clock or (lambda: datetime.now(timezone.utc))
    started = aware(clock())
    raw = fetcher(sec, scoring_period_id=week, views=ALLOWED_VIEWS, timeout=45)
    ended = aware(clock())
    result = summarize(frozen=frozen, raw=raw, started=started, ended=ended,
                       now=ended, week=week)
    _, afterward_hash = frozen_snapshot(runtime, week)
    need(afterward_hash == initial_hash, 'FROZEN_SNAPSHOT_MUTATED_DURING_PROBE')
    source_guard(root)
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, default='.')
    p.add_argument('--week', type=int, required=True)
    args = p.parse_args(argv)
    print('B2B4D AUTHENTICATED ESPN TRANSACTION SHAPE SOURCE PROBE READONLY', flush=True)
    try:
        result = probe(args.project_root.resolve(), args.week)
        print('B2B4D_RESULT=' + json.dumps(result, sort_keys=True, separators=(',', ':')), flush=True)
        print('NO_SYNC_CAPTURE_MC_OR_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
        return 0
    except Blocked as exc:
        print('B2B4D_BLOCKED=' + str(exc), flush=True)
    except Exception as exc:
        # Untrusted backend/credential exceptions may contain sensitive payloads.
        print('B2B4D_BLOCKED_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    print('NO_SYNC_CAPTURE_MC_OR_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
