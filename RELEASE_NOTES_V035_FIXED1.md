# v0.35-fixed1 — Predictive confirmation for temporal player-state transitions

## Commissioning defect corrected

The v0.35 live temporal path exposed a hierarchy violation: an expected-lineup Pareto screen could directly change future player membership. Because that screen omits the mature paired predictive H2H response, it could authorize aggressive future swaps that the commissioned player channel itself would not resolve.

fixed1 restores the established screen -> MC confirmation hierarchy.

## Authoritative future transaction rule

For week w > current week:

1. Generate a small deterministic expected-lineup Pareto frontier from guaranteed FREEAGENTs.
2. Re-evaluate only that frontier with the existing player predictive MC under common random numbers.
3. Compute paired H2H utility from week w onward against the same opponent universes.
4. Require the existing ACTIONABLE_EDGE or POSSIBLE_EDGE classification.
5. Require non-negative expected points response in the decision week.
6. Only then change P_w.

The deterministic screen is never authoritative.

## Physics boundary

This remains the first-order self-player state evolution of v0.35. Other managers' future player claims and post-perturbation transaction cascades remain frozen and are reserved for v0.36. No 2026 game outcomes are used for tuning.
