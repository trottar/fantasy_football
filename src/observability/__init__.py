"""Cross-cutting v1.0A observability contracts.

This package is intentionally observational.  It does not import or call
football, market, Monte Carlo, or GUI business logic.
"""

from .context import RunContext, new_correlation_id
from .diff import DiffEntry, DiffKind, ReplayDiff, diff_replay_bundles, diff_values
from .events import EVENT_SCHEMA_VERSION, StructuredEvent, make_event
from .invariants import (
    CORE_INVARIANT_REGISTRY,
    InvariantDefinition,
    InvariantRegistry,
    InvariantResult,
    InvariantSeverity,
    InvariantStatus,
)
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
from .redaction import (
    BINARY_REPLACEMENT,
    DEFAULT_REPLACEMENT,
    DEPTH_REPLACEMENT,
    RedactionPolicy,
    RedactionResult,
    is_sensitive_key,
    pseudonymize_text,
    redact,
    redact_event,
    redact_value,
    redacted_event_json,
)
from .registry import (
    CORE_EVENT_REGISTRY,
    CORE_SUBSYSTEMS,
    EventDefinition,
    EventLevel,
    EventRegistry,
)
from .replay import (
    ReplayBundle,
    ReplayVerification,
    load_replay_bundle,
    verify_replay_bundle,
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
from .snapshots import (
    BUNDLE_MANIFEST_FILE,
    BUNDLE_SCHEMA_VERSION,
    CORE_MEMBER_FILES,
    BundleManifest,
    BundleMember,
    write_snapshot_bundle,
)

__all__ = [
    "BINARY_REPLACEMENT",
    "BUNDLE_MANIFEST_FILE",
    "BUNDLE_SCHEMA_VERSION",
    "BundleManifest",
    "BundleMember",
    "CORE_EVENT_REGISTRY",
    "CORE_INVARIANT_REGISTRY",
    "CORE_MEMBER_FILES",
    "CORE_SUBSYSTEMS",
    "DEFAULT_REPLACEMENT",
    "DEPTH_REPLACEMENT",
    "DiffEntry",
    "DiffKind",
    "EVENT_SCHEMA_VERSION",
    "EventDefinition",
    "EventLevel",
    "EventRegistry",
    "EventSink",
    "FanoutSink",
    "HumanTextSink",
    "InvariantDefinition",
    "InvariantRegistry",
    "InvariantResult",
    "InvariantSeverity",
    "InvariantStatus",
    "JsonlSink",
    "MemorySink",
    "RedactionPolicy",
    "RedactionResult",
    "ReplayBundle",
    "ReplayDiff",
    "ReplayVerification",
    "RunContext",
    "SourceProvenance",
    "StructuredEvent",
    "canonical_json_bytes",
    "collect_provenance",
    "diff_replay_bundles",
    "diff_values",
    "emit_all",
    "format_human_event",
    "git_source_state",
    "is_sensitive_key",
    "load_replay_bundle",
    "make_event",
    "new_correlation_id",
    "pseudonymize_text",
    "read_release_version",
    "redact",
    "redact_event",
    "redact_value",
    "redacted_event_json",
    "sha256_bytes",
    "sha256_file",
    "sha256_json",
    "sha256_json_file",
    "verify_replay_bundle",
    "write_snapshot_bundle",
]
