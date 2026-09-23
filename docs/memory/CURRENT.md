# Current Project State

---
state_updated: 2026-09-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: week3_decision_management
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Protect and operate the causally valid Week 3 decision state through lineup lock
using prospective decision-time information. Phase 1D remains the next engineering
frontier but is secondary to the Week 3 calendar gate.

## Current Work Item

**Week 3 decision management: ACTIVE / WEDNESDAY DECISION STATE SECURED.**

The Sep 22 week-open capture remains immutable. A fresh Sep 23 decision-time
snapshot/capture was frozen before outcomes, then player, DST, kicker, matchup,
and lineup surfaces were recovered and reconciled without model retuning.

Current Wednesday decisions:

- QB/RB/WR/TE transaction channel: **HOLD**;
- DST channel: **HOLD Lions D/ST**;
- kicker channel: **HOLD Harrison Butker**;
- planning lineup FLEX: **Mark Andrews**;
- primary live uncertainty: **Puka Nacua**, currently modeled at 75% active from
  provisional status evidence;
- Puka OUT contingency: Carnell Tate and Rashid Shaheed at WR with J.K. Dobbins
  at FLEX.

No current waiver, DST, or kicker transaction is authorized by a resolved model
edge.

## Verified State

- Authoritative commissioned runtime: **v0.36-repack1**, internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow: **RUNTIME COMMISSIONED**.
- Phase 1B closure shadow: **SOURCE PUBLISHED / RUNTIME COMMISSIONED**.
- Phase 1C P/D/K observability: **COMPLETE / SOURCE PUBLISHED / RUNTIME
  COMMISSIONED**.
- Persistent observability sink: **DISABLED**.
- Phase 1D market/manager-behavior observability:
  **NOT INSTRUMENTED / READ-ONLY DISCOVERY READY**.
- Week 3 week-open reference:
  `pregame_2026_w03_20260922T141055Z.json`,
  SHA-256
  `82ee7e89a328930931aa88d9a0af4b5217586cbe4792d50b7b384fcf71125154`.
- Sep 23 decision snapshot:
  `20260923T175449Z/snapshot.json`,
  SHA-256
  `7e425f73c3d7c33e1bdc4378369535aba5d78092acd1af50d0411b9e32c62160`.
- Sep 23 prospective capture:
  `pregame_2026_w03_20260923T175539Z.json`,
  SHA-256
  `16111464877bbacb8425ee2c4f4edfcd88efea49581a00b9c18c085d22f2fe14`.
- Player-values recovery authority:
  exact predecessor artifact SHA-256
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.
- Player paired action evaluation completed all 72 SCREEN1 actions at 1,024
  universes and stopped for classification futility; no resolved positive
  player-channel edge survived.
- Player recommendation: **HOLD**.
- Recovered matchup diagnosis:
  fixed win 59.4%, realistic win 62.5%, modeled score
  `117.9 +/- 22.4` versus `108.0 +/- 20.8`.
- Exact-values lineup reconciliation: **PASS**.
- Planning expected-value FLEX: **Mark Andrews**, not Rashid Shaheed.
- Recovered chat report, roster action audit, and prediction audit were persisted
  in the commissioned runtime.
- No football/model/application source was changed by the decision/recovery
  packages.
- No repository source was changed by the decision/recovery packages.
- No observed 2026 outcome was used to tune v0.X.

Canonical Week 3 evidence:
`evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`.

## Calendar / Evidence Gates

- Week 3 prospective evidence is causally protected; do not reconstruct missed
  states after outcomes.
- The Wednesday decision state is a snapshot, not a permanent Sunday decision.
- Run a new decision-time refresh/capture when material injury/status information
  changes and before committing consequential lineup or transaction changes.
- Puka Nacua is the principal current status uncertainty; official practice
  evidence was unavailable in the Wednesday feed, so the 75% active probability
  remains provisional.
- Interaction-grid evidence was unavailable for current starters in the recovered
  report; neutral/base fallback remained active and must be treated as a model
  limitation, not silently repaired from hindsight.
- No observed 2026 result may tune v0.X.
- Manager-behavior observation/calibration and persistent evidence remain
  separately gated.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- Cross-channel coupling remains at complete-roster utility/state boundaries.
- Manager behavior is separate from football utility.
- `screen != authority`; the player HOLD result is accepted because the
  uncertainty-aware paired action machinery itself reached the futility
  classification, not because of a cheap screen alone.
- Frozen week-open and decision-time captures are immutable evidence.
- Diagnostics remain shadow-only/non-persistent unless separately gated.

## Exact Next Action

At the next material Week 3 injury/status update, or before the relevant Sunday
lineup locks if no earlier material change occurs, run a fresh season sync and
prospective decision-time capture, then re-evaluate the lineup with particular
attention to Puka Nacua. Preserve the Wednesday capture unchanged.

If no football decision needs immediate refresh before then, Phase 1D may resume
only as read-only boundary discovery and must yield immediately to the next
calendar capture gate.

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
- `evidence/PHASE1C_PLAYER_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`
- `memory/2026-09-23.md`
- `../../src/market_manager.py`
