# Current Project State

---
state_updated: 2026-10-17
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week6_live_ir_coverage_and_pre_sunday_gate
active_workstream: week6_pre_kickoff_decision_time_guard
memory_refinement_step: none
nfl_week: 6
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Preserve the October 17 Week 6 pre-kickoff snapshot/capture and state-bound nine-channel MC as immutable evidence. Operational health passed, but the IR replacement adapter remains `INCOMPLETE_COVERAGE` because one available IR slot has three individually legal move candidates. A subsequent live ESPN check found four market `nfl_team` changes, including one screened specialist asset, invalidating the saved MC for new actions. Protect the next Sunday/Monday decision-time capture gate. Keep v0.36-repack1, Week 5 selected fantasy-yield closure, and all earlier prospective captures unchanged.

## Current Work Item

**WEEK 6 LIVE INPUT DRIFT CONFIRMED; IR COVERAGE FAIL-CLOSED; PRE-KICKOFF CAPTURE NEXT.**

The October 17 00:18 UTC six-provider capture has 189 verified pre-kickoff, 15 post-lock, and 33 kickoff-unknown records. The 01:01 UTC nine-channel receipt reports lineup ACTION, specialist-inclusive trade ACTION (three Week 7-effective hypothetical offers), scoped HOLD in the remaining non-IR decision channels, and IR `INCOMPLETE_COVERAGE`; native overall `INCOMPLETE_COVERAGE`. The saved lineup is legally feasible but remains unset. Market candidate membership is unchanged, not model response. No ESPN transaction or football/model change has occurred.

## Verified State

- **Repository/runtime boundary:** published predecessor commit `d37ef6936104fac9694777b9b913d7eea30c2616` is the remote-verified Week 5 closure, not this memory checkpoint's future SHA. Commissioned runtime `v0.36-repack1` / `VERSION=0.36` unchanged.
- **Week 5:** selected pre-kickoff exact ESPN fantasy-yield observation coverage legacy 31/31, all-league players 158/158, DST 29/29, K 29/29. Component predictions/truth, independent availability, matchup/regret, and calibration remain open. No observed 2026 outcome tunes v0.X.
- **Week 6 frozen evidence:** snapshot `data/season_snapshots/20261017T001824Z/snapshot.json`, UTC `2026-10-17T00:18:47.019990+00:00`; bound capture `data/season_predictions/closure/pregame_2026_w06_20261017T001900Z.json`, SHA-256 `67bc87f6231ba8468ceb9513175cd4ac5b92e2a529bbb9a4096be6f7f696e0a4`. Six providers, integrity and binding PASS; causal per-record scope 189 PRE / 15 POST_LOCK / 33 UNKNOWN.
- **State-bound MC:** `data/season_decisions/weekly_decision_receipt_20261017T010119Z.json`, SHA-256 `f6a3788e1ce15d5c3bad90270700122454e60a2589138b6d4e5d417c942ba13d`. Health PASS; lineup ACTION; player/DST/K acquisition and player trades HOLD; specialist trade ACTION (three unsubmitted offers, 48-hour review, Week 7 effect); IR `INCOMPLETE_COVERAGE:GATE_B_IR_MOVE_PLUS_ADD_VALUE_ADAPTER`; overall `INCOMPLETE_COVERAGE`.
- **IR diagnosis:** roster legality PASS; active 16/16, IR 0/1, three unlocked OUT bench players eligible for one IR opening. Adapter supports one unambiguous candidate only; exact reason `AMBIGUOUS_IR_MOVE_CANDIDATE_WITHOUT_B2B_HORIZON`. Hypothetical branches share active 15/16, IR 1/1, one new active slot, position headroom and the same screened 74 player + 16 DST + 16 K candidates. A 64-scenario paired player-channel HOLD, one-add and delta comparison returned zero differences. These narrow results do **not** establish all-candidate utility, specialist response, acquisition probabilities, future IR return/capacity, or completed IR authority. No IR player selected.
- **Live gate:** October 17 03:15 UTC ESPN roster/lineup read found zero ownership/roster/transaction/matchup changes and nine feasible slots with Bass at K, but lineup not yet set. October 17 03:25 UTC attribution found exactly four `nfl_team` changes: one in the specialist frontier, none in player frontier, three outside. Screened ID sets remained 74 players / 32 specialists, holding non-ESPN annotations fixed for ESPN-only sensitivity. This is **material input drift**, not fresh six-provider or MC authority.
- **Unchanged scope:** no ESPN transactions, recaptured/backdated predictions, empirical v0.X retuning, production logic changes, or Git writes by post-capture diagnostics. Week 3 historical IR replay join and deeper Week 5 component closure are deferred.

## Calendar / Evidence Gates

Only the 189 individual PRE records are eligible for prospective Week 6 assessment; 15 POST_LOCK and 33 UNKNOWN are excluded and cannot be relabeled after kickoff. The October 17 saved MC is stale for consequential action because NFL-team assignment can affect specialist matchup or schedule response. Static/screen/sampled response equivalence does not override the IR `INCOMPLETE_COVERAGE` result. New decision-time evidence must precede the applicable still-unplayed kickoff. Preserve `MC -> Data -> closure -> diagnosis -> calibration`; time passing is not evidence for v1.X calibration and 2026 outcomes do not tune v0.X.

## Scientific / Architectural Boundaries

- `N_fantasy ~ L x sigma x A x epsilon`; preserve `P ⊕ D ⊕ K`; compose cross-channel response only at complete-roster utility/state: `Delta U = U(S + delta S) - U(S)`.
- `screen != authority`; use paired uncertainty-aware MC, decision-time inputs and separate manager behavior. Drops remain part of league state.
- Preserve frozen prospective evidence, explicit lock exclusions, and a-priori v0.X parameters. The full nine-channel completion contract remains fail-closed.
- Local control-root state, isolated staging, commit, remote verification, runtime synchronization and commissioning are distinct. Never bulk-stage private snapshots, caches, credentials, or runtime artifacts.

## Exact Next Action

**Secure a fresh Week 6 decision-time state and health-backed nine-channel evaluation before consequential Sunday/Monday actions.** Recheck live ESPN ownership, lineup and kickoff locks, injuries, pending transactions, market `nfl_team` mapping, six-provider health, Bass at K, and the 48-hour trade-effective boundary. If material changes persist, make a new immutable **pre-kickoff** capture and run the complete nine-channel MC bound to that state; keep all older predictions unchanged. The native IR coverage gap remains unresolved and must not be suppressed with sampled-equivalence claims. Do not submit IR moves, lineup edits, or trade offers automatically; require explicit approval and fresh legality/acceptance evidence. Defer any model-logic extension, B2b horizon inference, Week 5 deeper closure and Week 3 replay IR work until the calendar gate is secured.

## Relevant References

- `evidence/WEEK6_LIVE_IR_MARKET_DRIFT_RECOVERY_2026-10-17.md`
- `evidence/WEEK6_PROSPECTIVE_CAPTURE_AND_NINE_CHANNEL_RECOVERY_2026-10-16.md`
- `evidence/WEEK5_PROSPECTIVE_YIELD_CLOSURE_OBSERVATION_RECOVERY_2026-10-16.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`; `roadmap/STATUS.md`; `roadmap/SEASON_2026.md`
- `../../src/weekly_decision_cycle.py`; `../../src/ir_replacement.py`; `../../src/ir_roster_state.py`; `../../src/transaction_manager.py`
- `patches/PATCH_PROTOCOL.md`; `TOOLS.md`; `MEMORY.md`; `USER.md`
