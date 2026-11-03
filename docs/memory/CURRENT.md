# Current Project State

---
state_updated: 2026-11-03
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week9_portable_v2_supervised_gui_operator_gate
active_workstream: existing_portable_v2_supervised_weekly_evaluation_gui_entrypoint
memory_refinement_step: none
nfl_week: 9
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Finish the **existing October 27 Windows 10/11 portable v2** recurring weekly operator, not another portable build or report-only prototype. The approved contract is `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` plus `architecture/WEEKLY_DECISION_COMPLETION.md`: prospective capture, nine-channel P/D/K-separated MC, bounded live reconciliation, complete transaction consequences, ranked contingencies, and human-approved ESPN actions only after an independent action certificate.

## Current Work Item

The user authorized a supervised weekly evaluation control in the **existing portable v2 GUI**, with visible progress, failure classification, and no automatic ESPN transactions. The source candidate adds `src/gui/weekly_evaluation_runner.py`, wires an explicit-acknowledgment "Run supervised weekly evaluation" button into `src/gui/weekly_decision_view.py`, gives saved-report refresh visible feedback, and adds provider-free tests. The adapter verifies the pinned installed operator source, exact portable tree, protected slot, and one-start receipts; it launches **only** `weekly_operator_v2.py --mode trial --ack-live-readonly` via the GUI Python interpreter. Progress uses private phase **filenames**, not authenticated payloads. The existing native operator owns sync/capture/MC/review and remains fail-closed. All results retain `ESPN_ACTION_AUTHORITY=NONE`.

**Current boundary: source `LOCAL-APPLIED` only.** The November 3 source package applied six exact files successfully with targeted tests and compile validation, and no runtime, MC, ESPN, or Git publication effects. The first isolated-staging package failed **before staging** at control-root strict memory health (Python exit 1) because the delivered `CURRENT.md` and `CURRENT_HANDOFF.md` used noncanonical heading names/capitalization and handoff non-override wording. The corrective two-file memory-only package replaces those exact local output bytes, preserves the four other applied files, and must pass strict memory health before a corrected separate staging attempt. Do not rerun the already successful six-file local apply.

## Verified State

- Source checkpoint `d746d1a737e7c4901d1782ba8874296fce071dd2` was published and remote verified. The ranked MC GUI update was synchronized offline into existing portable v2; prior exact GUI Git blobs `82ed459dd70120ab25033063755d6480dc520c8b` and `f02b648102541bcf38f297e690d4a7f7adfef39d` were verified before the November 3 source candidate.
- On November 3 the user launched the installed portable v2, identified and restarted the existing port-8080 Python GUI server, and visually verified **Ranked MC decision board | Week 9**. It marked Week 8 evidence `SAVED_WEEK_NOT_CURRENT_DO_NOT_ACT` and `HISTORICAL_DO_NOT_ACT`. This verifies presentation, **not** a fresh Week 9 native run.
- Existing "Refresh saved decisions" rereads immutable saved reports only. The new supervised-evaluation GUI controls remain source-only until separately staged, published, and synchronized into portable v2.
- Existing `tools/operations/weekly_operator_v2.py` Git blob `eb5990de21d2bd80d701fdbfb218dd71db17c2a7` supports explicit supervised `trial` mode and protected calendar, six-provider sync, immutable capture, guarded M1a native MC, live read-only reconciliation, and private report. Production commissioning, full section-5A action certification, unattended scheduler, and ESPN writes remain unapproved.
- Local source-apply receipt: six exact paths, source SHA-256 identities, targeted tests and compile PASS. First staging attempt `week9_portable_v2_gui_supervised_evaluation_stage_20261103_v1` returned `FAIL_CLOSED:COMMAND_FAILED_RC_1` before the stage declaration and before any Git writes. This was **not** a full-test result and does not invalidate the passed local source apply.

## Calendar / Evidence Gates

November 3, 2026 is Week 9 under the project's Monday/Eastern convention; Thursday's next kickoff is November 5. Protect exact claim and player/game deadlines from current verified source evidence, not a guessed schedule. Preserve immutable frozen earlier-week captures; never backdate a missed prospective prediction. Do not run a live operator as an infrastructure test or repeat an uncertain native MC. A supervised run requires an eligible protected pre-lock slot and explicit human acknowledgment.

## Scientific / Architectural Boundaries

Preserve `N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `Delta U = U(S + delta S) - U(S)`; common-random-number paired MC; manager behavior separate from intrinsic football response; `screen != authority`; `MC -> Data -> closure -> diagnosis -> calibration`. No observed 2026 outcomes tune v0.X. No automatic ESPN transactions. Keep secrets, private snapshots, authenticated provider responses, and runtime evidence local. Separate local apply, isolated stage, publication, runtime synchronization, and commissioning.

## Exact Next Action

1. Apply the **two-file strict-memory correction** to `docs/memory/CURRENT.md` and `docs/memory/handoffs/CURRENT_HANDOFF.md`, guarded by the exact November 3 local-apply output SHA-256; preserve all four other applied source/test/evidence files. Validate corrected headings, handoff authority wording, and strict memory health on the corrected local control root. Do not repeat earlier passing local-apply tests or modify installed portable v2.
2. Use a corrected separate staging `.ffpkg` with updated two-file raw SHA-256 values and exact six-file scope. Verify remote predecessor `d746d1a737e7c4901d1782ba8874296fce071dd2`, stage Git clean-filter/index identities and schema-2 memory manifest, run the full `pytest` and `compileall`, and return the staged tree OID. Stop before commit/push.
3. After assistant verifies staged scope/tree, use a separate guarded publication package and independently verify GitHub, then synchronize **only** the two GUI module files to the existing portable v2. Restart GUI once, independently verify installed identities and read-only behavior. Installation must not run provider access, MC, or capture.
4. Invoke the supervised GUI entrypoint only at a valid prospective operating window with user acknowledgment. Inspect private phase and result receipts without promoting unsupported MC candidates to executable recommendations. Full section-5A action certification remains a separate prerequisite for any positive ESPN action recommendation or scheduler activation.

## Relevant References

- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`.
- `evidence/WEEK9_GUI_SUPERVISED_EVALUATION_ENTRYPOINT_2026-11-03.md`; `evidence/WEEK9_MC_DECISION_BOARD_2026-11-02.md`; `evidence/WEEK9_PORTABLE_V2_FROZEN_TRADE_JOIN_2026-11-02.md`.
- `../../src/gui/weekly_decision_view.py`; `../../src/gui/weekly_evaluation_runner.py`; `../../src/gui/weekly_mc_decision_board.py`; `../../tools/operations/weekly_operator_v2.py`; `../../tools/delivery/prepare_checkpoint_stage.py`.

`durable_memory_updated: true`
