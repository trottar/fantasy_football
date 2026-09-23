# Phase 1C Player Boundary Discovery Checkpoint Failures — 2026-09-22

## Scope

This record preserves the failed/rolled-back attempts to checkpoint the
read-only player-boundary discovery after published predecessor
`c6a33d12d394e9355c82a2fef84766779ca40420`.

The discovery result itself remained valid throughout. These failures concern
checkpoint tooling/content-maintenance workflow, not football/model behavior.

## Attempt v1

Classification:

`FAILED BEFORE MODIFICATION`

Cause:

The package invalidly assumed production `src/` existed under the synchronized
control root. That contradicted the established control-root versus commissioned
runtime-tree separation.

Modification state:

No project file was modified.

## Attempt v2

Classification:

`ROLLED BACK`

Cause:

Generated memory content was produced successfully, but a brittle semantic
assertion depended on wrapped prose layout and failed despite the intended
meaning being present.

Modification state:

The package restored the control root to the exact predecessor state.

## Attempt v3

Classification:

`ROLLED BACK`

Passed before the final failure:

- semantic predecessor contract;
- exact rendered-byte identities;
- rendered-memory cleanliness;
- `CURRENT.md` health.

Final failure:

Strict memory health reported `MEMORY.md` at the soft threshold:

- 351 lines;
- status `SOFT`.

Per `MAINTENANCE.md`, the package rolled back rather than publishing another
checkpoint that would immediately require maintenance.

Modification state:

The control root was restored exactly.

## Successor Decision

Do not directly retry the discovery-memory checkpoint.

Perform durable-memory maintenance first:

- keep the player-boundary discovery as canonical evidence;
- keep this failure lineage in evidence/dated history;
- relocate chronology out of `MEMORY.md` according to information role;
- keep one active objective and one exact next action in `CURRENT.md`;
- keep `CURRENT_HANDOFF.md` limited to exceptional transfer state;
- require strict memory health before the maintenance checkpoint succeeds;
- do not change football/model/application behavior.
