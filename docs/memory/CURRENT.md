# Current Project State

---
state_updated: 2026-10-18
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week6_sunday_lock_incident_to_week7_operational_recovery
active_workstream: protected_wednesday_saturday_mc_and_deadline_budget
memory_refinement_step: none
nfl_week: 6
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Protect **Wednesday and Saturday** prospective nine-channel runs before development. Avoid another Week 6 substitution lost to a ~40-minute MC finishing after player lock. No required early Sunday attendance. Preserve Week 6 immutable captures; leave v0.36-repack1 and nine-channel scientific authority unchanged.

## Current Work Item

**WEEK 6 SUNDAY CAPTURE SUCCEEDED; SAVED LINEUP ACTION EXPIRED DURING MC; WEEK 7 WEDNESDAY/SATURDAY OPERATIONS PROTECTED.**

Sunday's 09:14 EDT six-provider snapshot and pre-kickoff capture passed identity and binding. The complete native nine-channel receipt completed about 09:55 EDT, after the 09:30 London kickoff. Its Meyers-for-Andrews lineup recommendation was not executed. A 12:46 EDT fresh ESPN-only guard reported a saved selected player locked on the bench, material market/roster drift, and no legal saved lineup assignment. Native IR replacement is still `INCOMPLETE_COVERAGE`; no roster-wide completion or transaction authority exists. This is a deadline failure, not evidence of incorrect MC distributions.

## Verified State

- **Durable source / commissioned runtime:** remote-memory predecessor `68dfabed5088a6ddf90a5d3af4f5497bf25f334a` (not this candidate checkpoint); commissioned runtime `fantasy_season_v0_36_repack1` / `VERSION=0.36` unchanged. Local root is authoritative between checkpoints; local apply, isolated staged tree, commit/push, remote verification, and runtime commissioning remain separate.
- **Sunday October 18 snapshot/capture:** `data/season_snapshots/20261018T131404Z/snapshot.json`, snapshot UTC `2026-10-18T13:14:28.631418+00:00`; immutable capture `data/season_predictions/closure/pregame_2026_w06_20261018T131437Z.json`, SHA-256 `120761014402f7c145c5b80a4f78a71467cc30be024b7266b6ea39ba6ab35c1b`. Six providers/integrity/binding PASS; per-record kickoff PRE 190, POST_LOCK 15, UNKNOWN 33 (exclude non-PRE records from prospective closure). Bass owned at K; Butker not owned.
- **Sunday nine-channel receipt:** `data/season_decisions/weekly_decision_receipt_20261018T135542Z.json`, SHA-256 `937501f0a6b28e5297aa693b98679fb10542f3766b0071c271d011e38d411984`. Operational health PASS. Lineup ACTION (Meyers in / Andrews out; expected 114.8884) and three Week 7-effective specialist-inclusive trade offers were **proposals only**. Player/DST/K acquisition and player trades returned scoped HOLD. IR `INCOMPLETE_COVERAGE:GATE_B_IR_MOVE_PLUS_ADD_VALUE_ADAPTER`; native overall `INCOMPLETE_COVERAGE`.
- **Sunday live legality guard:** ESPN-only check `2026-10-18T16:46:27.085465+00:00`: frozen/live owned 200/200, market 852/852; owner moves 2, roster-state changes 33, market membership changes 2, market-state changes 101, transaction history changed, matchup/settings unchanged. Nine selected/current starters; Bass starting K. `LIVE_LINEUP_SLOT_LEGALITY=BLOCKED:SAVED_SELECTED_PLAYER_NOW_LOCKED_ON_BENCH`, `FRESH_MC_ESPN_INPUT_COMPARISON=MATERIAL_ESPN_DRIFT`, `CURRENT_ACTION_AUTHORITY=NONE`. The diagnostics did not change ESPN or Git.
- **Incident:** An early Sunday MC start was causally pre-kickoff but could not yield an executable lineup action by the first player lock. The first-kickoff gate checked capture timing, not **completion plus action**; the saved receipt did not contain exact ESPN slot assignments. Earlier Saturday outputs gave a legal candidate but real ESPN injury-status changes left refreshed decision authority unresolved. Do not retroactively label that stale Saturday output authoritative.
- **Earlier evidence:** Week 5 exact ESPN fantasy-yield selected observation closure remains available; component, availability, matchup/regret, and calibration work is open. Earlier Week 6 snapshots and captures remain immutable. Neither observed Week 6 outcomes nor arbitrary dates can tune v0.X.

