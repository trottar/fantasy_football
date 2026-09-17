from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import tempfile
import traceback
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .provenance import sha256_bytes
from .redaction import RedactionPolicy, redact_event, redact_value


FAILURE_BUNDLE_SCHEMA_VERSION = 1
FAILURE_BUNDLE_MANIFEST_FILE = "failure_bundle_manifest.json"
FAILURE_MEMBER_FILES = (
    "failure.json",
    "context.json",
    "invariants.json",
    "events.jsonl",
    "state_summary.json",
    "reproduction.json",
    "effects.json",
)
OMITTED_EXCEPTION_MESSAGE = "[OMITTED:EXCEPTION_MESSAGE]"


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


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _mapping_row(value: object, field: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        row = value.to_dict()
        if isinstance(row, Mapping):
            return dict(row)
    if hasattr(value, "as_dict"):
        row = value.as_dict()
        if isinstance(row, Mapping):
            return dict(row)
    raise TypeError(f"{field} must be a mapping or provide to_dict()/as_dict()")


def _positive_bound(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an integer")
    if value < 1:
        raise ValueError(f"{field} must be >= 1")
    return value


def _tail(values: Iterable[object], limit: int) -> tuple[object, ...]:
    return tuple(deque(values, maxlen=limit))


def _context_run_id(row: Mapping[str, Any]) -> str:
    value = row.get("run_id")
    if not isinstance(value, str) or not value:
        raise ValueError("context run_id must be a non-empty string")
    return value


def summarize_exception(
    error: BaseException,
    *,
    policy: RedactionPolicy | None = None,
    include_message: bool = False,
    max_frames: int = 32,
) -> dict[str, Any]:
    """Create a privacy-conservative structured exception summary.

    Raw exception text is omitted by default. Stack frames retain only file
    basenames, function names, and line numbers; local absolute paths and source
    code lines are deliberately excluded.
    """
    if not isinstance(error, BaseException):
        raise TypeError("error must be an exception")
    max_frames = _positive_bound(max_frames, "max_frames")
    active = RedactionPolicy() if policy is None else policy
    if not isinstance(active, RedactionPolicy):
        raise TypeError("policy must be a RedactionPolicy or None")

    if include_message:
        message = redact_value({"value": str(error)}, policy=active)["value"]
    else:
        message = OMITTED_EXCEPTION_MESSAGE

    extracted = traceback.extract_tb(error.__traceback__) if error.__traceback__ else []
    frames = [
        {
            "file": Path(frame.filename).name,
            "function": frame.name,
            "line": frame.lineno,
        }
        for frame in extracted[-max_frames:]
    ]
    return {
        "error_type": type(error).__name__,
        "message": message,
        "frames": frames,
        "frame_count": len(extracted),
        "frames_truncated": len(extracted) > max_frames,
    }


@dataclass(frozen=True)
class FailureBundleMember:
    path: str
    bytes: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "bytes": self.bytes, "sha256": self.sha256}


@dataclass(frozen=True)
class FailureBundleManifest:
    schema_version: int
    run_id: str
    members: tuple[FailureBundleMember, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "members": [member.to_dict() for member in self.members],
        }


@dataclass(frozen=True)
class FailureBundleVerification:
    ok: bool
    problems: tuple[str, ...]
    member_count: int

    def require_ok(self) -> None:
        if not self.ok:
            raise ValueError(
                "failure bundle integrity failure: " + "; ".join(self.problems)
            )


@dataclass(frozen=True)
class FailureBundle:
    root: Path
    failure: Mapping[str, Any]
    context: Mapping[str, Any]
    invariants: tuple[Mapping[str, Any], ...]
    events: tuple[Mapping[str, Any], ...]
    state_summary: Mapping[str, Any]
    reproduction: Mapping[str, Any]
    effects: Mapping[str, Any]

    @property
    def run_id(self) -> str | None:
        value = self.context.get("run_id")
        return value if isinstance(value, str) else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure": _thaw(self.failure),
            "context": _thaw(self.context),
            "invariants": [_thaw(row) for row in self.invariants],
            "events": [_thaw(row) for row in self.events],
            "state_summary": _thaw(self.state_summary),
            "reproduction": _thaw(self.reproduction),
            "effects": _thaw(self.effects),
        }


