# Durable Memory

This file owns **curated durable cross-phase knowledge**. It preserves scientific
invariants, stable architectural facts, commissioned baselines, and reusable
project rules.

It does not own the active frontier, startup membership, checkpoint procedure,
session chronology, or raw validation detail. Those belong respectively to
`CURRENT.md`, `AGENTS.md`/`MAINTENANCE.md`, `patches/PATCH_PROTOCOL.md`, dated
history, and canonical evidence/investigation records.

## Project Purpose

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

The target is not a permanently finished predictor. It is an adaptive system
whose assumptions, uncertainty, metadata, and subsystem representations are
tested against prospective evidence.

## Physics Analogy

Fantasy production is modeled as a stochastic response problem:

`N_fantasy ~ L x sigma x A x epsilon`

- `L` = opportunity/exposure;
- `sigma` = production/efficiency;
- `A` = matchup/kinematic acceptance;
- `epsilon` = fantasy scoring response.

Fantasy points are downstream observables.

The analogy is strongest for state representation, uncertainty propagation,
measurement, residual analysis, perturbation analysis, and coupled subsystems.
It is not a claim that football follows deterministic universal laws or fixed
equilibrium constants.

## Specialist-Channel Architecture

Preserve:

`P ⊕ D ⊕ K`

- P = QB/RB/WR/TE player channel;
- D = DST channel;
- K = kicker channel.

Players compare only to players, defenses only to defenses, and kickers only to
kickers. Cross-channel coupling belongs only at complete-roster utility/state
boundaries.

## Counterfactual Response and Weekly State

Roster decisions are perturbations:

`Delta U = U(S + delta S) - U(S)`

Weekly state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

Use common random numbers for paired comparisons where practical. Dropped players
remain part of league state. Direct response, field response, and manager
behavior remain distinct.

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

## Historical Evidence and Non-Stationarity

Historical football data is useful but football is non-stationary: schemes,
coaching, rules, player roles, strategy, and data quality change.

Do not assume:

`P(Y|X)_past ~= P(Y|X)_current`

Historical data should contribute:

`historical evidence -> contextual prior -> current evidence update`

not:

`historical data -> direct prediction`

Comparability should account for era, scheme, coaching, role, opportunity,
efficiency, injury context, opponent environment, and data quality. A smaller
comparable sample can be more useful than a larger incompatible sample.

## Behavioral Separation

Manager acquisition/trade behavior is a stochastic behavior kernel, not football
physics. Popularity, ownership, trends, and perception may affect manager
actions but do not change intrinsic football value.

## Scientific Version Boundary

- `v0.X` = a-priori architecture; observed 2026 outcomes do not tune it.
- `v1.X` = prospective Data/MC closure and evidence-supported calibration.

Structural representation defects may be fixed when the architecture cannot
represent the real process. Empirical retuning requires accumulated evidence.
One surprising game opens an investigation; it does not justify broad retuning.

## Commissioned 0.X Baseline

The final commissioned 0.X runtime baseline is **v0.36-repack1** with internal
`VERSION = 0.36`.

Durable conclusions:

- exact v0.36 source was reconciled and imported;
- no historical exact `v0.36-fixed1` artifact/provenance was established;
- the original v0.36 release package omitted four public mock-calibration
  fixtures;
- fixture-only restoration closed the deterministic failures and full suite;
- the repaired release passed automated source/runtime/GUI validation;
- live GUI commissioning was operator-confirmed successful.

Canonical records:

- `decisions/D-010_PHASE0_FINAL_0X_AUTHORITY.md`
- `decisions/D-011_V036_REPACK1_RELEASE_GATE.md`
- `decisions/D-012_V036_REPACK1_COMMISSIONED_V10A_READY.md`
- `evidence/V036_REPACK1_VALIDATION_2026-09-17.md`
- `evidence/V036_REPACK1_LIVE_GUI_COMMISSIONING_2026-09-17.md`

## Observability as Experimental Infrastructure

Observability is the project's measurement apparatus, not merely debugging or
logging.

```text
raw observations
  -> structured evidence
  -> metadata assessment
  -> diagnostics
  -> model improvement
  -> better decisions
```

It supports measurement, reproducibility, hypothesis testing, closure, failure
localization, and evidence-supported calibration.

Every major model addition should identify:

- claim: what stochastic process is represented;
- evidence: what observations support it;
- assumption: what uncertainty or approximation exists;
- failure mode: how the representation would be shown wrong.

Diagnostics must observe rather than alter football physics, manager behavior,
random draws, recommendation authority, or GUI business logic.

## v1.0A Durable Observability Architecture

The v1.0A substrate has immutable run/action context, typed events, explicit
sinks/provenance, privacy/redaction, local replay evidence, bounded structural
diffs/failure bundles, subsystem adapters, correlation boundaries, and paired
non-interference/overhead gating.

Direct P/D/K cross-channel nesting is rejected; a root context may enter
specialist channels independently. Default production integration remains
shadow, non-auto-emitting, and non-persistent.

