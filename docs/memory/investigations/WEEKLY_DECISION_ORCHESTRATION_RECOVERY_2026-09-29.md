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
## Read-Only Source / Design Audit

Source checkpoint audited:
`c21bfce9a5dd94f9269b7749ea10ea916d7c91e3`.

No production file was modified.

### Orchestration

`fantasy.py` exposes `week-lineup`, `roster-actions`, `defense-channel`,
`kicker-channel`, `trade-eval`, and `trade-search` independently. The GUI/service
likewise exposes independent player, specialist, and trade methods.

There is no production object that inventories required channel receipts and
fails closed before roster-wide completion language.

### Player actions

The broad player action engine already owns the required player-channel
counterfactual mechanics: legal add/drop enumeration, paired predictive MC,
waiver-acquisition behavior, released-player league-state response, and final
classification.

Reuse it; do not create a second player optimizer.

### Specialists

`specialist_policy_v032` is the commissioned DST/K authority and composes
same-channel policy effects into complete-state utility. Its current initial
dynamic market includes guaranteed FREEAGENT specialists while explicitly
excluding current WAIVERS.

The repair must add a distinct current-waiver acquisition state/behavior layer;
WAIVERS must not be fabricated as guaranteed FREEAGENTs.

### Trades

`evaluate_trade` can evaluate up to the configured two assets per side and
already handles unequal player packages with modeled legal post-trade release/fill
effects. Automated `search_trades` nevertheless enumerates only one-for-one
player offers.

Specialist assets are explicitly rejected. A complete repair therefore needs a
package-search frontier broader than one-for-one plus specialist-inclusive trade
composition that preserves `P ⊕ D ⊕ K` internally.

### IR / injury state

The ESPN normalized league snapshot already preserves `lineup_slot_id`,
normalized `IR`, `eligible_slots`, and team `move_to_ir` transaction counts.
League config has one IR slot.

The repair should model legal roster-state transitions from these direct facts,
not from a player name or injury-label heuristic alone.

Current-week availability has explicit evidence/timing state. Future weeks retain
the generic commissioned availability approximation, so known decision-time
multiweek absence horizon is not yet an explicit roster-action state.

### Health

Reusable health primitives exist but are fragmented:

- provider/source status in the snapshot/service;
- `verify_capture_integrity` plus the pre-data firewall;
- `shadow_persistence_state`;
- strict structural durable-memory health;
- runtime `VERSION` and exact dependency identities used by commissioning/
  diagnostics.

There is no unified weekly operational-health receipt. Strict memory health must
remain only one component, never a substitute for runtime/data/decision health.

## Repair Design

Canonical design record:
`../decisions/WEEKLY_DECISION_ORCHESTRATOR_DESIGN_2026-09-29.md`.

Implementation must be fail-closed from the first source patch:

1. add the completion/health receipt state machine;
2. wire existing commissioned authorities into it;
3. report unsupported families as `INCOMPLETE_COVERAGE`;
4. add missing capabilities behind that gate;
5. prohibit roster-wide COMPLETE/NO_ACTION until every required receipt passes;
6. expose the same authoritative receipt through CLI, GUI/service, and chat;
7. commission with targeted tests, full pytest, compileall, exact package QA,
   runtime synchronization, and a fresh complete decision-time cycle.

Production source remains not yet authorized.
