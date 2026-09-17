from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


CORE_POSITIONS = ["QB", "RB", "WR", "TE"]


def _load_json(path: str | Path) -> dict:
    with Path(path).open() as f:
        return json.load(f)


def _num(series):
    return pd.to_numeric(series, errors="coerce")


def _position_rank(df: pd.DataFrame) -> pd.Series:
    return (
        df.groupby("position")["latent_mean_ppg"]
        .rank(method="first", ascending=False)
        .astype("Int64")
    )


def _compute_starter_assignment(
    df: pd.DataFrame,
    league: dict,
    cfg: dict,
) -> tuple[pd.Series, dict[str, float], dict[str, int]]:
    """Allocate league-wide mandatory starters, then FLEX.

    This is a league-level approximation rather than a team-by-team draft.
    It is useful for defining the current starter boundary before actual
    rosters exist.
    """
    teams = int(league["teams"])
    scfg = cfg["starter_allocation"]

    mandatory = {
        "QB": teams * int(scfg["QB_per_team"]),
        "RB": teams * int(scfg["RB_per_team"]),
        "WR": teams * int(scfg["WR_per_team"]),
        "TE": teams * int(scfg["TE_per_team"]),
    }
    flex_slots = teams * int(scfg["FLEX_per_team"])
    flex_eligible = set(scfg["flex_eligible"])

    work = df.copy()
    starter = pd.Series(False, index=work.index)
    assigned_count = {p: 0 for p in CORE_POSITIONS}

    # Mandatory starter pools.
    for pos, count in mandatory.items():
        g = work[
            work["position"].eq(pos) & work["latent_mean_ppg"].notna()
        ].sort_values("latent_mean_ppg", ascending=False)
        idx = g.head(count).index
        starter.loc[idx] = True
        assigned_count[pos] += len(idx)

    # FLEX: highest remaining RB/WR/TE by modeled PPG.
    flex_pool = work[
        work["position"].isin(flex_eligible)
        & work["latent_mean_ppg"].notna()
        & ~starter
    ].sort_values("latent_mean_ppg", ascending=False)
    flex_idx = flex_pool.head(flex_slots).index
    starter.loc[flex_idx] = True
    for pos, n in work.loc[flex_idx, "position"].value_counts().items():
        assigned_count[pos] += int(n)

    cutoff = {}
    for pos in CORE_POSITIONS:
        vals = work.loc[
            starter & work["position"].eq(pos),
            "latent_mean_ppg"
        ].dropna()
        cutoff[pos] = float(vals.min()) if len(vals) else float("nan")

    return starter, cutoff, assigned_count


def _replacement_levels(
    df: pd.DataFrame,
    counts: dict[str, int],
) -> dict[str, dict]:
    result = {}
    for pos in CORE_POSITIONS:
        g = df[
            df["position"].eq(pos) & df["latent_mean_ppg"].notna()
        ].sort_values("latent_mean_ppg", ascending=False)

        n = int(counts[pos])
        if len(g) == 0:
            result[pos] = {
                "rostered_count": n,
                "replacement_rank": None,
                "replacement_ppg": float("nan"),
                "replacement_player": None,
            }
            continue

        # Replacement player is first player outside the expected rostered pool.
        idx = min(n, len(g) - 1)
        row = g.iloc[idx]
        result[pos] = {
            "rostered_count": n,
            "replacement_rank": int(idx + 1),
            "replacement_ppg": float(row["latent_mean_ppg"]),
            "replacement_player": row.get("name"),
        }
    return result


def _assign_tiers(g: pd.DataFrame, cfg: dict) -> pd.Series:
    """Assign uncertainty-aware tiers within one position.

    A new tier starts only when the adjacent PPG gap exceeds both:
      * an absolute minimum gap, and
      * a fraction of the combined epistemic uncertainty.

    This prevents tiny rank differences from becoming artificial tiers.
    """
    g = g.sort_values("latent_mean_ppg", ascending=False)
    tier = 1
    out = {}

    sigma_factor = float(cfg["tier_gap_sigma"])
    min_gap = float(cfg["tier_min_absolute_gap_ppg"])

    rows = list(g.iterrows())
    for i, (idx, row) in enumerate(rows):
        out[idx] = tier
        if i == len(rows) - 1:
            continue

        _, nxt = rows[i + 1]
        gap = float(row["latent_mean_ppg"] - nxt["latent_mean_ppg"])

        s1 = row.get("latent_mean_sd_ppg")
        s2 = nxt.get("latent_mean_sd_ppg")
        try:
            combined = float(np.sqrt(float(s1) ** 2 + float(s2) ** 2))
        except (TypeError, ValueError):
            combined = 0.0

        threshold = max(min_gap, sigma_factor * combined)
        if gap > threshold:
            tier += 1

    return pd.Series(out, dtype="Int64")


