# Current Project State

---
state_updated: 2026-09-30
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_orchestration_recovery
active_workstream: memory_semantic_integrity_hardening
memory_refinement_step: active_memory_semantic_integrity
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: semantic_integrity_hardened
---

## Active Objective

Keep the weekly-decision recovery state truthful and fail closed while preventing
repository memory from becoming structurally valid but semantically stale. No
production football/model/application repair is authorized by this memory/tooling
checkpoint.

## Current Work Item

**ACTIVE MEMORY SEMANTIC INTEGRITY HARDENING.**

The read-only Week 4 source/design audit is already the durable predecessor
checkpoint. The active-memory audit found deterministic contradictions that the
strict memory checker did not reject: stale self-publication, stale stable-handoff
residue, past-week calendar/status language, incomplete decision indexing, and
missing weekly decision-receipt/template contracts.

This checkpoint hardens only durable memory, memory-health tooling/tests, and
weekly record templates. The fail-closed weekly production orchestrator remains
designed but not authorized or implemented.

## Verified State

- Commissioned runtime baseline remains `v0.36-repack1`, internal `VERSION = 0.36`.
- Week 4 week-open and pre-lock captures remain valid frozen prospective evidence.
- The earlier one-for-one player-trade HOLD remains valid only for that narrow
  channel scope.
- Roster-wide Week 4 completion remains `INCOMPLETE_COVERAGE`; no broader HOLD or
  NO-ACTION authority exists.
- Read-only source/design audit established that the production CLI/GUI expose
  lineup, player actions, DST, kicker, and trade operations independently with no
  fail-closed weekly completion state machine above them.
- Existing calculation authorities remain reusable; missing orchestration and
  capability gaps remain explicit blockers.
- The repository-memory audit classified
  `ACTIVE_MEMORY_SEMANTIC_INTEGRITY_GAP = CONFIRMED`.
- Hardening carriers v1-v4 all failed without a durable checkpoint: v1/v2 on
  deterministic predecessor-marker defects, v3 on repository-root pytest
  over-collection, and v4 on application-test execution against the split
  control-root surface. v3/v4 reported rollback to the exact predecessor state.
- The successor memory/tooling design uses exact predecessor identities,
  whole-file result payloads rather than guessed text-patch anchors, and
  validation scoped to the authority surface actually modified.
- No football/model/application source, runtime, transaction, or persistence
  state is changed by this checkpoint.

## Calendar / Evidence Gates

- Week 4 prospective captures remain immutable evidence and must not be backfilled.
- A material Week 4 status/practice/roster/market change before an affected lock
  requires a fresh decision-time capture before consequential action.
- Missing historical Week 4 action-channel execution remains missing; it is not
  reconstructed as contemporaneous evidence.
- Week 3 Data/MC closure remains blocked behind the weekly-decision orchestration
  recovery.
- Phase 1E persistence activation remains separately gated and unauthorized.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K` for internal valuation: players compare to players, DST to
  DST, and kickers to kickers.
- Channel separation is not a prohibition on DST/K participation in league-legal
  transactions; cross-channel composition occurs only at complete-roster utility
  boundaries.
- User examples may open an investigation but never define production search
  scope.
- `screen != authority`.
- Missing decision coverage is `INCOMPLETE_COVERAGE`, never implicit HOLD.
- Missing/stale required health is `BLOCKED_HEALTH`, never implicit PASS.
- `v0.X` remains a-priori; observed 2026 outcomes may not tune it.
- The memory-health checker may enforce deterministic repository-state semantic
  contracts, but it may not infer football truth or substitute for weekly
  decision/operational-health receipts.

## Exact Next Action

Complete this memory/tooling checkpoint through the established human-in-the-loop
local-apply, isolated-staging, publication, and remote-verification sequence.
After remote verification, stop at the explicit production source-change
authorization boundary. If and only if production repair is authorized, begin
Gate A from the accepted orchestrator design: implement the fail-closed weekly
decision receipt/state machine and operational-health interface before closing
additional action-family gaps.

Week 3 closure remains blocked until the repaired orchestration is
source-published, runtime-commissioned, and proven by a fresh complete weekly
cycle.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `MAINTENANCE.md`
- `USER.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `decisions/D-026_ACTIVE_MEMORY_SEMANTIC_INTEGRITY.md`
- `decisions/WEEKLY_DECISION_ORCHESTRATOR_DESIGN_2026-09-29.md`
- `evidence/REPOSITORY_MEMORY_SEMANTIC_INTEGRITY_AUDIT_2026-09-30.md`
- `evidence/WEEKLY_DECISION_SOURCE_DESIGN_AUDIT_2026-09-29.md`
- `investigations/WEEKLY_DECISION_ORCHESTRATION_RECOVERY_2026-09-29.md`
- `templates/WEEKLY_DECISION_RECEIPT.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
