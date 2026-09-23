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
  **READY / READ-ONLY BOUNDARY DISCOVERY / SECONDARY TO WEEK 3 CALENDAR GATE**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 week-open prospective evidence: **SECURED / CAUSALLY PROTECTED**
- Week 3 Sep 23 decision-time state: **SECURED / OPERATIONAL DECISIONS COMPLETE**
- Week 3 current P/D/K transaction posture: **HOLD / HOLD / HOLD**
- Week 3 planning FLEX: **MARK ANDREWS**
- Week 3 next calendar gate: **STATUS/INJURY REFRESH BEFORE CONSEQUENTIAL
  LINEUP CHANGE OR RELEVANT SUNDAY LOCK**

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

Canonical Phase 1C player evidence:

- `../evidence/PHASE1C_PLAYER_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `../evidence/PHASE1C_PLAYER_PUBLICATION_RECOVERY_2026-09-23.md`
- `../evidence/PHASE1C_PLAYER_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`

## Week 3 Operational Gate

The Sep 22 week-open reference remains immutable and a separate Sep 23
decision-time capture was frozen before outcomes.

Wednesday operational classification:

- player channel: HOLD; 72 paired SCREEN1 actions completed at 1,024 universes
  and none survived the league-state plausibility gate;
- DST: HOLD Lions D/ST;
- K: HOLD Harrison Butker;
- expected-value lineup FLEX: Mark Andrews;
- principal live status uncertainty: Puka Nacua;
- Puka OUT contingency: Carnell Tate + Rashid Shaheed at WR, J.K. Dobbins at
  FLEX.

The next football gate is a fresh decision-time sync/capture when material status
information changes or before the relevant Sunday lineup locks. Wednesday
evidence must not be overwritten.

Canonical evidence:
`../evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`.

## Phase 1D Frontier

Manager behavior remains separate from football physics.

The existing integration plan names
`src/market_manager.py::search_trades` as proposed
`subsystem.trade.search`, but this is not yet an accepted Phase 1D production
boundary. `market_manager.py` also contains explicit manager-perception and
manager-response logic.

Phase 1D remains read-only discovery only and may proceed between calendar gates.
It must yield immediately when a prospective Week 3 decision capture is needed.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from manager behavior.
- Ownership, trend, and perception may affect behavior kernels but not intrinsic
  football value.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
- `screen != authority`.
