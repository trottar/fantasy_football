"""Cross-cutting v1.0A observability contracts.

This package is intentionally observational.  It does not import or call
football, market, Monte Carlo, or GUI business logic.
"""

from .context import RunContext, new_correlation_id
from .events import EVENT_SCHEMA_VERSION, StructuredEvent, make_event
from .provenance import (
    SourceProvenance,
    canonical_json_bytes,
    collect_provenance,
    git_source_state,
    read_release_version,
    sha256_bytes,
    sha256_file,
    sha256_json,
    sha256_json_file,
)
from .registry import (
    CORE_EVENT_REGISTRY,
    CORE_SUBSYSTEMS,
    EventDefinition,
    EventLevel,
    EventRegistry,
)
from .sinks import (
    EventSink,
    FanoutSink,
    HumanTextSink,
    JsonlSink,
    MemorySink,
    emit_all,
    format_human_event,
)

__all__ = [
    "CORE_EVENT_REGISTRY",
    "CORE_SUBSYSTEMS",
    "EVENT_SCHEMA_VERSION",
    "EventDefinition",
    "EventLevel",
    "EventRegistry",
    "EventSink",
    "FanoutSink",
    "HumanTextSink",
    "JsonlSink",
    "MemorySink",
    "RunContext",
    "SourceProvenance",
    "StructuredEvent",
    "canonical_json_bytes",
    "collect_provenance",
    "emit_all",
    "format_human_event",
    "git_source_state",
    "make_event",
    "new_correlation_id",
    "read_release_version",
    "sha256_bytes",
    "sha256_file",
    "sha256_json",
    "sha256_json_file",
]
