from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .historical import _season_table
from .player_value import robust_sigma, CORE_POSITIONS


def calibrate_year_to_year_transition(
    stats_path: str | Path,
    seasons: list[int],
    minimum_games_per_season: int = 6,
    minimum_pairs_per_position: int = 20,
    sigma_floors: dict | None = None,
) -> dict[str, dict]:
    """Estimate position-dependent season-to-season PPG drift.

    Uses consecutive regular seasons for the same player/position. This is not
    weekly variance; it is an empirical scale for how much a player's latent
    season-level production changes from one NFL season to the next.
    """
    sigma_floors = sigma_floors or {}
    stats = pd.read_csv(stats_path, low_memory=False)
    season_df = _season_table(stats, [int(s) for s in seasons])

    season_df = season_df[
        season_df["position"].isin(CORE_POSITIONS)
    ].copy()
    season_df = season_df[
        pd.to_numeric(season_df["games"], errors="coerce").fillna(0)
        >= int(minimum_games_per_season)
    ]

    pairs = []
    by_player = season_df.sort_values(["player_id", "season"]).groupby("player_id")
    for player_id, g in by_player:
        g = g.sort_values("season")
        rows = list(g.to_dict("records"))
        for a, b in zip(rows[:-1], rows[1:]):
            if int(b["season"]) != int(a["season"]) + 1:
                continue
            if a.get("position") != b.get("position"):
                continue
            ppg_a = pd.to_numeric(pd.Series([a.get("ppg")]), errors="coerce").iloc[0]
            ppg_b = pd.to_numeric(pd.Series([b.get("ppg")]), errors="coerce").iloc[0]
            if pd.isna(ppg_a) or pd.isna(ppg_b):
                continue
            pairs.append({
                "player_id": player_id,
                "position": a["position"],
                "season_from": int(a["season"]),
                "season_to": int(b["season"]),
                "ppg_from": float(ppg_a),
                "ppg_to": float(ppg_b),
                "delta_ppg": float(ppg_b - ppg_a),
            })

    pairs_df = pd.DataFrame(pairs)
    pooled = robust_sigma(pairs_df["delta_ppg"]) if len(pairs_df) else float("nan")
    if not np.isfinite(pooled):
        pooled = 3.0

    result = {}
    for pos in CORE_POSITIONS:
        g = pairs_df[pairs_df["position"].eq(pos)] if len(pairs_df) else pd.DataFrame()
        vals = g["delta_ppg"] if len(g) else []
        raw = robust_sigma(vals)
        if len(g) < int(minimum_pairs_per_position) or not np.isfinite(raw):
            raw = pooled
        floor = float(sigma_floors.get(pos, 2.0))
        result[pos] = {
            "pairs": int(len(g)),
            "raw_robust_sigma_ppg": float(raw),
            "transition_sigma_ppg": max(float(raw), floor),
        }

    return result, pairs_df
