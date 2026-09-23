# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1c_player_shadow
memory_refinement_step: maintenance_after_player_boundary_discovery
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: maintenance_checkpoint
---

## Active Objective

Advance Phase 1C player-channel observability at the accepted QB/RB/WR/TE-only
perturbation surfaces while preserving `P ⊕ D ⊕ K`, production semantics,
privacy, and random streams.

## Current Work Item

Phase 1C DST and K observability are complete, source-published,
runtime-commissioned, durable, and remote verified.

The player-boundary discovery is complete. It found no single production-wide
shared player-only wrapper spanning CLI and GUI flows.

Accepted player-only perturbation surfaces:

- CLI: `transaction_manager.evaluate_actions`
- GUI: `SeasonGuiService.evaluate_single_add_drop`

Rejected boundary:

- `transaction_manager.evaluate_roster_predictive` remains rejected because it
  is complete-roster P/D/K response machinery rather than a pure player boundary.

Classification:

`PHASE1C_PLAYER_SINGLE_SHARED_BOUNDARY_NOT_FOUND`

Player runtime instrumentation remains absent. Persistent evidence remains
disabled.

## Verified State

- `v0.36-repack1` remains the commissioned runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync observability is runtime commissioned.
- Phase 1B closure observability is source-published and runtime commissioned.
- Phase 1C DST is source-published and runtime commissioned.
- Phase 1C K is source-published and runtime commissioned.
- Published durable predecessor for this maintenance work:
  `c6a33d12d394e9355c82a2fef84766779ca40420`.
- The player-boundary discovery after that predecessor was read-only and changed
  no football/model/application behavior.
- Three attempts to checkpoint the discovery before maintenance retained no
  project-file modification:
  - v1: `FAILED BEFORE MODIFICATION`;
  - v2: `ROLLED BACK`;
  - v3: `ROLLED BACK` after strict memory health reported `MEMORY.md` at the
    351-line soft threshold.
- No player instrumentation or persistent runtime evidence is enabled.

Canonical discovery and checkpoint-failure records:

- `evidence/PHASE1C_PLAYER_BOUNDARY_DISCOVERY_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_BOUNDARY_CHECKPOINT_FAILURES_2026-09-22.md`

## Calendar / Evidence Gates

- Week 3 week-open prospective capture remains **SECURED / VALID / PRE-KICKOFF**.
- Preserve decision-time captures for consequential Week 3 lineup, waiver,
  trade, and specialist actions.
- No observed 2026 outcome may tune the v0.X model.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.
- Calendar deadlines do not substitute for evidence gates.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- Cross-channel coupling belongs only at complete-roster utility/state boundaries.
- `evaluate_roster_predictive` is not a player-only instrumentation boundary.
- The CLI and GUI player perturbation surfaces are independently valid
  QB/RB/WR/TE-only boundaries; no shared production football wrapper currently
  spans both.
- Observability remains non-interfering and non-authoritative.
- Instrumentation must not create a new football decision boundary merely to
  simplify diagnostics.
- Persistent evidence requires a separate authorization gate.

## Exact Next Action

Prepare one diagnostic-only Phase 1C player-shadow candidate that observes both
accepted player-only perturbation surfaces:

1. `transaction_manager.evaluate_actions`
2. `SeasonGuiService.evaluate_single_add_drop`

Reuse shared observability infrastructure where appropriate, but do **not**
introduce a production-wide shared football wrapper solely for instrumentation.
The candidate must preserve player-only semantics, result/exception behavior,
RNG and mutable state, privacy, `P ⊕ D ⊕ K`, and non-persistence, and it must pass
the established paired non-interference/overhead gate before any runtime
commissioning.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `MAINTENANCE.md`
- `architecture/PLAYER_CHANNEL.md`
- `architecture/SPECIALIST_CHANNELS.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_BOUNDARY_DISCOVERY_2026-09-22.md`
- `evidence/PHASE1C_PLAYER_BOUNDARY_CHECKPOINT_FAILURES_2026-09-22.md`
- `roadmap/STATUS.md`
- `patches/PATCH_PROTOCOL.md`
