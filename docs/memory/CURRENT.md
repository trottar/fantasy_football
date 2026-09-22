# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: memory_system_refinement
memory_refinement_step: M5_content_complete_M6_after_durable_checkpoint
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Refine the repository-backed durable-memory system in small, independently
reviewable checkpoints while preserving the commissioned football/runtime state
and the irreversible Week 3 prospective-capture gate.

M0-M3 established current-state, identity, procedure-ownership, and curated-memory
boundaries. M4 now formalizes the handoff as exceptional transition metadata
rather than a second copy of `CURRENT.md`.

## Current Work Item

**M5 — startup contract decision: CONTENT COMPLETE.**

M5 retains the five-file core for substantial work:

`AGENTS -> CURRENT -> MEMORY -> CURRENT_HANDOFF -> USER`

All five are read in full. Retrieval becomes selective only **after** that core:
use CURRENT/task-linked canonical records, exact source, and tests as needed
instead of eagerly loading the wider memory hierarchy.

Ownership is explicit:

- `AGENTS.md` owns the operational startup contract;
- `MAINTENANCE.md` owns startup-contract health/coherence;
- `README.md` summarizes navigation;
- M6, not M5, owns checker enforcement.

## Verified State

- `v0.36-repack1` remains the commissioned 0.X runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic `.ffpkg` delivery and declarative staging infrastructure are **PUSHED /
  REMOTE VERIFIED**.
- M0-M4 and M4R1 are **PUSHED / REMOTE VERIFIED**.
- M5 startup-contract content is recorded at
  `evidence/MEMORY_M5_STARTUP_CONTRACT_DECISION_2026-09-21.md`.
- The retained Phase 1B closure-shadow candidate remains isolated and unchanged.
  Its established candidate/test/probe gates remain valid and must not be rerun
  without new evidence.
- Persistent runtime evidence remains **DISABLED**.
- No football/model/application semantics are changed by M0-M5 maintenance.

## Calendar / Evidence Gates

- Use Week 1/2 as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Causally valid Week 3 capture outranks nonessential M6-M7 or Phase 1B work.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from intrinsic football utility.
- `screen != authority`.
- Only decision-time information may influence prospective actions.
- `0.X` remains a-priori; observed 2026 outcomes may tune only `1.X`.
- Observability remains non-interfering and non-authoritative.

## Exact Next Action

Resolve M5 durability from the repository context containing these files. If
remote `main` does not yet contain the exact M5 startup-contract/evidence state,
publish only the reviewed M5 checkpoint. If remote `main` already contains it,
advance to **M6 — memory-health enforcement**.

M6 may encode this selected startup contract in tooling, but it must not redesign
the contract.

## Relevant References

- `AGENTS.md`
- `MAINTENANCE.md`
- `README.md`
- `evidence/MEMORY_M5_STARTUP_CONTRACT_DECISION_2026-09-21.md`
- `evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- `roadmap/STATUS.md`
- `../../KNOWN_ISSUES.md`
