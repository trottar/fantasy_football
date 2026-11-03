# Current Project State

---
state_updated: 2026-11-02
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week9_portable_v2_operator_completion
active_workstream: existing_portable_v2_ranked_mc_decision_board
memory_refinement_step: none
nfl_week: 9
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Finish the existing October 27 Windows 10/11 portable v2 fantasy-football application**, not another exporter, prototype, or narrow MC diagnostic. Acceptance: the recurring GUI procedure in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md` with prospective capture, nine-channel MC, live reconciliation, legal transaction consequences, ranked contingencies, human ESPN approval, and independently tested portable startup/restart. Preserve v0.36 kernels and private evidence.

## Current Work Item

- Week 9 publication `c207a65a0e10b701f90b8ee3167f017ef99e154a` is independently remote verified. The frozen certification source join was installed and **offline-accepted** in the existing October 27 portable v2 (`tools/operations/weekly_operator_v2.py` Git blob `eb5990de21d2bd80d701fdbfb218dd71db17c2a7`). Do not rerun prior apply/staging/push/runtime-sync gates.
- Portable v2 root: `L:\Projects\fantasy_football_portable_win10_11_20261027_v2\fantasy_football`; runtime `fantasy_season_v0_36_repack1` within it. The commissioned v0.36 kernels and frozen evidence were unchanged by the Week 9 operator sync. Independent-machine acceptance, action certification and scheduler remain uncommissioned.
- Current defect: the installed GUI presents native MC candidates, alternatives, intervals and risks across several separate panels and can show saved prior-week outputs without an unmistakable current-week freshness boundary. The next patch adds a **read-only, ranked MC opportunity board** above the existing panels; it uses only existing frozen evidence, not new model evaluations. Numeric scores rank only within comparable P/D/K/trade groups.

## Verified State

- Source checkpoint `c207a65a0e10b701f90b8ee3167f017ef99e154a` parent/tree were verified, 1,113 full pytest passed in isolated staging, and the published operator was installed into existing portable v2 with `STATUS=SYNCED_ACCEPTED` and offline report/status acceptance. Action authority remains `NONE`.
- Commissioned baseline remains `v0.36-repack1`. Channel-separated stochastic P/D/K evaluation, multi-player trades, specialist streaming and complete-roster response remain unchanged; 2026 results do not tune v0.X.
- Historical Oct 28 native Week 8 receipt was `COMPLETE / ACTION_REQUIRED` with trade candidates, while full ESPN transactions remained uncertified. Oct 29 scoped MC was not a whole-roster HOLD. Those reports are historical, not Week 9 recommendations.
- The current saved-receipt GUI is an observability/reporting view, not a live weekly recommender. A future Week 9 native receipt requires prospective data and independently verified current action legality. The new ranked board must **never** turn stale or missing evidence into a transaction recommendation.

## Calendar / Evidence Gates

Week 9 Monday is November 2, 2026; a fresh Week 9 prospective capture and exact decision-time evidence, if not already frozen before relevant individual kickoffs, are mandatory before action. Weeks 7-8 historical observations must not become current authority or be backfilled. Protect the next real game/claim deadlines; no uncommissioned scheduler or automatic ESPN writes. The current change is code/source-only and must not read private evidence, run MC or cause a capture during installation.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `Delta U = U(S + delta S) - U(S)`; common-random-number paired MC; ownership and field response; manager behavior separate from football utility; `screen != authority`; `MC -> Data -> closure -> diagnosis -> calibration`. No ESPN writes without specific human approval. Raw private logs/cookies/IDs and frozen evidence remain local.

## Exact Next Action

**Implement and test the existing GUI's ranked MC decision board from already-frozen native evidence**. The pure board must show lineup/IR first, then player, DST, K, and trades, with within-channel MC scores/intervals and explicit missing coverage. On Week 9, label saved Week 8 advice historical and forbid action promotion. Change only the GUI reporting module, the new pure decision-board module, tests and memory/evidence; preserve all current football and manager kernels and all private data.

Then use guarded local `.ffpkg` source apply, targeted and full staging tests, separate commit/push and **separate existing-portable runtime sync** for the two GUI module files. Do not run the uncommissioned supervised trial merely as infrastructure proof. Current-week ranked advice can only follow a prospective Week 9 native receipt; the board cannot fabricate new MC or certifiable ESPN legality. Scheduler is deferred.

## Relevant References

- `USER.md`, `handoffs/CURRENT_HANDOFF.md`, `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`, `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`, `architecture/WEEKLY_DECISION_COMPLETION.md`.
- `evidence/WEEK8_WEDNESDAY_SPECIALIST_GUI_DISPLAY_2026-10-28.md`; `evidence/WEEK8_B2B6_CONDITIONAL_POSITION_REBALANCE_GATE_2026-10-29.md`; `evidence/WEEK8_CONTINUITY_PORTABLE_V2_RECONCILIATION_2026-10-29.md`.
- `../../tools/operations/weekly_operator_v2.py`; `../../tools/operations/action_certification.py`; `../../tools/operations/weekly_operator_review.py`; `../../tools/operations/weekly_operator_controller.py`.
- `evidence/WEEK9_PORTABLE_V2_FROZEN_TRADE_JOIN_2026-11-02.md`; `evidence/WEEK9_MC_DECISION_BOARD_2026-11-02.md`.
- `../../src/gui/weekly_decision_view.py`; `../../src/gui/weekly_mc_decision_board.py`.

`durable_memory_updated: true`