def write_failure_bundle(
    destination: str | Path,
    *,
    context: object,
    error: BaseException,
    events: Iterable[object] = (),
    invariants: Iterable[object] = (),
    state_summary: Mapping[str, Any] | None = None,
    reproduction: Mapping[str, Any] | None = None,
    project_modification_state: Mapping[str, Any] | None = None,
    runtime_side_effects: Mapping[str, Any] | None = None,
    policy: RedactionPolicy | None = None,
    include_exception_message: bool = False,
    max_events: int = 100,
    max_invariants: int = 100,
    max_frames: int = 32,
) -> FailureBundleManifest:
    """Atomically write one bounded, redacted local diagnostic failure bundle.

    The caller supplies structured summaries only. This function does not ingest
    raw authenticated files and does not capture anything automatically.
    """
    if not isinstance(error, BaseException):
        raise TypeError("error must be an exception")
    max_events = _positive_bound(max_events, "max_events")
    max_invariants = _positive_bound(max_invariants, "max_invariants")
    max_frames = _positive_bound(max_frames, "max_frames")
    active = RedactionPolicy() if policy is None else policy
    if not isinstance(active, RedactionPolicy):
        raise TypeError("policy must be a RedactionPolicy or None")

    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(
            f"failure bundle destination already exists: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)

    context_row = _mapping_row(context, "context")
    run_id = _context_run_id(context_row)
    failure_row = summarize_exception(
        error,
        policy=active,
        include_message=include_exception_message,
        max_frames=max_frames,
    )

    event_rows: list[dict[str, Any]] = []
    for event in _tail(events, max_events):
        redacted = redact_event(event, policy=active).to_value()
        if not isinstance(redacted, dict):
            raise TypeError("redacted event must be a mapping")
        event_rows.append(redacted)

    invariant_rows: list[dict[str, Any]] = []
    for invariant in _tail(invariants, max_invariants):
        row = _mapping_row(invariant, "invariant")
        redacted = redact_value(row, policy=active)
        if not isinstance(redacted, dict):
            raise TypeError("redacted invariant must be a mapping")
        invariant_rows.append(redacted)

    state = redact_value(dict(state_summary or {}), policy=active)
    repro = redact_value(dict(reproduction or {}), policy=active)
    effects = redact_value(
        {
            "project_modification_state": dict(project_modification_state or {}),
            "runtime_side_effects": dict(runtime_side_effects or {}),
        },
        policy=active,
    )

    members_data: dict[str, bytes] = {
        "failure.json": _json_bytes(redact_value(failure_row, policy=active)),
        "context.json": _json_bytes(redact_value(context_row, policy=active)),
        "invariants.json": _json_bytes(invariant_rows),
        "state_summary.json": _json_bytes(state),
        "reproduction.json": _json_bytes(repro),
        "effects.json": _json_bytes(effects),
    }

    event_lines = [
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        for row in event_rows
    ]
    members_data["events.jsonl"] = (
        ("\n".join(event_lines) + ("\n" if event_lines else "")).encode("utf-8")
    )

    if set(members_data) != set(FAILURE_MEMBER_FILES):
        raise RuntimeError("internal failure bundle member set mismatch")

    temp_root = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.",
            dir=str(destination.parent),
        )
    )
    try:
        members: list[FailureBundleMember] = []
        for name in FAILURE_MEMBER_FILES:
            data = members_data[name]
            path = temp_root / name
            path.write_bytes(data)
            members.append(
                FailureBundleMember(
                    path=name,
                    bytes=len(data),
                    sha256=sha256_bytes(data),
                )
            )

        manifest = FailureBundleManifest(
            schema_version=FAILURE_BUNDLE_SCHEMA_VERSION,
            run_id=run_id,
            members=tuple(members),
        )
        (temp_root / FAILURE_BUNDLE_MANIFEST_FILE).write_bytes(
            _json_bytes(manifest.to_dict())
        )
        os.replace(str(temp_root), str(destination))
        return manifest
    except Exception:
        if temp_root.exists():
            shutil.rmtree(temp_root, ignore_errors=True)
        raise


