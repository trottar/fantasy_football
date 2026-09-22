# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: memory_system_refinement
memory_refinement_step: M3A_content_complete_M3B_after_durable_checkpoint
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Refine the repository-backed durable-memory system in small, independently
reviewable checkpoints while preserving the commissioned football/runtime state
and the irreversible Week 3 prospective-capture gate.

M0 audited the system, M1 reconciled active/planning state, M2 established
checkpoint-identity semantics, and M3 is split so procedure ownership and curated
durable-memory cleanup are reviewed separately.

## Current Work Item

**M3A — procedure ownership / delivery wording cleanup: CONTENT COMPLETE.**

M3A removes obsolete ZIP/PowerShell checkpoint wording and restores one canonical
owner for detailed repository checkpoint mechanics:

- `patches/PATCH_PROTOCOL.md` owns repository checkpoint mechanics;
- `COMMUNICATION.md` owns communication lifecycle and evidence-return behavior;
- `TOOLS.md` owns environment/tool commands and proven operational facts;
- `README.md` maps memory roles and points to canonical owners;
- `DECISION_LOG.md` preserves D-009's authorization/human boundary while marking
  its old delivery mechanics superseded by D-025.

M3A does not yet rewrite `MEMORY.md`; that is M3B.

## Verified State

- `v0.36-repack1` remains the authoritative commissioned 0.X runtime baseline;
  internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic text `.ffpkg` delivery and declarative isolated staging infrastructure
  are **PUSHED / REMOTE VERIFIED**.
- M0 memory-system audit, M1 active/planning reconciliation, and M2
  checkpoint-identity semantics are **PUSHED / REMOTE VERIFIED**.
- M3A procedure/ownership cleanup is content-complete and recorded at
  `evidence/MEMORY_M3A_PROCEDURE_OWNERSHIP_CLEANUP_2026-09-21.md`.
- The retained Phase 1B closure-shadow candidate remains isolated and unchanged.
  Its established candidate/test/probe gates remain valid and must not be rerun
  without new evidence.
- Persistent runtime evidence remains **DISABLED**.
- No football/model/application semantics are changed by M0-M3A maintenance.

## Calendar / Evidence Gates

- Use Week 1/2 as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Causally valid Week 3 capture outranks nonessential M3B-M7 or Phase 1B work.
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

Resolve M3A durability from the repository context containing these files. If
remote `main` does not yet contain the exact M3A procedure/evidence state, publish
only the reviewed M3A checkpoint. If remote `main` already contains it, advance
to **M3B — curated durable-memory cleanup**.

Do not start M4-M7 or resume Phase 1B before M3B is separately reviewed, and do
not create a follow-up commit solely to record M3A's own commit SHA.

## Relevant References

- `evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- `evidence/MEMORY_CHECKPOINT_IDENTITY_SEMANTICS_2026-09-21.md`
- `evidence/MEMORY_M3A_PROCEDURE_OWNERSHIP_CLEANUP_2026-09-21.md`
- `MAINTENANCE.md`
- `COMMUNICATION.md`
- `TOOLS.md`
- `patches/PATCH_PROTOCOL.md`
- `decisions/D-025_GENERIC_DELIVERY_INFRASTRUCTURE.md`
- `roadmap/STATUS.md`
- `../../KNOWN_ISSUES.md`
