# Agent Operating Rules

## Mandatory startup contract

For every substantial work session, read this bootstrap set before planning or
acting:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Then read the task-relevant architecture, decision, investigation, evidence,
roadmap, patch/procedure, source, and test files referenced by that bootstrap
set.

`CURRENT.md` is the sole authoritative active-state document. `MEMORY.md`
contains durable cross-phase knowledge. `CURRENT_HANDOFF.md` is a compact resume
pointer and operational warning surface; it cannot override `CURRENT.md`.
Historical files and dated logs explain lineage but do not override newer
validated state.

Do not reduce this startup set to a shorter remembered subset. A fresh chat must
actually inspect these files rather than relying on chat summaries.

## Authority and evidence

When sources disagree, prefer:

1. exact current source plus fresh direct evidence;
2. successful exact validation/commissioning receipts and provenance;
3. `CURRENT.md`;
4. canonical architecture/decision/investigation/evidence records;
5. Git/checkpoint history;
6. older summaries and historical snapshots.

Within durable memory, newer validated checkpoint state supersedes older active
summaries unless the user explicitly says otherwise.

Raw measurements outrank derived classifiers when they conflict. Never claim
inspection, testing, validation, runtime acceptance, commissioning, commit, or
push that did not actually occur.

Before restating what a decision, gate, classification, deadline, or architectural
constraint says, open the canonical record that defines it. Do not propagate a
summary of a summary when the source record is available.

During the NFL season, distinguish **calendar gates** from **evidence gates**.
A prospective capture deadline is irreversible and must not be backfilled after
relevant outcomes are known. An evidence gate passes only when the accumulated
prospective evidence supports it; reaching a date never authorizes calibration
by itself. When these compete, preserve the causally valid capture first and
defer nonessential development.

The validated local state under `L:\Projects\fantasy_football\` is authoritative
between checkpoints. GitHub `trottar/fantasy_football` is the durable
source/history layer and should match validated checkpoints. Read-only GitHub
inspection may audit history/reference state, but it does not replace local
validation.

The control root is a synchronized working surface. Its local Git `HEAD`/index
may lag files synchronized from an isolated staging clone after a prior push.
For local package apply, use the target-specific predecessor contract, not the
control root's whole-tree Git status or local `HEAD`. For commit/push, use the
isolated staging clone's Git state as authority.

## Development method

Use the evidence-led loop:

`authority -> narrow question -> targeted probe -> raw evidence -> classification -> one coherent patch/defer/close`

Do not reopen resolved/deferred work without new evidence. Preserve unrelated
validated subsystems.

Detailed method:
`architecture/PROBLEM_SOLVING_METHOD.md`

## Scientific constraints

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from football physics.
- Use decision-time information only for prospective actions.
- Preserve frozen prospective state; no hindsight authorization.
- Treat uncertainty as first-class output.
- `screen != authority`.
- `0.X` remains a-priori; observed 2026 outcomes may inform only `1.X`.
- Diagnostics/observability must remain non-interfering.
- Observability is experimental measurement infrastructure, not merely logging.

## Authorization boundary

Standing authorization covers:
- `docs/memory/**`;
- observational diagnostic/probe/audit/logging/observability/replay/failure
  tooling.

Explicit user authorization is required for football/model/application/business
logic changes. If a change mixes diagnostics with production behavior and cannot
be cleanly separated, treat it as production.

## Repository checkpoint boundary

Repository checkpoint writes use the human-in-the-loop ZIP/PowerShell workflow
defined in `patches/PATCH_PROTOCOL.md`.

Default actor sequence:

1. assistant audits current state read-only;
2. assistant builds and validates a self-contained update package and `.ps1`;
3. user runs the `.ps1` locally;
4. user returns the complete local output;
5. assistant verifies the returned evidence;
6. assistant supplies separate commit/push commands;
7. user performs the push;
8. assistant may then verify the remote state read-only.

Do not use direct GitHub connector writes for this project. Do not commit or push
from a delivered installer unless the user explicitly overrides this rule for
that specific checkpoint.

If repository-write behavior is relevant to the task, `patches/PATCH_PROTOCOL.md`
is mandatory reading before constructing or proposing the checkpoint.

## Policy ownership

- Memory maintenance: `MAINTENANCE.md`
- Work-session/checkpoint communication: `COMMUNICATION.md`
- Environment/tooling procedures: `TOOLS.md`
- Patch/release mechanics: `patches/PATCH_PROTOCOL.md`
- Reusable lessons: `LEARNINGS.md`
- User/environment preferences: `USER.md`

Do not duplicate detailed policy unnecessarily; bootstrap and handoff files may
repeat only the critical safety/actor boundary needed to prevent an invalid
checkpoint transition.