## Protected Weekly Operating Contract

Canonical policy: `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`. Wednesday primary six-provider decision-time capture, all-nine-channel MC, and actionable review precede Thursday locks. Saturday final six-provider capture/MC and action review precede Sunday locks; execute changes Saturday if valid. Thursday, holiday, Saturday, Monday, international, and other atypical kickoffs override weekday defaults. Sunday is **optional** fast live verification, not a mandatory early-morning full MC. New feature development may not displace the Wednesday or Saturday operating cycle; use last **validated** runtime if development is unfinished.

A standalone **read-only deadline-budget preflight** `tools/operations/deadline_budget.py` is a first control-plane slice. It requires a verifiable next affected individual lock and budgets full-MC runtime, live legality check, user action time, and uncertainty margin *before* starting a new MC. It is not yet wired into the commissioned weekly-cycle, is not a football screen or MC, does not obtain schedules/ESPN data itself, and cannot confer action authority. Existing MC/capture execution gates remain unchanged.

## Calendar / Evidence Gates

Calendar capture gates are irreversible: no backdating, no relabeling POST_LOCK or UNKNOWN as PRE. Decision MC can finish after capture and produce valid prospective predictions, yet be operationally too late for specific actions. Deadline feasibility and recommendation authority are **distinct**. A preflight PASS authorizes neither a stale action nor a future lock guarantee. A post-MC fresh ESPN read must separately verify relevant player-by-player locks, availability, transaction state, exact slots, and material drift; then require user approval. An IR `INCOMPLETE_COVERAGE` is not a roster-wide HOLD. Trade review hours 48 and resulting week-of-effect must be respected.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L x sigma x A x epsilon`, `P ⊕ D ⊕ K`, paired MC, uncertainty propagation, complete-roster `Delta U`, behavior separation, and `screen != authority`. Prospective forecasts freeze before results; `MC -> Data -> closure -> diagnosis -> calibration`. Do not empirically tune v0.X from 2026. Do not submit lineup, IR, waiver, or trade actions without current authorizing evidence and user approval. Keep local authenticated raw ESPN responses, identifiers, secrets, and private runtime snapshots out of Git.

## Exact Next Action

**First validate and locally apply the protected-cadence/deadline-budget checkpoint; then stage/publish separately.** Validate its pure timing boundary tests, rendered memory health, deterministic carrier, and read-only/no-football-change scope. Mark it `LOCAL-APPLIED` only after a successful Windows runner receipt. After that, prepare **Week 7 Wednesday** using the unchanged commissioned runtime: verify actual fixture/individual lock deadlines, preflight at least 40 minutes of MC plus verification/action/safety budget, refresh six providers, freeze a new immutable prospective capture, run the complete nine-channel MC, review legality/health/drift, and deliver an executable approval-ready action plan while ample time remains. Repeat Saturday; no mandatory Sunday wake-up. Longer-term integrate a source-bound deadline gate directly into weekly orchestration only through a separate source/test/runtime checkpoint, without weakening MC or IR authority.

## Relevant References

- `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`
- `evidence/WEEK6_SUNDAY_MC_DEADLINE_INCIDENT_2026-10-18.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`; `roadmap/SEASON_2026.md`
- `patches/PATCH_PROTOCOL.md`; `COMMUNICATION.md`; `USER.md`
- `../../tools/operations/deadline_budget.py`; `../../src/weekly_decision_cycle.py`
