# Physics Model Charter

Fantasy football is treated as a stochastic response problem rooted in real NFL processes rather than as a static ranking exercise.

`N_fantasy ~ L x sigma x A x epsilon`

- `L`: opportunity/exposure
- `sigma`: production/efficiency
- `A`: matchup/kinematic acceptance
- `epsilon`: fantasy-scoring response

Fantasy points are downstream observables.

## Principles

1. **Physics first** — model the process that produces output.
2. **Prospective Data/MC closure** — freeze predictions before observation.
3. **Modularity** — preserve `P ⊕ D ⊕ K`.
4. **Dynamic state** — use weekly state, not static rankings.
5. **Uncertainty first** — distribution, not point estimate, is the answer.
6. **Perturbative complexity** — add higher orders only when material.
7. **Causality** — actions depend only on information available at decision time.
8. **Evidence before tuning** — classify discrepancies before calibration.
9. **Reproducibility** — snapshot -> model/config -> RNG/provenance -> result -> recommendation -> observation -> closure.
10. **Local/private/free-data first** — credentials and private raw data remain local.
