from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


CORE_POSITIONS = {"QB", "RB", "WR", "TE", "K"}


def load_model_config(path: str | Path):
    with Path(path).open() as f:
        return json.load(f)


def _custom_ppr_points(df: pd.DataFrame) -> pd.Series:
    def c(name):
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce").fillna(0.0)
        return pd.Series(0.0, index=df.index)

    fumbles_lost = c("sack_fumbles_lost") + c("rushing_fumbles_lost") + c("receiving_fumbles_lost")
    return (
        0.04 * c("passing_yards")
        + 4.0 * c("passing_tds")
        - 2.0 * c("passing_interceptions")
        + 2.0 * c("passing_2pt_conversions")
        + 0.1 * c("rushing_yards")
        + 6.0 * c("rushing_tds")
        + 2.0 * c("rushing_2pt_conversions")
        + 1.0 * c("receptions")
        + 0.1 * c("receiving_yards")
        + 6.0 * c("receiving_tds")
        + 2.0 * c("receiving_2pt_conversions")
        + 6.0 * c("special_teams_tds")
        - 2.0 * fumbles_lost
    )


def _season_table(stats: pd.DataFrame, seasons: list[int]) -> pd.DataFrame:
    stats = stats.copy()
    if "season_type" in stats.columns:
        stats = stats[stats["season_type"].astype(str).eq("REG")]
    stats = stats[stats["season"].isin(seasons)]

    if "fantasy_points_ppr" in stats.columns:
        stats["custom_ppr"] = pd.to_numeric(stats["fantasy_points_ppr"], errors="coerce")
        missing = stats["custom_ppr"].isna()
        if missing.any():
            stats.loc[missing, "custom_ppr"] = _custom_ppr_points(stats.loc[missing])
    else:
        stats["custom_ppr"] = _custom_ppr_points(stats)

    # nflverse may be weekly or season-summary depending on release/version.
    if "week" in stats.columns and stats["week"].notna().any():
        group_cols = ["player_id", "season"]
        agg = {
            "custom_ppr": "sum",
            "week": "nunique",
        }
        for optional in ["player_display_name", "player_name", "position", "position_group", "recent_team", "team"]:
            if optional in stats.columns:
                agg[optional] = "last"

        season_df = stats.groupby(group_cols, as_index=False).agg(agg)
        season_df = season_df.rename(columns={"week": "games"})
    else:
        season_df = stats.copy()
        if "games" not in season_df.columns:
            season_df["games"] = 1

    season_df["games"] = pd.to_numeric(season_df["games"], errors="coerce").fillna(0)
    season_df["ppg"] = np.where(
        season_df["games"] > 0,
        pd.to_numeric(season_df["custom_ppr"], errors="coerce") / season_df["games"],
        np.nan,
    )
    return season_df


def _weekly_table(stats: pd.DataFrame, seasons: list[int]) -> pd.DataFrame:
    stats = stats.copy()
    if "season_type" in stats.columns:
        stats = stats[stats["season_type"].astype(str).eq("REG")]
    stats = stats[stats["season"].isin(seasons)]
    if "week" not in stats.columns:
        return pd.DataFrame()

    if "fantasy_points_ppr" in stats.columns:
        stats["custom_ppr"] = pd.to_numeric(stats["fantasy_points_ppr"], errors="coerce")
        missing = stats["custom_ppr"].isna()
        if missing.any():
            stats.loc[missing, "custom_ppr"] = _custom_ppr_points(stats.loc[missing])
    else:
        stats["custom_ppr"] = _custom_ppr_points(stats)
    return stats


def build_historical_priors(
    stats_path: str | Path,
    model_config_path: str | Path,
    out_path: str | Path,
) -> pd.DataFrame:
    cfg = load_model_config(model_config_path)["historical_prior"]
    seasons = [int(s) for s in cfg["seasons"]]
    weights = {int(k): float(v) for k, v in cfg["season_weights"].items()}
    shrinkage_games = {k: float(v) for k, v in cfg["shrinkage_games"].items()}

    stats = pd.read_csv(stats_path, low_memory=False)
    season_df = _season_table(stats, seasons)
    weekly_df = _weekly_table(stats, seasons)

    if "position" not in season_df.columns:
        raise ValueError("nflverse stats are missing required 'position' column")

    season_df = season_df[season_df["position"].isin(CORE_POSITIONS)]
    season_df["season_weight"] = season_df["season"].map(weights).fillna(0.0)
    season_df["weighted_ppg"] = season_df["ppg"] * season_df["season_weight"]

    # Position baseline: weighted across player-seasons by games and recency.
    pop = season_df.dropna(subset=["ppg"]).copy()
    pop["pop_weight"] = pop["games"] * pop["season_weight"]
    # Avoid DataFrameGroupBy.apply(include_groups=...), which is only
    # available in newer pandas releases. A simple explicit group loop is
    # compatible with older Conda pandas versions and is clearer here.
    pos_baseline = {}
    for position, group in pop.groupby("position"):
        total_weight = float(group["pop_weight"].sum())
        if total_weight > 0:
            pos_baseline[position] = float(
                np.average(
                    group["ppg"].to_numpy(float),
                    weights=group["pop_weight"].to_numpy(float),
                )
            )
        else:
            pos_baseline[position] = np.nan

    records = []
    for player_id, g in season_df.groupby("player_id"):
        g = g.dropna(subset=["ppg"])
        if g.empty:
            continue

        # Each season's influence is recency weight * games played.
        w = g["season_weight"].to_numpy(float) * g["games"].to_numpy(float)
        if w.sum() <= 0:
            continue
        raw_mean = float(np.average(g["ppg"].to_numpy(float), weights=w))
        games = float(g["games"].sum())

        pos = str(g.sort_values("season").iloc[-1]["position"])
        pop_mean = float(pos_baseline.get(pos, raw_mean))
        k = float(shrinkage_games.get(pos, 10.0))
        lam = games / (games + k)
        prior_mean = lam * raw_mean + (1.0 - lam) * pop_mean

        prior_sd = np.nan
        if not weekly_df.empty:
            wg = weekly_df[weekly_df["player_id"].eq(player_id)]
            vals = pd.to_numeric(wg["custom_ppr"], errors="coerce").dropna()
            if len(vals) >= 2:
                prior_sd = float(vals.std(ddof=1))

        name_col = "player_display_name" if "player_display_name" in g.columns else (
            "player_name" if "player_name" in g.columns else None
        )
        name = g.sort_values("season").iloc[-1][name_col] if name_col else None

        records.append({
            "gsis_id": player_id,
            "name": name,
            "position": pos,
            "historical_games": games,
            "historical_raw_ppg": raw_mean,
            "position_population_ppg": pop_mean,
            "shrinkage_lambda": lam,
            "historical_prior_mean_ppg": prior_mean,
            "historical_prior_sd_weekly": prior_sd,
            "history_start_season": int(g["season"].min()),
            "history_end_season": int(g["season"].max()),
        })

    out = pd.DataFrame(records)
    if not out.empty:
        out = out.sort_values(
            ["position", "historical_prior_mean_ppg"],
            ascending=[True, False]
        )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    return out
