# Current Project State

---
state_updated: 2026-10-25
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_v2_integrated_operator_source_candidate
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Deliver and commission the unattended weekly fantasy decision procedure for Week 8**, not more standalone source-shape probes. One locally installed, scheduled controller must execute deadline-aware six-provider sync, immutable prospective capture, independently guarded nine-channel native MC, live ESPN drift reconciliation, complete P/D/K-aware roster/transaction certification, and one decision/report queue. A human approves actual ESPN actions; ChatGPT is not a weekly workflow step. Preserve commissioned `v0.36-repack1` physics/manager separation and no automatic ESPN writes or 2026-outcome tuning of v0.X. Acceptance owner: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Week 8 integrated v2 controller implementation, first source candidate.** Target `tools/operations/weekly_operator_v2.py`, synthetic integration tests, and `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`. The candidate joins correct NFL-week selection, fixed pregame calendar protection, commissioned native sync and capture CLI boundaries, immutable six-provider/snapshot and capture checks, the already-published M1a guarded MC/review, private restart markers, and a unified fail-closed private report. The new source is **not** the complete workflow: it requires an independently validated source-bound commissioning identity before any run and never certifies a transaction; current action certification, causal recovery, scheduler installation, and complete report/risk analysis are still gating work. Installation and tests do not perform ESPN GET/POST, refresh, capture, MC, or runtime/scheduler modification. No claims of operational readiness until live end-to-end commissioning.

## Verified State

- **Published baseline:** remote main `e714f22815375723fcda620f13b7c058c25bc16d`, parent `a1daf782bff2ee550dece1f1e3c52a3e4475f375`, tree `9e6046243632fe9b342e779d15d7f1d3bc62b583`, 3-file memory-only checkpoint, schema-2 manifest 215, 1030 full isolated tests. The commissioned runtime remains `fantasy_season_v0_36_repack1` / `VERSION=0.36`; source publication never equals runtime commissioning.
- **Week 8 calendar correction:** Sunday October 25 is the Week **7** game window (Oct 22-26); Week **8** games are October 29-November 2. The previous `CURRENT.md` pivot to Week 9 and interpretation of missing Week 8 archives as missed Week 8 prospective capture were incorrect. A Week 8 frozen archive should not be expected before the Week 8 capture. The October 25 evidence remains true as a bounded inventory (29 archives, 0 Week 8), but **does not mean Week 8 prospective opportunity was lost**. Canonical correction appended to `evidence/WEEK8_B2B4D_FROZEN_ARCHIVE_GATE_2026-10-25.md`.
- **Existing operational pieces:** `fantasy.py season-sync`, `closure-capture`, and `weekly-cycle` are installed native interfaces. `weekly_operator_controller.py` reuses native MC receipts/restarts; `weekly_operator_review.py` rechecks live ESPN and returns a scoped queue; `action_certification.py` is a fail-closed scaffold. None currently constitutes a commissioned end-to-end unattended workflow. Standalone B2b4a/b/c/d remain source diagnostics, not permission to submit transactions.
- **Uncertified:** automated evidence/MC phase recovery, mandatory legal drop/fill and roster-concentration counterfactuals, correlated manager acquisition/field response, full eight action-certification fixtures, one actionable portfolio report, independently corroborated actual ESPN claim/trade cutoffs, Task Scheduler activation, live source/runtime commissioning. `processDate` is not proven actual effect time. Week 5 component closure and B2b multiweek absence horizon remain separately deferred.

## Calendar / Evidence Gates

Protect Week **8** genuinely prospective windows now: Monday October 26 week-open, Tuesday pre-waiver (exact league cutoff **unknown until observed**), Wednesday October 28 primary, Saturday October 31 secondary, and every actual player/claim lock. The first Week 8 NFL game is Thursday October 29. A future matching snapshot can be newly captured before relevant outcomes; it must never be backdated or treated as covering already-elapsed outcomes. Protect capture ahead of nonessential development. Do not invent ESPN cutoffs, assume a trade is executable, infer future free-agent fills, or run an MC without validated timing/lead. Scheduler must remain disabled until commissioning.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. Only prospective decision-time information. Players vs players, DST vs DST, K vs K; couple only complete-roster utility. Preserve paired CRN and manager behavior separate from intrinsic football response. `screen != authority`. A native `ACTIONABLE_OFFER` is never a certified ESPN submission. Unsupported required coverage means `INCOMPLETE_COVERAGE`; invalid health means `BLOCKED_HEALTH`, not HOLD.

## Exact Next Action

**Implement the whole operator via the approved v2 spec, prioritizing missing integration over diagnostic expansion.** Guardedly local-apply this *source-only* integrated-controller candidate, 16 synthetic tests, corrective architecture and active/evidence memory. Require exact e714 published predecessor identity, absent new paths, byte/semantic preservation, rollback, compileall, strict memory health, and action/controller/source regressions. Then isolated full pytest, schema-2 Git-blob manifest and separate guarded publication; do not run installed `--mode run` or modify runtime/scheduler in that step. Immediately complete the nonoptional acceptance gates: source-bound native phase receipts with proven restart/one bounded drift epoch; full action certification and all eight §5A scenarios; one portfolio/report contract; protected scheduler with fail-closed deadline handling; isolated/full QA, source publication, explicit live read-only commissioning and scheduler activation. **No further optional B2b source-shape research ahead of this delivery.** Test the *actual* one-entrypoint output, not just helpers; never certify unsupported actions or autonomous ESPN writes. Week 8 capture deadline takes precedence throughout.

## Relevant References

- `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `evidence/WEEK8_B2B4D_FROZEN_ARCHIVE_GATE_2026-10-25.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `../../tools/operations/weekly_operator_v2.py`; `../../tools/operations/weekly_operator_controller.py`; `../../tools/operations/weekly_operator_review.py`; `../../tools/operations/weekly_operator_native_sync_adapter.py`; `../../tools/operations/guarded_weekly_cycle.py`; `../../tests/test_weekly_operator_v2.py`
