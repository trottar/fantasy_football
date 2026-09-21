# Current Handoff

`CURRENT.md` is authoritative. This file is a compact resume/operational-warning
surface and cannot override it.

## Last Remote-Verified Checkpoint

`440d17fecb823f29f4cbeaf6d74d82d52f7ea045`

Commit: **Record Phase 1A runtime commissioning**.

## Active Technical Checkpoint

**Generic `.ffpkg` delivery + repository staging infrastructure — LOCAL-APPLIED / VALIDATED**

Current classification:

`DELIVERY/STAGING INFRASTRUCTURE LOCAL-APPLIED / DELIVERY TESTS 18 PASS / GIT-FILTERED STAGE IDENTITY REGRESSION PASS / MEMORY .FFPKG PASS / RUNTIME UNCHANGED`

The commissioned runtime remains `v0.36-repack1`, internal `VERSION = 0.36`, and
Phase 1A remains commissioned. The retained Phase 1B closure-shadow candidate is
still isolated and unchanged; its candidate validation gates already passed and
must not be rerun without new evidence.

The permanent delivery path is now:

`assistant builds deterministic text .ffpkg -> user runs tools\delivery\run_package.cmd -> returned summary -> assistant verification -> separate staging/manifest/commit/push -> remote verification`

## Resume Instruction

1. Read the complete bootstrap set.
2. Treat Phase 1A runtime commissioning and repository closure as complete.
3. Treat the first generic durable-memory `.ffpkg` as passed.
4. Use `tools/delivery/prepare_checkpoint_stage.py` with a declarative staging
   spec; raw worktree SHA-256 and Git index blob identity are separate layers.
5. Stage the eight delivery/staging infrastructure and regression paths plus the
   reviewed memory delta, regenerate the schema-2 manifest, and validate without
   committing/pushing.
6. Commit/push/remote-verify that checkpoint separately, then resume the retained
   Phase 1B closure-shadow candidate; preserve the Week 3 prospective-capture deadline.

## Critical Boundaries

- control root != staging clone != commissioned runtime;
- generic delivery infrastructure owns transport/execution mechanics only;
- package entrypoints own target-specific predecessor/rollback/idempotence logic;
- no provider-level instrumentation;
- no arguments, returned payloads/paths, authenticated data, or exception
  messages in observability events;
- persistent sink remains disabled;
- no football/model semantic change;
- no direct GitHub connector writes for checkpoints;
- successful operator steps may return concise summary blocks; request full logs
  only for failures or missing evidence.
