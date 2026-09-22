# Current Handoff

`CURRENT.md` is authoritative. This file is only a compact resume and operational
warning surface; it cannot override current state.

## Resume State

- Commissioned runtime: `v0.36-repack1`, internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow: **COMPLETE / COMMISSIONED**.
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED**.
- M0 audit, M1 active/planning reconciliation, and M2 checkpoint identity
  semantics: **COMPLETE / DURABLE**.
- M3A procedure/ownership cleanup: **CONTENT COMPLETE**.
- M3B curated `MEMORY.md` cleanup: **NEXT after durable M3A**.
- Retained Phase 1B closure-shadow candidate: **PREFLIGHT VALIDATED / ISOLATED /
  UNCHANGED**. Do not rerun established gates without new evidence.

## Resume Instruction

1. Follow the current startup contract.
2. Resolve M3A durability from the repository context containing this handoff.
3. If remote `main` contains the M3A evidence/procedure state, proceed to M3B.
4. If M3A exists only locally, publish only the reviewed M3A scope first.
5. Do not jump to M4-M7 or Phase 1B.
6. Preserve the Week 3 week-open prospective capture even if memory work slips.

## Critical Boundaries

- control root != isolated staging clone != commissioned runtime;
- local-apply identity != staged tree identity != commit identity != remote ref;
- checkpoint mechanics are canonical in `patches/PATCH_PROTOCOL.md`;
- communication behavior is canonical in `COMMUNICATION.md`;
- environment/tool commands are canonical in `TOOLS.md`;
- no direct GitHub connector writes for project checkpoints;
- no football/model semantic change from memory maintenance;
- persistent evidence sink remains disabled;
- Week 3 prospective capture is causally irreversible and outranks nonessential
  development.

## Canonical Pointers

- active state: `../CURRENT.md`
- M3A evidence: `../evidence/MEMORY_M3A_PROCEDURE_OWNERSHIP_CLEANUP_2026-09-21.md`
- memory policy: `../MAINTENANCE.md`
- communication lifecycle: `../COMMUNICATION.md`
- tool procedures: `../TOOLS.md`
- checkpoint mechanics: `../patches/PATCH_PROTOCOL.md`
