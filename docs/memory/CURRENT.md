# Current Project State

---
state_updated: 2026-10-16
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week5_yield_observation_closure_week6_live_gate_next
active_workstream: week6_pre_sunday_live_state_guard_and_week5_component_open
memory_refinement_step: none
nfl_week: 6
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

The 2026 Week 5 selected pre-kickoff fantasy-yield forecasts are now paired with exact Week 5 ESPN actual scores in all four measured channels, after a targeted player-card recovery resolved historical roster/market observation gaps. This closes selected Week 5 fantasy-point observation coverage only; missing player component predictions, independent active/inactive truth, full matchup/regret reconciliation, and long-run calibration remain separate evidence gates. Preserve the Week 6 partial prospective freeze and evaluate live roster/lock state again before consequential Sunday/Monday actions. v0.36-repack1 remains unchanged; no 2026 outcomes tune v0.X.

## Current Work Item

**WEEK 5 SELECTED PROSPECTIVE FANTASY-YIELD OUTCOMES RECONCILED; WEEK 6 LIVE CALENDAR GATE NEXT.**

All 3 frozen Week 5 captures passed integrity and exact snapshot binding. ESPN's roster+market query scored six matchups but omitted 39 unique Week 5 actuals. The targeted player-card query recovered all 39, including three valid zeros. The final selected pre-kickoff forecast comparisons are legacy 31/31, all-league 158/158, DST 29/29 and K 29/29. This is not component or behavior/availability calibration closure. The last Week 6 state-bound MC remains the October 16 15:17 UTC state; any material change invalidates action authority. The two DST-inclusive offers remain modeled Week 7-effective candidates, not submitted transactions.

## Verified State

- Published Week 6 checkpoint commit `66d523c5d63fae9244f54ef7e5e9baf47efb09e6`, verified October 16 with tree `885d29c8987277f62d1225d6590b1e7172f1d364`. Runtime `v0.36-repack1` and internal `VERSION=0.36` remain commissioned and unchanged. The containing checkpoint's future commit SHA is not assumed.
- Week 5 frozen captures: October 8 23:39 UTC, October 9 05:54 UTC, and October 9 16:02 UTC; 3/3 canonical integrity and 3/3 snapshot bindings PASS. The late October 9 captures preserve 15 post-lock and 24 unknown-kickoff forecasts; only individually verified pre-kickoff records are eligible for prospective scoring.
- First Week 5 historical ESPN query: six of six scored matchups, 1,052 source rows, 187 unique scored IDs. It yielded 29/31 legacy, 151/158 all-league, 14/29 DST, and 12/29 K scored selected forecasts. Missingness was distinguished from legitimate zero scores, position mismatches, and conflicts; no missing score was imputed as zero.
- Targeted exact-2026-Week-5 player-card observation recovery returned 39 of 39 missing unique IDs, 3 exact zero scores, no wrong-week/position/conflict results. Final selected forecast coverage is legacy **31/31**, all-league **158/158**, DST **29/29**, K **29/29**. Legacy overlaps all-league.
- Final residual (observed minus frozen expected fantasy points), MAE and RMSE: legacy **+0.6585 / 6.0009 / 7.6221**; all-league **+0.9658 / 6.0716 / 7.9818**; DST **+1.0856 / 5.4669 / 6.8012**; K **+1.7872 / 4.4240 / 5.8559**. Metrics apply to selected pre-kickoff forecasts only.
- Week 5 component measurements remain missing for the player channels: zero component predictions in legacy and all-league frozen blocks. DST captures contain 1,080 component fields across the three artifacts, but independent DST component observation closure is not established; the kicker FG/XP component model was unavailable a priori. The legacy v0.29 ledger covers only its own `players` block, not all-league/DST/K. Active-truth labels cannot be inferred from zero fantasy points or later ESPN `active` fields.
- Week 6 partial freeze remains 189 pre-kickoff, 15 post-lock and 33 kickoff-unknown records. Fresh 15:17 UTC state-bound nine-channel MC receipt `weekly_decision_receipt_20261016T163643Z.json` SHA-256 `a7f163cb673235ff144990cf830f3a995121bb1a5fe2232ac0c10d0171989be0`: operational health PASS, eight channels HOLD and two DST-inclusive offers as the specialist ACTION. Both hypothetical trades take effect Week 7 under 48-hour review, need fresh ownership/legality checks, and were not submitted. Bass remains independently confirmed owned and in the starting K slot as of the 15:17 UTC snapshot.
- The three Week 5 audits were diagnostics only: no post-hoc prediction capture, MC rerun, outcome file writes, tuning, private ESPN data publication, ESPN transaction, source/runtime change, or Git write. Week 3 historical IR-move join remains deferred.

