# Communication and Checkpoint Protocol

This file owns the **communication lifecycle** for work sessions and checkpoints.

It does not own startup policy (`AGENTS.md`), repository execution mechanics
(`patches/PATCH_PROTOCOL.md`), environment/tool commands (`TOOLS.md`), or memory
maintenance rules (`MAINTENANCE.md`).

## Start of Work

1. Follow the startup contract currently defined by `AGENTS.md`.
2. Establish the active frontier from `CURRENT.md`.
3. Load only the task-relevant canonical records/source/tests required by that
   frontier.
4. If repository writes may occur, read `patches/PATCH_PROTOCOL.md` before
   constructing a package.
5. For a diagnostic/investigation, state the narrow question and decision
   boundary before probing.

## During Work

- Provide concise progress updates only when findings materially change direction.
- Preserve raw measurements when later interpretation changes.
- Record meaningful diagnostic/tooling failures with explicit modification state.
- Keep private/authenticated raw evidence local unless deliberately sanitized.
- Do not promote hypotheses into curated durable facts.
- Keep package construction, local apply, staging, commit, push, remote
  verification, runtime synchronization, and commissioning as distinct states.
- Do not repeat detailed repository mechanics here; use
  `patches/PATCH_PROTOCOL.md`.

## Checkpoint Communication Contract

For a repository checkpoint, communicate:

- package/checkpoint identity and narrow purpose;
- exact changed/unchanged scope;
- validation actually performed;
- explicit state boundary (for example `LOCAL-APPLIED / VALIDATED`);
- one complete local invocation;
- the concise success block to return;
- the full failure output to return when any gate fails.

Normal delivery uses the repository-owned deterministic text `.ffpkg` runner.
The detailed build/apply/stage/commit/push mechanics remain canonical in
`patches/PATCH_PROTOCOL.md` and `tools/delivery/`.

On success, request the concise final summary block rather than the complete
console transcript. Request full logs only when a step fails, a summary omits
evidence needed for classification, or a specific diagnostic line must be
inspected.

## Meaningful Checkpoint Memory Update

At a meaningful checkpoint:

1. classify what was actually validated;
2. update the relevant evidence/investigation/decision/roadmap record;
3. update dated operational history when chronology matters;
4. rewrite `CURRENT.md` to the new frontier rather than appending old states;
5. rewrite `CURRENT_HANDOFF.md` when transition state changes;
6. update `MEMORY.md` only for durable cross-phase knowledge;
7. apply `MAINTENANCE.md` role/health rules.

## End of Work

A completed handoff/summary must distinguish:

- what is complete;
- what is source/test/runtime/operator validated;
- what remains unvalidated;
- package/local/staged/committed/pushed/runtime state;
- the single exact next action;
- any blocker;
- where canonical evidence lives.

Do not leave competing next actions in active bootstrap documents.

## Failure / Evidence Vocabulary

Use explicit states where applicable:

- `FAILED BEFORE MODIFICATION`
- `FAILED BEFORE COMMIT/PUSH`
- `ROLLED BACK`
- `SOURCE-VALIDATED`
- `TEST-VALIDATED`
- `RUNTIME-VALIDATED`
- `OPERATOR-CONFIRMED`
- `COMMISSIONED`
- `LOCAL-APPLIED / VALIDATED`
- `STAGED / NOT COMMITTED`
- `COMMITTED / NOT PUSHED`
- `PUSHED / REMOTE VERIFIED`
- `DEFERRED`
- `SUPERSEDED`

Do not strengthen one evidence class into another.
