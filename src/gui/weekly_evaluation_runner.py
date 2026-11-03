"""Guarded GUI adapter to the existing supervised v2 weekly operator.

This module never implements football valuation, provider fetch, capture, or ESPN
transactions. The pinned published operator alone owns the prospective workflow.
Every start is explicitly human-approved and remains action-uncertified.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta, date
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

OPERATOR_BLOB = 'eb5990de21d2bd80d701fdbfb218dd71db17c2a7'
PORTABLE = 'fantasy_football_portable_win10_11_20261027_v2'
RELEASE = 'fantasy_season_v0_36_repack1'
FIRST_MONDAY = date(2026, 9, 7)
DST_END_UTC = datetime(2026, 11, 1, 6, tzinfo=timezone.utc)
SLOTS = {0:'MON', 1:'TUE', 2:'WED', 5:'SAT'}
MAX_OPERATOR_OUTPUT = 100_000
_RUNNING: set[str] = set()

class EvaluationBlocked(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise EvaluationBlocked(reason)


def blob(path: Path) -> str:
    need(path.is_file() and not path.is_symlink(), 'OPERATOR_SOURCE_MISSING_OR_LINKED')
    raw = path.read_bytes().removeprefix(b'\xef\xbb\xbf').replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def clock(now: datetime) -> tuple[int, str, str]:
    """Mirror pinned operator's local 2026 calendar; never infer from saved MC."""
    need(isinstance(now, datetime) and now.tzinfo is not None, 'NAIVE_CLOCK')
    utc = now.astimezone(timezone.utc)
    zone = timezone(timedelta(hours=-5 if utc >= DST_END_UTC else -4))
    local = utc.astimezone(zone)
    week = (local.date() - FIRST_MONDAY).days // 7 + 1
    need(1 <= week <= 18, 'OUT_OF_SEASON')
    return week, SLOTS.get(local.weekday(), 'PASSIVE'), local.strftime('%Y%m%d')


