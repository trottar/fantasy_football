"""M1b pre-refresh live owner/lock diagnostic; never starts refresh/capture/MC.

Read one public NFL calendar and one authenticated ESPN league roster, retain
private responses in memory only, and compare live ownership/locks to the
immutable prior snapshot and independently corroborated schedule. Passing
this diagnostic does not authorize a refresh or transaction: exact league
waiver/trade cutoffs and protected orchestration are separate unfinished gates.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from weekly_operator_calendar_evidence import (
    OFFICIAL_2026_BYES, TEAMS, compare as frozen_calendar_compare,
    independent_schedule, norm, public_scoreboard,
)
from weekly_operator_lock_preflight import kickoff, utc

MAX_PUBLIC_AGE_SECONDS = 120
MAX_LIVE_AGE_SECONDS = 60
MINIMUM_MC_LEAD_MINUTES = 80
POSITIONS = frozenset(('QB', 'RB', 'WR', 'TE', 'DST', 'K'))
# Exact normalized fields actually used by the published read-only reviewer.
OWNED_STATE_FIELDS = (
    'on_team_id', 'position', 'nfl_team', 'lineup_slot_id', 'lineup_slot',
    'lineup_locked', 'injury_status', 'active', 'eligible_slots', 'droppable',
)


class Blocked(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Blocked(code)


def _utc_time(dt: datetime, label: str) -> datetime:
    need(isinstance(dt, datetime) and dt.tzinfo is not None, label)
    return dt.astimezone(timezone.utc)


def _owner(teams: Any, name: str) -> dict:
    need(isinstance(teams, list), 'LIVE_OR_FROZEN_TEAMS_INVALID')
    found = [t for t in teams if isinstance(t, dict) and t.get('name') == name]
    need(len(found) == 1 and isinstance(found[0].get('roster'), list),
         'OWNED_TEAM_UNRESOLVED')
    return found[0]


def _indexed_roster(roster: list, label: str) -> dict[int, dict]:
    need(roster and isinstance(roster, list), 'EMPTY_OR_INVALID_' + label)
    out: dict[int, dict] = {}
    for asset in roster:
        need(isinstance(asset, dict), 'INVALID_ASSET_' + label)
        pid = asset.get('espn_id')
        need(type(pid) is int and pid not in out, 'DUPLICATE_OR_MISSING_ID_' + label)
        need(asset.get('position') in POSITIONS, 'INVALID_POSITION_' + label)
        need(norm(asset.get('nfl_team')) in TEAMS, 'UNKNOWN_NFL_TEAM_' + label)
        out[pid] = asset
    return out


def classify(frozen: dict, league: dict, scoreboard: dict, live: dict, *,
             now: datetime, public_fetched_at: datetime,
             live_fetched_at: datetime, week: int) -> dict:
    """Pure sanitized aggregate; no secret, player ID, names or raw live JSON."""
    now = _utc_time(now, 'NAIVE_NOW')
    pubtime = _utc_time(public_fetched_at, 'NAIVE_PUBLIC_TIME')
    livetime = _utc_time(live_fetched_at, 'NAIVE_LIVE_TIME')
    need(pubtime <= livetime <= now, 'FETCH_CHRONOLOGY_INVALID')
    need(0 <= (now - pubtime).total_seconds() <= MAX_PUBLIC_AGE_SECONDS,
         'PUBLIC_FETCH_TOO_OLD')
    need(0 <= (now - livetime).total_seconds() <= MAX_LIVE_AGE_SECONDS,
         'LIVE_ROSTER_FETCH_TOO_OLD')
    need(isinstance(frozen, dict) and isinstance(league, dict)
         and isinstance(live, dict), 'INPUT_NOT_OBJECT')
    # Reuse the accepted first-lock source comparison instead of rewriting it.
    try:
        previous = frozen_calendar_compare(frozen, league, scoreboard, now=now, week=week)
        games = independent_schedule(scoreboard, season=2026, week=week)
    except ValueError as exc:
        # Discard internal details of future backend exceptions by returning only
        # this fixed code to the calling boundary.
        raise Blocked('INDEPENDENT_CALENDAR_NOT_CORROBORATED') from exc
    frozen_espn = frozen.get('espn') or {}
    need(live.get('season') == 2026 and live.get('week') == week == frozen_espn.get('week'),
         'LIVE_ESPN_EPOCH_MISMATCH')
    need(type(live.get('league_id')) is int and live.get('league_id') == frozen_espn.get('league_id'),
         'LIVE_LEAGUE_ID_MISMATCH')
    name = league.get('user_team_name')
    need(isinstance(name, str) and bool(name.strip()), 'OWNER_CONFIG_MISSING')
    ft = _owner(frozen_espn.get('teams'), name)
    lt = _owner(live.get('teams'), name)
    need(type(ft.get('team_id')) is int and ft.get('team_id') == lt.get('team_id'),
         'LIVE_OWNER_TEAM_ID_MISMATCH')
    prior = _indexed_roster(ft['roster'], 'FROZEN_ROSTER')
    current = _indexed_roster(lt['roster'], 'LIVE_ROSTER')
    added = set(current) - set(prior)
    removed = set(prior) - set(current)
    changed = {pid for pid in set(prior) & set(current)
               if any(prior[pid].get(field) != current[pid].get(field)
                      for field in OWNED_STATE_FIELDS)}
    # Frozen nflverse schedule is retained as a consistency constraint even
    # when the owner roster changed after Thursday's prospective capture.
    nflverse = (frozen.get('matchup_context') or {}).get('team_week')
    need(isinstance(nflverse, dict), 'FROZEN_NFLVERSE_INVALID')
    future: list[datetime] = []
    elapsed = explicit_locked = unknown = confirmed = byes = 0
    for asset in current.values():
        team = norm(asset.get('nfl_team'))
        row = nflverse.get(team)
        match = row.get(str(week)) if isinstance(row, dict) else None
        if team not in games:
            need(OFFICIAL_2026_BYES.get(team) == week and match is None,
                 'LIVE_BYE_VS_NFLVERSE_DISAGREEMENT')
            byes += 1
            continue
        need(isinstance(match, dict), 'LIVE_TEAM_FROZEN_MATCHUP_MISSING')
        when = kickoff(match)
        need(when is not None and when == games[team][1] and
             norm(match.get('opponent')) == games[team][0],
             'LIVE_TEAM_PUBLIC_NFLVERSE_DISAGREEMENT')
        confirmed += 1
        lock = asset.get('lineup_locked')
        if when <= now:
            elapsed += 1
        elif lock is True:
            explicit_locked += 1
        elif lock is False:
            future.append(when)
        else:
            unknown += 1
    need(byes + confirmed == len(current), 'LIVE_OWNED_CALENDAR_INCOMPLETE')
    first = min(future) if future else None
    snapshot_age = previous['snapshot_age_seconds']
    if unknown:
        status = 'BLOCKED_UNKNOWN_LIVE_LOCK'
    elif first is None:
        status = 'BLOCKED_NO_FUTURE_UNLOCKED_OWNED_GAME'
    elif first - now <= timedelta(minutes=MINIMUM_MC_LEAD_MINUTES):
        status = 'BLOCKED_INSUFFICIENT_PROTECTED_LEAD'
    elif added or removed or changed:
        status = 'READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED'
    elif elapsed or explicit_locked:
        status = 'READONLY_PARTIAL_SCOPE_CALENDAR_LOCK_CORROBORATED'
    else:
        status = 'READONLY_LIVE_CALENDAR_LOCK_CORROBORATED'
    return {
        'phase': 'M1B_PRE_REFRESH_LIVE_OWNED_LOCK_READONLY',
        'status': status, 'season': 2026, 'week': week,
        'snapshot_age_seconds': snapshot_age,
        'frozen_snapshot_stale': snapshot_age >= 7200,
        'live_roster_check_age_seconds': round((now - livetime).total_seconds()),
        'public_calendar_check_age_seconds': round((now - pubtime).total_seconds()),
        'frozen_owned_records': len(prior), 'live_owned_records': len(current),
        'owned_added': len(added), 'owned_removed': len(removed),
        'owned_changed': len(changed),
        'live_game_records': confirmed, 'live_bye_records': byes,
        'elapsed_game_records': elapsed, 'explicit_locked_future_records': explicit_locked,
        'unknown_live_lock_records': unknown,
        'future_unlocked_records': len(future),
        'earliest_future_unlocked_kickoff_utc': first.isoformat() if first else None,
        'minimum_planning_lead_minutes': MINIMUM_MC_LEAD_MINUTES,
        'calendar_corrob_source': 'PUBLIC_ESPN_SCOREBOARD_PLUS_PUBLISHED_NFL_BYES_PLUS_FROZEN_NFLVERSE',
        'fresh_authenticated_espn_gets': 1,
        'market_and_claim_cutoffs_verified': False,
        'refresh_authority': 'NONE', 'capture_authority': 'NONE',
        'action_authority': 'NONE', 'automatic_refresh_or_capture': False,
        'native_mc_started': False, 'espn_writes': False,
    }


def run(root: Path, *, week: int, now: datetime | None = None,
        calendar_fetch=None, league_fetch=None) -> dict:
    """One public and one private ESPN GET, no persistence or modifying call."""
    need(root.name.casefold() == 'fantasy_football', 'WRONG_CONTROL_ROOT')
    # Reuse commissioned runtime sentinel. No modification of installed files.
    from guarded_weekly_cycle import validate_root
    runtime = validate_root(root)
    latest = runtime / 'data/season_snapshots/latest.json'
    raw = latest.read_bytes()
    frozen = json.loads(raw.decode('utf-8-sig'))
    need(isinstance(frozen, dict), 'FROZEN_SNAPSHOT_NOT_OBJECT')
    base = runtime / 'data/season_snapshots'
    matches = [p for p in base.glob('*/snapshot.json') if p.is_file() and p.read_bytes() == raw]
    need(len(matches) == 1, 'FROZEN_SNAPSHOT_EXACT_IDENTITY_INVALID')
    league = json.loads((runtime / 'config/league.json').read_text(encoding='utf-8-sig'))
    need(isinstance(league, dict), 'LEAGUE_CONFIG_INVALID')
    need(league.get('season') == 2026 and (frozen.get('espn') or {}).get('week') == week,
         'FROZEN_REQUEST_WEEK_MISMATCH')
    if calendar_fetch is None:
        calendar_fetch = lambda: public_scoreboard(season=2026, week=week)[0]
    public = calendar_fetch()
    public_time = datetime.now(timezone.utc)
    if league_fetch is None:
        sys.path.insert(0, str(runtime))
        from src.data_sources.secrets import load_espn_secrets
        from src.data_sources.espn_league import fetch_private_league, normalize_league
        paths = (root / 'config/secrets.json', runtime / 'config/secrets.json')
        candidates = [p for p in paths if p.is_file()]
        need(bool(candidates), 'LOCAL_ESPN_SECRETS_NOT_FOUND')
        sec = load_espn_secrets(candidates[0])
        need(sec.season == 2026 and sec.league_id == (frozen.get('espn') or {}).get('league_id'),
             'AUTHENTICATED_CONFIG_IDENTITY_MISMATCH')
        def league_fetch():
            payload = fetch_private_league(sec, scoring_period_id=week)
            need(payload.get('id') == sec.league_id and
                 payload.get('seasonId', 2026) == 2026,
                 'RAW_ESPN_IDENTITY_MISMATCH')
            if payload.get('scoringPeriodId') is not None:
                need(payload['scoringPeriodId'] == week, 'RAW_ESPN_SCORING_PERIOD_MISMATCH')
            return normalize_league(payload, season=2026, week=week)
    live = league_fetch()
    live_time = datetime.now(timezone.utc)
    result = classify(frozen, league, public, live,
                      now=(now or datetime.now(timezone.utc)),
                      public_fetched_at=public_time,
                      live_fetched_at=live_time, week=week)
    result['frozen_snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default='.')
    p.add_argument('--week', type=int, required=True)
    args = p.parse_args(argv)
    print('WEEKLY OPERATOR M1B PRE-REFRESH LIVE LOCK READONLY PROBE', flush=True)
    try:
        result = run(Path(args.project_root).resolve(), week=args.week)
        print('LIVE_LOCK_RESULT=' + json.dumps(result, sort_keys=True, separators=(',', ':')), flush=True)
        print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;REFRESH_AUTHORITY=NONE', flush=True)
        return 0
    except Blocked as exc:
        print('LIVE_LOCK_BLOCKED=' + str(exc), flush=True)
    except Exception as exc:
        # Do not print backend exceptions: private URLs, cookies, IDs or payloads
        # might be present in exception messages.
        print('LIVE_LOCK_BLOCKED_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;REFRESH_AUTHORITY=NONE', flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
