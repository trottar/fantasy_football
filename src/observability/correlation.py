from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .context import RunContext
from .events import StructuredEvent, make_event
from .registry import EventRegistry, CORE_EVENT_REGISTRY


class BoundaryKind(str, Enum):
    CLI = "cli"
    SERVICE = "service"
    BACKGROUND_TASK = "background_task"
    SUBSYSTEM = "subsystem"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted((_freeze(v) for v in value), key=repr))
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value


def _name(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("boundary name must be a string")
    value = value.strip()
    if not value:
        raise ValueError("boundary name cannot be empty")
    if len(value) > 128:
        raise ValueError("boundary name exceeds 128 characters")
    return value


@dataclass(frozen=True)
class CorrelationBoundary:
    context: RunContext
    kind: BoundaryKind
    name: str
    attributes: Mapping[str, Any]
    start_event: StructuredEvent
    registry: EventRegistry = CORE_EVENT_REGISTRY

    def __post_init__(self) -> None:
        if not isinstance(self.context, RunContext):
            raise TypeError("context must be a RunContext")
        if not isinstance(self.kind, BoundaryKind):
            raise TypeError("kind must be a BoundaryKind")
        object.__setattr__(self, "name", _name(self.name))
        if not isinstance(self.attributes, Mapping):
            raise TypeError("attributes must be a mapping")
        object.__setattr__(self, "attributes", _freeze(dict(self.attributes)))
        if not isinstance(self.start_event, StructuredEvent):
            raise TypeError("start_event must be a StructuredEvent")
        if self.start_event.context != self.context:
            raise ValueError("start_event context must match boundary context")
        if self.start_event.event_name != "action.start":
            raise ValueError("start_event must be action.start")

    @property
    def run_id(self) -> str:
        return self.context.run_id

    @property
    def action_id(self) -> str:
        assert self.context.action_id is not None
        return self.context.action_id

    @property
    def parent_action_id(self) -> str | None:
        return self.context.parent_action_id

    def base_payload(self) -> dict[str, Any]:
        return {
            "boundary_kind": self.kind.value,
            "boundary_name": self.name,
            "attributes": _thaw(self.attributes),
        }

    def complete(self, payload: Mapping[str, Any] | None = None) -> StructuredEvent:
        row = self.base_payload()
        if payload:
            row["result"] = dict(payload)
        return make_event(
            self.context,
            "action.complete",
            payload=row,
            registry=self.registry,
        )

    def fail(
        self,
        error: BaseException,
        payload: Mapping[str, Any] | None = None,
    ) -> StructuredEvent:
        if not isinstance(error, BaseException):
            raise TypeError("error must be an exception")
        row = self.base_payload()
        row["error_type"] = type(error).__name__
        if payload:
            row["diagnostic"] = dict(payload)
        return make_event(
            self.context,
            "action.error",
            payload=row,
            registry=self.registry,
        )


def begin_boundary(
    parent: RunContext,
    *,
    kind: BoundaryKind,
    name: str,
    subsystem: str | None = None,
    action_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
    registry: EventRegistry = CORE_EVENT_REGISTRY,
) -> CorrelationBoundary:
    if not isinstance(parent, RunContext):
        raise TypeError("parent must be a RunContext")
    if not isinstance(kind, BoundaryKind):
        raise TypeError("kind must be a BoundaryKind")
    clean_name = _name(name)
    child = parent.for_action(
        subsystem=parent.subsystem if subsystem is None else subsystem,
        action_id=action_id,
    )
    frozen_attributes = _freeze(dict(attributes or {}))
    payload = {
        "boundary_kind": kind.value,
        "boundary_name": clean_name,
        "attributes": _thaw(frozen_attributes),
    }
    start = make_event(
        child,
        "action.start",
        payload=payload,
        registry=registry,
    )
    return CorrelationBoundary(
        context=child,
        kind=kind,
        name=clean_name,
        attributes=frozen_attributes,
        start_event=start,
        registry=registry,
    )


def begin_cli_action(
    parent: RunContext,
    name: str,
    *,
    action_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> CorrelationBoundary:
    return begin_boundary(
        parent,
        kind=BoundaryKind.CLI,
        name=name,
        action_id=action_id,
        attributes=attributes,
    )


def begin_service_action(
    parent: RunContext,
    name: str,
    *,
    subsystem: str | None = None,
    action_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> CorrelationBoundary:
    return begin_boundary(
        parent,
        kind=BoundaryKind.SERVICE,
        name=name,
        subsystem=subsystem,
        action_id=action_id,
        attributes=attributes,
    )


def begin_background_task(
    parent: RunContext,
    name: str,
    *,
    subsystem: str | None = None,
    action_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> CorrelationBoundary:
    return begin_boundary(
        parent,
        kind=BoundaryKind.BACKGROUND_TASK,
        name=name,
        subsystem=subsystem,
        action_id=action_id,
        attributes=attributes,
    )
