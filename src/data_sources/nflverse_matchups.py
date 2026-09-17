from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

SCHEDULES_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
PLAYERS_URL = "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv"
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"

TEAM_ALIASES = {
    "LA": "LAR",
    "STL": "LAR",
    "WAS": "WSH",
    "JAC": "JAX",
    "OAK": "LV",
    "SD": "LAC",
}

PBP_DESIRED_COLUMNS = [
    "season",
    "season_type",
    "week",
    "game_id",
    "posteam",
    "defteam",
    "pass_attempt",
    "rush_attempt",
    "sack",
    "interception",
    "fumble_lost",
    "epa",
    "yards_gained",
    "yardline_100",
    "touchdown",
    "receiver_player_id",
]


def normalize_team(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    if not text or text in {"NAN", "NONE"}:
        return None
    return TEAM_ALIASES.get(text, text)


def _download(url: str, path: Path, *, refresh: bool) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = Path(str(path) + ".http.json")
    if path.exists() and not refresh:
        return path
    headers = {"User-Agent": "fantasy-football-season-manager/0.24 (personal analytics project)"}
    if refresh and path.exists() and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if meta.get("etag"):
            headers["If-None-Match"] = str(meta["etag"])
        if meta.get("last_modified"):
            headers["If-Modified-Since"] = str(meta["last_modified"])
    tmp = path.with_suffix(path.suffix + ".part")
    with requests.get(url, headers=headers, stream=True, timeout=120) as response:
        if response.status_code == 304 and path.exists():
            return path
        response.raise_for_status()
        with tmp.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
        response_meta = {
            "url": url,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "downloaded_utc": datetime.now(timezone.utc).isoformat(),
        }
    tmp.replace(path)
    meta_path.write_text(json.dumps(response_meta, indent=2), encoding="utf-8")
    return path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _finite(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _read_pbp(path: Path) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0, compression="infer")
    cols = [c for c in PBP_DESIRED_COLUMNS if c in header.columns]
    return pd.read_csv(path, usecols=cols, low_memory=False, compression="infer")


def _player_position_index(players_path: Path) -> dict[str, str]:
    if not players_path.exists():
        return {}
    header = pd.read_csv(players_path, nrows=0)
    id_col = next((c for c in ("gsis_id", "gsis_it_id", "nfl_id") if c in header.columns), None)
    pos_col = next((c for c in ("position", "position_group") if c in header.columns), None)
    if not id_col or not pos_col:
        return {}
    df = pd.read_csv(players_path, usecols=[id_col, pos_col], low_memory=False)
    out: dict[str, str] = {}
    for row in df.to_dict("records"):
        pid = str(row.get(id_col) or "").strip()
        pos = str(row.get(pos_col) or "").strip().upper()
        if pid and pos:
            out[pid] = pos
    return out


def _safe_mean(series: pd.Series) -> float:
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return float(vals.mean()) if len(vals) else 0.0


def aggregate_team_profiles(
    pbp: pd.DataFrame,
    *,
    receiver_positions: dict[str, str] | None = None,
    max_week: int | None = None,
) -> dict[str, Any]:
    """Aggregate offense/defense matchup observables from nflverse play-by-play.

    The output intentionally contains measured observables, not fantasy multipliers.
    The matchup model standardizes/shrinks them later so data/MC closure can retain
    the underlying acceptance coordinates.
    """
    df = pbp.copy()
    if "season_type" in df:
        df = df[df["season_type"].astype(str).str.upper().eq("REG")]
    if max_week is not None and "week" in df:
        df = df[pd.to_numeric(df["week"], errors="coerce") <= int(max_week)]
    if df.empty:
        return {"defense": {}, "offense": {}, "league": {}}

    for col in ("pass_attempt", "rush_attempt", "sack", "interception", "fumble_lost", "touchdown"):
        if col not in df:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    for col in ("epa", "yards_gained", "yardline_100"):
        if col not in df:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["posteam_norm"] = df.get("posteam", pd.Series(index=df.index, dtype=object)).map(normalize_team)
    df["defteam_norm"] = df.get("defteam", pd.Series(index=df.index, dtype=object)).map(normalize_team)
    df = df[df["posteam_norm"].notna() & df["defteam_norm"].notna()]
    if df.empty:
        return {"defense": {}, "offense": {}, "league": {}}

    df["is_pass"] = ((df["pass_attempt"] > 0) | (df["sack"] > 0)).astype(float)
    df["is_rush"] = (df["rush_attempt"] > 0).astype(float)
    df["is_play"] = ((df["is_pass"] > 0) | (df["is_rush"] > 0)).astype(float)
    df = df[df["is_play"] > 0].copy()
    df["turnover"] = ((df["interception"] > 0) | (df["fumble_lost"] > 0)).astype(float)
    df["explosive_pass"] = ((df["is_pass"] > 0) & (df["yards_gained"] >= 20)).astype(float)
    df["explosive_rush"] = ((df["is_rush"] > 0) & (df["yards_gained"] >= 10)).astype(float)
    df["redzone"] = (df["yardline_100"] <= 20).fillna(False).astype(float)
    df["redzone_td"] = ((df["redzone"] > 0) & (df["touchdown"] > 0)).astype(float)

    receiver_positions = receiver_positions or {}
    if "receiver_player_id" in df:
        df["receiver_pos"] = df["receiver_player_id"].astype(str).map(receiver_positions)
    else:
        df["receiver_pos"] = None

    def build(group_col: str, defense: bool) -> dict[str, dict[str, float]]:
        result: dict[str, dict[str, float]] = {}
        for team, g in df.groupby(group_col, dropna=True):
            team = normalize_team(team)
            if not team:
                continue
            plays = float(g["is_play"].sum())
            if plays <= 0:
                continue
            games = max(int(g["game_id"].nunique()) if "game_id" in g else 1, 1)
            pass_g = g[g["is_pass"] > 0]
            rush_g = g[g["is_rush"] > 0]
            rz = g[g["redzone"] > 0]
            targets = g[g.get("receiver_player_id", pd.Series(index=g.index, dtype=object)).notna()] if "receiver_player_id" in g else g.iloc[0:0]
            row = {
                "plays": plays,
                "games": float(games),
                "plays_per_game": plays / games,
                "pass_rate": float(g["is_pass"].sum() / plays),
                "rush_rate": float(g["is_rush"].sum() / plays),
                "epa_per_play": _safe_mean(g["epa"]),
                "pass_epa_per_play": _safe_mean(pass_g["epa"]),
                "rush_epa_per_play": _safe_mean(rush_g["epa"]),
                "yards_per_play": _safe_mean(g["yards_gained"]),
                "sack_rate": float(g["sack"].sum() / max(float(g["is_pass"].sum()), 1.0)),
                "turnover_rate": float(g["turnover"].sum() / plays),
                "explosive_pass_rate": float(pass_g["explosive_pass"].mean()) if len(pass_g) else 0.0,
                "explosive_rush_rate": float(rush_g["explosive_rush"].mean()) if len(rush_g) else 0.0,
                "redzone_td_rate": float(rz["redzone_td"].mean()) if len(rz) else 0.0,
            }
            if len(targets):
                denom = float(len(targets))
                for pos in ("RB", "WR", "TE"):
                    row[f"target_share_{pos.lower()}"] = float((targets["receiver_pos"] == pos).sum() / denom)
            else:
                for pos in ("RB", "WR", "TE"):
                    row[f"target_share_{pos.lower()}"] = 0.0
            result[team] = row
        return result

    defense = build("defteam_norm", True)
    offense = build("posteam_norm", False)

    numeric_keys = sorted({k for row in defense.values() for k in row if k not in {"games", "plays"}})
    league: dict[str, dict[str, float]] = {}
    for key in numeric_keys:
        vals = np.asarray([row[key] for row in defense.values() if math.isfinite(float(row.get(key, np.nan)))], dtype=float)
        if len(vals):
            league[key] = {"mean": float(np.mean(vals)), "sd": float(np.std(vals, ddof=0))}
    return {"defense": defense, "offense": offense, "league": league}


def _blend_profile(prior: dict[str, float] | None, current: dict[str, float] | None, *, k_plays: float) -> dict[str, float]:
    prior = prior or {}
    current = current or {}
    n = float(current.get("plays") or 0.0)
    lam = n / (n + max(float(k_plays), 1.0)) if n > 0 else 0.0
    keys = set(prior) | set(current)
    out: dict[str, float] = {"current_weight": float(lam), "current_plays": n}
    for key in keys:
        if key in {"current_weight", "current_plays"}:
            continue
        p = _finite(prior.get(key))
        c = _finite(current.get(key))
        if p is not None and c is not None:
            out[key] = float((1.0 - lam) * p + lam * c)
        elif c is not None:
            out[key] = float(c)
        elif p is not None:
            out[key] = float(p)
    return out


def build_matchup_context(
    schedules: pd.DataFrame,
    *,
    season: int,
    current_week: int,
    prior_profiles: dict[str, Any],
    current_profiles: dict[str, Any] | None,
    shrinkage_plays: float = 400.0,
) -> dict[str, Any]:
    current_profiles = current_profiles or {"defense": {}, "offense": {}}
    teams = sorted(set(prior_profiles.get("defense", {})) | set(current_profiles.get("defense", {})))
    defense: dict[str, dict[str, float]] = {}
    offense: dict[str, dict[str, float]] = {}
    for team in teams:
        defense[team] = _blend_profile(
            prior_profiles.get("defense", {}).get(team),
            current_profiles.get("defense", {}).get(team),
            k_plays=shrinkage_plays,
        )
        offense[team] = _blend_profile(
            prior_profiles.get("offense", {}).get(team),
            current_profiles.get("offense", {}).get(team),
            k_plays=shrinkage_plays,
        )

    # Standardize blended defense coordinates league-wide. Positive z means the
    # defense allows more of that observable unless the metric itself is suppressive
    # (sack_rate, turnover_rate), which the downstream position weights handle.
    metric_keys = [
        "plays_per_game", "pass_rate", "rush_rate", "epa_per_play", "pass_epa_per_play",
        "rush_epa_per_play", "yards_per_play", "sack_rate", "turnover_rate",
        "explosive_pass_rate", "explosive_rush_rate", "redzone_td_rate",
        "target_share_rb", "target_share_wr", "target_share_te",
    ]
    zscores: dict[str, dict[str, float]] = {team: {} for team in defense}
    league_ref: dict[str, dict[str, float]] = {}
    for key in metric_keys:
        vals = np.asarray([float(row[key]) for row in defense.values() if key in row and math.isfinite(float(row[key]))])
        if len(vals) < 2:
            mean, sd = (float(np.mean(vals)) if len(vals) else 0.0), 1.0
        else:
            mean, sd = float(np.mean(vals)), float(np.std(vals, ddof=0))
            sd = max(sd, 1e-9)
        league_ref[key] = {"mean": mean, "sd": sd}
        for team, row in defense.items():
            if key in row:
                zscores[team][key] = float((float(row[key]) - mean) / sd)

    team_week: dict[str, dict[str, dict[str, Any]]] = {}
    sdf = schedules.copy()
    if "season" in sdf:
        sdf = sdf[pd.to_numeric(sdf["season"], errors="coerce") == int(season)]
    if "game_type" in sdf:
        sdf = sdf[sdf["game_type"].astype(str).str.upper().eq("REG")]
    for row in sdf.to_dict("records"):
        try:
            week = int(row.get("week"))
        except (TypeError, ValueError):
            continue
        home = normalize_team(row.get("home_team"))
        away = normalize_team(row.get("away_team"))
        if not home or not away:
            continue
        total_line = _finite(row.get("total_line"))
        spread_line = _finite(row.get("spread_line"))
        # nflverse spread_line is positive when the home team is favored.
        home_implied = (total_line / 2.0 + spread_line / 2.0) if total_line is not None and spread_line is not None else None
        away_implied = (total_line / 2.0 - spread_line / 2.0) if total_line is not None and spread_line is not None else None
        common = {
            "game_id": row.get("game_id"),
            "gameday": row.get("gameday"),
            "gametime": row.get("gametime"),
            "total_line": total_line,
            "spread_line": spread_line,
            "location": row.get("location"),
        }
        team_week.setdefault(home, {})[str(week)] = {**common, "opponent": away, "home": True, "team_implied_points": home_implied}
        team_week.setdefault(away, {})[str(week)] = {**common, "opponent": home, "home": False, "team_implied_points": away_implied}

    return {
        "schema_version": 1,
        "season": int(season),
        "current_week": int(current_week),
        "prior_season": int(season) - 1,
        "shrinkage_plays": float(shrinkage_plays),
        "defense_profiles": defense,
        "offense_profiles": offense,
        "defense_zscores": zscores,
        "league_reference": league_ref,
        "team_week": team_week,
    }


def sync_nflverse_matchups(
    *,
    season: int,
    current_week: int,
    cache_dir: str | Path,
    snapshot_dir: str | Path,
    shrinkage_plays: float = 400.0,
) -> dict[str, Any]:
    """Download/cache nflverse matchup inputs and write a compact immutable snapshot.

    Historical PBP is cached and immutable. Current-season PBP and schedules refresh
    on season-sync. The timestamped season snapshot stores the derived coordinates,
    hashes, and URLs rather than duplicating a very large PBP file every day.
    """
    cache_dir = Path(cache_dir)
    snapshot_dir = Path(snapshot_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    prior_season = int(season) - 1
    schedules_path = _download(SCHEDULES_URL, cache_dir / "games.csv", refresh=True)
    players_path = _download(PLAYERS_URL, cache_dir / "players.csv", refresh=False)
    prior_pbp = _download(PBP_URL.format(season=prior_season), cache_dir / f"play_by_play_{prior_season}.csv.gz", refresh=False)

    current_pbp: Path | None = None
    current_error: str | None = None
    if int(current_week) > 1:
        try:
            current_pbp = _download(PBP_URL.format(season=season), cache_dir / f"play_by_play_{season}.csv.gz", refresh=True)
        except Exception as exc:  # current-season release can lag immediately after games
            current_error = f"{type(exc).__name__}: {exc}"

    positions = _player_position_index(players_path)
    prior_df = _read_pbp(prior_pbp)
    prior_profiles = aggregate_team_profiles(prior_df, receiver_positions=positions)
    current_profiles = {"defense": {}, "offense": {}, "league": {}}
    current_rows = 0
    if current_pbp is not None and current_pbp.exists():
        current_df = _read_pbp(current_pbp)
        current_rows = len(current_df)
        current_profiles = aggregate_team_profiles(
            current_df,
            receiver_positions=positions,
            max_week=max(int(current_week) - 1, 0),
        )

    schedules = pd.read_csv(schedules_path, low_memory=False)
    context = build_matchup_context(
        schedules,
        season=int(season),
        current_week=int(current_week),
        prior_profiles=prior_profiles,
        current_profiles=current_profiles,
        shrinkage_plays=float(shrinkage_plays),
    )
    source = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "schedules": {"url": SCHEDULES_URL, "path": str(schedules_path), "sha256": _sha256(schedules_path)},
        "players": {"url": PLAYERS_URL, "path": str(players_path), "sha256": _sha256(players_path)},
        "prior_pbp": {"url": PBP_URL.format(season=prior_season), "path": str(prior_pbp), "sha256": _sha256(prior_pbp), "rows": int(len(prior_df))},
        "current_pbp": None,
        "current_pbp_error": current_error,
    }
    if current_pbp is not None and current_pbp.exists():
        source["current_pbp"] = {"url": PBP_URL.format(season=season), "path": str(current_pbp), "sha256": _sha256(current_pbp), "rows": int(current_rows), "max_week_used": max(int(current_week) - 1, 0)}
    context["source"] = source
    path = snapshot_dir / "matchup_context.json"
    path.write_text(json.dumps(context, indent=2), encoding="utf-8")
    return context
