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

**Status:** ACTIVE / NARROW TOOLING REPAIR

A read-only audit of checkpoint `4b979b4c105f60bdf4f3467b9448b370cf9ce6a2`
found that `docs/memory/manifest.json` records Windows worktree byte counts and
SHA-256 values, while Git commits line-ending-normalized blob bytes.

Measured examples:
- `USER.md`: manifest 3316 bytes; committed Git blob 3268 bytes.
- `AGENTS.md`: manifest 7396 bytes; committed Git blob 7221 bytes.

The content push itself is valid. This is a registry-representation defect:
the manifest is currently a worktree-byte registry, not an exact durable
checkpoint-blob registry.

Decision boundary:
- repair the generator to hash the staged Git index representation;
- validate every entry against staged index bytes before commit;
- after commit, validate every entry against `HEAD:<path>` bytes;
- preserve `manifest.json` self-exclusion;
- keep scope to `docs/memory/**`;
- no football/model/application source change.
<!-- FANTASY_I005_MANIFEST_GIT_BLOB_SEMANTICS:END -->
