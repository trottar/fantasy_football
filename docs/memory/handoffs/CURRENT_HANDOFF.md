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
