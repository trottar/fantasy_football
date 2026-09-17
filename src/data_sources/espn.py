from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests


POSITION_MAP = {
    1: "QB",
    2: "RB",
    3: "WR",
    4: "TE",
    5: "K",
    16: "DST",
}

PRO_TEAM_ABBR = {
    0: "FA",
    1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL",
    7: "DEN", 8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC",
    13: "LV", 14: "LAR", 15: "MIA", 16: "MIN", 17: "NE", 18: "NO",
    19: "NYG", 20: "NYJ", 21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC",
    25: "SF", 26: "SEA", 27: "TB", 28: "WAS", 29: "CAR", 30: "JAX",
    33: "BAL", 34: "HOU",
}


def _first_dict(*objects):
    for obj in objects:
        if isinstance(obj, dict):
            return obj
    return {}


def _extract_rank(entry: dict[str, Any], rank_type: str = "PPR"):
    player = entry.get("player") or {}
    ratings = entry.get("ratings") or player.get("ratings") or {}

    # Common ESPN structure: player.draftRanksByRankType.PPR.rank
    rank_map = player.get("draftRanksByRankType") or {}
    if isinstance(rank_map, dict):
        obj = rank_map.get(rank_type)
        if isinstance(obj, dict) and obj.get("rank") is not None:
            return obj.get("rank")
        if isinstance(obj, (int, float)):
            return obj

    # Some responses place rank objects under ratings.
    if isinstance(ratings, dict):
        for value in ratings.values():
            if isinstance(value, dict):
                if value.get("rankType") == rank_type and value.get("rank") is not None:
                    return value.get("rank")
                if value.get("rank") is not None and rank_type in str(value).upper():
                    return value.get("rank")

    return None


def _extract_projection(entry: dict[str, Any], season: int):
    """Extract ESPN projected fantasy points.

    ESPN uses:
      statSourceId == 1   -> projection
      statSplitTypeId == 0 -> season total
      statSplitTypeId == 1 -> single scoring period

    Prefer a season-total projection (scoringPeriodId 0 / split 0). Fall back
    to the most complete projected entry if ESPN changes the exact layout.
    """
    player = entry.get("player") or {}
    pool = entry.get("playerPoolEntry") or {}

    stats = []
    for candidate in (
        pool.get("stats"),
        player.get("stats"),
        entry.get("stats"),
    ):
        if isinstance(candidate, list):
            stats.extend(candidate)

    candidates = []
    for stat in stats:
        if not isinstance(stat, dict):
            continue

        if stat.get("statSourceId") != 1:
            continue

        season_id = stat.get("seasonId", stat.get("seasonValue"))
        if season_id not in (None, season):
            continue

        applied = stat.get("appliedTotal")
        if applied is None:
            applied = stat.get("appliedStatTotal")
        if applied is None:
            continue

        scoring_period = stat.get("scoringPeriodId")
        split_type = stat.get("statSplitTypeId")

        # Highest priority = explicit season-total projection.
        priority = 0
        if split_type == 0:
            priority += 2
        if scoring_period == 0:
            priority += 2

        candidates.append({
            "priority": priority,
            "scoring_period": scoring_period,
            "split_type": split_type,
            "points": float(applied),
        })

    if not candidates:
        # Some ESPN player-pool responses expose only an entry-level applied
        # total. Treat it as a last-resort projection only when present.
        fallback = entry.get("appliedStatTotal")
        if fallback is not None:
            try:
                return float(fallback)
            except (TypeError, ValueError):
                pass
        return None

    candidates.sort(
        key=lambda x: (
            x["priority"],
            -(x["scoring_period"] or 0),
        ),
        reverse=True,
    )
    return candidates[0]["points"]


