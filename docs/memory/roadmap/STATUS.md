# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Phase M repository/season-roadmap authority transition: **COMPLETE / PUSHED /
  REMOTE VERIFIED**
- Active engineering series: **v1.0A observability**
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Memory-system refinement: **M0-M7 COMPLETE / DURABLE**
- Week 3 week-open capture: **ACTIVE HARD CALENDAR GATE / BEFORE SEP 24 FIRST
  GAME**
- Phase 1B closure instrumentation: **PREFLIGHT VALIDATED / RETAINED CANDIDATE /
  AFTER WEEK 3 CAPTURE GATE**
- Phase 1C player/DST/kicker observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**

## Memory-System Refinement

- M0 — read-only audit: **COMPLETE / DURABLE**
- M1 — active/planning reconciliation: **COMPLETE / DURABLE**
- M2 — checkpoint identity semantics: **COMPLETE / DURABLE**
- M3A — procedure ownership / delivery wording cleanup: **COMPLETE / DURABLE**
- M3B — curated `MEMORY.md` cleanup: **COMPLETE / DURABLE**
- M4 — handoff contract: **COMPLETE / DURABLE**
- M4R1 — maintenance newline repair: **COMPLETE / DURABLE**
- M5 — startup contract decision: **COMPLETE / DURABLE**
- M6 — memory-health enforcement: **COMPLETE / DURABLE**
- M7 — fresh-session integration audit: **COMPLETE / DURABLE**

Remote `main` at
`b49104b84e34d3169d1b4876a3e1748e6553800a` contains the exact M7 evidence and
continuity state required by the M7 completion condition. The memory-refinement
series is therefore closed.

Canonical durability evidence:
`../evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`.

## Week 3 Prospective Capture

Week 3 is now the immediate operational frontier.

Before the Sep 24 first game, freeze the week-open state using the commissioned
`v0.36-repack1` baseline and only information available at capture time. Keep
authenticated/raw runtime material local and preserve an immutable,
provenance-bearing prospective artifact.

A missed prospective state is recorded as missing and is never backfilled.

## Phase 1A — Commissioned Result

The outer `sync_season_snapshot` observability boundary is commissioned with
privacy/non-interference and runtime validation complete. Production football
semantics remain unchanged and the persistent sink remains disabled.

Canonical evidence:
`../evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`.

## Phase 1B — Retained Candidate

Closure instrumentation remains the next technical observability surface after
the Week 3 week-open capture is secured. The retained candidate already passed
its established source/test/probe gates and remains frozen unless new evidence
invalidates them.

Phase 1B does not authorize P/D/K instrumentation, manager-behavior
instrumentation, or persistent evidence.

## 2026 Season Milestones

- Week 3 (Sep 24-28): first future hard prospective week-open capture gate.
- Week 5: preferred broader v1.0 observability commissioning target / first bye
  stress.
- After Week 5: first formal three-clean-week prospective closure review, if the
  captures are valid.
- Before Week 9: commission only evidence-supported calibration; otherwise defer.
- Weeks 12-13: playoff-readiness/model-freeze preparation.
- Before Week 14: playoff production baseline commissioned.
- Weeks 14-17: production-first; major empirical calibration frozen by default.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- No observed 2026 outcome may retroactively tune a v0.X model.
- Diagnostics remain observers, not decision/control logic.
- Missed prospective captures are recorded as missing, never backfilled.
- Persistent evidence requires a separate authorization gate.

## Canonical References

- active state: `../CURRENT.md`
- M5 evidence: `../evidence/MEMORY_M5_STARTUP_CONTRACT_DECISION_2026-09-21.md`
- M6 evidence: `../evidence/MEMORY_M6_MEMORY_HEALTH_ENFORCEMENT_2026-09-21.md`
- M7 integration evidence: `../evidence/MEMORY_M7_FRESH_SESSION_INTEGRATION_AUDIT_2026-09-22.md`
- M7 durability evidence: `../evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`
- startup/handoff health: `../MAINTENANCE.md`
- long-range roadmap: `../../ROADMAP.md`
- 2026 weekly map: `SEASON_2026.md`
- known issues: `../../KNOWN_ISSUES.md`
