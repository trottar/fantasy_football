# Durable Project Memory

`docs/memory/` is the repository-backed continuity layer for the fantasy-football
project. Development must not depend on chat history alone.

## Mandatory Startup Contract

A fresh substantial work session must read:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Then read the task-relevant references named by those files or required by the
affected subsystem.

`CURRENT.md` is authoritative active state. `MEMORY.md` supplies durable
cross-phase scientific/project knowledge. `CURRENT_HANDOFF.md` is a compact
resume and operational-warning surface; it cannot override `CURRENT.md`.

Do not shorten this startup set from memory.

## Authority

When sources conflict, prefer:
1. exact current source plus fresh direct evidence;
2. successful exact validation/commissioning/provenance records;
3. `CURRENT.md`;
4. canonical architecture/decision/investigation/evidence records;
5. Git/checkpoint history;
6. older summaries/history.

Newer validated state supersedes older active summaries unless the user
explicitly says otherwise. Never silently merge contradictions.

The validated local tree is authoritative between checkpoints. GitHub is the
durable source/history layer and should match validated checkpoints.

## Core File Ownership

- `AGENTS.md` — startup contract, authority, scientific/authorization guardrails.
- `CURRENT.md` — sole authoritative active project frontier and next action.
- `USER.md` — collaboration/environment preferences.
- `MEMORY.md` — curated durable cross-phase scientific/project knowledge.
- `LEARNINGS.md` — reusable engineering/scientific lessons.
- `COMMUNICATION.md` — work-session/checkpoint communication lifecycle.
- `TOOLS.md` — environment/tooling and proven operational procedures.
- `MAINTENANCE.md` — memory-health, cleanup, threshold, and rewrite policy.
- `patches/PATCH_PROTOCOL.md` — canonical repository checkpoint mechanics.
- `handoffs/CURRENT_HANDOFF.md` — compact resume pointer and critical
  handoff/actor boundary.

## Planning Documents Outside `docs/memory/`

- `../ROADMAP.md` — accepted long-range project phases and phase acceptance gates.
- `../KNOWN_ISSUES.md` — open/deferred issues, blockers, debt, and explicit reopen
  conditions.

These planning documents do not override `CURRENT.md`. `roadmap/STATUS.md`
remains the compact current phase position, while `roadmap/SEASON_2026.md`
owns the 2026 week-by-week calendar gates.

## Typed Subdirectories

- `architecture/` — stable scientific/software contracts.
- `decisions/` — accepted/deferred/superseded decisions.
- `investigations/` — bounded questions, probes, evidence, classifications.
- `evidence/` — measured/validated results and commissioning receipts.
- `roadmap/` — implementation status and planned phases.
- `repository/` — code maps/audits/technical debt.
- `patches/` — checkpoint/release procedures and records.
- `handoffs/` — compact resumable transition state.
- `memory/` — detailed dated operational chronology.
- `history/` — explicitly superseded snapshots; never current authority.
- `templates/` — repeatable update formats.

## Checkpoint Contract

Meaningful code/release/diagnostic checkpoints update durable memory in the same
Git checkpoint.

The default human-in-the-loop repository flow is:

`assistant package -> user local run -> returned log -> assistant verification -> separate push commands -> user push -> read-only remote verification`

Direct GitHub connector writes are not used for project checkpoint writes.

Raw/private evidence stays local unless deliberately sanitized.

Active documents point to canonical evidence rather than copying complete
validation histories.

Memory health and cleanup rules are defined in `MAINTENANCE.md`. Checkpoint
surface/authority mechanics are defined in `patches/PATCH_PROTOCOL.md`; do not
infer local-apply predecessor authority from the synchronized control root's own
Git `HEAD`.
