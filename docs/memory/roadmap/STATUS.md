# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C P/D/K observability: **COMPLETE / SOURCE PUBLISHED / RUNTIME
  COMMISSIONED**
- Phase 1D market/manager-behavior observability:
  **BOUNDARY DISCOVERY COMPLETE / NARROW BEHAVIOR PROBE NEXT**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 prospective evidence: **SECURED / CAUSALLY PROTECTED**
- Week 3 current P/D/K transaction posture: **HOLD / HOLD / HOLD**
- Week 3 planning FLEX: **MARK ANDREWS**
- Trade-search operational target:
  **PREFERRED BEFORE WEEK 4 / SUBORDINATE TO WEEK 3 CALENDAR GATES**

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

All accepted Phase 1C boundaries are source-published and runtime-commissioned
with bounded in-memory observation and persistent evidence disabled.

## Week 3 Operational Gate

The Sep 22 week-open reference remains immutable and the separate Sep 23
decision-time capture is frozen before outcomes.

Wednesday operational classification:

- player add/drop channel: HOLD;
- DST: HOLD Lions D/ST;
- K: HOLD Harrison Butker;
- expected-value FLEX: Mark Andrews;
- principal live status uncertainty: Puka Nacua.

The waiver/free-agent search is complete for the Wednesday state. The Week 3
league-wide trade search was intentionally deferred because it is a more complex
decision surface.

The next football gate remains a fresh decision-time sync/capture when material
status information changes or before the relevant Sunday lineup locks.

Canonical evidence:
`../evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`.

## Phase 1D Boundary Discovery

Read-only source audit classified the current trade path into distinct layers.

**Football/roster response**

- `evaluate_roster_season_scenarios`;
- roster legality and post-trade automatic release/fill machinery;
- `_need_multiplier`;
- `_coarse_trade_score`;
- `screen_one_for_one_trades`.

**Manager perception / market feature**

- `_espn_market_ppg`;
- `perceived_market_value`.

**Manager behavior**

- `trade_response_probabilities`.

**Mixed complete trade response / orchestration**

- `evaluate_trade`;
- `search_trades`.

The integration-plan proposal `subsystem.trade.search` at `search_trades` is
therefore rejected as a behavior-only Phase 1D boundary. It joins the football
screen, both managers' predictive roster response, market perception, the
acceptance kernel, and offer ranking.

The preferred first Phase 1D behavior candidate is
`src/market_manager.py::trade_response_probabilities`. It is the narrow shared
accept/counter/reject response kernel used beneath both manual trade evaluation
and league-wide search. Its model remains explicitly
`UNCALIBRATED_TRADE_RESPONSE_V030`.

`perceived_market_value` remains a separate candidate for later market-perception
observation if evidence shows that a second boundary is useful. It is not part of
the first probe.

Canonical evidence:
`../evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`.

## Trade Search Before Week 4

The trade engine already exists and is covered by market-manager tests. The
automatic search:

1. screens league-wide one-for-one QB/RB/WR/TE offers;
2. runs predictive MC on the screened frontier;
3. keeps both managers' football deltas separate;
4. adds the uncalibrated manager-response layer;
5. ranks offers by expected offer value.

Operational readiness still requires an explicit data-dependency check because
the commissioned repack is known to lack its default
`data/processed/player_values_2026.csv`. The Week 3 recovery established an exact
predecessor artifact, but that should not be silently assumed as a permanent
runtime dependency.

Preferred target: resolve/validate that operational dependency and perform the
first prospective trade search before the Week 4 decision window, without
displacing Week 3 capture obligations.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from manager behavior.
- Ownership, trend, and perception may affect behavior kernels but not intrinsic
  football value.
- `screen != authority`.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
