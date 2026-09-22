# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: memory_system_refinement
memory_refinement_step: M2_content_complete_M3_after_durable_checkpoint
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Refine the repository-backed durable-memory system in small, independently
reviewable checkpoints while preserving the commissioned football/runtime state
and the irreversible Week 3 prospective-capture gate.

M0 audited the memory system, M1 reconciled active/planning state, and M2 defines
checkpoint-identity semantics so active memory no longer needs a follow-up commit
merely to write the SHA of the checkpoint that contains it.

## Current Work Item

**M2 — checkpoint identity semantics: CONTENT COMPLETE.**

Durability/publication state is intentionally resolved from the Git context that
contains these files, not from a future self-SHA embedded in `CURRENT.md`.

The M2 contract distinguishes:

- local package state by package ID plus predecessor/target identities;
- isolated staging state by expected remote predecessor plus staged tree identity;
- committed state by commit/parent/tree identity;
- pushed/remote-verified state by the remote ref actually containing the commit;
- historical concrete SHAs in evidence/history by their explicit historical role.

If this exact M2 state is already present on remote `main`, the M2 durability gate
is satisfied and M3 may begin. If it exists only as local-applied content, publish
only the reviewed M2 scope before beginning M3.

## Verified State

- `v0.36-repack1` remains the authoritative commissioned 0.X runtime baseline;
  internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic text `.ffpkg` delivery and declarative isolated staging infrastructure
  are **PUSHED / REMOTE VERIFIED**.
- M0 memory-system audit and M1 active/planning reconciliation are **PUSHED /
  REMOTE VERIFIED**.
- M2 checkpoint-identity semantics are content-complete and recorded at
  `evidence/MEMORY_CHECKPOINT_IDENTITY_SEMANTICS_2026-09-21.md`.
- The retained Phase 1B closure-shadow candidate remains isolated and unchanged.
  Its established candidate/test/probe gates remain valid and must not be rerun
  without new evidence.
- Phase 1C P/D/K observability, Phase 1D manager/market observability, and Phase
  1E persistent evidence authorization remain separately gated and not started.
- Persistent runtime evidence remains **DISABLED**.
- No football/model semantics are changed by M0-M2 memory maintenance.

## Calendar / Evidence Gates

- Use Week 1/2 as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Causally valid Week 3 capture outranks nonessential M3-M7 or Phase 1B work.
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

Resolve the M2 durability state from the repository context containing these
files. If remote `main` does not yet contain this exact M2 policy/evidence state,
publish only the reviewed M2 checkpoint. If remote `main` already contains it,
advance to **M3 — procedure/ownership cleanup**. Do not create a documentation-only
follow-up commit merely to write the M2 commit SHA into active memory.

## Relevant References

- `evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- `evidence/MEMORY_CHECKPOINT_IDENTITY_SEMANTICS_2026-09-21.md`
- `MAINTENANCE.md`
- `patches/PATCH_PROTOCOL.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../../KNOWN_ISSUES.md`
- `decisions/D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`
- `decisions/D-025_GENERIC_DELIVERY_INFRASTRUCTURE.md`
