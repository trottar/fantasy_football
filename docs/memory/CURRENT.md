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
- Phase 0 I-001 is resolved.
- Latest completed v1.0A slice: **privacy-safe bounded failure-bundle contract**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

Completed observability foundation includes immutable context/events, explicit
sinks, provenance hashing, invariant results, privacy/redaction, local
snapshot/replay/diff evidence, and bounded privacy-safe failure bundles.

No production football/market/service/controller/GUI call site emits events or
automatically captures evidence.

The exact next implementation slice is:

**subsystem adapter contracts + CLI/service/background-task correlation**

## Verified State

- v0.36-repack1 remains commissioned.
- Prior v1.0A slices remain test-validated.
- Failure-bundle slice:
  - targeted observability tests passed: 58;
  - full repository pytest passed: 411;
  - full compileall, strict memory health, and `git diff --check` passed;
  - exception messages are omitted by default;
  - stack evidence omits absolute paths/source lines;
  - events/invariants are bounded to caller-selected tails;
  - state/reproduction/effects are redacted before persistence;
  - project-file modification state is distinct from runtime side effects;
  - exact-byte bundle integrity verification detects tampering;
  - automatic capture and production event emission remain disabled.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Production behavior changes retain the explicit authorization boundary.
- Persistent private/authenticated event emission remains blocked until an
  integration layer explicitly applies redaction and is tested.
- Failure bundles are caller-triggered evidence contracts, not exception
  handling policy or production control flow.

## Current Implementation State

Implemented under `src/observability/`: context, events, registry, sinks,
provenance, invariants, redaction, snapshots, replay, diff, and failure_bundle.

Not yet implemented:
- subsystem adapters;
- CLI/service/background-task correlation;
- GUI event emission/integration;
- diagnostic overhead/non-interference benchmarks and v1.0A commissioning gate.

## Current Validation State

`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`

## Exact Next Action

Implement **subsystem adapter contracts + CLI/service/background-task
correlation** without enabling automatic production emission.

## Success Criterion

The next checkpoint must expose consistent correlation boundaries for later
integration while preserving results, privacy, and random streams.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-013, D-014, D-016, D-017, D-018
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
