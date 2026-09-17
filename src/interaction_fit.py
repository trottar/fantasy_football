from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .data_sources.nflverse_matchups import (
    PBP_URL,
    PLAYERS_URL,
    _download,
    _player_position_index,
    _read_pbp,
    aggregate_team_profiles,
    build_matchup_context,
    normalize_team,
)
from .interaction_grid import DEFAULT_COMPONENTS, interpolate_grid


@dataclass(frozen=True)
class FitResult:
    artifact_dir: Path
    manifest_path: Path
    validation_path: Path
    rows: int
    grids: int


def _write_fit_failure(
    out_dir: Path,
    *,
    reason: str,
    validation_season: int | None = None,
    coverage_path: Path | None = None,
) -> Path:
    marker = out_dir / "fit_failure.json"
    payload = {
        "failed_utc": datetime.now(timezone.utc).isoformat(),
        "model_version": "0.28",
        "reason": str(reason),
        "validation_season": int(validation_season) if validation_season is not None else None,
        "coverage_path": str(coverage_path) if coverage_path is not None else None,
    }
    marker.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return marker


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _numeric(df: pd.DataFrame, name: str) -> pd.Series:
    if name not in df.columns:
        return pd.Series(0.0, index=df.index, dtype=float)
    return pd.to_numeric(df[name], errors="coerce").fillna(0.0)


def _opponent_from_game_id(game_id: Any, team: Any) -> str | None:
    """Recover an opponent from nflverse game_id when opponent_team is absent.

    Weekly nflverse rows normally carry opponent_team directly.  The fallback is
    intentionally schema-driven (YYYY_WW_AWAY_HOME), not a fuzzy team-name guess.
    """
    parts = str(game_id or "").strip().split("_")
    if len(parts) < 4:
        return None
    away = normalize_team(parts[-2])
    home = normalize_team(parts[-1])
    current = normalize_team(team)
    if current and current == away:
        return home
    if current and current == home:
        return away
    return None


def _prepare_weekly_player_stats(stats: pd.DataFrame) -> pd.DataFrame:
    df = stats.copy()
    if "season_type" in df.columns:
        df = df[df["season_type"].astype(str).str.upper().eq("REG")]
    required = {"season", "week", "player_id", "position"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"nflverse player_stats missing required columns: {sorted(missing)}")
    df["season"] = pd.to_numeric(df["season"], errors="coerce")
    df["week"] = pd.to_numeric(df["week"], errors="coerce")
    df = df[df["season"].notna() & df["week"].notna()].copy()
    df["season"] = df["season"].astype(int)
    df["week"] = df["week"].astype(int)
    df["position"] = df["position"].astype(str).str.upper()
    df = df[df["position"].isin(DEFAULT_COMPONENTS)].copy()

    # Current nflverse stats_player weekly assets use recent_team, while older
    # player_stats assets may use team and/or opponent_team.  Preserve both
    # schemas and let build_training_rows recover any missing opponent from the
    # historical PBP team/week mapping.
    team_col = next((column for column in ("team", "recent_team", "team_abbr") if column in df.columns), None)
    df["team"] = df[team_col].map(normalize_team) if team_col else None
    if "opponent_team" in df.columns:
        df["opponent"] = df["opponent_team"].map(normalize_team)
    else:
        df["opponent"] = None
    if "game_id" in df.columns:
        missing_opp = df["opponent"].isna()
        if missing_opp.any():
            recovered = df.loc[missing_opp, ["game_id", "team"]].apply(
                lambda row: _opponent_from_game_id(row["game_id"], row["team"]), axis=1
            )
            df.loc[missing_opp, "opponent"] = recovered

    attempts = _numeric(df, "attempts")
    passing_yards = _numeric(df, "passing_yards")
    carries = _numeric(df, "carries")
    rushing_yards = _numeric(df, "rushing_yards")
    targets = _numeric(df, "targets")
    receptions = _numeric(df, "receptions")
    receiving_yards = _numeric(df, "receiving_yards")

    df["attempts"] = attempts
    df["passing_yards_per_attempt"] = np.where(attempts > 0, passing_yards / attempts, np.nan)
    df["carries"] = carries
    df["rushing_attempts"] = carries
    df["rushing_yards_per_attempt"] = np.where(carries > 0, rushing_yards / carries, np.nan)
    df["targets"] = targets
    df["catch_rate"] = np.where(targets > 0, receptions / targets, np.nan)
    df["receiving_yards_per_target"] = np.where(targets > 0, receiving_yards / targets, np.nan)
    return df


