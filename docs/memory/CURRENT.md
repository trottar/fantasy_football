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
- Latest completed v1.0A slice: **GUI background-task/lifecycle in-memory shadow pilot**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

Production shadow integration remains deliberately narrow:
- final CLI command dispatch;
- read-only `SeasonGuiService.source_health()`;
- selected-MC NiceGUI background task lifecycle;
- MC progress-pump task lifecycle;
- page mount/connect/disconnect/delete correlation.

GUI lifecycle evidence uses generated session/page/task IDs only. No persistent
sink, raw NiceGUI client ID, task arguments/results, authenticated payloads, or
exception messages are retained.

## Verified State

- v0.36-repack1 remains commissioned.
- targeted tests passed: 107;
- full repository pytest passed: 452;
- full compileall, strict memory health, and `git diff --check` passed;
- prior CLI and SeasonGuiService paired gates remain PASS;
- GUI background-task gate: PASS; baseline median
  690700 ns, observed median
  810650 ns, incremental
  119950 ns;
- task result/error/cancellation behavior and Python RNG matched;
- stale-page task termination emits evidence only and does not alter the task result;
- persistent sink remains disabled.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics remain observers and cannot become GUI control logic.
- Page deletion is observed; this pilot does not cancel or rewrite production work.
- P/D/K remain separate specialist channels and are untouched.
- Wider subsystem instrumentation remains separately gated.

## Current Implementation State

Implemented under `src/observability/`: prior v1.0A contracts plus
`gui_shadow.py` for bounded page/session/background-task lifecycle evidence.

Not yet integrated:
- player/DST/K/market/closure/data-source call sites;
- persistent runtime sinks;
- v1.0A commissioning gate.

## Current Validation State

`GUI LIFECYCLE SHADOW ENABLED / TEST-VALIDATED / NON-PERSISTENT`

## Exact Next Action

Prepare a **data-source season-sync shadow pilot** as the next single integration
surface, with the same non-interference/privacy/overhead authorization gate.

## Success Criterion

The next pilot must preserve data-source behavior and authenticated-data privacy
while producing bounded diagnostic evidence without changing football/model
semantics.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-020 through D-022
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
