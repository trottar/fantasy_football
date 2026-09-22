# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: memory_system_refinement
memory_refinement_step: M4_content_complete_M5_after_durable_checkpoint
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

**M4 — handoff contract: CONTENT COMPLETE.**

The handoff contract now requires:

- `CURRENT.md` remains the sole authoritative resumable project state;
- `CURRENT_HANDOFF.md` records only exceptional cross-session transition state
  that is not already recoverable from `CURRENT.md` and canonical references;
- a normal stable checkpoint may explicitly record no exceptional transfer state;
- completed checkpoint summaries, roadmap state, scientific rules, validation
  matrices, and superseded handoff history do not belong in the live handoff;
- transition detail is removed when resolved rather than accumulated;
- startup membership/ordering is unchanged by M4 and remains an M5 decision.

## Verified State

- `v0.36-repack1` remains the commissioned 0.X runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic `.ffpkg` delivery and declarative staging infrastructure are **PUSHED /
  REMOTE VERIFIED**.
- M0, M1, M2, M3A, and M3B are **PUSHED / REMOTE VERIFIED**.
- M4 handoff-contract content is recorded at
  `evidence/MEMORY_M4_HANDOFF_CONTRACT_2026-09-21.md`.
- The retained Phase 1B closure-shadow candidate remains isolated and unchanged.
  Its established candidate/test/probe gates remain valid and must not be rerun
  without new evidence.
- Persistent runtime evidence remains **DISABLED**.
- No football/model/application semantics are changed by M0-M4 maintenance.

## Calendar / Evidence Gates

- Use Week 1/2 as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Causally valid Week 3 capture outranks nonessential M5-M7 or Phase 1B work.
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

Resolve M4 durability from the repository context containing these files. If
remote `main` does not yet contain the exact M4 handoff-policy/evidence state,
publish only the reviewed M4 checkpoint. If remote `main` already contains it,
advance to **M5 — startup contract decision**.

M5 must explicitly decide the startup model; M4 does not silently alter the
five-file startup set.

## Relevant References

- `MAINTENANCE.md`
- `handoffs/CURRENT_HANDOFF.md`
- `templates/CURRENT_HANDOFF.md`
- `evidence/MEMORY_M4_HANDOFF_CONTRACT_2026-09-21.md`
- `evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- `roadmap/STATUS.md`
- `../../KNOWN_ISSUES.md`
