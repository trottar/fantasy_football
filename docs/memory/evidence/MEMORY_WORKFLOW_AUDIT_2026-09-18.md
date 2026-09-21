# Memory / Handoff Workflow Audit — 2026-09-18

## Scope

Read-only audit of:
- current durable-memory bootstrap/policy files;
- current roadmap and handoff;
- 2026-09-17 operational history;
- current GitHub reference state;
- project continuation/philosophy context supplied in the project.

No football/model/application source modification is part of this audit.

## Repository reference observed

Read-only GitHub reference during the audit:

- `main`: `f22115e7c75357e4321912831a3f99d1ea3e5c3f`
- commit: `Enable v1.0A GUI lifecycle shadow pilot`
- parent: `eb7fc236a61f50459397cf3e2f58cd1cdbb1091b`

This is a reference/history observation only. The validated local tree remains
authoritative between checkpoints.

## Findings

### A-001 — Bootstrap-set inconsistency

`AGENTS.md`, `README.md`, and `MAINTENANCE.md` described a three-file startup
(`AGENTS`, `CURRENT`, `USER`) while the project-level development workflow
requires substantial sessions to consult `CURRENT`, `MEMORY`,
`CURRENT_HANDOFF`, `USER`, and `AGENTS`.

Effect:
a fresh session could obey the repository's shorter bootstrap and never read the
handoff or curated durable memory before acting.

Classification:
`REAL CONTINUITY DEFECT`.

Correction:
make the five-file bootstrap mandatory and consistent across bootstrap/policy
documents.

### A-002 — Repository-write rule existed but actor separation was not explicit enough

The repository already contained:
- prohibition on direct GitHub connector checkpoint writes;
- ZIP/PowerShell checkpoint mechanics;
- local validation / commit / push concepts.

However, the workflow did not state strongly enough in the active handoff that
the user performs the local run and that commit/push commands are supplied only
after the user returns the complete local output.

Effect:
a fresh session could conflate package construction, local apply, and repository
synchronization.

Classification:
`OPERATIONAL HANDOFF DEFECT`.

Correction:
make the actor sequence canonical in `PATCH_PROTOCOL.md` and repeat the critical
boundary in `AGENTS.md`, `USER.md`, `TOOLS.md`, `COMMUNICATION.md`, and the
current handoff.

### A-003 — Direct connector write attempt

During the 2026-09-18 chat, a direct GitHub write path was attempted despite the
existing project rule. The write did not become a valid project checkpoint.

Classification:
`PROCEDURAL WORKFLOW VIOLATION / NO VALID PROJECT CHECKPOINT`.

Durable lesson:
correct procedure must be forced by startup/handoff structure rather than
assuming the agent will remember it.

### A-004 — Roadmap active-frontier header stale

The top of `roadmap/STATUS.md` still named `failure-bundle contract` as the exact
next slice, while later validated checkpoint records established:
- failure bundle complete;
- adapters/correlation complete;
- integration gate complete;
- CLI/service shadow complete;
- GUI lifecycle shadow complete;
- next slice = data-source season-sync shadow pilot.

Classification:
`STALE ACTIVE SUMMARY`.

Correction:
rewrite the roadmap current frontier from the newest validated checkpoint and
leave detailed chronology in dated memory/evidence.

### A-005 — Durable philosophy incompletely promoted

The project continuation/philosophy record contained durable principles not
fully promoted into `MEMORY.md`, including:
- observability as experimental measurement infrastructure;
- the MC as a microscope rather than the theory;
- constructive disagreement;
- historical non-stationarity and contextual priors;
- explicit limits of the physics analogy.

Classification:
`DURABLE KNOWLEDGE PROMOTION NEEDED`.

Correction:
promote these principles into curated durable memory without changing football
model behavior.

## Corrected checkpoint actor sequence

Default:

`assistant audit -> assistant package -> user local run -> user returns full log -> assistant verifies -> assistant supplies push commands -> user pushes -> assistant read-only verifies`

Default delivered `.ps1` behavior:
- may inspect pre-state;
- may back up;
- may apply reviewed files;
- may run local validation;
- must report exact modification state;
- must not stage, commit, or push.

Any deviation requires explicit user authorization for that checkpoint.

## Scope of this memory maintenance

Expected modified durable-memory files:
- `AGENTS.md`
- `COMMUNICATION.md`
- `CURRENT.md`
- `LEARNINGS.md`
- `MAINTENANCE.md`
- `MEMORY.md`
- `README.md`
- `TOOLS.md`
- `USER.md`
- `handoffs/CURRENT_HANDOFF.md`
- `roadmap/STATUS.md`
- `patches/PATCH_PROTOCOL.md`
- this audit record
- `memory/2026-09-18.md`
- `tools/check_memory_health.py` (observational memory-health tool only)

The health tool must be updated because its old self-test and bootstrap-order
check hard-coded the superseded three-file startup contract.

Expected football/model/application source changes:
`NONE`.

Expected runtime-tree changes:
`NONE`.

Expected commit/push during local apply:
`NONE`.

## Post-audit delivery correction — 2026-09-20

The v2 reconciliation launcher subsequently failed safely before modification.
That incident is not evidence against the memory conclusions above; it exposed a
launcher/pre-state defect. Canonical evidence and successor rule:
`MEMORY_HANDOFF_RECONCILIATION_V2_FAILURE_2026-09-20.md`.

## Post-audit delivery correction v3 — 2026-09-20

The v3 reconciliation launcher also failed safely before modification. It
corrected the remote/local-HEAD defect from v2 but used raw porcelain status as
the scoped cleanliness authority. On the Windows control checkout this reported
the tracked memory tree as modified because of worktree representation rather
than substantive content drift.

Canonical evidence and successor rule:
`MEMORY_HANDOFF_RECONCILIATION_V3_FAILURE_2026-09-20.md`.

## Post-audit delivery correction v5 / final authority diagnosis — 2026-09-20

v4 and v5 both failed safely before modification with the same whole-memory-tree
drift pattern. The repeated pattern disproved the assumption that the control
root's own local Git `HEAD`/index was the correct predecessor authority.

The established workflow commits/pushes from an isolated staging clone and then
synchronizes validated files back to the control/runtime surfaces. Therefore the
control root can legitimately contain the latest synchronized checkpoint while
its local Git metadata refers to an older state.

v5 still compared cleaned worktree blobs against that stale local `HEAD`, so it
preserved the same conceptual defect as v3/v4.

Corrected rule: local apply validates only overwrite targets against the known
predecessor checkpoint blob identities packaged with the update. Git
`HEAD`/index authority resumes in the isolated staging clone used for the later
commit/push stage.

Canonical evidence:
`MEMORY_HANDOFF_RECONCILIATION_ROOT_CAUSE_2026-09-20.md`.
