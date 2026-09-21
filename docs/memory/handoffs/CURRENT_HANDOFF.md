# Current Handoff

`CURRENT.md` is authoritative. This file is a compact resume/operational-warning
surface and cannot override it.

## Last Remote-Verified Checkpoint

`8592989b78b6e94cd08d8618694b8168c62cf715`

## Active Technical Checkpoint

**v1.0A data-source season-sync shadow pilot**

Current classification:

`STAGING PREFLIGHT VALIDATED / SCHEMA-2 MANIFEST PREFLIGHT PASS / 15 PATHS STAGED / NOT COMMITTED / RUNTIME UNCHANGED`

The retained source candidate passed 39 targeted tests, the paired privacy /
non-interference probe, full pytest (**459 passed in 52.73 s**), compileall, and
candidate diff/allowlist inspection.

A fresh staging clone at the exact remote checkpoint then passed: four technical
file byte identity, exact 10-path current-memory inventory/copy/byte identity,
strict memory health, combined diff-check, exact 14-path staging, schema-2
manifest regeneration from staged Git blobs (**100 entries**), exact 15-path
staged allowlist, no residue, and cached diff-check.

Because this v4 memory checkpoint advances control-root memory after that
manifest measurement, the current staged manifest is preflight evidence only.
Refresh the v4-updated memory files into the same staging clone and regenerate
the manifest once more before commit. Do not create another recursive memory
bookkeeping checkpoint before commit.

## Resume Instruction

1. Read the complete bootstrap set.
2. Read D-020, D-024, and the preflight evidence record.
3. Preserve the Week 3 prospective-capture deadline.
4. Resume from the last validated gate; do not rerun passed gates without new
   evidence.
5. Apply memory v4 if not already applied.
6. Refresh only the v4-updated memory files into the existing staging clone,
   re-stage them, regenerate the schema-2 manifest from staged Git blob bytes,
   and validate the staged allowlist/residue/cached diff.
7. Do not commit/push/runtime-sync during that refresh step.

## Critical Boundaries

- control root != source candidate != staging clone != commissioned runtime;
- no provider-level instrumentation;
- no arguments, returned payloads/paths, authenticated data, or exception
  messages in observability events;
- no persistent sink;
- no football/model semantic change;
- no direct GitHub connector writes for checkpoints;
- small validation steps are preferred after tooling/package failures.
