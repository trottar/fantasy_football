# Communication and Handoff Protocol

## Starting a work session

Load the smallest stable set first:

1. `MEMORY.md`
2. `CURRENT.md`
3. `USER.md`
4. `AGENTS.md`
5. `handoffs/CURRENT_HANDOFF.md`

Then read only relevant subsystem architecture, decisions, evidence, investigations, and source.

## During work

- Put durable discoveries in the current dated memory log.
- Do not promote hypotheses to `MEMORY.md` until evidence supports them.
- Update decision status instead of leaving contradictory current statements.
- Link investigations to evidence and affected source.
- Keep raw/private evidence local unless deliberately sanitized.

## Ending substantial work

Update, as applicable:
- dated memory log
- `CURRENT.md`
- roadmap/status
- affected decision/investigation/evidence
- current handoff
- `MEMORY.md` only for cross-phase durable facts

Meaningful patches/releases must travel with memory changes in the same Git checkpoint.
