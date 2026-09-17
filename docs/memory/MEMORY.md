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
