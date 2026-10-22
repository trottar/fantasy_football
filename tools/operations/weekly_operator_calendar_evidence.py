"""M1b independent public calendar comparison: observational only.

One public unauthenticated ESPN scoreboard GET, a source-attributed *published*
NFL 2026 bye table, and the frozen nflverse matchup/owned snapshot. No sync,
MC, capture, authenticated ESPN GET/POST, private evidence write or action gate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
from urllib.request import Request, urlopen

from weekly_operator_lock_preflight import PROVIDERS, kickoff, utc

NFL_2026_BYES_URL = 'https://www.nfl.com/_amp/2026-nfl-schedule-release-every-team-bye-week'
# Source: NFL's published 2026 team-by-team bye-week schedule (fixed season
# calendar, not claimed to have been fetched live on each invocation).
OFFICIAL_2026_BYES = {
    'CAR': 5, 'KC': 5,
    'CIN': 6, 'DET': 6, 'MIA': 6, 'MIN': 6,
    'BUF': 7, 'JAX': 7, 'LAC': 7, 'WSH': 7,
    'HOU': 8, 'NO': 8, 'NYG': 8, 'SF': 8,
    'PIT': 9, 'TEN': 9,
    'CHI': 10, 'DEN': 10, 'PHI': 10, 'TB': 10,
    'ATL': 11, 'CLE': 11, 'GB': 11, 'LAR': 11, 'NE': 11, 'SEA': 11,
    'BAL': 13, 'IND': 13, 'LV': 13, 'NYJ': 13,
    'ARI': 14, 'DAL': 14,
}
TEAMS = frozenset(OFFICIAL_2026_BYES)
ESPN_ALIASES = {'WSH': 'WSH', 'WAS': 'WSH', 'JAC': 'JAX', 'LA': 'LAR', 'STL': 'LAR', 'OAK': 'LV', 'SD': 'LAC'}
MAX_AGE_SECONDS = 7200
MIN_LEAD = timedelta(minutes=80)
MAX_SCOREBOARD_BYTES = 2_000_000


class Blocked(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Blocked(reason)


def norm(team: Any) -> str:
    v = str(team or '').strip().upper()
    return ESPN_ALIASES.get(v, v)


def independent_schedule(data: dict, *, season: int, week: int) -> dict[str, tuple[str, datetime]]:
    """All 32 NFL clubs must be accounted for exactly once (game or bye)."""
    require(isinstance(data, dict), 'PUBLIC_SCOREBOARD_INVALID')
    require((data.get('season') or {}).get('year') == season and
            (data.get('season') or {}).get('type') == 2 and
            (data.get('week') or {}).get('number') == week, 'PUBLIC_SCOREBOARD_EPOCH_MISMATCH')
    events = data.get('events')
    require(isinstance(events, list) and events, 'PUBLIC_SCOREBOARD_EVENTS_MISSING')
    byes = {team for team, wk in OFFICIAL_2026_BYES.items() if wk == week}
    require(len(events) == (len(TEAMS) - len(byes)) // 2, 'PUBLIC_SCOREBOARD_GAME_COUNT_MISMATCH')
    games: dict[str, tuple[str, datetime]] = {}
    event_ids: set[str] = set()
    for event in events:
        require(isinstance(event, dict), 'PUBLIC_SCOREBOARD_EVENT_INVALID')
        eid = str(event.get('id') or '')
        require(bool(eid) and eid not in event_ids, 'PUBLIC_SCOREBOARD_EVENT_ID_DUPLICATE_OR_MISSING')
        event_ids.add(eid)
        require((event.get('season') or {}).get('year') == season and
                (event.get('season') or {}).get('type') == 2 and
                (event.get('week') or {}).get('number') == week,
                'PUBLIC_EVENT_EPOCH_MISMATCH')
        when = utc(event.get('date'))
        require(when is not None, 'PUBLIC_KICKOFF_UNRESOLVED')
        comps = event.get('competitions')
        require(isinstance(comps, list) and len(comps) == 1, 'PUBLIC_COMPETITION_INVALID')
        sides = comps[0].get('competitors') if isinstance(comps[0], dict) else None
        require(isinstance(sides, list) and len(sides) == 2, 'PUBLIC_COMPETITORS_INVALID')
        team_sides = {}
        for side in sides:
            require(isinstance(side, dict) and side.get('homeAway') in ('home', 'away'),
                    'PUBLIC_HOME_AWAY_INVALID')
            name = norm((side.get('team') or {}).get('abbreviation'))
            require(name in TEAMS and name not in games and
                    side['homeAway'] not in team_sides, 'PUBLIC_TEAM_DUPLICATE_OR_UNKNOWN')
            team_sides[side['homeAway']] = name
        require(set(team_sides) == {'home', 'away'}, 'PUBLIC_OPPONENT_PAIR_INVALID')
        home, away = team_sides['home'], team_sides['away']
        require(home != away, 'PUBLIC_SELF_GAME_INVALID')
        games[home] = (away, when)
        games[away] = (home, when)
    require(set(games) == TEAMS - byes, 'PUBLIC_SCOREBOARD_LEAGUE_COVERAGE_MISMATCH')
    return games


def compare(snapshot: dict, league: dict, calendar: dict, *, now: datetime, week: int) -> dict:
    require(now.tzinfo is not None, 'NAIVE_NOW_FORBIDDEN')
    now = now.astimezone(timezone.utc)
    require(isinstance(snapshot, dict) and isinstance(league, dict), 'LOCAL_INPUT_INVALID')
    stamp = utc(snapshot.get('snapshot_utc'))
    require(stamp is not None and stamp <= now, 'FROZEN_SNAPSHOT_CHRONOLOGY_INVALID')
    espn = snapshot.get('espn')
    require(isinstance(espn, dict) and espn.get('season') == 2026 and espn.get('week') == week
            and league.get('season') == 2026 and 1 <= week <= 18, 'LOCAL_EPOCH_MISMATCH')
    source = snapshot.get('source_status')
    require(isinstance(source, dict), 'FROZEN_SOURCE_HEALTH_MISSING')
    for provider in PROVIDERS:
        row = source.get(provider)
        healthy = ((row.get('complete') if row.get('complete') is not None else row.get('ok'))
                   if provider == 'nfl_official_rosters' and isinstance(row, dict)
                   else row.get('ok') if isinstance(row, dict) else None)
        require(healthy is True, 'FROZEN_PROVIDER_HEALTH_BLOCKED:' + provider)
    games = independent_schedule(calendar, season=2026, week=week)
    team_name = league.get('user_team_name')
    require(isinstance(team_name, str) and team_name.strip(), 'LOCAL_OWNED_TEAM_NAME_MISSING')
    matches = [t for t in espn.get('teams', []) if isinstance(t, dict) and
               t.get('name') == team_name]
    require(len(matches) == 1, 'FROZEN_OWNED_TEAM_AMBIGUOUS')
    roster = matches[0].get('roster')
    require(isinstance(roster, list) and roster, 'FROZEN_ROSTER_INVALID')
    league_byes = league.get('bye_weeks_2026')
    require(isinstance(league_byes, dict), 'LEAGUE_BYES_MISSING')
    # Do not silently accept wrong current-week configured byes (including
    # missing entries for an NFL-official bye).
    for team in TEAMS:
        require(league_byes.get(team) == OFFICIAL_2026_BYES[team] if team in league_byes else
                team not in OFFICIAL_2026_BYES,
                'LEAGUE_OFFICIAL_BYE_TABLE_DISAGREEMENT')
    frozen_games = ((snapshot.get('matchup_context') or {}).get('team_week') or {})
    require(isinstance(frozen_games, dict) and frozen_games, 'FROZEN_NFLVERSE_SCHEDULE_MISSING')
    seen = set()
    known = bye_count = locked = 0
    future = []
    for asset in roster:
        require(isinstance(asset, dict) and isinstance(asset.get('espn_id'), int)
                and not isinstance(asset['espn_id'], bool) and asset['espn_id'] not in seen,
                'OWNED_ASSET_ID_INVALID')
        seen.add(asset['espn_id'])
        require(asset.get('position') in ('QB', 'RB', 'WR', 'TE', 'DST', 'K'), 'OWNED_POSITION_INVALID')
        team = norm(asset.get('nfl_team'))
        require(team in TEAMS, 'OWNED_NFL_TEAM_UNRESOLVED')
        row = frozen_games.get(team)
        fg = row.get(str(week)) if isinstance(row, dict) else None
        if team in games:
            require(isinstance(fg, dict), 'FROZEN_GAME_MISSING_FOR_PUBLIC_GAME')
            kt = kickoff(fg)
            require(kt is not None, 'FROZEN_KICKOFF_MALFORMED')
            opponent = norm(fg.get('opponent'))
            require(opponent == games[team][0] and kt == games[team][1],
                    'INDEPENDENT_NFLVERSE_GAME_OR_KICKOFF_DISAGREEMENT')
            known += 1
            if asset.get('lineup_locked') is True or kt <= now:
                locked += 1
            else:
                future.append(kt)
        else:
            require(team in OFFICIAL_2026_BYES and OFFICIAL_2026_BYES[team] == week,
                    'PUBLIC_GAME_MISSING_NON_BYE')
            require(fg is None, 'FROZEN_GAME_FOR_OFFICIAL_BYE')
            bye_count += 1
    require(known + bye_count == len(roster), 'OWNED_CALENDAR_COVERAGE_INCOMPLETE')
    age = round((now - stamp).total_seconds())
    first = min(future) if future else None
    if age >= MAX_AGE_SECONDS:
        status = 'CORROBORATED_CALENDAR_STALE_FROZEN_ROSTER'
    elif first is None:
        status = 'CORROBORATED_CALENDAR_NO_FUTURE_OWNED_LOCK'
    elif first - now <= MIN_LEAD:
        status = 'CORROBORATED_CALENDAR_INSUFFICIENT_PLANNING_LEAD'
    else:
        status = 'CORROBORATED_CALENDAR_LIVE_OWNED_ROSTER_STILL_REQUIRED'
    return {'phase': 'M1B_INDEPENDENT_PUBLIC_CALENDAR_READONLY',
            'status': status, 'season': 2026, 'week': week,
            'independent_game_source': 'PUBLIC_ESPN_SCOREBOARD',
            'published_bye_source': NFL_2026_BYES_URL,
            'league_games': len(games) // 2,
            'league_bye_teams': len(TEAMS - set(games)),
            'owned_records': len(roster), 'corroborated_kickoff_records': known,
            'corroborated_bye_records': bye_count, 'locked_or_elapsed_records': locked,
            'earliest_future_owned_kickoff_utc': first.isoformat() if first else None,
            'snapshot_utc': stamp.isoformat(), 'snapshot_age_seconds': age,
            'minimum_planning_lead_minutes': 80,
            'live_owned_roster_freshness_confirmed': False,
            'refresh_authority': 'NONE', 'capture_authority': 'NONE',
            'action_authority': 'NONE', 'native_mc_started': False,
            'espn_authenticated_access': False, 'espn_writes': False}


def public_scoreboard(*, season: int, week: int) -> tuple[dict, str]:
    require(season == 2026 and 1 <= week <= 18, 'PUBLIC_CALENDAR_EPOCH_UNSUPPORTED')
    url = ('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
           f'?week={week}&seasontype=2&season={season}')
    request = Request(url, headers={'Accept': 'application/json',
                                    'User-Agent': 'fantasy-football-calendar-readonly/1.0',
                                    'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=25) as response:
        require(response.status == 200, 'PUBLIC_SCOREBOARD_HTTP_NOT_OK')
        raw = response.read(MAX_SCOREBOARD_BYTES + 1)
    require(0 < len(raw) <= MAX_SCOREBOARD_BYTES, 'PUBLIC_SCOREBOARD_BODY_SIZE_INVALID')
    obj = json.loads(raw.decode('utf-8'))
    require(isinstance(obj, dict), 'PUBLIC_SCOREBOARD_JSON_INVALID')
    return obj, hashlib.sha256(raw).hexdigest()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default='.')
    p.add_argument('--week', required=True, type=int)
    args = p.parse_args(argv)
    print('WEEKLY OPERATOR M1B INDEPENDENT CALENDAR SOURCE PROBE', flush=True)
    try:
        root = Path(args.project_root).resolve()
        require(root.name.casefold() == 'fantasy_football', 'WRONG_PROJECT_ROOT')
        from guarded_weekly_cycle import validate_root
        runtime = validate_root(root)
        latest = runtime / 'data/season_snapshots/latest.json'
        raw = latest.read_bytes()
        frozen = json.loads(raw.decode('utf-8-sig'))
        require(isinstance(frozen, dict), 'FROZEN_SNAPSHOT_INVALID')
        base = runtime / 'data/season_snapshots'
        matches = [p for p in base.glob('*/snapshot.json') if p.is_file() and p.read_bytes() == raw]
        require(len(matches) == 1, 'FROZEN_SNAPSHOT_EXACT_COPY_AMBIGUOUS')
        league = json.loads((runtime / 'config/league.json').read_text(encoding='utf-8-sig'))
        # One public schedule GET only; no authenticated/private ESPN requests.
        public, source_sha = public_scoreboard(season=2026, week=args.week)
        outcome = compare(frozen, league, public, now=datetime.now(timezone.utc), week=args.week)
        outcome['frozen_snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
        outcome['public_scoreboard_sha256'] = source_sha
        print('CALENDAR_RESULT=' + json.dumps(outcome, sort_keys=True, separators=(',', ':')), flush=True)
        print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
        return 0  # classification is evidence; no automatic authority on success.
    except (Blocked, OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print('CALENDAR_BLOCKED=' + type(exc).__name__ + ':' + str(exc) if isinstance(exc, Blocked)
              else 'CALENDAR_BLOCKED_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    except Exception as exc:
        print('CALENDAR_BLOCKED_EXCEPTION_TYPE=' + type(exc).__name__, flush=True)
    print('NO_SYNC_CAPTURE_OR_MC=TRUE;NO_ESPN_WRITES=TRUE;ACTION_AUTHORITY=NONE', flush=True)
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
