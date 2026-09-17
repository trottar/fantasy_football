from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping


_INVARIANT_RE = re.compile(
    r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$"
)
_SUBSYSTEM_RE = re.compile(
    r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$"
)


class InvariantStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class InvariantSeverity(str, Enum):
    DIAGNOSTIC = "DIAGNOSTIC"
    AUDIT = "AUDIT"


def _freeze_json(value: Any, path: str = "details") -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{path} datetime must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return _freeze_json(value.value, path)
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} mapping keys must be strings")
            frozen[key] = _freeze_json(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    if isinstance(value, (set, frozenset)):
        frozen = [_freeze_json(item, f"{path}[]") for item in value]
        return tuple(sorted(frozen, key=repr))
    raise TypeError(
        f"{path} contains unsupported value type {type(value).__name__}"
    )


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class InvariantDefinition:
    name: str
    description: str
    severity: InvariantSeverity = InvariantSeverity.AUDIT
    allowed_subsystems: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _INVARIANT_RE.fullmatch(self.name):
            raise ValueError("invariant name must be dotted lowercase identifiers")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be non-empty")
        object.__setattr__(self, "description", self.description.strip())
        if not isinstance(self.severity, InvariantSeverity):
            raise TypeError("severity must be an InvariantSeverity")

        subsystems: list[str] = []
        for subsystem in self.allowed_subsystems:
            if not isinstance(subsystem, str) or not _SUBSYSTEM_RE.fullmatch(subsystem):
                raise ValueError(f"invalid allowed subsystem: {subsystem!r}")
            if subsystem not in subsystems:
                subsystems.append(subsystem)
        object.__setattr__(self, "allowed_subsystems", tuple(subsystems))

        tags: list[str] = []
        for tag in self.tags:
            if not isinstance(tag, str) or not tag.strip() or any(ch.isspace() for ch in tag):
                raise ValueError("tags must be non-empty strings without whitespace")
            normalized = tag.strip().lower()
            if normalized not in tags:
                tags.append(normalized)
        object.__setattr__(self, "tags", tuple(tags))


@dataclass(frozen=True)
class InvariantResult:
    name: str
    status: InvariantStatus
    severity: InvariantSeverity
    subsystem: str | None = None
    run_id: str | None = None
    correlation_id: str | None = None
    message: str = ""
    details: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _INVARIANT_RE.fullmatch(self.name):
            raise ValueError("invalid invariant result name")
        if not isinstance(self.status, InvariantStatus):
            raise TypeError("status must be an InvariantStatus")
        if not isinstance(self.severity, InvariantSeverity):
            raise TypeError("severity must be an InvariantSeverity")
        if self.subsystem is not None:
            if not isinstance(self.subsystem, str) or not _SUBSYSTEM_RE.fullmatch(self.subsystem):
                raise ValueError("invalid subsystem")
        for field_name in ("run_id", "correlation_id"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(f"{field_name} must be a non-empty string or None")
        if not isinstance(self.message, str):
            raise TypeError("message must be a string")
        raw_details = {} if self.details is None else dict(self.details)
        object.__setattr__(self, "details", _freeze_json(raw_details))

    @property
    def passed(self) -> bool:
        return self.status is InvariantStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status in {InvariantStatus.FAIL, InvariantStatus.ERROR}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "severity": self.severity.value,
            "subsystem": self.subsystem,
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "message": self.message,
            "details": _thaw_json(self.details),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


class InvariantRegistry:
    """Immutable registry of named invariant contracts."""

    def __init__(self, definitions: Iterable[InvariantDefinition]) -> None:
        rows: dict[str, InvariantDefinition] = {}
        for definition in definitions:
            if not isinstance(definition, InvariantDefinition):
                raise TypeError("registry entries must be InvariantDefinition values")
            if definition.name in rows:
                raise ValueError(f"duplicate invariant definition: {definition.name}")
            rows[definition.name] = definition
        self._definitions: Mapping[str, InvariantDefinition] = MappingProxyType(rows)

    def __len__(self) -> int:
        return len(self._definitions)

    def __iter__(self) -> Iterator[str]:
        return iter(self._definitions)

    def __contains__(self, name: object) -> bool:
        return name in self._definitions

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._definitions)

    def get(self, name: str) -> InvariantDefinition | None:
        return self._definitions.get(name)

    def require(self, name: str) -> InvariantDefinition:
        definition = self.get(name)
        if definition is None:
            raise KeyError(f"invariant is not registered: {name}")
        return definition

    def extended(self, definitions: Iterable[InvariantDefinition]) -> "InvariantRegistry":
        return InvariantRegistry((*self._definitions.values(), *tuple(definitions)))

    def result(
        self,
        name: str,
        *,
        passed: bool | None = None,
        status: InvariantStatus | None = None,
        context: object | None = None,
        subsystem: str | None = None,
        message: str = "",
        details: Mapping[str, Any] | None = None,
    ) -> InvariantResult:
        definition = self.require(name)
        if status is not None and passed is not None:
            raise ValueError("provide either passed or status, not both")
        if status is None:
            if passed is None:
                status = InvariantStatus.SKIP
            elif not isinstance(passed, bool):
                raise TypeError("passed must be bool or None")
            else:
                status = InvariantStatus.PASS if passed else InvariantStatus.FAIL
        elif not isinstance(status, InvariantStatus):
            raise TypeError("status must be an InvariantStatus")

        context_subsystem = getattr(context, "subsystem", None) if context is not None else None
        if subsystem is None:
            subsystem = context_subsystem
        elif context_subsystem is not None and subsystem != context_subsystem:
            raise ValueError("explicit subsystem disagrees with context.subsystem")

        if subsystem is not None and (
            not isinstance(subsystem, str) or not _SUBSYSTEM_RE.fullmatch(subsystem)
        ):
            raise ValueError("invalid subsystem")
        if definition.allowed_subsystems and subsystem not in definition.allowed_subsystems:
            raise ValueError(
                f"invariant {name!r} does not allow subsystem {subsystem!r}"
            )

        run_id = getattr(context, "run_id", None) if context is not None else None
        correlation_id = (
            getattr(context, "correlation_id", None)
            if context is not None
            else None
        )
        return InvariantResult(
            name=definition.name,
            status=status,
            severity=definition.severity,
            subsystem=subsystem,
            run_id=run_id,
            correlation_id=correlation_id,
            message=message,
            details=details,
        )

    def error_result(
        self,
        name: str,
        error: BaseException,
        *,
        context: object | None = None,
        subsystem: str | None = None,
        safe_message: str = "",
        details: Mapping[str, Any] | None = None,
    ) -> InvariantResult:
        if not isinstance(error, BaseException):
            raise TypeError("error must be an exception")
        safe_details = dict(details or {})
        safe_details["error_type"] = type(error).__name__
        return self.result(
            name,
            status=InvariantStatus.ERROR,
            context=context,
            subsystem=subsystem,
            message=safe_message,
            details=safe_details,
        )


def _definition(
    name: str,
    description: str,
    *,
    severity: InvariantSeverity = InvariantSeverity.AUDIT,
    subsystems: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> InvariantDefinition:
    return InvariantDefinition(
        name=name,
        description=description,
        severity=severity,
        allowed_subsystems=subsystems,
        tags=tags,
    )


CORE_INVARIANT_REGISTRY = InvariantRegistry(
    (
        _definition(
            "physics.channel_separation",
            "Preserve player, DST, and kicker channel separation.",
            tags=("physics", "channels"),
        ),
        _definition(
            "authority.screen_not_authority",
            "Cheap screens may not authorize predictive decisions.",
            tags=("authority",),
        ),
        _definition(
            "causality.prediction_frozen_before_outcome",
            "Predictions are frozen before observed outcomes.",
            tags=("causality",),
        ),
        _definition(
            "causality.information_not_after_decision",
            "Decision information time does not exceed decision time.",
            tags=("causality",),
        ),
        _definition(
            "randomness.crn_required_pairing",
            "Paired comparisons use common random numbers where required.",
            tags=("randomness", "crn"),
        ),
        _definition(
            "league.dropped_players_retained",
            "Dropped players remain represented in league state.",
            tags=("league_state",),
        ),
        _definition(
            "separation.football_vs_behavior",
            "Football utility remains separate from manager behavior.",
            tags=("separation",),
        ),
        _definition(
            "data.raw_vs_derived_separation",
            "Raw observations remain separate from derived/calibrated state.",
            tags=("data", "closure"),
        ),
        _definition(
            "gui.no_mutation_after_unmount",
            "UI mutation does not occur after client/page deletion or unmount.",
            subsystems=("gui",),
            tags=("gui", "lifecycle"),
        ),
        _definition(
            "gui.task_owned_and_cancelled",
            "Background GUI tasks have ownership and cancellation semantics.",
            subsystems=("gui",),
            tags=("gui", "lifecycle"),
        ),
        _definition(
            "gui.no_stale_service_write",
            "Service completion does not write into stale GUI context.",
            subsystems=("gui",),
            tags=("gui", "lifecycle"),
        ),
        _definition(
            "gui.refresh_render_correlated",
            "Refresh/render lifecycle exposes correlated start/end/error state.",
            subsystems=("gui",),
            tags=("gui", "lifecycle"),
        ),
        _definition(
            "gui.exception_correlation_preserved",
            "Exceptions crossing GUI service/controller boundaries retain correlation.",
            subsystems=("gui",),
            tags=("gui", "correlation"),
        ),
    )
)
