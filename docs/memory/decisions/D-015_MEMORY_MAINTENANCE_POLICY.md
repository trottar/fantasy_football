# D-015 — Durable Memory Maintenance Policy

**Status:** ACTIVE

## Decision

Adopt `docs/memory/MAINTENANCE.md` as the canonical memory-health policy.

Use the minimal startup set:

1. `AGENTS.md`
2. `CURRENT.md`
3. `USER.md`

`CURRENT.md` is the sole authoritative active frontier.

`CURRENT_HANDOFF.md` is a compact resume aid and cannot override current state.

Completed chronology belongs in dated memory, evidence, investigations, patches,
or history. `MEMORY.md` remains curated cross-phase knowledge.

Apply both semantic and size-based maintenance triggers. At a safe checkpoint,
rewrite active state rather than indefinitely appending checkpoint sections.

The observational `tools/check_memory_health.py` may report health but never
rewrite memory automatically.

This decision follows D-014, which is already assigned to the v1.0A
sinks/provenance contract. It changes no football/model/application behavior.
