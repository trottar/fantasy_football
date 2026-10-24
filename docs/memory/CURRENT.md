# Current Project State

---
state_updated: 2026-10-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: weekly_operator_m1b_measured_sync_duration_receipt_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the standalone weekly decision operator specified in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: source-independent pre-lock authority; protected six-provider refresh; irreversible prospective capture; nine-channel predictive MC; current ESPN reconciliation; complete legal action/portfolio certification; and eventually read-only scheduled rechecks. The operator, not ChatGPT, owns routine decision triage. The user explicitly approves ESPN transactions. Maintain commissioned `fantasy_season_v0_36_repack1` and physics `P ⊕ D ⊕ K` unchanged.

## Current Work Item

**M1b next narrow source-only candidate:** opt-in, in-process six-provider
refresh-duration observer and private receipt reader
(`tools/operations/weekly_operator_refresh_duration_receipt.py`), synthetic
regressions, and `architecture/WEEKLY_OPERATOR_M1B_REFRESH_DURATION_RECEIPT.md`.
It wraps **only an independently authorized existing sync callable**, measuring
UTC/monotonic elapsed time and binding a fully healthy six-provider snapshot.
No sync is initiated by package installation, and no previous runtime phase,
MC, capture, ESPN transaction or observed football result is changed.

## Verified State

- **Commissioned baseline:** `v0.36-repack1` (`VERSION=0.36`), physics `P ⊕ D ⊕ K` intact. Week 7 Thursday immutable snapshot SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`, prospective capture `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`, native nine-channel MC receipt `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`. Never backfill or rerun that epoch.
- **M1a:** read-only restart-safe controller remote verified at `09f63740413564fa0a569a8c5921167de8a7e897`; existing MC reused. Live lineup review was scoped, and market/partner drift blocked action approval. Action authority `NONE`.
- **M1b prior slices:** first lock preflight `ce00430bc0f78461c23531419b7cdb7c152411a5`; public calendar `0964d0a4fd4b252ef83a958d10381375119866e5`; private live owner/lock `0d0b59b290df97bbdf1416564c2cb84373befc8e`; deadline classifier `4d4808cdc14c79d56d9e55662204eb6838386e40`. The classifier checks source shapes and chronology only: it does not authenticate refresh-duration or cutoff receipt bytes.
- **Source-bound live evidence owner:** v3 checkpoint `98371db7a152d071a3f2ac831dd3d7b85bf26f26` remote verified, tree `653a3cdd92517f12f3540598c86ae8f5ad8a3c0d`, 206-entry manifest, 901 full isolated pytest passed. The preceding v2 staging/test fixture defect is resolved; source owner and commissioned runtime unchanged. No private live acceptance of this owner yet.
- **Missing evidence:** no source-bound measured six-provider refresh duration, independently verified per-candidate waiver/trade submission cutoff, or certified transaction effective time. ESPN `mSettings` field shapes alone never establish them. M1b native refresh/capture orchestration, M2 complete-roster/legal portfolio certification and M3 scheduling remain unimplemented.

## Calendar / Evidence Gates

Protected Week 7 capture/MC operations remain a separate calendar obligation; do not conflate this development slice with an operational trigger. For any consequential action, independently verify its individual lock, an 80-minute MC/approval budget **plus actual refresh margin**, fresh ESPN legality, and explicit user approval. Thursday October 22 prospective state remains immutable; elapsed/unknown locks block affected actions. No retrospective capture, stale MC authorization, automatic ESPN writes, or public sharing of private raw ESPN/credentials.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; paired complete-roster response with common random numbers; acquisition/manager behavior separate from intrinsic utility; `MC -> Data -> closure -> diagnosis -> evidence-supported v1.X calibration`. No 2026-observation tuning of a-priori v0.X. Distinguish control-root apply, isolated staging, committed, pushed/remote-verified, and commissioned states. No direct GitHub connector writes.

## Exact Next Action

Apply and targeted-test the source-only M1b six-provider duration observer and
private receipt verifier, then exact isolated staging/manifest and full QA;
separately authorize publication only after those gates pass and verify remote
read-only. Next integrate the observer into a **separately authorized** real
six-provider refresh path so actual elapsed time and source bytes can be
measured without replay/backfill. No measured receipt exists yet. Keep fresh
per-candidate ESPN cutoff verification, prospective capture gates and complete
M2 action certification independent. Automatic MC or ESPN writes remain forbidden.

## Relevant References

- `architecture/WEEKLY_OPERATOR_M1B_REFRESH_DURATION_RECEIPT.md`; `architecture/WEEKLY_OPERATOR_M1B_SOURCE_EVIDENCE_OWNER.md`; `architecture/WEEKLY_OPERATOR_M1B_DEADLINE_AUTHORITY.md`; `architecture/WEEKLY_OPERATOR_M1B_PRE_REFRESH_LIVE_OWNER_LOCK.md`; `architecture/WEEKLY_OPERATOR_M1B_INDEPENDENT_CALENDAR.md`; `architecture/WEEKLY_OPERATOR_M1B_FIRST_LOCK_PREFLIGHT.md`; `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`
- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/weekly_operator_refresh_duration_receipt.py`; `../../tools/operations/weekly_operator_source_evidence_owner.py`; `../../tools/operations/weekly_operator_deadline_authority.py`; `../../tools/operations/weekly_operator_live_lock_evidence.py`; `../../tools/operations/weekly_operator_calendar_evidence.py`; `../../tools/operations/weekly_operator_lock_preflight.py`; `../../tools/operations/weekly_operator_controller.py`