## Calendar / Evidence Gates

Week 5 yield closure is **per-asset prospective and observed-point complete only for selected eligible forecasts**, not a claim that post-lock/unknown predictions or all 2026 modeling components have valid causal closure. The Week 6 Thursday game was locked before Friday captures; only the 189 individual pre-kickoff forecast records are prospectively usable, and the 15 post-lock plus 33 unknown remain excluded. The Week 6 saved receipt cannot authorize Sunday/Monday actions after material state drift. Capture fresh evidence before still-unplayed kickoffs when required, never after outcomes. `MC -> Data -> closure -> diagnosis -> calibration` and the frozen v0.X boundary remain enforced.

## Scientific / Architectural Boundaries

- `N_fantasy ~ L x sigma x A x epsilon`, and `P ⊕ D ⊕ K` with complete-roster response `Delta U = U(S + delta S) - U(S)`.
- Keep player, DST and kicker valuation separate; couple only at complete-roster utility/state. Screen != authority; paired uncertainty-aware MC authorizes consequential decisions.
- Manager response and acquisition probability do not alter intrinsic football value. Drops remain in league state.
- Week 3 Phase A and all prior prospective captures remain immutable. No hindsight relabeling and no 2026 outcome-driven v0.X empirical tuning.
- The control-root local Git status is not the publication allowlist: numerous runtime directories, local caches, backups, carriers, and private observations remain untracked by design. Do not bulk-add, wipe, or publish them. Only exact declaratively staged Git index/manifest bytes authorize a checkpoint.

## Exact Next Action

**Week 6 live-state freshness gate before consequential Sunday/Monday actions.** On the Windows runtime, compare current ESPN roster, lineup/locks, player availability, market and pending transactions with the frozen October 16 15:17 UTC snapshot. If a material change exists, capture a fresh state and run the health-backed complete nine-channel decision authority with record-level kickoff exclusions before the relevant kickoff. Revalidate legal lineup slots, Bass in K, and any trade effective-time/ownership conditions. Do not submit the two old DST offers without fresh acceptance/legality evidence and explicit operator approval. Keep Week 5 yield observations closed only at the selected forecast level; separately investigate player component-prediction absence, DST component truth, availability labels, and lineup/matchup/regret with immutable decision-time provenance. No v0.X empirical tuning. Week 3 replay IR join remains deferred until the Week 6 calendar gate is secured.

## Relevant References

- `evidence/WEEK5_PROSPECTIVE_YIELD_CLOSURE_OBSERVATION_RECOVERY_2026-10-16.md`
- `evidence/WEEK6_PROSPECTIVE_CAPTURE_AND_NINE_CHANNEL_RECOVERY_2026-10-16.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `roadmap/STATUS.md`, `roadmap/SEASON_2026.md`
- `../../src/closure.py`, `../../src/prospective_measurement_v034.py`, `../../src/data_sources/espn_league.py`
- `../../src/weekly_decision_cycle.py`, `../../src/specialist_trade.py`
- `patches/PATCH_PROTOCOL.md`, `TOOLS.md`, `MEMORY.md`, `USER.md`
