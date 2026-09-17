from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .redaction import RedactionPolicy, redact_value
from .replay import ReplayBundle, load_replay_bundle


class DiffKind(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    CHANGED = "CHANGED"
    TYPE_CHANGED = "TYPE_CHANGED"


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
class DiffEntry:
    path: str
    kind: DiffKind
    before: Any
    after: Any

    def __post_init__(self) -> None:
        object.__setattr__(self, "before", _freeze(self.before))
        object.__setattr__(self, "after", _freeze(self.after))

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind.value,
            "before": _thaw(self.before),
            "after": _thaw(self.after),
        }


@dataclass(frozen=True)
class ReplayDiff:
    entries: tuple[DiffEntry, ...]
    truncated: bool

    @property
    def changed(self) -> bool:
        return bool(self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed": self.changed,
            "truncated": self.truncated,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def _type_family(value: Any) -> type:
    if isinstance(value, Mapping):
        return dict
    if isinstance(value, (list, tuple)):
        return list
    return type(value)


def diff_values(
    before: Any,
    after: Any,
    *,
    policy: RedactionPolicy | None = None,
    redact_inputs: bool = True,
    max_differences: int = 1000,
) -> ReplayDiff:
    if isinstance(max_differences, bool) or not isinstance(max_differences, int):
        raise TypeError("max_differences must be an integer")
    if max_differences < 1:
        raise ValueError("max_differences must be >= 1")

    if redact_inputs:
        before = redact_value(before, policy=policy)
        after = redact_value(after, policy=policy)

    entries: list[DiffEntry] = []
    truncated = False

    def add(path: str, kind: DiffKind, left: Any, right: Any) -> None:
        nonlocal truncated
        if len(entries) >= max_differences:
            truncated = True
            return
        entries.append(DiffEntry(path, kind, left, right))

    def walk(left: Any, right: Any, path: str) -> None:
        nonlocal truncated
        if truncated:
            return
        if _type_family(left) is not _type_family(right):
            add(path, DiffKind.TYPE_CHANGED, left, right)
            return

        if isinstance(left, Mapping) and isinstance(right, Mapping):
            left_keys = set(left)
            right_keys = set(right)
            for key in sorted(left_keys - right_keys):
                add(f"{path}.{key}", DiffKind.REMOVED, left[key], None)
                if truncated:
                    return
            for key in sorted(right_keys - left_keys):
                add(f"{path}.{key}", DiffKind.ADDED, None, right[key])
                if truncated:
                    return
            for key in sorted(left_keys & right_keys):
                walk(left[key], right[key], f"{path}.{key}")
                if truncated:
                    return
            return

        if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
            common = min(len(left), len(right))
            for index in range(common):
                walk(left[index], right[index], f"{path}[{index}]")
                if truncated:
                    return
            for index in range(common, len(left)):
                add(f"{path}[{index}]", DiffKind.REMOVED, left[index], None)
                if truncated:
                    return
            for index in range(common, len(right)):
                add(f"{path}[{index}]", DiffKind.ADDED, None, right[index])
                if truncated:
                    return
            return

        if left != right:
            add(path, DiffKind.CHANGED, left, right)

    walk(before, after, "$")
    return ReplayDiff(entries=tuple(entries), truncated=truncated)


def diff_replay_bundles(
    before: ReplayBundle | str,
    after: ReplayBundle | str,
    *,
    policy: RedactionPolicy | None = None,
    max_differences: int = 1000,
) -> ReplayDiff:
    if not isinstance(before, ReplayBundle):
        before = load_replay_bundle(before)
    if not isinstance(after, ReplayBundle):
        after = load_replay_bundle(after)

    return diff_values(
        before.to_dict(),
        after.to_dict(),
        policy=policy,
        redact_inputs=True,
        max_differences=max_differences,
    )
