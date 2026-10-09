# Week 5 Known-Bye Lock Authority Correction — 2026-10-08

---
evidence_type: structural_authority_correction
status: SOURCE_LOCAL_APPLY_CANDIDATE
football_model_tuning: false
runtime_release: v0.36-repack1
internal_version: "0.36"
source_predecessor_blob: 7969052173582e7b10bbdd846fb9f72ad104d676
---

## Trigger and Frozen Authority

The operator ran a fresh authenticated Week 5 snapshot and immutable prospective capture on October 8, 2026, using the commissioned runtime. The capture integrity/pre-data firewall passed. The nine-channel weekly cycle retained `BLOCKED_HEALTH` because machine-readable commissioning identity and strict memory-health evidence were omitted. Its independent lineup receipt was `INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY`.

Read-only packaged hotcheck `week5_receipt_lock_kicker_hotcheck_20261008_v1` proved:

- Exactly one raw lineup-legality gap: `lock_timing_unknown:<player-id>:NO_SCHEDULE`.
- Exactly one unresolved roster member: Harrison Butker (K).
- The configured league bye table establishes `KC: 5`.
- `weekly_manager` explicitly excludes bye players from legal weekly scoring/selection.
- Independent kicker channel: `PASS / HOLD`, `NO_RESOLVED_EDGE`, `P(better)=0.169921875`, mean complete-state delta `+0.006483734631147542`; this does **not** resolve the empty required Week 5 K slot.
- B2a IR open-slot model: one eligible Mayfield IR move; 112 replacement rows, no resolved edge.
- Specialist-inclusive trade search: four modeled ACTIONABLE_OFFER rows, without a verified immediate execution/effective-time gate.
- Snapshot/capture/receipts remain immutable and local-only. No fantasy transaction has occurred.

## Narrow Authorized Structural Correction

The user expressly authorized the Week 5 structural correction on October 8. Modify only `src/weekly_decision_cycle.py` so that the lock authority classifies a missing kickoff as a **known unlocked bye** only when BOTH `NO_SCHEDULE` and exact current-week membership in the league's configured bye table are present. Preserve ESPN explicit lock priority and fail-closed behavior for unknown non-bye schedules, malformed kickoff evidence, and all unsupported lineup slots. Let the existing optimizer independently reject bye players and report mandatory missing slots.

No player MC, DST/K models, IR/waiver behavior kernels, trade-effect-time rules, tuning, transaction submission, persistent observation, or outcome-based calibration is changed.

## Validation and State Boundaries

The local-apply package `week5_bye_lock_source_20261008_v1` carries production transform, seven targeted regressions, and this source-memory checkpoint. Its entrypoint checks exact source/CURRENT predecessors, validates rendered changes in an isolated test tree, applies with backups and rollback, and does not stage/commit/push or mutate the commissioned runtime. Local success is not remote publication, runtime synchronization, operational-health PASS, or roster-action authorization.

The **kicker same-channel policy vs legal mandatory current-week starter** remains a separate unresolved hypothesis. The pre-fix MC receipt does not authorize a new transaction. The Week 5 time-critical action after publishing and commissioning the structural fix is to collect a fresh decision-time snapshot and intact prospective capture, inspect the confirmed missing-slot receipt, then diagnose/repair the kicker baseline if required under a separate authorization and validation gate.

On completion of Week 5 operational actions, resume the Week 3 historical replay Phase-B IR move-to-IR join recorded in the October 7 `CURRENT.md` predecessor. Immutable Phase-A receipts and V002 outcome authority remain intact.

`durable_memory_updated: true`
