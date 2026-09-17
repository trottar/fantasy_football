from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests

from .espn import POSITION_MAP, PRO_TEAM_ABBR
from .secrets import EspnSecrets


LINEUP_SLOT_MAP = {
    0: "QB",
    2: "RB",
    4: "WR",
    6: "TE",
    16: "DST",
    17: "K",
    20: "BENCH",
    21: "IR",
    23: "FLEX",
}

DEFAULT_VIEWS = (
    "mSettings",
    "mTeam",
    "mRoster",
    "mMatchup",
    "mStandings",
    "mTransactions2",
)


def league_url(season: int, league_id: int) -> str:
    return (
        "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{int(season)}/segments/0/leagues/{int(league_id)}"
    )


def _cookies(secrets: EspnSecrets) -> dict[str, str]:
    return {"espn_s2": secrets.espn_s2, "SWID": secrets.swid}


def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "fantasy-season-manager/0.22 (personal analytics project)",
    }
    if extra:
        headers.update(extra)
    return headers


def fetch_private_league(
    secrets: EspnSecrets,
    scoring_period_id: int | None = None,
    views: Iterable[str] = DEFAULT_VIEWS,
    timeout: int = 45,
) -> dict[str, Any]:
    params: list[tuple[str, Any]] = []
    if scoring_period_id is not None:
        params.append(("scoringPeriodId", int(scoring_period_id)))
    params.extend(("view", str(v)) for v in views)

    response = requests.get(
        league_url(secrets.season, secrets.league_id),
        params=params,
        cookies=_cookies(secrets),
        headers=_headers(),
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("ESPN private league endpoint returned an unexpected payload")
    return payload


def fetch_available_players(
    secrets: EspnSecrets,
    scoring_period_id: int,
    statuses: tuple[str, ...] = ("FREEAGENT", "WAIVERS"),
    limit: int = 2500,
    timeout: int = 45,
) -> dict[str, Any]:
    fantasy_filter = {
        "players": {
            "filterStatus": {"value": list(statuses)},
            "filterSlotIds": {"value": [0, 2, 4, 6, 16, 17, 23]},
            "filterStatsForExternalIds": {"value": [int(secrets.season)]},
            "filterStatsForSourceIds": {"value": [0, 1]},
            "filterStatsForSplitTypeIds": {"value": [0, 1]},
            # Ask ESPN for current/top scoring-period rows in addition to season totals.
            # The normalizer below still requires an exact requested-week row before
            # calling anything a weekly projection.
            "filterStatsForTopScoringPeriodIds": {
                "value": 5,
                "additionalValue": [f"00{int(secrets.season)}", f"10{int(secrets.season)}"],
            },
            "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
            "limit": int(limit),
            "offset": 0,
        }
    }
    headers = _headers({
        "X-Fantasy-Source": "kona",
        "X-Fantasy-Filter": json.dumps(fantasy_filter, separators=(",", ":")),
    })
    response = requests.get(
        league_url(secrets.season, secrets.league_id),
        params={"scoringPeriodId": int(scoring_period_id), "view": "kona_player_info"},
        cookies=_cookies(secrets),
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("ESPN available-player query returned an unexpected payload")
    return payload


def infer_scoring_period(payload: dict[str, Any], default: int = 1) -> int:
    status = payload.get("status") or {}
    candidates = (
        status.get("currentScoringPeriod"),
        status.get("currentMatchupPeriod"),
        payload.get("scoringPeriodId"),
    )
    for value in candidates:
        try:
            if value is not None and int(value) > 0:
                return int(value)
        except (TypeError, ValueError):
            pass
    return int(default)


def _stat_points(player: dict[str, Any], season: int, week: int, source_id: int) -> float | None:
    """Return points for one *exact* scoring period.

    ESPN player stat arrays mix season aggregates (`statSplitTypeId == 0`) with
    single-scoring-period rows (`statSplitTypeId == 1`).  A season aggregate must
    never be used as a weekly point estimate.
    """
    candidates: list[float] = []
    for stat in player.get("stats") or []:
        if not isinstance(stat, dict):
            continue
        if stat.get("statSourceId") != source_id:
            continue
        season_id = stat.get("seasonId", stat.get("seasonValue"))
        if season_id not in (None, int(season)):
            continue
        if stat.get("statSplitTypeId") != 1:
            continue
        try:
            if int(stat.get("scoringPeriodId")) != int(week):
                continue
        except (TypeError, ValueError):
            continue
        applied = stat.get("appliedTotal", stat.get("appliedStatTotal"))
        if applied is None:
            continue
        try:
            candidates.append(float(applied))
        except (TypeError, ValueError):
            continue
    if not candidates:
        return None
    # Duplicate exact-week rows are unusual.  Prefer the last/highest finite value
    # only to remain deterministic; they should ordinarily be identical.
    return max(candidates)


def _season_projection(player: dict[str, Any], season: int) -> float | None:
    """Return ESPN's projected season total, never a weekly split."""
    candidates: list[tuple[int, float]] = []
    for stat in player.get("stats") or []:
        if not isinstance(stat, dict) or stat.get("statSourceId") != 1:
            continue
        season_id = stat.get("seasonId", stat.get("seasonValue"))
        if season_id not in (None, int(season)):
            continue
        if stat.get("statSplitTypeId") != 0:
            continue
        applied = stat.get("appliedTotal", stat.get("appliedStatTotal"))
        if applied is None:
            continue
        priority = 2 if stat.get("scoringPeriodId") == 0 else 0
        try:
            candidates.append((priority, float(applied)))
        except (TypeError, ValueError):
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def normalize_player_entry(
    entry: dict[str, Any],
    season: int,
    week: int,
    fantasy_status: str | None = None,
    lineup_slot_id: int | None = None,
) -> dict[str, Any]:
    pool = entry.get("playerPoolEntry") or entry
    player = pool.get("player") or entry.get("player") or {}
    ownership = player.get("ownership") or pool.get("ownership") or {}
    espn_id = pool.get("id", player.get("id", entry.get("id")))
    default_position = player.get("defaultPositionId")
    pro_team_id = player.get("proTeamId")

    return {
        "espn_id": espn_id,
        "name": player.get("fullName"),
        "position": POSITION_MAP.get(default_position, str(default_position) if default_position else None),
        "nfl_team": PRO_TEAM_ABBR.get(pro_team_id),
        "pro_team_id": pro_team_id,
        "active": player.get("active"),
        "injury_status": player.get("injuryStatus"),
        "droppable": player.get("droppable"),
        "lineup_locked": pool.get("lineupLocked", entry.get("lineupLocked")),
        "on_team_id": pool.get("onTeamId", entry.get("onTeamId")),
        "fantasy_status": fantasy_status,
        "lineup_slot_id": lineup_slot_id,
        "lineup_slot": LINEUP_SLOT_MAP.get(lineup_slot_id, str(lineup_slot_id) if lineup_slot_id is not None else None),
        "eligible_slots": list(player.get("eligibleSlots") or []),
        "percent_owned": ownership.get("percentOwned"),
        "percent_started": ownership.get("percentStarted"),
        "weekly_projection": _stat_points(player, season, week, source_id=1),
        "weekly_actual": _stat_points(player, season, week, source_id=0),
        "season_projection": _season_projection(player, season),
        "acquisition_type": entry.get("acquisitionType"),
        "acquisition_date": entry.get("acquisitionDate"),
    }


def _team_name(team: dict[str, Any]) -> str:
    if team.get("name"):
        return str(team["name"])
    parts = [str(team.get(k) or "").strip() for k in ("location", "nickname")]
    name = " ".join(x for x in parts if x).strip()
    return name or str(team.get("abbrev") or team.get("id") or "Unknown")


def normalize_league(payload: dict[str, Any], season: int, week: int) -> dict[str, Any]:
    teams: list[dict[str, Any]] = []
    for team in payload.get("teams") or []:
        if not isinstance(team, dict):
            continue
        entries = ((team.get("roster") or {}).get("entries") or [])
        roster = [
            normalize_player_entry(
                entry,
                season=season,
                week=week,
                fantasy_status="ROSTERED",
                lineup_slot_id=entry.get("lineupSlotId"),
            )
            for entry in entries
            if isinstance(entry, dict)
        ]
        record = ((team.get("record") or {}).get("overall") or {})
        counter = team.get("transactionCounter") or {}
        teams.append({
            "team_id": team.get("id"),
            "name": _team_name(team),
            "abbrev": team.get("abbrev"),
            "waiver_rank": team.get("waiverRank"),
            "wins": record.get("wins"),
            "losses": record.get("losses"),
            "ties": record.get("ties"),
            "points_for": record.get("pointsFor"),
            "points_against": record.get("pointsAgainst"),
            "acquisitions": counter.get("acquisitions"),
            "drops": counter.get("drops"),
            "trades": counter.get("trades"),
            "move_to_ir": counter.get("moveToIR"),
            "roster": roster,
        })

    matchups: list[dict[str, Any]] = []
    for m in payload.get("schedule") or []:
        if not isinstance(m, dict):
            continue
        period = m.get("matchupPeriodId") or m.get("scoringPeriodId")
        if period is not None and int(period) != int(week):
            continue
        home = m.get("home") or {}
        away = m.get("away") or {}
        matchups.append({
            "id": m.get("id"),
            "week": period,
            "home_team_id": home.get("teamId"),
            "away_team_id": away.get("teamId"),
            "home_points": home.get("totalPoints"),
            "away_points": away.get("totalPoints"),
        })

    settings = payload.get("settings") or {}
    status = payload.get("status") or {}
    return {
        "league_id": payload.get("id"),
        "league_name": settings.get("name"),
        "season": int(season),
        "week": int(week),
        "current_scoring_period": status.get("currentScoringPeriod"),
        "current_matchup_period": status.get("currentMatchupPeriod"),
        "teams": teams,
        "matchups": matchups,
        "transactions": normalize_transactions(payload.get("transactions") or []),
    }


def normalize_available_players(payload: dict[str, Any], season: int, week: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for entry in payload.get("players") or []:
        if not isinstance(entry, dict):
            continue
        status = entry.get("status") or (entry.get("playerPoolEntry") or {}).get("status")
        out.append(normalize_player_entry(entry, season, week, fantasy_status=status))
    return out


def normalize_transactions(transactions: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for tx in transactions:
        if not isinstance(tx, dict):
            continue
        items = []
        for item in tx.get("items") or []:
            if not isinstance(item, dict):
                continue
            items.append({
                "player_id": item.get("playerId"),
                "from_team_id": item.get("fromTeamId"),
                "to_team_id": item.get("toTeamId"),
                "type": item.get("type"),
                "lineup_slot_id": item.get("lineupSlotId"),
            })
        out.append({
            "id": tx.get("id"),
            "type": tx.get("type"),
            "status": tx.get("status"),
            "proposed_date": tx.get("proposedDate"),
            "process_date": tx.get("processDate"),
            "team_id": tx.get("teamId"),
            "items": items,
        })
    return out


def sync_private_league_snapshot(
    secrets: EspnSecrets,
    out_dir: str | Path,
    week: int | None = None,
    player_limit: int = 2500,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_league = fetch_private_league(secrets, scoring_period_id=week)
    resolved_week = int(week or infer_scoring_period(raw_league))
    if week is None:
        # Re-query at the resolved scoring period so roster/matchup stats are explicit.
        raw_league = fetch_private_league(secrets, scoring_period_id=resolved_week)

    raw_players = fetch_available_players(
        secrets, scoring_period_id=resolved_week, limit=player_limit
    )

    (out_dir / "espn_league_raw.json").write_text(
        json.dumps(raw_league, indent=2), encoding="utf-8"
    )
    (out_dir / "espn_available_raw.json").write_text(
        json.dumps(raw_players, indent=2), encoding="utf-8"
    )

    normalized = normalize_league(raw_league, secrets.season, resolved_week)
    normalized["available_players"] = normalize_available_players(
        raw_players, secrets.season, resolved_week
    )
    normalized["snapshot_utc"] = datetime.now(timezone.utc).isoformat()
    normalized_path = out_dir / "espn_normalized.json"
    normalized_path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    return normalized
