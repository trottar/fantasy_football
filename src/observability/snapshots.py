from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Iterable, Mapping

from .provenance import sha256_bytes
from .redaction import RedactionPolicy, redact_event, redact_value


BUNDLE_SCHEMA_VERSION = 1
BUNDLE_MANIFEST_FILE = "bundle_manifest.json"
CORE_MEMBER_FILES = (
    "run_manifest.json",
    "inputs_manifest.json",
    "config_snapshot.json",
    "decision_snapshot.json",
    "events.jsonl",
    "summary.json",
)


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


@dataclass(frozen=True)
class BundleMember:
    path: str
    bytes: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "bytes": self.bytes, "sha256": self.sha256}


@dataclass(frozen=True)
class BundleManifest:
    schema_version: int
    run_id: str
    members: tuple[BundleMember, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "members": [member.to_dict() for member in self.members],
        }


def _context_row(context: object) -> dict[str, Any]:
    if not hasattr(context, "as_dict"):
        raise TypeError("context must provide as_dict()")
    row = context.as_dict()
    if not isinstance(row, Mapping):
        raise TypeError("context.as_dict() must return a mapping")
    return dict(row)


def _run_id(context_row: Mapping[str, Any]) -> str:
    value = context_row.get("run_id")
    if not isinstance(value, str) or not value:
        raise ValueError("context run_id must be a non-empty string")
    return value


def _event_rows(
    events: Iterable[object],
    *,
    policy: RedactionPolicy,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in events:
        redacted = redact_event(event, policy=policy).to_value()
        if not isinstance(redacted, dict):
            raise TypeError("redacted event must be a mapping")
        rows.append(redacted)
    return rows


def write_snapshot_bundle(
    destination: str | Path,
    *,
    context: object,
    inputs_manifest: Mapping[str, Any],
    config_snapshot: Mapping[str, Any],
    decision_snapshot: Mapping[str, Any],
    events: Iterable[object],
    summary: Mapping[str, Any],
    policy: RedactionPolicy | None = None,
) -> BundleManifest:
    """Write one local replay-evidence bundle atomically.

    All persisted JSON/event values pass through the explicit redaction policy.
    This function accepts structured values only; it does not ingest raw
    authenticated response files.
    """
    active = RedactionPolicy() if policy is None else policy
    if not isinstance(active, RedactionPolicy):
        raise TypeError("policy must be a RedactionPolicy or None")

    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"snapshot destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    context_row = _context_row(context)
    run_id = _run_id(context_row)

    redacted_context = redact_value(context_row, policy=active)
    members_data: dict[str, bytes] = {
        "run_manifest.json": _json_bytes(
            {
                "schema_version": BUNDLE_SCHEMA_VERSION,
                "context": redacted_context,
            }
        ),
        "inputs_manifest.json": _json_bytes(
            redact_value(dict(inputs_manifest), policy=active)
        ),
        "config_snapshot.json": _json_bytes(
            redact_value(dict(config_snapshot), policy=active)
        ),
        "decision_snapshot.json": _json_bytes(
            redact_value(dict(decision_snapshot), policy=active)
        ),
        "summary.json": _json_bytes(
            redact_value(dict(summary), policy=active)
        ),
    }

    event_lines = [
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        for row in _event_rows(events, policy=active)
    ]
    members_data["events.jsonl"] = (
        ("\n".join(event_lines) + ("\n" if event_lines else "")).encode("utf-8")
    )

    if set(members_data) != set(CORE_MEMBER_FILES):
        raise RuntimeError("internal snapshot member set mismatch")

    temp_root = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.",
            dir=str(destination.parent),
        )
    )
    try:
        members: list[BundleMember] = []
        for name in CORE_MEMBER_FILES:
            data = members_data[name]
            path = temp_root / name
            path.write_bytes(data)
            members.append(
                BundleMember(
                    path=name,
                    bytes=len(data),
                    sha256=sha256_bytes(data),
                )
            )

        manifest = BundleManifest(
            schema_version=BUNDLE_SCHEMA_VERSION,
            run_id=run_id,
            members=tuple(members),
        )
        (temp_root / BUNDLE_MANIFEST_FILE).write_bytes(
            _json_bytes(manifest.to_dict())
        )

        os.replace(str(temp_root), str(destination))
        return manifest
    except Exception:
        if temp_root.exists():
            shutil.rmtree(temp_root, ignore_errors=True)
        raise
