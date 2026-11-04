# Current Project State

---
state_updated: 2026-11-04
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week9_supervised_operator_and_coverage_recovery
active_workstream: week9_joint_two_acquisition_paired_mc_shadow
memory_refinement_step: none
nfl_week: 9
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Finish the existing October 27 Windows 10/11 portable v2 operator with complete nine-channel prospective evaluation, P/D/K separation, bounded uncertainty, and independent section-5A certification. Preserve commissioned v0.36 physics/manager kernels, frozen 2026 captures, and human-only ESPN action approval.

## Current Work Item

A source-only, *opt-in shadow* joint response candidate is being prepared. It uses a common native `UtilityContext` and paired scenarios to evaluate current-week `NO_ACTION`, `MOVE_ONLY`, `FIRST_ONLY`, `SECOND_ONLY`, and `BOTH` states. The selected IR move removes that player from current-week starting choices without asserting future return dates. One player-add and at most one addition per DST/K channel can be composed at the complete-roster boundary. Both-of-same-specialist-channel, unsupported IR specialist moves, absent headroom, unverified acquisition outcomes, and unmodeled joint claim behavior remain explicitly blocked. Exact joint waiver success cannot be inferred from marginal probabilities; only Fréchet bounds are shown. The opt-in code never upgrades action authority or overall IR coverage, and its default configuration performs no additional live MC.

The corrected current candidate has not yet been applied to the Windows control root, staged, published, synchronized to the portable, or live commissioned. Actual carrier and Windows receipts must establish each boundary independently.

## Verified State

- GitHub `main` published `week9_ir_mixed_two_openings_scoped_response_20261104_v1` at `36ea137388c8d6e505f805a1e73667dc80aebeaa`, parent `fff9c2ad0cd1fdb6e32c4877c3c78aca2c62ecaa`, staged/committed tree `61fc2e515a81c2e654a2ebbaafa2f78f5ec30975`, 234 manifest entries, six exact staged paths. Full isolated pytest: 1,138 passed; compileall, diff, memory and staged identity gates passed. Remote branch verification independently confirmed.
- The guarded corrected carrier `week9_ir_mixed_two_openings_portable_v2_guarded_runtime_sync_20261104_v1_carrierfix.ffpkg` was run successfully. Portable runtime `src/ir_replacement.py` now has Git blob `a0c1dffcf13385a44d7dbf6e4eb763e1a089e34e`; unchanged `tools/operations/guarded_weekly_cycle.py` blob `801a87ae3787aa9e159f52964d880d8ff1d1e2ac`. Offline imports/guard/mixed branch passed. One runtime source file changed. No ESPN, capture, native MC, or Git writes occurred in runtime sync.
- Tuesday November 3 and Wednesday November 4 supervised Week 9 phase chains each completed CALENDAR/SYNC/CAPTURE/MC/REVIEW with bound immutable MC receipts. No ESPN writes. Do **not** backfill or rerun those native phases. Wednesday's source-bound frozen IR state is active 15/16, IR 0/1, one directly open active slot, three alternative unlocked IR-move candidates competing for one IR slot, two potential current acquisitions. Four specialist-inclusive trade offers were native candidates but **zero** certified transactions.
- The first joint shadow source carrier (`week9_ir_joint_paired_two_acquisition_shadow_source_20261104_v1`) passed 21 isolated targeted tests before and after a guarded local write but failed strict memory health because candidate `CURRENT.md` omitted three canonical headings and the handoff omitted exact non-override language. It rolled back the entire six-path local apply. This corrected v2 successor changes only the carrier and durable-memory payloads; the tested joint source/module/regression payloads are unchanged.
- Published mixed-capacity source evaluates the one direct addition as scoped P/D/K response and enumerates structurally feasible pairs under one selected legal IR move, but leaves the coupled predictive and acquisition-contingency response unevaluated. Overall IR/weekly coverage remains `INCOMPLETE_COVERAGE`, not an actionable HOLD, certified waiver, trade or ESPN recommendation.

## Calendar / Evidence Gates

Thursday November 5 kickoff is the next prospective Week 9 lock. Saturday's operator is a separately gated future opportunity, not permission to replay Wednesday MC. Capture deadlines outrank nonessential development. No hindsight refit, no ESPN write, no inferred waiver cutoff.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L × sigma × A × epsilon`, `P ⊕ D ⊕ K`, `Delta U = U(S + delta S) - U(S)`, paired common-random-number uncertainty, distinct manager behavior and `MC -> Data -> closure -> diagnosis -> calibration`. `screen != authority`. The native physics distribution must not be retuned to 2026 outcomes in v0.X. Shadow estimates cannot certify actions; section-5A legal/transaction/roster review remains separately required.

## Exact Next Action

1. Run and verify the source-only bounded paired-MC shadow `.ffpkg` on the Windows control root. It must pin the published predecessor source and memory, create a stage-backed full import tree, run both original and new targeted tests before and after apply, enforce strict memory health, idempotence and rollback. No portable/ESPN/native-MC/Git writes.
2. If locally accepted, use the separate generic declarative isolated stage at published base `36ea137388c8d6e505f805a1e73667dc80aebeaa`, rerun full pytest, compileall, staged Git-blob/schema-2 manifest, strict memory and diff gates. Stop before commit/push. Publish only with a separate user-run guarded carrier and independent remote verification.
3. Keep the portable unchanged until separate guarded runtime sync and offline acceptance. Evaluate the opt-in joint shadow and its runtime cost only under a separately authorized non-prospective commissioning context, never by replaying Tuesday/Wednesday frozen MC or using a protected future capture as a test.
4. To qualify full IR coverage, close unsupported same-channel specialist pairing, additional current IR move variants, joint waiver/claim queue behavior, and all legal composites; then commission coupled MC and independent section-5A action certification. Until then no roster-wide `COMPLETE`, no certified trade/waiver/IR action.

## Relevant References

- `architecture/WEEKLY_DECISION_COMPLETION.md`, `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`, `evidence/WEEK9_IR_MIXED_TWO_OPENINGS_SCOPED_RESPONSE_2026-11-04.md`, `evidence/WEEK9_IR_JOINT_PAIRED_SHADOW_2026-11-04.md`.
- `../../src/ir_replacement.py`, `../../src/ir_joint_response.py`, `../../src/ir_roster_state.py`, `../../src/specialist_policy_v032.py`, `../../src/transaction_manager.py`, `../../src/weekly_decision_cycle.py`.

`durable_memory_updated: true`
