"""Week 8 v2 weekly workflow integration candidate, source-only until commissioned.

ONE guarded entrypoint for week selection, immutable refresh/capture, published
M1a MC, read-only live review, and a single private report. The installer never
runs this program. Transactions, scheduler installation, speculative cutoffs,
and positive transaction certificates are outside this source checkpoint.

Mode 'status' performs a no-network, no-write routing calculation. Mode 'run'
is opt-in and uses the commissioned runtime only after exact source validation.
The control plane MUST NOT be scheduled until separately commissioned.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

CONTRACT = 'WEEK8_INTEGRATED_OPERATOR_V2_SOURCE_CANDIDATE_V1'
PHASE_CONTRACT = 'WEEK8_V2_PHASE_BOUND_RECEIPT_V1'
MAX_PHASE_AGE = timedelta(hours=2)
FIRST_MONDAY = date(2026, 9, 7)
MIN_LEAD = timedelta(minutes=80)
PHASES = ('CALENDAR', 'SYNC', 'CAPTURE', 'MC', 'REVIEW', 'REPORT')
NATIVE_RUNTIME = 'fantasy_season_v0_36_repack1'
MAX_PRIVATE_REPORT_BYTES = 1024 * 1024


class Blocked(ValueError):
    pass


def require(ok: bool, why: str) -> None:
    if not ok:
        raise Blocked(why)


def eastern(now: datetime) -> datetime:
    """2026 fantasy season EDT/EST without depending on Windows tzdata."""
    require(isinstance(now, datetime) and now.tzinfo is not None, 'CLOCK_NOT_AWARE')
    utc = now.astimezone(timezone.utc)
    # 2026 DST ends 2026-11-01 06:00 UTC; the season ends in Jan 2027.
    off = -5 if utc >= datetime(2026, 11, 1, 6, tzinfo=timezone.utc) else -4
    return utc.astimezone(timezone(timedelta(hours=off)))


def selected_week(now: datetime) -> int:
    """Week starts Monday for work scheduling, NOT at previous Sunday's game."""
    require(isinstance(now, datetime) and now.tzinfo is not None, 'CLOCK_NOT_AWARE')
    local = eastern(now).date()
    week = (local - FIRST_MONDAY).days // 7 + 1
    require(1 <= week <= 18, 'OUTSIDE_2026_FANTASY_CALENDAR')
    return week


def planned_slot(now: datetime, week: int) -> str:
    require(selected_week(now) == week, 'CALENDAR_WEEK_DISAGREEMENT')
    weekday = eastern(now).weekday()
    # Mon reference, Tue pre-waiver, Wed primary, Sat second. Other days are
    # passive review only; triggers must not invent a claim cutoff.
    return {0: 'MON', 1: 'TUE', 2: 'WED', 5: 'SAT'}.get(weekday, 'PASSIVE')


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), 'EVIDENCE_FILE_MISSING')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonfile(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 32 * 1024 * 1024,
            'EVIDENCE_FILE_INVALID')
    obj = json.loads(path.read_text(encoding='utf-8-sig'))
    require(isinstance(obj, dict), 'EVIDENCE_OBJECT_INVALID')
    return obj


def snapshot_identity(runtime: Path, week: int, *, now: datetime) -> dict:
    base = runtime / 'data/season_snapshots'
    latest = base / 'latest.json'
    obj = jsonfile(latest)
    require((obj.get('espn') or {}).get('season') == 2026 and
            (obj.get('espn') or {}).get('week') == week, 'FRESH_SNAPSHOT_WRONG_WEEK')
    when = datetime.fromisoformat(str(obj.get('snapshot_utc')).replace('Z', '+00:00'))
    require(when.tzinfo is not None and when <= now.astimezone(timezone.utc),
            'FRESH_SNAPSHOT_TIME_INVALID')
    sha = digest(latest)
    same = [p for p in base.glob('*/snapshot.json') if p.is_file() and not p.is_symlink()
            and p.stat().st_size == latest.stat().st_size and digest(p) == sha]
    require(len(same) == 1, 'FRESH_SNAPSHOT_IMMUTABLE_COPY_NOT_UNIQUE')
    for provider in ('espn', 'sleeper', 'nflverse_rosters', 'nflverse_matchups',
                     'nfl_official_rosters', 'nfl_official'):
        status = (obj.get('source_status') or {}).get(provider)
        field = ('complete' if provider == 'nfl_official_rosters'
                 and isinstance(status, dict) and status.get('complete') is not None else 'ok')
        require(isinstance(status, dict) and status.get(field) is True,
                'FRESH_PROVIDER_UNHEALTHY_' + provider.upper())
    return {'sha256': sha, 'timestamp': obj['snapshot_utc'], 'week': week}


