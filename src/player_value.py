from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


CORE_POSITIONS = ["QB", "RB", "WR", "TE"]


def load_model_config(path: str | Path) -> dict:
    with Path(path).open() as f:
        return json.load(f)


def robust_sigma(values) -> float:
    arr = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(float)
    if len(arr) < 2:
        return float("nan")
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    sigma = 1.4826 * mad
    if sigma <= 0:
        sigma = float(np.std(arr, ddof=1))
    return sigma


def _bool_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    s = df[col]
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def calibrate_projection_uncertainty(
    df: pd.DataFrame,
    cfg: dict,
    transition: dict[str, dict],
) -> dict[str, dict]:
    """Infer projection uncertainty after accounting for historical drift.

    Current cross-sectional residuals satisfy approximately

        sigma(residual)^2 ~= sigma(history-to-2026)^2 + sigma(projection)^2

    so the projection component is estimated by quadrature subtraction, with a
    position-dependent floor.
    """
    season_games = float(cfg["season_games"])
    floors = {k: float(v) for k, v in cfg["projection_sigma_floor_ppg"].items()}
    min_n = int(cfg.get("minimum_calibration_players", 8))

    work = df.copy()
    work["projection_ppg"] = pd.to_numeric(
        work.get("espn_proj_points"), errors="coerce"
    ) / season_games
    work["historical_prior_mean_ppg"] = pd.to_numeric(
        work.get("historical_prior_mean_ppg"), errors="coerce"
    )

    pooled_residuals = (
        work["projection_ppg"] - work["historical_prior_mean_ppg"]
    ).dropna()
    pooled_sigma = robust_sigma(pooled_residuals)
    if not np.isfinite(pooled_sigma):
        pooled_sigma = 4.0

    result = {}
    for pos in CORE_POSITIONS:
        g = work[work["position"].eq(pos)]
        residual = (
            g["projection_ppg"] - g["historical_prior_mean_ppg"]
        ).dropna()
        resid_sigma = robust_sigma(residual)
        if len(residual) < min_n or not np.isfinite(resid_sigma):
            resid_sigma = pooled_sigma

        hist_transition = float(
            transition.get(pos, {}).get("transition_sigma_ppg", 0.0)
        )
        floor = floors.get(pos, 2.0)
        proj_component_sq = max(
            float(resid_sigma) ** 2 - hist_transition ** 2,
            float(floor) ** 2,
        )
        proj_sigma = float(np.sqrt(proj_component_sq))

        result[pos] = {
            "n": int(len(residual)),
            "residual_sigma_ppg": float(resid_sigma),
            "historical_transition_sigma_ppg": hist_transition,
            "projection_sigma_ppg": proj_sigma,
        }
    return result


def _historical_mean_sigma(
    row: pd.Series,
    cfg: dict,
    transition_sigma: float,
) -> float:
    pos = row.get("position")
    floors = cfg["historical_mean_floor_ppg"]
    floor = float(floors.get(pos, 1.5))

    weekly_sd = pd.to_numeric(
        pd.Series([row.get("historical_prior_sd_weekly")]), errors="coerce"
    ).iloc[0]
    games = pd.to_numeric(
        pd.Series([row.get("historical_games")]), errors="coerce"
    ).iloc[0]

    if pd.isna(weekly_sd) or pd.isna(games) or games <= 0:
        sampling = floor
    else:
        sampling = max(
            floor,
            float(weekly_sd) / np.sqrt(float(games)),
        )

    # Historical data are not a stationary measurement of the 2026 mean.
    # Add empirical year-to-year player drift as a systematic/transition term.
    return float(
        np.sqrt(
            sampling ** 2
            + float(transition_sigma) ** 2
        )
    )


def _is_rookie_like(row: pd.Series) -> bool:
    # Explicit rookie flag if later added.
    explicit = row.get("rookie")
    if explicit is not None and not pd.isna(explicit):
        if str(explicit).lower() in ("true", "1", "yes"):
            return True

    yoe = row.get("years_of_experience")
    try:
        if not pd.isna(yoe) and float(yoe) <= 0:
            return True
    except (TypeError, ValueError):
        pass

    # In the current pipeline, a current player with no historical prior is
    # often a rookie or a player without recent NFL fantasy history. We label
    # this separately from a confirmed rookie.
    return False


