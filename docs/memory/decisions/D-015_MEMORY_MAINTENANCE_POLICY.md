# D-015 — Durable Memory Maintenance Policy

**Status:** ACTIVE

## Decision

Adopt `docs/memory/MAINTENANCE.md` as the canonical memory-health policy.

For substantial work, use the complete bootstrap set:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Then load only task-relevant source, architecture, decisions, investigations,
evidence, roadmap, procedures, and tests.

`CURRENT.md` is the sole authoritative active frontier.

`MEMORY.md` contains curated durable cross-phase knowledge rather than
chronology.

`CURRENT_HANDOFF.md` is a compact resume/operational-warning surface and cannot
override current state.

Before restating a decision, gate, classification, deadline, or stable
constraint, read the canonical record that defines it rather than propagating a
summary of a summary.

Completed chronology belongs in dated memory, evidence, investigations, patches,
or history.

Apply semantic and size-based maintenance triggers. At a safe checkpoint,
rewrite active state rather than indefinitely appending checkpoint sections.

The observational `tools/check_memory_health.py` reports health but never
rewrites memory automatically.

## Reconciliation note

This wording supersedes the earlier D-015 three-file startup list
(`AGENTS.md -> CURRENT.md -> USER.md`), which was rendered obsolete by the
2026-09-18 memory/handoff reconciliation.

No football/model/application behavior changes are authorized by this decision.