def capture_identity(runtime: Path, snapshot: dict, week: int) -> dict:
    folder = runtime / 'data/season_predictions/closure'
    entries = []
    for p in folder.glob(f'pregame_2026_w{week:02d}_*.json'):
        if not p.is_file() or p.is_symlink():
            continue
        cap = jsonfile(p)
        if cap.get('snapshot_utc') == snapshot['timestamp']:
            entries.append((p, cap))
    require(len(entries) == 1, 'CAPTURE_MISSING_OR_AMBIGUOUS_FOR_SNAPSHOT')
    p,cap = entries[0]
    require(cap.get('measurement_contract') == 'A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
            'CAPTURE_NOT_PROSPECTIVE')
    require(cap.get('season') == 2026 and cap.get('week') == week,
            'CAPTURE_EPOCH_MISMATCH')
    captured = datetime.fromisoformat(cap['captured_utc'].replace('Z', '+00:00'))
    require(captured.tzinfo is not None and captured >=
            datetime.fromisoformat(snapshot['timestamp']), 'CAPTURE_CHRONOLOGY_INVALID')
    return {'sha256': digest(p), 'path': p.relative_to(runtime).as_posix(),
            'captured_utc': captured.isoformat()}


def atomic_private_json(path: Path, data: dict) -> None:
    """Only under commissioned runtime's private decision directory."""
    raw = (json.dumps(data, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':')) + '\n').encode('utf-8')
    require(len(raw) <= MAX_PRIVATE_REPORT_BYTES, 'PRIVATE_RECEIPT_SIZE_INVALID')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())



def phase_path(folder: Path, slot_id: str, phase: str, kind: str) -> Path:
    require(phase in ('SYNC', 'CAPTURE', 'MC') and kind in ('start', 'done'),
            'PHASE_RECEIPT_NAME_INVALID')
    return folder / (slot_id + '.' + phase.lower() + '.' + kind + '.json')


def phase_begin(folder: Path, slot_id: str, phase: str, *,
                launch_sha256: str, dependencies: dict, source_sha256: str) -> tuple[Path, bool]:
    """A create-only intent is durable BEFORE starting an expensive operation."""
    path = phase_path(folder, slot_id, phase, 'start')
    expected = {'contract': PHASE_CONTRACT, 'phase': phase,
                'launch_sha256': launch_sha256, 'dependencies': dependencies,
                'source_sha256': source_sha256}
    if path.exists():
        require(jsonfile(path) == expected, 'PHASE_BEGIN_IDENTITY_CHANGED_' + phase)
        return path, False
    atomic_private_json(path, expected)
    return path, True


def phase_complete(folder: Path, slot_id: str, phase: str,
                   *, begin: Path, facts: dict) -> dict:
    """The output can be reused only with its matching verified intent."""
    path = phase_path(folder, slot_id, phase, 'done')
    expected = {'contract': PHASE_CONTRACT, 'phase': phase,
                'begin_sha256': digest(begin), 'facts': facts}
    if path.exists():
        require(jsonfile(path) == expected, 'PHASE_RESULT_IDENTITY_CHANGED_' + phase)
    else:
        atomic_private_json(path, expected)
    return expected


def prior_phase(folder: Path, slot_id: str, phase: str,
                *, begin: Path, live_facts: dict) -> bool:
    """Refuse an uncertain started-but-not-completed phase; no retry by guess."""
    path = phase_path(folder, slot_id, phase, 'done')
    if not path.exists():
        raise Blocked('PHASE_OUTCOME_UNCERTAIN_' + phase)
    phase_complete(folder, slot_id, phase, begin=begin, facts=live_facts)
    return True


