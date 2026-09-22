# Current Handoff

`CURRENT.md` is authoritative. This file is only a compact resume and operational
warning surface; it cannot override current state.

## Resume State

- Commissioned runtime: `v0.36-repack1`, internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow: **COMPLETE / COMMISSIONED**.
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED** at `e52665db5b0799bf76f09cbacbac5edf44e507a9`.
- M0 memory-system audit: **COMPLETE**.
- M1 active/planning reconciliation: **CONTENT COMPLETE**.
- Next memory-design step: **M2 checkpoint-identity semantics**, but only after
  the M0+M1 memory checkpoint is `PUSHED / REMOTE VERIFIED`.
- Retained Phase 1B closure-shadow candidate: **PREFLIGHT VALIDATED / ISOLATED /
  UNCHANGED**. Do not rerun established gates without new evidence.

## Resume Instruction

1. Read the complete bootstrap set required by the current policy.
2. Check whether the M0+M1 memory checkpoint containing
   `MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md` and the six reconciled active/planning
   files is already `PUSHED / REMOTE VERIFIED`.
3. If not, publish only that reviewed scope through the generic staging workflow.
4. If yes, proceed to M2. Do not jump to M3-M7 or Phase 1B.
5. Preserve the Week 3 week-open prospective capture even if memory work slips.

## Critical Boundaries

- control root != isolated staging clone != commissioned runtime;
- no direct GitHub connector writes for project checkpoints;
- generic delivery owns transport/execution mechanics; package entrypoints own
  target-specific predecessor/rollback/idempotence/validation;
- no football/model semantic change from memory maintenance;
- persistent evidence sink remains disabled;
- Week 3 prospective capture is causally irreversible and outranks nonessential
  development.

## Canonical Pointers

- active state: `../CURRENT.md`
- M0 audit: `../evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- roadmap status: `../roadmap/STATUS.md`
- season gates: `../roadmap/SEASON_2026.md`
- checkpoint mechanics: `../patches/PATCH_PROTOCOL.md`