def normalize_espn_players(payload: dict[str, Any], season: int = 2026,
                           rank_type: str = "PPR") -> pd.DataFrame:
    rows = []
    for entry in payload.get("players", []):
        if not isinstance(entry, dict):
            continue
        player = entry.get("player") or {}
        pool = entry.get("playerPoolEntry") or {}
        ownership = _first_dict(
            player.get("ownership"),
            pool.get("ownership"),
            entry.get("ownership"),
        )

        default_pos_id = player.get("defaultPositionId")
        pos = POSITION_MAP.get(default_pos_id, str(default_pos_id) if default_pos_id else None)
        pro_team_id = player.get("proTeamId")

        rows.append({
            "espn_id": entry.get("id", player.get("id")),
            "name": player.get("fullName"),
            "position": pos,
            "espn_position_id": default_pos_id,
            "pro_team_id": pro_team_id,
            "nfl_team": PRO_TEAM_ABBR.get(pro_team_id),
            "active": player.get("active"),
            "injury_status": player.get("injuryStatus"),
            "percent_owned": ownership.get("percentOwned"),
            "percent_started": ownership.get("percentStarted"),
            "espn_adp": ownership.get("averageDraftPosition"),
            "espn_rank": _extract_rank(entry, rank_type=rank_type),
            "espn_proj_points": _extract_projection(entry, season=season),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["espn_id"] = pd.to_numeric(df["espn_id"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["espn_id", "name"]).drop_duplicates("espn_id")
    return df


def fetch_espn_ppr_player_pool(
    season: int = 2026,
    scoring_default_id: int = 3,
    rank_type: str = "PPR",
    limit: int = 2000,
) -> dict[str, Any]:
    url = (
        f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{season}/segments/0/leaguedefaults/{scoring_default_id}"
        "?scoringPeriodId=0&view=kona_player_info"
    )

    fantasy_filter = {
        "players": {
            "filterSlotIds": {"value": [0, 2, 4, 6, 17, 16]},
            "filterStatsForExternalIds": {"value": [season]},
            "filterStatsForSourceIds": {"value": [1]},
            "filterStatsForSplitTypeIds": {"value": [0]},
            "filterStatsForTopScoringPeriodIds": {
                "value": 2,
                "additionalValue": [
                    f"00{season}",
                    f"10{season}",
                    f"11{season}0",
                    f"02{season}",
                ],
            },
            "sortAppliedStatTotal": {
                "sortAsc": False,
                "sortPriority": 3,
                "value": f"11{season}0",
            },
            "sortDraftRanks": {
                "sortPriority": 1,
                "sortAsc": True,
                "value": rank_type,
            },
            "sortPercOwned": {
                "sortPriority": 2,
                "sortAsc": False,
            },
            "limit": int(limit),
            "offset": 0,
            "filterRanksForScoringPeriodIds": {"value": [1]},
            "filterRanksForRankTypes": {"value": [rank_type]},
            "filterRanksForSlotIds": {"value": [0, 2, 4, 6, 17, 16]},
        }
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "fantasy-draft-optimizer/0.2 "
                      "(personal analytics project)",
        "X-Fantasy-Source": "kona",
        "X-Fantasy-Filter": json.dumps(fantasy_filter, separators=(",", ":")),
    }

    response = requests.get(url, headers=headers, timeout=45)
    response.raise_for_status()
    return response.json()


def sync_espn(
    out_dir: str | Path,
    season: int = 2026,
    scoring_default_id: int = 3,
    rank_type: str = "PPR",
    limit: int = 2000,
) -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = fetch_espn_ppr_player_pool(
        season=season,
        scoring_default_id=scoring_default_id,
        rank_type=rank_type,
        limit=limit,
    )

    raw_path = out_dir / f"player_pool_{season}.json"
    raw_path.write_text(json.dumps(payload, indent=2))

    df = normalize_espn_players(payload, season=season, rank_type=rank_type)
    csv_path = out_dir / f"player_pool_{season}.csv"
    df.to_csv(csv_path, index=False)

    return {"raw": raw_path, "csv": csv_path}
