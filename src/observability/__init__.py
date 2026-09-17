"""Cross-cutting v1.0A observability contracts.

This package is intentionally observational.  It does not import or call
football, market, Monte Carlo, or GUI business logic.
"""

from .context import RunContext, new_correlation_id
from .events import EVENT_SCHEMA_VERSION, StructuredEvent, make_event
from .registry import (
    CORE_EVENT_REGISTRY,
    CORE_SUBSYSTEMS,
    EventDefinition,
    EventLevel,
    EventRegistry,
)

__all__ = [
    "CORE_EVENT_REGISTRY",
    "CORE_SUBSYSTEMS",
    "EVENT_SCHEMA_VERSION",
    "EventDefinition",
    "EventLevel",
    "EventRegistry",
    "RunContext",
    "StructuredEvent",
    "make_event",
    "new_correlation_id",
]
