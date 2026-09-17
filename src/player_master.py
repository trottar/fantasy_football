from __future__ import annotations

from pathlib import Path
import pandas as pd


def build_player_master(
    espn_path: str | Path,
    nflverse_players_path: str | Path,
    priors_path: str | Path | None,
    out_path: str | Path,
) -> pd.DataFrame:
    espn = pd.read_csv(espn_path)
    players = pd.read_csv(nflverse_players_path, low_memory=False)

    if "espn_id" not in players.columns:
        raise ValueError("nflverse players file is missing espn_id")
    if "gsis_id" not in players.columns:
        raise ValueError("nflverse players file is missing gsis_id")

    espn["espn_id"] = pd.to_numeric(espn["espn_id"], errors="coerce").astype("Int64")
    players["espn_id"] = pd.to_numeric(players["espn_id"], errors="coerce").astype("Int64")

    keep_candidates = [
        "gsis_id", "espn_id", "display_name", "position",
        "birth_date", "years_of_experience", "draft_year",
        "draft_round", "draft_pick", "status"
    ]
    keep = [c for c in keep_candidates if c in players.columns]
    p = players[keep].dropna(subset=["espn_id"]).drop_duplicates("espn_id")

    master = espn.merge(p, on="espn_id", how="left", suffixes=("_espn", "_nflverse"))

    if priors_path is not None and Path(priors_path).exists():
        priors = pd.read_csv(priors_path)
        master = master.merge(priors, on="gsis_id", how="left", suffixes=("", "_prior"))

    master["has_nflverse_id"] = master["gsis_id"].notna()
    if "historical_prior_mean_ppg" in master.columns:
        master["has_historical_prior"] = master["historical_prior_mean_ppg"].notna()
    else:
        master["has_historical_prior"] = False

    # Preserve ESPN as the current source of name/team/position when available.
    if "position_espn" in master.columns:
        master["position"] = master["position_espn"].fillna(master.get("position_nflverse"))
    elif "position" not in master.columns and "position_nflverse" in master.columns:
        master["position"] = master["position_nflverse"]

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(out_path, index=False)
    return master
