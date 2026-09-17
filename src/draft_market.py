from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


CORE_POSITIONS = ["QB", "RB", "WR", "TE"]


def _load_json(path: str | Path) -> dict:
    with Path(path).open() as f:
        return json.load(f)


def _num(x):
    return pd.to_numeric(x, errors="coerce")


def _normal_survival(x: float, mean: float, sigma: float) -> float:
    if not np.isfinite(mean) or not np.isfinite(sigma) or sigma <= 0:
        return float("nan")
    z = (x - mean) / (sigma * math.sqrt(2.0))
    return 0.5 * math.erfc(z)


def conditional_survival_probability(
    market_pick_mean: float,
    market_pick_sigma: float,
    current_pick: int,
    target_pick: int,
) -> float:
    """P(player available at target | available at current).

    Treat the latent selection pick as a continuous normal variable. A player
    is available at the start of pick p if selection_pick >= p - 0.5.
    """
    if target_pick <= current_pick:
        return 1.0

    current_threshold = float(current_pick) - 0.5
    target_threshold = float(target_pick) - 0.5

    denom = _normal_survival(
        current_threshold, market_pick_mean, market_pick_sigma
    )
    numer = _normal_survival(
        target_threshold, market_pick_mean, market_pick_sigma
    )
    if not np.isfinite(denom) or denom <= 1e-12:
        return 0.0
    return float(np.clip(numer / denom, 0.0, 1.0))


