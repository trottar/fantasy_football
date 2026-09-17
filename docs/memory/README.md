# Durable Project Memory

`docs/memory/` is the repository-backed continuity layer for the fantasy-football
project. Development must not depend on chat history alone.

## Minimal Startup Contract

A fresh substantial work session should read:

1. `AGENTS.md`
2. `CURRENT.md`
3. `USER.md`

Then read only task-relevant references named by `CURRENT.md` or required by the
affected subsystem.

`MEMORY.md` is durable cross-phase knowledge, not mandatory cover-to-cover
startup material. `handoffs/CURRENT_HANDOFF.md` is a small resume aid and cannot
override `CURRENT.md`.

## Authority

When sources conflict, prefer:
1. exact current source plus fresh direct evidence;
2. successful exact validation/commissioning/provenance records;
3. `CURRENT.md`;
4. canonical architecture/decision/investigation/evidence records;
5. Git/checkpoint history;
6. older summaries/history.

Never silently merge contradictions.

## Core File Ownership

- `AGENTS.md` — startup contract, authority, scientific/authorization guardrails.
- `CURRENT.md` — sole authoritative active project frontier and next action.
- `USER.md` — collaboration/environment preferences.
- `MEMORY.md` — curated durable cross-phase scientific/project knowledge.
- `LEARNINGS.md` — reusable engineering/scientific lessons.
- `COMMUNICATION.md` — work-session/checkpoint communication lifecycle.
- `TOOLS.md` — environment/tooling and proven operational procedures.
- `MAINTENANCE.md` — memory-health, cleanup, threshold, and rewrite policy.

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

## Memory Contract

Meaningful code/release/diagnostic checkpoints update durable memory in the same
Git checkpoint.

Raw/private evidence stays local unless deliberately sanitized.

Active documents point to canonical evidence rather than copying complete
validation histories.

Memory health and cleanup rules are defined in `MAINTENANCE.md`.
