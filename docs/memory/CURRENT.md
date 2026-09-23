# Current Project State

---
state_updated: 2026-09-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1d_trade_behavior_boundary_probe
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Advance Phase 1D market/manager-behavior observability from completed read-only
boundary discovery to one non-modifying paired probe of the narrow trade-response
kernel, while preserving all Week 3 prospective calendar gates.

A preferred operational target is to have the trade-search path ready for
prospective use before the Week 4 decision window. That target does not override
a Week 3 injury/status capture deadline.

## Current Work Item

**Phase 1D trade-behavior boundary candidate: DISCOVERY COMPLETE / PAIRED PROBE
NEXT / NO PRODUCTION INSTRUMENTATION.**

Read-only source classification established:

- `search_trades` is mixed orchestration: cheap football screening, full
  predictive roster response, manager-response probability, and offer ranking;
- `evaluate_trade` is a mixed complete trade-response surface joining football
  value and manager behavior;
- `perceived_market_value` is a separate manager-perception/market feature and
  does not alter intrinsic football value;
- `trade_response_probabilities` is the narrow behavior-only response kernel and
  is the preferred Phase 1D shadow candidate.

The existing integration-plan proposal at `subsystem.trade.search` is therefore
not accepted as the Phase 1D manager-behavior boundary.

## Verified State

- Authoritative commissioned runtime: **v0.36-repack1**, internal
  `VERSION = 0.36`.
- Phase 1A season-sync shadow: **RUNTIME COMMISSIONED**.
- Phase 1B closure shadow: **SOURCE PUBLISHED / RUNTIME COMMISSIONED**.
- Phase 1C P/D/K observability: **COMPLETE / SOURCE PUBLISHED / RUNTIME
  COMMISSIONED**.
- Persistent observability sink: **DISABLED**.
- Week 3 Wednesday decision state remains valid:
  - player add/drop channel: **HOLD**;
  - DST: **HOLD Lions D/ST**;
  - kicker: **HOLD Harrison Butker**;
  - planning FLEX: **Mark Andrews**;
  - principal live uncertainty: **Puka Nacua**.
- The Week 3 waiver/free-agent conclusion is a completed model result, not a
  readiness placeholder: 72 paired player actions completed SCREEN1 at 1,024
  universes and no resolved positive league-state edge survived.
- No Week 3 league-wide trade search has been run.
- The trade engine already supports:
  - one-for-one league-wide screening followed by predictive MC through
    `search_trades`;
  - manual `evaluate_trade` packages up to two players per side;
  - modeled post-trade legal releases/fills;
  - separate football deltas for both managers;
  - a separate, explicitly uncalibrated acceptance/counter/reject behavior
    model.
- The automatic trade search remains one-for-one and defaults to
  `data/processed/player_values_2026.csv`.
- The commissioned repack is known from the Week 3 recovery to lack that default
  processed values artifact; operational trade-search readiness before Week 4
  must resolve or explicitly route that dependency rather than silently assume
  it exists.
- Current MC architecture is materially more advanced than the original
  preseason system and consumes fresh weekly state, but **no observed 2026
  outcome has tuned v0.X**. Weeks 1-2 are not empirical parameter updates.
- Phase 1D source authority:
  - `src/market_manager.py` Git blob
    `4ffa2f9ead68c9933dd6d1ab06deb425b4a17278`;
  - `src/observability/integration_plan.py` Git blob
    `c8ef2dbcf8a9e30bf3f77497f270c4bb8fbedcbd`;
  - `tests/test_market_manager_v030.py` Git blob
    `1dcd38be513c588c6c374b40516e2fdc4e90bc7c`.
- Canonical Phase 1D discovery evidence:
  `evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`.

## Calendar / Evidence Gates

- Preserve the Sep 22 Week 3 week-open reference and Sep 23 decision-time capture
  unchanged.
- A material Puka/Dobbins status change, or the relevant Sunday lineup lock,
  preempts nonessential Phase 1D work and requires a fresh prospective
  decision-time state.
- Trade-search readiness before Week 4 is a **preferred operational development
  target**, not a retrospective evidence gate and not permission to tune v0.X.
- A future consequential trade recommendation requires its own prospective
  decision-time capture using information available at that time.
- No observed 2026 result may tune v0.X; empirical evolution remains v1.X and
  evidence-gated.
- Manager-response probabilities remain explicitly uncalibrated until
  prospective behavior evidence supports calibration.
- Persistent evidence remains separately gated.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- Cross-channel coupling remains at complete-roster utility/state boundaries.
- Football utility and manager behavior are separate stochastic response layers.
- Market ownership/trend/perception may affect the behavior kernel but may not
  alter intrinsic football value.
- `screen != authority`; the one-for-one trade screen may select candidates but
  cannot authorize an offer without uncertainty-aware predictive evaluation.
- `search_trades` and `evaluate_trade` are mixed surfaces and must not be
  mislabeled as behavior-only observability boundaries.
- Diagnostics remain shadow-only, non-interfering, and non-persistent unless
  separately gated.

## Exact Next Action

Build and run one **non-modifying paired Phase 1D probe** around
`src/market_manager.py::trade_response_probabilities` from the exact current
source. Measure:

- output and exception equivalence;
- Python and NumPy RNG non-interference;
- mutable-state non-interference;
- bounded privacy/correlation structure;
- absolute and relative overhead, with special attention to the kernel's very
  short baseline runtime.

If the probe passes, propose one narrow behavior shadow-instrumentation candidate.
If it fails, classify the failure and defer or adjust the observability boundary.

Do **not** instrument `search_trades`, `evaluate_trade`, or
`perceived_market_value` as part of this probe. Do not enable persistence or tune
manager-response parameters.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `MAINTENANCE.md`
- `COMMUNICATION.md`
- `TOOLS.md`
- `patches/PATCH_PROTOCOL.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `architecture/PHASE_V1_CONTEXT.md`
- `evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`
- `evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`
- `../../src/market_manager.py`
- `../../src/observability/integration_plan.py`
- `../../tests/test_market_manager_v030.py`