def classify_draft_eligibility(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Add explicit current-market draftability flags and reasons."""
    out = df.copy()
    out["espn_adp"] = _num(out.get("espn_adp"))
    out["espn_rank"] = _num(out.get("espn_rank"))
    out["espn_proj_points"] = _num(out.get("espn_proj_points"))

    sentinel = float(cfg["adp_sentinel_floor"])
    history_rank_max = float(cfg["history_only_max_rank"])
    general_rank_max = float(cfg["general_max_rank"])

    eligible = []
    reasons = []

    for _, row in out.iterrows():
        pos = row.get("position")
        team = str(row.get("nfl_team") or "").upper()
        status = str(row.get("model_status") or "")
        adp = row.get("espn_adp")
        rank = row.get("espn_rank")
        proj = row.get("espn_proj_points")

        reason = "eligible"
        ok = True

        if pos not in CORE_POSITIONS:
            ok = False
            reason = "non_core_position"
        elif team in {"", "NAN", "FA"}:
            ok = False
            reason = "no_current_nfl_team"
        elif status == "history_only":
            credible_rank = pd.notna(rank) and float(rank) <= history_rank_max
            credible_adp = pd.notna(adp) and float(adp) < sentinel
            if not (credible_rank or credible_adp):
                ok = False
                reason = "stale_history_only_market"
        else:
            has_projection = pd.notna(proj) and float(proj) > 0
            credible_rank = pd.notna(rank) and float(rank) <= general_rank_max
            credible_adp = pd.notna(adp) and float(adp) < sentinel
            if not (has_projection or credible_rank or credible_adp):
                ok = False
                reason = "no_current_market_signal"

        eligible.append(bool(ok))
        reasons.append(reason)

    out["draft_eligible"] = eligible
    out["draft_eligibility_reason"] = reasons
    return out


def calibrate_market_pick_sigma(df: pd.DataFrame, cfg: dict) -> dict:
    """Estimate ADP-pick dispersion by draft region.

    ADP is the behavioral center. The local robust width of (rank - ADP)
    supplies an empirical market-disagreement scale, with a pick-number-
    dependent floor so late-round selections remain appropriately diffuse.
    """
    sentinel = float(cfg["adp_sentinel_floor"])
    bins = [float(x) for x in cfg["adp_bins"]]

    work = df[
        df["draft_eligible"]
        & df["espn_adp"].notna()
        & df["espn_rank"].notna()
        & (df["espn_adp"] < sentinel)
        & (df["espn_rank"] <= float(cfg["general_max_rank"]))
    ].copy()

    work["market_residual"] = work["espn_rank"] - work["espn_adp"]

    result = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        g = work[
            (work["espn_adp"] > lo)
            & (work["espn_adp"] <= hi)
        ]
        vals = g["market_residual"].dropna().to_numpy(float)

        if len(vals) >= 3:
            med = float(np.median(vals))
            mad = float(np.median(np.abs(vals - med)))
            robust = 1.4826 * mad
            if robust <= 0 and len(vals) > 1:
                robust = float(np.std(vals, ddof=1))
        else:
            robust = float("nan")

        midpoint = 0.5 * (lo + hi)
        floor = max(
            float(cfg["market_pick_sigma_floor"]),
            float(cfg["market_pick_sigma_fraction"]) * midpoint,
        )
        sigma = robust if np.isfinite(robust) else floor
        sigma = max(float(sigma), floor)
        sigma = min(float(sigma), float(cfg["market_pick_sigma_cap"]))

        key = f"{lo:g}-{hi:g}"
        result[key] = {
            "lo": lo,
            "hi": hi,
            "n": int(len(vals)),
            "robust_rank_minus_adp_sigma": (
                float(robust) if np.isfinite(robust) else None
            ),
            "sigma_pick": float(sigma),
        }

    return result


def _sigma_for_adp(adp: float, calibration: dict, cfg: dict) -> float:
    for info in calibration.values():
        if adp > info["lo"] and adp <= info["hi"]:
            return float(info["sigma_pick"])

    fallback = max(
        float(cfg["market_pick_sigma_floor"]),
        float(cfg["market_pick_sigma_fraction"]) * float(adp),
    )
    return min(float(fallback), float(cfg["market_pick_sigma_cap"]))


def build_market_values(
    draft_values_path: str | Path,
    league_path: str | Path,
    model_path: str | Path,
    out_path: str | Path,
    diagnostics_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(draft_values_path, low_memory=False)
    league = _load_json(league_path)
    model = _load_json(model_path)
    cfg = model["draft_market"]

    df = classify_draft_eligibility(df, cfg)
    calibration = calibrate_market_pick_sigma(df, cfg)

    sentinel = float(cfg["adp_sentinel_floor"])
    means = []
    sigmas = []
    sources = []

    for _, row in df.iterrows():
        adp = row.get("espn_adp")
        rank = row.get("espn_rank")

        if (
            row["draft_eligible"]
            and pd.notna(adp)
            and float(adp) < sentinel
        ):
            mean = float(adp)
            source = "espn_adp"
        elif (
            row["draft_eligible"]
            and pd.notna(rank)
            and float(rank) <= float(cfg["general_max_rank"])
        ):
            mean = float(rank)
            source = "espn_rank_fallback"
        else:
            mean = float("nan")
            source = "none"

        sigma = (
            _sigma_for_adp(mean, calibration, cfg)
            if np.isfinite(mean) else float("nan")
        )
        means.append(mean)
        sigmas.append(sigma)
        sources.append(source)

    df["market_pick_mean"] = means
    df["market_pick_sigma"] = sigmas
    df["market_center_source"] = sources

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    excluded = df[~df["draft_eligible"]].copy()
    diagnostics = {
        "eligible_players": int(df["draft_eligible"].sum()),
        "excluded_players": int((~df["draft_eligible"]).sum()),
        "exclusion_reasons": {
            str(k): int(v)
            for k, v in excluded["draft_eligibility_reason"]
            .value_counts()
            .to_dict()
            .items()
        },
        "market_sigma_calibration": calibration,
    }

    if diagnostics_path is not None:
        diagnostics_path = Path(diagnostics_path)
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(json.dumps(diagnostics, indent=2))

    return df, diagnostics


def add_survival_to_target(
    df: pd.DataFrame,
    current_pick: int,
    target_pick: int,
) -> pd.DataFrame:
    out = df.copy()
    probs = []
    for _, row in out.iterrows():
        if not bool(row.get("draft_eligible", False)):
            probs.append(0.0)
            continue
        mean = row.get("market_pick_mean")
        sigma = row.get("market_pick_sigma")
        if pd.isna(mean) or pd.isna(sigma):
            probs.append(float("nan"))
            continue
        probs.append(
            conditional_survival_probability(
                float(mean), float(sigma),
                int(current_pick), int(target_pick),
            )
        )
    out[f"p_available_pick_{target_pick}"] = probs
    return out


def next_user_pick(
    current_pick: int,
    num_teams: int,
    rounds: int,
    draft_slot: int,
) -> int | None:
    from .league import user_overall_picks
    picks = user_overall_picks(num_teams, rounds, draft_slot)
    future = [p for p in picks if p > current_pick]
    return min(future) if future else None


def print_market_diagnostics(diag: dict):
    print("=== CURRENT DRAFTABLE UNIVERSE ===")
    print(f'Eligible: {diag["eligible_players"]}')
    print(f'Excluded: {diag["excluded_players"]}')
    for reason, count in diag["exclusion_reasons"].items():
        print(f"  {reason}: {count}")

    print("\n=== MARKET PICK DISPERSION ===")
    for key, info in diag["market_sigma_calibration"].items():
        raw = info["robust_rank_minus_adp_sigma"]
        raw_txt = "nan" if raw is None else f"{raw:.2f}"
        print(
            f'{key:>10}: n={info["n"]:>3} '
            f'raw={raw_txt:>6} sigma_pick={info["sigma_pick"]:6.2f}'
        )
