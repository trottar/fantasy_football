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

**WEEKLY LINEUP LOCK AUTHORITY - STRUCTURAL CORRECTION LOCAL-APPLIED / VALIDATED.**

The October 4 post-multi-K fresh cycle preserved a valid decision-time snapshot and
prospective capture, passed operational health, and produced all nine receipt rows.
Its lineup channel nevertheless authorized an impossible perturbation: locked
bench WR Jakobi Meyers was selected into the starting lineup.

Source inspection proved the defect is in `weekly_decision_cycle._default_lineup`:
it computed lock information but did not constrain `optimize_lineup` or
`action_required` with the commissioned lock authority.

The authorized correction is now local-applied/validated in the control root:
locked starters are frozen in their current slots, locked bench players are
excluded from candidate optimization, only unlocked players compete for remaining
legal slots, and unresolved lock/slot state fails closed as
`INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY`.

Validated candidate identities:
- `src/weekly_decision_cycle.py` SHA-256
  `b48162719044e625e32f23b882d9030c1bf22323a473b11a48d200f30731b852`;
- Git blob `7969052173582e7b10bbdd846fb9f72ad104d676`;
- regression SHA-256
  `c9046463d090088f6ff290420a185c77c245f10a4558de0a42101f7632a4461d`;
- regression Git blob `4cd790e3cf82c3a5dd66e1aece8f4d5272e68c79`.

The October 4 four-offer specialist frontier is valid diagnostic evidence after
the multi-K repair, but no lineup or trade action is executable until this lineup
correction is source-published, runtime-commissioned, and followed by a fresh
decision-time weekly rerun.

## Verified State

- Runtime baseline: `v0.36-repack1`, internal `VERSION = 0.36` - **COMMISSIONED**, but still carries the pre-lineup-fix weekly authority.
- Gate A, B1, B2a, B3, Gate B5, and the specialist multi-K correction remain **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2b remains **DEFERRED / FAIL-CLOSED / NO FUTURE CAPACITY CREDIT**.
- October 4 snapshot UTC `2026-10-04T21:30:24.707083+00:00` and capture UTC `2026-10-04T21:30:25.525534+00:00` are **VALID IMMUTABLE PROSPECTIVE EVIDENCE**.
- October 4 operational health: **PASS**; receipt inventory: **9/9**, but action authorization is invalidated by the lineup-lock defect.
- Fresh-cycle lock scope from commissioned timing authority: players 13 locked / 1 unlocked / 0 unknown; specialists 1 locked / 1 unlocked / 0 unknown.
- The defective lineup action attempted to move locked-bench Jakobi Meyers into the starting lineup.
- The four post-multi-K specialist offers are DST-only compositions; none reintroduces unsupported multi-K ownership.
- Lineup-lock correction source preflight v1: **SUPERSEDED HARNESS PATH-PARSER FAILURE / NON-MUTATING**.
- Lineup-lock correction source preflight v2: **PASS / NON-MUTATING**; exact two-path candidate validated.
- Exact candidate is now **LOCAL-APPLIED / VALIDATED**; source publication and runtime commissioning are pending.
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

Publish the exact local-applied lineup-lock source/test candidate from remote base
`1cfce15ba6838901883dfcfd60132a87bbe3f2f7`, then commission the published
`src/weekly_decision_cycle.py` into `v0.36-repack1`.

After runtime commissioning, create a new decision-time Week 4 snapshot and
prospective capture and rerun the complete nine-channel weekly receipt. Do not
reuse the October 4 defective lineup action or execute any of its four specialist
trade offers as current authority.

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
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
