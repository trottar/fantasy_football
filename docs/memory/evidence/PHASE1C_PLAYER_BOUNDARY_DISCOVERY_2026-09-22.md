# Phase 1C Player Boundary Discovery — 2026-09-22

## Question

Does current production source contain one shared QB/RB/WR/TE-only boundary that
can support the Phase 1C player shadow across both CLI and GUI action flows
without crossing into DST/K state?

## Predecessor

Latest published durable checkpoint before this read-only discovery:

`c6a33d12d394e9355c82a2fef84766779ca40420`

At that checkpoint, DST and K observability were already complete,
source-published, runtime-commissioned, durable, and remote verified. Player
runtime instrumentation was absent.

## Probe

Read-only exact-source boundary discovery inspected the existing player action
evaluation surfaces and the previously proposed predictive roster boundary.

No production files, runtime files, persistent sinks, model parameters, or
decision semantics were changed.

## Raw Findings

1. `transaction_manager.evaluate_roster_predictive` remains unsuitable as a
   player-only boundary because it is complete-roster P/D/K response machinery.
2. CLI player add/drop perturbation evaluation has a clean QB/RB/WR/TE surface:
   `transaction_manager.evaluate_actions`.
3. GUI single add/drop perturbation evaluation has a clean QB/RB/WR/TE surface:
   `SeasonGuiService.evaluate_single_add_drop`.
4. No production-wide shared player-only wrapper currently spans both surfaces.

## Classification

`PHASE1C_PLAYER_SINGLE_SHARED_BOUNDARY_NOT_FOUND`

This is an architectural discovery, not a model-calibration result.

## Decision

Do not force the complete-roster predictive evaluator into the player channel and
do not create a new shared football-production wrapper merely to make
instrumentation convenient.

The next player-shadow candidate may observe both accepted player-only surfaces
and may reuse common observability infrastructure, provided the observer remains
non-interfering, non-authoritative, private-data safe, and non-persistent.

## Limitations

This discovery does not commission player instrumentation. It does not establish
persistent evidence authority and does not alter football/model/application
behavior.

## Durable Boundary

Preserve `P ⊕ D ⊕ K`: players compare only with players; cross-channel coupling
belongs only at complete-roster utility/state boundaries.
