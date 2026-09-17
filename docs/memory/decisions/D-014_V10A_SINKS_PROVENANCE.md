# D-014 — v1.0A Sinks and Provenance

<!-- FANTASY_D014_V10A_SINKS_PROVENANCE:BEGIN -->
## Decision

Keep event persistence explicit and dependency-injected. Do not create a hidden global logger or automatically emit from production paths.

Human text output omits payload by default. JSONL persists the complete structured event supplied by the caller, so production/private integration remains blocked until the redaction contract is implemented and tested.

Use canonical semantic JSON hashing for configuration identity and exact-byte hashing for frozen input snapshot identity. Git provenance records commit + tracked-dirty state but does not publish changed path names.
<!-- FANTASY_D014_V10A_SINKS_PROVENANCE:END -->
