# Current Project State

---
state_updated: 2026-10-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: weekly_operator_m1b_independent_deadline_authority_source_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the standalone weekly decision operator specified in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: source-independent pre-lock authority; protected six-provider refresh; irreversible prospective capture; nine-channel predictive MC; current ESPN reconciliation; complete legal action/portfolio certification; and eventually read-only scheduled rechecks. The operator, not ChatGPT, owns routine decision triage. The user explicitly approves ESPN transactions. Maintain commissioned `fantasy_season_v0_36_repack1` and physics `P ⊕ D ⊕ K` unchanged.

## Current Work Item

**M1b next narrow source-only candidate:** pure read-only
`tools/operations/weekly_operator_deadline_authority.py` and targeted synthetic
tests plus `architecture/WEEKLY_OPERATOR_M1B_DEADLINE_AUTHORITY.md`. Separate
independently corroborated live game locks from per-candidate ESPN waiver/trade
submission deadlines and measured refresh-plus-buffer planning lead. No inference
of claim cutoffs from processing schedules, no ESPN calls, sync/capture/MC,
runtime modification or transaction authority. The previous three M1b slices
remain published and unchanged.

## Verified State

- **Commissioned:** unchanged `v0.36-repack1`, internal `VERSION=0.36`, P/D/K intact. Week 7 Thursday Oct 22 immutable six-provider snapshot SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`, prospective capture SHA-256 `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`, native nine-channel MC receipt SHA-256 `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`. Never repeat or backfill this MC/capture.
- **M1a:** remote verified `09f63740413564fa0a569a8c5921167de8a7e897`, live tested status/review. MC receipt reused without rerun; `SCOPED_REVIEW_REQUIRED` on conditional Lamar Jackson start versus current Jacoby Brissett starter, market/partner drift blocking trade and acquisition actions, DST/K/IR scoped HOLD, action authority NONE. Sunday Oct 25 15:30 UTC QB recheck is not scheduled automatically.
- **M1b first frozen-source lock preflight:** remote verified `ce00430bc0f78461c23531419b7cdb7c152411a5`, 805 isolated tests; live Week 7: 16 owned, 15 known kickoffs, one unverified configured bye, 16,040-second-old snapshot => correctly `BLOCKED_STALE_SNAPSHOT`.
- **M1b independent public calendar:** checkpoint `week8_m1b_independent_public_calendar_20261022_v3` remote verified `0964d0a4fd4b252ef83a958d10381375119866e5`, parent `ce00430bc0f78461c23531419b7cdb7c152411a5`, tree `e0d3362a64c5a17db4413a7fe1dab1a898b6174e`, five changed paths, 203-entry memory manifest, full isolated pytest **820 passed**, compileall/strict memory/index validation. Private live read-only calendar accepted with public scoreboard SHA-256 `51727124e6a895f39779b02af91d8f4dc6e72d032f87cf8f61f96a1c09348d7c`: 14 games, 4 byes, 15 owned kicks, 1 owned bye, frozen age 22,930 seconds => `CORROBORATED_CALENDAR_STALE_FROZEN_ROSTER`. No live owner freshness or refresh authority.
- **M1b third live owner/lock diagnostic:** remote verified checkpoint
  `0d0b59b290df97bbdf1416564c2cb84373befc8e`, tree
  `04e65c9be00f581fe04faec0787dae9bac011502`, five changed paths,
  204-entry memory manifest, 833 full isolated pytest passes. Private live Week 7
  read-only acceptance: 16/16 owned assets, zero added/removed, four materially
  changed, 14 future unlocked, one elapsed, one verified bye, zero unknown;
  `READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED`, action/refresh/capture
  authority `NONE`. The Oct 23 v3 mSettings field-shape probe confirmed
  `acquisitionType`, `waiverProcessHour`, six string-valued processing days,
  `deadlineDate` and roster lock-policy field types; exact individual waiver
  cutoff, trade effective timestamp and refresh duration margin remain unproven.
  The new source-only evaluator is a candidate, not locally applied or published.
- **Action certification diagnostics:** A/B1/B2a/B2b1/B2b2 remote verified through `b45ba6abea843bed95ea1fabacc323bdb7b96399`. These are not end-to-end certified ESPN actions. Complete M1b six-provider orchestration, M2 legal/portfolio certification and M3 scheduling remain unimplemented.

## Calendar / Evidence Gates

**Absolute priority:** Saturday October 24 Week 7 six-provider refresh, immutable capture and full nine-channel MC, followed by decision-time live ESPN legality/approval checks. Independently establish *each affected still-future action lock* and the conservative 80-minute MC/validation/approval/safety lead plus refresh margin before initiating costly work. Thursday Week 7 NE–CHI kickoff `2026-10-23T00:15:00Z` is an earlier boundary and must not be retrospectively treated as prospective. An expired/unknown kickoff blocks that affected action. Never backfill prospective predictions, run new MC on a stale unlaunched capture, execute ESPN writes without user approval, or treat read-only calendar checks as transaction authority. Private raw ESPN/credentials remain local.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; paired complete-roster response with common random numbers; acquisition/manager behavior separate from intrinsic utility; `MC -> Data -> closure -> diagnosis -> evidence-supported v1.X calibration`. No 2026-observation tuning of a-priori v0.X. Distinguish control-root apply, isolated staging, committed, pushed/remote-verified, and commissioned states. No direct GitHub connector writes.

## Exact Next Action

Deliver, guardedly local-apply and targeted-test the pure M1b independent
transaction cutoff/refresh-lead classifier and source evidence record; then
validate the exact isolated Git staging/index and schema-2 memory manifest,
run full isolated pytest/compileall, publish separately with exact guards,
and verify remote read-only. Next add a source-bound live evidence owner that
proves actual cutoff/refresh receipt provenance before integrating the native
refresh/capture phases and finite restart-safe MC. The Oct 23 v3 probe has
closed the initial settings field-shape question; do not loop through more
field-name probes absent new evidence. Maintain causal capture windows and
protected operations independently of this development task. No read-only
planning classifier may authorize a transaction or automatic MC.

## Relevant References

- `architecture/WEEKLY_OPERATOR_M1B_DEADLINE_AUTHORITY.md`; `architecture/WEEKLY_OPERATOR_M1B_PRE_REFRESH_LIVE_OWNER_LOCK.md`; `architecture/WEEKLY_OPERATOR_M1B_INDEPENDENT_CALENDAR.md`; `architecture/WEEKLY_OPERATOR_M1B_FIRST_LOCK_PREFLIGHT.md`; `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`
- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/weekly_operator_live_lock_evidence.py`; `../../tools/operations/weekly_operator_calendar_evidence.py`; `../../tools/operations/weekly_operator_lock_preflight.py`; `../../tools/operations/weekly_operator_controller.py`
