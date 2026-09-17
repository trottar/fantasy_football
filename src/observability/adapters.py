from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .context import RunContext
from .correlation import BoundaryKind, CorrelationBoundary, begin_boundary
from .registry import CORE_EVENT_REGISTRY, CORE_SUBSYSTEMS, EventRegistry


SPECIALIST_CHANNELS = frozenset({"player", "dst", "k"})


def _validate_subsystem(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("subsystem must be a string")
    if value not in CORE_SUBSYSTEMS:
        raise ValueError(f"unsupported observability subsystem: {value!r}")
    return value


def _check_channel_transition(parent: RunContext, target: str) -> None:
    if parent.subsystem in SPECIALIST_CHANNELS and target in SPECIALIST_CHANNELS:
        if parent.subsystem != target:
            raise ValueError(
                "direct P/D/K cross-channel correlation is not allowed: "
                f"{parent.subsystem!r} -> {target!r}"
            )


@dataclass(frozen=True)
class SubsystemAdapter:
    subsystem: str
    registry: EventRegistry = CORE_EVENT_REGISTRY

    def __post_init__(self) -> None:
        object.__setattr__(self, "subsystem", _validate_subsystem(self.subsystem))
        if not isinstance(self.registry, EventRegistry):
            raise TypeError("registry must be an EventRegistry")

    def begin(
        self,
        parent: RunContext,
        name: str,
        *,
        kind: BoundaryKind = BoundaryKind.SUBSYSTEM,
        action_id: str | None = None,
        attributes: Mapping[str, object] | None = None,
    ) -> CorrelationBoundary:
        _check_channel_transition(parent, self.subsystem)
        return begin_boundary(
            parent,
            kind=kind,
            name=name,
            subsystem=self.subsystem,
            action_id=action_id,
            attributes=attributes,
            registry=self.registry,
        )


class AdapterRegistry:
    def __init__(self, adapters: Mapping[str, SubsystemAdapter]):
        rows: dict[str, SubsystemAdapter] = {}
        for name, adapter in adapters.items():
            if not isinstance(adapter, SubsystemAdapter):
                raise TypeError("adapter registry values must be SubsystemAdapter")
            if name != adapter.subsystem:
                raise ValueError(
                    f"adapter key {name!r} does not match subsystem "
                    f"{adapter.subsystem!r}"
                )
            if name in rows:
                raise ValueError(f"duplicate adapter: {name}")
            rows[name] = adapter
        self._adapters = MappingProxyType(rows)

    def __len__(self) -> int:
        return len(self._adapters)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._adapters)

    def require(self, subsystem: str) -> SubsystemAdapter:
        try:
            return self._adapters[subsystem]
        except KeyError as exc:
            raise KeyError(f"subsystem adapter is not registered: {subsystem}") from exc


CORE_ADAPTER_REGISTRY = AdapterRegistry(
    {name: SubsystemAdapter(name) for name in sorted(CORE_SUBSYSTEMS)}
)
