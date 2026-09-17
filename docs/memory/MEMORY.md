# Durable Memory

## Project purpose

Build a prospectively validated stochastic model of NFL fantasy production and
use state-response dynamics to make roster decisions under uncertainty.

```text
NFL process
  -> distribution of fantasy outcomes
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

Fantasy points are downstream observables.

## Channel architecture

`P ⊕ D ⊕ K`

- P = QB/RB/WR/TE player channel
- D = DST channel
- K = kicker channel

Players compare only to players; defenses only to defenses; kickers only to
kickers. Cross-channel coupling occurs only at complete-roster utility/state
boundaries.

## Counterfactual response and state

Roster decisions are perturbations:

`Delta U = U(S + delta S) - U(S)`

Weekly state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

Use common random numbers where practical. Dropped players remain part of league
state. Direct response, field response, and manager behavior remain distinct.

Guiding question:

> What is the state, what is the response, what information is available, and
> what uncertainty must be propagated?

## Causality and Data/MC

Predictions are frozen before outcomes are observed.

Use:

`MC -> Data -> closure -> diagnosis -> calibration`

Only decision-time information may influence prospective actions.

`screen != authority`

Raw observations are immutable evidence. Derived/calibrated state remains
separate.

## Behavioral separation

Manager acquisition/trade behavior is a stochastic behavior kernel, not
football physics. Popularity, ownership, trends, and perception may affect
manager actions but do not change intrinsic football value.

## Scientific version boundary

- `v0.X` = a-priori architecture; observed 2026 outcomes do not tune it.
- `v1.X` = prospective Data/MC closure and evidence-supported calibration.

Structural representation defects may be fixed when the architecture cannot
represent the real process. Empirical retuning requires accumulated evidence.

## Commissioned 0.X baseline

The final commissioned 0.X runtime baseline is **v0.36-repack1** with internal
`VERSION = 0.36`.

Durable conclusions:
- exact v0.36 source was reconciled and imported;
- no historical exact `v0.36-fixed1` artifact/provenance was established;
- the original v0.36 ZIP had a packaging-only omission of four public
  mock-calibration fixtures;
- fixture-only restoration closed both deterministic failures and the full
  suite;
- the repaired exact release passed automated source/runtime/GUI validation;
- live GUI commissioning was operator-confirmed successful.

Canonical details:
- `decisions/D-010_PHASE0_FINAL_0X_AUTHORITY.md`
- `decisions/D-011_V036_REPACK1_RELEASE_GATE.md`
- `decisions/D-012_V036_REPACK1_COMMISSIONED_V10A_READY.md`
- `evidence/V036_REPACK1_VALIDATION_2026-09-17.md`
- `evidence/V036_REPACK1_LIVE_GUI_COMMISSIONING_2026-09-17.md`

## First-class observability rule

Diagnostics/observability are a cross-cutting subsystem, not after-the-fact
print statements.

Significant future subsystems should expose, where applicable:
- structured events;
- run/action provenance;
- invariant checks;
- bounded snapshots/failure bundles;
- replay/diff support;
- privacy/redaction;
- enough context to reproduce or diagnose recommendation changes.

GUI diagnostics are part of the same system from the beginning.

Diagnostics must observe rather than alter physics, manager behavior, random
draws, recommendation authority, or GUI business logic.

## v1.0A durable contract

Checkpoint `fd829ac829e9ffddd38c14e9bca9cd3eaa6a96e3` established:
- frozen `RunContext`;
- run/action correlation;
- release/source/config/input provenance fields;
- schema-versioned immutable structured events;
- immutable event registry;
- `NORMAL`, `DIAGNOSTIC`, `TRACE`, `AUDIT` levels;
- generic run/action events;
- reserved GUI lifecycle/action/service/task/state/render/refresh event names.

The contract is test-validated but is not yet integrated into production call
sites.

Canonical decision/evidence:
- `decisions/D-013_V10A_CONTEXT_EVENT_CONTRACT.md`
- `evidence/V10A_CONTEXT_EVENTS_2026-09-17.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`


## v1.0A sinks/provenance durable contract

Checkpoint `a4e84ed5c1433e29292b53b4e7d62bbb3b255386` established:
- explicit thread-safe memory, JSONL, human-text, and fanout sink contracts;
- human-text payload omission by default;
- no hidden global logger or automatic production emission;
- exact-byte SHA-256 and canonical semantic JSON hashing;
- release version + Git HEAD/tracked-dirty source provenance;
- frozen `SourceProvenance` compatible with `RunContext`;
- persistent private/authenticated runtime logging remains blocked until the
  redaction contract is implemented and tested.

The slice passed 22 targeted observability tests, 375 full repository tests,
full compileall, `git diff --check`, and non-interference/privacy-oriented unit
tests.

Canonical decision/evidence:
- `decisions/D-014_V10A_SINKS_PROVENANCE.md`
- `evidence/V10A_SINKS_PROVENANCE_2026-09-17.md`

## Durable development rules

- Current source plus fresh evidence outranks summaries.
- Raw measurements outrank classifiers when they conflict.
- Never reconstruct a release from memory when exact source exists.
- Never claim testing or commissioning that did not occur.
- Preserve validated subsystem boundaries.
- Use one narrow hypothesis/probe/patch loop.
- Preserve causal information boundaries.
- Keep secrets and authenticated raw data local.
- Meaningful checkpoints update durable memory in the same repository
  checkpoint.
- Memory maintenance follows `MAINTENANCE.md`.

<!-- FANTASY_MEMORY_V10A_SNAPSHOT_REPLAY_DIFF_20260917:BEGIN -->
## v1.0A replay-evidence contract

The observability substrate includes local redacted fixed-member snapshot
bundles, exact-byte integrity verification, immutable evidence loading, and
bounded redacted structural diffing. This is not computation replay and is not
integrated into production call sites.
<!-- FANTASY_MEMORY_V10A_SNAPSHOT_REPLAY_DIFF_20260917:END -->

<!-- FANTASY_MEMORY_V10A_FAILURE_BUNDLE_20260917:BEGIN -->
## v1.0A failure-bundle contract

The observability substrate includes bounded, privacy-safe local failure
bundles. Exception messages are omitted by default; stack frames retain only
file basenames/function/line; events/invariants are bounded; structured
state/reproduction/effects are redacted; exact-byte integrity is verified
before load. Project-file modification state remains distinct from runtime side
effects. Automatic capture and production emission remain disabled.
<!-- FANTASY_MEMORY_V10A_FAILURE_BUNDLE_20260917:END -->

<!-- FANTASY_MEMORY_V10A_ADAPTERS_CORRELATION_20260917:BEGIN -->
## v1.0A subsystem adapters and correlation

The observability substrate includes opt-in subsystem adapters and typed
CLI/service/background-task correlation boundaries. They reuse immutable
`RunContext` action parentage and generic action events, own no sink, and emit
nothing automatically. Direct P/D/K cross-channel nesting is rejected while a
root observability context may enter each specialist channel independently.
<!-- FANTASY_MEMORY_V10A_ADAPTERS_CORRELATION_20260917:END -->

<!-- FANTASY_MEMORY_V10A_INTEGRATION_GATE_20260917:BEGIN -->
## v1.0A production-integration gate

The observability substrate includes a repository-grounded shadow integration
plan and a paired non-interference/overhead benchmark gate. Default integration
points are non-auto-emitting and non-persistent. The benchmark compares baseline
and observed behavior from the same captured probe state, verifies result or
exception-type equivalence, compares/restores Python RNG and caller-supplied
state probes, and applies absolute/relative overhead budgets without persisting
returned values or exception messages.
<!-- FANTASY_MEMORY_V10A_INTEGRATION_GATE_20260917:END -->
