# Current Project State

---
state_updated: 2026-09-20
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: 2026_season_roadmap_memory_checkpoint
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Complete the documentation-only 2026 season-roadmap/memory checkpoint through
`PUSHED / REMOTE VERIFIED` before resuming technical implementation. Preserve
`v0.36-repack1` and the existing v1.0A technical frontier unchanged.

The season operates on two clocks:
- **calendar gates** protect irreversible prospective captures/operations;
- **evidence gates** authorize diagnosis/calibration only when prospective
  Data/MC closure supports them.

Calendar pressure never authorizes hindsight or evidence-free tuning.

## Verified State

- `v0.36-repack1` remains **COMMISSIONED**; internal version `0.36`.
- Latest completed v1.0A technical slice: GUI background-task/lifecycle
  in-memory shadow pilot.
- Its standing validation remains 107 targeted tests, 452 full tests, compileall,
  strict memory health, diff-check, paired non-interference/overhead gates,
  cancellation propagation, and stale-page evidence behavior.
- Persistent runtime sink remains disabled.
- No football/model/application/runtime behavior changes are authorized by this
  documentation checkpoint.
- Read-only GitHub audit on 2026-09-20 observed `main` at
  `f22115e7c75357e4321912831a3f99d1ea3e5c3f`; validated local state remains
  authoritative between checkpoints.

## Current Work Item

Establish the accepted planning/memory structure:
- `docs/ROADMAP.md` — long-range phases and acceptance gates;
- `roadmap/SEASON_2026.md` — Week 1-18 calendar and evidence deadlines;
- `docs/KNOWN_ISSUES.md` — open/deferred/resume conditions;
- `architecture/PHASE_V1_CONTEXT.md` — stable prospective v1.X contract;
- D-023 — calendar/evidence gates and playoff freeze;
- expanded weekly closure and memory-update templates.

The first v1 package attempt on 2026-09-20 reached strict memory health, found
that rendered `MEMORY.md` crossed its soft line threshold, and rolled back exact
target bytes. The corrected package relocates detail to typed roadmap/context
records and keeps bootstrap files below their soft limits.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Manager behavior remains separate from intrinsic football utility.
- `0.X` remains a-priori; observed 2026 outcomes may inform only `1.X`.
- Freeze week-open and consequential decision-time state before relevant
  outcomes; never backfill a missed prospective capture.
- Use `MC -> Data -> closure -> diagnosis -> calibration`.
- `screen != authority`; diagnostics remain observers.
- A date can force capture/freeze but cannot force an evidence gate to pass.
- Major empirical calibration freezes by default during fantasy Weeks 14-17;
  structural correctness repairs remain separately reviewable.

## Current Implementation State

Not yet integrated in production v1.0A:
- data-source season sync;
- player, DST, kicker, market/behavior, and closure call sites;
- persistent runtime sink;
- final v1.0A commissioning gate.

Accepted next technical slice after this memory checkpoint:
**data-source season-sync shadow pilot**.

## Current Validation State

`GUI LIFECYCLE SHADOW ENABLED / TEST-VALIDATED / NON-PERSISTENT`

Roadmap/memory checkpoint:
`DOCUMENTATION-ONLY / TECHNICAL WORK GATED UNTIL PUSHED / REMOTE VERIFIED`

## Repository / Handoff Boundary

`assistant package -> user local run -> returned log -> assistant verification -> separate push commands -> user push -> read-only remote verification`

Prepared, locally applied, committed, pushed, and remote-verified states are
distinct. Local apply uses target predecessor contracts; isolated staging-clone
Git state authorizes commit/push.

## Exact Next Action

Complete this **2026 season-roadmap durable-memory checkpoint** through
`PUSHED / REMOTE VERIFIED`. Then begin the **data-source season-sync shadow
pilot** as the first technical implementation slice.

## Success Criterion

A fresh session can recover the production baseline, technical frontier, weekly
calendar gates, evidence-gate policy, prospective capture/closure cycle,
calibration/playoff-freeze rules, open/deferred work, and repository actor state
without chat history.

## Do Not Reopen Without New Evidence

- Phase 0 / `v0.36-repack1` commissioning.
- Completed CLI/service and GUI lifecycle shadow pilots.
- `P ⊕ D ⊕ K`, the 0.X/1.X boundary, behavior/football separation, and the
  human-in-the-loop checkpoint actor boundary.
- Resolved/deferred investigations without new evidence.

## Relevant References

- `../ROADMAP.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../KNOWN_ISSUES.md`
- `architecture/PHASE_V1_CONTEXT.md`
- `decisions/D-023_2026_SEASON_GATED_ROADMAP.md`
- `architecture/PHYSICS_MODEL.md`
- `architecture/INFORMATION_CAUSALITY.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `patches/PATCH_PROTOCOL.md`
- `evidence/MEMORY_WORKFLOW_AUDIT_2026-09-18.md`
- `evidence/MEMORY_HANDOFF_RECONCILIATION_ROOT_CAUSE_2026-09-20.md`
- `memory/2026-09-20.md`
