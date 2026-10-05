# Historical Counterfactual Replay / Regret Laboratory

## Purpose

After each completed fantasy week, use the project's validated decision machinery
to replay prior decision states and measure counterfactual response, regret,
search coverage, and structural correctness without converting hindsight into
prospective evidence or v0.X tuning data.

The central question is:

> Given a specified historical information state, what decisions does the current
> machinery produce, what response did it predict, what happened under observed
> outcomes, and is any discrepancy structural or statistical?

## Scientific Boundary

Historical replay is retrospective analysis. Even when all replay inputs are
genuinely frozen at the historical decision time, a replay run performed later is
not a contemporaneous prospective decision and must never be relabeled as one.

Observed 2026 outcomes may reveal structural contradictions in v0.X. They may not
be used to tune v0.X coefficients, priors, thresholds, weights, or decision
parameters to improve historical wins.

Allowed iteration in v0.X:

`replay -> structural contradiction -> targeted diagnosis -> structural fix -> replay regression`

Prohibited iteration in v0.X:

`observed result -> parameter tweak -> replay until historical outcome improves`

## Replay Modes

### `CAUSAL_FROZEN_REPLAY`

Use only decision-driving inputs that are genuine historical decision-time
artifacts or are otherwise proven to have been available at that time.

Required provenance includes the historical state plus every material dependency
used by the replayed authority: roster/market state, lock and transaction state,
availability evidence, league/model configuration, value/model dependencies, and
any other decision inputs.

A frozen snapshot alone does not establish this mode if another material input was
reconstructed or substituted after outcomes.

This mode may test current policy and structural machinery against a causally
bounded historical input state. It is still retrospective replay evidence, not a
new prospective capture.

### `RECONSTRUCTED_RETROSPECTIVE_REPLAY`

Use when any material replay input is reconstructed, substituted, or cannot be
proved decision-time-valid.

The receipt must explicitly report reconstructed/missing fields and possible
information leakage. This mode may test mechanics, search coverage, legality,
state representation, and structural behavior. It may not support prospective
performance claims or empirical calibration.

## Two-Phase Outcome Firewall

Every replay run has two phases.

### Phase A - blind predictive replay

1. select and validate the historical input state;
2. classify replay mode before evaluation;
3. enumerate the complete legal action space supported by the weekly contract;
4. evaluate candidates with the current commissioned response machinery;
5. freeze candidate predictions, uncertainty, rankings, and model-preferred
   action;
6. record replay-engine/source/dependency identities.

Observed outcomes must not be available to candidate generation, screening,
predictive evaluation, ranking, or model-action selection.

### Phase B - observed-outcome attachment

Only after Phase A is immutable:

1. attach actual historical outcomes;
2. score the actual historical state;
3. score the frozen model-preferred counterfactual;
4. identify the hindsight oracle-best feasible counterfactual;
5. calculate regret and matchup-flip diagnostics;
6. classify discrepancies.

The oracle is descriptive hindsight only and never decision authority.

## Action-Space Contract

Replay should cover the same league-legal families as the weekly decision
contract when the historical state supports them:

- lineup / availability;
- QB/RB/WR/TE waiver and free-agent actions;
- DST actions;
- kicker actions;
- IR/reserve/open-slot/injury replacement;
- one-for-one player trades;
- supported multi-player and unequal packages;
- specialist-inclusive trades;
- explicit post-transaction drops, fills, roster legality, locks, waiver state,
  and effective timing.

Preserve `P ⊕ D ⊕ K` inside valuation. Cross-channel composition occurs only at
the complete-roster state boundary.

Cheap screens may generate candidates; uncertainty-aware predictive authority
must authorize model decisions.

## Comparator States

For each replayable decision point, preserve three distinct states:

1. **Historical actual** - what the roster/manager actually did.
2. **Model-preferred replay** - the action selected by frozen Phase-A replay.
3. **Oracle-best feasible** - the best realized outcome among historically
   feasible candidates, computed only in Phase B.

The oracle establishes a descriptive upper bound. Failure to select the oracle is
not automatically a model defect.

## Metrics

Where supported, record:

- predicted `Delta U`;
- predicted current-week and season response;
- uncertainty intervals;
- `P(better)` and matchup-win-probability change;
- realized counterfactual score delta;
- actual versus model-preferred result;
- actual versus oracle result;
- model-preferred versus oracle result;
- whether any feasible action would have flipped the historical matchup;
- information-consistent decision regret;
- outcome regret;
- predictive/model residuals;
- decomposition by P, D, K, lineup, waiver, IR, trade, and specialist family.

Use common random numbers for paired comparisons where practical.

## Diagnostic Classification

Replay findings may be classified as:

- `EXPECTED_STATISTICAL_FLUCTUATION`;
- `MODEL_INPUT_DEFECT`;
- `MODEL_STRUCTURE_GAP`;
- `UNCERTAINTY_MISCALIBRATION`;
- `DATA_SOURCE_DEFECT`;
- `BEHAVIOR_MODEL_GAP`;
- `SEARCH_COVERAGE_GAP`;
- `STATE_REPRESENTATION_GAP`;
- `TRANSACTION_TIMING_GAP`;
- `LEGALITY_CONSTRAINT_GAP`;
- `INSUFFICIENT_EVIDENCE`;
- `CALIBRATION_CANDIDATE`.

A `CALIBRATION_CANDIDATE` is an investigation label only while v0.X remains
frozen against 2026 empirical tuning.

## Regression Use

Every confirmed structural defect found by replay should produce a minimal
regression fixture or replay scenario before closure. Old replay weeks therefore
become an expanding integration test bench for corrected infrastructure.

Do not change an old raw outcome or frozen historical artifact. Derived replay
receipts may be regenerated under newer commissioned code, but must record the
replay-engine identity and remain separate from original evidence.

## Weekly Procedure

After each fantasy week is complete:

1. freeze raw outcomes;
2. perform ordinary Data/MC closure against genuine prospective captures;
3. run Phase-A/Phase-B replay for the just-completed week;
4. add confirmed structural scenarios to the replay regression suite;
5. rerun prior structural regression scenarios under any changed decision
   machinery;
6. summarize regret, matchup-flip opportunities, and anomaly classifications;
7. open narrow investigations for structural contradictions;
8. keep empirical tuning gated by the v0.X/v1.X evidence boundary.

The cumulative Weeks 1..N replay laboratory is a development/diagnostic surface.
It never replaces prospective Week N+1 capture and decision authority.
