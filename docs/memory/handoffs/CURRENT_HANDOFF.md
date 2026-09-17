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
