from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
import re
from typing import Iterable, Iterator, Mapping


_EVENT_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_SUBSYSTEM_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")


class EventLevel(str, Enum):
    NORMAL = "NORMAL"
    DIAGNOSTIC = "DIAGNOSTIC"
    TRACE = "TRACE"
    AUDIT = "AUDIT"


CORE_SUBSYSTEMS = frozenset(
    {
        "player",
        "dst",
        "k",
        "lineup",
        "waiver",
        "trade",
        "behavior",
        "data_source",
        "closure",
        "gui",
        "observability",
    }
)


@dataclass(frozen=True)
class EventDefinition:
    name: str
    default_level: EventLevel
    description: str
    allowed_subsystems: tuple[str, ...] = ()
    required_payload_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _EVENT_RE.fullmatch(self.name):
            raise ValueError(
                f"event name must match {_EVENT_RE.pattern!r}; received {self.name!r}"
            )
        if not isinstance(self.default_level, EventLevel):
            raise TypeError("default_level must be an EventLevel")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be non-empty")

        normalized_subsystems: list[str] = []
        for subsystem in self.allowed_subsystems:
            if not isinstance(subsystem, str) or not _SUBSYSTEM_RE.fullmatch(
                subsystem
            ):
                raise ValueError(f"invalid allowed subsystem: {subsystem!r}")
            if subsystem not in normalized_subsystems:
                normalized_subsystems.append(subsystem)
        object.__setattr__(
            self,
            "allowed_subsystems",
            tuple(normalized_subsystems),
        )

        normalized_keys: list[str] = []
        for key in self.required_payload_keys:
            if not isinstance(key, str) or not key:
                raise ValueError("required payload keys must be non-empty strings")
            if key not in normalized_keys:
                normalized_keys.append(key)
        object.__setattr__(
            self,
            "required_payload_keys",
            tuple(normalized_keys),
        )


class EventRegistry:
    """Immutable event-definition registry."""

    def __init__(self, definitions: Iterable[EventDefinition]):
        rows: dict[str, EventDefinition] = {}
        for definition in definitions:
            if not isinstance(definition, EventDefinition):
                raise TypeError("registry entries must be EventDefinition values")
            if definition.name in rows:
                raise ValueError(f"duplicate event definition: {definition.name}")
            rows[definition.name] = definition
        self._definitions: Mapping[str, EventDefinition] = MappingProxyType(rows)

    def __len__(self) -> int:
        return len(self._definitions)

    def __iter__(self) -> Iterator[str]:
        return iter(self._definitions)

    def __contains__(self, name: object) -> bool:
        return name in self._definitions

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._definitions)

    def get(self, name: str) -> EventDefinition | None:
        return self._definitions.get(name)

    def require(self, name: str) -> EventDefinition:
        definition = self.get(name)
        if definition is None:
            raise KeyError(f"event is not registered: {name}")
        return definition

    def extended(self, definitions: Iterable[EventDefinition]) -> "EventRegistry":
        return EventRegistry((*self._definitions.values(), *tuple(definitions)))


def _def(
    name: str,
    level: EventLevel,
    description: str,
    *,
    subsystems: tuple[str, ...] = (),
    required: tuple[str, ...] = (),
) -> EventDefinition:
    return EventDefinition(
        name=name,
        default_level=level,
        description=description,
        allowed_subsystems=subsystems,
        required_payload_keys=required,
    )


_CORE_DEFINITIONS = (
    _def("run.start", EventLevel.NORMAL, "Run execution started."),
    _def("run.complete", EventLevel.NORMAL, "Run execution completed."),
    _def("run.error", EventLevel.AUDIT, "Run execution failed.", required=("error_type",)),
    _def("action.start", EventLevel.NORMAL, "Correlated action started."),
    _def("action.complete", EventLevel.NORMAL, "Correlated action completed."),
    _def(
        "action.error",
        EventLevel.AUDIT,
        "Correlated action failed.",
        required=("error_type",),
    ),
    _def("gui.app.start", EventLevel.NORMAL, "GUI application started.", subsystems=("gui",)),
    _def("gui.app.stop", EventLevel.NORMAL, "GUI application stopped.", subsystems=("gui",)),
    _def("gui.client.connect", EventLevel.NORMAL, "GUI client connected.", subsystems=("gui",)),
    _def("gui.client.disconnect", EventLevel.NORMAL, "GUI client disconnected.", subsystems=("gui",)),
    _def("gui.page.mount", EventLevel.TRACE, "GUI page mounted.", subsystems=("gui",)),
    _def("gui.page.unmount", EventLevel.TRACE, "GUI page unmounted.", subsystems=("gui",)),
    _def("gui.action.start", EventLevel.NORMAL, "GUI action started.", subsystems=("gui",)),
    _def("gui.action.complete", EventLevel.NORMAL, "GUI action completed.", subsystems=("gui",)),
    _def(
        "gui.action.error",
        EventLevel.AUDIT,
        "GUI action failed.",
        subsystems=("gui",),
        required=("error_type",),
    ),
    _def("gui.task.spawn", EventLevel.TRACE, "GUI background task spawned.", subsystems=("gui",)),
    _def("gui.task.cancel", EventLevel.TRACE, "GUI background task cancelled.", subsystems=("gui",)),
    _def("gui.service.start", EventLevel.DIAGNOSTIC, "GUI service call started.", subsystems=("gui",)),
    _def("gui.service.complete", EventLevel.DIAGNOSTIC, "GUI service call completed.", subsystems=("gui",)),
    _def(
        "gui.service.error",
        EventLevel.AUDIT,
        "GUI service call failed.",
        subsystems=("gui",),
        required=("error_type",),
    ),
    _def("gui.state.read", EventLevel.TRACE, "GUI state was read.", subsystems=("gui",)),
    _def("gui.state.write", EventLevel.TRACE, "GUI state was written.", subsystems=("gui",)),
    _def("gui.render.start", EventLevel.TRACE, "GUI render started.", subsystems=("gui",)),
    _def("gui.render.complete", EventLevel.TRACE, "GUI render completed.", subsystems=("gui",)),
    _def("gui.refresh.request", EventLevel.NORMAL, "GUI refresh requested.", subsystems=("gui",)),
    _def("gui.refresh.complete", EventLevel.NORMAL, "GUI refresh completed.", subsystems=("gui",)),
    _def("gui.notification", EventLevel.DIAGNOSTIC, "GUI notification emitted.", subsystems=("gui",)),
    _def(
        "gui.lifecycle.violation",
        EventLevel.AUDIT,
        "GUI lifecycle invariant was violated.",
        subsystems=("gui",),
        required=("invariant",),
    ),
)

CORE_EVENT_REGISTRY = EventRegistry(_CORE_DEFINITIONS)
