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

<!-- FANTASY_HANDOFF_V10A_OBSERVABILITY_START:BEGIN -->
## 2026-09-17 transition: Phase 0 evidence + v1.0A start

Phase 0 v1.4 produced valid raw measurements but an invalid high-level classifier. The classifier is superseded because generic `fixed1` name matching could classify the known v0.35-fixed1 baseline artifacts as evidence of v0.36-fixed1. Preserve the raw measurements; do not infer final authority from that classifier.

Final 0.X authority remains deferred pending direct inspection of the v1.4 sanitized evidence bundle and exact v0.36/fixed1 provenance.

In parallel, v1.0A observability design is active. Source integration remains development-only until the final 0.X tree is frozen.

The observability substrate must be modular and include GUI diagnostics from the start. Later phases should plug into one shared run/event/provenance/invariant/failure/replay system rather than inventing subsystem-specific debug scripts.
<!-- FANTASY_HANDOFF_V10A_OBSERVABILITY_START:END -->

<!-- FANTASY_PRIVYHUB_STYLE_HANDOFF:BEGIN -->
## Checkpoint authorization / delivery boundary

Use PrivyHub-style ZIP checkpoints.

- Push durable memory as part of the checkpoint ZIP.
- Diagnostic/probe/observability tools may be developed and pushed with memory.
- Do not use direct GitHub connector writes for project checkpoints.
- Do not modify football/model/application/business logic until the user explicitly authorizes it at the end of the checkpoint.

This rule supersedes earlier generic read-only GitHub wording where it conflicts.
<!-- FANTASY_PRIVYHUB_STYLE_HANDOFF:END -->

<!-- FANTASY_I005_MANIFEST_HANDOFF:BEGIN -->
## I-005 manifest representation repair

The PrivyHub-style memory/diagnostic workflow is successfully checkpointed at
`4b979b4c105f60bdf4f3467b9448b370cf9ce6a2`.

A follow-up audit found that the memory manifest still describes Windows
worktree bytes rather than committed Git blob bytes due line-ending
normalization. Memory content and scope are valid; exact manifest integrity
semantics need a narrow tooling repair.

The successor generator must hash staged Git index bytes and validate against
committed `HEAD` bytes before push.
<!-- FANTASY_I005_MANIFEST_HANDOFF:END -->

<!-- FANTASY_MEMORY_INFRA_READY_HANDOFF:BEGIN -->
## Memory / diagnostics infrastructure ready

As of checkpoint `243e4ee4906f42582a5603170e7d7c73095c9dac`,
the PrivyHub-style memory/diagnostic checkpoint machinery is validated and ready.

I-005 is resolved. The manifest now describes staged/committed Git blob bytes,
not Windows worktree bytes.

Continue with:
1. Phase 0 raw evidence review and final 0.X lineage freeze;
2. prospective Week 2 state capture while causally valid;
3. v1.0A observability tooling/substrate work;
4. no football/model/application implementation until explicit user
   authorization at the checkpoint boundary.
<!-- FANTASY_MEMORY_INFRA_READY_HANDOFF:END -->

<!-- FANTASY_I001_V2_HANDOFF:BEGIN -->
## I-001 v2 authoritative-artifact review

Result: `V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED`
Authority: `V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`

The exact local v0.36 ZIP identifies as VERSION 0.36; no exact v0.36-fixed1 artifact or specific v0.36-fixed1 provenance was established.

Predecessor v1 failed before modification because its required prior result ZIP
was missing. v2 removed that dependency and reconstructed evidence directly.

Proceed only with the narrow successor implied by this classification.
<!-- FANTASY_I001_V2_HANDOFF:END -->

<!-- FANTASY_HANDOFF_DIAGNOSTIC_QA_HOLD:BEGIN -->
## Diagnostic QA checkpoint before GUI-lineage successor

Do not rerun `fantasy_phase0_gui_lineage_isolation_20260917_v1`.

It failed because `run_release_checks()` referenced `sys` without importing it.
The failure occurred before memory commit/push and before any production-source
modification.

Before the next GUI-lineage diagnostic:
- enforce the diagnostic QA release gate;
- use a new unique ZIP/extraction name;
- execute release-check helper branches in package QA;
- audit undefined globals;
- enforce cleanup with `finally`;
- treat launcher/non-GUI divergence conservatively;
- support safe `ALREADY APPLIED` behavior.
<!-- FANTASY_HANDOFF_DIAGNOSTIC_QA_HOLD:END -->

