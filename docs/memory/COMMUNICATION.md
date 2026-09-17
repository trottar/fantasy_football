# Communication and Checkpoint Protocol

This file owns the work-session and checkpoint communication lifecycle.

Startup authority is defined in `AGENTS.md`; do not maintain a second startup
sequence here.

## Start of Work

1. Follow the `AGENTS.md` startup contract.
2. Establish the exact current authority from `CURRENT.md`.
3. Read only the referenced files and exact source/tests needed for the current
   task.
4. For a diagnostic/investigation, state the narrow question and decision
   boundary before probing.

## During Work

- Provide concise progress updates when findings materially change direction.
- For long local procedures, emit timestamped step/progress output.
- Preserve raw measurements when an interpretation is later superseded.
- Record meaningful diagnostic/tooling failures with explicit modification
  state.
- Keep private/authenticated raw evidence local unless deliberately sanitized.
- Do not promote hypotheses into curated durable facts.

## Checkpoint Transition

At a meaningful checkpoint:

1. classify what was actually validated;
2. update the relevant evidence/investigation/decision/roadmap record;
3. update the dated operational log;
4. rewrite `CURRENT.md` to the new frontier rather than appending another
   previously-current state;
5. rewrite `handoffs/CURRENT_HANDOFF.md` if a resume pointer is useful;
6. update `MEMORY.md` only for durable cross-phase knowledge;
7. apply `MAINTENANCE.md` thresholds/triggers;
8. deliver memory changes in the same ZIP/checkpoint as the work.

Repository writes follow `patches/PATCH_PROTOCOL.md`.

## End of Work

A completed handoff must distinguish:
- what is complete;
- what is source/test/runtime/operator validated;
- what remains unvalidated;
- the single exact next action;
- any blocker;
- where canonical evidence lives.

Do not leave two competing "next actions" in bootstrap documents.

## Failure Vocabulary

Use explicit states where applicable:
- `FAILED BEFORE MODIFICATION`
- `ROLLED BACK`
- `SOURCE-VALIDATED`
- `TEST-VALIDATED`
- `RUNTIME-VALIDATED`
- `OPERATOR-CONFIRMED`
- `COMMISSIONED`
- `DEFERRED`
- `SUPERSEDED`

Do not strengthen one evidence class into another.
