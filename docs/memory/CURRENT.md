# Current Project State

---
state_updated: 2026-11-03
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week9_supervised_operator_and_coverage_recovery
active_workstream: week9_direct_open_active_slot_current_only_ir_replacement
memory_refinement_step: none
nfl_week: 9
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Finish the existing October 27 Windows 10/11 portable v2 weekly operator, not a new portable build. The contract in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md` requires nine-channel prospective P/D/K-separated decision evaluation, complete legal transaction consequences, and independent action certification before any recommendation for human ESPN approval. Preserve the commissioned v0.36 kernels and frozen evidence.

## Current Work Item

**Week 9 current B2a direct-open-slot coverage recovery.** Committed `src/ir_roster_state.py` distinguishes direct open active slots from IR-move-created slots. The existing `src/ir_replacement.py` values only one IR-created current-week opening and returns `DIRECT_OPEN_ACTIVE_SLOT_OUT_OF_SCOPE` for a direct open slot, leaving mandatory action coverage incomplete. The intended source-only successor admits exactly one currently open active slot with no IR move, evaluates P/D/K candidates through the existing current-week complete-roster machinery, distinguishes `DIRECT_OPEN_SLOT_ADD` from `IR_MOVE_PLUS_ADD`, and retains no future capacity credit. Multiple openings, unsupported horizon assumptions, missing position headroom, and unsupported states must remain fail-closed.

## Verified State

- GitHub `main` at inspected predecessor commit `722ead079dba9aa4251a0beef55738c9bb918450` already contains the weekly-cycle guard-pin reconciliation: `tools/operations/guarded_weekly_cycle.py` blob `801a87ae3787aa9e159f52964d880d8ff1d1e2ac` pins published `src/weekly_decision_cycle.py` blob `1c4c40ffc856e27d7b8c0919ee363ec15ce21f89`. The prior active memory had incorrectly still called this source repair pending; portable runtime synchronization of that guard has not been demonstrated in the present recovery evidence.
- The previous Week 9 supervised GUI trial returned `BLOCKED_NO_VALID_PUBLIC_RESULT` with no Tuesday trial launch, SYNC, CAPTURE, MC, or REPORT marker; it is not a valid Week 9 operator result. Existing ranked Week 8 output remains historical, not prospective Week 9 authority.
- The first attempted source carrier, `week9_ir_direct_open_slot_b2a_current_only_20261103_v1`, was blocked and rolled back following targeted pytest exit 2. The successful follow-up read-only diagnostic `week9_ir_apply_targeted_pytest_rc2_isolated_diagnostic_20261103_v1` reconstructed the failed source/test transforms and classified two `ModuleNotFoundError: src.weekly_manager` collection errors. The committed `src/weekly_manager.py` does exist; that isolated test context was incomplete. Its diagnostic did not change source, runtime, Git, capture, or MC state.
- The validated sparse-root stage-backed source-only successor carries the minimal direct-capacity branch and no-IR action classification, source-bound regression, current active-memory reconciliation, and sanitized diagnostic evidence. Its successful guarded run proves stage-backed isolated targeted tests before writes and again from the applied source/test bytes, plus strict memory health. **The retained post-apply memory is `LOCAL-APPLIED` only**; actual receipt identities govern acceptance. Full-suite validation, staging, publication, portable sync, and live commissioning remain unverified.

## Calendar / Evidence Gates

Week 9 Tuesday is November 3, 2026; the next scheduled Thursday game is November 5. A valid prospective opportunity/capture must precede relevant locks or outcomes and cannot be backfilled. No inferred waiver deadline, retrospective MC, repeat uncertain native MC, or live operator infrastructure test. Current operational health and eligibility require fresh protected-window evidence.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L × sigma × A × epsilon`, `P ⊕ D ⊕ K`, `Delta U = U(S + delta S) - U(S)`, common-random-number uncertainty, separate manager behavior, and `MC -> Data -> closure -> diagnosis -> calibration`. `screen != authority`. No observed 2026 outcomes tune v0.X. No automatic ESPN writes. All private authenticated sources and runtime receipts remain local. Keep `LOCAL-APPLIED`, `STAGED`, `PUSHED / REMOTE VERIFIED`, portable `SYNCED`, and commissioned trial authority distinct.

## Exact Next Action

1. Verify the Week 9 direct-slot successor **`LOCAL-APPLIED`** result against its exact predecessor/result blobs, stage-backed isolated targeted pytest before and after local writes, and strict memory health. A missing or failing receipt blocks promotion; never infer success from the presence of a file. Do not repeat the completed earlier diagnostic.
2. After validating the local receipt, prepare a **five-source-path** declarative isolated stage plus schema-2 memory manifest, with exact predecessor/remote checks, full pytest, compileall, strict memory health and diff checks. Stop before commit/push.
3. Publish only that validated stage using a separate guarded `.ffpkg`; independently remote-verify. Audit the previously published guard-pin runtime sync independently before any GUI trial. No runtime synchronization or live ESPN/MC action is implied by source publication.
4. Only after offline preflight and fresh protected-window eligibility may a human explicitly launch a supervised read-only Week 9 cycle. No positive ESPN action recommendation or automatic scheduler/transactions until independent section-5A certification is commissioned.

## Relevant References

- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`, `architecture/WEEKLY_DECISION_COMPLETION.md`, `evidence/WEEK9_GUARD_PIN_RECONCILIATION_2026-11-03.md`, `evidence/WEEK9_IR_DIRECT_OPEN_SLOT_RC2_RECOVERY_2026-11-03.md`.
- `../../src/ir_replacement.py`, `../../src/ir_roster_state.py`, `../../src/specialist_policy_v032.py`, `../../src/weekly_decision_cycle.py`, `../../tools/operations/guarded_weekly_cycle.py`.

`durable_memory_updated: true`
