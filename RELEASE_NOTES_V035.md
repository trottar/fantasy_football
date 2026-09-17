# v0.35 — Causal temporal player-membership state

Parent: commissioned `v0.34`.

## Scientific scope

v0.35 advances the pre-data state equation from a future-information correction on frozen player membership to an explicit first-order temporal player state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

Our QB/RB/WR/TE membership `P_w` now evolves from the synchronized current roster under a causal player-channel policy before a future specialist perturbation is evaluated.

### Player-state transition

- Current-week membership is observed and immutable in this layer. Immediate player transactions remain authoritative in `roster-actions`.
- Beginning with the next modeled week, at most one guaranteed-FREEAGENT add/drop best response is allowed per week.
- A future swap must improve expected remaining-season player-lineup response without worsening that decision week's expected lineup response.
- Candidate screening uses the commissioned player-yield model, not ownership/trend popularity.
- Current WAIVERS are excluded from guaranteed future acquisition.
- A player dropped by our modeled policy re-enters the local free pool only in the following modeled week.
- Realized fantasy-score samples never select a future transaction.

### First-order expansion boundary

For future second-DST evaluation:

1. evolve `P_w` causally to the effective activation week;
2. freeze that local player state as the expansion point;
3. apply the second-DST/player-release perturbation;
4. evaluate the complete H2H response under common random numbers.

Post-perturbation player-market reaction and other managers' future player transactions are intentionally not propagated in v0.35. Those higher-order league-state effects are reserved for v0.36.

The external-player-market approximation is therefore explicit:

`FROZEN_CURRENT_GUARANTEED_FREEAGENT_POOL_NO_EXTERNAL_CLAIMS_V035`

### Prospective measurement

The v0.34 a-priori measurement contract remains active. `closure-capture` now additionally freezes the predicted v0.35 temporal player-state path. The capture `model_version` advances to `0.35`; the measurement protocol remains `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`.

No 2026 game outcome is consumed for tuning, refitting, classification, or calibration.

## Release format

v0.35 is a standalone full-source archive rather than a self-materializing delta. Runtime bootstrap/materialization files are not required. The user migrates only the `data/` directory from the commissioned v0.34 tree.
