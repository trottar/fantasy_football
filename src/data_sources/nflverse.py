from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


PLAYERS_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/"
    "players/players.csv"
)
PLAYER_STATS_WEEK_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/"
    "stats_player/stats_player_week_{season}.csv"
)
DEFAULT_PLAYER_STATS_SEASONS = (2022, 2023, 2024, 2025)


def _download(url: str, path: str | Path, force: bool = False) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not force:
        return path

    tmp = path.with_suffix(path.suffix + ".part")
    headers = {
        "User-Agent": "fantasy-draft-optimizer/0.2 "
                      "(personal analytics project)"
    }
    with requests.get(url, headers=headers, stream=True, timeout=90) as response:
        response.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    tmp.replace(path)
    return path


def _normalize_seasons(seasons: Iterable[int] | None) -> list[int]:
    values = sorted({int(s) for s in (seasons or DEFAULT_PLAYER_STATS_SEASONS)})
    if not values:
        raise ValueError("sync-nflverse requires at least one player-stat season")
    return values


def _combine_weekly_player_stats(paths: list[Path], out_path: Path) -> Path:
    frames: list[pd.DataFrame] = []
    for path in paths:
        frame = pd.read_csv(path, low_memory=False)
        if "season" not in frame.columns:
            # The season is encoded in the canonical nflverse asset name; fail
            # explicitly rather than guessing if an unexpected asset is supplied.
            raise ValueError(f"nflverse weekly player-stat asset has no season column: {path}")
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True, sort=False)
    subset = [column for column in ("season", "week", "season_type", "player_id") if column in combined.columns]
    if subset:
        combined = combined.drop_duplicates(subset=subset, keep="last")
    sort_cols = [column for column in ("season", "week", "player_id") if column in combined.columns]
    if sort_cols:
        combined = combined.sort_values(sort_cols).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False, compression="gzip")
    return out_path



def sync_weekly_player_stats(
    out_dir: str | Path,
    *,
    season: int,
    force: bool = False,
) -> Path:
    """Download one nflverse stats_player weekly season asset without rewriting the historical aggregate."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return _download(
        PLAYER_STATS_WEEK_URL.format(season=int(season)),
        out_dir / f"stats_player_week_{int(season)}.csv",
        force=force,
    )

def sync_nflverse(
    out_dir: str | Path,
    force: bool = False,
    *,
    seasons: Iterable[int] | None = None,
) -> dict[str, Path]:
    """Sync canonical players plus explicit season-level weekly player stats.

    nflverse's current player-stat release is ``stats_player`` with assets named
    ``stats_player_week_<season>.csv``.  The older aggregate ``player_stats``
    release is not guaranteed to contain the latest completed season, so the
    local historical file is rebuilt from the requested season assets.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    players = _download(PLAYERS_URL, out_dir / "players.csv", force=force)
    selected = _normalize_seasons(seasons)
    season_dir = out_dir / "player_stats_seasons"
    season_paths = [
        _download(
            PLAYER_STATS_WEEK_URL.format(season=season),
            season_dir / f"stats_player_week_{season}.csv",
            force=force,
        )
        for season in selected
    ]
    stats = _combine_weekly_player_stats(season_paths, out_dir / "player_stats.csv.gz")
    return {"players": players, "player_stats": stats}
