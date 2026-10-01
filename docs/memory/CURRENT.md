# Current Project State

---
state_updated: 2026-10-01
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_gate_b_capability_closure
active_workstream: gate_b2_ir_open_slot_and_absence_state
memory_refinement_step: soft_threshold_compaction
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: active_state_compacted_for_b2
---

## Active Objective

Close the remaining Gate B capability gaps behind the commissioned Gate A control
plane without weakening causal or channel boundaries. Gate B1 is source-published
and runtime-commissioned. Gate B2 is now split by direct evidence into a current
IR/open-slot representation slice (B2a) and a decision-time multiweek absence
horizon slice (B2b).

## Current Work Item

**WEEKLY DECISION GATE B2 — IR/OPEN-SLOT + ABSENCE STATE.**

The sanitized Week 4 audits establish that this league has one IR slot, no
current IR occupant, and one roster player tagged `OUT` by ESPN. Normalized
`injury_status` matches raw ESPN `player.injuryStatus` for all 16 roster rows.
All 16 players advertise IR in `eligibleSlots`, including 12 `ACTIVE` players,
so `eligibleSlots` is generic slot compatibility and is not current IR-eligibility
authority.

No normalized or raw ESPN field supplies an explicit return week,
absence-through week, or other multiweek absence horizon. Therefore B2a may
represent current legal IR/open-slot state, but it may not treat the resulting
extra active-roster capacity as permanently available for season valuation.
B2b remains fail-closed until explicit decision-time horizon evidence exists.

## Verified State

- Runtime baseline: `v0.36-repack1`, internal `VERSION = 0.36` — **COMMISSIONED**.
- Gate A fail-closed weekly control plane — **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B1 specialist current-WAIVER coverage — **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
  Canonical commissioning evidence:
  `evidence/WEEKLY_DECISION_GATE_B1_SPECIALIST_WAIVERS_RUNTIME_COMMISSIONING_2026-10-01.md`.
- B1 commissioning-memory checkpoint is remote-durable at predecessor role
  `6363ded2a3c6b4fa09de6a8b7b274ebb076ebfea`; read the containing Git ref for
  the current checkpoint identity.
- B2 audit v1
  `weekly_decision_gate_b2_ir_absence_state_audit_v1_20261001` passed and proved
  one configured/open IR slot plus no explicit absence-horizon field. Its initial
  `eligible_slots`-based IR-eligibility interpretation is **SUPERSEDED** by the
  raw measurement that all 16 roster players expose IR slot compatibility.
- B2 audit v2
  `weekly_decision_gate_b2_ir_eligibility_rule_audit_v2_20261001` passed and
  established ESPN `injuryStatus` as the preserved platform-rule input: one
  `OUT` player is currently status-rule eligible for IR, with one open IR slot;
  normalized/raw player status matched 16/16.
- B2 classification:
  `B2_IR_MOVE_PLUS_ADD_PATCHABLE_ABSENCE_HORIZON_STILL_MISSING`.
- B2a source candidate is intentionally representation-only. It adds a pure IR
  roster-state authority plus the weekly-cycle adapter/test surface; it does not
  alter commissioned player/DST/K football physics or authorize a replacement
  recommendation without temporal capacity evidence.
- B2a source-preflight v1 failed **before modification** because strict memory
  health classified the prior `CURRENT.md` as `SOFT` on the Windows worktree.
  Control root and commissioned runtime remained untouched. No operator full
  B2a source validation was completed by that failed run.
- This maintenance checkpoint compacts active state and preserves the B2 audit
  lineage in
  `evidence/WEEKLY_DECISION_GATE_B2_IR_ABSENCE_AUDIT_2026-10-01.md`.
- Week 4 roster-wide completion remains `INCOMPLETE_COVERAGE` for B2b and the
  remaining trade families.
- No observed 2026 outcome has tuned v0.X. Phase 1E persistence remains disabled.

## Calendar / Evidence Gates

- Week 4 prospective captures are immutable; never backfill a missed state.
- A material status/practice/roster/market change before an affected lock requires
  a fresh decision-time capture before consequential action.
- The B2 audits are decision-time structural evidence, not permission to infer an
  unobserved return date or recovery horizon.
- Do not run a fresh roster-wide Week 4 completion cycle until required Gate B
  families are commissioned or explicitly not applicable under the completion
  contract.
- Week 3 Data/MC closure remains blocked until a later fresh complete weekly
  receipt matrix passes.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K` inside valuation; compose only at complete-roster state
  boundaries.
- ESPN `injury_status` supplies current platform IR-rule input. Generic
  `eligible_slots` must not be interpreted as current IR eligibility.
- Current IR/open-slot legality is distinct from future roster-capacity value.
  Without explicit decision-time absence/return horizon, do not propagate an IR
  opening as permanent season capacity.
- Manager acquisition behavior remains separate from intrinsic football value.
- `screen != authority`; raw measurements outrank derived classifiers.
- Missing action coverage is `INCOMPLETE_COVERAGE`, never implicit HOLD.
- Missing/stale required health is `BLOCKED_HEALTH`, never implicit PASS.
- `v0.X` remains a-priori; observed 2026 outcomes may not tune it.

## Exact Next Action

Regenerate the unchanged B2a IR roster-state source-preflight carrier against the
remote checkpoint containing this maintenance result, then run the operator
source preflight. Require exact three-path result identities, targeted B2a/Gate A/
B1 regressions, full repository `pytest`, `compileall`, strict memory health, and
diff checks before any B2a local apply.

Do not rerun the passed B2 audit probes or any Gate A/B1 source/runtime gates
unless new evidence invalidates them. Keep B2b absence-horizon valuation and the
remaining trade-family work separate from B2a.

## Relevant References

- `AGENTS.md`
- `MAINTENANCE.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `evidence/WEEKLY_DECISION_GATE_B1_SPECIALIST_WAIVERS_RUNTIME_COMMISSIONING_2026-10-01.md`
- `evidence/WEEKLY_DECISION_GATE_B2_IR_ABSENCE_AUDIT_2026-10-01.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
