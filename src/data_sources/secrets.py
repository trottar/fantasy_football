from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class EspnSecrets:
    season: int
    league_id: int
    espn_s2: str
    swid: str


def find_secrets_path(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("FANTASY_SECRETS")
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.extend([Path("../config/secrets.json"), Path("config/secrets.json")])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Prefer the project-root layout described by the setup chat in the error message.
    return Path("../config/secrets.json")


def load_espn_secrets(path: str | Path | None = None) -> EspnSecrets:
    path = find_secrets_path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing ESPN secrets file: {path}. Copy config/secrets.example.json "
            "to config/secrets.json and fill it locally."
        )

    payload = json.loads(path.read_text(encoding="utf-8"))
    cfg = payload.get("espn") or {}
    missing = [k for k in ("season", "league_id", "espn_s2") if not cfg.get(k)]
    swid = cfg.get("swid") or cfg.get("SWID")
    if not swid:
        missing.append("swid")
    if missing:
        raise ValueError(f"Missing ESPN secrets fields in {path}: {', '.join(missing)}")

    return EspnSecrets(
        season=int(cfg["season"]),
        league_id=int(cfg["league_id"]),
        espn_s2=str(cfg["espn_s2"]),
        swid=str(swid),
    )
