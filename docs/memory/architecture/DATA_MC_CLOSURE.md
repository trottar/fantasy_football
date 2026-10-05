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

## Historical Counterfactual Replay

After ordinary prospective closure, completed weeks may enter the replay
laboratory defined by `HISTORICAL_COUNTERFACTUAL_REPLAY.md`.

Replay uses a two-phase firewall: blind predictive replay freezes candidate
predictions, uncertainty, rankings, and the model-preferred action before
observed outcomes are attached. Phase B then computes descriptive oracle and
regret metrics.

A causal-input replay requires every material decision input/dependency to be
historically decision-time-valid; otherwise classify it as reconstructed
retrospective replay. Neither mode is a backfilled prospective capture.

Extend the regret taxonomy with matchup-flip opportunity,
actual-vs-model-preferred regret, actual-vs-oracle regret, model-vs-oracle
regret, predicted-versus-realized counterfactual response, and P/D/K/action-family
decomposition.

Replay findings may justify structural investigations and regression tests. They
may not empirically tune v0.X.
