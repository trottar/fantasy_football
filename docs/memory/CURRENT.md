# Current Project State

---
state_updated: 2026-10-02
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_gate_b_capability_closure
active_workstream: gate_b2_ir_move_plus_add_completion
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Recover a causally valid Week 4 roster-wide decision state through the commissioned
Gate A/B control plane without backfilling missed prospective searches or weakening
channel, health, or decision-time information boundaries.

The fresh post-specialist-commissioning cycle is preserved and operationally
healthy. Eight of nine required channels produced valid receipts. The sole
remaining production blocker is the current IR move-plus-add value/capacity
adapter. B2b remains deferred/fail-closed after corrected claim-local freshness
auditing retained zero qualifying horizon claims.

## Current Work Item

**WEEKLY DECISION GATE B2 — IR MOVE-PLUS-ADD SOURCE-PUBLISHED / RUNTIME-COMMISSIONED.**

The redesigned v4 source preflight passed against repository checkpoint
`1c61e1b3574f6797be518061c03a2b4e66d1c373`, and the exact five-path candidate is
now local-applied/validated in the control root.

The candidate:

- targets only the proven single B2a `IR_MOVE_PLUS_ADD` transition and fails
  closed on direct/multiple unsupported open-slot states;
- reuses the commissioned kickoff/snapshot-aware lock boundary;
- preserves FREEAGENT versus WAIVER uncertainty;
- covers league-legal player, DST, and K acquisition branches made relevant by
  the opened slot;
- adds one specialist primitive,
  `OPEN_SLOT_PLUS_ONE_CURRENT_ONLY`, without enabling the general two-kicker
  `CARRY2` policy;
- gives zero future IR-capacity credit while B2b remains deferred;
- leaves `transaction_manager.py` and `ir_roster_state.py` unchanged;
- advances the weekly completion contract to
  `WEEKLY_DECISION_COMPLETION_GATE_B5_IR_MOVE_PLUS_ADD_V001`.

The exact source is now **PUSHED / REMOTE VERIFIED** at `d254e569f7c4dc5a3e27f85f6ba1386e4a6c98eb`, and the three production runtime files are **COMMISSIONED / VALIDATED** in `v0.36-repack1`.

## Verified State

- Runtime baseline: `v0.36-repack1`, internal `VERSION = 0.36` — **COMMISSIONED**.
- Remote/source checkpoint before the redesigned patch:
  `24e09e586d113d10e8884f1fb4173a58b3fd1297`.
- Gate A fail-closed weekly control plane — **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B1 specialist current-WAIVER coverage — **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2a current IR/open-slot representation — **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Gate B2b absence horizon — **DEFERRED / FAIL-CLOSED** until fresh qualifying
  decision-time evidence exists.
- Gate B3 bounded player-only 1x1/1x2/2x1/2x2 search —
  **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Specialist-inclusive trade composition —
  **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Fresh Week 4 cycle at snapshot `2026-10-02T05:25:32.944434+00:00` —
  **OPERATIONAL HEALTH PASS / INCOMPLETE_COVERAGE**.
- Fresh prospective capture at `2026-10-02T05:25:33.654991+00:00` passed integrity
  and is a post-lock partial-week decision-time capture.
- Eight of nine weekly channels returned valid receipts; the sole unsupported
  channel remains `ir_reserve_open_slot_injury_replacement`.
- Current IR state: 16/16 active roster, 0/1 IR occupied, one unlocked `OUT` QB
  move candidate, `IR_MOVE_PLUS_ADD_CAPACITY=1`, no direct open active slot, and
  no IR blockers.
- Corrected claim-local B2b audit retained zero qualifying horizon claims —
  **B2B DEFERRED / FAIL-CLOSED**.
- Explicit production authorization for the IR adapter — **GRANTED**.
- Preflight v1 — **FAILED / NON-MUTATING / HARNESS CLEANUP**.
- Preflight v2 — **FAILED / NON-MUTATING / 576 PASSED + 1 STALE CONTRACT TEST**;
  its targeted Gate A/B regression set passed before the full-suite failure.
- Preflight v3 — **FAILED / NON-MUTATING / DETERMINISTIC TRANSFORM-ROUTING BUG**.
- Redesigned preflight v4 — **PASS / NON-MUTATING** with path-keyed transform
  self-test, targeted pytest, full pytest, compileall, strict memory health, and
  `git diff --check`.
- Exact v4 candidate — **LOCAL-APPLIED / VALIDATED** in the control root; five
  source/test paths only.
- Production source publication — **PUSHED / REMOTE VERIFIED** at
  `d254e569f7c4dc5a3e27f85f6ba1386e4a6c98eb`, tree
  `be0829c8539df8947d848acbef0070e739614437`.
- Runtime commissioning v1 — **FAILED / ROLLED BACK** because the sparse runtime
  lacked `tests/test_weekly_decision_gate_b2a_ir_roster_state.py`; this was a
  validation-harness inventory failure, not a production candidate defect.
- Runtime commissioning v2 — **COMMISSIONED / VALIDATED** in `v0.36-repack1`;
  three retained production paths, six published targeted regressions overlaid
  temporarily and restored/removed, targeted/full pytest PASS, compileall PASS,
  import smoke PASS, result identities PASS, residue NONE.
- `CURRENT_IR_MOVE_PLUS_ADD_VALUE_ADAPTER_GAP` — **RESOLVED / COMMISSIONED**.
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

Run a **fresh Week 4 decision-time snapshot/capture and roster-wide weekly cycle**
through the commissioned Gate B5 control plane.

Do not reuse the Oct. 2 05:25 UTC snapshot/capture for current action
authorization. The runtime was commissioned many hours later and material roster,
injury/practice, availability, market, waiver, or kickoff/lock state may have
changed. Preserve the morning capture as immutable prospective evidence; create a
new causally valid capture for the next decision.

Require the complete receipt matrix and current operational-health contract. If
fresh state changes the B2a IR transition, evaluate that observed state rather
than carrying forward the morning one-slot assumption. B2b remains
deferred/fail-closed and contributes no future IR-capacity credit.

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
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