def _rolling_baselines(df: pd.DataFrame, *, min_games: int, shrink_games: float) -> pd.DataFrame:
    out = df.sort_values(["player_id", "season", "week"]).copy()
    metrics = sorted({metric for schema in DEFAULT_COMPONENTS.values() for metric in schema})
    for metric in metrics:
        if metric not in out.columns:
            continue
        values = pd.to_numeric(out[metric], errors="coerce")
        out[metric] = values
        # Prior-player estimate: expanding mean shifted one game, so the current
        # observation is never in its own baseline.
        player_mean = (
            out.assign(_v=values)
            .groupby("player_id", sort=False)["_v"]
            .transform(lambda series: series.expanding(min_periods=1).mean().shift(1))
        )
        player_games = (
            out.assign(_ok=values.notna().astype(float))
            .groupby("player_id", sort=False)["_ok"]
            .transform(lambda series: series.cumsum().shift(1).fillna(0.0))
        )

        # v0.28-fixed3: the shrinkage population must also be pregame.  The old
        # season-position mean included the current game and future games from the
        # same season.  Aggregate by position/week, then use only cumulative
        # observations from strictly earlier weeks/seasons.
        weekly = out[["position", "season", "week"]].copy()
        weekly["_v"] = values
        weekly = (
            weekly.dropna(subset=["_v"])
            .groupby(["position", "season", "week"], as_index=False)["_v"]
            .agg(["sum", "count"])
            .reset_index()
            .sort_values(["position", "season", "week"])
        )
        if len(weekly):
            weekly["_prior_sum"] = weekly.groupby("position", sort=False)["sum"].cumsum() - weekly["sum"]
            weekly["_prior_count"] = weekly.groupby("position", sort=False)["count"].cumsum() - weekly["count"]
            weekly["_pregame_pop"] = np.where(
                weekly["_prior_count"] > 0,
                weekly["_prior_sum"] / weekly["_prior_count"],
                np.nan,
            )
            pop_map = weekly.set_index(["position", "season", "week"])["_pregame_pop"]
            keys = pd.MultiIndex.from_frame(out[["position", "season", "week"]])
            pop = pd.Series(pop_map.reindex(keys).to_numpy(dtype=float), index=out.index)
        else:
            pop = pd.Series(np.nan, index=out.index, dtype=float)

        lam = player_games / (player_games + max(float(shrink_games), 1.0))
        baseline = lam * player_mean + (1.0 - lam) * pop
        baseline = baseline.where(player_games >= int(min_games))
        out[f"baseline_{metric}"] = baseline
        out[f"prior_games_{metric}"] = player_games
    return out


