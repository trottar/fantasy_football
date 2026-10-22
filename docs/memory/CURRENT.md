# Current Project State

---
state_updated: 2026-10-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: weekly_operator_m1a_restart_safe_phase_controller
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Build the permanent, standalone weekly operating controller with a protected six-provider refresh, immutable prospective capture, complete nine-channel native MC, current ESPN reconciliation, exact action certification, and scheduled decision-time rechecks. Keep commissioned `fantasy_season_v0_36_repack1` (`VERSION=0.36`) and P/D/K intrinsic physics unchanged. The user approves executable transactions; the controller must not delegate ordinary decision triage to ChatGPT.

## Current Work Item

**M1a: guarded restart-safe phase-state controller source candidate** (`tools/operations/weekly_operator_controller.py`; canonical `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`). It joins frozen snapshot/capture/receipt identities, offers offline `status`, defaults to current read-only decision `review` for complete evidence, and can explicitly resume native MC **only** if the frozen capture is fresh, source-bound and no MC launch has previously occurred. Exclusive private launch evidence blocks double execution after crash/uncertainty. It does not create a six-provider refresh or prospective capture, modify physics, approve ESPN actions, or schedule checks. Full local-apply/staging/publication and live validation are still distinct, not implied by source construction.

## Verified State

- The native v0.36-repack1 runtime is commissioned and unchanged. Its nine-channel Week 7 MC ran on the Thursday October 22 six-provider snapshot `20261022T135837Z` (SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`), prospective capture `pregame_2026_w07_20261022T135909Z` (SHA-256 `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`), and nine-channel receipt `weekly_decision_receipt_20261022T144605Z.json` (SHA-256 `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`). `COMPLETE / ACTION_REQUIRED` at the frozen state was not executable ESPN action authority.
- The DST response reported HOLD and `NO_RESOLVED_EDGE`. The frozen lineup selected QUESTIONABLE Lamar Jackson over active Jacoby Brissett, requiring a conditional injury and exact-slot recheck. Four native trade candidate offers were unqualified due to post-trade drops/fills, partner acceptance, timing and app legality; market drift blocked market-dependent transactions. Week 7 working plan remains the current roster with the QB slot contingent on fresh current evidence. No ESPN writes occurred.
- Week 8 source-only diagnostic Slices A/B1/B2a/B2b1/B2b2 were all remote verified through B2b2 commit `b45ba6abea843bed95ea1fabacc323bdb7b96399`. They are **not** runtime commissioned action certification, probability models or approval authority.
- The permanent read-only weekly decision triage MVP was guarded locally applied, staged as exact five paths (including 200-entry schema-2 manifest), full isolated suite **773 passed**, compiled and memory verified, and live read-only operator accepted. It returned `SCOPED_REVIEW_REQUIRED` and isolated Lamar's conditional injury recheck, DST/K HOLD and RB/WR market-dependent blockers. Guarded publication was independently remote verified as commit `42470bf0bf0d060d3d842b52db8dac4cdfc144b5`, parent `b45ba6abea843bed95ea1fabacc323bdb7b96399`, tree `50f7e5c244e3266dc3c5ceca061447d06c66fd79`. This is control-root/source tooling, not commissioned automatic weekly orchestration.

## Calendar / Evidence Gates

**Absolute priority:** Saturday October 24 protected six-provider prospective Week 7 capture and full nine-channel MC before the independently verified earliest relevant actionable lock (initial budget MC 40 + validation 15 + approval/action 15 + safety 10 minutes, plus refresh margin). Thursday NE-at-CHI first kickoff at `2026-10-23T00:15:00Z` remains a relevant current-week boundary. If an individual capture deadline passes, preserve observations; never backfill prospective predictions. Unverified lock, waiver deadline, lineup slot, injury, partner action or transaction timing is BLOCKED, not HOLD. An MC or cheap screen does not authorize an ESPN POST. Secrets and authenticated raw snapshots stay local.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L × sigma × A × epsilon`, separate P/D/K channel comparisons, complete-roster paired response, common random numbers, distinct manager behavior/acquisition uncertainty, and `MC -> Data -> closure -> diagnosis -> evidence-supported v1.X calibration` only. No tuning v0.X against observed 2026 outcomes. No direct GitHub writes; package-based local apply, isolated stage, guarded publication and independent remote verification are separate boundaries.

## Exact Next Action

**Guardedly locally apply the small M1a read-only/source-control package**, validate exact installed tests and strict durable memory, run full isolated checkout `pytest`/`compileall`/manifest/index QA, then separately guarded-publish and read-only verify the remote. Exercise the new `--mode review` path locally against existing Thursday immutable evidence without launching new MC. Next **M1b** must add fresh six-provider sync/capture and a per-player first-lock deadline preflight, immutable phase receipts/restart, and finite state-drift recovery; do not let engineering preempt the Saturday protected capture. After M1, proceed to exact ESPN legality, B2b3 coupled complete-roster fill/portfolio MC, action certification and scheduled read-only operation.

## Relevant References

- `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`; `architecture/WEEKLY_OPERATOR_READONLY_TRIAGE_MVP.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B2.md`; `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/weekly_operator_controller.py`; `../../tools/operations/weekly_operator_review.py`; `../../tools/operations/guarded_weekly_cycle.py`; `../../tests/test_weekly_operator_controller.py`