<!-- FANTASY_GUI_LINEAGE_V2_INVALID_HANDOFF:BEGIN -->
## GUI-lineage v2 status

Do not reuse `fantasy_phase0_gui_lineage_isolation_20260917_v2.zip`.

It is `INVALID / SUPERSEDED` tooling because its generated evidence failed
`git diff --cached --check`.

Retain only its measured evidence:
- local extracted v0.36 equals exact v0.36 on compared source surface;
- `compileall=0`;
- `pytest=1` with unresolved cause;
- evidence ZIP SHA:
  `e64094a5b5da9205f65b18176c641b08dec9bf4116dc128e425755fbe77587c0`.

Next narrow task: inspect/reproduce the exact v0.36 pytest failure and close the
final Phase 0 authority question. A successor tool must pass rendered-memory
whitespace QA before delivery.
<!-- FANTASY_GUI_LINEAGE_V2_INVALID_HANDOFF:END -->

<!-- FANTASY_V036_PYTEST_DIAGNOSIS_HANDOFF_20260917:BEGIN -->
## Phase 0 pytest diagnosis result

Diagnosis: `V036_SPECIFIC_DETERMINISTIC_TEST_REGRESSION`

Exact v0.35-fixed1 passes in the same Python environment, while 2 v0.36 failing node(s) remain failing when rerun directly.

Exact v0.36 failing nodes:
- `tests/test_mock_calibration.py::test_packaged_full_mock_is_complete_and_has_16_user_picks`
- `tests/test_mock_calibration.py::test_mock_inventory_sees_first_calibration_sample`

Exact v0.35-fixed1 failing nodes:
(none parsed)

Use the captured evidence before making the final 0.X authority/commissioning
decision. Do not reinterpret `pytest=1` without the recorded node-level result.
<!-- FANTASY_V036_PYTEST_DIAGNOSIS_HANDOFF_20260917:END -->

<!-- FANTASY_V036_FIXTURE_RESTORATION_HANDOFF_20260917:BEGIN -->
## Phase 0 fixture-restoration result

Classification: `V036_RELEASE_PACKAGING_FIXTURE_REGRESSION_CONFIRMED`

The two deterministic v0.36 failures disappear after restoring only the four missing baseline mock-draft fixtures, and the full v0.36 suite then passes.

Use this result to decide whether v0.36 requires only a release-packaging repair
or whether broader source correction remains necessary.

No production source was changed.
<!-- FANTASY_V036_FIXTURE_RESTORATION_HANDOFF_20260917:END -->

<!-- FANTASY_HANDOFF_PHASE0_FINAL_AUTHORITY_20260917:BEGIN -->
## Phase 0 complete — production boundary reached

I-001 final 0.X reconciliation is resolved.

Use this authority split:
- v0.36 source: `SOURCE-VALIDATED / NOT YET DURABLY IMPORTED`;
- existing v0.36 ZIP: `INVALID AS COMMISSIONED RELEASE ARTIFACT`;
- historical v0.36-fixed1: `NOT ESTABLISHED`.

Do not continue probing the same lineage issue without new evidence.

Next production task, only after explicit authorization:
1. construct a packaging-only repaired v0.36-derived release;
2. include the four required public mock-calibration fixtures;
3. make no football/model/config behavior changes;
4. run targeted tests, full pytest, compileall, and exact-ZIP validation;
5. import the validated v0.36 source/release into durable Git history using the
   established checkpoint workflow;
6. commission the repaired artifact separately from source validation.

After that, proceed to the v1.0A observability substrate.
<!-- FANTASY_HANDOFF_PHASE0_FINAL_AUTHORITY_20260917:END -->

<!-- FANTASY_HANDOFF_V036_REPACK1_20260917:BEGIN -->
## Pre-v1.0A boundary

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

Next action: live GUI commissioning against current local season data. Do not begin v1.0A until that passes.
<!-- FANTASY_HANDOFF_V036_REPACK1_20260917:END -->

<!-- FANTASY_HANDOFF_V10A_READY_20260917:BEGIN -->
## v1.0A start boundary

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

Next narrow implementation target:
establish the v1.0A observability substrate without changing football decision semantics. Begin with immutable run/action context and structured event contracts, then sinks/invariants/provenance/snapshot-replay in coherent checkpoints.
<!-- FANTASY_HANDOFF_V10A_READY_20260917:END -->
