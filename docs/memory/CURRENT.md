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
- Latest completed v1.0A slice: **production-integration design + non-interference/overhead gate**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

The observability substrate now includes immutable context/events, sinks,
provenance, invariants, privacy/redaction, replay/diff evidence, failure bundles,
subsystem adapters/correlation, a repository-grounded shadow integration plan,
and a paired non-interference/overhead benchmark gate.

No production football/market/service/controller/GUI call site emits events or
automatically captures/persists evidence.

The exact next implementation slice is:

**narrow shadow-integration pilot: CLI command boundary + SeasonGuiService**

with no persistent sink and with benchmark/non-interference authorization before
wider GUI/background/subsystem instrumentation.

## Verified State

- v0.36-repack1 remains commissioned.
- Prior v1.0A slices remain test-validated.
- Integration-gate slice:
  - targeted observability tests passed: 79;
  - full repository pytest passed: 432;
  - full compileall, strict memory health, and `git diff --check` passed;
  - proposed integration surfaces name real repository source paths;
  - all default integration points are shadow-only, non-persistent, and non-auto-emitting;
  - paired gate compares return/exception behavior from identical captured state;
  - Python RNG and caller-supplied state probes are compared and restored;
  - tiny-call overhead uses an absolute budget, while longer calls also require a relative budget;
  - gate results contain timing/boolean evidence, not returned values or exception messages.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Production behavior changes retain the explicit authorization boundary.
- P/D/K remain separate specialist channels.
- Integration begins in shadow mode with no automatic persistence.
- Broader instrumentation is not authorized by a contract alone; each pilot must
  pass non-interference/privacy/overhead evidence on the actual call path.

## Current Implementation State

Implemented under `src/observability/`: context, events, registry, sinks,
provenance, invariants, redaction, snapshots, replay, diff, failure_bundle,
correlation, adapters, integration_plan, and benchmark_gate.

Not yet integrated:
- production CLI/service call sites;
- GUI/background lifecycle emission;
- player/DST/K/market/closure/data-source call-site instrumentation;
- v1.0A commissioning gate.

## Current Validation State

`CHECKPOINTED / TEST-VALIDATED / SHADOW-INTEGRATION NOT YET ENABLED`

## Exact Next Action

Implement a **narrow shadow-integration pilot at the CLI command boundary and
SeasonGuiService**, with explicit in-memory/non-persistent diagnostics and paired
non-interference/overhead evidence before expansion.

## Success Criterion

The pilot must preserve outputs, exceptions, random/state channels, privacy, and
model semantics, while meeting the configured engineering overhead gate.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-013 through D-020 as applicable
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