def _scarcity_gap(g: pd.DataFrame, lookahead: int) -> pd.Series:
    """PPG drop to the player `lookahead` places later at same position."""
    g = g.sort_values("latent_mean_ppg", ascending=False)
    vals = g["latent_mean_ppg"].to_numpy(float)
    gaps = {}
    for i, idx in enumerate(g.index):
        j = min(i + lookahead, len(g) - 1)
        gaps[idx] = float(vals[i] - vals[j])
    return pd.Series(gaps)


def build_draft_values(
    values_path: str | Path,
    league_path: str | Path,
    model_path: str | Path,
    out_path: str | Path,
    diagnostics_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    values = pd.read_csv(values_path, low_memory=False)
    league = _load_json(league_path)
    model = _load_json(model_path)
    cfg = model["draft_value"]

    df = values[values["position"].isin(CORE_POSITIONS)].copy()

    # If the current-market eligibility layer has already been attached,
    # stale/non-draftable names must not define starter/replacement boundaries.
    if "draft_eligible" in df.columns:
        eligible_mask = df["draft_eligible"].astype(str).str.lower().isin(
            ["true", "1", "yes"]
        )
        boundary_df = df[eligible_mask].copy()
    else:
        boundary_df = df.copy()

    for col in [
        "latent_mean_ppg", "latent_mean_sd_ppg",
        "predictive_weekly_sd_ppg", "espn_adp", "espn_rank",
    ]:
        if col in df.columns:
            df[col] = _num(df[col])
        if col in boundary_df.columns:
            boundary_df[col] = _num(boundary_df[col])

    df["position_rank_model"] = _position_rank(df)

    starter_flag_boundary, starter_cutoff, starter_counts = _compute_starter_assignment(
        boundary_df, league, cfg
    )
    starter_flag = pd.Series(False, index=df.index)
    starter_flag.loc[starter_flag_boundary.index] = starter_flag_boundary
    df["projected_league_starter"] = starter_flag

    replacements = _replacement_levels(
        boundary_df, cfg["expected_rostered_counts"]
    )

    df["starter_cutoff_ppg"] = df["position"].map(starter_cutoff)
    df["replacement_ppg"] = df["position"].map(
        {p: replacements[p]["replacement_ppg"] for p in CORE_POSITIONS}
    )

    df["starter_advantage_ppg"] = (
        df["latent_mean_ppg"] - df["starter_cutoff_ppg"]
    )
    df["vorp_ppg"] = (
        df["latent_mean_ppg"] - df["replacement_ppg"]
    )

    # Conservative VORP: one epistemic sigma below the latent mean.
    df["vorp_conservative_ppg"] = (
        df["latent_mean_ppg"]
        - df["latent_mean_sd_ppg"]
        - df["replacement_ppg"]
    )

    lookahead = int(cfg["scarcity_lookahead_players"])
    df["scarcity_gap_next_n_ppg"] = np.nan
    df["tier"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    for pos in CORE_POSITIONS:
        g = df[
            df["position"].eq(pos) & df["latent_mean_ppg"].notna()
        ].copy()
        if len(g) == 0:
            continue
        df.loc[g.index, "tier"] = _assign_tiers(g, cfg)
        df.loc[g.index, "scarcity_gap_next_n_ppg"] = _scarcity_gap(g, lookahead)

    # This is not the final Monte Carlo objective. It is a transparent,
    # position-relative ordering for the next stage.
    df["draft_value_score"] = (
        df["vorp_ppg"]
        + 0.25 * df["scarcity_gap_next_n_ppg"].fillna(0.0)
    )

    df = df.sort_values(
        ["draft_value_score", "espn_adp"],
        ascending=[False, True],
        na_position="last",
    )

    diagnostics = {
        "teams": int(league["teams"]),
        "starter_counts": {k: int(v) for k, v in starter_counts.items()},
        "starter_cutoff_ppg": starter_cutoff,
        "replacement": replacements,
        "expected_rostered_counts": {
            k: int(v) for k, v in cfg["expected_rostered_counts"].items()
        },
        "scarcity_lookahead_players": lookahead,
    }

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    if diagnostics_path is not None:
        diagnostics_path = Path(diagnostics_path)
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(json.dumps(diagnostics, indent=2))

    return df, diagnostics


def print_draft_value_summary(diagnostics: dict):
    print("=== LEAGUE-WIDE STARTER ALLOCATION ===")
    for pos in CORE_POSITIONS:
        count = diagnostics["starter_counts"][pos]
        cutoff = diagnostics["starter_cutoff_ppg"][pos]
        print(f"{pos:>2}: starters={count:>3} cutoff={cutoff:6.3f} PPG")

    print("\n=== REPLACEMENT LEVELS ===")
    for pos in CORE_POSITIONS:
        r = diagnostics["replacement"][pos]
        print(
            f'{pos:>2}: expected rostered={r["rostered_count"]:>3} '
            f'replacement rank={r["replacement_rank"]:>3} '
            f'PPG={r["replacement_ppg"]:6.3f} '
            f'({r["replacement_player"]})'
        )