def build_player_values(
    master_path: str | Path,
    model_config_path: str | Path,
    out_path: str | Path,
    calibration_path: str | Path | None = None,
    stats_path: str | Path | None = None,
    transition_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    master = pd.read_csv(master_path, low_memory=False)
    cfg_all = load_model_config(model_config_path)
    cfg = cfg_all["latent_value"]

    master = master[master["position"].isin(CORE_POSITIONS)].copy()

    master["espn_proj_points"] = pd.to_numeric(
        master.get("espn_proj_points"), errors="coerce"
    )
    master["projection_ppg"] = master["espn_proj_points"] / float(cfg["season_games"])
    master["historical_prior_mean_ppg"] = pd.to_numeric(
        master.get("historical_prior_mean_ppg"), errors="coerce"
    )
    master["historical_prior_sd_weekly"] = pd.to_numeric(
        master.get("historical_prior_sd_weekly"), errors="coerce"
    )
    master["historical_games"] = pd.to_numeric(
        master.get("historical_games"), errors="coerce"
    )

    from .transition import calibrate_year_to_year_transition

    tcfg = cfg["transition_calibration"]
    if stats_path is None:
        raise ValueError("stats_path is required for transition calibration")

    transition, transition_pairs = calibrate_year_to_year_transition(
        stats_path,
        seasons=[int(s) for s in tcfg["seasons"]],
        minimum_games_per_season=int(tcfg["minimum_games_per_season"]),
        minimum_pairs_per_position=int(tcfg["minimum_pairs_per_position"]),
        sigma_floors=tcfg["transition_sigma_floor_ppg"],
    )

    calibration = calibrate_projection_uncertainty(master, cfg, transition)

    if transition_path is not None:
        transition_path = Path(transition_path)
        transition_path.parent.mkdir(parents=True, exist_ok=True)
        transition_path.write_text(json.dumps({
            "position_calibration": transition,
            "pairs": int(len(transition_pairs)),
        }, indent=2))

    records = []
    for _, row in master.iterrows():
        pos = row["position"]
        hist_mean = row["historical_prior_mean_ppg"]
        proj_mean = row["projection_ppg"]
        has_hist = pd.notna(hist_mean)
        has_proj = pd.notna(proj_mean) and float(proj_mean) > 0

        transition_sigma = float(
            transition.get(pos, {}).get("transition_sigma_ppg", 0.0)
        )
        hist_sigma_mean = (
            _historical_mean_sigma(row, cfg, transition_sigma)
            if has_hist else np.nan
        )
        proj_sigma = float(calibration[pos]["projection_sigma_ppg"])

        rookie_like = _is_rookie_like(row)
        history_games = row["historical_games"]
        limited_history = (
            has_hist
            and pd.notna(history_games)
            and float(history_games) < float(cfg["limited_history_games"])
        )

        if rookie_like:
            proj_sigma *= float(cfg["rookie_epistemic_multiplier"])
        elif limited_history:
            proj_sigma *= float(cfg["limited_history_multiplier"])

        if has_hist and has_proj:
            wh = 1.0 / (hist_sigma_mean ** 2)
            wp = 1.0 / (proj_sigma ** 2)
            latent_mean = (wh * float(hist_mean) + wp * float(proj_mean)) / (wh + wp)
            latent_mean_sd = np.sqrt(1.0 / (wh + wp))
            model_status = "history+projection"
            hist_weight = wh / (wh + wp)
            proj_weight = wp / (wh + wp)
        elif has_proj:
            latent_mean = float(proj_mean)
            latent_mean_sd = float(proj_sigma)
            model_status = "projection_only"
            hist_weight = 0.0
            proj_weight = 1.0
        elif has_hist:
            latent_mean = float(hist_mean)
            latent_mean_sd = float(hist_sigma_mean)
            model_status = "history_only"
            hist_weight = 1.0
            proj_weight = 0.0
        else:
            latent_mean = np.nan
            latent_mean_sd = np.nan
            model_status = "insufficient"
            hist_weight = np.nan
            proj_weight = np.nan

        weekly_sd = row["historical_prior_sd_weekly"]
        if pd.isna(weekly_sd) or float(weekly_sd) <= 0:
            weekly_sd = float(cfg["weekly_sd_fallback_ppg"].get(pos, 7.0))

        predictive_sd = (
            np.sqrt(float(weekly_sd) ** 2 + float(latent_mean_sd) ** 2)
            if pd.notna(latent_mean_sd)
            else np.nan
        )

        rec = row.to_dict()
        rec.update({
            "projection_sigma_ppg": proj_sigma,
            "historical_transition_sigma_ppg": transition_sigma,
            "historical_mean_sigma_ppg": hist_sigma_mean,
            "latent_mean_ppg": latent_mean,
            "latent_mean_sd_ppg": latent_mean_sd,
            "weekly_aleatoric_sd_ppg": weekly_sd,
            "predictive_weekly_sd_ppg": predictive_sd,
            "history_weight": hist_weight,
            "projection_weight": proj_weight,
            "model_status": model_status,
            "rookie_like": rookie_like,
            "limited_history": limited_history,
        })
        records.append(rec)

    out = pd.DataFrame(records)

    # Keep market information separate, but make a convenient ordering for
    # diagnostics. Lower ADP/rank is better.
    out["espn_adp"] = pd.to_numeric(out.get("espn_adp"), errors="coerce")
    out["espn_rank"] = pd.to_numeric(out.get("espn_rank"), errors="coerce")

    sort_cols = ["latent_mean_ppg", "espn_adp"]
    out = out.sort_values(sort_cols, ascending=[False, True], na_position="last")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    if calibration_path is not None:
        calibration_path = Path(calibration_path)
        calibration_path.parent.mkdir(parents=True, exist_ok=True)
        calibration_path.write_text(json.dumps(calibration, indent=2))

    return out, calibration


def player_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pos, g in df.groupby("position"):
        rows.append({
            "position": pos,
            "players": int(len(g)),
            "history+projection": int((g["model_status"] == "history+projection").sum()),
            "projection_only": int((g["model_status"] == "projection_only").sum()),
            "history_only": int((g["model_status"] == "history_only").sum()),
            "insufficient": int((g["model_status"] == "insufficient").sum()),
            "modeled": int(g["latent_mean_ppg"].notna().sum()),
        })
    return pd.DataFrame(rows).sort_values("position")
