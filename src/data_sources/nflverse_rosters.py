from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROSTER_URL_TEMPLATE = (
    "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{season}.csv"
)

# Higher means more likely to be the player's current live roster row when duplicate
# ESPN IDs occur after a transaction. Week is considered first, then status priority.
_STATUS_PRIORITY = {
    "ACT": 100,
    "INA": 90,
    "PUP": 85,
    "RES": 85,
    "RSN": 85,
    "SUS": 85,
    "EXE": 85,
    "E14": 80,
    "DEV": 70,
    "NWT": 20,
    "RFA": 20,
    "RSR": 20,
    "UFA": 10,
    "CUT": 5,
    "RET": 0,
    "TRC": 0,
    "TRD": 0,
    "TRT": 0,
}


def _headers() -> dict[str, str]:
    return {
        "Accept": "text/csv,*/*",
        "User-Agent": "Mozilla/5.0 fantasy-season-manager/0.22 (personal analytics project)",
    }


def fetch_roster_csv(season: int, timeout: int = 45) -> tuple[str, str]:
    url = ROSTER_URL_TEMPLATE.format(season=int(season))
    response = requests.get(url, headers=_headers(), timeout=timeout)
    response.raise_for_status()
    return response.text, url


def parse_roster_csv(text: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(text), low_memory=False)
    # Keep source field names intact; normalize only key fields needed for joins.
    if "espn_id" in df.columns:
        df["_espn_id_num"] = pd.to_numeric(df["espn_id"], errors="coerce")
    else:
        df["_espn_id_num"] = pd.NA
    if "week" in df.columns:
        df["_week_num"] = pd.to_numeric(df["week"], errors="coerce").fillna(-1)
    else:
        df["_week_num"] = -1
    status = df.get("status", pd.Series(index=df.index, dtype="object")).astype("string").str.upper()
    df["_status_priority"] = status.map(_STATUS_PRIORITY).fillna(-1).astype(int)
    return df


def build_roster_index(df: pd.DataFrame) -> dict[int, dict[str, Any]]:
    if df.empty or "_espn_id_num" not in df.columns:
        return {}
    usable = df[df["_espn_id_num"].notna()].copy()
    if usable.empty:
        return {}
    # Latest week wins; within the same week, prefer an active/contracted row over a
    # stale released row. This handles players changing teams during the season.
    usable = usable.sort_values(
        ["_espn_id_num", "_week_num", "_status_priority"],
        ascending=[True, True, True],
        kind="stable",
    )
    usable = usable.drop_duplicates("_espn_id_num", keep="last")

    out: dict[int, dict[str, Any]] = {}
    fields = (
        "season",
        "team",
        "position",
        "depth_chart_position",
        "status",
        "status_description_abbr",
        "full_name",
        "gsis_id",
        "espn_id",
        "sleeper_id",
        "week",
    )
    for rec in usable.to_dict("records"):
        try:
            pid = int(float(rec.get("_espn_id_num")))
        except (TypeError, ValueError):
            continue
        row: dict[str, Any] = {}
        for field in fields:
            value = rec.get(field)
            try:
                if pd.isna(value):
                    value = None
            except (TypeError, ValueError):
                pass
            row[field] = value
        out[pid] = row
    return out


def sync_nflverse_rosters(out_dir: str | Path, season: int) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    text, url = fetch_roster_csv(int(season))
    raw_path = out_dir / f"roster_{int(season)}.csv"
    raw_path.write_text(text, encoding="utf-8")
    df = parse_roster_csv(text)
    index = build_roster_index(df)
    return index, {
        "ok": True,
        "url": url,
        "rows": int(len(df)),
        "matched_espn_ids": int(len(index)),
        "path": str(raw_path),
    }
