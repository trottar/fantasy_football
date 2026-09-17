# Current Project State

```yaml
as_of: 2026-09-16
baseline_release: 0.35-fixed1
baseline_commit: c85434a6be7852310c47fc8d1847c61a0a023209
season: 2026
week_1_status: complete
week_2_first_game: 2026-09-17
```

## Current authority

The GitHub repository is the durable source-of-truth for pushed source and curated project memory.

The current committed baseline is the commissioned `v0.35-fixed1` tree. A `v0.36.zip` artifact exists locally outside Git, but it is not yet represented in repository history. Historical notes indicate later v0.36 work, but exact source/provenance must be reconciled before importing it.

## Scientific boundary

`0.X` is the a-priori architecture era. No observed 2026 game outcomes may be used to tune a 0.X model.

Week 1 is complete, so any data-informed development belongs in `1.X`.

## Immediate priorities

1. Establish this durable-memory system before further model work.
2. Reconcile the exact final 0.X source lineage, including v0.36 and any GUI fixed release.
3. Preserve an independent Week 2 prospective capture before Week 2 starts if still causally possible.
4. Implement v1.0 observability: Week 1 ingestion, weekly recap, immutable observation schema, residual diagnostics, transaction ledger, and anomaly classification.
5. Rebuild waiver/FA market mechanics in v1.2.
6. Rebuild trade search/negotiation mechanics in v1.3.
7. Delay empirical calibration until evidence supports it.

## Known market defects to investigate

- Automated trade search historically screens only 1-for-1 candidates even though the evaluator can support larger packages.
- Waiver acquisition probability is historically modeled as independent candidate-level manager claims rather than ordered contingent claim lists resolved through actual waiver priority/mechanics.
- Manager behavior must remain separate from football utility.

## Current rule

Do not modify football physics while bootstrapping memory/observability. Evidence and structure first.
