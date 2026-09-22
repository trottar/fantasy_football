# Durable Project Memory

`docs/memory/` is the repository-backed continuity layer for the fantasy-football
project. Development must not depend on chat history alone.

## Startup Contract

M5 retains a fixed five-file core for every fresh substantial work session:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Read that core in full. Then expand selectively from `CURRENT.md`'s exact next
action/references and the task itself; do not eagerly load the wider hierarchy.

`AGENTS.md` owns the operational startup contract. `MAINTENANCE.md` owns its
health/coherence rules. `CURRENT.md` is authoritative active state. `MEMORY.md`
supplies curated durable cross-phase knowledge. `CURRENT_HANDOFF.md` carries only
exceptional transfer state and cannot override `CURRENT.md`.

## Authority

When sources conflict, prefer exact current source/fresh direct evidence, exact
validation/commissioning provenance, `CURRENT.md`, canonical deeper records,
Git/checkpoint history, then older summaries/history.

The validated local tree is authoritative between checkpoints. GitHub is the
durable source/history layer and should match validated checkpoints.

## Core File Ownership

- `AGENTS.md` — startup, authority, scientific/authorization guardrails.
- `CURRENT.md` — sole authoritative active frontier and next action.
- `USER.md` — collaboration/environment preferences.
- `MEMORY.md` — curated durable cross-phase knowledge.
- `LEARNINGS.md` — reusable engineering/scientific lessons.
- `COMMUNICATION.md` — work-session/checkpoint communication lifecycle.
- `TOOLS.md` — environment/tool commands and proven operational facts.
- `MAINTENANCE.md` — memory-health, cleanup, threshold, and rewrite policy.
- `patches/PATCH_PROTOCOL.md` — canonical repository checkpoint mechanics.
- `handoffs/CURRENT_HANDOFF.md` — compact resume/transition metadata.

Detailed procedure should have one canonical owner. Other files point to it
rather than reproducing it, except for brief safety boundaries needed to prevent
an invalid transition.

## Planning Documents Outside `docs/memory/`

- `../ROADMAP.md` — accepted long-range phases and phase acceptance gates.
- `../KNOWN_ISSUES.md` — open/deferred issues, blockers, debt, and reopen/resolve
  conditions.

These do not override `CURRENT.md`. `roadmap/STATUS.md` is the compact current
roadmap position; `roadmap/SEASON_2026.md` owns weekly calendar gates.

## Typed Subdirectories

- `architecture/` — stable scientific/software contracts.
- `decisions/` — accepted/deferred/superseded decisions.
- `investigations/` — bounded questions, probes, classifications.
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

Canonical owners:

- repository checkpoint mechanics: `patches/PATCH_PROTOCOL.md`;
- communication/evidence-return lifecycle: `COMMUNICATION.md`;
- environment/tool commands: `TOOLS.md`;
- memory health/cleanup: `MAINTENANCE.md`.

Normal package transport uses deterministic text `.ffpkg` infrastructure under
`tools/delivery/`. Direct GitHub connector writes are not project checkpoint
writes. Raw/private evidence stays local unless deliberately sanitized.

Active documents point to canonical evidence instead of copying complete
validation histories.
