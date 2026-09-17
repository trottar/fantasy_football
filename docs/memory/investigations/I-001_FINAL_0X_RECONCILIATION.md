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

<!-- FANTASY_I001_V2_AUTHORITATIVE_ARTIFACT_REVIEW:BEGIN -->
## v2 authoritative-artifact evidence review

Timestamp: `2026-09-17T03:06:26.836159-04:00`

**Status:** `V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED`
**Authority:** `V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`

### Predecessor v1 failure

`fantasy_phase0_i001_evidence_review_v1` failed at runtime before modification.

Observed error:
`Required v1.4 evidence ZIP missing: L:\Projects\fantasy_football\phase0_reconcile_results_20260917_020142.zip. Found alternatives: []`

Classification: `FAILED BEFORE MODIFICATION`.

The v1 script verified remote `main = 840e4064...` and then stopped before local
memory writes, staging clone, commit, or push. No football/model/application
source changed.

Root cause: the successor review depended on a prior diagnostic result ZIP that
was not durable local authority and was no longer present.

v2 correction: reconstruct the evidence directly from authoritative local
v0.36 artifacts plus the exact committed v0.35-fixed1 baseline. Prior result
ZIPs are no longer required.

### Fresh raw evidence

- baseline commit: `c85434a6be7852310c47fc8d1847c61a0a023209`
- baseline VERSION: `0.35-fixed1`
- v0.36 ZIP: `L:\Projects\fantasy_football\fantasy_season_v0_36.zip`
- v0.36 ZIP SHA-256: `598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`
- v0.36 VERSION: `0.36`
- exact VERSION-verified v0.36-fixed1 artifacts: `0`
- source-bundle exact v0.36-fixed1 hits: `0`
- v0.36 ZIP internal exact v0.36-fixed1 text files: `0`
- comparison vs baseline: changed `23`, added `3`, removed `7`

### Interpretation

The exact local v0.36 ZIP identifies as VERSION 0.36; no exact v0.36-fixed1 artifact or specific v0.36-fixed1 provenance was established.

The old v1.4 name-only `fixed1` classifier remains superseded. This review uses
exact artifact identity and exact v0.36-fixed1 provenance only.

No football/model/application source was modified or executed.
<!-- FANTASY_I001_V2_AUTHORITATIVE_ARTIFACT_REVIEW:END -->

<!-- FANTASY_I001_GUI_DIAGNOSTIC_FAILURE_20260917:BEGIN -->
## GUI-lineage diagnostic failure and tooling QA hold

**Status:** `DIAGNOSTIC TOOLING HOLD / FAILURE RECORDED`

The unique package
`fantasy_phase0_gui_lineage_isolation_20260917_v1.zip`
failed during diagnostic execution before any project-memory commit/push.

Observed exception:

```text
NameError: name 'sys' is not defined
```

The exception occurred in `run_release_checks()` while attempting to call
`sys.executable`.

### Classification

`FAILED DURING DIAGNOSTIC EXECUTION / BEFORE MEMORY COMMIT-PUSH`

No football/model/application source was modified.

### Root cause

The delivered script referenced the global name `sys` without importing it.

The prior validation was insufficient:
- `py_compile` checks syntax, not runtime name resolution;
- the synthetic self-test did not execute `run_release_checks()`;
- therefore the actual failing path was not covered before delivery.

### Additional audit findings

The full script audit also found:
- staging-clone cleanup was not protected by an unconditional `finally`;
- the GUI-only classifier allowed `fantasy.py` launcher divergence to coexist
  with GUI changes without forcing a broader classification;
- `ALREADY APPLIED` protected the remote from duplicate push but did not prove
  local memory synchronization after a hypothetical push/local-sync split.

### Decision

Pause I-001 GUI-lineage execution until the strengthened diagnostic-tool QA gate
is checkpointed and the successor passes it.

The successful earlier I-001 result remains authoritative:
`V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED` /
`V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`.
<!-- FANTASY_I001_GUI_DIAGNOSTIC_FAILURE_20260917:END -->
