# Memory M4 Handoff Contract — 2026-09-21

## Classification

`M4 HANDOFF CONTRACT = CONTENT COMPLETE / NO FOOTBALL OR RUNTIME CHANGE`

M4 formalizes `CURRENT_HANDOFF.md` as a small exceptional-transfer note rather
than a second active-state summary.

## Predecessor

M3B curated-memory cleanup is durable on remote `main` at repository checkpoint
`7308e6cb44e8bbb97121a822d5b7452fff008ce9`.

That concrete SHA is historical predecessor evidence, not a self-SHA field in
active memory.

## Problem

The M0 audit identified a useful PrivyHub principle: one authoritative resumable
state plus a small transfer note. Fantasy already declared `CURRENT.md`
authoritative, but the live handoff still repeated routine project state:

- commissioned runtime and Phase 1A status;
- delivery/staging status;
- sequential M0-M3 status;
- retained Phase 1B status;
- Week 3 safety state;
- a second set of canonical pointers and resume steps.

Most of that information is already recoverable from `CURRENT.md`, roadmap
status, and canonical records. Repeating it makes the handoff drift whenever the
frontier changes and encourages it to behave like a second CURRENT.

## Adopted Contract

### Authority

`CURRENT.md` is the sole authoritative resumable project state.

`CURRENT_HANDOFF.md` is non-authoritative. If it conflicts with `CURRENT.md`,
`CURRENT.md` wins and the handoff is repaired at the next safe checkpoint.

### Allowed handoff content

The live handoff may contain only transition-specific information that a fresh
session cannot safely recover from `CURRENT.md` and its canonical references,
for example:

- a local-applied but unpublished checkpoint;
- a staged/committed but not pushed checkpoint;
- a repository checkpoint published while runtime synchronization or
  commissioning is still incomplete;
- an unusual temporary tool/access/operator condition that changes the normal
  resume path;
- one short temporary warning required to prevent an invalid transition.

### Forbidden handoff content

Do not use the live handoff for:

- a second project/phase status summary;
- routine commissioned-baseline restatement;
- roadmap or known-issues duplication;
- scientific/architectural rules already owned elsewhere;
- validation matrices or evidence detail;
- completed-checkpoint chronology;
- superseded handoff history;
- a duplicate ordinary next action when `CURRENT.md` already states it.

### Stable-state form

At a normal stable checkpoint, the handoff may simply say:

`No exceptional transfer state is recorded.`

and direct the reader to `CURRENT.md`.

This is a valid, useful handoff. The file does not need to change merely because
the ordinary active frontier changes.

### Rewrite rule

Update the handoff only when transfer-specific state changes. When an exceptional
condition resolves, remove it. Preserve historical detail in dated
memory/evidence/patch records rather than appending it below the live handoff.

## Startup Boundary

M4 does **not** change which files are mandatory at startup or their order.
The five-file eager-versus-selective startup decision remains M5.

## Template

`templates/CURRENT_HANDOFF.md` captures the contract and the normal stable-state
form. Its commented examples are guidance only, not live project state.

## Validation Contract

The M4 package must:

- authorize all existing targets against the durable M3B predecessor;
- preserve target BOM/newline representation;
- rewrite the live handoff to the stable-state form;
- keep the live handoff below 2 KiB and below 40 lines;
- reject routine project-status/chronology markers from the handoff;
- replace the handoff-policy section in `MAINTENANCE.md`;
- remove the old health-check requirement that the handoff repeat the default
  actor sequence;
- preserve the existing five-file startup contract unchanged;
- create the handoff template and this evidence record exactly;
- support idempotent rerun and rollback on post-write failure;
- pass strict memory health;
- leave `docs/memory/manifest.json` and the control-root Git index unchanged
  during local apply;
- not touch football/model/application source or the commissioned runtime.

## Next Memory Step

Once M4 is durable on remote `main`, proceed to **M5 — startup contract
decision**. M5 must make an explicit atomic choice; M4 does not pre-decide it.

Week 3 prospective capture remains a harder calendar gate than nonessential
M5-M7 progress.