def prepare(runtime: Path, executable: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Read-only preflight. No network/capture/MC; no automatic process starts."""
    now = now or datetime.now(timezone.utc)
    runtime = runtime.resolve()
    need(runtime.name == RELEASE and runtime.parent.name == 'fantasy_football'
         and runtime.parent.parent.name == PORTABLE, 'NOT_EXISTING_PORTABLE_V2')
    root = runtime.parent
    operator = root / 'tools/operations/weekly_operator_v2.py'
    need(blob(operator) == OPERATOR_BLOB, 'PUBLISHED_OPERATOR_IDENTITY_MISMATCH')
    need((runtime / 'fantasy.py').is_file() and (runtime / 'data/season_decisions').is_dir(),
         'COMMISSIONED_RUNTIME_OR_PRIVATE_RECEIPT_DIR_MISSING')
    executable = executable.resolve()
    need(executable.is_file(), 'GUI_PYTHON_UNAVAILABLE')
    week, slot, day = clock(now)
    need(slot in ('MON', 'TUE', 'WED', 'SAT'), 'NO_PROTECTED_OPERATOR_WINDOW')
    name = f'operator_v2_trial_2026_w{week:02d}_{slot}_{day}'
    folder = runtime / 'data/season_decisions'
    # If a prior attempt launched, its phase markers are authority. Never
    # silently launch a second expensive run in the same protected window.
    need(not (folder / (name+'.launch.json')).exists() and
         not (folder / (name+'.report.json')).exists(),
         'TRIAL_ALREADY_STARTED_THIS_SLOT_NO_AUTOMATIC_REPEAT')
    return {'root': root, 'runtime': runtime, 'operator': operator,
            'executable': executable, 'week':week, 'slot':slot,
            'name':name, 'folder':folder, 'id':str(runtime)}


def phase_status(plan: dict[str, Any]) -> str:
    """Existence-only observation of fixed private phase filenames."""
    folder, stem = plan['folder'], plan['name']
    if (folder / (stem+'.report.json')).is_file():
        return 'REPORT_WRITTEN'
    for phase in ('MC', 'CAPTURE', 'SYNC'):
        low=phase.lower()
        if (folder / (stem+'.'+low+'.done.json')).is_file():
            return phase+'_COMPLETE'
        if (folder / (stem+'.'+low+'.start.json')).is_file():
            return phase+'_RUNNING_OR_INTERRUPTED'
    if (folder / (stem+'.launch.json')).is_file():
        return 'CALENDAR_OR_PREFLIGHT'
    return 'LAUNCH_PENDING'


def outcome(returncode: int, stdout: bytes, plan: dict[str, Any]) -> dict[str, Any]:
    """Strictly parse bounded sanitized native public results; never echo child logs."""
    if len(stdout) > MAX_OPERATOR_OUTPUT:
        return {'state':'BLOCKED_UNBOUNDED_OPERATOR_OUTPUT','action_authority':'NONE'}
    try:
        output = stdout.decode('utf-8', 'strict')
    except UnicodeDecodeError:
        return {'state':'BLOCKED_OPERATOR_OUTPUT_ENCODING','action_authority':'NONE'}
    lines = [x for x in output.splitlines() if x.startswith('WEEKLY_OPERATOR_RESULT=')]
    if len(lines) != 1:
        # The operator may emit WEEKLY_OPERATOR_BLOCKED=...; never surface
        # untrusted raw stdout or private provider exception strings.
        errors = [x.removeprefix('WEEKLY_OPERATOR_BLOCKED=') for x in output.splitlines()
                  if x.startswith('WEEKLY_OPERATOR_BLOCKED=')]
        code = (errors[0] if (len(errors)==1 and len(errors[0])<=100 and
               all(c.isupper() or c.isdigit() or c in '_:' for c in errors[0])) else 'NO_VALID_PUBLIC_RESULT')
        return {'state':'BLOCKED_'+code, 'action_authority':'NONE'}
    try:
        row=json.loads(lines[0].split('=',1)[1])
    except (ValueError,TypeError):
        return {'state':'BLOCKED_OPERATOR_RESULT_JSON','action_authority':'NONE'}
    if not isinstance(row,dict) or row.get('transaction_authority')!='NONE' or \
       row.get('commissioning_trial') is not True or row.get('week')!=plan['week'] or \
       row.get('slot')!=plan['slot'] or row.get('contract')!='WEEK8_INTEGRATED_OPERATOR_V2_SOURCE_CANDIDATE_V1':
        return {'state':'BLOCKED_OPERATOR_AUTHORITY_OR_IDENTITY','action_authority':'NONE'}
    state=row.get('operator_state')
    if state not in ('SCOPED_READY','CAPTURE_REQUIRED','BLOCKED_SOURCE','BLOCKED_HEALTH','INCOMPLETE_COVERAGE'):
        return {'state':'BLOCKED_UNKNOWN_OPERATOR_STATE','action_authority':'NONE'}
    phases=row.get('completed_phases')
    if not isinstance(phases,list) or len(phases)>6 or any(x not in
        ('CALENDAR','SYNC','CAPTURE','MC','REVIEW','REPORT') for x in phases):
        return {'state':'BLOCKED_PHASE_RECEIPT_SHAPE','action_authority':'NONE'}
    blocker = row.get('blocker')
    if blocker is not None and (not isinstance(blocker,str) or len(blocker)>120 or
        not all(c.isupper() or c.isdigit() or c in '_:' for c in blocker)):
        blocker = 'UNSAFE_BLOCKER_REDACTED'
    # Even a fully completed nine-channel MC is not certified for ESPN writes.
    return {'state': 'NATIVE_MC_COMPLETE_ACTION_CERTIFICATION_BLOCKED'
            if returncode == 0 and state == 'INCOMPLETE_COVERAGE' and 'MC' in phases
            else 'REVIEW_ONLY_NO_ESPN_AUTHORITY' if returncode == 0
            else 'BLOCKED_'+state,
            'native_state':state,'phases':phases,'blocker':blocker,
            'action_authority':'NONE'}


async def supervised_run(plan: dict[str, Any]) -> dict[str, Any]:
    """Exactly one supervised child per GUI process; no retry after any failure."""
    key=plan['id']
    need(key not in _RUNNING, 'GUI_WEEKLY_EVALUATION_ALREADY_RUNNING')
    # Close click-to-click race before spawning a child.
    _RUNNING.add(key)
    try:
        # Recheck all predecessor invariants immediately before execution.
        fresh=prepare(plan['runtime'],plan['executable'])
        need(fresh['name']==plan['name'], 'PROTECTED_WINDOW_CHANGED')
        child = await asyncio.create_subprocess_exec(
            str(plan['executable']), '-B', str(plan['operator']),
            '--project-root', str(plan['root']), '--week',str(plan['week']),
            '--mode','trial','--ack-live-readonly',
            cwd=str(plan['root']),stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        # No optimistic success and no automatic rerun. A server restart or
        # disconnect leaves the operator's immutable launch receipts intact.
        out,_=await child.communicate()
        return outcome(child.returncode,out,plan)
    finally:
        _RUNNING.discard(key)
