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

<!-- FANTASY_CURRENT_2026_09_17_OBSERVABILITY:BEGIN -->
## Current state — 2026-09-17 observability transition

Phase 0 remains active until final 0.X lineage is proven.

Measured Phase 0 v1.4 facts:
- exact public `v0.35-fixed1` baseline retrieval/verification succeeded;
- local `fantasy_season_v0_36` and `fantasy_season_v0_36.zip` were found and compared to the baseline;
- v0.36 ZIP comparison measured 23 changed, 3 added, and 7 removed public-safe files relative to the retrieved baseline;
- non-memory Git porcelain remained unchanged;
- football/model source was not modified;
- the v1.4 classifier `FIXED1_NAMED_ARTIFACT_FOUND_NEEDS_CONTENT_VALIDATION` is superseded as representation-incomplete because baseline names containing `fixed1` could trigger it. Raw measurements remain valid and outrank the classifier.

Current authority for final 0.X is still `DEFERRED_PENDING_EVIDENCE_REVIEW`.

In parallel, `v1.0A` diagnostics/observability architecture is active as a development-only engineering phase. It may define schemas, diagnostic tools, static audits, provenance, invariants, replay/failure contracts, and GUI diagnostics, but must not alter football physics or assume a final source baseline before Phase 0 closes.

Immediate order:
1. inspect Phase 0 v1.4 raw evidence and freeze final 0.X;
2. preserve prospective Week 2 state while causally possible;
3. commission the v1.0A observability substrate against the frozen baseline;
4. proceed to immutable observation ingestion and Data/MC closure.
<!-- FANTASY_CURRENT_2026_09_17_OBSERVABILITY:END -->

<!-- FANTASY_MEMORY_INFRA_READY_2026_09_17:BEGIN -->
## Memory / diagnostic checkpoint infrastructure — READY

The PrivyHub-style checkpoint workflow is now established and validated.

Current durable checkpoint:
`243e4ee4906f42582a5603170e7d7c73095c9dac`

Validated infrastructure:
- memory updates travel in ZIP/PowerShell checkpoints and are pushed as part of
  the checkpoint;
- diagnostic/probe/audit/observability tooling has standing authorization to
  advance through the same workflow;
- football/model/application/business-logic code remains gated behind explicit
  user authorization;
- exact staged allowlists are required;
- remote-moved guards and post-push SHA verification are required;
- memory manifest paths exclude self-reference and use committed Git-blob
  semantics (`schema: 2`, `git_index_blob_bytes`);
- failures and successor fixes remain in durable history.

Infrastructure status: `READY`.

Phase 0 source-lineage reconciliation remains the next football-development
question; v1.0A diagnostics/observability can continue in parallel without
changing football physics.
<!-- FANTASY_MEMORY_INFRA_READY_2026_09_17:END -->

<!-- FANTASY_CURRENT_I001_V2:BEGIN -->
## I-001 current result

Classification: `V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED`
Authority: `V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`

The exact local v0.36 ZIP identifies as VERSION 0.36; no exact v0.36-fixed1 artifact or specific v0.36-fixed1 provenance was established.

The diagnostic evidence was rebuilt from authoritative artifacts; no prior
ephemeral result ZIP is required.

No football/model/application source change occurred.
<!-- FANTASY_CURRENT_I001_V2:END -->

<!-- FANTASY_CURRENT_DIAGNOSTIC_QA_HOLD:BEGIN -->
## Diagnostic QA hold before next I-001 probe

The authoritative Phase 0 result remains:

- classification: `V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED`;
- authority: `V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`.

The attempted GUI-lineage diagnostic failed from a tooling defect (`sys` not
imported) before any memory commit/push or production-source modification.

Current action:
1. checkpoint the strengthened diagnostic QA protocol;
2. build the GUI-lineage successor only after it passes the full runtime-path
   gate;
3. resume I-001 evidence work without changing football physics.
<!-- FANTASY_CURRENT_DIAGNOSTIC_QA_HOLD:END -->

<!-- FANTASY_CURRENT_GUI_LINEAGE_V2_INVALID_TOOL:BEGIN -->
## Current Phase 0 lineage state after invalid v2 diagnostic package

The GUI-lineage v2 package is **INVALID / SUPERSEDED** as tooling. The prior
statement that it was fully package-validated was incorrect.

