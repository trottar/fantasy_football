# Durable Memory

## Project purpose

Build a prospectively validated stochastic model of NFL fantasy production and use its state-response dynamics to make roster decisions under uncertainty.

```text
NFL physics
  -> probability distribution of fantasy outcomes
  -> league state
  -> counterfactual response
  -> decision
  -> observed Data
  -> closure
  -> knowledge
```

## Physics analogy

Fantasy production is modeled as a response problem:

`N_fantasy ~ L x sigma x A x epsilon`

- `L` = opportunity/exposure
- `sigma` = production/efficiency
- `A` = matchup/kinematic acceptance
- `epsilon` = fantasy scoring response

Fantasy points are detector output, not the fundamental process.

## Channel separation

`P ⊕ D ⊕ K`

- P = QB/RB/WR/TE player channel
- D = DST channel
- K = kicker channel

Players compare only to players; defenses only to defenses; kickers only to kickers. Cross-channel coupling occurs only at complete-roster utility boundaries.

## Counterfactual response

Roster decisions are state perturbations:

`Delta U = U(S + delta S) - U(S)`

Use common random numbers where practical. Dropped players remain part of league state. Direct response and field response remain distinct. Behavioral acquisition/acceptance probabilities are separate from football response.

## Dynamic state

`S_w = (P_w, D_w, K_w, M_w, I_w)`

Guiding question:

> What is the state, what is the response, what information is available, and what uncertainty must be propagated?

## Prospective Data/MC

Predictions are frozen before observation. Data is compared to MC later. Calibration follows diagnosis.

`screen != authority`

## Behavioral separation

Manager claim/trade behavior is a stochastic behavior kernel, not football physics. Popularity, ownership, and trend features may affect behavior/perception but must not make a player intrinsically better.

## Scientific version boundary

- `v0.X` = a-priori model architecture; no observed 2026 outcomes used for tuning.
- `v1.X` = prospective Data/MC closure and evidence-supported calibration.

Week 1 completion establishes the practical start of 1.X for data-informed work.

## Durable rules

- Current source and fresh evidence outrank summaries.
- Never reconstruct a release from memory when exact source exists.
- Never claim testing or commissioning that did not run.
- Preserve validated subsystem boundaries.
- One narrow hypothesis -> one targeted diagnostic -> fresh evidence -> inspect -> one coherent patch.
- Every meaningful code/release checkpoint updates durable memory in the same Git commit.
- Secrets and raw authenticated data remain local.

<!-- FANTASY_OBSERVABILITY_DURABLE_RULE:BEGIN -->
## First-class observability rule

Diagnostics/observability are a cross-cutting architectural subsystem, not after-the-fact print statements.

Every significant future subsystem should expose, where applicable: structured events; run/action provenance; invariant checks; bounded snapshots/failure bundles; replay/diff support; privacy/redaction; and enough context to reproduce or diagnose a recommendation change.

GUI diagnostics are included from the beginning. GUI lifecycle, action, service, background-task, render/refresh, and stale-client/state-transition failures must be diagnosable through the same correlation/provenance system.

Diagnostics must observe rather than change physics, manager behavior, random draws, recommendation authority, or GUI business logic.
<!-- FANTASY_OBSERVABILITY_DURABLE_RULE:END -->

<!-- FANTASY_MEMORY_PHASE0_FINAL_AUTHORITY_20260917:BEGIN -->
## Final 0.X authority split

Phase 0 I-001 is resolved.

Durable facts:
- exact v0.36 ZIP SHA:
  `598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`;
- local extracted v0.36 source matched the exact ZIP source surface `0/0/0`;
- two deterministic packaged-test failures were caused by four omitted
  mock-draft fixtures;
- fixture-only restoration changed targeted exits `[1,1] -> [0,0]`;
- the full v0.36 suite then passed;
- no source/config/model/physics change was required;
- therefore v0.36 is `SOURCE-VALIDATED`;
- the existing v0.36 ZIP is not a valid commissioned release artifact;
- no historical v0.36-fixed1 artifact/provenance was established;
- durable source import and repaired release creation require explicit
  production/release authorization.
<!-- FANTASY_MEMORY_PHASE0_FINAL_AUTHORITY_20260917:END -->

<!-- FANTASY_MEMORY_V036_REPACK1_20260917:BEGIN -->
## v0.36-repack1 durable facts

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
<!-- FANTASY_MEMORY_V036_REPACK1_20260917:END -->

<!-- FANTASY_MEMORY_V036_REPACK1_COMMISSIONED_20260917:BEGIN -->
## v0.36-repack1 commissioned

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

Do not reopen the v0.36 packaging/GUI commissioning investigation without new runtime evidence.
<!-- FANTASY_MEMORY_V036_REPACK1_COMMISSIONED_20260917:END -->
