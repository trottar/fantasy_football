# Current Project State

---
state_updated: 2026-10-24
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: week7_mc_guard_owned_player_and_bye_source_correction_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Build the standalone weekly decision operator in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: verified source/lock authority, protected six-provider refresh, irreversible prospective capture, nine-channel MC, current ESPN reconciliation and whole-roster legal-action certification. The operator should minimize manual intervention. Preserve commissioned `v0.36-repack1` and the `P ⊕ D ⊕ K` stochastic model. No automatic ESPN transactions; user approval is required for every transaction.

## Current Work Item

**Narrow source-only operational safety defect:** the existing `tools/operations/guarded_weekly_cycle.py` player lock guard uses `side == 'US'` for the `league_player_predictions` block, which stores `side='LEAGUE'` and authoritative `fantasy_team_id`. On the Saturday Week 7 prospective capture it checked only two specialists, not 14 owned QB/RB/WR/TE players, and returned a false `PASS`. The owner mapping must use `fantasy_team_id`; missing owned kickoffs may be excluded only for independently corroborated official byes. Do not change the frozen prediction or football physics. The v1 installer failed on a legacy compact fixture missing `week` (1 failed, 55 passed); the v2 installer passed all 57 targeted tests but rolled back after strict memory health rejected a merged `CURRENT.md` heading. v3 preserves production capture-week enforcement, restores both canonical headings and checks the generated memory contract before writing. Candidate and exact evidence: `architecture/WEEK7_SATURDAY_MC_GUARD_OWNERSHIP_BYE_FIX.md`.

## Verified State

- **Commissioned baseline:** `v0.36-repack1`, internal `VERSION=0.36`; native physics unchanged. Remote published operator source checkpoint `ab3db6b46c285d737210b31c41af87da08ef7715` (2026-10-24), exact tree `16c0764b7fd8b583d6fbd90340ef2226d6adcd98`; 956 isolated tests passed. The published native sync adapter does not itself authorize an operation.
- **Thursday Week 7 epoch remains immutable:** snapshot SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`, capture `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`, MC receipt `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`. Do not rerun or backfill.
- **Saturday Week 7 protected prospective epoch:** user-authorized real six-provider sync completed once, 27s measured and independently verified; new immutable snapshot `f7ba8ac8ba8511a9f26dc8e579a36ecc3a227a6850be0df64aaeade62ec759e7` at `2026-10-24T15:44:13.846276+00:00`, private measured receipt `c82fd36a26a5d1abf34afec45f996e9c00e68cb02d4c14dca1da7fbca3672316`. Protected immutable prospective capture `a1ba36bd6b2008a2ea432c116aed1b8f56d0b356d381de8fde927ddafd41424a` at approximately `2026-10-24T15:51:38Z`, with 174 league player predictions and 63 specialist predictions. No Saturday MC has been started or authorized, no ESPN transactions made.
- **Direct read-only diagnosis:** owned player records 14, all `side='LEAGUE'`, zero recognized by guard; owned specialists two, both recognized. One owned player lacks a kickoff but is corroborated as a legitimate 2026 Week 7 bye by official published calendar, configured league bye and immutable nflverse schedule. Owned non-bye unknown kickoff records: zero. The false-positive guard returned `PASS` with only two recognized owned records. No MC launch markers matched.
- **Independent health blocker:** fresh commissioned identity and strict memory-health receipts required by existing MC launcher were missing in local diagnostic (`FRESH_COMMISSIONED_IDENTITY.JSON_EVIDENCE_REQUIRED`). Do not fabricate, infer, or bypass them. Exact waiver/trade cutoffs, effective times, current ESPN action legality and M2 complete-roster certification remain unverified.

## Calendar / Evidence Gates

The Saturday capture is scientifically immutable and must never be recreated or backdated. M1a's current new-MC gate expires two hours after capture, about **2026-10-24 17:51:38 UTC (13:51:38 EDT)**; a source fix or later receipt cannot extend this window. If the gate closes before an independently authorized and fully validated MC launch, preserve the capture for later closure and defer this MC epoch. Fresh known individual locks and the conservative 80-minute MC/verification/approval/safety budget are still needed before launch.

## Scientific / Architectural Boundaries

Preserve `P ⊕ D ⊕ K`: player, defense and kicker valuations remain separate, with only complete-roster utility coupling. No empirical tuning of a-priori `v0.X`, changes to native football physics, backdating prospective evidence, or retrospective MC authorization. Manager response remains separate from intrinsic football utility.

## Exact Next Action

Guardedly apply the source-only ownership/independently verified-bye correction to the *control-root* MC guard plus focused regressions and this durable memory update. Run targeted tests, compileall and strict memory health; then isolated staging with the schema-2 manifest, full QA and separate guarded publication. **Do not run MC, six-provider sync, capture, ESPN writes, Git stage, commit or push as part of the local apply.** No live MC launch is authorized by this patch. Separately establish genuine fresh commissioning and memory-health evidence; inspect current time and capture freshness before any future MC launch. Once gates pass, obtain separate operator approval and use the restart-safe no-repeat controller. Resume M1b cutoff source work/M2 complete-roster certification after the protected operation is closed or deferred.

## Relevant References

- `architecture/WEEK7_SATURDAY_MC_GUARD_OWNERSHIP_BYE_FIX.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`; `architecture/WEEKLY_OPERATOR_M1B_NATIVE_SYNC_ADAPTER.md`; `architecture/WEEKLY_OPERATOR_M1B_REFRESH_DURATION_RECEIPT.md`; `architecture/WEEKLY_OPERATOR_M1B_PRE_REFRESH_LIVE_OWNER_LOCK.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `patches/PATCH_PROTOCOL.md`; `USER.md`; `roadmap/SEASON_2026.md`; `../../tools/operations/guarded_weekly_cycle.py`; `../../tools/operations/weekly_operator_controller.py`; `../../tools/operations/weekly_operator_calendar_evidence.py`; `../../tests/test_guarded_weekly_cycle.py`