def snapshot_reuse(runtime: Path, week: int, *, now: datetime) -> dict:
    actual = snapshot_identity(runtime, week, now=now)
    stamp = datetime.fromisoformat(str(actual['timestamp']).replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and timedelta(0) <= now - stamp <= MAX_PHASE_AGE,
            'SAVED_SYNC_TOO_OLD_FOR_PROSPECTIVE_CAPTURE')
    return actual


def capture_reuse(runtime: Path, snapshot: dict, week: int,
                  *, now: datetime) -> dict:
    actual = capture_identity(runtime, snapshot, week)
    created = datetime.fromisoformat(str(actual['captured_utc']).replace('Z', '+00:00'))
    require(created.tzinfo is not None and timedelta(0) <= now - created <= MAX_PHASE_AGE,
            'SAVED_CAPTURE_TOO_OLD_FOR_NATIVE_MC')
    # The published M1a controller independently verifies integrity, firewall,
    # commissioning identity and source dependencies before launching native MC.
    return actual


def write_verified_mc_evidence(root: Path, runtime: Path, *, now: datetime, slot_id: str) -> dict:
    """Re-attest the already commissioned v0.36 runtime and strict memory state.

    These are FRESH INPUT RECEIPTS for M1a, not v2 commissioning or action
    approval. Never trust a previous Boolean in place of validating live bytes.
    """
    require(now.tzinfo is not None, 'HEALTH_CLOCK_NOT_AWARE')
    import guarded_weekly_cycle as guarded
    require(Path(guarded.__file__).resolve() ==
            (root/'tools/operations/guarded_weekly_cycle.py').resolve(),
            'HEALTH_GUARD_SOURCE_ORIGIN_INVALID')
    require(guarded.validate_root(root).resolve() == runtime.resolve(),
            'HEALTH_RUNTIME_SOURCE_DRIFT')
    deps = {}
    for key, rel in guarded.DEPENDENCIES.items():
        file = runtime/rel
        require(file.is_file() and not file.is_symlink(),
                'HEALTH_DEPENDENCY_MISSING_' + key.upper())
        deps[key] = digest(file)
    try:
        checked = subprocess.run(
            [sys.executable, '-B', str(root/'tools/check_memory_health.py'),
             '--root', str(root), '--strict', '--json'],
            cwd=str(root), capture_output=True, text=True, timeout=120, check=False)
        require(checked.returncode == 0, 'HEALTH_STRICT_MEMORY_COMMAND_FAILED')
        health = json.loads(checked.stdout)
        require(isinstance(health, dict) and health.get('healthy') is True and
                not health.get('issues'), 'HEALTH_STRICT_MEMORY_RESULT_BLOCKED')
    except Blocked:
        raise
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
        raise Blocked('HEALTH_STRICT_MEMORY_EXCEPTION_' + type(exc).__name__) from None
    stamp = datetime.now(timezone.utc)
    require(stamp >= now.astimezone(timezone.utc) - timedelta(minutes=60),
            'HEALTH_CLOCK_DRIFT')
    timecode = stamp.strftime('%Y%m%dT%H%M%S%fZ')
    out = runtime/'data/season_decisions'
    runtime_receipt = {
        'contract':'WEEK8_V2_FRESH_M1A_RUNTIME_EVIDENCE_V1',
        'commissioned':True,
        'source_checkpoint': guarded.EXPECTED_SOURCE_CHECKPOINT,
        'runtime_version':guarded.EXPECTED_VERSION,
        'dependencies':deps,
        'verified_utc':stamp.isoformat(),
        'operator_v2_commissioned':False,
        'action_authority':'NONE',
    }
    memory_receipt = {
        'contract':'WEEK8_V2_FRESH_M1A_MEMORY_EVIDENCE_V1',
        # Native Gate A joins strict-memory proof to the same commissioned
        # v0.36 source checkpoint as its runtime-identity receipt. Omitting
        # this key manufactures a BLOCKED_HEALTH native receipt despite a
        # successful independent strict-memory check.
        'source_checkpoint':guarded.EXPECTED_SOURCE_CHECKPOINT,
        'status':'PASS','strict':True,'checked_utc':stamp.isoformat(),
        'operator_v2_commissioned':False,'action_authority':'NONE',
    }
    identity_path = out/(slot_id+'_'+timecode+'_commissioned_identity.json')
    memory_path = out/(slot_id+'_'+timecode+'_memory_health.json')
    atomic_private_json(identity_path, runtime_receipt)
    atomic_private_json(memory_path, memory_receipt)
    # Read back both create-only files before allowing M1a to discover them.
    require(jsonfile(identity_path) == runtime_receipt and
            jsonfile(memory_path) == memory_receipt,
            'FRESH_M1A_EVIDENCE_READBACK_FAILED')
    return {'runtime_identity_sha256':digest(identity_path),
            'memory_health_sha256':digest(memory_path),
            'runtime_commissioned':True, 'operator_v2_commissioned':False}


