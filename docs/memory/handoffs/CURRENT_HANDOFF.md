# Current Handoff

`CURRENT.md` is authoritative. This file is only a compact resume and operational
warning surface; it cannot override current state.

## Resume State

- Commissioned runtime: `v0.36-repack1`, internal `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow: **COMPLETE / COMMISSIONED**.
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED**.
- M0-M2 and M3A: **COMPLETE / DURABLE**.
- M3B curated durable-memory cleanup: **CONTENT COMPLETE**.
- M4 handoff contract: **NEXT after durable M3B**.
- Retained Phase 1B closure-shadow candidate: **PREFLIGHT VALIDATED / ISOLATED /
  UNCHANGED**. Do not rerun established gates without new evidence.

## Resume Instruction

1. Follow the current startup contract.
2. Resolve M3B durability from the repository context containing this handoff.
3. If remote `main` contains the M3B evidence/curated-memory state, proceed to M4.
4. If M3B exists only locally, publish only the reviewed M3B scope first.
5. Do not jump to M5-M7 or Phase 1B.
6. Preserve the Week 3 week-open prospective capture even if memory work slips.

## Critical Boundaries

- `CURRENT.md` owns active state; `MEMORY.md` owns curated durable knowledge;
- checkpoint procedure belongs to `patches/PATCH_PROTOCOL.md`;
- control root != isolated staging clone != commissioned runtime;
- no direct GitHub connector writes for project checkpoints;
- no football/model semantic change from memory maintenance;
- persistent evidence sink remains disabled;
- Week 3 prospective capture is causally irreversible and outranks nonessential
  development.

## Canonical Pointers

- active state: `../CURRENT.md`
- curated durable memory: `../MEMORY.md`
- M3B evidence: `../evidence/MEMORY_M3B_CURATED_DURABLE_MEMORY_CLEANUP_2026-09-21.md`
- memory policy: `../MAINTENANCE.md`
- checkpoint mechanics: `../patches/PATCH_PROTOCOL.md`
- roadmap status: `../roadmap/STATUS.md`
