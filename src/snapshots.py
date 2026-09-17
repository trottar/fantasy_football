from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_snapshot(path: str | Path, *, state, available=None, recommendations=None, metadata=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "state": state.to_dict(),
        "available": available or [],
        "recommendations": recommendations or [],
        "metadata": metadata or {},
    }
    path.write_text(json.dumps(payload, indent=2))
    return path
