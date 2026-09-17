# Data/MC Closure Architecture

## Continuous outputs

For prediction `M_i`, observation `D_i`, uncertainty `sigma_i`:

- residual: `r_i = D_i - M_i`
- pull: `z_i = (D_i - M_i) / sigma_i`

Track:
- mean residual
- MAE
- RMSE
- median residual
- pull mean
- pull RMS/width
- 50/68/90/95% interval coverage

Add CRPS/PIT when full distributions are consistently available.

## Availability

For active probability `p_active` and observed binary state `y`:

`Brier = (p_active - y)^2`

## Player decomposition

Separate:
- availability
- snaps/routes/participation
- carries/targets
- production efficiency
- TD/scoring response
- matchup effects
- final fantasy score

## Anomaly classes

- `EXPECTED_STATISTICAL_FLUCTUATION`
- `MODEL_INPUT_DEFECT`
- `MODEL_STRUCTURE_GAP`
- `UNCERTAINTY_MISCALIBRATION`
- `DATA_SOURCE_DEFECT`
- `BEHAVIOR_MODEL_GAP`
- `INSUFFICIENT_EVIDENCE`
- `CALIBRATION_CANDIDATE`

## Regret taxonomy

1. Outcome regret — hindsight best lineup; descriptive only.
2. Information-consistent decision regret — pre-lock information only; tests policy.
3. Model regret — distributions/inputs systematically wrong; tests physics.
