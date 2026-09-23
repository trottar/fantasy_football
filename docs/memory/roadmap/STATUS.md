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
- Phase 1C player shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C P/D/K observability: **COMPLETE**
- Phase 1D market/manager-behavior observability:
  **ACTIVE / READ-ONLY BOUNDARY DISCOVERY**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 prospective evidence: **SECURED / CAUSALLY PROTECTED**

## Phase 1C Commissioned State

DST boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`
at `subsystem.dst.channel`.

K boundary:
`src/specialist_policy_v032.py::evaluate_kicker_channel`
at `subsystem.k.channel`.

Player boundaries:

- CLI: `transaction_manager.evaluate_actions`
  at `subsystem.player.evaluate_actions`;
- GUI: `SeasonGuiService.evaluate_single_add_drop`
  at `subsystem.player.evaluate_single_add_drop`.

All four accepted Phase 1C shadow boundaries are source-published and
runtime-commissioned with bounded in-memory observation and persistent evidence
disabled.

The player runtime gate passed exact source/runtime identity checks, dedicated
pytest, paired output/exception/RNG/state/privacy/overhead probing, full runtime
pytest, compileall, and residue checks.

Canonical Phase 1C player evidence:

- `../evidence/PHASE1C_PLAYER_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `../evidence/PHASE1C_PLAYER_PUBLICATION_RECOVERY_2026-09-23.md`
- `../evidence/PHASE1C_PLAYER_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`

## Phase 1D Frontier

Manager behavior remains separate from football physics.

The existing integration plan names
`src/market_manager.py::search_trades` as proposed
`subsystem.trade.search`, but this is not yet an accepted Phase 1D production
boundary. `market_manager.py` also contains explicit manager-perception and
manager-response logic, so the next gate is a read-only boundary audit that
separates:

- intrinsic football/roster utility;
- manager perception and market response;
- waiver/trade behavior;
- mixed complete-roster response.

Only after that classification may a narrow shadow instrumentation candidate be
proposed. No manager-response parameter calibration is authorized by discovery.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from manager behavior.
- Ownership, trend, and perception may affect behavior kernels but not intrinsic
  football value.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
