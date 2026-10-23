# Current Project State

---
state_updated: 2026-10-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week7_protected_operations_and_week8_operator_implementation
active_workstream: weekly_operator_m1b_source_bound_live_evidence_owner_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the standalone weekly decision operator specified in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: source-independent pre-lock authority; protected six-provider refresh; irreversible prospective capture; nine-channel predictive MC; current ESPN reconciliation; complete legal action/portfolio certification; and eventually read-only scheduled rechecks. The operator, not ChatGPT, owns routine decision triage. The user explicitly approves ESPN transactions. Maintain commissioned `fantasy_season_v0_36_repack1` and physics `P ⊕ D ⊕ K` unchanged.

## Current Work Item

**M1b source-bound live evidence owner candidate:** new read-only
`tools/operations/weekly_operator_source_evidence_owner.py` and targeted
synthetic tests plus `architecture/WEEKLY_OPERATOR_M1B_SOURCE_EVIDENCE_OWNER.md`.
The candidate reuses one published live roster/calendar observation, verifies
exact published source blobs and local immutable snapshot bytes before and
after the read, and feeds the result to the published pure deadline classifier.
It must not synthesize a six-provider measured-refresh receipt or a per-candidate
ESPN transaction cutoff. It grants no sync/capture/MC or ESPN action authority.

## Verified State

- **Baseline:** commissioned `v0.36-repack1` / version `0.36`, physics `P ⊕ D ⊕ K` unchanged. Week 7 Thursday immutable snapshot SHA-256 `7c90ca5ff9ebf87ae1ae97dde20d98c0bdde0eeef1b79dd97c28783bacca21db`, prospective capture `a3afb25ff1d312ca3c47641475a750d94ad01db45a0f00aee58592ccc4c07b87`, nine-channel MC receipt `24ce0bab9c05e862e6d647493cc9abaf101b24cbba935b151b55ca5e2b6f1965`. Do not replay, overwrite, or backfill this epoch.
- **M1a:** restart-safe controller published (`09f63740413564fa0a569a8c5921167de8a7e897`) and live tested: existing native MC reused; scoped lineup review required, market/partner drift blocks actions. All ESPN action authority remains `NONE`.
- **M1b prior observations:** frozen-source preflight `ce00430bc0f78461c23531419b7cdb7c152411a5`; independent calendar `0964d0a4fd4b252ef83a958d10381375119866e5`; live owner/lock diagnostic `0d0b59b290df97bbdf1416564c2cb84373befc8e` (833 isolated pytest passed). Private Week 7 read: 16 owned; 14 unlocked future, one elapsed, one verified bye, zero unknown, four changed assets. New capture needed for changed state; no refresh or transaction authority.
- **M1b deadline classifier:** exact predecessor `4d4808cdc14c79d56d9e55662204eb6838386e40`, published/remote-verified; staged tree `5456c77c4c0845c568332b80e565d760e8c8ad76`; 205-entry manifest and 876 full isolated pytest passes. It structurally checks refresh, game-lock and candidate cutoff envelopes only: no source receipt authentication or execution authority. Private `mSettings` v3 proved rule field shapes, **not** exact claims/trade deadlines or measured refresh duration.
- **M1b owner checkpoint:** v2 guarded local apply and isolated staging passed (tree `3d54f2aba3cd8b71206a383e5a4573742deaa67b`, 206 memory entries); full isolated QA was **blocked**: 899 passed, one Windows BOM/CRLF fixture failed, no commit/push. This v3 source-only correction canonicalizes test inputs before constructing BOM+CRLF variants; source guard and commissioned runtime remain unchanged. The v2 staged tree is superseded.
- **Downstream:** M1b six-provider automatic orchestration, M2 transaction/portfolio certification, M3 scheduling remain unimplemented. Previous A/B1/B2a/B2b1/B2b2 diagnostics are not ESPN action certificates.

## Calendar / Evidence Gates

Protected Week 7 capture/MC operations remain a separate calendar obligation; do not conflate this development slice with an operational trigger. For any consequential action, independently verify its individual lock, an 80-minute MC/approval budget **plus actual refresh margin**, fresh ESPN legality, and explicit user approval. Thursday October 22 prospective state remains immutable; elapsed/unknown locks block affected actions. No retrospective capture, stale MC authorization, automatic ESPN writes, or public sharing of private raw ESPN/credentials.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; paired complete-roster response with common random numbers; acquisition/manager behavior separate from intrinsic utility; `MC -> Data -> closure -> diagnosis -> evidence-supported v1.X calibration`. No 2026-observation tuning of a-priori v0.X. Distinguish control-root apply, isolated staging, committed, pushed/remote-verified, and commissioned states. No direct GitHub connector writes.

## Exact Next Action

Promote this narrow v3 fixture correction only through guarded local apply,
new exact isolated staging, full tests, separate authorized publication, and
remote verification; the prior v2 staging tree cannot be published. Once those
gates pass, implement the next *source-bound measured six-provider sync-duration
receipt producer*. Cutoff timestamps remain blocked until a separate verified
per-candidate ESPN source proves their semantics. Do not infer refresh/transaction
authority from a shape, timing guess or synthetic proof. Preserve finite MC
recovery, frozen prospective captures, commissioned P/D/K physics and human
ESPN approval; protected operations are independent of this work item.

## Relevant References

- `architecture/WEEKLY_OPERATOR_M1B_SOURCE_EVIDENCE_OWNER.md`; `architecture/WEEKLY_OPERATOR_M1B_DEADLINE_AUTHORITY.md`; `architecture/WEEKLY_OPERATOR_M1B_PRE_REFRESH_LIVE_OWNER_LOCK.md`; `architecture/WEEKLY_OPERATOR_M1B_INDEPENDENT_CALENDAR.md`; `architecture/WEEKLY_OPERATOR_M1B_FIRST_LOCK_PREFLIGHT.md`; `architecture/WEEKLY_OPERATOR_M1A_RESTART_CONTROLLER.md`
- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/PROTECTED_WEEKLY_MC_OPERATIONS.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`
- `patches/PATCH_PROTOCOL.md`; `roadmap/SEASON_2026.md`; `USER.md`
- `../../tools/operations/weekly_operator_source_evidence_owner.py`; `../../tools/operations/weekly_operator_deadline_authority.py`; `../../tools/operations/weekly_operator_live_lock_evidence.py`; `../../tools/operations/weekly_operator_calendar_evidence.py`; `../../tools/operations/weekly_operator_lock_preflight.py`; `../../tools/operations/weekly_operator_controller.py`