def _load_manifest(root: Path) -> dict[str, Any]:
    with (root / FAILURE_BUNDLE_MANIFEST_FILE).open(
        "r",
        encoding="utf-8",
    ) as handle:
        row = json.load(handle)
    if not isinstance(row, dict):
        raise ValueError("failure bundle manifest must be a JSON object")
    return row


def verify_failure_bundle(root: str | Path) -> FailureBundleVerification:
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return FailureBundleVerification(
            False,
            ("bundle root is not a directory",),
            0,
        )

    try:
        manifest = _load_manifest(root)
    except Exception as exc:
        return FailureBundleVerification(
            False,
            (f"cannot load failure bundle manifest: {type(exc).__name__}",),
            0,
        )

    if manifest.get("schema_version") != FAILURE_BUNDLE_SCHEMA_VERSION:
        problems.append("unsupported failure bundle schema version")

    rows = manifest.get("members")
    if not isinstance(rows, list):
        return FailureBundleVerification(
            False,
            tuple(problems + ["manifest members must be a list"]),
            0,
        )

    paths: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            problems.append("manifest member must be an object")
            continue
        name = row.get("path")
        expected_bytes = row.get("bytes")
        expected_sha = row.get("sha256")
        if not isinstance(name, str) or name not in FAILURE_MEMBER_FILES:
            problems.append(f"unexpected member path: {name!r}")
            continue
        if name in paths:
            problems.append(f"duplicate member path: {name}")
            continue
        paths.append(name)

        path = root / name
        if not path.is_file():
            problems.append(f"missing member: {name}")
            continue
        data = path.read_bytes()
        if expected_bytes != len(data):
            problems.append(f"byte length mismatch: {name}")
        if expected_sha != sha256_bytes(data):
            problems.append(f"sha256 mismatch: {name}")

    expected = set(FAILURE_MEMBER_FILES)
    if set(paths) != expected:
        for missing in sorted(expected - set(paths)):
            problems.append(f"manifest omits member: {missing}")

    return FailureBundleVerification(
        ok=not problems,
        problems=tuple(problems),
        member_count=len(paths),
    )


def _read_object(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        row = json.load(handle)
    if not isinstance(row, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return _freeze(row)


def load_failure_bundle(
    root: str | Path,
    *,
    verify: bool = True,
) -> FailureBundle:
    root = Path(root)
    if verify:
        verify_failure_bundle(root).require_ok()

    with (root / "invariants.json").open("r", encoding="utf-8") as handle:
        invariant_rows = json.load(handle)
    if not isinstance(invariant_rows, list) or not all(
        isinstance(row, dict) for row in invariant_rows
    ):
        raise ValueError("invariants.json must contain a list of objects")

    events: list[Mapping[str, Any]] = []
    with (root / "events.jsonl").open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(
                    f"events.jsonl line {line_number} must be a JSON object"
                )
            events.append(_freeze(row))

    return FailureBundle(
        root=root,
        failure=_read_object(root / "failure.json"),
        context=_read_object(root / "context.json"),
        invariants=tuple(_freeze(row) for row in invariant_rows),
        events=tuple(events),
        state_summary=_read_object(root / "state_summary.json"),
        reproduction=_read_object(root / "reproduction.json"),
        effects=_read_object(root / "effects.json"),
    )
