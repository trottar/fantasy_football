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

**First prospective league-wide trade search: COMPLETE / NO ACTION.**

A fresh authenticated Week 3 snapshot was synchronized, frozen in the final
v0.34 prospective-capture contract, integrity-verified, and then used for the
existing one-for-one player-channel trade search.

The predictive MC returned six candidates. Only two had positive mean football
delta for our roster, and both were weak/near-coin-flip improvements with
substantial modeled partner loss and very low uncalibrated acceptance
probability:

- Mark Andrews -> Matthew Golden: `+0.104` season PPG, `P(better)=51.5%`,
  partner `-0.490`, `P(accept)=8.0%`;
- George Kittle -> Emeka Egbuka: `+0.196` season PPG,
  `P(better)=52.1%`, partner `-1.387`, `P(accept)=1.3%`.

The other four candidates were negative for our roster. No trade was submitted.
The operational classification is **HOLD / NO ACTION**.

The cheap screen and predictive MC diverged materially on several candidates,
providing a direct prospective example of the architectural rule
`screen != authority`.

A package-only renderer defect initially omitted partner/player identities from
the decision audit because `search_trades` returns flat fields while the
serializer expected nested objects. A guarded replay against the exact frozen
snapshot/capture reproduced all six scalar result vectors within `1e-12`,
recovered the identities, wrote a new corrected audit, and left the original
evidence immutable. No application/model source changed.

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
- No trade was submitted.
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

Do not submit any of the six one-for-one trade candidates from the frozen
Sep 24 search.

The next gate is fresh material Week 3 status/lineup evidence. If Puka Nacua,
J.K. Dobbins, Jakobi Meyers, or another consequential roster status changes, or
a relevant lineup lock approaches, run a fresh decision-time sync/capture before
making the lineup/transaction decision.

Do not rerun or reinterpret the Sep 24 trade search as a later decision state.

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
- `../../src/market_manager.py`
- `../../src/gui/season_service.py`
