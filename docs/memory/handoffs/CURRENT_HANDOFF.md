# Current Handoff

## Baseline

Repository: `trottar/fantasy_football`

Pre-memory baseline:

`c85434a6be7852310c47fc8d1847c61a0a023209`

Release: `0.35-fixed1`

## Established

- GitHub is the durable source-of-truth for pushed source and curated memory.
- Public-repository/local-secret boundary is explicit.
- OpenClaw/PrivyHub-style durable memory is adopted.
- No Week 1 calibration or model retuning occurred during bootstrap.

## Next technical action

Reconcile exact final 0.X lineage before modifying model code. Locate and inspect exact v0.36 source/release artifacts and determine GUI fixed-release status.

Then build v1.0 as an observability/evidence release: Week 1 ingestion, weekly recap, Data/MC closure, transaction ledger, and investigations with zero automatic calibration.

## Guardrails

- 0.X remains a-priori.
- Data-informed changes are 1.X.
- `P ⊕ D ⊕ K` remains intact.
- `screen != authority`.
- Behavior kernels remain separate from football physics.
- Use decision-time information only.

<!-- FANTASY_PROCEDURE_AUDIT_HANDOFF:BEGIN -->
## Problem-solving procedure adopted from repository audit

The development method has been normalized around evidence-led, typed durable memory:

`authority check -> narrow question -> targeted probe -> fresh evidence -> inspect raw result -> classify -> coherent patch/defer/close`

Key continuation rules:
- local validated tree + fresh evidence outrank historical summaries;
- define decision boundaries before probes;
- preserve raw measurements when interpretations are later superseded;
- separate current state, durable facts, dated history, decisions, investigations, evidence, patches, and handoffs;
- validate exact generated/installed output;
- use explicit failure/rollback/install states;
- keep meaningful memory updates in the same ZIP/checkpoint as the work;
- do not reopen resolved/deferred work without new evidence;
- preserve stable subsystems during unrelated fixes.
<!-- FANTASY_PROCEDURE_AUDIT_HANDOFF:END -->

<!-- FANTASY_MANIFEST_REGISTRY_REPAIR_HANDOFF:BEGIN -->
## Durable-memory manifest repair handoff

The procedure-memory content is preserved and football/model source is unchanged.

A post-push audit found the memory registry generator produced malformed `y/...`
relative paths and included `manifest.json` in its own inventory. This is a
tooling/registry defect, not a football-model defect.

The active repair replaces string-sliced relative paths with provider-derived
relative paths and requires exact registry/tree set equality plus per-file
byte/SHA-256 verification before any commit/push.

Do not treat the manifest registry as repaired unless the repair package ends
with `MANIFEST REPAIR: PUSHED SUCCESSFULLY` and the resulting GitHub commit is
read-back verified.
<!-- FANTASY_MANIFEST_REGISTRY_REPAIR_HANDOFF:END -->
