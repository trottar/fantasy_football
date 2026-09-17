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
- Latest completed v1.0A slice: **subsystem adapters + correlation contracts**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

Completed observability foundation includes immutable context/events, explicit
sinks, provenance hashing, invariant results, privacy/redaction, local
snapshot/replay/diff evidence, bounded failure bundles, and opt-in subsystem
adapter/correlation contracts.

No production football/market/service/controller/GUI call site emits events or
automatically captures evidence.

The exact next implementation slice is:

**production integration design + non-interference/overhead benchmark gate**

before any broad GUI/CLI/service instrumentation is enabled.

## Verified State

- v0.36-repack1 remains commissioned.
- Prior v1.0A slices remain test-validated.
- Adapter/correlation slice:
  - targeted observability tests passed: 67;
  - full repository pytest passed: 420;
  - full compileall, strict memory health, and `git diff --check` passed;
  - CLI -> service -> background-task parent correlation is explicit;
  - subsystem identity is typed and validated;
  - direct P/D/K cross-channel nesting is rejected;
  - boundary attributes are immutable copies;
  - error events retain exception type but not exception message;
  - adapters own no sink and emit nothing automatically;
  - Python RNG state is unchanged by correlation construction.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Production behavior changes retain the explicit authorization boundary.
- P/D/K remain separate specialist channels.
- Correlation contracts construct evidence only; persistence requires explicit
  caller action.

## Current Implementation State

Implemented under `src/observability/`: context, events, registry, sinks,
provenance, invariants, redaction, snapshots, replay, diff, failure_bundle,
correlation, and adapters.

Not yet implemented/integrated:
- production CLI/service/background-task call-site instrumentation;
- GUI event emission/integration;
- overhead/non-interference benchmark gate;
- v1.0A commissioning gate.

## Current Validation State

`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`

## Exact Next Action

Design and validate the **production integration + overhead/non-interference
gate** before enabling broad call-site instrumentation.

## Success Criterion

The next checkpoint must demonstrate that proposed instrumentation preserves
results, causal state, random streams, privacy boundaries, and acceptable
runtime overhead before integration is commissioned.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-013 through D-019 as applicable
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
