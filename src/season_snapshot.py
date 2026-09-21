from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import math

from .data_sources.espn_league import sync_private_league_snapshot
from .data_sources.secrets import load_espn_secrets
from .data_sources.sleeper import sync_sleeper
from .data_sources.nfl_official import sync_nfl_official
from .data_sources.nfl_team_rosters import sync_nfl_team_rosters
from .data_sources.nflverse_rosters import sync_nflverse_rosters
from .data_sources.nflverse_matchups import sync_nflverse_matchups
from .observability.shadow_pilot import shadow_data_source_call


def _compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _clean_scalar(value: Any) -> Any:
    """Convert pandas/CSV missing scalars (NaN/NA) to JSON-safe None."""
    if value is None:
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except TypeError:
        pass
    # pandas.NA cannot be used in a normal truth test, so compare through isna lazily.
    try:
        import pandas as pd
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _annotate_sleeper(players: list[dict[str, Any]], sleeper_by_espn: dict[int, dict[str, Any]]) -> None:
    for p in players:
        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            continue
        s = sleeper_by_espn.get(pid)
        if not s:
            continue
        p["sleeper_id"] = _clean_scalar(s.get("sleeper_id"))
        p["sleeper_team"] = _clean_scalar(s.get("team"))
        p["sleeper_status"] = _clean_scalar(s.get("status"))
        p["sleeper_injury_status"] = _clean_scalar(s.get("injury_status"))
        p["sleeper_injury_start_date"] = _clean_scalar(s.get("injury_start_date"))
        p["sleeper_practice_participation"] = _clean_scalar(s.get("practice_participation"))
        p["sleeper_depth_chart_position"] = _clean_scalar(s.get("depth_chart_position"))
        p["sleeper_depth_chart_order"] = _clean_scalar(s.get("depth_chart_order"))


def build_sleeper_index(csv_path: str | Path) -> dict[int, dict[str, Any]]:
    import pandas as pd

    path = Path(csv_path)
    if not path.exists():
        return {}
    df = pd.read_csv(path, low_memory=False)
    out: dict[int, dict[str, Any]] = {}
    for row in df.to_dict("records"):
        try:
            pid = int(float(row.get("espn_id")))
        except (TypeError, ValueError):
            continue
        out[pid] = {k: _clean_scalar(v) for k, v in row.items()}
    return out


