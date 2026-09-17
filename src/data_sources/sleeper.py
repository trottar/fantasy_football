from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests


BASE_URL = "https://api.sleeper.app/v1"


def fetch_players(timeout: int = 45) -> dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}/players/nfl",
        headers={"User-Agent": "fantasy-season-manager/0.22 (personal analytics project)"},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Sleeper /players/nfl returned an unexpected payload")
    return payload


def fetch_trending(kind: str = "add", lookback_hours: int = 24, limit: int = 100,
                   timeout: int = 45) -> list[dict[str, Any]]:
    if kind not in {"add", "drop"}:
        raise ValueError("kind must be 'add' or 'drop'")
    response = requests.get(
        f"{BASE_URL}/players/nfl/trending/{kind}",
        params={"lookback_hours": int(lookback_hours), "limit": int(limit)},
        headers={"User-Agent": "fantasy-season-manager/0.22 (personal analytics project)"},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Sleeper trending endpoint returned an unexpected payload")
    return payload


def normalize_players(payload: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for sleeper_id, player in payload.items():
        if not isinstance(player, dict):
            continue
        fantasy_positions = player.get("fantasy_positions") or []
        rows.append({
            "sleeper_id": str(sleeper_id),
            "espn_id": player.get("espn_id"),
            "gsis_id": player.get("gsis_id"),
            "sportradar_id": player.get("sportradar_id"),
            "fantasy_data_id": player.get("fantasy_data_id"),
            "full_name": player.get("full_name") or " ".join(
                x for x in (player.get("first_name"), player.get("last_name")) if x
            ).strip(),
            "team": player.get("team"),
            "position": player.get("position"),
            "fantasy_positions": ",".join(map(str, fantasy_positions)),
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "injury_start_date": player.get("injury_start_date"),
            "practice_participation": player.get("practice_participation"),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "age": player.get("age"),
            "years_exp": player.get("years_exp"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["espn_id"] = pd.to_numeric(df["espn_id"], errors="coerce").astype("Int64")
    return df


def sync_sleeper(out_dir: str | Path, include_trends: bool = True) -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    players = fetch_players()
    players_json = out_dir / "players_nfl.json"
    players_json.write_text(json.dumps(players, indent=2), encoding="utf-8")
    players_csv = out_dir / "players_nfl.csv"
    normalize_players(players).to_csv(players_csv, index=False)

    result = {"players_json": players_json, "players_csv": players_csv}
    if include_trends:
        for kind in ("add", "drop"):
            payload = fetch_trending(kind=kind)
            path = out_dir / f"trending_{kind}_24h.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            result[f"trending_{kind}"] = path
    return result
