# Memory Maintenance Audit — 2026-09-17

## Classification

`DOCUMENTATION / MEMORY-INFRASTRUCTURE MAINTENANCE`

`NO PRODUCTION BEHAVIOR CHANGE`

## Authority

Pre-maintenance repository state was the committed v1.0A context/event
checkpoint with commissioned `v0.36-repack1` as the final 0.X runtime baseline.

The maintenance was triggered by both size and semantic conditions:

- `CURRENT.md` had accumulated sequential previously-current checkpoints;
- `CURRENT_HANDOFF.md` had become an append-only historical ledger;
- startup instructions differed between `AGENTS.md` and `COMMUNICATION.md`;
- `TOOLS.md` and memory README metadata still exposed stale 0.35-fixed1 baseline
  wording;
- `roadmap/STATUS.md` retained superseded Phase 0 progress beside the completed
  state;
- `investigations/ACTIVE.md` still listed resolved I-001/I-005 work.

## Before / After

| File | Before bytes | Before lines | After bytes | After lines |
| --- | ---: | ---: | ---: | ---: |
| AGENTS.md | 7396 | 175 | 2572 | 79 |
| CURRENT.md | 16685 | 392 | 5488 | 145 |
| MEMORY.md | 11880 | 302 | 5928 | 185 |
| CURRENT_HANDOFF.md | 18207 | 429 | 1222 | 36 |
| COMMUNICATION.md | 3198 | 83 | 2177 | 68 |
| Initial bootstrap total (AGENTS + CURRENT + USER) | 27397 | 615 | 9817 | 273 |

## Startup Contract

Fresh substantial work now reads:

1. `AGENTS.md`
2. `CURRENT.md`
3. `USER.md`

Then only task-relevant referenced material and exact source/tests.

## Authority Model

- current state: `CURRENT.md`
- durable cross-phase knowledge: `MEMORY.md`
- user/environment preferences: `USER.md`
- operating/startup rules: `AGENTS.md`
- maintenance policy: `MAINTENANCE.md`
- communication/checkpoint lifecycle: `COMMUNICATION.md`
- tooling/procedures: `TOOLS.md` + `patches/PATCH_PROTOCOL.md`
- evidence: `evidence/`
- investigations: `investigations/`
- dated history: `memory/YYYY-MM-DD.md`
- handoff: `handoffs/CURRENT_HANDOFF.md` (non-authoritative resume aid)

## Information Preservation

Exact pre-maintenance copies of every rewritten bootstrap/active/procedural file
were preserved under:

`history/2026-09-17_pre_maintenance/`

Canonical evidence, investigation, decision, patch, and dated-history files were
not deleted.

The old append-only state is historical, not current authority.

## Current Frontier Preserved

- commissioned baseline: `v0.36-repack1`, internal `VERSION = 0.36`;
- Phase 0 I-001: resolved;
- v1.0A context/event slice 1: test-validated;
- completed v1.0A sinks/provenance slice is present and test-validated;
- next development slice: invariant registry + privacy/redaction primitives;
- production event call-site integration: not started.

The first maintenance package was stale when executed because the repository had
already advanced to the sinks/provenance checkpoint. It failed before modification
and is superseded. That failure is preserved in maintenance evidence/history.

## Validation

This checkpoint requires:
- exact pre-state snapshot preservation;
- generated Markdown trailing-whitespace checks;
- memory-health strict check;
- startup-contract consistency checks;
- internal reference existence checks;
- `git diff --cached --check`;
- exact staged allowlist;
- schema-2 Git index/HEAD manifest validation;
- `py_compile` + self-test of the memory-health tool;
- full repository `compileall`;
- full repository `pytest`;
- remote-moved guard and post-push verification.

## Production Boundary

No football physics, player valuation, Monte Carlo behavior, manager behavior,
waiver/trade logic, specialist policy, recommendation threshold, GUI business
logic, model calibration, or production decision semantics changed.

`NO PRODUCTION BEHAVIOR CHANGE`