Commissioned production-source pilots remain deliberately narrow: final CLI
dispatch, read-only `SeasonGuiService.source_health()`, selected-MC/progress-pump
GUI task lifecycle, and page/connect/disconnect/delete correlation. They capture
no arguments, returned values, authenticated payloads, raw client IDs, or
exception messages. Observer failures/lifecycle evidence never authorize
production cancellation, retry, suppression, or result replacement.

Canonical architecture/decisions:
`architecture/DIAGNOSTICS_OBSERVABILITY.md` and D-013 through D-022.

## Phase 1A Commissioned Data-Source Shadow

The outer `sync_season_snapshot` boundary is commissioned in the
`v0.36-repack1` runtime.

The observer retains only generated correlation, boundary identity, duration,
and exception type in bounded memory. Arguments, credentials/authenticated
payloads, returned snapshot/path data, exception messages, provider internals,
and persistent sinks remain excluded.

Phase 1A is complete and runtime commissioned. Persistent evidence remains
disabled. Phase 1C P/D/K, Phase 1D market/behavior, and Phase 1E persistence
remain separately gated.

Canonical records:

- `decisions/D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT_PREFLIGHT_2026-09-21.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`

## Phase 1B Commissioned Closure Shadow

The final v0.34 `build_pregame_capture_from_context` public override is
commissioned in the `v0.36-repack1` runtime at
`subsystem.closure.capture`.

The observer reuses the bounded in-memory `ShadowRecorder`; it captures boundary
identity/correlation, duration, and exception type only. It does not retain
arguments, returned capture payloads, authenticated/private data, or exception
messages. The inherited pre-v0.34 closure implementation remains uninstrumented,
persistent evidence remains disabled, and football/model/P-D-K/manager behavior
semantics are unchanged.

Repository source checkpoint:
`29b0635218b06a9d4abe203128d426402cb1ebc8`.

Canonical records:

- `evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1B_CLOSURE_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`

Phase 1C player/DST/kicker observability remains separately gated.

## Phase 1C Channel-Boundary Audit

The initial Phase 1C source audit found that the v1.0A integration map's planned
player point, `transaction_manager.evaluate_roster_predictive`, is not a pure
player-channel boundary. Production passes complete rosters through it and its
predictive simulation includes specialist handling, including DST component
simulation. Treat it as a complete-roster utility/response surface, not
`subsystem.player`.

The current DST and K outer policy wrappers in `specialist_policy_v032.py` are
accepted as separate channel boundaries because each fixes its specialist
position (`DST` or `K`) before entering position-scoped policy evaluation.
Permitted player/specialist coupling remains confined to complete-roster
utility/state response boundaries.

Phase 1C sequencing begins with DST targeted preflight. K remains separately
gated, and player instrumentation remains blocked until a narrower QB/RB/WR/TE
production boundary is established.

Canonical evidence:
`evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`.

## 2026 Season-Gated Development Contract

The season uses two independent clocks.

**Calendar gates** protect irreversible prospective captures and operational
opportunities. **Evidence gates** authorize diagnosis or calibration only when
accumulated prospective closure supports it. `DEFER / COLLECT MORE DATA` is a
valid result.

Never backfill a missed prospective capture.

For the configured 2026 league, Weeks 1-13 are the fantasy regular season and
Weeks 14-17 are the playoff window. Commission the playoff production baseline
before Week 14 and freeze major empirical calibration by default through the
playoff window.

Preserve both a week-open reference capture and decision-time captures for
consequential lineup, waiver, trade, and specialist actions.

Canonical planning/context:

- `docs/ROADMAP.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `architecture/PHASE_V1_CONTEXT.md`

## Durable Development Rules

- Current source plus fresh direct evidence outranks summaries.
- Raw measurements outrank classifiers when they conflict.
- Never reconstruct a release from memory or claim validation that did not run.
- Preserve validated subsystem, causal, privacy, and information boundaries.
- Use one narrow hypothesis -> targeted probe -> evidence -> coherent
  patch/defer/close loop.
- Keep secrets and authenticated raw data local.
- Meaningful checkpoints update typed durable memory in the same Git checkpoint.
- Canonical evidence/decision/investigation records are sources; do not build
  summaries of summaries.
- `CURRENT.md` owns active state. This file should not accumulate checkpoint
  chronology or competing next actions.
- Startup policy belongs to `AGENTS.md`/`MAINTENANCE.md`.
- Repository checkpoint mechanics belong to `patches/PATCH_PROTOCOL.md`.
- Communication lifecycle belongs to `COMMUNICATION.md`.
- Environment/tool commands belong to `TOOLS.md`.

## Constructive Disagreement

Collaboration optimizes for scientific validity, not agreement. Architectural
proposals are hypotheses.

Challenge assumptions, implementation choices, analogies, data requirements,
causal boundaries, and feasibility. Agreement is not validation.
