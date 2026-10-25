# Current Project State

---
state_updated: 2026-10-25
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_b2b4b_conditional_joint_predictive_source_candidate
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the source-bound standalone weekly decision operator in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: calendar/deadline/refresh/capture, guarded nine-channel MC, ESPN drift reconciliation, complete-roster legal action certification and one approval-ready report. The operator owns routine triage. Preserve commissioned `v0.36-repack1` physics and `P ⊕ D ⊕ K`; no automatic ESPN writes or v0.X tuning using observed 2026 results.

## Current Work Item

**Week 8 M2 / B2b4b source-only candidate:** `tools/operations/action_joint_predictive_b2b4b.py`, tests, and `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4B.md`. The predecessor B2b4a ordered two-offer structural state and released-player ledger was source-published/remote-verified at `e79735927552c4d889bdd5e37961a68ccb34a3c4` (tree `a0c445da6d25b016c4f2b3a6037704ceefd21504`); runtime remains unchanged. B2b4b consumes complete B2b4a ordered conditional cases without thinning, simulates each passing complete-league final roster through unchanged P/D/K composition, reports within-manager paired complete-roster utility and native opponent-reference shift; BLOCKED branches are not simulated. Frozen original FREEAGENT success is hypothetical; released assets remain market-status-unknown and are never silently available. Trade order processing, downstream released-player reacquisition, correlated manager/acquisition behavior and ESPN action legality remain unmodeled.

## Verified State

- **Commissioned baseline:** `fantasy_season_v0_36_repack1`, internal VERSION `0.36`, P/D/K and behavior unchanged. GitHub is durable source, not proof of runtime synchronization.
- **Week 8 predecessor:** B2b4a published with five-path exact stage/tree `a0c445da6d25b016c4f2b3a6037704ceefd21504`; parent `d1720be7a394204dba0be84ef233766c67501236`; remote commit `e79735927552c4d889bdd5e37961a68ccb34a3c4`; schema-2 manifest 211 entries; no runtime update/ESPN writes.
- **Week 7 safeguarded MC:** source repair at `6596f30c538304201f88a6cff2384684a58cb1c5` passed 973 full isolated tests. Saturday Oct 24 frozen six-provider SHA256 `f7ba8ac8ba8511a9f26dc8e579a36ecc3a227a6850be0df64aaeade62ec759e7`, capture SHA256 `a1ba36bd6b2008a2ea432c116aed1b8f56d0b356d381de8fde927ddafd41424a`, native MC receipt SHA256 `5a2fe4a85a6db4cba0408d3e27c15082c260cea6621f319ae05af43dc02f5705`; subsequent owned/market/partner drift blocked current action authority. Week 7 closed; do not repeat or backfill.
- **Source frontier:** M1a/M1b protected operation/deadline tools and M2 A/B1/B2a/B2b1/B2b2/B2b3/B2b4a are source-published; B2b3/B2b4a not runtime-commissioned. Source-bound correlated behavior, exact ESPN processing/action screens, injury downside, complete legal portfolios, M3 scheduler and full operator remain unfinished.
- **Evidence closure:** Week 5 selected yield exists but full P/D/K and regret closure incomplete; Week 7 closure only after actual outcomes. B2b multiweek absence horizon deferred without qualifying claim-local evidence.

## Calendar / Evidence Gates

Week 7 prospective evidence immutable. On Sunday October 25 Week 8 prospective deadlines and captures outrank source engineering; no backfilling after outcomes and no automatic ESPN action. Confirm any future decision-time freeze is causally prior to relevant outcomes and is independently current. An evidence review never authorizes empirical v0.X retuning.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. Independent manager scenario indices are **not** a correlated distribution. Paired CRN apply within supported manager states. Intrinsic football response, opponent/field response, manager acquisition behavior, and ESPN execution legality are distinct. `screen != authority`. Future released assets are not guaranteed FREEAGENTs.

## Exact Next Action

Guardedly **local apply only** B2b4b's new diagnostic/test/architecture and coherent `CURRENT.md`. Check B2b4a and CURRENT exact predecessor Git-blob identities, new-path absence and runner `--package-id`, validate rendered memory, back up CURRENT, rollback on failure, run targeted B2b4b/B2b4a/B2b3/B2b2/B2b1/B2a/B1 regressions, compileall and strict memory health. Package leaves manifest/Git/index/remote, native MC, six-provider sync, snapshot/capture, runtime and ESPN GET/POST untouched. Then separate declarative isolated staging with schema-2 manifest and full repository pytest, then separately authorized publication/remote verification. After publishing evaluate acquisition event-time and released-asset downstream field response using real decision-time manager/market evidence (no invented probabilities), complete M1/M2 legal screen and one-command report, then M3 scheduler. No prospective backfill or 2026-result tuning of v0.X.

## Relevant References

- `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4B.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4A.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B3.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/action_joint_predictive_b2b4b.py`; `../../tools/operations/action_joint_state_b2b4a.py`; `../../tools/operations/action_fill_predictive_b2b3.py`; `../../tests/test_action_joint_predictive_b2b4b.py`
