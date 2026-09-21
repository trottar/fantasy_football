# Durable Memory Maintenance Policy

This file is the authoritative policy for keeping `docs/memory/` small, typed,
authoritative, and sustainable.

It is project-state maintenance. It is model-agnostic and platform-agnostic and
does not depend on any chat/model runtime.

## Central Invariant

A fresh contributor/session should be able to determine the current project
state, the critical operational boundaries, and the next narrow task after
reading a small stable bootstrap set.

Historical chronology, evidence, investigations, release receipts, and
superseded states remain available but are not required to determine what is
current.

## Bootstrap Set

Read first, in full:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Then load task-relevant referenced material and exact source/tests.

`CURRENT.md` is authoritative active state.

`MEMORY.md` is curated durable cross-phase knowledge.

`handoffs/CURRENT_HANDOFF.md` is compact resume/operational metadata and cannot
override `CURRENT.md`.

For any repository-write/package task, `patches/PATCH_PROTOCOL.md` becomes
mandatory reading before action.

## Information Roles

### Active Project State — `CURRENT.md`

Answers only:
- what is active;
- current validated baseline;
- current implementation/validation state;
- blockers;
- one exact next action;
- success criterion;
- what not to reopen;
- pointers to deeper records.

It is not a development diary.

### Durable Cross-Phase Knowledge

Primary homes:
- `MEMORY.md`
- `LEARNINGS.md`
- `architecture/`
- `decisions/`

Keep scientific invariants, stable architecture, enduring workflow rules, and
reusable lessons. Do not keep detailed checkpoint chronology here.

### Long-Range Roadmap / Known Issues

- `../ROADMAP.md` owns accepted long-range phases, dependencies, and phase
  acceptance gates.
- `../KNOWN_ISSUES.md` owns open/deferred issues, debt, blocker classification,
  and explicit reopen/resolve conditions.
- `roadmap/STATUS.md` owns only the current roadmap position.
- `roadmap/SEASON_2026.md` owns 2026 week-by-week calendar gates and planned
  evidence-review points.

These documents may point to active state, but none overrides `CURRENT.md`.

### Collaboration / Environment

`USER.md` owns collaboration and environment preferences.

### Operating Procedures

- `AGENTS.md` — startup, authority, scientific/authorization guardrails
- `COMMUNICATION.md` — work-session/checkpoint communication lifecycle
- `TOOLS.md` — environment/tooling procedures
- `patches/PATCH_PROTOCOL.md` — patch/release/checkpoint mechanics
- `MAINTENANCE.md` — memory health and cleanup

One document owns each detailed policy; other files should link to it. Critical
checkpoint actor boundaries may be repeated briefly in bootstrap/handoff files
when needed to prevent an invalid transition.

### Dated Operational History

`memory/YYYY-MM-DD.md` owns detailed chronological progress, temporary
classifications, tooling failures, and superseded checkpoint states.

### Investigations

`investigations/` owns bounded questions, hypotheses, probes, raw evidence,
classification, limitations, decision, next action, and status.

Once resolved, `CURRENT.md` retains only the conclusion if still relevant and a
pointer.

### Evidence

`evidence/` owns measured/tested/runtime/commissioning results and provenance.

Active state points to evidence instead of reproducing full validation matrices.

### Patch / Release Records

`patches/` and evidence own package contents, validation matrices, installation
receipts, lineage, and packaging defects.

### Superseded History

`history/` stores records worth retaining that are explicitly no longer current
authority. Nothing in `history/` overrides current state.

## Size Triggers

Thresholds are guidance plus semantic checks; size alone does not define health.

### `CURRENT.md`

- soft: 8 KiB or 175 lines
- hard: 16 KiB or 300 lines
- desired steady state: 3–8 KiB

Soft violation: perform maintenance at the next safe checkpoint before another
substantial work item.

Hard violation: maintenance becomes the next project-maintenance task once the
repository is in a safe checkpoint state.

### `handoffs/CURRENT_HANDOFF.md`

