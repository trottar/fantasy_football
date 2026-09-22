# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1c_dst_shadow_preflight
memory_refinement_step: M0_M7_complete_durable
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Advance Phase 1C one channel at a time while preserving `P ⊕ D ⊕ K`.

The read-only channel-boundary audit is complete. DST is the first narrow
candidate. K remains separately gated. The previously planned player boundary is
not authorized because it is complete-roster rather than player-channel pure.

## Current Work Item

**Phase 1B closure instrumentation: COMPLETE / SOURCE PUBLISHED / RUNTIME
COMMISSIONED.**

**Phase 1C channel boundary audit: COMPLETE.**

**Phase 1C DST shadow: TARGETED PREFLIGHT NEXT / NO SOURCE CHANGE YET.**

The Week 3 week-open prospective capture remains
**SECURED / VALID / PRE-KICKOFF**.

Canonical Phase 1C audit:
`evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`.

## Verified State

- `v0.36-repack1` remains the commissioned 0.X runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is
  **COMPLETE / RUNTIME COMMISSIONED**.
- Phase 1B closure-capture shadow is
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**.
- Phase 1B durable closure checkpoint:
  `340a2b87a5e4b3fc5c04848dff1db03280f148c7`.
- Persistent runtime evidence remains **DISABLED**.
- The v1.0A integration map proposes:
  - player: `src/transaction_manager.py::evaluate_roster_predictive`;
  - DST: `src/specialist_policy_v032.py::evaluate_defense_channel`;
  - K: `src/specialist_policy_v032.py::evaluate_kicker_channel`.
- The proposed player point is **NOT ACCEPTED** as a Phase 1C player-only
  observability boundary:
  - production calls evaluate it with `ctx.roster` and action `new_roster`;
  - the complete-roster simulation includes K/DST positions;
  - the predictive path explicitly executes DST component simulation.
- Therefore `evaluate_roster_predictive` is a complete-roster utility/response
  boundary, not a pure `P = QB/RB/WR/TE` boundary.
- No player instrumentation is authorized until a narrower player-only production
  boundary is identified from exact source.
- The DST and K policy wrappers are acceptable outer channel boundaries:
  - `evaluate_defense_channel` fixes `position="DST"`;
  - `evaluate_kicker_channel` fixes `position="K"`;
  - specialist candidate/configuration machinery filters within the selected
    specialist position;
  - permitted cross-channel coupling remains at complete-roster utility/state
    boundaries rather than peer comparison.
- DST is selected for the first Phase 1C targeted preflight because its physical
  channel already exposes explicit component response (sacks, interceptions,
  fumble recoveries, defensive TDs, points allowed, yards allowed).
- K remains deferred behind the DST gate. Its current model is deliberately
  simpler aggregate yield/team-environment response pending prospective kicker
  closure.
- This audit changed no production source, runtime source, football/model logic,
  manager behavior, persistent sink, Git index/history, or remote source.

## Calendar / Evidence Gates

- Weeks 1/2 count as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 week-open capture gate is **SECURED**.
- Preserve separate decision-time captures for consequential Week 3 actions.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.
- Week 5 remains the preferred broader v1.0 observability commissioning target.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- Cross-channel coupling belongs only at complete-roster utility/state boundaries.
- Keep manager behavior separate from intrinsic football utility.
- `screen != authority`.
- Only decision-time information may influence prospective actions.
- `0.X` remains a-priori; observed 2026 outcomes may tune only `1.X`.
- Observability remains non-interfering and non-authoritative.
- Authenticated/raw capture material remains local.
- Persistent evidence requires a separate authorization gate.

## Exact Next Action

Construct one **diagnostic-only targeted preflight** for the exact current
`src/specialist_policy_v032.py::evaluate_defense_channel` boundary.

The preflight must not modify production source. It should establish the DST
observer contract before instrumentation:

- boundary identity: `subsystem.dst.channel`;
- subsystem: `dst`;
- bounded in-memory only;
- no arguments, returned report payloads, private/authenticated data, or exception
  messages retained;
- production result/exception wins over observer behavior;
- Python/NumPy stochastic state and relevant mutable input state are unchanged by
  observation;
- output/exception behavior is paired against the unobserved call;
- overhead uses the existing benchmark-gate contract;
- persistent sink remains disabled.

Do not include K or player instrumentation in the DST preflight.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `architecture/PLAYER_CHANNEL.md`
- `architecture/SPECIALIST_CHANNELS.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`
- `evidence/PHASE1B_CLOSURE_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `patches/PATCH_PROTOCOL.md`
