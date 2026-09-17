# Durable Project Memory

This directory is the repository-backed continuity layer for the fantasy-football project. Development must not depend on chat history alone.

## Authority order

When sources disagree, use this order:

1. Current repository source plus fresh measured runtime evidence.
2. Successful commissioning evidence and exact release/provenance records.
3. `CURRENT.md`, `MEMORY.md`, and the current handoff.
4. Architecture, decisions, investigations, and evidence in this directory.
5. Git history and release history.
6. Older chat summaries and historical snapshots.

Never silently merge contradictions. Mark superseded states explicitly.

## Core files

- `CURRENT.md` — immediate project state and next actions.
- `MEMORY.md` — compact durable facts and decisions.
- `AGENTS.md` — operating rules for future development agents/chats.
- `USER.md` — collaboration and environment preferences.
- `TOOLS.md` — proven commands, evidence entry points, and environment constraints.
- `LEARNINGS.md` — durable engineering/scientific lessons.
- `COMMUNICATION.md` — startup, handoff, and memory-update protocol.

## Indexed subdirectories

- `architecture/` — scientific and software architecture contracts.
- `decisions/` — durable design decisions and status.
- `investigations/` — active and resolved investigations.
- `evidence/` — commissioning, calibration, and weekly observed evidence.
- `roadmap/` — implementation status and planned releases.
- `repository/` — code maps, audits, and technical debt.
- `patches/` — patch/release protocol and release index.
- `handoffs/` — concise current handoff.
- `memory/` — dated operational memory logs.
- `history/` — explicitly superseded snapshots.
- `templates/` — repeatable evidence and decision templates.

## Memory contract

Every meaningful release or patch must update durable memory in the same Git checkpoint. Raw/private evidence stays local unless deliberately sanitized. Durable conclusions, architecture, and reproducible evidence summaries belong here.

Raw observed NFL/ESPN data is immutable evidence. Derived/calibrated state must be stored separately from raw observations.

```yaml
memory_schema: 1
as_of: 2026-09-16
baseline_release: 0.35-fixed1
baseline_commit: c85434a6be7852310c47fc8d1847c61a0a023209
next_data_informed_major_version: 1.X
```