- soft: 6 KiB or 125 lines
- hard: 10 KiB or 200 lines
- desired steady state: 2–5 KiB maximum; smaller is preferred

### `MEMORY.md`

- soft: 30 KiB or 350 lines
- hard: 50 KiB or 550 lines

Do not mechanically shorten valid durable scientific knowledge merely to meet a
number. Relocate material according to role.

## Semantic Maintenance Triggers

Maintenance is required when any of these is true:
- `CURRENT.md` has more than one authoritative objective;
- multiple sections describe different next actions;
- resolved investigations remain active;
- completed checkpoints accumulate sequentially in `CURRENT.md`;
- completed checkpoints accumulate sequentially in the current handoff;
- old release states sit beside newer authoritative release states;
- failed diagnostics remain beside resolved successors without historical
  separation;
- the same checkpoint result is substantially repeated across bootstrap files;
- chronology must be reconciled to determine current state;
- historical logs are required to discover the next action;
- a major phase changes;
- a release becomes commissioned;
- an investigation becomes resolved;
- a new authoritative baseline supersedes an old one;
- procedural rules are copied inconsistently across bootstrap files;
- bootstrap documents disagree about which files must be read;
- the handoff does not make repository actor boundaries unambiguous.

Also review procedural duplication when substantially identical detailed
instructions appear in three or more policy files. Brief safety reminders may
repeat; one canonical owner must still exist.

## Safe-Checkpoint Rule

Do not interrupt an unsafe repository state merely for documentation cleanup.

Wait briefly if:
- an installer is mid-operation;
- release validation is incomplete;
- staging is incomplete;
- temporary diagnostic state still needs cleanup;
- evidence exists but has not been classified;
- a local checkpoint has not completed remote verification.

Once the state is stable, perform required maintenance before opening another
major task.

## Required Procedure

### 1. Establish Authority

Determine:
- current baseline;
- current phase;
- active work item;
- validation/commissioning state;
- blockers;
- exact next action;
- package/apply/commit/push state where relevant.

Do not infer current state by selecting the last paragraph of a large file.

### 2. Identify Superseded States

Find previously-current `PENDING`, `RESOLVED`, `READY`, `COMMISSIONED`, or
similar sequential states in active files.

### 3. Protect Raw Evidence

Never destroy a valid measurement because its interpretation changed.

Preserve original measurement, historical classification where useful, reason
for supersession, and successor classification in evidence/investigation/dated
history.

### 4. Preserve Failure Lineage

Keep diagnostic/tooling/workflow failures, but after classification and
promotion of any reusable lesson, move detailed chronology out of active
bootstrap files.

### 5. Promote Durable Lessons

Reusable rules belong in `LEARNINGS.md`, `TOOLS.md`, architecture, or patch
protocols.

### 6. Move Completed Chronology

Use dated memory, investigations, evidence, patches, and history.

### 7. Confirm Canonical Evidence

Before shortening active detail, verify a canonical deeper record exists.
Create one if necessary.

### 8. Rewrite Active State

Rewrite `CURRENT.md` coherently from today's frontier. Do not merely trim old
sections.

### 9. Reconcile Bootstrap and Handoff

Verify that `AGENTS.md`, `CURRENT.md`, `MEMORY.md`,
`handoffs/CURRENT_HANDOFF.md`, and `USER.md` agree on authority and that a fresh
session can recover the checkpoint workflow without chat history.

## Handoff Policy

Preferred model:

- `CURRENT.md` = complete authoritative resumable project state.
- `CURRENT_HANDOFF.md` = compact transition metadata plus critical actor/safety
  boundaries.

A handoff may contain:
- last completed checkpoint;
- temporary local-vs-remote condition;
- unusual uncommitted state;
- exact resume instruction;
- checkpoint package/apply/commit/push state;
- the mandatory actor sequence when needed for continuity.

Rewrite it at meaningful checkpoints. Do not append indefinitely.

## Prevent Recursive Summarization

Do not preserve knowledge only through summaries of summaries.

