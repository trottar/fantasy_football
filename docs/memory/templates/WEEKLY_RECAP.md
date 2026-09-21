# Weekly Recap / Data-MC Closure Template

This record is a prospective-closure artifact, not a hindsight reconstruction.
If a required pregame or decision-time capture is missing, record it as missing
and do not synthesize one after outcomes are known.

## Provenance

```yaml
season:
week:
fantasy_stage:
model_release:
source_commit:
model_hash:
config_hash:
input_snapshot_hash:
week_open_capture_id:
week_open_capture_time_utc:
week_open_data_as_of_utc:
observation_finalize_time_utc:
closure_generated_time_utc:
```

## Information-set integrity

- Earliest game / freeze deadline:
- Week-open capture present: YES / NO
- Any missing prospective capture:
- Any post-outcome information excluded:
- Decision-time capture IDs:
- Causality/invariant violations:

## User matchup closure

- Predicted team distribution:
- Predicted opponent distribution:
- Pregame win probability:
- Actual final score/result:
- Matchup residual / calibration note:
- Information-consistent lineup regret:

## Player-channel closure

For each relevant QB/RB/WR/TE preserve:

- prediction timestamp / data-as-of;
- predicted fantasy distribution;
- actual fantasy points;
- residual `r = D - M`;
- pull `z = (D - M) / sigma`;
- interval membership/coverage;
- active/inactive state;
- snaps/routes/participation;
- carries/targets;
- opportunity/exposure;
- production efficiency;
- TD/scoring contribution;
- matchup/interactions;
- availability probability/outcome where relevant.

Aggregate by position and useful process strata.

Do not compare players directly with DST or kickers.

## DST-channel closure

Preserve component response:

- sacks;
- interceptions;
- fumble recoveries;
- blocked kicks;
- defensive/special-teams TDs;
- safeties;
- points allowed;
- yards allowed;
- fantasy scoring response;
- residual/pull/coverage;
- matchup-state diagnostics.

DST compares only to DST.

## Kicker-channel closure

Separate opportunity from yield:

- team scoring environment;
- FG attempt opportunity;
- FG make outcome;
- distance mix;
- XP opportunity/makes;
- aggregate fantasy yield;
- residual/pull/coverage.

Kicker compares only to kicker.

## Opponent and league-wide closure

Apply the same channel decomposition where evidence exists.

Track at minimum:

- residual mean/distribution;
- MAE;
- RMSE;
- pull mean;
- pull width;
- interval coverage;
- availability Brier score;
- channel/position stratification;
- important tails/outliers.

## Market / manager-behavior ledger

Keep behavior separate from football utility.

- waiver claims and priority/order;
- fallback/contingent claims where observable;
- actual waiver resolution;
- adds/drops;
- ownership transitions;
- trades/offers where observable;
- failed/blocked actions;
- dropped-player field response;
- behavior-model probability/outcome closure.

## Regret analysis

Distinguish:

- outcome regret;
- information-consistent decision regret;
- model regret;
- transaction regret;
- lineup regret.

Do not call an action wrong merely because a lower-probability outcome occurred.

## Anomalies / investigations

For each notable discrepancy:

1. record raw measurement first;
2. link one narrow investigation;
3. classify with one or more:
   - EXPECTED_STATISTICAL_FLUCTUATION
   - MODEL_INPUT_DEFECT
   - MODEL_STRUCTURE_GAP
   - UNCERTAINTY_MISCALIBRATION
   - DATA_SOURCE_DEFECT
   - BEHAVIOR_MODEL_GAP
   - INSUFFICIENT_EVIDENCE
   - CALIBRATION_CANDIDATE

## Calibration decision

Choose explicitly:

- `NONE`
- `INVESTIGATE`
- `SHADOW_CALIBRATION`
- `AUTHORIZE_CALIBRATION`
- `DEFER / COLLECT MORE DATA`

State the evidence gate and why it passed or did not pass.

A calendar review date is not evidence.

## Negative results

Record rejected candidates, clean probes, rollbacks, insufficient-evidence
outcomes, and hypotheses that failed.

If none:

`No meaningful negative result this week.`

## Next-week consequences

- production behavior change:
- shadow experiment:
- additional capture needed:
- unresolved blocker:
- next hard calendar gate:
- next evidence review gate:

## Durable conclusions

Promote only evidence-supported cross-week conclusions to `MEMORY.md`,
`LEARNINGS.md`, architecture, or decisions. Detailed weekly measurements stay in
the canonical weekly evidence record.
