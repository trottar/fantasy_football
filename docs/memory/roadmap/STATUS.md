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
- Memory-system refinement: **M0-M5 COMPLETE / M4R1 COMPLETE /
  M6 CONTENT COMPLETE / M7 NEXT AFTER DURABLE M6**
- Phase 1B closure instrumentation: **PREFLIGHT VALIDATED / RETAINED CANDIDATE /
  CHECKPOINT DEFERRED DURING MEMORY REFINEMENT**
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
- M6 — memory-health enforcement: **CONTENT COMPLETE**
- M7 — fresh-session integration test: **NEXT after M6 is durable**

M6 encodes the selected M1-M5 memory representation contracts in observational
health tooling. It checks startup-contract agreement, CURRENT structure, handoff
role/authority, durable-memory role separation, and rendered-text regressions
without trying to infer substantive football truth from prose.

The Week 3 prospective-capture gate outranks nonessential M7 progress.

## Phase 1A — Commissioned Result

The outer `sync_season_snapshot` observability boundary is commissioned with
privacy/non-interference and runtime validation complete. Production football
semantics remain unchanged and the persistent sink remains disabled.

Canonical evidence:
`../evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`.

## Phase 1B — Retained Candidate

Closure instrumentation remains the next technical surface after memory
refinement. The retained candidate already passed its established
source/test/probe gates and remains frozen unless new evidence invalidates it.

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
- M4 evidence: `../evidence/MEMORY_M4_HANDOFF_CONTRACT_2026-09-21.md`
- M4R1 evidence: `../evidence/MEMORY_M4R1_MAINTENANCE_NEWLINE_REPAIR_2026-09-21.md`
- M5 evidence: `../evidence/MEMORY_M5_STARTUP_CONTRACT_DECISION_2026-09-21.md`
- M6 evidence: `../evidence/MEMORY_M6_MEMORY_HEALTH_ENFORCEMENT_2026-09-21.md`
- handoff contract: `../MAINTENANCE.md`
- handoff template: `../templates/CURRENT_HANDOFF.md`
- long-range roadmap: `../../ROADMAP.md`
- 2026 weekly map: `SEASON_2026.md`
- known issues: `../../KNOWN_ISSUES.md`