Valid measured evidence from the failed run:
- exact v0.36 source equals local extracted v0.36 source on the compared surface:
  `changed=0`, `added=0`, `removed=0`;
- classification: `NO_LOCAL_SOURCE_SUCCESSOR_DELTA`;
- exact v0.36 compileall: `0`;
- exact v0.36 pytest: `1` (`UNRESOLVED` cause);
- evidence ZIP SHA-256:
  `e64094a5b5da9205f65b18176c641b08dec9bf4116dc128e425755fbe77587c0`.

The successful I-001 authority result remains:
`V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED` /
`V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`.

No production source changed.
<!-- FANTASY_CURRENT_GUI_LINEAGE_V2_INVALID_TOOL:END -->

<!-- FANTASY_CURRENT_V036_PYTEST_DIAGNOSIS_20260917:BEGIN -->
## Current Phase 0 test diagnosis

Exact v0.36 pytest diagnosis:
`V036_SPECIFIC_DETERMINISTIC_TEST_REGRESSION`

Exact v0.35-fixed1 passes in the same Python environment, while 2 v0.36 failing node(s) remain failing when rerun directly.

v0.36 pytest exit: `1`
v0.35-fixed1 baseline pytest exit: `0`

Final 0.X authority should use this diagnosis together with the established fact
that local extracted v0.36 has no source delta from the exact v0.36 ZIP.
<!-- FANTASY_CURRENT_V036_PYTEST_DIAGNOSIS_20260917:END -->

<!-- FANTASY_CURRENT_V036_FIXTURE_RESTORATION_20260917:BEGIN -->
## Current Phase 0 fixture-regression result

Classification:
`V036_RELEASE_PACKAGING_FIXTURE_REGRESSION_CONFIRMED`

The two deterministic v0.36 failures disappear after restoring only the four missing baseline mock-draft fixtures, and the full v0.36 suite then passes.

This probe changes only disposable test fixtures. It does not modify or tune
football physics.

The final 0.X decision should distinguish a release-packaging defect from a
football/model/source defect.
<!-- FANTASY_CURRENT_V036_FIXTURE_RESTORATION_20260917:END -->

<!-- FANTASY_CURRENT_PHASE0_FINAL_AUTHORITY_20260917:BEGIN -->
## Phase 0 final 0.X authority

I-001 is `RESOLVED`.

Current authority split:

- **v0.36 source:** `SOURCE-VALIDATED / NOT YET DURABLY IMPORTED`
- **existing v0.36 ZIP:** `INVALID AS COMMISSIONED RELEASE ARTIFACT`
- **historical v0.36-fixed1:** `NOT ESTABLISHED`
- **production/release repair/import:** `PENDING EXPLICIT AUTHORIZATION`

The v0.36 test failures were caused solely by four omitted mock-draft fixtures.
Fixture-only restoration closed both targeted failures and the complete suite
without modifying football/model/application source.

Phase 0 investigation is complete. The next production action is a narrow
packaging/import checkpoint, not additional diagnosis.
<!-- FANTASY_CURRENT_PHASE0_FINAL_AUTHORITY_20260917:END -->

<!-- FANTASY_V036_REPACK1_IMPORT_GUI_GATE_20260917_V1:BEGIN -->
## v0.36 durable import + repack1

Timestamp: `2026-09-17T11:01:47.459865-04:00`

Artifact label: `v0.36-repack1` (packaging revision only; internal `VERSION` remains `0.36`).

Original invalid v0.36 ZIP SHA-256:
`598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`

Repaired release ZIP:
`fantasy_season_v0_36_repack1.zip`

Repaired release SHA-256:
`01dc3ddce16d828ba91f97058e15ce4102592418a2648049135c24d146826380`

Packaging delta relative to exact v0.36:
- changed: `0`
- removed: `0`
- added: exactly the four previously identified mock-calibration fixtures.

Source import:
- imported the 26 previously measured/validated v0.36 changed-or-added files;
- no newly designed football/model/GUI logic was introduced in this checkpoint;
- the v0.36 source delta itself includes its already-validated `config/model.json` and source changes;
- the packaging repair adds fixtures only.

Validation:
- fixture-targeted pytest: PASS;
- candidate compileall: PASS;
- candidate full pytest: PASS;
- automated GUI gate: PASS (`17` GUI-focused test files);
- GUI lifecycle invariants: PASS;
- GUI safe-module import smoke: PASS;
- `gui` and `draft-gui` CLI/parser smoke: PASS;
- exact repaired ZIP compileall/full pytest/GUI gate: PASS;
- installed-tree byte manifest matches the validated exact ZIP: PASS.

