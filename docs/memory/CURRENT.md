# Current Project State

---
state_updated: 2026-09-24
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: week3_status_gate
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Protect Week 3 prospective evidence and make lineup/transaction decisions only
from fresh decision-time state when material status information changes.

## Current Work Item

**Week 3 fresh status/lineup gate: CAPTURED / HOLD.**

A fresh authenticated Week 3 state was synchronized on Sep 24, frozen in the
final v0.34 prospective-capture contract, integrity-verified, and reconciled
through the exact commissioned lineup path.

The fresh state showed:

- roster availability/practice state changes: `0`;
- expected-lineup identity change: `false`;
- expected lineup projection: `123.30`;
- availability-weighted expected lineup: `118.02`;
- Puka Nacua, Jakobi Meyers, and J.K. Dobbins remain QUESTIONABLE at provisional
  `P(active)=75%` with no captured practice sequence;
- Josh Jacobs remains hard-unavailable: EXEMPT,
  `P(active)=0%`, bench.

The initial package classifier set `decision_relevant=true` only because Josh
Jacobs' Thursday kickoff was within 12 hours. That was a diagnostic classifier
false positive: Jacobs is bench, hard-unavailable, and not needed by the current
planned lineup or any captured one-player contingency.

A bounded recovery against the exact frozen snapshot/capture/audit reclassified
the gate:

**HOLD / NO HEAVY CHANNEL RERUN**

No add/drop, DST, kicker, or trade MC was rerun. No transaction was submitted.
No football/model/application source changed.

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
- First prospective trade-search snapshot:
  SHA-256 `3a300ecd1971795888847d7fada1f2702f9e5afd1d3e7640d17ca3cbc081cd38`.
- Frozen prospective capture:
  SHA-256 `5b05e1cd0e62b74df8a3a68b66c41dbc3dfb6be0e40cd424d3d161d891cd8bda`,
  contract `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`, integrity PASS.
- Corrected identity-recovery audit:
  SHA-256 `9eaafcfe4bb7e003f5622a5d8c901c286b7ddcb9139a82cd898a7ccbd1259e32`.
- First league-wide one-for-one trade search: **NO ACTION / HOLD**.
- Fresh Sep 24 status-gate snapshot:
  SHA-256 `440e061603867ce59192709c22cefdf52a6eb2f437b2a10ab08ee359b2980644`.
- Fresh Sep 24 status-gate capture:
  SHA-256 `721331684b8f354e9d534545190bfdd6c20acdbbb24e5664086e475f13a828f0`,
  integrity PASS.
- Status/lineup decision audit:
  SHA-256 `c944b29ff05e83b7116d224c69cf7997217d43b5cad4b0e98e49a15a830ed817`.
- Relevance-recovery audit:
  SHA-256 `cb1752c1bbe88c3f750198ad059602b3cb2e69c87d2cf77d018836222207c317`.
- Recovered status-gate classification:
  **HOLD / NO HEAVY CHANNEL RERUN**.
- No trade or other transaction was submitted.
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

Maintain the current Week 3 HOLD state.

Trigger the next decision cycle only when:

1. Puka Nacua, J.K. Dobbins, Jakobi Meyers, or another consequential roster
   status/practice observation materially changes; or
2. a player who is actually in the planned lineup or a captured contingency
   approaches a consequential lock/reveal window.

At that gate, perform a fresh decision-time sync/capture before changing the
lineup or rerunning a decision-relevant player/DST/K channel.

A hard-unavailable bench player's approaching kickoff alone is not a decision
trigger. Do not rerun or reinterpret prior frozen trade/status states as later
decision-time evidence.

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
- `evidence/WEEK3_PROSPECTIVE_TRADE_SEARCH_2026-09-24.md`
- `evidence/WEEK3_STATUS_LINEUP_GATE_2026-09-24.md`
- `../../src/market_manager.py`
- `../../src/gui/season_service.py`
