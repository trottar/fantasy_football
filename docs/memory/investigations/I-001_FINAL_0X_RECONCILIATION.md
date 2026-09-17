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

<!-- FANTASY_I001_GUI_LINEAGE_V2_INVALID_TOOL_RECORD:BEGIN -->
## GUI-lineage v2 package — INVALID / SUPERSEDED

**Package:** `fantasy_phase0_gui_lineage_isolation_20260917_v2.zip`

**Tool/package status:** `INVALID / NOT PACKAGE-VALIDATED / SUPERSEDED`

The earlier claim that this package was fully package-validated was **incorrect**.
The package failed on the real Windows project before commit/push because its
generated Markdown evidence contained trailing whitespace that was rejected by:

`git diff --cached --check`

Therefore this package must not be described as successfully validated,
commissioned, or reusable.

### Valid measurements produced before the tooling failure

These measurements completed before the failure and remain valid evidence:

- exact v0.36 ZIP SHA-256:
  `598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`
- exact-v0.36 vs local extracted-v0.36 source delta:
  changed `0`, added `0`, removed `0`
- lineage classification:
  `NO_LOCAL_SOURCE_SUCCESSOR_DELTA`
- exact v0.36 `compileall` exit: `0`
- exact v0.36 `pytest -q` exit: `1`
- sanitized evidence ZIP:
  `phase0_gui_lineage_v2_evidence_20260917_033228.zip`
- sanitized evidence ZIP SHA-256:
  `e64094a5b5da9205f65b18176c641b08dec9bf4116dc128e425755fbe77587c0`

### Interpretation boundary

`NO_LOCAL_SOURCE_SUCCESSOR_DELTA` means the local extracted
`fantasy_season_v0_36` source surface matches the exact v0.36 ZIP on the
diagnostic's compared source surface. There is no local GUI-only successor
hidden in that extracted tree.

`pytest = 1` is a measured nonzero test result, but its cause is not yet
diagnosed. It must remain `UNRESOLVED` until the failing test output is inspected
or reproduced with captured diagnostics.

### Tooling failure

The generated evidence Markdown contained added blank lines with trailing
whitespace. The failure occurred after evidence generation and manifest
generation, but before commit/push.

No football/model/application source was modified.

### Successor requirement

Before another lineage diagnostic is delivered:
- generated Markdown must be normalized to remove trailing whitespace;
- package QA must render representative memory output and run an actual
  whitespace cleanliness check on that rendered output;
- the exact delivered package must repeat that rendered-output check.
<!-- FANTASY_I001_GUI_LINEAGE_V2_INVALID_TOOL_RECORD:END -->

<!-- FANTASY_I001_V036_PYTEST_DIAGNOSIS_20260917_V1:BEGIN -->
## Exact v0.36 pytest diagnosis

Timestamp: `2026-09-17T03:50:59.301342-04:00`

**Diagnosis:** `V036_SPECIFIC_DETERMINISTIC_TEST_REGRESSION`

Exact v0.35-fixed1 passes in the same Python environment, while 2 v0.36 failing node(s) remain failing when rerun directly.

### Exact v0.36

- ZIP SHA-256: `598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`
- pytest exit: `1`
- parsed failing nodes: `2`
- targeted reruns executed: `2`

Failing nodes:
- `tests/test_mock_calibration.py::test_packaged_full_mock_is_complete_and_has_16_user_picks`
- `tests/test_mock_calibration.py::test_mock_inventory_sees_first_calibration_sample`

### Exact v0.35-fixed1 baseline

- commit: `c85434a6be7852310c47fc8d1847c61a0a023209`
- VERSION: `0.35-fixed1`
- pytest exit: `0`
- parsed failing nodes: `0`

Baseline failing nodes:
(none parsed)

### Evidence

- sanitized evidence ZIP:
  `phase0_v036_pytest_diagnosis_20260917_035059.zip`
- SHA-256:
  `db44cb6ec8929f1818eb0aa786ce77a53d6af8943067171011ab69708ac9d3b7`

No football/model/application source was modified. All tests ran in disposable
extractions using the same local Python environment.
<!-- FANTASY_I001_V036_PYTEST_DIAGNOSIS_20260917_V1:END -->

<!-- FANTASY_I001_V036_FIXTURE_RESTORATION_20260917_V1:BEGIN -->
## v0.36 fixture-restoration probe

Timestamp: `2026-09-17T04:04:48.120222-04:00`