Live browser GUI commissioning is still `PENDING`; v1.0A implementation remains blocked until that live check passes.

State: `SOURCE IMPORTED / RELEASE RUNTIME-VALIDATED / AUTOMATED GUI GATE PASS / LIVE GUI PENDING`.
<!-- FANTASY_V036_REPACK1_IMPORT_GUI_GATE_20260917_V1:END -->

<!-- FANTASY_V036_REPACK1_LIVE_GUI_COMMISSIONED_20260917_V1:BEGIN -->
## v0.36-repack1 live commissioning closure

Timestamp: `2026-09-17T12:09:41.522486-04:00`

Pre-commission GitHub main:
`8d4d95f8a12f1168372280381c75285bf5133647`

Release:
`v0.36-repack1` artifact revision, internal `VERSION = 0.36`.

Automated validation already completed at the production checkpoint:
- exact repaired ZIP validated;
- targeted mock-calibration tests passed;
- candidate and exact-ZIP compileall passed;
- candidate and exact-ZIP full pytest passed;
- automated GUI gate passed across 17 GUI-focused test files;
- GUI lifecycle invariants passed;
- GUI safe-module imports passed;
- `gui` and `draft-gui` CLI/parser smoke passed.

Live GUI commissioning:
- operator completed the supplied live commissioning workflow;
- service-layer smoke and live GUI launch completed without reported issue;
- dashboard interaction/recompute/refresh workflow completed without reported issue;
- historical deleted-client lifecycle failure was not observed;
- operator reported: "everything ran with no issues".

Evidence classification:
`OPERATOR-CONFIRMED LIVE RUNTIME COMMISSIONING`.

This is intentionally distinct from instrumented/automated log evidence. The
live commissioning conclusion is based on direct operator confirmation; the
automated release/GUI validation is separately machine-measured and already
durable.

Result:
`v0.36-repack1 = COMMISSIONED`.

The pre-v1.0A release gate is closed. v1.0A observability implementation is
`READY TO BEGIN`.

Current development boundary:
- Phase 0: COMPLETE
- v0.36 source import: COMPLETE
- v0.36-repack1 automated validation: COMPLETE
- live GUI commissioning: COMPLETE
- v1.0A observability: READY TO BEGIN / NOT YET IMPLEMENTED
<!-- FANTASY_V036_REPACK1_LIVE_GUI_COMMISSIONED_20260917_V1:END -->

<!-- FANTASY_V10A_CONTEXT_EVENTS_CHECKPOINT_20260917_V1:BEGIN -->
## v1.0A context/events checkpoint

Timestamp: `2026-09-17T12:22:28.118480-04:00`

Pre-state GitHub main:
`4e7f5277cd4a3d98378e3bdeaf8f965ab27df14b`

Checkpoint:
`v1.0A context/events slice 1`

Implemented contract:
- `src/observability/context.py`
  - frozen `RunContext`;
  - run/action correlation;
  - timezone-aware timestamps normalized to UTC;
  - release/source/config/input provenance fields;
  - week / decision-time / data-as-of / scenario / seed / CRN fields;
  - child-action derivation without mutating the parent context.
- `src/observability/registry.py`
  - immutable event registry;
  - `NORMAL`, `DIAGNOSTIC`, `TRACE`, `AUDIT` levels;
  - generic run/action events;
  - GUI lifecycle/action/service/task/state/render/refresh event names reserved exactly at the contract layer.
- `src/observability/events.py`
  - schema version 1;
  - frozen structured event envelope;
  - recursively immutable JSON-safe payload;
  - deterministic JSON rendering;
  - registry, subsystem, and required-payload validation.

No sink, logger, adapter, invariant engine, replay layer, or production call site is introduced by this checkpoint.

Validation:
- targeted observability tests: PASS (11);
- full pytest: PASS (364);
- full repository compileall: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- no existing football/model/application source file modified;
- context/event construction RNG non-interference tests: PASS;
- caller payload immutability/deep-freeze tests: PASS.

State:
`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`.

The commissioned v0.36-repack1 football/model/GUI behavior remains unchanged.
<!-- FANTASY_V10A_CONTEXT_EVENTS_CHECKPOINT_20260917_V1:END -->
