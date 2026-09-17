# Agent Operating Rules

## Startup order

For substantial work, read:

1. `CURRENT.md`
2. `MEMORY.md`
3. `handoffs/CURRENT_HANDOFF.md`
4. `USER.md`
5. `AGENTS.md`
6. relevant architecture/decision/evidence/investigation/roadmap files
7. current source and tests for the affected subsystem

Do not use `history/` to override current state.

## Authority and evidence

Current source plus fresh runtime evidence is authoritative between checkpoints. Git history is reference/history unless it matches the validated working state.

Raw measurements outrank derived classifiers when they conflict. Investigate the measurement/classifier boundary before changing physics.

Never claim validation, testing, commissioning, or source inspection that did not actually occur.

## Development method

`one narrow hypothesis -> one targeted diagnostic/probe -> fresh evidence -> inspect evidence -> one coherent patch`

Do not bundle unrelated cleanup into a scientific fix. Do not reopen resolved/deferred work without new evidence.

## Scientific constraints

- Preserve `P ⊕ D ⊕ K`.
- Keep football physics separate from manager behavior.
- Use decision-time information only for prospective decisions.
- Preserve frozen pregame states.
- Do not use hindsight to justify a pregame action.
- Treat uncertainty as first-class output.
- Add higher-order response only when material.
- `screen != authority`.

## Version boundary

Observed 2026 outcomes must not tune any 0.X release. Data-informed work is 1.X.

Structural defects may be fixed when the real process cannot be represented. Empirical retuning requires accumulated evidence.

## Release/patch discipline

1. Inspect exact latest source.
2. Record expected pre-state.
3. Make a narrow coherent change.
4. Run targeted tests.
5. Run full tests.
6. Run `compileall`.
7. Package reproducibly when needed.
8. Validate exact generated output.
9. Re-test exact delivered package when release packaging is involved.
10. Update durable memory in the same checkpoint.

Never include secrets, caches, bytecode, or local authenticated raw data in Git/releases.

## Windows operational rule

Primary local environment: Windows 10 + Windows PowerShell. Prefer self-contained ZIP + `.ps1` + one root-level execution command for multi-step local procedures.
