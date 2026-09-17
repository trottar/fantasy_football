from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


CORE_DRAFT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DST"]


def _nonnull_count(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns:
        return 0
    return int(df[col].notna().sum())


def _position_table(df: pd.DataFrame) -> pd.DataFrame:
    if "position" not in df.columns:
        return pd.DataFrame()

    rows = []
    for pos, g in df.groupby("position", dropna=False):
        rows.append({
            "position": pos,
            "players": len(g),
            "espn_adp": _nonnull_count(g, "espn_adp"),
            "espn_rank": _nonnull_count(g, "espn_rank"),
            "espn_proj_points": _nonnull_count(g, "espn_proj_points"),
            "nflverse_id": int(g.get("has_nflverse_id", pd.Series(False, index=g.index)).fillna(False).astype(bool).sum()),
            "historical_prior": int(g.get("has_historical_prior", pd.Series(False, index=g.index)).fillna(False).astype(bool).sum()),
        })
    return pd.DataFrame(rows).sort_values("position")


def build_data_diagnostics(
    master_path: str | Path,
    priors_path: str | Path | None = None,
    out_dir: str | Path = "data/processed/diagnostics",
    top_n: int = 50,
) -> dict:
    master_path = Path(master_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(master_path, low_memory=False)
    pos = _position_table(df)

    unmatched = df.copy()
    if "has_nflverse_id" in unmatched.columns:
        unmatched = unmatched[~unmatched["has_nflverse_id"].fillna(False).astype(bool)]
    else:
        unmatched = unmatched.iloc[0:0]

    cols = [
        c for c in [
            "espn_id", "name", "position", "nfl_team",
            "espn_adp", "espn_rank", "espn_proj_points",
            "injury_status", "active"
        ] if c in unmatched.columns
    ]
    unmatched = unmatched[cols].copy()

    no_prior = df.copy()
    if "has_historical_prior" in no_prior.columns:
        no_prior = no_prior[~no_prior["has_historical_prior"].fillna(False).astype(bool)]
    else:
        no_prior = no_prior.iloc[0:0]

    # Draft-relevant board sorted primarily by ADP, then ESPN rank.
    draftable = df[df.get("position", pd.Series(index=df.index, dtype=object)).isin(CORE_DRAFT_POSITIONS)].copy()
    if "espn_adp" in draftable.columns:
        draftable["_sort_adp"] = pd.to_numeric(draftable["espn_adp"], errors="coerce").fillna(1e9)
    else:
        draftable["_sort_adp"] = 1e9
    if "espn_rank" in draftable.columns:
        draftable["_sort_rank"] = pd.to_numeric(draftable["espn_rank"], errors="coerce").fillna(1e9)
    else:
        draftable["_sort_rank"] = 1e9

    board_cols = [
        c for c in [
            "espn_id", "gsis_id", "name", "position", "nfl_team",
            "espn_adp", "espn_rank", "espn_proj_points",
            "historical_prior_mean_ppg", "historical_prior_sd_weekly",
            "historical_games", "has_historical_prior",
            "injury_status"
        ] if c in draftable.columns
    ]
    board = (
        draftable
        .sort_values(["_sort_adp", "_sort_rank"])
        [board_cols]
        .head(int(top_n))
        .copy()
    )

    pos.to_csv(out_dir / "coverage_by_position.csv", index=False)
    unmatched.to_csv(out_dir / "unmatched_espn_players.csv", index=False)

    nop_cols = [
        c for c in [
            "espn_id", "gsis_id", "name", "position", "nfl_team",
            "espn_adp", "espn_rank", "espn_proj_points",
            "years_of_experience", "draft_year", "injury_status"
        ] if c in no_prior.columns
    ]
    no_prior[nop_cols].to_csv(out_dir / "players_without_historical_prior.csv", index=False)
    board.to_csv(out_dir / "top_market_board.csv", index=False)

    summary = {
        "master_rows": int(len(df)),
        "columns": list(df.columns),
        "coverage": {
            "espn_adp": _nonnull_count(df, "espn_adp"),
            "espn_rank": _nonnull_count(df, "espn_rank"),
            "espn_proj_points": _nonnull_count(df, "espn_proj_points"),
            "nflverse_id": int(df.get("has_nflverse_id", pd.Series(False, index=df.index)).fillna(False).astype(bool).sum()),
            "historical_prior": int(df.get("has_historical_prior", pd.Series(False, index=df.index)).fillna(False).astype(bool).sum()),
        },
        "unmatched_espn_players": int(len(unmatched)),
        "players_without_historical_prior": int(len(no_prior)),
        "top_board_rows": int(len(board)),
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return {
        "summary": summary,
        "position_coverage": pos,
        "unmatched": unmatched,
        "no_prior": no_prior[nop_cols],
        "board": board,
        "out_dir": out_dir,
    }


def print_data_diagnostics(result: dict, unmatched_limit: int = 20, board_limit: int = 30):
    summary = result["summary"]

    print("=== MASTER DATA COVERAGE ===")
    print(f'Rows:                 {summary["master_rows"]}')
    print(f'ESPN ADP:             {summary["coverage"]["espn_adp"]}')
    print(f'ESPN rank:            {summary["coverage"]["espn_rank"]}')
    print(f'ESPN projections:     {summary["coverage"]["espn_proj_points"]}')
    print(f'nflverse ID matched:  {summary["coverage"]["nflverse_id"]}')
    print(f'Historical priors:    {summary["coverage"]["historical_prior"]}')

    print("\n=== COVERAGE BY POSITION ===")
    pos = result["position_coverage"]
    if len(pos):
        print(pos.to_string(index=False))
    else:
        print("No position column found.")

    print("\n=== UNMATCHED ESPN PLAYERS ===")
    unmatched = result["unmatched"]
    if len(unmatched):
        print(unmatched.head(unmatched_limit).to_string(index=False))
        if len(unmatched) > unmatched_limit:
            print(f"... {len(unmatched) - unmatched_limit} more written to CSV")
    else:
        print("None.")

    print("\n=== TOP ESPN MARKET BOARD ===")
    board = result["board"]
    if len(board):
        print(board.head(board_limit).to_string(index=False))
    else:
        print("No draftable rows found.")

    print(f'\nDiagnostic files: {result["out_dir"]}')


def projection_coverage(master_path: str | Path):
    df = pd.read_csv(master_path, low_memory=False)
    if "espn_proj_points" not in df.columns:
        raise ValueError("player master has no espn_proj_points column")

    relevant = df[df["position"].isin(["QB", "RB", "WR", "TE"])].copy()
    relevant["espn_proj_points"] = pd.to_numeric(
        relevant["espn_proj_points"], errors="coerce"
    )

    rows = []
    for pos, g in relevant.groupby("position"):
        n = len(g)
        good = int(g["espn_proj_points"].notna().sum())
        positive = int((g["espn_proj_points"].fillna(0) > 0).sum())
        rows.append({
            "position": pos,
            "players": n,
            "projection_nonnull": good,
            "projection_positive": positive,
            "coverage_fraction": good / n if n else 0.0,
        })
    return pd.DataFrame(rows).sort_values("position")
