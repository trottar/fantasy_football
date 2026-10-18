# Current Project State

---
state_updated: 2026-10-18
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_decision_operations
active_workstream: guarded_wednesday_saturday_mc_launch
memory_refinement_step: none
nfl_week: 6
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Operate protected **Wednesday and Saturday** six-provider prospective captures and complete nine-channel Monte Carlo runs with sufficient time for legality verification, approval, and actual player-specific lineup locks. Sunday morning must not be required. Keep commissioned v0.36-repack1, causal capture rules, and all football valuation machinery unchanged.

## Current Work Item

**WEEK 6 DEADLINE LOSS CLASSIFIED; WEDNESDAY/SATURDAY OPERATING CONTRACT PUBLISHED; GUARDED MC LAUNCHER NEXT.**

A pre-kickoff Sunday October 18 Week 6 snapshot/capture passed integrity, but the approximately 40-minute nine-channel MC finished after the 9:30 a.m. EDT London kickoff. The recommended Jakobi Meyers-for-Mark Andrews lineup was no longer legal because a proposed starter was locked on the bench. The old Sunday operation checked capture timing rather than completion plus approval/action time. The local Sunday guard later confirmed material ESPN state drift. No lineup, waiver, IR, or trade was submitted. The 80-minute deadline-budget helper is source-published and tested but was not wired into the 40-minute MC entrypoint.

## Verified State

- **Published checkpoint:** `1aef72976fb78195148111a1d32fe1684ccb8bfb` is remote-verified, parent `68dfabed5088a6ddf90a5d3af4f5497bf25f334a`; exact six paths were staged and published with 193 schema-2 memory-manifest entries. This checkpoint established `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`, `tools/operations/deadline_budget.py`, and its tests. Commissioned runtime `fantasy_season_v0_36_repack1` (`VERSION=0.36`) was not modified or resynchronized.
- **Sunday Week 6 frozen evidence:** snapshot `data/season_snapshots/20261018T131404Z/snapshot.json` UTC `2026-10-18T13:14:28.631418+00:00`; bound capture `data/season_predictions/closure/pregame_2026_w06_20261018T131437Z.json` SHA-256 `120761014402f7c145c5b80a4f78a71467cc30be024b7266b6ea39ba6ab35c1b`; 6 providers PASS, 190 PRE, 15 POST_LOCK, 33 UNKNOWN. Only PRE is prospective; others cannot be backfilled.
- **Sunday nine-channel receipt:** `data/season_decisions/weekly_decision_receipt_20261018T135542Z.json` SHA-256 `937501f0a6b28e5297aa693b98679fb10542f3766b0071c271d011e38d411984`. Health PASS; proposed lineup Meyers in/Andrews out, projected 114.8884; three specialist-inclusive trade offers have 48-hour review and Week 7 effect. Other acquisition/player-trade channels returned narrowly scoped HOLD. IR `INCOMPLETE_COVERAGE:GATE_B_IR_MOVE_PLUS_ADD_VALUE_ADAPTER`, native overall `INCOMPLETE_COVERAGE`; no ESPN action authority.
- **Post-MC ESPN guard:** 2026-10-18 16:46 UTC live ESPN read found one saved selected bench player locked, with 2 owner moves, 33 roster-state changes, 2 market membership changes, 101 market-state changes, changed transactions, and blocked saved slot assignment. Bass remained starting K. No ESPN/Git writes.
- **New launcher development boundary:** `tools/operations/guarded_weekly_cycle.py` is an opt-in source-bound control-root launcher that checks fresh six-provider snapshot/capture integrity, owned and candidate kickoff times, and 80-minute budget **before** native MC invocation. It rechecks just before launching and marks an expired completion window after MC; it cannot certify fresh live ESPN legality or transaction permission. This is not an in-place patch to commissioned `fantasy.py` and does not intercept other unguarded callers. Requires independent local apply, staging/publication, and operator acceptance before production use.
- Week 5 closure is partially complete: exact observed ESPN fantasy yield exists, while component, availability, matchup/regret and calibration closure remain open. Do not use 2026 outcomes to tune a-priori v0.X. Earlier captures and receipts are immutable.

## Calendar / Evidence Gates

Wednesday October 21 is the protected Week 7 primary run; Saturday October 24 is the second run. The earliest affected individual Thursday, Saturday, Sunday, Monday, international or holiday kickoff overrides weekday defaults. Budget initially MC 40 minutes + verification 15 + user action 15 + safety 10 = 80 minutes **before kickoff**. Unknown owned-player lock or insufficient slack must block actionable MC launch. Material fresh status, trade, market, ownership or lineup changes require re-evaluation without backdating. A preflight PASS is timing-only; **post-MC ESPN recheck of exact roster, injury, lock and slots is mandatory**; human approval required before any ESPN transaction. Sunday is optional fast recheck, never mandatory early full MC. Full roster-wide `COMPLETE/HOLD` is forbidden while IR or any required nine-channel receipt is incomplete.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L x sigma x A x epsilon`, `P ⊕ D ⊕ K`, uncertainty-aware paired MC and complete-roster `Delta U = U(S + delta S) - U(S)`. Football response remains distinct from manager behavior; `screen != authority`. Maintain `MC -> Data -> closure -> diagnosis -> calibration`, pre-outcome frozen predictions and `v0.X` a-priori isolation. Secrets and authenticated ESPN payloads stay local. Control-root local apply, staged clone, commit/push, remote verification, runtime synchronization and commissioning are separate authorities.

## Exact Next Action

**Validate and locally apply the source-bound protected MC launcher on the control root.** Verify exact current source identities, existing `deadline_budget.py`, targeted success and failure fixtures, source/compiled output, strict memory health, idempotent apply and rollback. The launcher must block too-late or unverified runs *before* calling `fantasy.py weekly-cycle`, without changing its model/MC. After operator receipt: stage exact reviewed paths with schema-2 manifest, separately publish under guards, then run an explicit local check-only probe and commission the **opt-in launcher workflow** before Wednesday Week 7. Until accepted, use the existing commissioned runtime and protected schedule, never claim automatic enforcement from a standalone helper. Prepare Week 7 first run well ahead of first affected lock; repeat Saturday, defer unrelated development.

## Relevant References

- `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`
- `evidence/WEEK6_SUNDAY_MC_DEADLINE_INCIDENT_2026-10-18.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`; `roadmap/SEASON_2026.md`
- `patches/PATCH_PROTOCOL.md`; `COMMUNICATION.md`; `USER.md`
- `../../tools/operations/deadline_budget.py`; `../../tools/operations/guarded_weekly_cycle.py`
- `../../src/weekly_decision_cycle.py`; `../../fantasy.py`
