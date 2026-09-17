from __future__ import annotations

import json

from src.data_sources.secrets import load_espn_secrets


def test_load_espn_secrets(tmp_path):
    path = tmp_path / "secrets.json"
    path.write_text(json.dumps({"espn": {
        "season": 2026,
        "league_id": 123,
        "espn_s2": "secret",
        "swid": "{ABC}",
    }}))
    cfg = load_espn_secrets(path)
    assert cfg.season == 2026
    assert cfg.league_id == 123
    assert cfg.swid == "{ABC}"
