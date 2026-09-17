# Active Investigations

## I-001 — Final 0.X source reconciliation

Determine exact source/provenance status of v0.36 and any GUI fixed release relative to committed v0.35-fixed1. Do not reconstruct from memory if exact artifacts/source exist.

## I-002 — Trade search architecture

Audit latest exact source to confirm whether automated trade candidate generation is still effectively 1-for-1 only and whether larger package evaluation exists without corresponding search coverage.

## I-003 — Waiver resolver architecture

Audit actual ESPN waiver configuration and transaction semantics. Replace candidate-independent Bernoulli acquisition approximations with ordered contingent claim-list resolution if latest source still has that structural mismatch.

## I-004 — Week 1 Data/MC closure

Ingest immutable Week 1 observations and compare them to frozen prospective predictions. Open sub-investigations for structural/input/uncertainty/behavior discrepancies. Do not retune automatically.

<!-- FANTASY_I005_MANIFEST_GIT_BLOB_SEMANTICS:BEGIN -->
## I-005 — Durable-memory manifest Git-blob semantics

**Status:** RESOLVED / RUNTIME-VALIDATED

Checkpoint `243e4ee4906f42582a5603170e7d7c73095c9dac`
successfully repaired the durable-memory registry representation.

Validated result:
- manifest schema is `2`;
- representation is `git_index_blob_bytes`;
- generation hashes staged Git index bytes;
- post-commit validation compares entries against committed `HEAD` blob bytes;
- the manifest excludes itself;
- the repair commit changed only `docs/memory/**`;
- remote `main` was verified at the repair checkpoint;
- no football/model/application source changed.

The previous worktree-vs-Git-byte mismatch is closed. Reopen only if new evidence
shows index/HEAD/remote checkpoint disagreement.
<!-- FANTASY_I005_MANIFEST_GIT_BLOB_SEMANTICS:END -->
