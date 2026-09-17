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

<!-- FANTASY_COMMUNICATION_CHECKPOINT_METHOD:BEGIN -->
## Work-session communication protocol

A new chat should reconstruct the project from a small stable set of repository files, not from conversation history.

### Start of substantial work

Read:
1. `CURRENT.md`
2. `MEMORY.md`
3. `handoffs/CURRENT_HANDOFF.md`
4. `USER.md`
5. `AGENTS.md`
6. only the architecture/decision/evidence/investigation/patch/roadmap files relevant to the task
7. exact current source/tests for the affected subsystem

### During work

- Put detailed measured discoveries in the dated log.
- Keep hypotheses out of curated durable facts until evidence supports them.
- When a decision changes, update status/supersession rather than leaving two apparently-current decisions.
- Record failed diagnostics and tooling defects when they materially change what is known or what should be tried next.
- Provide timestamped progress/debug output for long local procedures so failure location and completed stages are visible.

### End of meaningful work

Update, as applicable:
- dated log;
- `CURRENT.md`;
- decision/investigation/evidence/roadmap;
- current handoff;
- `MEMORY.md` only for durable cross-phase facts.

Memory changes belonging to a patch travel in the same ZIP. The patch itself is a continuation checkpoint containing what changed, what was actually validated, what remains unvalidated, and what comes next.
<!-- FANTASY_COMMUNICATION_CHECKPOINT_METHOD:END -->
