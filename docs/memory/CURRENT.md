# Current Project State

---
state_updated: 2026-10-04
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_gate_b_capability_closure
active_workstream: weekly_decision_lineup_lock_authority_correction
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Recover a causally valid Week 4 roster-wide decision state through the commissioned
Gate A/B control plane while preserving channel, health, decision-time, and
specialist-policy boundaries.

The October 3 fresh Gate B5 cycle achieved complete 9/9 coverage and operational
health, but its sole action channel exposed a structural specialist-trade defect:
four of six actionable offers derived material value from post-trade two-kicker
fixed ownership even though the commissioned K channel explicitly disables general
two-kicker `CARRY2`. The frozen cycle remains valid evidence of the defect, but its
specialist-trade frontier is not executable.

## Current Work Item

**WEEKLY LINEUP LOCK AUTHORITY - SOURCE-PUBLISHED / RUNTIME-COMMISSIONED.**

Source checkpoint `5dba8ea39f5b0cdeb16203b7a423cc6fe7849b52` is pushed and
remote-verified. The exact lock-aware weekly lineup authority is commissioned in
`v0.36-repack1`.

Commissioned `src/weekly_decision_cycle.py`:
- SHA-256 `b48162719044e625e32f23b882d9030c1bf22323a473b11a48d200f30731b852`;
- Git blob `7969052173582e7b10bbdd846fb9f72ad104d676`.

Runtime validation passed exact published source/test identity, import-root smoke,
the frozen October 4 Meyers/Kamara timing probe, locked-bench exclusion,
locked-starter preservation, fail-closed unknown-lock handling, targeted/full
pytest, compileall, and zero validation residue. Rollback was not required.

The October 4 snapshot/capture and defective lineup action remain immutable
evidence. The four specialist offers from that receipt remain diagnostic evidence
only and are not executable. Current authorization requires a fresh decision-time
snapshot/capture and complete nine-channel weekly rerun through the corrected
commissioned runtime.

## Verified State

- Runtime baseline: `v0.36-repack1`, internal `VERSION = 0.36` - **COMMISSIONED**.
- Gate A, B1, B2a, B3, Gate B5, specialist multi-K correction, and lineup-lock correction are **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2b remains **DEFERRED / FAIL-CLOSED / NO FUTURE CAPACITY CREDIT**.
- Lineup-lock source checkpoint: `5dba8ea39f5b0cdeb16203b7a423cc6fe7849b52`.
- Commissioned weekly-decision source SHA-256: `b48162719044e625e32f23b882d9030c1bf22323a473b11a48d200f30731b852`.
- Commissioned weekly-decision Git blob: `7969052173582e7b10bbdd846fb9f72ad104d676`.
- Runtime validation: published identity PASS; import-root smoke PASS; locked-bench exclusion PASS; locked-starter freeze PASS; unknown-lock fail-closed PASS; frozen Oct. 4 Meyers/Kamara probe PASS; targeted/full pytest PASS; compileall PASS; validation residue NONE; rollback false.
- October 4 snapshot UTC `2026-10-04T21:30:24.707083+00:00` and capture UTC `2026-10-04T21:30:25.525534+00:00` remain **VALID IMMUTABLE PROSPECTIVE EVIDENCE / NOT CURRENT AUTHORIZATION**.
- October 4 raw receipt inventory was 9/9 with health PASS, but its lineup action was invalidated by the now-corrected lock-authority defect.
- The four October 4 post-multi-K specialist offers remain **DIAGNOSTIC EVIDENCE / NOT EXECUTABLE** pending fresh reauthorization.
- General K `CARRY2` remains **DISABLED / UNCHANGED**.
- No observed 2026 outcome has tuned v0.X. Phase 1E persistence remains disabled.

## Calendar / Evidence Gates

- Week 4 prospective captures are immutable; never backfill a missed state.
- Before a consequential Week 4 action, refresh decision-time state/health if any
  material roster, injury/practice, availability, market, or lock information has
  changed.
- B2b may reopen only from fresh qualifying current-status, freshness,
  quantification, and binding evidence.
- Week 3 Data/MC closure remains blocked until a later fresh complete weekly receipt
  matrix passes.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; compose only at complete-roster state boundaries.
- Player-only and specialist authorities remain distinct.
- Manager behavior remains separate from football utility.
- `screen != authority`; raw measurements outrank derived classifiers.
- Missing legal action coverage is `INCOMPLETE_COVERAGE`, never implicit HOLD.
- Current-week lock semantics must include kickoff/snapshot timing where the
  commissioned authority does.
- Do not convert the disabled general two-kicker `CARRY2` policy into evidence that
  an otherwise league-legal open-slot kicker acquisition is irrelevant.
- No future IR-capacity credit is authorized while B2b is deferred.
- `v0.X` remains a-priori; observed 2026 outcomes may not tune it.

## Exact Next Action

Create a **new decision-time Week 4 snapshot and prospective capture** through the
corrected commissioned `v0.36-repack1` runtime, then rerun the complete
nine-channel weekly decision receipt and operational-health matrix.

Preserve current lock semantics. Do not reuse the October 4 21:30 UTC
snapshot/capture as current authorization, do not execute its defective lineup
action, and do not execute any of its four specialist offers unless a fresh
post-commissioning receipt reauthorizes them.

B2b remains deferred/fail-closed and contributes no future IR-capacity credit.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `MAINTENANCE.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `evidence/WEEK4_IR_COMPLETION_FRONTIER_AND_B2B_CORRECTION_2026-10-02.md`
- `evidence/WEEK4_IR_ADAPTER_PREFLIGHT_REALIGNMENT_2026-10-02.md`
- `evidence/WEEK4_IR_MOVE_PLUS_ADD_SOURCE_VALIDATION_2026-10-02.md`
- `evidence/WEEK4_IR_MOVE_PLUS_ADD_RUNTIME_COMMISSIONING_2026-10-02.md`
- `evidence/WEEK4_SPECIALIST_TRADE_MULTI_K_BOUNDARY_2026-10-03.md`
- `evidence/WEEK4_SPECIALIST_TRADE_MULTI_K_RUNTIME_COMMISSIONING_2026-10-03.md`
- `evidence/WEEK4_LINEUP_LOCK_AUTHORITY_DEFECT_2026-10-04.md`
- `evidence/WEEK4_LINEUP_LOCK_AUTHORITY_RUNTIME_COMMISSIONING_2026-10-04.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
