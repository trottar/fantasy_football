# Current Project State

---
state_updated: 2026-09-29
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_orchestration_recovery
active_workstream: memory_contract_hardening
memory_refinement_step: weekly_decision_completion_contract
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: blocking_workflow_failure
---

## Active Objective

Correct the durable operating contract before any infrastructure or football
source work resumes. A weekly fantasy decision cycle may not be called complete,
HOLD, or no-action unless every required roster-action channel and required
health gate has an explicit current receipt.

## Current Work Item

**WEEKLY DECISION ORCHESTRATION / COMPLETION-GATE FAILURE — BLOCKING.**

The Week 4 prospective captures remain valid frozen measurements. The prior
one-for-one player-trade HOLD remains valid only for that narrow search scope.
Any broader interpretation that the Week 4 roster decision cycle was complete is
withdrawn.

This memory checkpoint is intentionally first. Do not resume Week 3 closure,
Phase 1E activation, roster transactions, or production-source repair until this
memory audit is remote-durable.

## Verified State

- Week 3 evidence shows the broad player add/drop engine and separate DST/K
  evaluations were actually exercised; the capability existed.
- Week 4 week-open and fresh pre-lock captures remain causally valid and
  integrity-checked.
- Week 4 automated trade search evaluated one-for-one QB/RB/WR/TE trades only.
- Week 4 did not run the full player waiver/free-agent channel before the earlier
  roster-level HOLD interpretation.
- Week 4 did not run the commissioned DST and kicker policy channels before that
  interpretation.
- Player waiver/free-agent, DST, and kicker subsystems already existed; the
  failure was missing orchestration/completion enforcement.
- `search_trades` is automated one-for-one player search. The underlying player
  trade evaluator can represent up to two assets per side, but automated
  multi-asset search is absent.
- Specialist assets are rejected by the current player trade evaluator; no
  specialist-aware trade evaluator is commissioned.
- The commissioned specialist dynamic policy starts from guaranteed current
  FREEAGENTs and excludes current WAIVERS from its authoritative dynamic pool.
- IR-move-plus-add is not an explicit ordinary action, and explicit multiweek
  injury-duration propagation is not represented as a roster-action state.
- Validation/health tools exist, but the weekly operating contract did not
  require a fresh health receipt before declaring decision completeness.
- No football/model/application source is changed by this checkpoint.

## Calendar / Evidence Gates

- Week 4 prospective evidence already captured remains immutable evidence.
- A material Week 4 status/practice change before an affected player's lock still
  preempts deferrable memory/publication work for a fresh causal capture.
- Missing action-channel coverage is not reconstructed as if it had been run.
- Week 3 Data/MC closure is blocked until the weekly decision completion contract
  is durable and the production orchestration gap is repaired.
- Phase 1E.4 persistence activation remains separately gated and unauthorized.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K` for valuation and response; this is not a prohibition on
  DST/K participation in league-legal transactions.
- Cross-channel transaction effects combine only at complete-roster utility/state
  boundaries.
- User-named examples never define search scope; the system must scan the whole
  relevant roster, market, and supported action family.
- `screen != authority`.
- Missing channel receipt means `INCOMPLETE_COVERAGE`, never implicit HOLD.
- Missing/stale required health receipt means `BLOCKED_HEALTH`, never implicit
  operational readiness.
- Observed 2026 outcomes still may not tune v0.X.

## Exact Next Action

If this memory-audit state is not yet remote-durable, publish this exact
memory-only checkpoint through the normal isolated staging/publication workflow.

Once remote `main` contains this state, perform a read-only source/design audit
for the weekly decision orchestrator and health gate. Do not modify production
source until that design is reconciled against
`architecture/WEEKLY_DECISION_COMPLETION.md`.

The first repaired weekly cycle must run from fresh decision-time state and
produce explicit receipts for every required channel and health gate before any
roster-wide HOLD/NO-ACTION conclusion.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `MAINTENANCE.md`
- `USER.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `architecture/SPECIALIST_CHANNELS.md`
- `investigations/WEEKLY_DECISION_ORCHESTRATION_RECOVERY_2026-09-29.md`
- `evidence/WEEKLY_DECISION_ORCHESTRATION_FAILURE_AUDIT_2026-09-29.md`
- `evidence/WEEK4_PROSPECTIVE_CAPTURE_AND_DECISION_2026-09-29.md`
- `evidence/WEEK4_PRELOCK_STATUS_GATE_2026-09-29.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
