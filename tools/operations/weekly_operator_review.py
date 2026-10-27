"""Permanent read-only weekly decision-review layer for the commissioned runtime.

One invocation selects the *latest snapshot epoch*, its single prospective
capture and native 9-channel receipt, then rechecks ESPN. It produces a bounded
scope-specific decision queue. It never converts MC candidate offers into an
ESPN submission certificate and never writes local or remote files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess
from pathlib import Path
import sys
from typing import Any, Callable

CHANNELS = (
    'lineup_availability', 'player_waiver_free_agent', 'dst_waiver_free_agent',
    'kicker_waiver_free_agent', 'ir_reserve_open_slot_injury_replacement',
    'trade_one_for_one_player', 'trade_multi_player_unequal',
    'trade_specialist_inclusive', 'prospective_capture_provenance',
)
TRADE_CHANNELS = CHANNELS[5:8]
INACTIVE_SLOTS = {'', 'BE', 'BENCH', 'IR', 'RESERVE'}
ROSTER_FIELDS = ('on_team_id','position','nfl_team','lineup_slot_id','lineup_slot',
                 'lineup_locked','injury_status','active','eligible_slots','droppable')
MARKET_FIELDS = ('fantasy_status','on_team_id','injury_status','active',
                 'acquisition_type','acquisition_date')
UNKNOWN_INJURY = {'QUESTIONABLE','DOUBTFUL','OUT','IR','INJURED_RESERVE','SUSPENDED','PUP'}

class Blocked(ValueError):
    pass

def require(value: bool, reason: str) -> None:
    if not value:
        raise Blocked(reason)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def jload(path: Path) -> dict[str, Any]:
    require(path.is_file(), 'MISSING_LOCAL_ARTIFACT:'+path.name)
    try:
        result=json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, ValueError) as exc:
        raise Blocked('MALFORMED_LOCAL_ARTIFACT:'+path.name) from exc
    require(isinstance(result,dict), 'NOT_JSON_OBJECT:'+path.name)
    return result

def utc(raw: Any) -> datetime | None:
    try:
        value=datetime.fromisoformat(str(raw).replace('Z','+00:00'))
        return value.astimezone(timezone.utc) if value.tzinfo is not None else None
    except (ValueError, TypeError, OverflowError):
        return None

def uid(raw: Any) -> int | None:
    if isinstance(raw,bool):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError, OverflowError):
        return None

def index(rows: list[dict], label: str) -> dict[int,dict]:
    require(isinstance(rows,list),'NOT_LIST:'+label)
    result={}
    for row in rows:
        require(isinstance(row,dict),'INVALID_ROW:'+label)
        pid=uid(row.get('espn_id'))
        require(pid is not None and pid not in result,'DUPLICATE_OR_MISSING_ID:'+label)
        result[pid]=row
    return result

def roster(espn:dict, teamid:int) -> list[dict]:
    matches=[t for t in (espn.get('teams') or []) if isinstance(t,dict) and uid(t.get('team_id'))==teamid]
    require(len(matches)==1 and isinstance(matches[0].get('roster'),list),'OWNER_TEAM_UNRESOLVED')
    return matches[0]['roster']

def receipt_channels(rec:dict) -> dict[str,dict]:
    found={}
    for row in rec.get('channels') or []:
        require(isinstance(row,dict),'RECEIPT_CHANNEL_INVALID')
        k=row.get('key')
        require(k in CHANNELS and k not in found,'RECEIPT_CHANNEL_DUPLICATE_OR_UNKNOWN')
        found[k]=row
    require(set(found)==set(CHANNELS),'NINE_CHANNEL_MATRIX_INCOMPLETE')
    return found

def safe_candidates(root:Path, directory:str, pattern:str) -> list[Path]:
    base=(root/directory).resolve()
    require(base.is_dir() and base.is_relative_to(root.resolve()),'ARTIFACT_DIRECTORY_INVALID')
    return sorted(p for p in base.glob(pattern) if p.is_file() and p.resolve().is_relative_to(base))

def _canon(value: Any) -> str:
    # Native canonical SHA uses sorted JSON and exact package/source contract.
    return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,
                          allow_nan=False,default=str).encode('utf-8'))

def discover(runtime:Path, now:datetime, *, verify_capture:Callable[[dict],bool] | None=None,
             canonical:Callable[[dict],str] | None=None) -> tuple[dict,dict,dict,dict]:
    """Reject stale epochs, ambiguous joins, or incomplete provenance."""
    require(runtime.is_dir(),'COMMISSIONED_RUNTIME_MISSING')
    snapshot=jload(runtime/'data/season_snapshots/latest.json')
    snaputc=utc(snapshot.get('snapshot_utc'))
    season=uid((snapshot.get('espn') or {}).get('season'))
    week=uid((snapshot.get('espn') or {}).get('week'))
    require(snaputc is not None and snaputc<=now and season is not None and week is not None,
            'LATEST_SNAPSHOT_EPOCH_INVALID')
    # Latest is a copy: prove a single immutable source snapshot identical bytewise.
    options=[]
    latest_hash=sha((runtime/'data/season_snapshots/latest.json').read_bytes())
    for p in safe_candidates(runtime,'data/season_snapshots','*/snapshot.json'):
        obj=jload(p)
        if obj.get('snapshot_utc')==snapshot.get('snapshot_utc') and sha(p.read_bytes())==latest_hash:
            options.append(p)
    require(len(options)==1,'LATEST_IMMUTABLE_SNAPSHOT_IDENTITY_AMBIGUOUS')
    captured=[]
    for p in safe_candidates(runtime,'data/season_predictions/closure',f'pregame_{season}_w{week:02d}_*.json'):
        obj=jload(p)
        if obj.get('snapshot_utc')==snapshot.get('snapshot_utc'):
            captured.append((p,obj))
    require(len(captured)==1,'CAPTURE_REQUIRED_FOR_LATEST_SNAPSHOT')
    cp,capture=captured[0]
    ct=utc(capture.get('captured_utc'))
    require(ct is not None and snaputc<=ct<=now and
            uid(capture.get('season'))==season and uid(capture.get('week'))==week,
            'CAPTURE_CHRONOLOGY_OR_WEEK_INVALID')
    require(capture.get('measurement_contract')=='A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034',
            'CAPTURE_NOT_PROSPECTIVE')
    if canonical is not None:
        require((capture.get('behavioral_observation_state') or {}).get('snapshot_sha256')==canonical(snapshot),
                'SNAPSHOT_CAPTURE_BINDING_INVALID')
    if verify_capture is not None:
        require(verify_capture(capture),'CAPTURE_INTEGRITY_INVALID')
    matches=[]
    for p in safe_candidates(runtime,'data/season_decisions','weekly_decision_receipt_*.json'):
        obj=jload(p)
        if (obj.get('provenance') or {}).get('snapshot_utc')==snapshot.get('snapshot_utc'):
            matches.append((p,obj))
    require(len(matches)==1,'NATIVE_NINE_CHANNEL_RECEIPT_REQUIRED_OR_AMBIGUOUS')
    rp,rec=matches[0]
    rt=utc(rec.get('generated_utc'))
    require(rt is not None and ct<=rt<=now and uid(rec.get('season'))==season and
            uid(rec.get('week'))==week and (rec.get('operational_health') or {}).get('status')=='PASS',
            'NATIVE_RECEIPT_HEALTH_OR_CHRONOLOGY_INVALID')
    # A native healthy-but-incomplete receipt is valid scoped evidence, never
    # a roster-wide decision certificate. The actual nine-channel gap must be
    # present; no blocked health channel may be smuggled into scoped review.
    channels = receipt_channels(rec)
    overall = rec.get('overall_state')
    incomplete = [key for key, row in channels.items()
                  if str(row.get('status') or '').startswith('INCOMPLETE_COVERAGE')]
    blocked = [key for key, row in channels.items()
               if str(row.get('status') or '').startswith('BLOCKED_HEALTH')]
    if overall == 'INCOMPLETE_COVERAGE':
        require(bool(incomplete) and not blocked,
                'NATIVE_INCOMPLETE_SCOPE_IDENTITY_INVALID')
    else:
        require(overall in {'COMPLETE / ACTION_REQUIRED', 'COMPLETE / NO_ACTION'}
                and not incomplete and not blocked, 'NATIVE_RECEIPT_NOT_COMPLETE')
    identity_rows=[item.get('evidence') for item in ((rec.get('operational_health') or {}).get('items') or [])
                   if isinstance(item,dict) and item.get('key')=='runtime_identity']
    require(len(identity_rows)==1 and isinstance(identity_rows[0],dict),
            'NATIVE_RUNTIME_IDENTITY_EVIDENCE_REQUIRED')
    deps=identity_rows[0].get('expected_dependencies') or {}
    for label,relative in (('league_config','config/league.json'),('model_config','config/model.json'),
                           ('player_values','data/processed/player_values_2026.csv')):
        require(isinstance(deps.get(label),str) and len(deps[label])==64 and
                (runtime/relative).is_file() and sha((runtime/relative).read_bytes())==deps[label],
                'COMMISSIONED_DEPENDENCY_DRIFT:'+label)
    return snapshot,capture,rec,{'snapshot_sha256':sha(options[0].read_bytes()),
            'capture_sha256':sha(cp.read_bytes()),'receipt_sha256':sha(rp.read_bytes()),
            'snapshot_utc':snapshot['snapshot_utc'],'week':week,'season':season}

def compare(old:dict,new:dict,fields:tuple[str,...]) -> dict:
    changed={pid for pid in set(old)&set(new) if any(old[pid].get(f)!=new[pid].get(f) for f in fields)}
    return {'added':len(set(new)-set(old)),'removed':len(set(old)-set(new)),
            'changed':len(changed),'changed_ids':changed,'added_ids':set(new)-set(old),
            'removed_ids':set(old)-set(new)}

def _txkey(espn:dict) -> tuple | None:
    rows=espn.get('transactions')
    if not isinstance(rows,list) or not rows:
        return None
    fields=('id','type','status','process_date','items')
    return tuple(sorted(json.dumps({k:r.get(k) for k in fields},sort_keys=True,default=str)
                        for r in rows if isinstance(r,dict)))

def _player(row:dict) -> dict:
    return {'name':str(row.get('name') or 'UNRESOLVED'),
            'position':str(row.get('position') or 'UNKNOWN'),
            'lineup_slot':str(row.get('lineup_slot') or ''),
            'injury_status':str(row.get('injury_status') or 'UNKNOWN'),
            'active':row.get('active') if isinstance(row.get('active'),bool) else 'UNKNOWN',
            'lineup_locked':row.get('lineup_locked') if isinstance(row.get('lineup_locked'),bool) else 'UNKNOWN'}

def _kickoffs(cap:dict) -> dict[int,datetime]:
    ret={}
    for group in ('league_player_predictions','specialist_predictions'):
        for row in (cap.get(group) or {}).get('records') or []:
            if not isinstance(row,dict):
                continue
            pid=uid(row.get('espn_id'))
            t=utc(row.get('kickoff_utc'))
            if pid is not None and t is not None:
                if pid in ret and ret[pid]!=t:
                    raise Blocked('CONTRADICTORY_KICKOFF_EVIDENCE')
                ret[pid]=t
    return ret

def decide(snapshot:dict,capture:dict,rec:dict,live:dict,market:list[dict],*,now:datetime) -> dict:
    """Pure decision-to-report function; no network, writes, or MC."""
    require((live.get('season'),live.get('week'))==
            ((snapshot.get('espn') or {}).get('season'),(snapshot.get('espn') or {}).get('week')),
            'LIVE_ESPN_WEEK_CHANGED')
    require(live.get('league_id')==(snapshot.get('espn') or {}).get('league_id'),
            'LIVE_ESPN_LEAGUE_CHANGED')
    teamid=uid(rec.get('team_id'))
    require(teamid is not None and teamid==uid(capture.get('team_id')),'OWNER_IDENTITY_MISMATCH')
    base=(snapshot.get('espn') or {})
    old_own=index(roster(base,teamid),'FROZEN_OWNED')
    new_own=index(roster(live,teamid),'LIVE_OWNED')
    old_market=index(base.get('available_players') or [],'FROZEN_MARKET')
    new_market=index(market,'LIVE_MARKET')
    owned=compare(old_own,new_own,ROSTER_FIELDS)
    mkt=compare(old_market,new_market,MARKET_FIELDS)
    transactions='MATCH' if _txkey(base) is not None and _txkey(base)==_txkey(live) else 'UNVERIFIED_OR_CHANGED'
    settings='MATCH' if base.get('transaction_settings')==live.get('transaction_settings') else 'CHANGED'
    # All partner rosters also matter for trade certification.
    all_teams=lambda e:{uid(t.get('team_id')):index(t.get('roster') or [],'TEAM_ROSTER')
                        for t in e.get('teams') or [] if isinstance(t,dict)}
    old_teams,new_teams=all_teams(base),all_teams(live)
    partner_drift=(set(old_teams)!=set(new_teams) or
                   any(compare(old_teams[k],new_teams[k],ROSTER_FIELDS)['changed'] or
                       set(old_teams[k])!=set(new_teams[k]) for k in set(old_teams)&set(new_teams) if k!=teamid))
    ch=receipt_channels(rec)
    statuses={key:ch[key].get('status') for key in CHANNELS}
    lineup=ch['lineup_availability']
    ev=lineup.get('evidence') or {}
    require(isinstance(ev,dict),'NATIVE_LINEUP_EVIDENCE_INVALID')
    lineup_state='NO_CERTIFIED_LINEUP_EVIDENCE'
    swaps=[]
    if lineup.get('status') in ('PASS / ACTION','PASS / HOLD:LINEUP_AVAILABILITY'):
        selected=ev.get('selected_espn_ids') or []
        current=ev.get('current_starter_espn_ids') or []
        si=[uid(x) for x in selected];ci=[uid(x) for x in current]
        require(si and ci and None not in si and None not in ci and len(si)==len(set(si))
                and len(ci)==len(set(ci)) and set(si).issubset(old_own) and
                set(ci).issubset(old_own),'LINEUP_RECEIPT_IDENTITIES_INVALID')
        current_live={pid for pid,r in new_own.items() if str(r.get('lineup_slot') or '').upper() not in INACTIVE_SLOTS}
        frozen_starters=set(ci)
        ins=set(si)-current_live
        outs=current_live-set(si)
        live_same=(not any(owned[k] for k in ('added','removed','changed')) and
                   current_live==frozen_starters)
        kicks=_kickoffs(capture)
        for pid in sorted(ins):
            record=new_own.get(pid)
            require(record is not None,'SELECTED_STARTER_NO_LONGER_OWNED')
            t=kicks.get(pid)
            locked=record.get('lineup_locked')
            state=('BLOCKED_LOCK_OR_UNKNOWN_KICKOFF' if locked is not False or t is None or t<=now else
                   'PENDING_INJURY_STATUS' if str(record.get('injury_status') or '').upper() in UNKNOWN_INJURY or record.get('active') is not True else
                   'PENDING_ESPN_EXACT_SLOT_CONFIRMATION')
            swaps.append({'direction':'START','player':_player(record),'kickoff_utc':t.isoformat() if t else None,'state':state})
        for pid in sorted(outs):
            record=new_own.get(pid)
            require(record is not None,'CURRENT_STARTER_NO_LONGER_OWNED')
            t=kicks.get(pid)
            locked=record.get('lineup_locked')
            state=('BLOCKED_LOCK_OR_UNKNOWN_KICKOFF' if locked is not False or t is None or t<=now else
                   'PENDING_ESPN_EXACT_SLOT_CONFIRMATION')
            swaps.append({'direction':'BENCH','player':_player(record),'kickoff_utc':t.isoformat() if t else None,'state':state})
        if not live_same:
            lineup_state='CAPTURE_REQUIRED_OWNED_OR_SLOT_DRIFT'
        elif not swaps:
            lineup_state='HOLD_CURRENT_STARTERS'
        elif any(x['state']=='BLOCKED_LOCK_OR_UNKNOWN_KICKOFF' for x in swaps):
            lineup_state='BLOCKED_LOCK_OR_KICKOFF'
        elif any(x['state']=='PENDING_INJURY_STATUS' for x in swaps):
            lineup_state='CONDITIONAL_INJURY_RECHECK_REQUIRED'
        else:
            lineup_state='MODEL_PREFERENCE_APP_SLOT_CONFIRMATION_REQUIRED'
    changed_market_positions=sorted({str((new_market.get(pid) or old_market.get(pid) or {}).get('position') or '')
                                      for pid in mkt['changed_ids']|mkt['removed_ids']|mkt['added_ids']})
    market_drift=any(mkt[k] for k in ('added','removed','changed'))
    trade_count={k:len((ch[k].get('action') or {}).get('offers') or []) for k in TRADE_CHANNELS}
    # Native trade labels cannot override the uncommissioned B2 certification blockers.
    trade_state=('CAPTURE_REQUIRED_MARKET_ROSTER_OR_PARTNER_DRIFT' if
                 market_drift or partner_drift or any(owned[k] for k in ('added','removed','changed')) or
                 transactions!='MATCH' or settings!='MATCH' else 'BLOCKED_UNCERTIFIED_END_TO_END_TRADE')
    queue=[]
    if lineup_state!='HOLD_CURRENT_STARTERS':
        queue.append({'family':'LINEUP','state':lineup_state,'proposals':swaps,
                      'next_step':'REVALIDATE_QUESTIONABLE_STATUS_AND_EXACT_ESPN_SLOTS' if swaps else 'RECOMPUTE_LINEUP_EPOCH'})
    else:
        queue.append({'family':'LINEUP','state':'HOLD_CURRENT_STARTERS','proposals':[],'next_step':'NONE'})
    queue.append({'family':'DST','state':('RECHECK_DST_MARKET' if 'DST' in changed_market_positions else
                 'NATIVE_'+str(statuses['dst_waiver_free_agent'])),'next_step':'NONE_UNLESS_NEW_MARKET_EVIDENCE'})
    queue.append({'family':'K','state':('RECHECK_K_MARKET' if 'K' in changed_market_positions else
                 'NATIVE_'+str(statuses['kicker_waiver_free_agent'])),'next_step':'NONE_UNLESS_NEW_MARKET_EVIDENCE'})
    queue.append({'family':'PLAYER_ACQUISITION','state':'CAPTURE_REQUIRED_MARKET_DRIFT' if market_drift else
                  'NATIVE_'+str(statuses['player_waiver_free_agent']),
                  'next_step':'NEW_CAPTURE_AND_AFFECTED_CHANNEL_EVALUATION' if market_drift else 'NONE'})
    queue.append({'family':'TRADES','state':trade_state,'native_actionable_offer_counts':trade_count,
                  'next_step':'COMPLETE_BOTH_MANAGER_LEGALITY_FILLS_BEHAVIOR_AND_APP_VALIDATION'})
    queue.append({'family':'IR','state': 'CAPTURE_REQUIRED_OWNED_DRIFT' if any(owned[k] for k in ('added','removed','changed'))
                  else 'NATIVE_'+str(statuses['ir_reserve_open_slot_injury_replacement']), 'next_step':'NONE'})
    # A future availability check is an explicit operator requirement, NOT an
    # installed scheduler or a fresh prediction. Never backdate a pre-lock check.
    candidate_kickoffs=[utc(x.get('kickoff_utc')) for x in swaps
                        if x.get('direction')=='START' and x.get('state')=='PENDING_INJURY_STATUS']
    candidate_kickoffs=[x for x in candidate_kickoffs if x is not None and x>now]
    next_check_utc=(max(now,min(candidate_kickoffs)-timedelta(minutes=90)).isoformat()
                    if candidate_kickoffs else None)
    # The output cannot authorize any roster-wide state while live material drift remains.
    return {'week':rec.get('week'),'season':rec.get('season'),'native_overall':rec.get('overall_state'),
            'operator_state':'SCOPED_REVIEW_REQUIRED' if not any(owned[k] for k in ('added','removed','changed'))
                else 'CAPTURE_REQUIRED_OWNED_DRIFT',
            'channel_statuses':statuses,
            'lineup_state':lineup_state,'next_check_utc':next_check_utc,
            'queue':queue,
            'live_drift':{'owned':{k:owned[k] for k in ('added','removed','changed')},
              'market':{k:mkt[k] for k in ('added','removed','changed')},
              'market_affected_positions':changed_market_positions,
              'partner_state_changed':partner_drift,'transactions':transactions,'settings':settings},
            'action_authority':'NONE','espn_writes':False}

def run(root:Path, *, now:datetime | None=None, fetch=None, runtime_guard=None,
        verify_capture=None, canonical=None, memory_guard=None) -> dict:
    now=now or datetime.now(timezone.utc)
    require(root.name.casefold()=='fantasy_football','WRONG_CONTROL_ROOT')
    runtime=root/'fantasy_season_v0_36_repack1'
    if runtime_guard is None:
        sys.path.insert(0,str(root/'tools/operations'))
        from guarded_weekly_cycle import validate_root
        runtime=validate_root(root)
    else:
        runtime=runtime_guard(root)
    if memory_guard is None:
        cmd=[sys.executable,'-B',str(root/'tools/check_memory_health.py'),
             '--root',str(root),'--strict','--json']
        try:
            result=subprocess.run(cmd,capture_output=True,text=True,check=False,timeout=120)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise Blocked('STRICT_MEMORY_HEALTH_UNAVAILABLE') from exc
        require(result.returncode==0,'STRICT_MEMORY_HEALTH_BLOCKED')
        try:
            health=json.loads(result.stdout)
        except ValueError as exc:
            raise Blocked('STRICT_MEMORY_HEALTH_NOT_JSON') from exc
        require(health.get('healthy') is True and not health.get('issues'),
                'STRICT_MEMORY_HEALTH_NOT_HEALTHY')
    else:
        memory_guard(root)
    if verify_capture is None or canonical is None:
        sys.path.insert(0,str(runtime))
        from src.prospective_measurement_v034 import canonical_sha256,verify_capture_integrity
        verify_capture=verify_capture or verify_capture_integrity
        canonical=canonical or canonical_sha256
    snapshot,capture,receipt,ids=discover(runtime,now,verify_capture=verify_capture,canonical=canonical)
    if fetch is None:
        from src.data_sources.secrets import load_espn_secrets
        from src.data_sources.espn_league import (fetch_private_league,fetch_available_players,
                        normalize_league,normalize_available_players)
        # Same private local secret resolver as the validated Thursday runner.
        from pathlib import Path as _Path
        secret_candidates=[root/'config/secrets.json',runtime/'config/secrets.json']
        options=[p for p in secret_candidates if p.is_file()]
        require(bool(options),'LOCAL_ESPN_SECRETS_MISSING')
        sec=load_espn_secrets(options[0])
        season,week=ids['season'],ids['week']
        def fetch():
            raw=fetch_private_league(sec,scoring_period_id=week)
            av=fetch_available_players(sec,scoring_period_id=week)
            return normalize_league(raw,season,week),normalize_available_players(av,season,week)
    live,market=fetch()
    outcome=decide(snapshot,capture,receipt,live,market,now=now)
    outcome['provenance']=ids
    return outcome

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',default='.')
    args=ap.parse_args(argv)
    print('WEEKLY OPERATOR PERMANENT READONLY DECISION TRIAGE',flush=True)
    print('ESPN_GETS=2;NO_MC_OR_CAPTURE_OR_ESPN_WRITE=TRUE',flush=True)
    try:
        result=run(Path(args.project_root).resolve())
        for key in ('operator_state','week','native_overall','lineup_state','next_check_utc','channel_statuses','queue','live_drift','provenance'):
            print(key.upper()+'='+json.dumps(result[key],sort_keys=True,ensure_ascii=True,separators=(',',':')),flush=True)
        print('NEXT_OPERATOR_STEP=REVIEW_SCOPED_QUEUE_AND_RECHECK_AFFECTED_STATE',flush=True)
        print('ESPN_ACTION_AUTHORITY=NONE;ESPN_WRITES=NONE',flush=True)
        return 0
    except Blocked as exc:
        print('WEEKLY_OPERATOR_BLOCKED='+str(exc),flush=True)
    except Exception as exc:
        print('WEEKLY_OPERATOR_BLOCKED_EXCEPTION_TYPE='+type(exc).__name__,flush=True)
    print('ESPN_ACTION_AUTHORITY=NONE;ESPN_WRITES=NONE',flush=True)
    return 3

if __name__=='__main__':
    raise SystemExit(main())
