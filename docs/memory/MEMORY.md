# Durable Memory

This file owns curated durable cross-phase knowledge: scientific invariants,
stable architecture, commissioned baselines, and reusable project rules.

It does not own active state, transfer state, checkpoint procedure, or detailed
chronology. Those belong to `CURRENT.md`, `handoffs/CURRENT_HANDOFF.md`,
`patches/PATCH_PROTOCOL.md`, canonical evidence/investigations, and dated memory.

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

The target is an adaptive system whose assumptions, uncertainty, metadata, and
subsystem representations are tested against prospective evidence.

## Physics Analogy

Fantasy production is modeled as a stochastic response problem:

`N_fantasy ~ L x sigma x A x epsilon`

- `L` = opportunity/exposure;
- `sigma` = production/efficiency;
- `A` = matchup/kinematic acceptance;
- `epsilon` = fantasy-scoring response.

Fantasy points are downstream observables. The analogy is strongest for state
representation, uncertainty propagation, measurement, residual analysis,
perturbation analysis, and coupled subsystems.

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

Use common random numbers for paired comparisons where practical. Dropped
players remain part of league state. Direct response, field response, and
manager behavior remain distinct.

Guiding question:

> What is the state, what is the response, what information is available, and
> what uncertainty must be propagated?

## Causality and Data/MC

Predictions are frozen before outcomes are observed.

`MC -> Data -> closure -> diagnosis -> calibration`

Only decision-time information may influence prospective actions.

`screen != authority`

Raw observations are immutable evidence. Derived/calibrated state remains
separate.

The MC is a microscope, not the theory. More samples cannot repair a wrong state
representation, response mechanism, or uncertainty model. Priority is correct
state, response, uncertainty, then sampling.

## Historical Evidence and Non-Stationarity

Football is non-stationary. Historical evidence contributes as contextual prior
information rather than direct current truth.

Comparability should account for era, scheme, coaching, role, opportunity,
efficiency, injury context, opponent environment, and data quality.

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
logging. It supports measurement, reproducibility, hypothesis testing, closure,
failure localization, and evidence-supported calibration.

Every major model addition should identify its claim, evidence, assumptions, and
failure mode.

Diagnostics must observe rather than alter football physics, manager behavior,
random draws, recommendation authority, or GUI business logic.

## v1.0A Durable Observability Architecture

The substrate has immutable run/action context, typed events, explicit
sinks/provenance, privacy/redaction, local replay evidence, bounded structural
diffs/failure bundles, subsystem adapters, correlation boundaries, and paired
non-interference/overhead gating.

Direct P/D/K cross-channel nesting is rejected; a root context may enter
specialist channels independently. Production integration remains shadow and
non-persistent unless separately authorized.

Existing narrow production observers capture correlation/boundary/timing and
exception type only where applicable; they do not retain arguments, returned
values, authenticated payloads, raw client IDs, or exception messages. Observer
failure never authorizes cancellation, retry, suppression, or result
replacement.

Canonical architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`.

## Commissioned v1.0A Slices

### Phase 1A — data-source season sync

The outer `sync_season_snapshot` boundary is runtime commissioned. The observer
is bounded and in-memory only. Authenticated inputs, returned snapshot/path
content, provider internals, and persistent sinks remain excluded.

Canonical records:

- `decisions/D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT_PREFLIGHT_2026-09-21.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`

### Phase 1B — closure capture

The final v0.34 `build_pregame_capture_from_context` public override is runtime
commissioned at `subsystem.closure.capture`. The inherited pre-v0.34
implementation remains uninstrumented. Persistent evidence remains disabled.

Canonical records:

- `evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1B_CLOSURE_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`

### Phase 1C — specialist and player-channel boundaries

The outer specialist wrappers in `specialist_policy_v032.py` are the accepted
separate DST and K boundaries:

- DST: `evaluate_defense_channel` at `subsystem.dst.channel`;
- K: `evaluate_kicker_channel` at `subsystem.k.channel`.

Both are source-published and runtime-commissioned with bounded in-memory
observation and persistent evidence disabled.

`transaction_manager.evaluate_roster_predictive` is durably rejected as a pure
player boundary because it carries complete-roster P/D/K response machinery.

Read-only discovery found no single production-wide shared QB/RB/WR/TE wrapper
spanning CLI and GUI action evaluation. The accepted player-only perturbation
surfaces are:

- CLI: `transaction_manager.evaluate_actions`
  at `subsystem.player.evaluate_actions`;
- GUI: `SeasonGuiService.evaluate_single_add_drop`
  at `subsystem.player.evaluate_single_add_drop`.

Both player surfaces are now source-published and runtime-commissioned with the
same bounded in-memory, fail-open, privacy-preserving shadow contract. Paired
runtime probing confirmed output/exception equivalence, Python/NumPy RNG and
mutable-state non-interference, structure/privacy gates, and bounded overhead.
Persistent evidence remains disabled.

No shared football-production wrapper was introduced. Shared observability
support may be reused, but production boundaries remain dictated by the
football/application architecture.

Canonical records:

- `evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `evidence/PHASE1C_K_TARGETED_PREFLIGHT_2026-09-22.md`
- `evidence/PHASE1C_K_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_K_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_BOUNDARY_DISCOVERY_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_PUBLICATION_RECOVERY_2026-09-23.md`
- `evidence/PHASE1C_PLAYER_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`

## 2026 Season-Gated Development Contract

Calendar gates protect irreversible prospective captures and operational
opportunities. Evidence gates authorize diagnosis or calibration only when
accumulated prospective closure supports it. `DEFER / COLLECT MORE DATA` is a
valid result.

Never backfill a missed prospective capture. Preserve both a week-open reference
capture and decision-time captures for consequential lineup, waiver, trade, and
specialist actions.

For the configured league, Weeks 1-13 are the fantasy regular season and Weeks
14-17 are the playoff window. Major empirical calibration is frozen by default
through the playoff window.

Canonical planning:

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
- Canonical evidence/decision/investigation records are sources; avoid summaries
  of summaries.
- `CURRENT.md` owns active state.
- Detailed checkpoint chronology belongs in dated memory/evidence, not here.
- Startup policy belongs to `AGENTS.md`/`MAINTENANCE.md`.
- Repository checkpoint mechanics belong to `patches/PATCH_PROTOCOL.md`.
- Communication lifecycle belongs to `COMMUNICATION.md`.
- Environment/tool commands belong to `TOOLS.md`.

## Constructive Disagreement

Collaboration optimizes for scientific validity, not agreement. Architectural
proposals are hypotheses; challenge assumptions, implementation choices,
analogies, data requirements, causal boundaries, and feasibility.
