# Current Project State

---
state_updated: 2026-10-03
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_gate_b_capability_closure
active_workstream: specialist_trade_multi_k_boundary_correction
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

**SPECIALIST TRADE MULTI-K BOUNDARY - SOURCE CANDIDATE LOCAL-APPLIED / VALIDATED.**

Fresh October 3 evidence reopened the previously commissioned specialist-inclusive
trade surface. The authoritative decomposition reproduced all six frozen offers and
showed that four ended with two K assets and inherited future best-of-week kicker
option value. DST multi-ownership was not invalidated; K multi-ownership crossed
the commissioned K-channel policy boundary.

The authorized structural correction is deliberately fail-closed:

- after legal mixed-package drop/fill normalization, reject any user or partner
  final state with more than one K;
- preserve league-legal multi-DST states and all existing DST machinery;
- do not invent a two-kicker valuation or acquisition strategy;
- leave screening non-authoritative and unchanged;
- leave player-only trade authority, manager behavior, IR Gate B5, and B2b
  boundaries unchanged;
- use no observed outcome to tune v0.X.

Source preflight v1 failed only on CRLF-warning path parsing; v2 reached 26 targeted
passes and failed only because a new regression omitted a test-only `Path` import.
Corrected v3 passed targeted pytest, full pytest, compileall, strict memory health,
and `git diff --check` against remote `75e0806e50d4b7d4fbc873a870db3281c80b45ad`.

The exact two-path source/test candidate is now **LOCAL-APPLIED / VALIDATED** in
the control root. Publication and runtime commissioning remain pending.

## Verified State

- Runtime baseline: `v0.36-repack1`, internal `VERSION = 0.36` - **COMMISSIONED**.
- Gate A fail-closed weekly control plane - **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B1 specialist current-WAIVER coverage - **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2a current IR/open-slot representation - **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2b absence horizon - **DEFERRED / FAIL-CLOSED**; corrected claim-local
  freshness retains zero qualifying claims and no future capacity credit.
- Gate B3 bounded player-only 1x1/1x2/2x1/2x2 search -
  **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B5 IR move-plus-add adapter - **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- October 3 fresh snapshot `2026-10-03T07:07:57.420185+00:00` and prospective
  capture `2026-10-03T07:07:58.070713+00:00` - **VALID / PRESERVED**.
- October 3 weekly receipt - **OPERATIONAL HEALTH PASS / 9 OF 9 COVERAGE /
  COMPLETE / ACTION_REQUIRED**; only `trade_specialist_inclusive` produced action.
- Frozen specialist frontier - six offers reproduced exactly with decomposition
  identity PASS; five were specialist-dominated.
- Policy-boundary audit - all six offers ended with multi-specialist ownership;
  four ended with two K and three with multiple DST.
- General K `CARRY2` - **DISABLED / DIRECT BEHAVIOR CONFIRMED**.
- Structural classification - post-trade multi-K fixed-ownership option value is
  outside the commissioned K-channel contract; multi-DST ownership is not
  invalidated by this evidence.
- Current specialist trade action frontier - **NOT EXECUTABLE / CORRECTION
  REQUIRED**. No trade should be sent from the October 3 six-offer frontier.
- Production authorization for the narrow multi-K structural correction -
  **GRANTED**.
- Multi-K source preflight v1 - **FAILED / NON-MUTATING / CRLF WARNING PARSER**.
- Multi-K source preflight v2 - **FAILED / NON-MUTATING / 26 PASSED + 1
  TEST-HARNESS NAMEERROR**.
- Multi-K source preflight v3 - **PASS / NON-MUTATING** with exact two-path
  candidate, targeted/full pytest, compileall, strict memory health, and
  `git diff --check`.
- Exact multi-K source/test candidate - **LOCAL-APPLIED / VALIDATED** in the
  control root; source publication and runtime commissioning pending.
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

Stage and publish the exact validated two-path specialist-trade multi-K source
correction together with this durable-memory checkpoint, then commission the
published `src/specialist_trade.py` into `v0.36-repack1`.

After runtime commissioning, create a **new decision-time Week 4 snapshot/capture**
and rerun the complete weekly receipt matrix. Do not authorize a specialist trade
from the October 3 six-offer frontier; it was generated under the now-classified
multi-K valuation defect. The October 3 snapshot/capture remain immutable
prospective evidence of the pre-correction state.

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
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
