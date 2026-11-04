# Week 9 — direct-open-slot IR RC2 test-context recovery

`durable_memory_updated: true`

## Source and diagnostic lineage

GitHub predecessor commit: `722ead079dba9aa4251a0beef55738c9bb918450`.

Existing committed baseline: `src/ir_replacement.py` blob `6344a0b21d0a2397acb10d66d9e8e59932004f22` and the existing seven-case IR replacement regression file blob `fffc28f0f02dab23ad940ed1e842c6518cc0c4da`. The existing `src/weekly_manager.py` blob `15a2f734b8b379fe54fac885c756c6dd7dec7398` is present in the published repository. The guard-pin correction is independently committed with guard blob `801a87ae3787aa9e159f52964d880d8ff1d1e2ac`.

The first source-apply carrier `week9_ir_direct_open_slot_b2a_current_only_20261103_v1` failed targeted pytest (exit code 2) and rolled back without source/runtime/ESPN/MC/Git effects. The follow-up diagnostic `week9_ir_apply_targeted_pytest_rc2_isolated_diagnostic_20261103_v1` completed with `PYTEST_EXIT_CODE=2`, `PYTEST_CLASSIFIERS=IMPORT_MISSING_MODULE:src.weekly_manager,PYTEST_COLLECTION_ERROR,PYTEST_INTERRUPTED`, `PYTEST_COUNT_ERROR=2 errors`, `PYTEST_EXCEPTION_TYPES=ModuleNotFoundError`, `RECONSTRUCTION=EXACT_FAILED_CARRIER_TRANSFORMS`, and `CONTROL_ROOT_UNCHANGED=TRUE`, `PORTABLE_RUNTIME_UNCHANGED=TRUE`, `ESPN=NONE`, `CAPTURE=NONE`, `MC=NONE`, `GIT_WRITES=NONE`. Reconstructed candidate blob labels `a8acf6a55e1a25b06b0d224d2edaca564f85ca35` and `8d69a65c139f5de211b99886bcadf4df57c38fa0` belong only to the prior failed candidate and are not validation of it.

## Narrow successor scope

Correct only one supported current B2a state: exactly one direct open active roster slot, no IR move, current-week complete-state P/D/K evaluation. Keep no-drop consequences, explicit `DIRECT_OPEN_SLOT_ADD` action kind, no future capacity credit, no assumed future waiver success, the P/D/K specialist policy and v0.36 kernels unchanged. Multi-slot, ambiguous IR/horizon, locked candidates, and missing position headroom remain fail-closed.

The v2 successor `week9_ir_direct_open_slot_full_import_root_local_apply_20261103_v2` was blocked in its pre-state before writing because it wrongly required `src/weekly_manager.py` in the control root. Its log recorded `MISSING_WEEKLY_MANAGER_IN_CONTROL_ROOT`, exit code 3, and no runtime/ESPN/MC/Git effects. The subsequent `week9_ir_sparse_control_root_layout_readonly_probe_20261103_v1` succeeded read-only: the control root has 45 Python source files, lacks `src/weekly_manager.py` and `src/specialist_channels.py`, and has exactly one test matching the published test blob at `tests/test_weekly_decision_gate_b2_ir_move_plus_add.py`. Both discovered isolated stage checkouts contain all five exact relevant source blobs; the existing portable commissioned release also contains them but must remain untouched.

The corrected v3 package selects a read-only isolated stage checkout with exact five-blob and test identities. It constructs disposable shadow trees from stage dependency source overlaid with authoritative control-root source, the proposed IR source patch and exact patched regression. It checks that `src.weekly_manager`, `src.ir_replacement`, and `src.specialist_channels` import from the temporary root, runs targeted tests before writes and again from the post-write source/test bytes, then strict durable-memory health. It never writes to stage or portable source, and backs up/rolls back only the five intended control-root paths on failure.

## Evidence boundary

This record describes the source candidate and its fail-closed validation plan. It is **not** a full-suite pass, isolated stage, Git commit, remote verification, portable runtime sync, supervised Week 9 trial, operational action certificate, ESPN transaction, or MC result. Preserve operator receipts and detailed outcomes locally until the user returns the package summary. The next checkpoint must validate actual package identities and the full isolated staging gate.