def _pregame_defense_states(
    *,
    seasons: list[int],
    cache_dir: Path,
    shrinkage_plays: float,
    weeks_by_season: dict[int, list[int]] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    players_path = _download(PLAYERS_URL, cache_dir / "players.csv", refresh=False)
    position_index = _player_position_index(players_path)
    rows: list[dict[str, Any]] = []
    opponent_rows: list[dict[str, Any]] = []
    sources: dict[str, Any] = {"players": {"path": str(players_path), "sha256": _sha256(players_path)}, "pbp": {}}

    for season in seasons:
        prior_path = _download(PBP_URL.format(season=season - 1), cache_dir / f"play_by_play_{season - 1}.csv.gz", refresh=False)
        current_path = _download(PBP_URL.format(season=season), cache_dir / f"play_by_play_{season}.csv.gz", refresh=False)
        prior_pbp = _read_pbp(prior_path)
        current_pbp = _read_pbp(current_path)
        prior_profiles = aggregate_team_profiles(prior_pbp, receiver_positions=position_index)

        # Current stats_player weekly files do not consistently carry an
        # opponent column.  Historical PBP does: for each offensive team/week,
        # posteam and defteam identify the opponent.  Build this map once and
        # use it only to recover missing schedule identity, never as a matchup
        # performance feature.
        if len(current_pbp) and {"week", "posteam", "defteam"}.issubset(current_pbp.columns):
            map_frame = current_pbp[["week", "posteam", "defteam"]].copy()
            if "season_type" in current_pbp.columns:
                reg_mask = current_pbp["season_type"].astype(str).str.upper().eq("REG")
                map_frame = map_frame.loc[reg_mask]
            map_frame["week"] = pd.to_numeric(map_frame["week"], errors="coerce")
            map_frame = map_frame.dropna(subset=["week", "posteam", "defteam"])
            for rec in map_frame.drop_duplicates().to_dict("records"):
                team = normalize_team(rec.get("posteam"))
                opponent = normalize_team(rec.get("defteam"))
                if team and opponent:
                    opponent_rows.append({
                        "season": int(season),
                        "week": int(rec["week"]),
                        "team": team,
                        "opponent_from_pbp": opponent,
                    })
        requested_weeks = sorted({int(w) for w in (weeks_by_season or {}).get(int(season), []) if int(w) > 0})
        if requested_weeks:
            weeks = requested_weeks
        else:
            week_values = pd.to_numeric(current_pbp.get("week"), errors="coerce") if len(current_pbp) else pd.Series(dtype=float)
            max_week = int(week_values.max()) if len(week_values.dropna()) else 18
            weeks = list(range(1, max_week + 1))
        for week in weeks:
            current_profiles = aggregate_team_profiles(
                current_pbp,
                receiver_positions=position_index,
                max_week=week - 1,
            ) if week > 1 else {"defense": {}, "offense": {}, "league": {}}
            context = build_matchup_context(
                pd.DataFrame(),
                season=season,
                current_week=week,
                prior_profiles=prior_profiles,
                current_profiles=current_profiles,
                shrinkage_plays=shrinkage_plays,
            )
            for team, z in (context.get("defense_zscores") or {}).items():
                row: dict[str, Any] = {"season": season, "week": week, "opponent": normalize_team(team)}
                for key, value in z.items():
                    try:
                        row[f"def_{key}"] = float(value)
                    except (TypeError, ValueError):
                        pass
                rows.append(row)
        sources["pbp"][str(season - 1)] = {"path": str(prior_path), "sha256": _sha256(prior_path)}
        sources["pbp"][str(season)] = {"path": str(current_path), "sha256": _sha256(current_path)}
    defense = pd.DataFrame(rows)
    if len(defense):
        defense = defense.drop_duplicates(["season", "week", "opponent"])
    opponent_map = pd.DataFrame(opponent_rows)
    if len(opponent_map):
        opponent_map = opponent_map.drop_duplicates(["season", "week", "team"])
    return defense, opponent_map, sources


def build_training_rows(
    stats_path: str | Path,
    *,
    seasons: list[int],
    cache_dir: str | Path,
    min_prior_games: int = 3,
    baseline_shrink_games: float = 8.0,
    defense_shrinkage_plays: float = 400.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    stats_path = Path(stats_path)
    stats = pd.read_csv(stats_path, low_memory=False, compression="infer")
    weekly = _prepare_weekly_player_stats(stats)
    weekly = weekly[weekly["season"].isin([int(s) for s in seasons])].copy()
    weekly = _rolling_baselines(weekly, min_games=min_prior_games, shrink_games=baseline_shrink_games)
    weeks_by_season = {
        int(season): sorted(pd.to_numeric(group["week"], errors="coerce").dropna().astype(int).unique().tolist())
        for season, group in weekly.groupby("season")
    }
    defense, opponent_map, sources = _pregame_defense_states(
        seasons=[int(s) for s in seasons],
        cache_dir=Path(cache_dir),
        shrinkage_plays=defense_shrinkage_plays,
        weeks_by_season=weeks_by_season,
    )

    # Recover opponent identity from PBP when the modern stats_player weekly
    # schema supplies recent_team but no opponent_team/game_id.  Existing
    # explicit opponent values remain authoritative.
    if len(opponent_map) and "team" in weekly.columns:
        weekly = weekly.merge(
            opponent_map,
            on=["season", "week", "team"],
            how="left",
            validate="many_to_one",
        )
        weekly["opponent"] = weekly["opponent"].where(
            weekly["opponent"].notna(), weekly["opponent_from_pbp"]
        )
        weekly = weekly.drop(columns=["opponent_from_pbp"])

    joined = weekly.merge(defense, on=["season", "week", "opponent"], how="left", validate="many_to_one")
    sources["player_stats"] = {"path": str(stats_path), "sha256": _sha256(stats_path)}
    sources["opponent_mapping"] = {
        "method": "STATS_EXPLICIT_THEN_PBP_POSTEAM_DEFTEAM",
        "rows": int(len(opponent_map)),
    }
    return joined, sources


def _coverage_summary(rows: pd.DataFrame, seasons: list[int]) -> dict[str, Any]:
    defense_cols = [column for column in rows.columns if column.startswith("def_")]
    summary: dict[str, Any] = {"seasons": {}, "defense_columns": defense_cols}
    for season in seasons:
        season_rows = rows[rows["season"].eq(int(season))].copy()
        if defense_cols:
            defense_matched = season_rows[defense_cols].notna().any(axis=1)
        else:
            defense_matched = pd.Series(False, index=season_rows.index)
        component_usable: dict[str, int] = {}
        for position, components in DEFAULT_COMPONENTS.items():
            pos_rows = season_rows[season_rows["position"].eq(position)]
            for component, defense_feature in components.items():
                baseline_col = f"baseline_{component}"
                defense_col = f"def_{defense_feature}"
                if component not in pos_rows or baseline_col not in pos_rows or defense_col not in pos_rows:
                    continue
                usable = (
                    pd.to_numeric(pos_rows[baseline_col], errors="coerce").notna()
                    & (pd.to_numeric(pos_rows[baseline_col], errors="coerce") > 1e-9)
                    & pd.to_numeric(pos_rows[component], errors="coerce").notna()
                    & pd.to_numeric(pos_rows[defense_col], errors="coerce").notna()
                )
                component_usable[f"{position}.{component}"] = int(usable.sum())
        summary["seasons"][str(int(season))] = {
            "rows": int(len(season_rows)),
            "opponent_present": int(season_rows["opponent"].notna().sum()) if "opponent" in season_rows else 0,
            "defense_matched": int(defense_matched.sum()),
            "defense_match_fraction": float(defense_matched.mean()) if len(season_rows) else 0.0,
            "components_usable": component_usable,
        }
    return summary


def _centers_from_quantiles(values: np.ndarray, bins: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.asarray([0.0], dtype=float)
    q = np.linspace(0.05, 0.95, max(int(bins), 2))
    centers = np.unique(np.quantile(values, q))
    if len(centers) < 2:
        scale = max(abs(float(centers[0])) * 0.1, 0.1)
        centers = np.asarray([float(centers[0]) - scale, float(centers[0]) + scale])
    return centers.astype(float)


def _nearest(values: np.ndarray, x: float) -> int:
    return int(np.argmin(np.abs(np.asarray(values, dtype=float) - float(x))))


def fit_grid(
    rows: pd.DataFrame,
    *,
    baseline_col: str,
    observed_col: str,
    defense_col: str,
    baseline_bins: int,
    defense_centers: np.ndarray,
    shrink_n: float,
    ratio_min: float,
    ratio_max: float,
    uncertainty_floor: float,
) -> dict[str, np.ndarray]:
    work = rows[[baseline_col, observed_col, defense_col]].copy()
    for col in work.columns:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    work = work.dropna()
    work = work[(work[baseline_col] > 1e-9) & np.isfinite(work[defense_col])]
    if work.empty:
        raise ValueError(f"No usable rows for grid {observed_col} × {defense_col}")
    work["ratio"] = (work[observed_col] / work[baseline_col]).clip(float(ratio_min), float(ratio_max))
    x_centers = _centers_from_quantiles(work[baseline_col].to_numpy(float), baseline_bins)
    z_centers = np.asarray(defense_centers, dtype=float)
    shape = (len(x_centers), len(z_centers))
    raw = np.ones(shape, dtype=float)
    correction = np.ones(shape, dtype=float)
    uncertainty = np.full(shape, float(uncertainty_floor), dtype=float)
    support = np.zeros(shape, dtype=float)

    buckets: dict[tuple[int, int], list[float]] = {}
    for rec in work.to_dict("records"):
        ix = _nearest(x_centers, float(rec[baseline_col]))
        iz = _nearest(z_centers, float(rec[defense_col]))
        buckets.setdefault((ix, iz), []).append(float(rec["ratio"]))
    for ix in range(shape[0]):
        for iz in range(shape[1]):
            vals = np.asarray(buckets.get((ix, iz), []), dtype=float)
            n = len(vals)
            support[ix, iz] = float(n)
            if n == 0:
                continue
            mean = float(np.mean(vals))
            raw[ix, iz] = mean
            lam = n / (n + max(float(shrink_n), 1.0))
            correction[ix, iz] = 1.0 + lam * (mean - 1.0)
            if n >= 2:
                se = float(np.std(vals, ddof=1) / math.sqrt(n))
                uncertainty[ix, iz] = max(float(uncertainty_floor), lam * se + (1.0 - lam) * float(uncertainty_floor))

    # One conservative neighbor smoothing pass. Cells retain their own correction
    # when well populated; sparse cells borrow only from immediate neighbors and a
    # unit-correction prior.
    smoothed = correction.copy()
    for ix in range(shape[0]):
        for iz in range(shape[1]):
            num = correction[ix, iz] * (support[ix, iz] + shrink_n)
            den = support[ix, iz] + shrink_n
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                jx, jz = ix + dx, iz + dz
                if 0 <= jx < shape[0] and 0 <= jz < shape[1] and support[jx, jz] > 0:
                    w = min(support[jx, jz], shrink_n) * 0.20
                    num += correction[jx, jz] * w
                    den += w
            smoothed[ix, iz] = num / max(den, 1e-12)

    return {
        "baseline_centers": x_centers,
        "defense_z_centers": z_centers,
        "raw_correction": raw,
        "correction": smoothed,
        "uncertainty": uncertainty,
        "support": support,
    }


def _grid_predict(grid: dict[str, np.ndarray], baseline: pd.Series, defense_z: pd.Series) -> np.ndarray:
    values = []
    for x, z in zip(pd.to_numeric(baseline, errors="coerce"), pd.to_numeric(defense_z, errors="coerce")):
        if not np.isfinite(x) or not np.isfinite(z):
            values.append(np.nan)
            continue
        corr, _sd, _support = interpolate_grid(grid, float(x), float(z))
        values.append(corr)
    return np.asarray(values, dtype=float)


def _validation_metrics(rows: pd.DataFrame, grid: dict[str, np.ndarray], *, baseline_col: str, observed_col: str, defense_col: str) -> dict[str, float | int | bool]:
    raw = rows[[baseline_col, observed_col, defense_col]].copy()
    diagnostics = {
        "rows": int(len(raw)),
        "baseline_present": int(pd.to_numeric(raw[baseline_col], errors="coerce").notna().sum()),
        "observed_present": int(pd.to_numeric(raw[observed_col], errors="coerce").notna().sum()),
        "defense_present": int(pd.to_numeric(raw[defense_col], errors="coerce").notna().sum()),
    }
    work = raw.dropna()
    work = work[pd.to_numeric(work[baseline_col], errors="coerce") > 1e-9]
    if work.empty:
        return {
            **diagnostics,
            "n": 0,
            "mae_ratio_before": float("nan"),
            "mae_ratio_after": float("nan"),
            "improvement": float("nan"),
            "commissioned": False,
        }
    ratio = np.asarray(work[observed_col] / work[baseline_col], dtype=float)
    corr = _grid_predict(grid, work[baseline_col], work[defense_col])
    valid = np.isfinite(ratio) & np.isfinite(corr) & (corr > 1e-9)
    ratio = ratio[valid]
    corr = corr[valid]
    before = float(np.mean(np.abs(ratio - 1.0))) if len(ratio) else float("nan")
    after = float(np.mean(np.abs(ratio / corr - 1.0))) if len(ratio) else float("nan")
    improvement = before - after if math.isfinite(before) and math.isfinite(after) else float("nan")
    return {
        **diagnostics,
        "n": int(len(ratio)),
        "mae_ratio_before": before,
        "mae_ratio_after": after,
        "improvement": improvement,
        "commissioned": bool(len(ratio) >= 50 and math.isfinite(improvement) and improvement > 0.0),
    }


def _player_baselines(stats: pd.DataFrame, *, seasons: list[int], games: int) -> tuple[dict[str, Any], dict[str, Any]]:
    df = _prepare_weekly_player_stats(stats)
    df = df[df["season"].isin(seasons)].sort_values(["player_id", "season", "week"])
    metrics = sorted({metric for schema in DEFAULT_COMPONENTS.values() for metric in schema})
    players: dict[str, Any] = {}
    for player_id, group in df.groupby("player_id"):
        tail = group.tail(max(int(games), 1))
        position = str(tail.iloc[-1]["position"])
        row: dict[str, Any] = {"position": position, "games": int(len(tail))}
        for metric in metrics:
            if metric not in tail.columns:
                continue
            vals = pd.to_numeric(tail[metric], errors="coerce").dropna()
            if len(vals):
                row[metric] = float(vals.mean())
        players[str(player_id)] = row
    positions: dict[str, Any] = {}
    for position, group in df.groupby("position"):
        row: dict[str, Any] = {"position": position, "games": int(len(group))}
        for metric in metrics:
            if metric not in group.columns:
                continue
            vals = pd.to_numeric(group[metric], errors="coerce").dropna()
            if len(vals):
                row[metric] = float(vals.median())
        positions[str(position)] = row
    return players, positions


def fit_interaction_grids(
    *,
    stats_path: str | Path,
    model: dict[str, Any],
    cache_dir: str | Path,
    out_dir: str | Path,
    seasons: list[int] | None = None,
) -> FitResult:
    cfg = model.get("interaction_grid") or {}
    fit_cfg = cfg.get("fit") or {}
    seasons = [int(s) for s in (seasons or fit_cfg.get("seasons") or [2022, 2023, 2024, 2025])]
    if len(seasons) < 2:
        raise ValueError("interaction-fit needs at least two seasons so the latest season can be held out chronologically")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows, sources = build_training_rows(
        stats_path,
        seasons=seasons,
        cache_dir=cache_dir,
        min_prior_games=int(fit_cfg.get("minimum_prior_games", 3)),
        baseline_shrink_games=float(fit_cfg.get("baseline_shrink_games", 8.0)),
        defense_shrinkage_plays=float(fit_cfg.get("defense_shrinkage_plays", 400.0)),
    )
    train_seasons = seasons[:-1]
    validation_season = seasons[-1]
    coverage = _coverage_summary(rows, seasons)
    coverage_path = out_dir / "coverage.json"
    coverage_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    holdout_coverage = (coverage.get("seasons") or {}).get(str(validation_season), {})
    usable_holdout = sum(int(value) for value in (holdout_coverage.get("components_usable") or {}).values())
    if int(holdout_coverage.get("rows") or 0) == 0:
        reason = (
            f"interaction-fit validation season {validation_season} has zero player rows; "
            f"see {coverage_path}"
        )
        _write_fit_failure(out_dir, reason=reason, validation_season=validation_season, coverage_path=coverage_path)
        raise ValueError(reason)
    if int(holdout_coverage.get("defense_matched") or 0) == 0:
        reason = (
            f"interaction-fit validation season {validation_season} has zero player×defense matches; "
            f"the previous v0.28 behavior would silently report n=0 for every component. "
            f"See {coverage_path}"
        )
        _write_fit_failure(out_dir, reason=reason, validation_season=validation_season, coverage_path=coverage_path)
        raise ValueError(reason)
    if usable_holdout == 0:
        reason = (
            f"interaction-fit validation season {validation_season} has defense matches but zero usable "
            f"baseline/stat component rows; see {coverage_path}"
        )
        _write_fit_failure(out_dir, reason=reason, validation_season=validation_season, coverage_path=coverage_path)
        raise ValueError(reason)

    defense_centers = np.asarray(fit_cfg.get("defense_z_centers", [-2.0, -1.0, 0.0, 1.0, 2.0]), dtype=float)
    grid_count = 0
    validation: dict[str, Any] = {
        "validation_season": validation_season,
        "train_seasons": train_seasons,
        "coverage": holdout_coverage,
        "components": {},
    }

    for position, components in DEFAULT_COMPONENTS.items():
        pos_dir = out_dir / position
        pos_dir.mkdir(parents=True, exist_ok=True)
        validation["components"].setdefault(position, {})
        for component, defense_feature in components.items():
            baseline_col = f"baseline_{component}"
            defense_col = f"def_{defense_feature}"
            if component not in rows.columns or baseline_col not in rows.columns or defense_col not in rows.columns:
                continue
            relevant = rows[rows["position"].eq(position)].copy()
            train = relevant[relevant["season"].isin(train_seasons)]
            holdout = relevant[relevant["season"].eq(validation_season)]
            try:
                validation_grid = fit_grid(
                    train,
                    baseline_col=baseline_col,
                    observed_col=component,
                    defense_col=defense_col,
                    baseline_bins=int(fit_cfg.get("baseline_bins", 5)),
                    defense_centers=defense_centers,
                    shrink_n=float(fit_cfg.get("cell_shrink_n", 30.0)),
                    ratio_min=float(fit_cfg.get("ratio_min", 0.25)),
                    ratio_max=float(fit_cfg.get("ratio_max", 1.75)),
                    uncertainty_floor=float(fit_cfg.get("uncertainty_floor", 0.03)),
                )
            except ValueError:
                continue
            metrics = _validation_metrics(
                holdout,
                validation_grid,
                baseline_col=baseline_col,
                observed_col=component,
                defense_col=defense_col,
            )
            commissioned = bool(metrics["commissioned"])
            validation["components"][position][component] = metrics

            final_grid = fit_grid(
                relevant,
                baseline_col=baseline_col,
                observed_col=component,
                defense_col=defense_col,
                baseline_bins=int(fit_cfg.get("baseline_bins", 5)),
                defense_centers=defense_centers,
                shrink_n=float(fit_cfg.get("cell_shrink_n", 30.0)),
                ratio_min=float(fit_cfg.get("ratio_min", 0.25)),
                ratio_max=float(fit_cfg.get("ratio_max", 1.75)),
                uncertainty_floor=float(fit_cfg.get("uncertainty_floor", 0.03)),
            )
            np.savez_compressed(pos_dir / f"{component}.npz", **final_grid)
            (pos_dir / f"{component}.json").write_text(json.dumps({
                "position": position,
                "component": component,
                "defense_feature": defense_feature,
                "commissioned": commissioned,
                "validation": metrics,
                "training_rows": int(relevant[[baseline_col, component, defense_col]].dropna().shape[0]),
            }, indent=2), encoding="utf-8")
            grid_count += 1

    raw_stats = pd.read_csv(stats_path, low_memory=False, compression="infer")
    players, positions = _player_baselines(
        raw_stats,
        seasons=seasons,
        games=int(fit_cfg.get("current_baseline_games", 8)),
    )
    (out_dir / "player_baselines.json").write_text(json.dumps({"players": players}, indent=2), encoding="utf-8")
    (out_dir / "position_baselines.json").write_text(json.dumps({"positions": positions}, indent=2), encoding="utf-8")
    validation_path = out_dir / "validation.json"
    validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    artifact_id = str(cfg.get("artifact_id") or "offense_defense_interaction_v001")
    manifest = {
        "schema_version": 1,
        "artifact_id": artifact_id,
        "model_version": "0.28",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "training_seasons": seasons,
        "validation_season": validation_season,
        "baseline_method": "ROLLING_PLAYER_COMPONENT_MEAN_SHRUNK_TO_STRICTLY_PREGAME_POSITION_V028_FIXED2",
        "correction_definition": "observed_football_stat / pregame_baseline_football_stat",
        "fantasy_points_used_in_fit": False,
        "interpolation": "bilinear_on_component_baseline_x_defense_z",
        "grids": int(grid_count),
        "training_rows_total": int(len(rows)),
        "sources": sources,
        "notes": [
            "All defense coordinates are reconstructed pregame; current-week outcomes are excluded from their own predictors.",
            "v0.28-fixed3 generates defense-state weeks from the player-stat weeks requested for each season and audits player×defense merge coverage before fitting.",
            "Player baselines and their population shrinkage reference use only observations from strictly earlier games/weeks; current/future season observations are excluded.",
            "Fantasy scoring is not a training target. Scoring is applied only downstream when component corrections are propagated to the fantasy-yield response.",
            "Each component is chronologically validated on the latest configured season; uncommissioned grids remain diagnostic and are neutralized operationally by default.",
        ],
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Persist a compact training manifest, not the large joined table, to keep the
    # weekly project light. The underlying nflverse caches are retained separately.
    (out_dir / "training_summary.json").write_text(json.dumps({
        "rows": int(len(rows)),
        "positions": rows["position"].value_counts().to_dict() if len(rows) else {},
        "season_rows": rows["season"].value_counts().sort_index().to_dict() if len(rows) else {},
        "coverage": coverage,
    }, indent=2), encoding="utf-8")
    failure_marker = out_dir / "fit_failure.json"
    if failure_marker.exists():
        failure_marker.unlink()
    return FitResult(out_dir, manifest_path, validation_path, int(len(rows)), int(grid_count))
