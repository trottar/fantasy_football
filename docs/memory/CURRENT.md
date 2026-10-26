# Current Project State

---
state_updated: 2026-10-26
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_native_health_checkpoint_contract_repair
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Deliver and commission the unattended weekly fantasy decision procedure for Week 8**, not more standalone source-shape probes. One locally installed, scheduled controller must execute deadline-aware six-provider sync, immutable prospective capture, independently guarded nine-channel native MC, live ESPN drift reconciliation, complete P/D/K-aware roster/transaction certification, and one decision/report queue. A human approves actual ESPN actions; ChatGPT is not a weekly workflow step. Preserve commissioned `v0.36-repack1` physics/manager separation and no automatic ESPN writes or 2026-outcome tuning of v0.X. Acceptance owner: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Week 8 live trial evidence: native receipt health join blocked.** The supervised-trial bridge is remote verified at `4295520b67c0d5cbd5c98c328575a969b3b02151` (tree `6c0b8260ca26c965fc00f296ced9392da0a22de8`; 1058 full tests; manifest 218). On Monday October 26, the user-run trial completed calendar, six-provider sync, and immutable capture, then returned `STAGE_EXCEPTION_Blocked` before a v2 MC completion. Two subsequent read-only diagnostic receipts verified the frozen snapshot/capture and one matching **native nine-channel receipt**, but native `review.discover` rejected the native receipt as `NATIVE_RECEIPT_HEALTH_OR_CHRONOLOGY_INVALID`. The exact published v2 receipt writer omits `source_checkpoint` from its strict-memory input, while native Gate A requires it equal the runtime-identity source checkpoint: a deterministic contract defect even with valid memory health. The native receipt's precise blocker set must still be treated as unverified until examined; the Monday native receipt is immutable and **must not be modified, reclassified as PASS, or followed by a duplicate MC**. Apply only a prospective source/test fix adding the independently derived checkpoint to future strict-memory input receipts. Evidence: `evidence/WEEK8_V2_NATIVE_HEALTH_CHECKPOINT_MISMATCH_2026-10-26.md`.

## Verified State

- **Source authority:** GitHub `main` `4295520b67c0d5cbd5c98c328575a969b3b02151`, parent `b43b98596c5d5da24464e444fe24e0abb5a2dbdf`, tree `6c0b8260ca26c965fc00f296ced9392da0a22de8`, 6 exact files and 218 manifest entries, 1058 isolated full tests; source published, v2 not commissioned.
- **Frozen Monday Week 8 evidence:** successful Week 8 calendar, sync, capture phases; create-only SYNC/CAPTURE completion bound, valid snapshot and prospective capture, canonical snapshot binding and pre-data firewall, one M1a/native MC launch marker and one matching native receipt. No v2 MC completion; the native health/chronology validator blocks. No second MC launch. The user's read-only diagnostics made zero ESPN requests or project writes.
- **Source defect identified:** fresh v2 `memory_health` evidence is missing `source_checkpoint` required by native Gate A, although its sibling commissioned-runtime identity carries the field. Earlier synthetic test asserted `strict` but not checkpoint parity. Fix only future input receipts, leaving previously frozen native outcomes and phase markers unchanged.
- **Commissioned baseline:** `fantasy_season_v0_36_repack1` / `VERSION=0.36` unchanged. No v2 full-chain commissioning or Windows scheduler. Comprehensive action certification, §5A fixtures, ranked report, bounded drift recovery and verified claim timing remain incomplete. ESPN auto-writes prohibited. No 2026 outcome tuning of v0.X.

## Calendar / Evidence Gates

Protect Week **8** genuinely prospective windows now: Monday October 26 week-open, Tuesday pre-waiver (exact league cutoff **unknown until observed**), Wednesday October 28 primary, Saturday October 31 secondary, and every actual player/claim lock. The first Week 8 NFL game is Thursday October 29. A future matching snapshot can be newly captured before relevant outcomes; it must never be backdated or treated as covering already-elapsed outcomes. Protect capture ahead of nonessential development. Do not invent ESPN cutoffs, assume a trade is executable, infer future free-agent fills, or run an MC without validated timing/lead. Scheduler must remain disabled until commissioning.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. Only prospective decision-time information. Players vs players, DST vs DST, K vs K; couple only complete-roster utility. Preserve paired CRN and manager behavior separate from intrinsic football response. `screen != authority`. A native `ACTIONABLE_OFFER` is never a certified ESPN submission. Unsupported required coverage means `INCOMPLETE_COVERAGE`; invalid health means `BLOCKED_HEALTH`, not HOLD.

## Exact Next Action

**Apply and validate the narrow native Gate A memory-checkpoint source contract fix** in `weekly_operator_v2.py` and tests. Confirm the published `4295520b` predecessor blobs, exact affected-file scope, rollback and code-owned structural regression; run targeted + full isolated QA, memory health, schema-2 manifest and separate guarded publication. Do not alter Monday runtime receipts, frozen capture, MC launch marker or report; do not relaunch Monday MC or call ESPN. Then protect the next real Week 8 decision-time prospective slot (Tuesday pre-waiver only if independently before the real cutoff; Wednesday and Saturday with proper future-game scope), with a **new independently verified** native health input and one guarded MC per new immutable capture, not a retrospective repair. Source publication is not commissioning. Following prospective evidence, complete material-drift recovery, full §5A/eight-scenario action certification, ranked approval report and scheduler acceptance. Never call INCOMPLETE_COVERAGE a HOLD or certify a rejected native receipt.

## Relevant References

- `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`; `evidence/WEEK8_V2_NATIVE_HEALTH_CHECKPOINT_MISMATCH_2026-10-26.md`; `evidence/WEEK8_V2_COMMISSIONING_TRIAL_SOURCE_2026-10-25.md`; `evidence/WEEK8_V2_PHASE_RECOVERY_SOURCE_2026-10-25.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `../../tools/operations/weekly_operator_v2.py`; `../../tools/operations/weekly_operator_controller.py`; `../../tools/operations/guarded_weekly_cycle.py`; `../../tests/test_weekly_operator_v2.py`