def public_lock_preflight(*, now: datetime, week: int, scoreboard: dict) -> dict:
    """No past game may be falsely treated as a full-week prospective freeze."""
    import weekly_operator_calendar_evidence as calendar
    games = calendar.independent_schedule(scoreboard, season=2026, week=week)
    all_times = [game[1] for game in games.values()]
    require(bool(all_times), 'PUBLIC_NFL_CALENDAR_EMPTY')
    # Saturday is deliberately after a Thursday lock. Exclude those outcomes;
    # never mislabel the *whole* scoring week as prospectively frozen.
    future = [kick for kick in all_times if kick > now]
    require(bool(future), 'NO_REMAINING_FUTURE_NFL_GAME')
    earliest = min(future)
    require(earliest - now >= MIN_LEAD, 'NEXT_GAME_PROSPECTIVE_LEAD_MISSING')
    return {'earliest_future_nfl_lock_utc': earliest.isoformat(),
            'lead_minutes': int((earliest - now).total_seconds() // 60),
            'week': week, 'already_elapsed_game_records': len(all_times)-len(future),
            'prospective_scope': 'FUTURE_GAMES_ONLY_NOT_RETROSPECTIVE_BACKFILL'}


def run_native_cli(runtime: Path, *args: str, timeout: int = 3600,
                   launcher: Callable | None = None) -> None:
    run = launcher or subprocess.run
    # Do not forward native stdout/stderr: private league/player details may be
    # included. Fail with fixed classification, never an exception message.
    try:
        result = run([sys.executable, '-B', 'fantasy.py', *args], cwd=str(runtime),
                     capture_output=True, text=True, timeout=timeout, check=False)
    except Exception as exc:
        raise Blocked('NATIVE_STAGE_EXCEPTION_' + type(exc).__name__) from None
    require(result.returncode == 0, 'NATIVE_STAGE_FAILED_' + args[0])


def preflight(root: Path, now: datetime, week: int) -> Path:
    require(root.name.casefold() == 'fantasy_football', 'CONTROL_ROOT_WRONG')
    ops = root / 'tools/operations'
    if str(ops) not in sys.path:
        sys.path.insert(0, str(ops))
    from guarded_weekly_cycle import validate_root
    runtime = validate_root(root)
    require(runtime.resolve() == (root / NATIVE_RUNTIME).resolve(),
            'COMMISSIONED_RUNTIME_MISMATCH')
    cp = subprocess.run([sys.executable, '-B', str(root/'tools/check_memory_health.py'),
                         '--root', str(root), '--strict', '--json'],
                        capture_output=True, text=True, timeout=120, check=False)
    require(cp.returncode == 0, 'STRICT_MEMORY_HEALTH_BLOCKED')
    health = json.loads(cp.stdout)
    require(health.get('healthy') is True and not health.get('issues'),
            'STRICT_MEMORY_UNHEALTHY')
    require(selected_week(now) == week, 'REQUESTED_WEEK_MISMATCH')
    return runtime


def safe_report(root: Path, runtime: Path, *, week: int, slot: str,
                state: str, stages: list[str], blocker: str | None,
                observation_utc: str, queue: Any = None,
                commissioning_trial: bool = False) -> dict:
    """Reports remain private even when the outcome is incomplete or blocked."""
    allowed = {'SCOPED_READY', 'CAPTURE_REQUIRED', 'BLOCKED_SOURCE',
               'BLOCKED_HEALTH', 'INCOMPLETE_COVERAGE'}
    require(state in allowed, 'UNRECOGNIZED_REPORT_STATE')
    return {'contract': CONTRACT, 'season': 2026, 'week': week, 'slot': slot,
            'created_utc': observation_utc, 'operator_state': state,
            'completed_phases': stages, 'blocker': blocker,
            'recommendation_certified': False, 'transaction_authority': 'NONE',
            'espn_writes': False,
            'commissioning_trial': commissioning_trial,
            'queue': queue if isinstance(queue, list) else [],
            'next_step': ('REVIEW_PRIVATE_REPORT' if state == 'SCOPED_READY' else
                          'RESOLVE_EXPLICIT_BLOCKER_NO_ESPN_SUBMISSION')}


def execute(root: Path, *, now: datetime, week: int | None = None,
            scoreboard_fetch: Callable | None = None,
            native_launcher: Callable | None = None,
            controller: Any = None, commissioning_trial: bool = False) -> dict:
    week = selected_week(now) if week is None else week
    slot = planned_slot(now, week)
    require(slot in ('MON', 'TUE', 'WED', 'SAT'), 'NOT_A_PROTECTED_OPERATION_SLOT')
    runtime = preflight(root, now, week)
    commissioning = runtime / 'data/season_decisions/weekly_operator_v2_commissioning.json'
    source_sha = digest(Path(__file__))
    if not commissioning_trial:
        require(commissioning.is_file(), 'V2_WORKFLOW_NOT_COMMISSIONED')
        activated = jsonfile(commissioning)
        require(activated.get('contract') == CONTRACT and activated.get('commissioned') is True
                and activated.get('operator_source_sha256') == source_sha
                and activated.get('runtime_version') == '0.36', 'V2_ACTIVATION_IDENTITY_INVALID')
    # Trial is an explicit, supervised real-read acceptance attempt. It NEVER
    # creates the permanent v2 commissioning receipt or enables scheduling.
    ops = root / 'tools/operations'
    if str(ops) not in sys.path:
        sys.path.insert(0, str(ops))
    import weekly_operator_calendar_evidence as calendar
    observations = runtime / 'data/season_decisions'
    standard_slot = f'operator_v2_2026_w{week:02d}_{slot}_{eastern(now).date():%Y%m%d}'
    trial_slot = standard_slot.replace('operator_v2_', 'operator_v2_trial_', 1)
    if not commissioning_trial:
        require(not (observations/(trial_slot+'.launch.json')).exists(),
                'TRIAL_SLOT_EXISTS_NO_PRODUCTION_DOUBLE_RUN')
    slot_id = trial_slot if commissioning_trial else standard_slot
    marker = observations / (slot_id + '.launch.json')
    report_file = observations / (slot_id + '.report.json')
    if report_file.exists():
        prior = jsonfile(report_file)
        require(prior.get('contract') == CONTRACT and prior.get('week') == week and
                prior.get('slot') == slot and prior.get('operator_state') in
                ('INCOMPLETE_COVERAGE', 'SCOPED_READY', 'BLOCKED_HEALTH',
                 'BLOCKED_SOURCE', 'CAPTURE_REQUIRED'),
                'EXISTING_REPORT_IDENTITY_DRIFT')
        return prior
    controller = controller or __import__('weekly_operator_controller')
    done: list[str] = []
    blocker: str | None = None
    queue: list = []
    status = 'BLOCKED_HEALTH'
    expected_launch = {'contract': CONTRACT, 'week': week, 'slot': slot,
                       'source_sha256': source_sha, 'no_automatic_repeat': True,
                       'commissioning_trial': commissioning_trial}
    if marker.exists():
        first = jsonfile(marker)
        require(all(first.get(k) == v for k,v in expected_launch.items()),
                'EXISTING_LAUNCH_IDENTITY_DRIFT')
        started = datetime.fromisoformat(str(first.get('started_utc')).replace('Z','+00:00'))
        require(started.tzinfo is not None and timedelta(0) <= now - started <= MAX_PHASE_AGE,
                'SAVED_LAUNCH_TOO_OLD_FOR_RESUME')
    else:
        atomic_private_json(marker, {**expected_launch,
            'started_utc': now.astimezone(timezone.utc).isoformat()})
    launch_sha = digest(marker)
    try:
        # A public GET and current calendar checks are cheap and repeated on
        # resume: a previously future kickoff may have become elapsed.
        board = scoreboard_fetch() if scoreboard_fetch else calendar.public_scoreboard(
            season=2026, week=week)[0]
        public_lock_preflight(now=now, week=week, scoreboard=board)
        done.append('CALENDAR')

        sync_start, fresh = phase_begin(observations, slot_id, 'SYNC',
                launch_sha256=launch_sha, dependencies={'week': week}, source_sha256=source_sha)
        if fresh:
            run_native_cli(runtime, 'season-sync', '--week', str(week), timeout=1200,
                           launcher=native_launcher)
            snap = snapshot_identity(runtime, week, now=datetime.now(timezone.utc))
            phase_complete(observations, slot_id, 'SYNC', begin=sync_start, facts=snap)
        else:
            # If native sync started but its receipt was not durably committed,
            # the side effect is uncertain. Never issue another six-provider sync.
            sync_done = phase_path(observations, slot_id, 'SYNC', 'done')
            require(sync_done.exists(), 'PHASE_OUTCOME_UNCERTAIN_SYNC')
            snap = snapshot_reuse(runtime, week, now=now)
            prior_phase(observations,slot_id,'SYNC',begin=sync_start,live_facts=snap)
        done.append('SYNC')

        capture_start, fresh = phase_begin(observations, slot_id, 'CAPTURE',
                launch_sha256=launch_sha, dependencies={'week':week,'snapshot':snap},
                source_sha256=source_sha)
        if fresh:
            run_native_cli(runtime,'closure-capture','--snapshot',
                           'data/season_snapshots/latest.json',
                           timeout=600,launcher=native_launcher)
            cap = capture_identity(runtime,snap,week)
            phase_complete(observations, slot_id, 'CAPTURE', begin=capture_start, facts=cap)
        else:
            # An incomplete capture is NOT reconstructed after the fact.
            capture_done = phase_path(observations, slot_id, 'CAPTURE', 'done')
            require(capture_done.exists(), 'PHASE_OUTCOME_UNCERTAIN_CAPTURE')
            cap = capture_reuse(runtime,snap,week,now=now)
            prior_phase(observations,slot_id,'CAPTURE',begin=capture_start,live_facts=cap)
        done.append('CAPTURE')

        # M1a needs freshly verified identities; producing them here removes a
        # weekly manual operator dependency without commissioning v2 by fiat.
        write_verified_mc_evidence(root, runtime, now=datetime.now(timezone.utc),
                                   slot_id=slot_id)
        mc_start, _ = phase_begin(observations, slot_id, 'MC',
                launch_sha256=launch_sha,
                dependencies={'snapshot_sha256':snap['sha256'],
                              'capture_sha256':cap['sha256']},
                source_sha256=source_sha)
        # M1a has independent launch-before-execute / exact-receipt guards. An
        # interruption here may resume review or reuse committed MC; an uncertain
        # launch without a receipt remains blocked by M1a, never rerun blindly.
        plan = controller.run(root,now=datetime.now(timezone.utc),week=week,mode='resume-mc')
        require(plan.get('phase') == 'READONLY_DECISION_REVIEW',
                'GUARDED_MC_INCOMPLETE_' + str(plan.get('phase')))
        require(plan.get('authority') == 'NONE', 'REVIEW_ESCALATED_AUTHORITY')
        receipt_sha = ((plan.get('planner') or {}).get('receipt_sha256') or
                       plan.get('receipt_sha256'))
        require(isinstance(receipt_sha,str) and len(receipt_sha)==64 and
                all(c in '0123456789abcdef' for c in receipt_sha),
                'NATIVE_MC_RECEIPT_IDENTITY_MISSING')
        # Freeze the identity of the MC output, not the ephemeral live review.
        phase_complete(observations, slot_id, 'MC', begin=mc_start,
                       facts={'snapshot_sha256':snap['sha256'],
                              'capture_sha256':cap['sha256'],
                              'receipt_sha256':receipt_sha})
        done.append('MC')
        queue = plan.get('queue') if isinstance(plan.get('queue'), list) else []
        done.append('REVIEW')
        status = 'INCOMPLETE_COVERAGE'
        blocker = 'FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED'
    except Blocked as exc:
        blocker = str(exc)
        status = ('CAPTURE_REQUIRED' if 'CAPTURE' in blocker else
                  'BLOCKED_SOURCE' if 'SOURCE' in blocker or 'PROVIDER' in blocker else
                  'BLOCKED_HEALTH')
    except Exception as exc:
        blocker = 'STAGE_EXCEPTION_' + type(exc).__name__
        status = 'BLOCKED_HEALTH'
    report = safe_report(root,runtime,week=week,slot=slot,state=status,stages=done,
                         blocker=blocker,queue=queue,
                         observation_utc=datetime.now(timezone.utc).isoformat(),
                         commissioning_trial=commissioning_trial)
    atomic_private_json(report_file,report)
    return report

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',type=Path,default=Path('.'))
    ap.add_argument('--week',type=int)
    ap.add_argument('--mode',choices=('status','trial','run'),default='status')
    ap.add_argument('--ack-live-readonly',action='store_true')
    args = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    print('WEEK8 V2 INTEGRATED WEEKLY OPERATOR SOURCE CANDIDATE',flush=True)
    try:
        wk = selected_week(now) if args.week is None else args.week
        if args.mode == 'status':
            print('OPERATOR_STATUS='+json.dumps({'week':wk,'slot':planned_slot(now,wk),
                 'mode':'SOURCE_ONLY_STATUS','production_commissioned':False,
                 'espn_writes':False,'transaction_authority':'NONE'},sort_keys=True),flush=True)
            return 0
        require(args.mode != 'trial' or args.ack_live_readonly,
                'EXPLICIT_LIVE_TRIAL_ACK_REQUIRED')
        require(args.mode != 'run' or not args.ack_live_readonly,
                'LIVE_TRIAL_ACK_NOT_VALID_FOR_PRODUCTION_RUN')
        result = execute(args.project_root.resolve(),now=now,week=wk,
                         commissioning_trial=args.mode=='trial')
        # No raw provider exception, ID or player/league private data in console.
        public = {k:result[k] for k in ('contract','season','week','slot','operator_state',
                                        'completed_phases','blocker','transaction_authority',
                                        'commissioning_trial')}
        print('WEEKLY_OPERATOR_RESULT='+json.dumps(public,sort_keys=True),flush=True)
        print('NO_ESPN_WRITES=TRUE;ESPN_ACTION_AUTHORITY=NONE',flush=True)
        # A full *trial phase chain* is a useful acceptance result even while
        # the transaction/report product correctly remains incomplete.
        trial_chain = (args.mode == 'trial' and
                       result['operator_state']=='INCOMPLETE_COVERAGE' and
                       result['completed_phases']==list(PHASES[:-1]) and
                       result['blocker']=='FULL_ACTION_CERTIFICATION_NOT_COMMISSIONED')
        return 0 if (trial_chain or result['operator_state']=='SCOPED_READY') else 3
    except (Blocked,ValueError,OSError) as exc:
        print('WEEKLY_OPERATOR_BLOCKED='+str(exc),flush=True)
    except Exception as exc:
        print('WEEKLY_OPERATOR_BLOCKED_EXCEPTION_TYPE='+type(exc).__name__,flush=True)
    print('NO_ESPN_WRITES=TRUE;ESPN_ACTION_AUTHORITY=NONE',flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
