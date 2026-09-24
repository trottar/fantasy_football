# Current Project State

---
state_updated: 2026-09-24
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: trade_search_dependency_readiness
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Make the existing automatic trade search operationally ready without changing
football/model logic, then run the first prospective league-wide search only
from a fresh decision-time state.

## Current Work Item

**Trade-search processed-player-values dependency: RUNTIME SYNCHRONIZED /
VALIDATED.**

The commissioned runtime's automatic trade-search path remains unchanged:
`SeasonGuiService` defaults to `data/processed/player_values_2026.csv`, forwards
`self.values_path` into `search_trades`, and `market_manager.search_trades`
requires that path explicitly.

A bounded read-only inventory proved the commissioned
`fantasy_season_v0_36_repack1` runtime alone lacked that default artifact, while
the control root, `fantasy_season_v0_35_fixed1`, and `fantasy_season_v0_36`
contained byte-identical copies with SHA-256
`4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.

The dependency is now made explicit by a hash-guarded synchronization of that
exact control-root artifact into the commissioned runtime. No football,
manager-response, trade-ranking, observability, or calibration code changed.

## Verified State

- Commissioned runtime remains **v0.36-repack1**, internal `VERSION = 0.36`.
- Phase 1A, 1B, 1C, and 1D observability are source-published and runtime
  commissioned.
- Persistent observability sink remains **DISABLED**.
- Phase 1D boundary remains only
  `subsystem.behavior.trade_response_probabilities`; `search_trades`,
  `evaluate_trade`, and `perceived_market_value` remain uninstrumented.
- Source checkpoint `7a3bf1503b5d32be9846d9f7ad110fcff3cff179`
  remains **PUSHED / REMOTE VERIFIED**.
- Runtime Phase 1D commissioning remains validated: dedicated behavior test
  `8 passed`, targeted integration/market tests `38 passed`, full runtime suite
  `353 passed`, retained paired probe PASS, and `compileall` PASS.
- Trade-search dependency inventory confirmed the automatic default path is
  `data/processed/player_values_2026.csv` and the commissioned runtime target
  was absent before synchronization.
- Three available source artifacts were identical: control root,
  `v0.35-fixed1`, and `v0.36`; each was 361778 bytes, 939 CSV rows, and SHA-256
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.
- Required columns `espn_id` and `latent_mean_ppg` are present; optional model
  columns `latent_mean_sd_ppg` and `predictive_weekly_sd_ppg` are also present.
- The exact artifact is now present at
  `fantasy_season_v0_36_repack1/data/processed/player_values_2026.csv`.
- Runtime validation loaded the synchronized artifact through the exact
  `transaction_manager` and `weekly_manager` model-value loaders.
- No trade search was executed by the dependency synchronization.
- Week 3 operational posture remains player HOLD / Lions DST HOLD / Butker K
  HOLD / planning FLEX Mark Andrews. Puka Nacua remains the principal live
  status uncertainty.
- No observed 2026 outcome has tuned v0.X.

Canonical dependency record:
- `evidence/TRADE_SEARCH_PLAYER_VALUES_RUNTIME_SYNC_2026-09-24.md`.

## Calendar / Evidence Gates

- Preserve the Sep 22 week-open and Sep 23 decision-time Week 3 captures.
- A material Puka/Dobbins status change or relevant lineup lock preempts
  nonessential engineering and requires a fresh prospective decision-time state.
- Consequential future trade decisions require their own prospective capture.
- The synchronized player-values artifact is an operational dependency only; it
  is not new outcome evidence and does not authorize v0.X tuning.
- Manager-response probabilities remain explicitly uncalibrated until
  prospective behavior evidence supports calibration.
- Persistent evidence remains separately gated.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Football utility, market perception, and manager behavior remain separate
  response layers.
- Ownership/trend/perception may affect behavior but not intrinsic football
  value.
- `screen != authority`.
- Diagnostics and dependency synchronization must not alter football/model
  formulas or prospective evidence.
- No observed 2026 result may tune v0.X.

## Exact Next Action

Before the first prospective league-wide trade search, obtain a fresh
decision-time season state and freeze the corresponding prospective capture.
Then run the existing league-wide trade search against that frozen state using
the now-explicit commissioned runtime dependency.

Do not reuse the Sep 23 decision-time state for a later consequential trade
decision. Week 3 calendar/status gates still preempt nonessential work.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`
- `evidence/PHASE1D_BEHAVIOR_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`
- `evidence/TRADE_SEARCH_PLAYER_VALUES_RUNTIME_SYNC_2026-09-24.md`
- `../../src/market_manager.py`
- `../../src/gui/season_service.py`
