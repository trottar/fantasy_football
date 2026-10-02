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

**WEEKLY DECISION GATE B2 — REDESIGN CURRENT IR MOVE-PLUS-ADD VALUE ADAPTER.**

Explicit production authorization was granted on 2026-10-02. Three subsequent
source-preflight packages failed before any source/runtime modification:

- v1: disposable-clone Windows read-only cleanup failure;
- v2: candidate reached full pytest with 576 passed / 1 failed; the single failure
  was the pre-existing Gate B4 weekly-contract literal after the candidate
  intentionally advanced the contract;
- v3: deterministic packaging defect routed a test-file transform through the
  weekly-source transform list and failed before code validation.

The v1-v3 candidate line is superseded. Source audit after v3 found two production
design defects that require redesign rather than another harness-only rerun:

1. player acquisition lock filtering must use the commissioned decision-time
   kickoff-aware lock boundary, not only `lineup_locked`;
2. an IR-opened active slot must not silently omit a league-legal specialist branch
   such as an additional kicker merely because the general two-kicker `CARRY2`
   policy is disabled.

The repair must target the proven single current B2a IR-opened slot and fail closed
on broader unsupported capacity states rather than claiming coverage.

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
- Source/runtime/staging/commit/push after all three failures — **UNCHANGED /
  NOT PERFORMED**.
- Active structural blocker remains `CURRENT_IR_MOVE_PLUS_ADD_VALUE_ADAPTER_GAP`.
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

Redesign one narrow source preflight for the current single B2a
`IR_MOVE_PLUS_ADD` state from exact source.

The redesigned candidate must:

1. consume only the proven one-slot B2a transition and fail closed on broader
   unsupported current-capacity states;
2. use the commissioned kickoff-aware decision-time lock boundary for acquisition
   candidates;
3. preserve FREEAGENT-versus-WAIVER uncertainty and manager/football separation;
4. preserve `P ⊕ D ⊕ K` and compose only at the complete-roster boundary;
5. cover every league-legal player/DST/K acquisition branch made relevant by the
   opened slot, or explicitly remain `INCOMPLETE_COVERAGE` for any unsupported
   branch;
6. give zero future IR-capacity credit while B2b remains deferred;
7. keep the mature player add/drop authority and commissioned specialist policy
   unchanged unless exact source evidence proves a minimal shared primitive must
   be extended;
8. key deterministic transforms by target file path and execute the exact
   transform-routing logic in package QA before operator delivery;
9. rerun targeted tests, full `pytest`, `compileall`, strict memory health, and
   `git diff --check` because the production design changes from the v2 candidate.

Do not rerun the full Week 4 roster-wide cycle until the corrected structural
coverage is source-published and runtime-commissioned, or fresh material
decision-time information independently requires a new capture.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `MAINTENANCE.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `evidence/WEEK4_IR_COMPLETION_FRONTIER_AND_B2B_CORRECTION_2026-10-02.md`
- `evidence/WEEK4_IR_ADAPTER_PREFLIGHT_REALIGNMENT_2026-10-02.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
