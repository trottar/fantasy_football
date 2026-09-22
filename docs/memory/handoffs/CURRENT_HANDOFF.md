# Current Handoff

`CURRENT.md` is authoritative. This file is only a compact resume and operational
warning surface; it cannot override current state.

## Resume State

- Commissioned runtime: `v0.36-repack1`, internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow: **COMPLETE / COMMISSIONED**.
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED**.
- M0 memory-system audit: **COMPLETE / DURABLE**.
- M1 active/planning reconciliation: **COMPLETE / DURABLE**.
- M2 checkpoint-identity semantics: **CONTENT COMPLETE**.
- Retained Phase 1B closure-shadow candidate: **PREFLIGHT VALIDATED / ISOLATED /
  UNCHANGED**. Do not rerun established gates without new evidence.

## Resume Instruction

1. Read the complete bootstrap set required by the current policy.
2. Resolve M2 durability from the repository context containing this handoff and
   `CURRENT.md`; do not expect either file to name its own future commit SHA.
3. If remote `main` already contains the M2 evidence/policy state, proceed to M3
   procedure/ownership cleanup.
4. If M2 exists only as local-applied content, publish only the reviewed M2 scope
   through the generic staging/publication workflow before M3.
5. Do not jump to M4-M7 or Phase 1B.
6. Preserve the Week 3 week-open prospective capture even if memory work slips.

## Critical Boundaries

- control root != isolated staging clone != commissioned runtime;
- local-apply identity != staged tree identity != commit identity != remote ref;
- exact current committed checkpoint identity comes from Git/ref context, not an
  embedded self-SHA in active memory;
- historical/predecessor SHAs are allowed when their role is explicit;
- no direct GitHub connector writes for project checkpoints;
- no football/model semantic change from memory maintenance;
- persistent evidence sink remains disabled;
- Week 3 prospective capture is causally irreversible and outranks nonessential
  development.

## Canonical Pointers

- active state: `../CURRENT.md`
- M0 audit: `../evidence/MEMORY_SYSTEM_M0_AUDIT_2026-09-21.md`
- M2 identity semantics: `../evidence/MEMORY_CHECKPOINT_IDENTITY_SEMANTICS_2026-09-21.md`
- memory policy: `../MAINTENANCE.md`
- checkpoint mechanics: `../patches/PATCH_PROTOCOL.md`
- roadmap status: `../roadmap/STATUS.md`
