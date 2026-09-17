# I-001 — Final 0.X Source Reconciliation

<!-- FANTASY_I001_V14_CLASSIFIER_SUPERSESSION:BEGIN -->
## v1.4 measured result and classifier supersession

Probe v1.4 runtime completed.

Valid raw measurements:
- baseline `v0.35-fixed1` retrieval and VERSION verification passed;
- local `fantasy_season_v0_36` and `fantasy_season_v0_36.zip` were compared;
- v0.36 ZIP comparison: 23 changed / 3 added / 7 removed public-safe files;
- 330 sanitized provenance hits were collected;
- non-memory Git porcelain was unchanged;
- football/model source was not modified.

The emitted classification `FIXED1_NAMED_ARTIFACT_FOUND_NEEDS_CONTENT_VALIDATION` is `SUPERSEDED / REPRESENTATION-INCOMPLETE`.

Reason: the classifier treated any artifact name containing `fixed1` as potential fixed1 lineage evidence, including known v0.35-fixed1 baseline artifacts. Therefore that label cannot establish a v0.36-fixed1 artifact.

Authority decision remains `DEFERRED_PENDING_EVIDENCE_REVIEW`.

Next narrow action: inspect the sanitized v1.4 artifact inventory, candidate comparisons, provenance hits, and bounded diffs. Decide exact v0.36/fixed1 lineage from raw evidence, not the superseded classifier.
<!-- FANTASY_I001_V14_CLASSIFIER_SUPERSESSION:END -->
