# Communication and Checkpoint Protocol

This file owns the work-session and checkpoint communication lifecycle.

Startup authority is defined in `AGENTS.md`; do not maintain a competing startup
sequence here.

## Start of Work

1. Follow the complete `AGENTS.md` startup contract.
2. Establish the exact current authority from `CURRENT.md`.
3. Read `MEMORY.md`, `handoffs/CURRENT_HANDOFF.md`, and `USER.md`.
4. Read only the referenced files and exact source/tests needed for the current
   task.
5. If repository writes may occur, read `patches/PATCH_PROTOCOL.md` before
   constructing a package.
6. For a diagnostic/investigation, state the narrow question and decision
   boundary before probing.

## During Work

- Provide concise progress updates when findings materially change direction.
- For long local procedures, emit timestamped step/progress output.
- Preserve raw measurements when an interpretation is later superseded.
- Record meaningful diagnostic/tooling failures with explicit modification
  state.
- Keep private/authenticated raw evidence local unless deliberately sanitized.
- Do not promote hypotheses into curated durable facts.
- Never imply that package construction, local application, commit, push, and
  remote verification are the same checkpoint state.

## Human-in-the-loop Checkpoint Transition

The default checkpoint lifecycle is intentionally split across turns and actors:

1. assistant audits the authoritative state and prepares the update;
2. assistant validates the generated package as far as the available environment
   permits;
3. assistant delivers the self-contained ZIP / PowerShell entry point and states
   exactly what was and was not validated;
4. user runs the local PowerShell workflow;
5. user returns the complete output/log;
6. assistant checks the returned output against the expected success/failure
   gates;
7. only after that verification does the assistant provide the separate
   commit/push commands;
8. user performs commit/push;
9. assistant may perform read-only remote verification afterward.

A normal delivered `.ps1` must not commit or push. Direct GitHub connector writes
are not the project checkpoint mechanism.

At a meaningful checkpoint:

1. classify what was actually validated;
2. update the relevant evidence/investigation/decision/roadmap record;
3. update the dated operational log;
4. rewrite `CURRENT.md` to the new frontier rather than appending another
   previously-current state;
5. rewrite `handoffs/CURRENT_HANDOFF.md` when resume/operational state changed;
6. update `MEMORY.md` only for durable cross-phase knowledge;
7. apply `MAINTENANCE.md` thresholds/triggers;
8. deliver memory changes in the same checkpoint payload as the work.

Repository writes follow `patches/PATCH_PROTOCOL.md`. During local apply, the
control root's own Git `HEAD` is not predecessor-content authority; the package's
target-specific predecessor contract is. Git `HEAD`/index authority belongs to
the later isolated staging clone used for commit/push.

## End of Work

A completed handoff must distinguish:
- what is complete;
- what is source/test/runtime/operator validated;
- what remains unvalidated;
- whether the package has only been prepared, locally applied, committed, or
  pushed;
- the single exact next action;
- any blocker;
- where canonical evidence lives.

Do not leave two competing "next actions" in bootstrap documents.

## Failure Vocabulary

Use explicit states where applicable:
- `FAILED BEFORE MODIFICATION`
- `FAILED BEFORE COMMIT/PUSH`
- `ROLLED BACK`
- `SOURCE-VALIDATED`
- `TEST-VALIDATED`
- `RUNTIME-VALIDATED`
- `OPERATOR-CONFIRMED`
- `COMMISSIONED`
- `LOCAL APPLY VALIDATED / NOT COMMITTED`
- `COMMITTED / NOT PUSHED`
- `PUSHED / REMOTE VERIFIED`
- `DEFERRED`
- `SUPERSEDED`

Do not strengthen one evidence class into another.
