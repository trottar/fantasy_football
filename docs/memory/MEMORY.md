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

The target is not a permanently finished predictor. It is a validated adaptive
system that learns where its assumptions, uncertainty, metadata, or subsystem
representations are incomplete.

## Physics analogy

Fantasy production is modeled as a response problem:

`N_fantasy ~ L x sigma x A x epsilon`

- `L` = opportunity/exposure
- `sigma` = production/efficiency
- `A` = matchup/kinematic acceptance
- `epsilon` = fantasy scoring response

Fantasy points are downstream observables.

The physics analogy is strongest for state representation, uncertainty
propagation, measurement, residual analysis, perturbation analysis, and coupled
subsystems. It is not a claim that football obeys deterministic universal laws,
fixed constants, or equilibrium assumptions.

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

The MC is a microscope, not the theory. More samples cannot repair a wrong state
representation, response mechanism, or uncertainty model.

Priority:
1. correct state representation;
2. correct response mechanisms;
3. correct uncertainty;
4. computational sampling.

## Observability as experimental infrastructure

Observability is not merely debugging or logging. It is the experimental
measurement apparatus for the project.

Pipeline:

`raw observations -> structured evidence -> metadata assessment -> diagnostics -> model improvement -> better decisions`

It exists to support:
- measurement;
- reproducibility;
- hypothesis testing;
- closure;
- failure localization;
- evidence-supported calibration and model evolution.

Every major model addition should identify:
- claim: what stochastic process is represented;
- evidence: what observations support it;
- assumption: what uncertainty or approximation exists;
- failure mode: how the representation would be shown wrong.

## Constructive disagreement

Collaboration should optimize for scientific validity, not agreement.

Architectural proposals are hypotheses. Challenge:
- assumptions;
- implementation choices;
- analogies;
- data requirements;
- causal boundaries;
- feasibility.

Agreement is not validation.

## Historical evidence and non-stationarity

Historical football data is useful but dangerous because football is
non-stationary: schemes, coaching, rules, player roles, strategy, and data
quality change.

Do not assume:

`P(Y|X)_past ~= P(Y|X)_current`

Historical data should contribute:

`historical evidence -> contextual prior -> current evidence update`

not:

`historical data -> direct prediction`

Historical comparability should account for era, scheme, coaching, role,
opportunity profile, efficiency profile, injury context, opponent environment,
and data quality. A smaller comparable sample can be more useful than a larger
incompatible sample.

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

## v1.0A durable observability state

The v1.0A substrate has immutable run/action context, typed events, explicit
sinks/provenance, privacy/redaction, local replay evidence, bounded structural
diffs/failure bundles, subsystem adapters, correlation boundaries, and paired
non-interference/overhead gating. Direct P/D/K cross-channel nesting is
rejected; a root context may enter specialist channels independently. Default
production integration remains shadow, non-auto-emitting, and non-persistent.
Canonical detail lives in `architecture/DIAGNOSTICS_OBSERVABILITY.md`, D-013
through D-022, and their evidence records.

The commissioned production-source pilots remain deliberately narrow: final CLI
dispatch, read-only `SeasonGuiService.source_health()`, selected-MC/progress-pump
GUI task lifecycle, and page/connect/disconnect/delete correlation. They capture
no arguments, returned values, authenticated payloads, raw client IDs, or
exception messages. Observer failures/lifecycle evidence never authorize
production cancellation, retry, suppression, or result replacement.

## Durable development rules

- Current source plus fresh evidence outranks summaries; raw measurements
  outrank classifiers when they conflict.
- Never reconstruct a release from memory or claim validation that did not run.
- Preserve validated subsystem, causal, privacy, and information boundaries.
- Use one narrow hypothesis/probe/patch-or-defer loop.
- Keep secrets/authenticated raw data local.
- Meaningful checkpoints update typed durable memory in the same Git checkpoint.
- Read the complete `AGENTS.md` bootstrap; canonical decisions/evidence are
  sources, not summaries to be recursively paraphrased.
- Memory maintenance follows `MAINTENANCE.md`; detailed chronology belongs in
  dated history/evidence/investigations rather than this file.

## Human-in-the-loop repository checkpoint rule

Default actor sequence:

`assistant package -> user local run -> returned log -> assistant verification -> separate push commands -> user push -> read-only remote verification`

Prepared, local-apply, committed, pushed, remote-verified, and runtime-commissioned
states are distinct. Control-root local apply uses target predecessor contracts;
Git `HEAD`/index authority belongs to the isolated staging clone for commit/push.
Direct GitHub connector writes are not project checkpoint writes.

## Memory / handoff reconciliation

The mandatory substantial-session bootstrap is:
`AGENTS -> CURRENT -> MEMORY -> CURRENT_HANDOFF -> USER`.
`CURRENT.md` is sole active-state authority; `MEMORY.md` is curated cross-phase
knowledge; the handoff is compact transition metadata and cannot override
`CURRENT.md`. Canonical audit: `evidence/MEMORY_WORKFLOW_AUDIT_2026-09-18.md`.

## 2026 season-gated development contract

The season uses two independent clocks. **Calendar gates** protect irreversible
prospective captures/operational opportunities. **Evidence gates** authorize
diagnosis or calibration only when accumulated prospective closure supports it;
`DEFER / COLLECT MORE DATA` is a valid result. Never backfill a missed capture.

For the configured 2026 league, Weeks 1-13 are the fantasy regular season and
Weeks 14-17 are the playoff window; Week 14 is Round 1 and includes Arizona and
Dallas byes. Commission the playoff production baseline before Week 14 and freeze
major empirical calibration by default through the playoff window.

Preserve both a week-open reference capture and decision-time captures for
consequential lineup/waiver/trade/specialist actions. Detailed phase intent lives
in `docs/ROADMAP.md`, weekly dates/gates in `roadmap/SEASON_2026.md`, active
position in `roadmap/STATUS.md`, and stable v1.X rules in
`architecture/PHASE_V1_CONTEXT.md`.
