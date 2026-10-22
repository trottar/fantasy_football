# Current Project State

---
state_updated: 2026-10-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: weekly_operator_m1b_independent_calendar_source
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the standalone weekly decision operator specified in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: source-independent pre-lock authority; protected six-provider refresh; irreversible prospective capture; nine-channel predictive MC; current ESPN reconciliation; complete legal action/portfolio certification; and eventually read-only scheduled rechecks. The operator, not ChatGPT, owns routine decision triage. The user explicitly approves ESPN transactions. Maintain commissioned `fantasy_season_v0_36_repack1` and physics `P ⊕ D ⊕ K` unchanged.

## Current Work Item

**M1b second narrow source-only slice:** `tools/operations/weekly_operator_calendar_evidence.py` + tests + `architecture/WEEKLY_OPERATOR_M1B_INDEPENDENT_CALENDAR.md`. The tool obtains a single public, unauthenticated ESPN scoreboard for a specified week, cross-checks its complete 32-team game/bye partition against the NFL's independently published 2026 bye table, the configured league bye table, and exact frozen nflverse opponent/kickoff data for every owned P/D/K asset. It *never* treats a stale frozen roster as fresh or authorizes sync, capture, MC, an ESPN action, or a scheduler. The first preflight and M1a are already published. Source publication and live acceptance are separate receipt-backed gates; neither is established by documentation or source presence alone.

## Verified State

- **Commissioned runtime:** `v0.36-repack1` internal `VERSION=0.36`, unchanged. Week 7 October 22 native nine-channel MC was run on immutable six-provider snapshot `20261022T135837Z` (SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`), prospective `pregame_2026_w07_20261022T135909Z` capture (SHA-256 `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`) and complete MC receipt (SHA-256 `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`). Preserve these frozen identities and do not repeat the Thursday MC.
- **Operator M1a:** published and remote verified at `09f63740413564fa0a569a8c5921167de8a7e897` (tree `e3f0db0e0fd4f747a5063a114a3f47e4eb9126f6`). Live read-only `--mode status` returned `NATIVE_RECEIPT_READY` / `REUSE_VALIDATED_NATIVE_MC`. A later `--mode review --week 7` returned `SCOPED_REVIEW_REQUIRED`, with existing MC reused and `ACTION_AUTHORITY=NONE`. Lamar Jackson remained questionable and benched against currently active QB-slot starter Jacoby Brissett; conditional injury/slot recheck only. DST/K and IR reported native HOLD; player acquisitions and all four native trade candidates remain uncertified due to market/partner drift, exact legal fills/timing and acceptance uncertainty. The computed next cheap QB check was October 25, 2026 at 15:30 UTC; this is not an installed schedule.
- **Operator M1b first-lock preflight:** five-path checkpoint published and independently remote verified at `ce00430bc0f78461c23531419b7cdb7c152411a5`, parent `09f63740413564fa0a569a8c5921167de8a7e897`, tree `890835160a78c8b45290eb9e768cd035fcf12d41`. Isolated pytest 805 passed, compileall, strict memory and schema-2 manifest 202 entries reported PASS. Live read-only private Week 7 preflight saw 16 owned (15 known kickoff, one configured/unverified bye, zero unknown non-bye), a 16,040-second-old frozen snapshot, status `BLOCKED_STALE_SNAPSHOT`; this is expected evidence, not an MC defect.
- **Source-only action certification diagnostics:** A/B1/B2a/B2b1/B2b2 remote verified through `b45ba6abea843bed95ea1fabacc323bdb7b96399`; these do *not* constitute end-to-end certified ESPN trade/waiver approval or runtime commissioning. Full M1b six-provider orchestration, immutable phase receipt/recovery loop, complete M2 certification, and M3 scheduler are not yet implemented.

## Calendar / Evidence Gates

**Absolute priority:** Saturday October 24 Week 7 six-provider refresh, immutable capture and full nine-channel MC, followed by decision-time live ESPN legality/approval checks. Independently establish *each affected still-future action lock* and the conservative 80-minute MC/validation/approval/safety lead plus refresh margin before initiating costly work. Thursday Week 7 NE–CHI kickoff `2026-10-23T00:15:00Z` is an earlier boundary and must not be retrospectively treated as prospective. An expired/unknown kickoff blocks that affected action. Never backfill prospective predictions, run new MC on a stale unlaunched capture, execute ESPN writes without user approval, or treat read-only calendar checks as transaction authority. Private raw ESPN/credentials remain local.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; paired complete-roster response with common random numbers; acquisition/manager behavior separate from intrinsic utility; `MC -> Data -> closure -> diagnosis -> evidence-supported v1.X calibration`. No 2026-observation tuning of a-priori v0.X. Distinguish control-root apply, isolated staging, committed, pushed/remote-verified, and commissioned states. No direct GitHub connector writes.

## Exact Next Action

**Next substantive gate:** live read-only independent calendar acceptance after its guarded local-apply/staging/publication checkpoints, if not already completed. Examine actual public game coverage, published bye corroboration, exact frozen per-owned kickoff comparisons, and pre-refresh roster freshness without granting action authority. Then implement the *next narrow M1b integration*: freshly sourced **pre-refresh owned roster/lock authority** and explicit protected refresh gate, then native six-provider sync + immutable prospective capture with private phase receipts, followed by finite one-epoch material-drift recovery and existing native MC reuse. The Saturday October 24 prospective capture is the non-negotiable earlier calendar gate. M2 complete-roster legal action certification and optional M3 scheduling follow only after the M1b controller reaches the required acceptance gates.

## Relevant References

- `architecture/WEEKLY_OPERATOR_M1B_INDEPENDENT_CALENDAR.md`; `architecture/WEEKLY_OPERATOR_M1B_FIRST_LOCK_PREFLIGHT.md`; `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`
- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/weekly_operator_calendar_evidence.py`; `../../tools/operations/weekly_operator_lock_preflight.py`; `../../tools/operations/weekly_operator_controller.py`
