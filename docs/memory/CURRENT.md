# Current Project State

---
state_updated: 2026-09-17
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
maintenance_status: healthy
---

## Authority Metadata

- Final `0.X` runtime baseline: **`v0.36-repack1` — COMMISSIONED**.
- Internal `VERSION` remains `0.36`; `repack1` is an artifact revision.
- Phase 0 I-001 is resolved.
- Latest completed v1.0A slice: **invariant registry + privacy/redaction primitives**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

Completed observability foundation:
- immutable run/action context;
- structured events and event registry;
- explicit memory/JSONL/human/fanout sinks;
- provenance/config/input hashing;
- immutable invariant definitions/results/registry;
- conservative recursive redaction and keyed pseudonymization primitives.

No production football/market/service/controller/GUI call site emits events yet.
No automatic redacting sink or persistent private/authenticated event logging is
enabled.

The exact next implementation slice is:

**local snapshot/replay/diff contract**

## Verified State

- v0.36-repack1 remains commissioned.
- Context/events slice: test-validated.
- Sinks/provenance slice: test-validated.
- Invariants/redaction slice:
  - targeted observability tests passed: 38;
  - full repository pytest passed: 391;
  - full compileall and `git diff --check` passed;
  - invariant results preserve PASS/FAIL/SKIP/ERROR explicitly;
  - invariant error results retain exception type without exception-message leakage;
  - redaction is recursive, copy-only, and conservative for secrets/auth IDs;
  - inline Authorization/cookie/ESPN secret patterns are redacted;
  - caller-supplied exact secret values are replaceable;
  - binary/depth fallbacks are conservative;
  - keyed HMAC pseudonymization is available for correlation-safe IDs;
  - RNG non-interference tests passed.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Production behavior changes retain the explicit authorization boundary.
- Persistent private/authenticated event emission remains blocked until an
  integration layer explicitly applies the redaction policy and is tested.
- Invariants are evidence contracts in this slice, not production enforcement
  hooks.

## Current Implementation State

Implemented under `src/observability/`:
- `context.py`
- `events.py`
- `registry.py`
- `sinks.py`
- `provenance.py`
- `invariants.py`
- `redaction.py`

Not yet implemented:
- snapshot/replay/diff;
- failure bundles;
- subsystem adapters;
- CLI/service/background-task correlation;
- GUI event emission/integration.

## Current Validation State

`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`

No blocker exists for the next observational slice.

## Exact Next Action

Implement the **v1.0A local snapshot/replay/diff contract** while keeping
production event emission disabled.

## Success Criterion

The next checkpoint must add replayable local evidence without changing model
results, exposing secrets, or requiring reconstruction from chat history.

## Do Not Reopen Without New Evidence

- I-001 final 0.X lineage reconciliation.
- historical v0.36-fixed1 artifact search;
- v0.36 packaging diagnosis;
- v0.36-repack1 GUI commissioning;
- resolved memory/manifest/diagnostic-tool QA defects.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Context/event decision: `decisions/D-013_V10A_CONTEXT_EVENT_CONTRACT.md`
- Sinks/provenance decision: `decisions/D-014_V10A_SINKS_PROVENANCE.md`
- Invariants/redaction decision: `decisions/D-016_V10A_INVARIANTS_REDACTION.md`
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
