# Current Handoff

`CURRENT.md` is authoritative. This file is a compact resume/operational-warning
surface and cannot override it.

## Last Completed Technical Checkpoint

v1.0A GUI background-task/lifecycle in-memory shadow pilot.

Result:

`GUI LIFECYCLE SHADOW ENABLED / TEST-VALIDATED / NON-PERSISTENT`

The accepted technical frontier remains:

**data-source season-sync shadow pilot**

## Active Repository Gate

Before that technical work begins, complete the documentation-only
**2026 season-roadmap durable-memory checkpoint** through:

`local apply -> assistant verification -> separate staging/manifest/commit/push -> read-only remote verification`

If remote verification already confirms this checkpoint, treat the gate as
satisfied and resume the technical frontier above.

Do not infer `PUSHED / REMOTE VERIFIED` merely from this file.

## Resume Instruction

1. Read `AGENTS.md`, `CURRENT.md`, `MEMORY.md`,
   `handoffs/CURRENT_HANDOFF.md`, and `USER.md`.
2. Read `docs/ROADMAP.md`, `roadmap/STATUS.md`, and
   `roadmap/SEASON_2026.md`.
3. Read D-023 and `architecture/PHASE_V1_CONTEXT.md`.
4. Determine the actual repository checkpoint state.
5. If the roadmap/memory checkpoint is not remote verified, finish that
   transition first.
6. Once it is remote verified, prepare the data-source season-sync shadow pilot
   as the next single technical integration surface.

## Critical Boundaries

- no direct GitHub connector writes for checkpoints;
- no football/model/application behavior change in the memory checkpoint;
- preserve `P ⊕ D ⊕ K`;
- preserve the `0.X` a-priori / `1.X` empirical boundary;
- preserve prospective capture deadlines; never backfill hindsight as
  prospective.
