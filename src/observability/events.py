from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .context import RunContext
from .registry import CORE_EVENT_REGISTRY, EventLevel, EventRegistry


EVENT_SCHEMA_VERSION = 1


def _utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _freeze_json(value: Any, path: str = "payload") -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value

    if isinstance(value, datetime):
        return _iso(_utc(value, path))

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
class StructuredEvent:
    timestamp: datetime
    level: EventLevel
    event_name: str
    context: RunContext
    correlation_id: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "timestamp",
            _utc(self.timestamp, "timestamp"),
        )
        if not isinstance(self.level, EventLevel):
            raise TypeError("level must be an EventLevel")
        if not isinstance(self.context, RunContext):
            raise TypeError("context must be a RunContext")
        if not isinstance(self.correlation_id, str) or not self.correlation_id:
            raise ValueError("correlation_id must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")

        frozen = _freeze_json(dict(self.payload))
        object.__setattr__(self, "payload", frozen)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EVENT_SCHEMA_VERSION,
            "timestamp": _iso(self.timestamp),
            "level": self.level.value,
            "event_name": self.event_name,
            "subsystem": self.context.subsystem,
            "run_id": self.context.run_id,
            "correlation_id": self.correlation_id,
            "action_id": self.context.action_id,
            "parent_action_id": self.context.parent_action_id,
            "payload": _thaw_json(self.payload),
            "provenance": self.context.provenance(),
            "context": self.context.as_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def make_event(
    context: RunContext,
    event_name: str,
    *,
    payload: Mapping[str, Any] | None = None,
    level: EventLevel | None = None,
    timestamp: datetime | None = None,
    correlation_id: str | None = None,
    registry: EventRegistry = CORE_EVENT_REGISTRY,
) -> StructuredEvent:
    definition = registry.require(event_name)

    if (
        definition.allowed_subsystems
        and context.subsystem not in definition.allowed_subsystems
    ):
        raise ValueError(
            f"event {event_name!r} does not allow subsystem "
            f"{context.subsystem!r}"
        )

    raw_payload = {} if payload is None else dict(payload)
    missing = [
        key
        for key in definition.required_payload_keys
        if key not in raw_payload
    ]
    if missing:
        raise ValueError(
            f"event {event_name!r} missing required payload keys: {missing}"
        )

    return StructuredEvent(
        timestamp=timestamp or datetime.now(timezone.utc),
        level=definition.default_level if level is None else level,
        event_name=event_name,
        context=context,
        correlation_id=correlation_id or context.correlation_id,
        payload=raw_payload,
    )
