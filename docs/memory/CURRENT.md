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
- Latest completed v1.0A slice: **CLI + SeasonGuiService in-memory shadow pilot**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

The first production-source shadow pilot is enabled at two narrow boundaries:

- final CLI command dispatch in `fantasy.py`;
- read-only `SeasonGuiService.source_health()`.

Both use bounded in-memory events only. No persistent sink, argument/result
capture, authenticated payload capture, or exception-message capture is enabled.

The exact next implementation slice is:

**GUI background-task/lifecycle shadow pilot**

before player/DST/K/market/closure/data-source instrumentation.

## Verified State

- v0.36-repack1 remains commissioned.
- Prior v1.0A observability contracts remain test-validated.
- Shadow pilot:
  - targeted tests passed: 91;
  - full repository pytest passed: 443;
  - full compileall, strict memory health, and `git diff --check` passed;
  - CLI paired gate: PASS; baseline median 12650 ns,
    observed median 97950 ns,
    incremental 85300 ns;
  - SeasonGuiService paired gate: PASS; baseline median
    3850 ns,
    observed median 65150 ns,
    incremental 61300 ns;
  - output/exception behavior, Python RNG, and caller state probes matched;
  - service shadow events are inspectable in memory;
  - no production result or exception message is retained by the recorder.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics remain observers; observer failures fall back to the wrapped
  production call and cannot replace its result/exception.
- P/D/K remain separate specialist channels and are not instrumented by this
  pilot.
- No automatic persistence is enabled.
- Wider instrumentation still requires a narrow call-path gate.

## Current Implementation State

Implemented under `src/observability/`: context, events, registry, sinks,
provenance, invariants, redaction, snapshots, replay, diff, failure_bundle,
correlation, adapters, integration_plan, benchmark_gate, and shadow_pilot.

Production shadow integration currently exists only at:
- CLI final dispatch;
- `SeasonGuiService.source_health()`.

Not yet integrated:
- GUI background-task/lifecycle paths;
- player/DST/K/market/closure/data-source call sites;
- v1.0A commissioning gate.

## Current Validation State

`SHADOW PILOT ENABLED / TEST-VALIDATED / NON-PERSISTENT`

## Exact Next Action

Implement the **GUI background-task/lifecycle shadow pilot** with explicit
client/session/task correlation and the same non-interference/privacy/overhead
gate.

## Success Criterion

The next pilot must preserve GUI control flow and stale-client lifecycle
semantics while producing bounded in-memory evidence and meeting the configured
engineering gate.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-019 through D-021
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
