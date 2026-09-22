# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1c_player_boundary_discovery
memory_refinement_step: M0_M7_complete_durable
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Resume Phase 1C at the unresolved player-only observability boundary while
preserving `P ⊕ D ⊕ K`.

DST and K are now source-published and runtime-commissioned as separate bounded
specialist observers. The next task is read-only exact-source discovery of a
narrower QB/RB/WR/TE-only production boundary. Player instrumentation remains
blocked until that boundary is accepted by evidence.

## Current Work Item

**Phase 1B closure instrumentation: COMPLETE / SOURCE PUBLISHED / RUNTIME
COMMISSIONED.**

**Phase 1C channel boundary audit: COMPLETE / DURABLE.**

**Phase 1C DST shadow: COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED.**

**Phase 1C K shadow: COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED.**

**Phase 1C player shadow: BOUNDARY UNRESOLVED / DISCOVERY NEXT.**

The Week 3 week-open prospective capture remains
**SECURED / VALID / PRE-KICKOFF**.

## Verified State

- `v0.36-repack1` remains the commissioned runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1C DST remains commissioned at `subsystem.dst.channel`.
- Phase 1C K source checkpoint:
  `2d28adf926c8da22dcb695c03f7945bd361d13d2`, tree
  `ebb4997245abace8d2d692de3aa35d03e646af35`, remote verified.
- K runtime commissioning:
  - dedicated K+DST pytest: **12 passed in 0.82 s**;
  - paired K probe: baseline `7400 ns`, observed `82700 ns`, incremental
    `75300 ns`;
  - privacy/semantics/RNG/mutable-state, DST non-interference, and P/D/K guard:
    PASS;
  - full runtime pytest: **353 passed in 44.75 s**;
  - compileall, final target identities, rollback-backup identity, cleanup, and
    residue: PASS / NONE;
  - persistent sink: false.
- Commissioned K production SHA-256:
  - `src/specialist_policy_v032.py`:
    `d9124bb51a9baa93a0a8f53768a4b41af9b08ed690c5e0f8ebc98c32d28ad271`;
  - `src/observability/k_shadow.py`:
    `81e324a432f3ace85bb9032e2deb60af945607891131d00ee787381880a45ab0`.
- Player runtime instrumentation remains absent.
- No football/model/decision authority changed; persistent runtime evidence
  remains disabled.

## Calendar / Evidence Gates

- Week 3 week-open capture remains **SECURED / VALID / PRE-KICKOFF**.
- Preserve separate decision-time captures for consequential Week 3 lineup,
  waiver, trade, and specialist actions.
- No observed 2026 outcome may tune the v0.X model.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.
- Week 5 remains the preferred broader v1.0 observability commissioning target.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- `evaluate_defense_channel` remains DST-only.
- `evaluate_kicker_channel` is commissioned only at `subsystem.k.channel`.
- Player production remains uninstrumented pending a narrower player-only boundary.
- Cross-channel coupling belongs only at complete-roster utility/state boundaries.
- Observability remains non-interfering and non-authoritative.
- Persistent evidence requires a separate authorization gate.

## Exact Next Action

Conduct one read-only exact-source boundary-discovery pass for a narrower
QB/RB/WR/TE-only production boundary.

Reject any candidate that carries complete-roster specialist state or directly
couples P/D/K channels. Do not modify player production source, enable persistent
evidence, or retune football/model behavior during boundary discovery.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `architecture/SPECIALIST_CHANNELS.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `evidence/PHASE1C_K_TARGETED_PREFLIGHT_2026-09-22.md`
- `evidence/PHASE1C_K_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_K_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `roadmap/STATUS.md`
- `patches/PATCH_PROTOCOL.md`
