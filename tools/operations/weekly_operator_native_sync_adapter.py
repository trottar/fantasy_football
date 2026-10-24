"""M1b opt-in adapter for the *installed* native six-provider season sync.

Installing or importing this module performs no provider calls or writes. Only
observe_approved_sync_once, when passed explicit execution_approved=True by an
independently authorized caller, invokes the exact installed native callback.
The commissioned runtime and P/D/K business logic remain unchanged.
"""
from __future__ import annotations

import ast
from importlib import import_module
from pathlib import Path
import hashlib
import sys
from typing import Any, Callable

NATIVE_SYNC_BLOB = 'eabcbee3ea2a06e7f68dfea5cbe0e4a2eb768609'
NATIVE_CLI_BLOB = 'dd3a0a2b39ea1c6b424e71f6a11273f2503ccc64'
OBSERVER_BLOB = 'da0250350e0a6419455412af172887960f11025e'
NATIVE_KWARGS = ('secrets_path', 'out_root', 'week', 'include_sleeper', 'include_nfl')

class Blocked(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Blocked(reason)


def blob(raw: bytes) -> str:
    clean=raw.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n',b'\n').replace(b'\r',b'\n')
    return hashlib.sha1(b'blob '+str(len(clean)).encode('ascii')+b'\0'+clean).hexdigest()


def checked_source(path: Path, oid: str, label: str) -> bytes:
    need(path.is_file() and not path.is_symlink(), label+'_SOURCE_MISSING_OR_SYMLINK')
    need(0<path.stat().st_size<=2*1024*1024, label+'_SOURCE_UNBOUNDED')
    raw=path.read_bytes()
    need(blob(raw)==oid, label+'_SOURCE_BLOB_MISMATCH')
    return raw


def _ast_binding(sync_bytes: bytes, cli_bytes: bytes) -> None:
    try:
        t=ast.parse(sync_bytes.decode('utf-8-sig'))
        c=ast.parse(cli_bytes.decode('utf-8-sig'))
    except (UnicodeError,SyntaxError) as exc:
        raise Blocked('NATIVE_SOURCE_AST_INVALID') from exc
    routines=[f for f in t.body if isinstance(f,ast.FunctionDef) and f.name=='sync_season_snapshot']
    need(len(routines)==1 and tuple(a.arg for a in routines[0].args.args)==NATIVE_KWARGS
         and routines[0].args.vararg is None and routines[0].args.kwarg is None,
         'NATIVE_SYNC_SIGNATURE_CHANGED')
    cmds=[f for f in c.body if isinstance(f,ast.FunctionDef) and f.name=='cmd_season_sync']
    need(len(cmds)==1,'NATIVE_CLI_BINDING_CHANGED')
    calls=[f for f in ast.walk(cmds[0]) if isinstance(f,ast.Call) and
           isinstance(f.func,ast.Name) and f.func.id=='sync_season_snapshot']
    need(len(calls)==1 and {k.arg for k in calls[0].keywords}==set(NATIVE_KWARGS),
         'NATIVE_CLI_BINDING_CHANGED')


def boundary(root: Path) -> Path:
    """Read-only fixed-identity check; no import of native sync or secrets."""
    need(root.name.casefold()=='fantasy_football','WRONG_CONTROL_ROOT')
    runtime=root/'fantasy_season_v0_36_repack1'
    need(runtime.is_dir() and not runtime.is_symlink(),'COMMISSIONED_RUNTIME_MISSING')
    ver=runtime/'VERSION'
    need(ver.is_file() and not ver.is_symlink() and
         ver.read_text(encoding='utf-8-sig').strip()=='0.36','COMMISSIONED_VERSION_MISMATCH')
    cli=checked_source(runtime/'fantasy.py',NATIVE_CLI_BLOB,'NATIVE_CLI')
    sync=checked_source(runtime/'src/season_snapshot.py',NATIVE_SYNC_BLOB,'NATIVE_SYNC')
    checked_source(root/'tools/operations/weekly_operator_refresh_duration_receipt.py',
                   OBSERVER_BLOB,'PUBLISHED_OBSERVER')
    _ast_binding(sync,cli)
    # Runtime source is authoritative. Control-root src copy is not required.
    return runtime


def _load_native(runtime: Path) -> Any:
    """Deferred until after explicit approval; reject already-loaded foreign src."""
    prefix=str(runtime.resolve())
    for name in ('src','src.season_snapshot'):
        existing=sys.modules.get(name)
        if existing is not None:
            loc=getattr(existing,'__file__',None)
            if loc is not None:
                owned=Path(loc).resolve().is_relative_to(runtime.resolve())
            elif name=='src':
                locations=getattr(existing,'__path__',None)
                owned=bool(locations) and all(
                    Path(item).resolve()==(runtime/'src').resolve()
                    for item in locations)
            else:
                owned=False
            need(owned, 'FOREIGN_SRC_MODULE_ALREADY_LOADED')
    sys.path.insert(0,prefix)
    try:
        module=import_module('src.season_snapshot')
    finally:
        sys.path.remove(prefix)
    return module


def observe_approved_sync_once(root: Path, *, week: int, buffer_seconds: int,
                               execution_approved: bool = False,
                               boundary_check: Callable[[Path],Path] | None = None,
                               module_loader: Callable[[Path],Any] | None = None,
                               observer: Any = None) -> dict:
    """Run one *separately approved* native sync, without MC/capture/action.

    This function is never executed by installation, imports or test packaging.
    Caller owns live authorization, calendar/lock gates, and any private receipt
    persistence. Synthetic collaborator injection is reserved for isolated tests.
    """
    need(execution_approved is True, 'EXPLICIT_REFRESH_APPROVAL_REQUIRED')
    need(type(week) is int and 1<=week<=18, 'INVALID_WEEK')
    need(type(buffer_seconds) is int and 60<=buffer_seconds<=3600,
         'EXPLICIT_REFRESH_MARGIN_REQUIRED')
    check=boundary_check or boundary
    runtime=check(root)
    need(isinstance(runtime,Path) and runtime.resolve()==
         (root/'fantasy_season_v0_36_repack1').resolve(), 'RUNTIME_BOUNDARY_INVALID')
    load=module_loader or _load_native
    module=load(runtime)
    source=getattr(module,'__file__',None)
    need(isinstance(source,str) and Path(source).resolve()==
         (runtime/'src/season_snapshot.py').resolve(), 'NATIVE_MODULE_ORIGIN_MISMATCH')
    native=getattr(module,'sync_season_snapshot',None)
    need(callable(native), 'NATIVE_SYNC_CALLABLE_MISSING')
    if observer is None:
        ops=str(root/'tools/operations')
        sys.path.insert(0,ops)
        try:
            import weekly_operator_refresh_duration_receipt as observer
        finally:
            sys.path.remove(ops)
        # Refuse a stale/misbound prior observer import.
        need(Path(getattr(observer,'__file__','')).resolve()==
             (root/'tools/operations/weekly_operator_refresh_duration_receipt.py').resolve(),
             'OBSERVER_MODULE_ORIGIN_MISMATCH')

    # No optional provider switches, custom output path or secrets input accepted
    # from a caller; use the established configured league credentials locally.
    def invoke_native():
        return native(secrets_path=None,
                      out_root=runtime/'data/season_snapshots',
                      week=week,include_sleeper=True,include_nfl=True)

    measurement=observer.measure_authorized_sync(
        root,week=week,sync_call=invoke_native,buffer_seconds=buffer_seconds)
    need(isinstance(measurement,dict) and measurement.get('action_authority')=='NONE'
         and measurement.get('capture_authority')=='NONE'
         and measurement.get('refresh_authority')=='NONE'
         and measurement.get('automatic_sync_or_mc') is False,
         'MEASUREMENT_AUTHORITY_ESCALATION')
    need(check(root).resolve()==runtime.resolve(), 'NATIVE_SOURCE_CHANGED_DURING_SYNC')
    # Return receipt payload in memory only. persist_private is separately opt-in.
    return measurement