**Classification:** `V036_RELEASE_PACKAGING_FIXTURE_REGRESSION_CONFIRMED`

The two deterministic v0.36 failures disappear after restoring only the four missing baseline mock-draft fixtures, and the full v0.36 suite then passes.

### Probe design

The exact v0.36 release was extracted to a disposable directory. Only the four
mock-draft fixture files absent from v0.36 but present in the exact
v0.35-fixed1 baseline were copied into that disposable extraction. No Python
source, config, version file, or model data was changed.

Restored fixtures:
- `data/mock_drafts/Pasted_markdown_20260830-223840_.csv` — SHA-256 `ca8556577c5bfdd42683da4b3a24d112522c650ac8f301fb406edaa20dc50603`
- `data/mock_drafts/Pasted_markdown_20260830-223840__summary.json` — SHA-256 `97a693e6fd1c890c9beab20e05b02ab6fc263d2d9816675936a772d6046f6054`
- `data/mock_drafts/mock_20260830_full.csv` — SHA-256 `008461de49f486dc837feb5c867ba222db2a3b02bfc619772c36384ea4b3f78b`
- `data/mock_drafts/mock_20260830_full_summary.json` — SHA-256 `c6e2f2334cb3f2f1723fc9459400bcea5a79df1ba1848e83f2746afe6fd99050`

### Results

Known failing nodes before restoration:
- `tests/test_mock_calibration.py::test_packaged_full_mock_is_complete_and_has_16_user_picks`
- `tests/test_mock_calibration.py::test_mock_inventory_sees_first_calibration_sample`

Targeted reruns before restoration:
- exits: `[1, 1]`

Targeted reruns after restoration:
- exits: `[0, 0]`

Full v0.36 suite after restoration:
- exit: `0`

Evidence ZIP:
`phase0_v036_fixture_probe_20260917_040448.zip`

Evidence SHA-256:
`823fd30bf500dd4835bbc4cfa942774783a6958bf8f5c8a7c2da2b2d769e02f9`

No football/model/application source was modified.
<!-- FANTASY_I001_V036_FIXTURE_RESTORATION_20260917_V1:END -->

<!-- FANTASY_I001_FINAL_AUTHORITY_20260917_V1:BEGIN -->
## I-001 final authority decision

**Status:** `RESOLVED`

### Final Phase 0 conclusion

The investigation distinguishes **source validity** from **release-artifact
validity**.

#### v0.36 source

**Status:** `SOURCE-VALIDATED / NOT YET DURABLY IMPORTED`

Evidence:
- exact `fantasy_season_v0_36.zip` identified as VERSION `0.36`;
- local extracted `fantasy_season_v0_36` has `0 changed / 0 added / 0 removed`
  on the compared source surface relative to the exact ZIP;
- exact v0.36 initially had two deterministic pytest failures;
- both failures were traced to four omitted mock-draft calibration fixtures;
- restoring only those four baseline fixtures in a disposable v0.36 extraction
  changed the targeted failures from `[1, 1]` to `[0, 0]`;
- the full v0.36 suite then passed with exit code `0`;
- no Python source, config, model parameter, or football physics was changed to
  obtain closure.

Therefore the measured defect is not a v0.36 football/model/source regression.

#### Existing v0.36 ZIP

**Status:** `INVALID AS COMMISSIONED RELEASE ARTIFACT / SUPERSEDED FOR DELIVERY`

The existing ZIP SHA-256 is:

`598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`

It omits four test-required mock-calibration fixtures and fails its own packaged
test suite. It must not be described as a clean commissioned final release.

#### v0.36-fixed1

**Status:** `NOT ESTABLISHED`

No exact artifact or specific provenance for a pre-existing v0.36-fixed1 release
was found.

### Authority boundary

For future technical reasoning, v0.36 is the latest **source-validated 0.X
candidate**.

The durable/public repository still does not contain a validated import of that
v0.36 source, and no repaired release artifact has been commissioned.

Creating/importing a repaired v0.36-derived release is a production/release
change and remains behind explicit user authorization.

### Reopen rule

Reopen I-001 only if new evidence appears that:
- the exact v0.36 source differs from the measured local source;
- fixture-only restoration does not reproduce the full-suite closure;
- a genuine historical v0.36-fixed1 artifact/provenance is recovered; or
- a new deterministic source-level regression is demonstrated.
<!-- FANTASY_I001_FINAL_AUTHORITY_20260917_V1:END -->
