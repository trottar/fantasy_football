"""M1b first-lock inventory on a *previously frozen* six-provider snapshot.

Read-only and fail-closed. This does not refresh providers, produce prospective
captures, launch MC, or authorize ESPN actions. Latest.json is *not* a fresh
source merely because it is called "latest"; age and exact immutable identity
must be checked by the caller and by this preflight.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROVIDERS = ('espn', 'sleeper', 'nflverse_rosters', 'nflverse_matchups',
             'nfl_official_rosters', 'nfl_official')
EASTERN = ZoneInfo('America/New_York')
MINIMUM_LEAD_MINUTES = 80
MAX_SNAPSHOT_AGE_SECONDS = 7200


class Blocked(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Blocked(reason)


def utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc) if dt.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def kickoff(game: Any) -> datetime | None:
    if not isinstance(game, dict):
        return None
    day, tm = game.get('gameday'), game.get('gametime')
    if not isinstance(day, str) or not isinstance(tm, str):
        return None
    for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %I:%M%p', '%Y-%m-%d %I:%M %p'):
        try:
            dt = datetime.strptime(day.strip() + ' ' + tm.strip(), fmt)
            return dt.replace(tzinfo=EASTERN).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def classify(snapshot: dict[str, Any], league: dict[str, Any], *, now: datetime,
             week: int | None = None) -> dict[str, Any]:
    """Only aggregate public-safe state is returned; no player/league IDs."""
    require(now.tzinfo is not None, 'NAIVE_NOW_FORBIDDEN')
    now = now.astimezone(timezone.utc)
    stamp = utc(snapshot.get('snapshot_utc'))
    require(stamp is not None and stamp <= now, 'SNAPSHOT_CHRONOLOGY_INVALID')
    age = (now - stamp).total_seconds()
    espn = snapshot.get('espn')
    require(isinstance(espn, dict), 'ESPN_SNAPSHOT_MISSING')
    try:
        season, wk = int(espn['season']), int(espn['week'])
    except (ValueError, KeyError, TypeError) as exc:
        raise Blocked('SCHEDULE_EPOCH_UNRESOLVED') from exc
    require(1 <= wk <= 18 and (week is None or wk == week), 'WEEK_NOT_CURRENT')
    require(season == league.get('season'), 'LEAGUE_SEASON_MISMATCH')
    source = snapshot.get('source_status')
    require(isinstance(source, dict), 'SOURCE_HEALTH_MISSING')
    for provider in PROVIDERS:
        state = source.get(provider)
        healthy = (state.get('complete') if provider == 'nfl_official_rosters'
                   and state.get('complete') is not None else state.get('ok')) if isinstance(state, dict) else None
        require(healthy is True, 'SIX_PROVIDER_HEALTH_BLOCKED:' + provider)
    context = snapshot.get('matchup_context')
    teams_games = (context or {}).get('team_week') if isinstance(context, dict) else None
    require(isinstance(teams_games, dict) and teams_games, 'NFLVERSE_TEAM_WEEK_SCHEDULE_MISSING')
    team_name = league.get('user_team_name')
    require(isinstance(team_name, str) and team_name.strip(), 'OWNED_TEAM_NAME_MISSING')
    matches = [t for t in (espn.get('teams') or []) if isinstance(t, dict)
               and str(t.get('name') or '').strip() == team_name.strip()]
    require(len(matches) == 1, 'OWNED_TEAM_NAME_UNRESOLVED_OR_AMBIGUOUS')
    roster = matches[0].get('roster')
    require(isinstance(roster, list) and roster, 'OWNED_ROSTER_MISSING')
    byes = league.get('bye_weeks_2026')
    require(isinstance(byes, dict), 'CONFIGURED_BYES_MISSING')
    seen = set()
    known, future_unlocked, unknown, configured_byes, locked, positions = [], [], 0, 0, 0, {}
    for row in roster:
        require(isinstance(row, dict), 'INVALID_ROSTER_ROW')
        pid = row.get('espn_id')
        require(isinstance(pid, int) and not isinstance(pid, bool) and pid not in seen,
                'ROSTER_PLAYER_ID_MISSING_OR_DUPLICATED')
        seen.add(pid)
        pos = str(row.get('position') or '').upper()
        team = str(row.get('nfl_team') or '').upper()
        require(pos in {'QB', 'RB', 'WR', 'TE', 'DST', 'K'}, 'ROSTER_POSITION_INVALID')
        positions[pos] = positions.get(pos, 0) + 1
        mapping = teams_games.get(team)
        game = mapping.get(str(wk)) if isinstance(mapping, dict) else None
        dt = kickoff(game)
        if dt is None:
            if game is None and byes.get(team) == wk:
                configured_byes += 1
                # This is a configured bye, NOT independently confirmed by
                # the nflverse game map. Never claim known lock coverage.
            else:
                unknown += 1
            continue
        # An ESPN true lock outranks an inferred future kickoff.
        if row.get('lineup_locked') is True or dt <= now:
            locked += 1
        else:
            future_unlocked.append(dt)
        known.append(dt)
    upcoming = sorted(future_unlocked)
    first = min(known).isoformat() if known else None
    first_future = upcoming[0].isoformat() if upcoming else None
    enough_lead = bool(upcoming) and (upcoming[0] - now).total_seconds() > MINIMUM_LEAD_MINUTES * 60
    if age >= MAX_SNAPSHOT_AGE_SECONDS:
        status = 'BLOCKED_STALE_SNAPSHOT'
    elif unknown or configured_byes:
        status = 'BLOCKED_UNVERIFIED_OWNED_LOCK_OR_BYE'
    elif not upcoming:
        status = 'BLOCKED_NO_FUTURE_OWNED_LOCK'
    elif not enough_lead:
        status = 'BLOCKED_INSUFFICIENT_LEAD'
    elif locked:
        status = 'READONLY_PARTIAL_SCOPE_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY'
    else:
        status = 'READONLY_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY'
    return {
        'phase': 'M1B_FIRST_LOCK_READONLY_PREFLIGHT', 'week': wk, 'season': season,
        'status': status, 'source': 'FROZEN_SIX_PROVIDER_SNAPSHOT_NFLVERSE_MATCHUPS',
        'snapshot_utc': stamp.isoformat(), 'snapshot_age_seconds': round(age),
        'owned_records': len(roster), 'position_counts': dict(sorted(positions.items())),
        'known_kickoff_records': len(known), 'locked_or_elapsed_records': locked,
        'unknown_lock_records': unknown, 'configured_bye_unverified_records': configured_byes,
        'earliest_owned_lock_utc': first, 'earliest_future_owned_lock_utc': first_future,
        'minimum_lead_minutes': MINIMUM_LEAD_MINUTES, 'native_mc_started': False,
        'automatic_refresh_or_capture': False, 'espn_writes': False,
        'action_authority': 'NONE',
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--week', type=int)
    args = parser.parse_args(argv)
    print('WEEKLY OPERATOR M1B READONLY FIRST LOCK PREFLIGHT', flush=True)
    try:
        root = Path(args.project_root).resolve()
        require(root.name.casefold() == 'fantasy_football', 'WRONG_PROJECT_ROOT')
        runtime = root / 'fantasy_season_v0_36_repack1'
        # Source-bound commissioned runtime validation; do not fall back to an
        # arbitrary installed fantasy version.
        import sys
        sys.path.insert(0, str(root / 'tools' / 'operations'))
        from guarded_weekly_cycle import validate_root
        require(validate_root(root) == runtime, 'RUNTIME_IDENTITY_UNVERIFIED')
        snap_path = runtime / 'data/season_snapshots/latest.json'
        raw = snap_path.read_bytes()
        snap = json.loads(raw.decode('utf-8-sig'))
        require(isinstance(snap, dict), 'SNAPSHOT_JSON_INVALID')
        # Prove latest is an exact copy of one immutable epoch directory.
        folder = runtime / 'data/season_snapshots'
        exact = [p for p in folder.glob('*/snapshot.json') if p.is_file()
                 and p.read_bytes() == raw]
        require(len(exact) == 1, 'IMMUTABLE_SNAPSHOT_IDENTITY_NOT_UNIQUE')
        league = json.loads((runtime / 'config/league.json').read_text(encoding='utf-8-sig'))
        result = classify(snap, league, now=datetime.now(timezone.utc), week=args.week)
        result['snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
        print('PREFLIGHT_RESULT=' + json.dumps(result, sort_keys=True, separators=(',', ':')), flush=True)
        return 0 if result['status'] in ('READONLY_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY',
                                         'READONLY_PARTIAL_SCOPE_TIME_BUDGET_PASS_NOT_ACTION_AUTHORITY') else 2
    except (Blocked, ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
        print('PREFLIGHT_BLOCKED=' + str(exc), flush=True)
    except Exception as exc:
        print('PREFLIGHT_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    print('NO_ESPN_WRITES=TRUE;NO_REFRESH_CAPTURE_OR_MC=TRUE;ACTION_AUTHORITY=NONE', flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
