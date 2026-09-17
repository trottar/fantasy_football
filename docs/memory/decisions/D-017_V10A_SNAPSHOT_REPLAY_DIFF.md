# D-017 — v1.0A Local Snapshot / Replay / Diff Contract

**Status:** ACTIVE

## Decision

Adopt a local, privacy-aware replay-evidence format before production
observability integration.

### Snapshot

The writer persists only caller-supplied structured values, applies the
redaction policy before writing, uses a fixed member set, and atomically creates
a new destination. It does not ingest raw authenticated response files.

### Replay

Replay currently means integrity-verified evidence loading. Member exact-byte
lengths and SHA-256 values are checked before exposure. This slice does not
execute MC, recommendations, football utilities, or manager behavior.

### Diff

Structural diffs are bounded and redacted by default. They identify
added/removed/changed/type-changed paths without becoming recommendation logic.

### Integration boundary

No production call site automatically captures bundles. No private/authenticated
persistent emission is enabled. Execution replay and subsystem adapters remain
later integration work.
