# Current Project State

---
state_updated: 2026-10-25
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_b2b4a_ordered_joint_structural_source_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the standalone weekly decision operator specified by `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: source-bound calendar/deadline/refresh/capture; guarded nine-channel MC; live ESPN drift reconciliation; complete-roster legal transaction certification; and one usable approval-ready report. Preserve the commissioned `v0.36-repack1` stochastic football baseline, `P ⊕ D ⊕ K` and causal MC/Data boundaries. No automatic ESPN writes or outcome-informed v0.X tuning.

## Current Work Item

**Week 8 M2 / B2b4a:** frozen ordered joint-trade state and released-asset field-exposure audit, **not** joint MC or live action certification. Published B1/B2a/B2b1/B2b2/B2b3 already expose frozen provenance-bound trade/drop/frontier, separate user/partner paired response, an unweighted future-fill lattice and per-offer conditional fill MC. B2b3 published at `d1720be7a394204dba0be84ef233766c67501236` with 983 full isolated tests and tree `6362e290d5b56142acba568afcfd308f8108ed29`; no runtime commissioning. B2b4a selects exactly two native offers and exact user-drop variants, evaluates both orders through the **same evolving copied league state**, enumerates bounded conditional future free-agent outcomes, tracks all released assets and checks frozen static roster constraints at each step. Direct owner/lock/fill conflicts block; success is only conditional. Shared future fills are not treated as independent. No football model change, probability fit, ESPN provider request or trade execution. Canonical record: `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4A.md`.

## Verified State

- **Commissioned baseline:** `fantasy_season_v0_36_repack1`, `VERSION=0.36`; player, DST, kicker and manager-behavior kernels unchanged. GitHub `trottar/fantasy_football` is historical/durable source, not proof the installed runtime is synced. Control-root local source is authoritative between checkpoints.
- **Week 7 source safety correction:** ownership/independent-bye guarded MC fix passed 973 full isolated tests, committed and remotely verified at `6596f30c538304201f88a6cff2384684a58cb1c5`. The source-only fix did not change commissioned physics.
- **Saturday October 24 Week 7 prospective operation:** frozen six-provider snapshot SHA256 `f7ba8ac8ba8511a9f26dc8e579a36ecc3a227a6850be0df64aaeade62ec759e7`, prospective capture SHA256 `a1ba36bd6b2008a2ea432c116aed1b8f56d0b356d381de8fde927ddafd41424a`, successful protected nine-channel MC receipt SHA256 `5a2fe4a85a6db4cba0408d3e27c15082c260cea6621f319ae05af43dc02f5705`. Four changed owned records, two changed market records, partner drift and uncertain transaction history on subsequent ESPN GET; `CAPTURE_REQUIRED_OWNED_DRIFT` barred current action certification. Week 7 user operations closed, evidence retained for future closure; never repeat/backfill.
- **M1/M2 frontier:** M1a restart-safe phase controller, M1b source/lock/cutoff/sync evidence components, M2 Slice A/B1/B2a/B2b1/B2b2/B2b3 source-published; B2b3 remains opt-in non-commissioned. Full one-command operator and its exact ESPN transaction cutoffs/action-screen proof, end-to-end correlated manager/market acquisition, joint portfolio predictive field response, injury downside and temporal legality remain unresolved. M3 read-only scheduled operation not commissioned.
- **Closure:** Week 5 selected fantasy yield observed, but player/DST/K component truths and regret not fully closed; Week 7 closure after outcome finalization. B2b prospective multiweek absence horizon still deferred without claim-local qualifying evidence.

## Calendar / Evidence Gates

Week 7 prospective predictions/captures and receipts immutable. Do not relabel later observations as predictions or rerun completed Week 7 MC for drift. Week 8 protected prospective capture and any decision-time transaction cutoff outrank nonessential development. A Week 8 calibration review is an evidence gate, not an automatic retuning instruction. User approval mandatory for every ESPN transaction.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; within-manager paired common random numbers where valid. Football utility, opponent field response, acquisition/manager behavior and action legality are distinct layers. Native action screening is not execution authority. No assumed future FREEAGENT success, cross-manager joint sample equivalence, posterior tuning of v0.X using observed 2026 outcomes, or retrospective prospective capture.

## Exact Next Action

Guardedly **local apply only** the new B2b4a read-only structural diagnostic, synthetic regression tests, this `CURRENT.md` update and canonical B2b4a architecture record. Require exact source predecessor Git-blob identity, correct `--package-id` runner interface, absent new paths, source-scope allowlist, backups/rollback and generated-memory prevalidation. Run targeted B2b4a/B2b3/B2b2/B2b1/B2a/B1 regressions, compileall, strict memory health. Then use separate exact isolated staging/schema-2 manifest, full repository QA, and an independently authorized guarded publication/remote verification. The local apply performs **no** staging, commit, push, native MC, ESPN GET/POST, six-provider refresh, prospective capture or runtime change. After publishing, evaluate B2b4b source-bound joint complete-roster paired MC plus observed field-release effects, not naive addition of B2b3 per-offer returns. Keep correlated acquisition probabilities UNKNOWN without decision-time manager behavior evidence; after that finish M1/M2 end-to-end candidate/time/legal certification and one-command report.

## Relevant References

- `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4A.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B3.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B2.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B1.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `roadmap/SEASON_2026.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `../../tools/operations/action_joint_state_b2b4a.py`; `../../tools/operations/action_fill_predictive_b2b3.py`; `../../tools/operations/action_portfolio_b2b2.py`; `../../tests/test_action_joint_state_b2b4a.py`
