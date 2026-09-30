# Weekly Decision Orchestration Recovery — 2026-09-29

---
status: OPEN_BLOCKING
classification: WEEKLY_DECISION_ORCHESTRATION_COMPLETION_GATE_FAILURE
scope: workflow_orchestration_and_health
football_model_tuning: forbidden
production_source_change: not_yet_authorized
---

## Question

How did a project with functioning player, DST, and kicker decision machinery
allow a Week 4 partial search to be communicated as if the roster decision cycle
were complete, and what contract must block recurrence before source repair?

## Established Facts

- The documented 2026 weekly cycle already required decision-time handling for
  waiver/add/drop, trade evaluation, DST/kicker streaming, and injury
  replacement.
- Week 3 evidence shows the broad player add/drop engine and separate DST/K
  evaluation were actually run.
- Week 4 one-for-one player trade search was valid for its narrow scope.
- Week 4 player waiver/free-agent and commissioned DST/K channels were not all run
  before broader HOLD language was used.
- The automated trade search covers one-for-one player trades only.
- The player trade evaluator can represent up to two assets per side but rejects
  specialist assets.
- The commissioned specialist dynamic policy excludes current WAIVERS from the
  guaranteed-free-agent acquisition pool.
- IR-move-plus-add and explicit multiweek injury-duration roster actions are not
  complete production action families.
- Validation tools exist, but no weekly operational health receipt was required
  as a completion precondition.

## Root Classification

The primary defect is not absence of football models. It is absence of a hard
**weekly orchestration/completion/health gate** above the existing subsystems.

Subsystem existence and prior successful use were incorrectly treated as if they
guaranteed future weekly execution.

## Blocking Requirements Before Production Repair

1. Make `architecture/WEEKLY_DECISION_COMPLETION.md` durable.
2. Withdraw roster-wide authority from incomplete Week 4 HOLD language while
   preserving raw prospective evidence.
3. Require full-roster/action-family scope independent of user examples.
4. Require fresh weekly operational-health receipts.
5. Design source repair against the contract before modifying production logic.
6. Commission the repair with targeted/full tests, compileall, exact artifacts,
   runtime evidence, and a fresh complete Week 4 decision cycle.

## Open Production Gaps

- unified weekly orchestrator/completion receipt;
- authoritative specialist current-waiver acquisition;
- automated multi-asset player trade search;
- specialist-inclusive trade evaluation;
- IR-move-plus-add;
- explicit multiweek injury-duration state where evidence supports it;
- integrated weekly operational-health gate.

## Non-Goals

- no v0.X empirical tuning;
- no player-specific heuristic patch;
- no manual recommendation substituted for missing production authority;
- no retrospective backfill of searches that were not run prospectively.

## Exit

This investigation closes only after the repaired weekly orchestration is
source-published, runtime-commissioned, and a fresh decision cycle proves all
required coverage and health receipts without user prompting.