Before restating a decision, gate, classification, deadline, or architecture
constraint, open the canonical source record that defines it. Active summaries
should point to source records rather than becoming a new source.

Prefer:

`canonical evidence/investigation <- concise CURRENT pointer`

Before deleting active detail:
1. locate the canonical record;
2. confirm it contains necessary qualifiers/provenance;
3. create it if absent;
4. link to it;
5. then shorten active state.

## Preserve Epistemic Strength

Keep distinctions such as:
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
- `FAILED BEFORE MODIFICATION`
- `FAILED BEFORE COMMIT/PUSH`

Do not convert operator-confirmed evidence into automated evidence or vice versa.
Do not convert package/local-apply state into commit/push state.

## Health Tool

`tools/check_memory_health.py` is observational.

It reports:
- byte/line thresholds;
- duplicate headings;
- active-objective and exact-next-action counts;
- checkpoint-marker accumulation in active files;
- bootstrap total.

It never rewrites memory.

## Checkpoint Integration

Memory maintenance uses the normal repository checkpoint process. Local apply
validates package targets against the package predecessor contract; the
synchronized control root's local Git `HEAD` is not the apply authority.


1. inspect exact pre-state;
2. preserve superseded material;
3. validate generated Markdown;
4. run `git diff --check`;
5. user applies the delivered update locally;
6. user returns the complete validation output;
7. assistant verifies that evidence;
8. only then supply separate staging/manifest/commit/push commands;
9. stage an exact allowlist;
10. maintain schema-2 Git-blob manifest semantics;
11. verify remote state after the user pushes;
12. preserve public/private boundaries.

Direct GitHub connector writes do not satisfy this process.

## Memory Health Check

### Current State

- [ ] `CURRENT.md` has exactly one active objective.
- [ ] `CURRENT.md` has exactly one authoritative next action.
- [ ] Current baseline/release is not contradicted later in the file.
- [ ] Resolved investigations are absent from active chronology.
- [ ] Superseded states are historical.

### Evidence

- [ ] Important measurements have canonical evidence records.
- [ ] Raw evidence has not been destroyed.
- [ ] Active memory points to evidence instead of reproducing it.
- [ ] Evidence classifications preserve epistemic strength.

### Durable Memory

- [ ] `MEMORY.md` contains cross-phase knowledge, not session history.
- [ ] Reusable rules live in `LEARNINGS.md`/`TOOLS.md`.
- [ ] Stable contracts live in architecture/decisions.

### Handoff

- [ ] Handoff purpose is distinct from `CURRENT.md`.
- [ ] Handoff is rewritten, not append-only.
- [ ] Handoff cannot override `CURRENT.md`.
- [ ] Handoff makes package/apply/commit/push state explicit.
- [ ] Handoff makes the default actor sequence explicit.

### Procedures

- [ ] `AGENTS.md`, `COMMUNICATION.md`, `TOOLS.md`, and `MAINTENANCE.md`
  have distinct responsibilities.
- [ ] Detailed policies have one canonical owner.
- [ ] Startup instructions agree.
- [ ] `PATCH_PROTOCOL.md` is read before repository-write/package work.

### Bootstrap

- [ ] A fresh session can understand current work from the complete mandatory
  bootstrap set.
- [ ] Historical logs are not needed during normal startup.
- [ ] Evidence is loaded only when relevant.
- [ ] Bootstrap files remain below thresholds.

### Integrity

- [ ] No unique scientific knowledge was lost.
- [ ] No football/model/application behavior changed during maintenance.
- [ ] Public/private boundaries remain intact.
- [ ] No package/local state is mislabeled as pushed/remote state.
- [ ] Calendar gates are not represented as evidence/calibration authorization.
- [ ] Missed prospective captures are recorded as missing rather than backfilled.
- [ ] Root roadmap, known-issues state, roadmap status, and season calendar do not
  contradict `CURRENT.md`.

<!-- FANTASY_MEMORY_MAINTENANCE_20260918_V3 -->
