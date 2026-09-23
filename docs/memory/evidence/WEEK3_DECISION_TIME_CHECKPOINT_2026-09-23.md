# Week 3 Decision-Time Checkpoint — 2026-09-23

## Purpose

Record the causally valid Wednesday Week 3 operational state after fresh
decision-time capture, player/DST/K evaluation, recovery of missing runtime data
dependencies, and exact-values lineup reconciliation.

This evidence is observational/operational. It does not authorize v0.X tuning,
change football/model/application source, or enable the persistent observability
sink.

## Causal Inputs

Week-open reference:

- file: `pregame_2026_w03_20260922T141055Z.json`
- SHA-256:
  `82ee7e89a328930931aa88d9a0af4b5217586cbe4792d50b7b384fcf71125154`
- role: immutable Week 3 week-open prospective reference

Wednesday decision snapshot:

- file: `data/season_snapshots/20260923T175449Z/snapshot.json`
- SHA-256:
  `7e425f73c3d7c33e1bdc4378369535aba5d78092acd1af50d0411b9e32c62160`

Wednesday prospective capture:

- file:
  `data/season_predictions/closure/pregame_2026_w03_20260923T175539Z.json`
- SHA-256:
  `16111464877bbacb8425ee2c4f4edfcd88efea49581a00b9c18c085d22f2fe14`
- integrity: PASS
- measurement contract:
  `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`
- bounded cascade:
  `PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE`

The fresh capture contained all required prospective sectors and was later
preserved unchanged by recovery/reconciliation runs.

## Recovery Provenance

The repacked runtime did not contain
`data/processed/player_values_2026.csv`.

Recovery inspected local predecessor/sibling artifacts and selected the exact
predecessor copy:

- path:
  `fantasy_season_v0_35_fixed1/data/processed/player_values_2026.csv`
- SHA-256:
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`
- selection basis: `EXACT_PREDECESSOR_V035_FIXED1`
- identical sibling representation was also observed in `fantasy_season_v0_36`.

Recovery package:
`week3_current_decision_recovery_20260923_v2`.

Recovery receipt:

- pinned Wednesday snapshot: PASS
- pinned Wednesday prospective capture: PASS
- week-open reference preserved: PASS
- roster actions: PASS
- chat report: PASS
- fresh sync/capture rerun: false
- football/model/application source changed: false
- repository changed: false
- state boundary: `DECISION-TIME-CAPTURED`

Consolidated recovery report SHA-256:
`91547a4d0815b6e61b6166a44a100921a2e0fac496e6aa98472f14eba694f048`.

## Player Channel

The player transaction engine evaluated:

- 80 actionable QB/RB/WR/TE candidates;
- 12 legal player-channel drops;
- 72 initial paired actions;
- hierarchical plan: 1,024 -> 4,096 -> 16,384 universes.

All 72 actions completed SCREEN1 at 1,024 universes. The hierarchy then stopped
because no action was league-state-classification-plausible enough to justify
escalation.

HOLD baseline at SCREEN1:

- expected H2H utility: 53.58%
- current-week expected: `110.72 +/- 19.29`
- current-week nominal: 115.63
- remaining-season lineup: 105.72 points/week
- bench insurance: 2.82 points/week above replacement
- deterministic bye floor: 98.06

The highest reported action,
Xavier Hutchinson for Justice Hill, remained `NO_RESOLVED_EDGE`:

- direct paired H2H delta: +0.080 percentage points
- league-state paired utility delta: +0.072 percentage points
- league-state tie probability: 98.2%

Accepted classification:

`PLAYER_CHANNEL = HOLD / NO RESOLVED POSITIVE COUNTERFACTUAL EDGE`

Persisted runtime audit:

- `data/season_decisions/roster_actions_20260923T185830Z.json`
- `data/season_predictions/prediction_20260923T185830Z.json`

## Specialist Channels

Separate specialist-channel evaluation preserved `P ⊕ D ⊕ K`.

Accepted Wednesday classifications:

- DST: `HOLD Lions D/ST / NO_RESOLVED_EDGE`
- K: `HOLD Harrison Butker / NO_RESOLVED_EDGE`

No player-to-DST or player-to-kicker comparison authorized either decision.

## Matchup Diagnosis

Recovered `FANTASY CHAT DIAGNOSIS v0.36` on the pinned Wednesday snapshot:

- fixed win probability: 59.4%
- realistic win probability: 62.5%
- ideal-active win probability: 63.4%
- ideal-full win probability: 63.6%
- modeled team points: `117.9 +/- 22.4`
- modeled opponent points: `108.0 +/- 20.8`
- modeled margin: `+10.0 +/- 30.6`

Persisted report:

- `data/chat_reports/chat_report_20260923T190706Z.txt`
- `data/chat_reports/chat_report_20260923T190706Z.json`

## Lineup Reconciliation

A narrow successor diagnostic,
`week3_flex_reconcile_20260923_v1`, reran only `week-lineup` and `week-yields`
using:

- the exact pinned Wednesday snapshot; and
- the exact recovered predecessor player-values artifact.

No sync, capture, specialist evaluation, or heavy paired action MC was rerun.

Planning expected-value lineup:

- QB: Lamar Jackson
- RB1: Ashton Jeanty
- RB2: Jeremiyah Love
- WR1: Puka Nacua
- WR2: Carnell Tate
- TE: George Kittle
- FLEX: Mark Andrews
- K: Harrison Butker
- DST: Lions D/ST

Planning projection total: 123.37.
Availability-weighted total: 118.08.

Mark Andrews:

- operational mean: 10.61
- P(active): 99.5%

Rashid Shaheed:

- operational mean: 10.26
- P(active): 99.5%

Therefore the exact-values expected lineup resolves the prior fallback
disagreement in favor of Mark Andrews at FLEX.

## Live Contingency

Puka Nacua is the principal Wednesday status uncertainty:

- operational mean: 19.06
- provisional P(active): 75.0%
- game-status source: ESPN/status fallback rather than official practice evidence

If Puka Nacua is OUT, the exact-values one-player contingency is:

- WR1/WR2: Carnell Tate and Rashid Shaheed
- FLEX: J.K. Dobbins
- contingency nominal total: 114.72

J.K. Dobbins itself is also modeled at provisional 75% active. If Dobbins is OUT
while Puka remains available, Mark Andrews remains the expected FLEX.

## Known Limitations

- NFL.com injury-page rows were zero in the recovered Wednesday report; official
  practice evidence was unavailable from that feed.
- v0.27 practice likelihood ratios remain uncalibrated priors.
- Current-starter v0.28 interaction grids were missing/unavailable; base MC/K
  fallback was active.
- Availability probabilities remain provisional.
- No completed prospective v0.29 fantasy-yield closure observations existed at
  this decision point.
- No observed Week 3 outcome may be used to rewrite this Wednesday state or tune
  v0.X.

## Next Gate

Preserve the Wednesday snapshot/capture and all audits unchanged.

At the next material injury/status update, or before the relevant Sunday lineup
locks if no earlier material change occurs:

1. perform a fresh season sync;
2. freeze a new prospective decision-time capture;
3. re-evaluate the lineup, especially Puka Nacua;
4. rerun transaction/specialist channels only if the changed state makes them
   decision-relevant.

Phase 1D read-only engineering may proceed between calendar gates but must not
displace the next prospective capture.
