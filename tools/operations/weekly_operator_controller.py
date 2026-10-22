"""Restart-safe phase-gated weekly controller M1a (no new sync or capture).

Discovers the immutable latest snapshot/capture/native receipt, reuses a complete
MC, or explicitly and guardingly resumes *only an unlaunched* native MC for an
already-captured epoch. Never reruns an uncertain MC, never writes ESPN, never
claims a transaction is executable, and never backfills a pregame capture.

This is a source-only control-root diagnostic, not a commissioned automatic
refresh/capture/scheduler. It depends on the unchanged guarded native launcher
and published weekly_operator_review. No automatic recovery retry loop.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys
from typing import Any, Callable

PHASES = ('NEW_SNAPSHOT_REQUIRED', 'CAPTURE_REQUIRED', 'MC_READY_TO_GUARD',
          'MC_OUTCOME_UNCERTAIN', 'NATIVE_RECEIPT_READY')
MARKER_PREFIX = 'weekly_operator_m1a_mc_launch_'

class Blocked(ValueError):
    pass

def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Blocked(reason)

def _deps(root: Path):
    ops = root / 'tools' / 'operations'
    need(ops.is_dir(), 'OPERATIONS_DIRECTORY_MISSING')
    if str(ops) not in sys.path:
        sys.path.insert(0, str(ops))
    import weekly_operator_review as review
    import guarded_weekly_cycle as guarded
    return review, guarded

def _matching_files(runtime: Path, folder: str, pattern: str, loader: Callable[[Path], dict],
                    match: Callable[[dict], bool]) -> list[tuple[Path,dict]]:
    base = runtime / folder
    need(base.is_dir(), 'EVIDENCE_DIRECTORY_MISSING:'+folder)
    out=[]
    for path in sorted(base.glob(pattern)):
        need(path.is_file() and path.resolve().is_relative_to(base.resolve()),
             'EVIDENCE_PATH_INVALID')
        item=loader(path)
        if match(item):
            out.append((path,item))
    return out

def _launch_markers(runtime: Path, snapshot_hash: str, capture_hash: str, load) -> list[str]:
    folder = runtime/'data/season_decisions'
    matched=[]
    # Include known legacy and permanent launch records; a matching prior
    # attempt with no receipt must not trigger another expensive MC.
    for item in sorted(folder.glob('*mc_launch*.json')):
        need(item.is_file(), 'LAUNCH_EVIDENCE_NOT_FILE')
        obj=load(item)
        if (obj.get('snapshot_sha256')==snapshot_hash and
                obj.get('capture_sha256')==capture_hash):
            matched.append(item.name)
    return matched

def inspect(root: Path, *, now: datetime, week: int | None = None,
            verifier: Callable[[dict],bool] | None = None,
            canonical: Callable[[dict],str] | None = None,
            review_module: Any = None) -> dict:
    """Pure inspection of already-frozen phase artifacts; no provider/MC work."""
    need(now.tzinfo is not None, 'NAIVE_NOW_FORBIDDEN')
    need(root.name.casefold()=='fantasy_football', 'WRONG_CONTROL_ROOT')
    review=review_module or _deps(root)[0]
    runtime=root/'fantasy_season_v0_36_repack1'
    need(runtime.is_dir(), 'COMMISSIONED_RUNTIME_MISSING')
    latest=runtime/'data/season_snapshots/latest.json'
    if not latest.is_file():
        return {'phase':PHASES[0], 'reason':'NO_LATEST_SNAPSHOT', 'week':week,
                'authority':'NONE', 'native_mc_started':False}
    snap=review.jload(latest)
    stamp=review.utc(snap.get('snapshot_utc'))
    season=review.uid((snap.get('espn') or {}).get('season'))
    wk=review.uid((snap.get('espn') or {}).get('week'))
    need(stamp is not None and stamp<=now and season is not None and wk is not None,
         'LATEST_SNAPSHOT_EPOCH_INVALID')
    if week is not None and wk!=week:
        return {'phase':PHASES[0], 'reason':'LATEST_WEEK_DIFFERS_FROM_REQUESTED_WEEK',
                'week':week, 'observed_week':wk,'authority':'NONE','native_mc_started':False}
    snapshot_hash=review.sha(latest.read_bytes())
    snapshots=_matching_files(runtime,'data/season_snapshots','*/snapshot.json',review.jload,
        lambda obj:obj.get('snapshot_utc')==snap['snapshot_utc'] and obj.get('espn') is not None)
    exact=[p for p,obj in snapshots if review.sha(p.read_bytes())==snapshot_hash]
    need(len(exact)==1,'LATEST_IMMUTABLE_SNAPSHOT_IDENTITY_AMBIGUOUS')
    for provider in ('espn','sleeper','nflverse_rosters','nflverse_matchups','nfl_official_rosters','nfl_official'):
        entry=(snap.get('source_status') or {}).get(provider)
        need(isinstance(entry,dict) and (entry.get('complete') if provider=='nfl_official_rosters'
             and entry.get('complete') is not None else entry.get('ok')) is True,
             'SIX_PROVIDER_SNAPSHOT_HEALTH_BLOCKED:'+provider)
    base={'week':wk,'season':season,'snapshot_sha256':snapshot_hash,
          'snapshot_utc':snap['snapshot_utc'],'authority':'NONE','native_mc_started':False}
    captures=_matching_files(runtime,'data/season_predictions/closure',
        f'pregame_{season}_w{wk:02d}_*.json',review.jload,
        lambda obj:obj.get('snapshot_utc')==snap['snapshot_utc'])
    need(len(captures)<=1,'AMBIGUOUS_CAPTURE_FOR_LATEST_EPOCH')
    if not captures:
        return {**base,'phase':PHASES[1], 'reason':'SNAPSHOT_EXISTS_WITHOUT_PROSPECTIVE_CAPTURE'}
    cp,cap=captures[0]
    captured=review.utc(cap.get('captured_utc'))
    need(captured is not None and stamp<=captured<=now and
         review.uid(cap.get('season'))==season and review.uid(cap.get('week'))==wk,
         'CAPTURE_CHRONOLOGY_OR_WEEK_INVALID')
    need(cap.get('measurement_contract')=='A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
         'CAPTURE_NOT_PROSPECTIVE')
    canon=canonical or review._canon
    need((cap.get('behavioral_observation_state') or {}).get('snapshot_sha256')==canon(snap),
         'CAPTURE_SNAPSHOT_BINDING_INVALID')
    if verifier is not None:
        need(verifier(cap),'CAPTURE_INTEGRITY_INVALID')
    fw=cap.get('pre_data_firewall') or {}
    need(all(fw.get(key) is False for key in
             ('2026_game_outcomes_used_for_tuning','automatic_refit','automatic_calibration')),
         'CAPTURE_PROSPECTIVE_FIREWALL_INVALID')
    ch=review.sha(cp.read_bytes())
    base.update({'capture_sha256':ch,'capture_file':cp.relative_to(runtime).as_posix()})
    matches=_matching_files(runtime,'data/season_decisions','weekly_decision_receipt_*.json',
        review.jload,lambda obj:(obj.get('provenance') or {}).get('snapshot_utc')==snap['snapshot_utc'])
    need(len(matches)<=1,'NATIVE_RECEIPT_AMBIGUOUS_FOR_CAPTURE')
    if matches:
        # Reuse the published authoritative join including exact runtime deps,
        # nine-channel coverage, and receipt operational health.
        _,_,_,ids=review.discover(runtime,now,verify_capture=verifier,canonical=canon)
        return {**base, 'phase':PHASES[4], 'reason':'REUSE_VALIDATED_NATIVE_MC',
                'receipt_sha256':ids['receipt_sha256'],'native_mc_started':True,
                'no_repeat_mc':True}
    markers=_launch_markers(runtime,snapshot_hash,ch,review.jload)
    if markers:
        return {**base,'phase':PHASES[3], 'reason':'MATCHING_MC_LAUNCH_WITHOUT_VALID_RECEIPT',
                'native_mc_started':True, 'no_repeat_mc':True,'launch_markers':len(markers)}
    if (now-captured)>timedelta(hours=2):
        return {**base,'phase':PHASES[1],
                'reason':'FROZEN_CAPTURE_TOO_OLD_FOR_NEW_MC_DO_NOT_BACKFILL',
                'native_mc_started':False,'no_repeat_mc':False}
    return {**base,'phase':PHASES[2], 'reason':'CAPTURE_PRESENT_NO_NATIVE_MC',
            'native_mc_started':False,'no_repeat_mc':False}

def _identity_pair(runtime:Path,now:datetime, load) -> tuple[str,str]:
    """Use existing recent commissioning and memory receipts, never fabricate them."""
    dirname=runtime/'data/season_decisions'
    def select(glob:str, condition) -> str:
        candidates=[]
        for p in sorted(dirname.glob(glob)):
            obj=load(p)
            if condition(obj):
                t=obj.get('verified_utc') or obj.get('checked_utc')
                try:
                    dt=datetime.fromisoformat(t.replace('Z','+00:00')) if isinstance(t,str) else None
                except (ValueError,OverflowError):
                    dt=None
                if dt is not None and dt.tzinfo is not None and 0 <= (now-dt.astimezone(timezone.utc)).total_seconds() < 7200:
                    candidates.append((dt,p))
        need(bool(candidates),'FRESH_'+glob.upper().replace('*','')+'_EVIDENCE_REQUIRED')
        candidates.sort(key=lambda x:x[0])
        return candidates[-1][1].relative_to(runtime).as_posix()
    return (select('*commissioned_identity*.json',lambda x:x.get('commissioned') is True),
            select('*memory_health*.json',lambda x:x.get('strict') is True and x.get('status')=='PASS'))

def execute_existing_mc(root:Path, now:datetime, planned:dict, *, review_module=None,
                        guard_module=None, child=None) -> dict:
    """Explicit resume of *unlaunched* MC only. No six-provider refresh here."""
    need(planned.get('phase')==PHASES[2], 'MC_LAUNCH_BLOCKED_BY_PHASE')
    review=review_module or _deps(root)[0]
    guarded=guard_module or _deps(root)[1]
    runtime=guarded.validate_root(root)
    reread=inspect(root,now=now,week=planned['week'],review_module=review,
                   canonical=review._canon)
    need(reread['phase']==PHASES[2] and reread['capture_sha256']==planned['capture_sha256']
         and reread['snapshot_sha256']==planned['snapshot_sha256'],
         'PRELAUNCH_EPOCH_CHANGED')
    identity,memory=_identity_pair(runtime,now,review.jload)
    snap_rel='data/season_snapshots/latest.json'
    paths=(snap_rel,planned['capture_file'],identity,memory)
    locks,evidence=guarded.inspect(root,runtime,*paths,now)
    need(evidence['capture_sha256']==planned['capture_sha256'] and
         evidence['snapshot_sha256']==planned['snapshot_sha256'],
         'PROTECTED_CAPTURE_IDENTITY_CHANGED')
    timing=guarded.evaluate_timing(root,now,locks['deadline'])
    need(timing['classification']=='READY_TO_START_MC_NOT_ACTION_AUTHORITY',
         'INSUFFICIENT_PROTECTED_MC_WINDOW')
    out=runtime/'data/season_decisions'
    marker=out/(MARKER_PREFIX+planned['capture_sha256']+'.json')
    payload={'contract':'WEEKLY_OPERATOR_M1A_V1','week':planned['week'],
             'snapshot_sha256':planned['snapshot_sha256'],
             'capture_sha256':planned['capture_sha256'],
             'snapshot_utc':planned['snapshot_utc'], 'launched_utc':now.isoformat(),
             'no_automatic_relaunch':True}
    # Fail closed if a launch was previously attempted, even after a crash.
    with marker.open('x',encoding='utf-8') as stream:
        json.dump(payload,stream,sort_keys=True)
        stream.write('\n')
        stream.flush()
    result=guarded.execute(root,runtime,paths,locks['deadline'],evidence,
                           child=child)
    need(result.get('receipt_sha256') is not None, 'NATIVE_MC_NO_RECEIPT_IDENTITY')
    return {'phase':'NATIVE_MC_COMPLETED_REVIEW_REQUIRED',
            'receipt_sha256':result['receipt_sha256'],
            'action_window':result['action_window'],'authority':'NONE',
            'native_mc_started':True,'no_repeat_mc':True}

def run(root:Path, *, now:datetime|None=None, week:int|None=None, mode:str='review',
        review_module=None, guarded_module=None, review_run=None,
        verifier=None, canonical=None, child=None) -> dict:
    now=now or datetime.now(timezone.utc)
    review=review_module or _deps(root)[0]
    guarded=guarded_module or _deps(root)[1]
    # Always verify installed committed runtime and strict-memory health before
    # reporting a phase eligible for MC. Review.run repeats these checks.
    guarded.validate_root(root)
    planned=inspect(root,now=now,week=week,verifier=verifier,canonical=canonical,
                    review_module=review)
    if mode=='status':
        return planned
    if planned['phase']==PHASES[4]:
        result=(review_run or review.run)(root)
        return {'phase':'READONLY_DECISION_REVIEW', 'planner':planned,
                'operator_state':result.get('operator_state'),'queue':result.get('queue'),
                'next_check_utc':result.get('next_check_utc'),'authority':'NONE',
                'native_mc_started':False, 'no_repeat_mc':True}
    if mode=='resume-mc' and planned['phase']==PHASES[2]:
        completed=execute_existing_mc(root,now,planned,review_module=review,
                                      guard_module=guarded,child=child)
        # A completed native receipt can be reused even if live reconciliation
        # subsequently fails; never repeat the MC in an attempt to repair it.
        evaluated=(review_run or review.run)(root)
        return {**completed, 'phase':'READONLY_DECISION_REVIEW',
                'operator_state':evaluated.get('operator_state'),
                'queue':evaluated.get('queue'),
                'next_check_utc':evaluated.get('next_check_utc')}
    return planned

def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',default='.')
    ap.add_argument('--week',type=int)
    ap.add_argument('--mode',choices=('status','review','resume-mc'),default='review')
    args=ap.parse_args(argv)
    print('WEEKLY OPERATOR M1A RESTART-SAFE PHASE CONTROLLER',flush=True)
    try:
        output=run(Path(args.project_root).resolve(),week=args.week,mode=args.mode)
        print('CONTROLLER_RESULT='+json.dumps(output,sort_keys=True,ensure_ascii=True,separators=(',',':')),flush=True)
        print('NO_ESPN_WRITES=TRUE;NO_AUTOMATIC_REFRESH_OR_CAPTURE=TRUE;ACTION_AUTHORITY=NONE',flush=True)
        return 0 if output.get('phase') in {'READONLY_DECISION_REVIEW','NATIVE_RECEIPT_READY',
                                          'NATIVE_MC_COMPLETED_REVIEW_REQUIRED'} else 2
    except (Blocked,ValueError,OSError,KeyError,TypeError) as exc:
        print('CONTROLLER_BLOCKED='+str(exc),flush=True)
    except Exception as exc:
        print('CONTROLLER_EXCEPTION_TYPE='+type(exc).__name__,flush=True)
    print('NO_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE',flush=True)
    return 3

if __name__=='__main__':
    raise SystemExit(main())
