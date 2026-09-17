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

<!-- FANTASY_PROBLEM_SOLVING_METHOD:BEGIN -->
## Evidence-led development method

Use this operating loop for substantial work:

**authority check -> one narrow question/hypothesis -> one targeted diagnostic/probe -> fresh evidence -> inspect the raw evidence -> classify the result -> one coherent patch or explicit defer/close decision**

### Authority

1. The validated local working tree plus fresh measured evidence is authoritative between checkpoints.
2. Exact successful installer/runtime receipts and installed-output hashes outrank reconstructed historical expectations.
3. Current durable-memory state (`CURRENT.md`, `MEMORY.md`, current handoff, current dated log) follows.
4. Git/GitHub is durable source/history, but must not silently override a newer validated local state.
5. Older summaries/history are reference only.

When sources disagree, do not silently merge them. Record the discrepancy, identify which evidence is newer/more direct, and explicitly supersede the stale statement.

### Before changing production behavior

- Inspect exact current source and relevant runtime state.
- State the narrow question being answered.
- Define the decision boundary before running the probe: what outcomes would justify patching, further diagnosis, deferral, or closure.
- Prefer a diagnostic-only probe while cause, architecture, or measurement semantics remain uncertain.
- Reuse existing logs, telemetry, snapshots, and model instrumentation before adding parallel instrumentation.
- Do not infer a subsystem failure from a downstream symptom when a direct measurement exists.
- Raw measurements outrank derived classifiers when they disagree.

### After a probe

Record:
- question;
- pre-state/provenance;
- probe and scope;
- raw measured result;
- interpretation/classification;
- limitations or representation gaps;
- decision;
- next narrow action.

If later evidence shows an earlier metric was incomplete, preserve the earlier measurement but annotate the limitation and point to the superseding investigation. Do not rewrite history to make the earlier result appear more complete than it was.

### Patch discipline

- Make one coherent change.
- Preserve unrelated validated subsystems.
- Avoid opportunistic cleanup.
- Validate the exact generated/installed output, not merely the generator or intended command.
- Distinguish source correctness, deterministic/package validation, runtime validation, and commissioning.
- Never claim a validation ran if it did not run.
- Do not reopen a resolved/deferred investigation without new evidence.

### Failure-state vocabulary

Keep these states explicit where applicable:
- `FAILED BEFORE MODIFICATION`
- `ROLLED BACK`
- `INSTALLED SUCCESSFULLY`
- `SOURCE-VALIDATED`
- `RUNTIME-VALIDATED`
- `COMMISSIONED`
- `DEFERRED`
- `SUPERSEDED`

A failed installer/probe can have side effects before a production-file write. Track project-file modification state separately from runtime cleanup or temporary side effects.

### Packaging

A meaningful patch ZIP is also a communication checkpoint: implementation, validation state, durable-memory updates, and rollback/provenance information travel together. Set `durable_memory_updated: true` in the package manifest.
<!-- FANTASY_PROBLEM_SOLVING_METHOD:END -->
