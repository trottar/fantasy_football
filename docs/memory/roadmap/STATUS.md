# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C channel boundary audit: **COMPLETE / DURABLE**
- Phase 1C DST shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C K shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C player boundary discovery: **COMPLETE / READ-ONLY**
- Phase 1C player shadow: **NOT YET INSTRUMENTED / DUAL-SURFACE CANDIDATE NEXT**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 week-open capture: **SECURED / VALID / PRE-KICKOFF**

## Phase 1C Specialist State

DST boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`
at `subsystem.dst.channel`.

K boundary:
`src/specialist_policy_v032.py::evaluate_kicker_channel`
at `subsystem.k.channel`.

Both specialist shadows are source-published and runtime-commissioned. Their
observers remain bounded and in-memory only.

Canonical runtime evidence:

- `../evidence/PHASE1C_DST_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `../evidence/PHASE1C_K_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`

## Phase 1C Player Boundary State

Rejected as player-only:

`transaction_manager.evaluate_roster_predictive`

Reason: it is complete-roster P/D/K response machinery and therefore cannot be
treated as a pure player-channel boundary.

Read-only discovery found no single production-wide shared player wrapper.

Accepted player-only perturbation surfaces:

- CLI: `transaction_manager.evaluate_actions`
- GUI: `SeasonGuiService.evaluate_single_add_drop`

Classification:

`PHASE1C_PLAYER_SINGLE_SHARED_BOUNDARY_NOT_FOUND`

Canonical evidence:
`../evidence/PHASE1C_PLAYER_BOUNDARY_DISCOVERY_2026-09-22.md`.

The next candidate should observe both accepted surfaces while sharing only
observability support where appropriate. Do not invent a new football-production
wrapper merely to simplify instrumentation.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players.
- Diagnostics remain observers, not decision/control logic.
- Player instrumentation must preserve output/exception semantics, RNG, mutable
  state, privacy, and the established overhead gate.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