def _load_sleeper_trends(paths: dict[str, Path]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for kind, key in (("add", "trending_add"), ("drop", "trending_drop")):
        path = paths.get(key)
        if not path or not Path(path).exists():
            continue
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in payload if isinstance(payload, list) else []:
            if not isinstance(row, dict):
                continue
            sid = str(row.get("player_id") or "").strip()
            if not sid:
                continue
            try:
                count = int(row.get("count") or 0)
            except (TypeError, ValueError):
                count = 0
            out.setdefault(sid, {})[kind] = count
    return out


def _annotate_sleeper_trends(players: list[dict[str, Any]], trends: dict[str, dict[str, int]]) -> None:
    for p in players:
        sid = str(p.get("sleeper_id") or "").strip()
        if not sid or sid not in trends:
            continue
        p["sleeper_trending_add_24h"] = int(trends[sid].get("add", 0))
        p["sleeper_trending_drop_24h"] = int(trends[sid].get("drop", 0))


def _name_key(value: Any) -> str:
    return " ".join(str(value or "").casefold().replace(".", "").replace("'", "").split())


def _annotate_nfl_official_injuries(players: list[dict[str, Any]], injuries: list[dict[str, Any]]) -> int:
    # Exact normalized-name matches only. Ambiguous names are deliberately ignored.
    by_name: dict[str, list[dict[str, Any]]] = {}
    for row in injuries:
        key = _name_key(row.get("name"))
        if key:
            by_name.setdefault(key, []).append(row)
    matched = 0
    for p in players:
        rows = by_name.get(_name_key(p.get("name"))) or []
        if len(rows) != 1:
            continue
        row = rows[0]
        status = _clean_scalar(row.get("game_status"))
        if status:
            p["official_injury_status"] = status
        p["official_injury"] = _clean_scalar(row.get("injury"))
        p["official_practice"] = row.get("practice") or {}
        p["official_injury_source"] = "NFL.com"
        matched += 1
    return matched





def _annotate_nfl_official_rosters(players: list[dict[str, Any]], rows: list[dict[str, Any]]) -> int:
    # NFL.com team roster pages are the highest-priority current roster-state
    # observation. Match exact normalized names only; ambiguous names fail safe.
    # NFL.com uses compact administrative codes. RSR is a reserve-list class used
    # for players such as reserve/injured-designated-to-return; it is unavailable
    # for the current week even though the player remains under contract.
    hard_map = {
        "PUP": "PUP",
        "RES": "RESERVE",
        "IR": "IR",
        "RSR": "IR",
        "INA": "OUT",
        "SUS": "SUSPENDED",
        "EXE": "EXEMPT",
        "RLS": "RESERVE",
        "NFI": "NFI_RESERVE",
        "CUT": "OUT",
        "RET": "OUT",
        "UFA": "OUT",
    }
    by_name: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = _name_key(row.get("name"))
        if key:
            by_name.setdefault(key, []).append(row)
    matched = 0
    for p in players:
        if str(p.get("position") or "").upper() == "DST":
            continue
        candidates = by_name.get(_name_key(p.get("name"))) or []
        if len(candidates) != 1:
            continue
        row = candidates[0]
        matched += 1
        team = _clean_scalar(row.get("team"))
        status = str(_clean_scalar(row.get("status")) or "").strip().upper() or None
        p["official_roster_team"] = team
        p["official_roster_status"] = status
        p["official_roster_source"] = "NFL.com/team/roster"
        p["official_roster_url"] = _clean_scalar(row.get("source_url"))
        if status in hard_map:
            p["official_roster_availability_status"] = hard_map[status]
        # Only a confirmed ACT row rewrites the current team. Non-active rows keep
        # the lower-source team for historical/context display but are excluded by
        # transaction_manager from ordinary add/drop valuation.
        if status == "ACT" and team:
            if p.get("nfl_team") != team:
                p["pre_official_nfl_team"] = p.get("nfl_team")
            p["nfl_team"] = team
            p["nfl_team_source"] = "NFL_OFFICIAL_ROSTER"
    return matched

def _annotate_nflverse_rosters(players: list[dict[str, Any]], roster_by_espn: dict[int, dict[str, Any]]) -> int:
    matched = 0
    hard_map = {
        "PUP": "PUP",
        "SUS": "SUSPENDED",
        "EXE": "EXEMPT",
        "RES": "RESERVE",
        "RSN": "RESERVE",
        "RET": "OUT",
    }
    for p in players:
        # ESPN D/ST pseudo-players are team entities, not nflverse player rows.
        if str(p.get("position") or "").upper() == "DST":
            continue
        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            continue
        row = roster_by_espn.get(pid)
        if not row:
            continue
        matched += 1
        team = _clean_scalar(row.get("team"))
        status = str(_clean_scalar(row.get("status")) or "").strip().upper() or None
        p["nflverse_roster_team"] = team
        p["nflverse_roster_status"] = status
        p["nflverse_roster_week"] = _clean_scalar(row.get("week"))
        p["nflverse_gsis_id"] = _clean_scalar(row.get("gsis_id"))
        p["nflverse_roster_match"] = "ESPN_ID"
        # An active nflverse row is a better current-team observation than ESPN's
        # fantasy metadata, which can lag NFL transactions. Preserve the ESPN value.
        if status == "ACT" and team:
            if p.get("nfl_team") != team:
                p["espn_nfl_team_original"] = p.get("nfl_team")
            p["nfl_team"] = team
            p["nfl_team_source"] = "NFLVERSE_ROSTER"
        if status in hard_map:
            p["nflverse_availability_status"] = hard_map[status]
    return matched

@shadow_data_source_call("subsystem.data_source.season_sync")
def sync_season_snapshot(
    secrets_path: str | Path | None = None,
    out_root: str | Path = "data/season_snapshots",
    week: int | None = None,
    include_sleeper: bool = True,
    include_nfl: bool = True,
) -> tuple[dict[str, Any], Path]:
    secrets = load_espn_secrets(secrets_path)
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = _compact_timestamp()
    snapshot_dir = out_root / stamp
    suffix = 1
    while snapshot_dir.exists():
        snapshot_dir = out_root / f"{stamp}_{suffix:02d}"
        suffix += 1
    snapshot_dir.mkdir(parents=True)

    espn = sync_private_league_snapshot(secrets, snapshot_dir / "espn", week=week)
    source_status: dict[str, Any] = {
        "espn": {"ok": True, "authoritative": "fantasy_league_state"},
    }

    sleeper_index: dict[int, dict[str, Any]] = {}
    sleeper_trends: dict[str, dict[str, int]] = {}
    if include_sleeper:
        try:
            paths = sync_sleeper(snapshot_dir / "sleeper", include_trends=True)
            sleeper_index = build_sleeper_index(paths["players_csv"])
            sleeper_trends = _load_sleeper_trends(paths)
            source_status["sleeper"] = {
                "ok": True,
                "authoritative": False,
                "role": "corroborating_player_metadata",
                "players": len(sleeper_index),
            }
        except Exception as exc:  # secondary source must not destroy ESPN snapshot
            source_status["sleeper"] = {
                "ok": False,
                "authoritative": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

    if sleeper_index:
        for team in espn.get("teams") or []:
            _annotate_sleeper(team.get("roster") or [], sleeper_index)
        _annotate_sleeper(espn.get("available_players") or [], sleeper_index)
        if sleeper_trends:
            for team in espn.get("teams") or []:
                _annotate_sleeper_trends(team.get("roster") or [], sleeper_trends)
            _annotate_sleeper_trends(espn.get("available_players") or [], sleeper_trends)

    # nflverse rosters are refreshed daily and provide a current NFL roster/status
    # cross-check with ESPN IDs. Failure is non-fatal; ESPN/Sleeper remain available.
    try:
        roster_index, roster_meta = sync_nflverse_rosters(
            snapshot_dir / "nflverse_rosters", int(espn.get("season") or secrets.season)
        )
        roster_matches = 0
        for team in espn.get("teams") or []:
            roster_matches += _annotate_nflverse_rosters(team.get("roster") or [], roster_index)
        roster_matches += _annotate_nflverse_rosters(espn.get("available_players") or [], roster_index)
        source_status["nflverse_rosters"] = {
            **roster_meta,
            "authoritative": False,
            "role": "current_nfl_roster_status_crosscheck",
            "fantasy_player_matches": roster_matches,
        }
    except Exception as exc:
        source_status["nflverse_rosters"] = {
            "ok": False,
            "authoritative": False,
            "role": "current_nfl_roster_status_crosscheck",
            "error": f"{type(exc).__name__}: {exc}",
        }

    matchup_context: dict[str, Any] = {}
    try:
        season_value = int(espn.get("season") or secrets.season)
        week_value = int(espn.get("week") or week or 1)
        matchup_context = sync_nflverse_matchups(
            season=season_value,
            current_week=week_value,
            cache_dir=out_root.parent / "raw" / "nflverse_matchups",
            snapshot_dir=snapshot_dir / "nflverse_matchups",
            shrinkage_plays=400.0,
        )
        source = matchup_context.get("source") or {}
        current = source.get("current_pbp") or {}
        source_status["nflverse_matchups"] = {
            "ok": True,
            "authoritative": False,
            "role": "matchup_acceptance_inputs",
            "prior_season": int(matchup_context.get("prior_season") or season_value - 1),
            "defense_profiles": len(matchup_context.get("defense_profiles") or {}),
            "offense_profiles": len(matchup_context.get("offense_profiles") or {}),
            "scheduled_teams": len(matchup_context.get("team_week") or {}),
            "current_pbp_rows": int(current.get("rows") or 0),
            "current_pbp_error": source.get("current_pbp_error"),
        }
    except Exception as exc:
        source_status["nflverse_matchups"] = {
            "ok": False,
            "authoritative": False,
            "role": "matchup_acceptance_inputs",
            "error": f"{type(exc).__name__}: {exc}",
        }

    nfl_official: dict[str, Any] = {"transactions": [], "injuries": []}
    if include_nfl:
        # Current team roster pages are a stronger current roster-state observation
        # than ESPN/Sleeper/nflverse when those feeds lag cuts/reserve moves.
        try:
            official_rosters = sync_nfl_team_rosters(snapshot_dir / "nfl_team_rosters")
            roster_rows = official_rosters.get("rows") or []
            official_roster_matches = 0
            if roster_rows:
                for team in espn.get("teams") or []:
                    official_roster_matches += _annotate_nfl_official_rosters(team.get("roster") or [], roster_rows)
                official_roster_matches += _annotate_nfl_official_rosters(espn.get("available_players") or [], roster_rows)
            source_status["nfl_official_rosters"] = {
                "ok": bool(official_rosters.get("fetches_ok")),
                "authoritative": "real_nfl_roster_status",
                "fetches_ok": int(official_rosters.get("fetches_ok") or 0),
                "fetches_total": int(official_rosters.get("fetches_total") or 0),
                "parsed_teams": int(official_rosters.get("parsed_teams") or 0),
                "rows": int(official_rosters.get("total_rows") or 0),
                "complete": bool(official_rosters.get("complete")),
                "fantasy_player_matches": int(official_roster_matches),
            }
        except Exception as exc:
            source_status["nfl_official_rosters"] = {
                "ok": False,
                "authoritative": "real_nfl_roster_status",
                "error": f"{type(exc).__name__}: {exc}",
            }

        try:
            nfl_official = sync_nfl_official(snapshot_dir / "nfl_official")
            injury_matches = 0
            injuries = nfl_official.get("injuries") or []
            if injuries:
                for team in espn.get("teams") or []:
                    injury_matches += _annotate_nfl_official_injuries(team.get("roster") or [], injuries)
                injury_matches += _annotate_nfl_official_injuries(espn.get("available_players") or [], injuries)
            categories = nfl_official.get("transaction_categories") or {}
            tx_fetches_ok = sum(1 for info in categories.values() if isinstance(info, dict) and info.get("ok"))
            injury_fetch_ok = bool((nfl_official.get("injury_status") or {}).get("ok"))
            source_status["nfl_official"] = {
                "ok": bool(tx_fetches_ok or injury_fetch_ok),
                "authoritative": "real_nfl_status",
                "transactions": len(nfl_official.get("transactions") or []),
                "transaction_category_fetches_ok": tx_fetches_ok,
                "transaction_category_fetches_total": len(categories),
                "injury_page_ok": injury_fetch_ok,
                "injury_rows": len(injuries),
                "injury_player_matches": injury_matches,
                "injury_parser_active": bool(injuries),
            }
        except Exception as exc:
            source_status["nfl_official"] = {
                "ok": False,
                "authoritative": "real_nfl_status",
                "error": f"{type(exc).__name__}: {exc}",
            }

    snapshot = {
        "schema_version": 1,
        "snapshot_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_dir": str(snapshot_dir),
        "source_status": source_status,
        "espn": espn,
        "nfl_official": nfl_official,
        "matchup_context": matchup_context,
    }
    path = snapshot_dir / "snapshot.json"
    path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    # Copy, rather than symlink, so the project behaves identically on Windows.
    latest = out_root / "latest.json"
    latest.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot, path
