# Weekly Recap Template

## Metadata

```yaml
season:
week:
model_release:
pregame_capture_id:
pregame_capture_time_utc:
observation_finalize_time_utc:
```

## User matchup

- Predicted team distribution:
- Predicted opponent distribution:
- Pregame win probability:
- Actual final score/result:

## Player-channel closure

For each relevant player:
- predicted fantasy distribution
- actual fantasy points
- residual/pull
- active/inactive state
- snaps/routes/participation
- carries/targets
- efficiency
- TD/scoring contribution
- matchup/interactions

## DST closure

- sacks
- INT
- fumble recoveries
- defensive TDs
- points allowed
- yards allowed
- fantasy scoring response

## Kicker closure

- team scoring environment
- FG attempts/makes/distances
- XP opportunities/makes
- aggregate fantasy yield

## Opponent closure

Apply the same decomposition to the opposing fantasy roster.

## League-wide closure

- all rostered QB/RB/WR/TE residual distributions
- coverage diagnostics
- availability Brier metrics
- DST/K summaries

## Market/behavior ledger

- waiver claims
- adds/drops
- trades
- failed/blocked actions where observable
- manager behavior-model comparisons

## Regret analysis

- outcome regret
- information-consistent decision regret
- model regret

## Anomalies/investigations

Classify each notable discrepancy and link to an investigation.

## Durable conclusions

Only evidence-supported conclusions should be promoted to `MEMORY.md` or decision records.
