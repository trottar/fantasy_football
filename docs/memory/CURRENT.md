# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: memory_system_refinement
memory_refinement_step: M3B_content_complete_M4_after_durable_checkpoint
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Refine the repository-backed durable-memory system in small, independently
reviewable checkpoints while preserving the commissioned football/runtime state
and the irreversible Week 3 prospective-capture gate.

M0 audited the system, M1 reconciled active/planning state, M2 established
checkpoint-identity semantics, and M3 has now separated procedure ownership from
curated durable knowledge.

## Current Work Item

**M3B — curated durable-memory cleanup: CONTENT COMPLETE.**

M3B rewrites `MEMORY.md` around its actual ownership contract:

- preserve stable scientific/architectural invariants;
- preserve commissioned baselines and durable cross-phase conclusions;
- point to canonical evidence instead of copying validation matrices;
- remove sequential candidate -> commissioned chronology;
- remove staging-failure chronology;
- remove detailed repository actor/procedure duplication;
- remove ownership of the startup sequence from `MEMORY.md`.

M3A and M3B together complete M3 once M3B is durable.

## Verified State

- `v0.36-repack1` remains the authoritative commissioned 0.X runtime baseline;
  internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic `.ffpkg` delivery and declarative staging infrastructure are **PUSHED /
  REMOTE VERIFIED**.
- M0, M1, M2, and M3A are **PUSHED / REMOTE VERIFIED**.
- M3B curated-memory cleanup is content-complete and recorded at
  `evidence/MEMORY_M3B_CURATED_DURABLE_MEMORY_CLEANUP_2026-09-21.md`.
- The retained Phase 1B closure-shadow candidate remains isolated and unchanged.
  Its established candidate/test/probe gates remain valid and must not be rerun
  without new evidence.
- Persistent runtime evidence remains **DISABLED**.
- No football/model/application semantics are changed by M0-M3B maintenance.

## Calendar / Evidence Gates

- Use Week 1/2 as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Causally valid Week 3 capture outranks nonessential M4-M7 or Phase 1B work.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from intrinsic football utility.
- `screen != authority`.
- Only decision-time information may influence prospective actions.
- `0.X` remains a-priori; observed 2026 outcomes may tune only `1.X`.
- Observability remains non-interfering and non-authoritative.
- No authenticated payloads, arguments, returned snapshot/path data, or
  exception messages enter the commissioned Phase 1A shadow evidence.

## Exact Next Action

Resolve M3B durability from the repository context containing these files. If
remote `main` does not yet contain the exact M3B curated-memory/evidence state,
publish only the reviewed M3B checkpoint. If remote `main` already contains it,
advance to **M4 — handoff contract**.

Do not start M5-M7 or resume Phase 1B before M4 is separately reviewed, and do
not create a follow-up commit solely to record M3B's own commit SHA.

## Relevant References

- `MEMORY.md`
- `evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- `evidence/MEMORY_M3A_PROCEDURE_OWNERSHIP_CLEANUP_2026-09-21.md`
- `evidence/MEMORY_M3B_CURATED_DURABLE_MEMORY_CLEANUP_2026-09-21.md`
- `MAINTENANCE.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../../KNOWN_ISSUES.md`
