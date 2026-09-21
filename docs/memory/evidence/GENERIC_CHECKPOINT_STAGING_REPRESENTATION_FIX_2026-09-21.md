# Generic Checkpoint Staging Representation Fix — 2026-09-21

## Classification

`INFRASTRUCTURE DEFECT / ISOLATED STAGING ONLY / NO COMMIT / NO PUSH / CONTROL ROOT UNCHANGED / RUNTIME UNCHANGED`

## Evidence

The first declarative staging attempt failed at gate 1 because the checkpoint
spec used an inexact semantic marker for D-025. The helper correctly stopped
before staging.

The corrected spec passed:
- declarative/control-root validation;
- remote movement guard at
  `440d17fecb823f29f4cbeaf6d74d82d52f7ea045`;
- fresh isolated staging clone at that exact HEAD;
- 19-path reviewed copy/stage;
- schema-2 manifest generation with 103 entries.

The final gate then failed on:

`staged exact identity mismatch: tools/delivery/run_package.cmd`

Root cause: the helper compared the SHA-256 of raw control-root/worktree bytes
against staged Git blob bytes. Git text-clean normalization may transform CRLF
worktree bytes to LF index bytes. Those byte streams can have different SHA-256
values while representing the exact intended Git content.

## Correction

Permanent `tools/delivery/prepare_checkpoint_stage.py` now:
1. validates raw control-root SHA-256 identities;
2. verifies raw copy identity;
3. derives each expected staged blob OID with
   `git hash-object --path <path> --stdin` in the staging checkout;
4. compares that OID with the index blob OID;
5. generates and validates the memory manifest from staged Git blob bytes;
6. stops before commit/push.

Regression coverage explicitly proves a CRLF `.cmd` worktree file normalizes to
LF in the index while the filtered Git blob identity remains exact.

No Phase 1B source or commissioned-runtime source is changed by this fix.
