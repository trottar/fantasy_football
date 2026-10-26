# Current Project State

---
state_updated: 2026-10-25
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_v2_phase_receipt_recovery
memory_refinement_step: none
nfl_week: 7
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Deliver and commission the unattended weekly fantasy decision procedure for Week 8**, not more standalone source-shape probes. One locally installed, scheduled controller must execute deadline-aware six-provider sync, immutable prospective capture, independently guarded nine-channel native MC, live ESPN drift reconciliation, complete P/D/K-aware roster/transaction certification, and one decision/report queue. A human approves actual ESPN actions; ChatGPT is not a weekly workflow step. Preserve commissioned `v0.36-repack1` physics/manager separation and no automatic ESPN writes or 2026-outcome tuning of v0.X. Acceptance owner: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Week 8 v2 phase-receipt recovery source candidate.** The initial integrated controller is source-published/remote-verified at `bc3575407f73bc1dc282deb208632af0746b9000` (tree `6a0dd6dd74f38339974e5bfd1bfa50f4d02720fe`, 1046 isolated full tests, manifest 216), but never runtime commissioned or scheduled. Exact-source audit found its per-slot launch marker prevented rerun of any interrupted sync/capture/MC workflow, even after durable early phases were valid. The successor adds create-only, source/launch/dependency-bound `SYNC`, `CAPTURE`, and `MC` start/completion receipts. Completed sync/capture are reused only with exact unchanged frozen identities and a 2-hour age gate; ambiguous started-but-uncompleted sync/capture block without implicit repeat. An interrupted MC is resumed only through existing M1a's native launch/receipt guards. Receipt corruption, clock drift and missing MC output remain fail-closed. `weekly_operator_v2.py` remains activation-gated and action-incomplete. Canonical evidence: `evidence/WEEK8_V2_PHASE_RECOVERY_SOURCE_2026-10-25.md`.

## Verified State

- **Validated predecessor:** GitHub `main` `bc3575407f73bc1dc282deb208632af0746b9000`, parent `e714f22815375723fcda620f13b7c058c25bc16d`, exact staged/committed tree `6a0dd6dd74f38339974e5bfd1bfa50f4d02720fe`, 6 paths/216 manifest entries. Staging receipt: 16 isolated integration + 1046 full tests, compileall, strict memory health and diff checks PASS. Source publication is not commissioning.
- **Commissioned baseline:** `fantasy_season_v0_36_repack1` / internal `VERSION=0.36` unchanged. No v2 run commissioning receipt, Windows schedule or ESPN submission authority exists.
- **Calendar:** Sunday October 25 is NFL Week 7; Week 8 operations begin Monday October 26, first game Thursday October 29; an October 25 archive inventory (29 inspected, 0 Week 8) did not show a missed Week 8 prospective gate. Protect real upcoming captures and independently verified claim/player locks.
- **Operating gaps:** prior v2 source has one coordinator but not a commissioned autonomous procedure. Full §5A legal alternatives, uncertain future fill, complete injury/roster consequences, eight acceptance fixtures, ranked approved action portfolio, bounded material-drift recovery, scheduler installation and live end-to-end QA remain missing. `processDate` is not proven actual effective time.
- **Scientific evidence:** Week 7 immutable six-provider/capture/MC receipts remain preserved; Week 5 component closure and B2b absence horizon remain separately deferred. No source diagnostics authorize action or v0.X empirical retuning.

## Calendar / Evidence Gates

Protect Week **8** genuinely prospective windows now: Monday October 26 week-open, Tuesday pre-waiver (exact league cutoff **unknown until observed**), Wednesday October 28 primary, Saturday October 31 secondary, and every actual player/claim lock. The first Week 8 NFL game is Thursday October 29. A future matching snapshot can be newly captured before relevant outcomes; it must never be backdated or treated as covering already-elapsed outcomes. Protect capture ahead of nonessential development. Do not invent ESPN cutoffs, assume a trade is executable, infer future free-agent fills, or run an MC without validated timing/lead. Scheduler must remain disabled until commissioning.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. Only prospective decision-time information. Players vs players, DST vs DST, K vs K; couple only complete-roster utility. Preserve paired CRN and manager behavior separate from intrinsic football response. `screen != authority`. A native `ACTIONABLE_OFFER` is never a certified ESPN submission. Unsupported required coverage means `INCOMPLETE_COVERAGE`; invalid health means `BLOCKED_HEALTH`, not HOLD.

## Exact Next Action

**Apply the narrow v2 restart-safe phase-receipt source/test/memory checkpoint**, preserving installed runtime, scheduler, MC and ESPN untouched. Validate exact published predecessor Git blobs for overwrite targets, source-only scope, rendered-memory health, rollback, same-epoch crash/restart and incomplete-phase fail-closed synthetic tests. Then stage exactly the reviewed paths plus schema-2 manifest in the isolated Git checkout; run full pytest, compileall, diff/identity/memory gates; use a separate user-authorized guarded publication carrier and remote verification. This patch does **not** commission the operator. Next, complete the native read-only acceptance run and one bounded material-drift recovery, then full §5A action certification/eight fixtures, ranked report and protected scheduler commissioning. Protect a genuine Week 8 prospective capture before verified locks; do not wait for nonessential engineering if the calendar gate arrives. No automatic ESPN writes.

## Relevant References

- `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`; `evidence/WEEK8_V2_PHASE_RECOVERY_SOURCE_2026-10-25.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `../../tools/operations/weekly_operator_v2.py`; `../../tools/operations/weekly_operator_controller.py`; `../../tools/operations/guarded_weekly_cycle.py`; `../../tests/test_weekly_operator_v2.py`
