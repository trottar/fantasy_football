# Agent Operating Rules

## Startup contract — M5 retained five-file core

For every substantial work session, read this stable core **in full** before
planning or acting:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

M5 explicitly retains this five-file core. It is not an instruction to eagerly
load the wider memory hierarchy.

After the core is read:

1. use `CURRENT.md`'s exact next action and references as the primary retrieval
   frontier;
2. open the canonical record before restating a decision, gate, classification,
   deadline, or architectural constraint;
3. load only task-relevant architecture, decision, investigation, evidence,
   roadmap, patch/procedure, source, and test files;
4. consult dated history and other deep memory only when the active task requires
   it.

`CURRENT.md` is the sole authoritative active-state document. `MEMORY.md`
contains curated durable cross-phase knowledge. `CURRENT_HANDOFF.md` contains
exceptional transfer state only and cannot override `CURRENT.md`. `USER.md` owns
collaboration/environment preferences. Historical files and dated logs explain
lineage but do not override newer validated state.

A fresh chat must actually inspect all five core files rather than relying on
chat summaries or a remembered subset.

This section in `AGENTS.md` is the operational owner of the startup contract.
`MAINTENANCE.md` owns its health/coherence rules and `README.md` summarizes it.

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

For deterministic checkpoint artifacts, derive expected literals, semantic
markers, paths, hashes, object identities, and assertions from exact
source/package/result representations whenever they are inspectable. Do not guess
an inspectable deterministic value. Validate the final rendered/extracted
artifact before delivery; the operator must not be the first validator of
deterministic generated content.

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

## Checkpoint identity semantics

When exact identity of the current committed checkpoint is required, resolve it
from the Git commit/ref that contains the memory files. `CURRENT.md` and
`CURRENT_HANDOFF.md` must not be required to name their own not-yet-created
commit.

Concrete SHAs in active memory are valid only when their role is explicit, such
as a predecessor, commissioned source checkpoint, or historical evidence
checkpoint. They are not an implicit "latest state" field.

Local package state, isolated staged state, committed state, and remote-verified
state remain distinct. The canonical memory policy is `MAINTENANCE.md`; repository
publication mechanics are in `patches/PATCH_PROTOCOL.md`.

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

Repository checkpoint writes use the reusable human-in-the-loop `.ffpkg`
delivery workflow defined in `patches/PATCH_PROTOCOL.md`.

Default actor sequence:

1. assistant audits current state read-only;
2. assistant builds and validates a deterministic text `.ffpkg` carrier with the
   generic delivery infrastructure;
3. user runs the carrier through `tools\delivery\run_package.cmd` locally;
4. user returns the concise success summary, or the full log on failure;
5. assistant verifies the returned evidence;
6. assistant provides the declarative isolated-staging step/spec and the user
   runs it;
7. assistant verifies the exact staged tree/manifest;
8. assistant delivers a separate deterministic publication `.ffpkg` that invokes
   a generic/proven publisher under exact base/tree/allowlist guards;
9. user runs that publication carrier, which is the explicit authorization for
   commit/push at that already-validated stage;
10. assistant verifies the remote state read-only.

Transport, integrity, extraction, subprocess execution, and exit propagation are
owned by `tools/delivery/`. Package-specific predecessor checks, rollback,
idempotence, and domain validation remain inside each package entrypoint. Do not
create phase-specific launch wrappers when the generic runner can execute the
package contract.

Do not use direct GitHub connector writes for this project. Local-apply packages
stop before staging/commit/push. A distinct publication package may commit/push
only after the isolated stage has been separately validated and only when the
user runs that publication package. Do not replace such a multi-step publication
operation with a wall of interactive PowerShell when a package/proven generic
publisher can carry the same guards.

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
