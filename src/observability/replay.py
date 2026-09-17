from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .provenance import sha256_bytes
from .snapshots import (
    BUNDLE_MANIFEST_FILE,
    BUNDLE_SCHEMA_VERSION,
    CORE_MEMBER_FILES,
)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value


@dataclass(frozen=True)
class ReplayVerification:
    ok: bool
    problems: tuple[str, ...]
    member_count: int

    def require_ok(self) -> None:
        if not self.ok:
            raise ValueError(
                "replay bundle integrity failure: " + "; ".join(self.problems)
            )


@dataclass(frozen=True)
class ReplayBundle:
    root: Path
    run_manifest: Mapping[str, Any]
    inputs_manifest: Mapping[str, Any]
    config_snapshot: Mapping[str, Any]
    decision_snapshot: Mapping[str, Any]
    events: tuple[Mapping[str, Any], ...]
    summary: Mapping[str, Any]

    @property
    def run_id(self) -> str | None:
        context = self.run_manifest.get("context", {})
        if isinstance(context, Mapping):
            value = context.get("run_id")
            return value if isinstance(value, str) else None
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_manifest": _thaw(self.run_manifest),
            "inputs_manifest": _thaw(self.inputs_manifest),
            "config_snapshot": _thaw(self.config_snapshot),
            "decision_snapshot": _thaw(self.decision_snapshot),
            "events": [_thaw(event) for event in self.events],
            "summary": _thaw(self.summary),
        }


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / BUNDLE_MANIFEST_FILE
    with path.open("r", encoding="utf-8") as handle:
        row = json.load(handle)
    if not isinstance(row, dict):
        raise ValueError("bundle manifest must be a JSON object")
    return row


def verify_replay_bundle(root: str | Path) -> ReplayVerification:
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return ReplayVerification(False, ("bundle root is not a directory",), 0)

    try:
        manifest = _load_manifest(root)
    except Exception as exc:
        return ReplayVerification(
            False,
            (f"cannot load bundle manifest: {type(exc).__name__}",),
            0,
        )

    if manifest.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        problems.append("unsupported bundle schema version")

    rows = manifest.get("members")
    if not isinstance(rows, list):
        return ReplayVerification(
            False,
            tuple(problems + ["manifest members must be a list"]),
            0,
        )

    member_paths: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            problems.append("manifest member must be an object")
            continue
        name = row.get("path")
        expected_bytes = row.get("bytes")
        expected_sha = row.get("sha256")
        if not isinstance(name, str) or name not in CORE_MEMBER_FILES:
            problems.append(f"unexpected member path: {name!r}")
            continue
        if name in member_paths:
            problems.append(f"duplicate member path: {name}")
            continue
        member_paths.append(name)

        path = root / name
        if not path.is_file():
            problems.append(f"missing member: {name}")
            continue
        data = path.read_bytes()
        if expected_bytes != len(data):
            problems.append(f"byte length mismatch: {name}")
        if expected_sha != sha256_bytes(data):
            problems.append(f"sha256 mismatch: {name}")

    expected = set(CORE_MEMBER_FILES)
    if set(member_paths) != expected:
        for missing in sorted(expected - set(member_paths)):
            problems.append(f"manifest omits member: {missing}")

    return ReplayVerification(
        ok=not problems,
        problems=tuple(problems),
        member_count=len(member_paths),
    )


def _read_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        row = json.load(handle)
    if not isinstance(row, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return _freeze(row)


def load_replay_bundle(
    root: str | Path,
    *,
    verify: bool = True,
) -> ReplayBundle:
    root = Path(root)
    if verify:
        verify_replay_bundle(root).require_ok()

    events: list[Mapping[str, Any]] = []
    events_path = root / "events.jsonl"
    with events_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(
                    f"events.jsonl line {line_number} must be a JSON object"
                )
            events.append(_freeze(row))

    return ReplayBundle(
        root=root,
        run_manifest=_read_json(root / "run_manifest.json"),
        inputs_manifest=_read_json(root / "inputs_manifest.json"),
        config_snapshot=_read_json(root / "config_snapshot.json"),
        decision_snapshot=_read_json(root / "decision_snapshot.json"),
        events=tuple(events),
        summary=_read_json(root / "summary.json"),
    )
