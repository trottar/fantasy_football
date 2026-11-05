# Week 9 — Player direct-open-slot acquisition response (authorized source candidate)

Date: 2026-11-05
Checkpoint candidate: `week9_player_direct_open_slot_acquisition_source_20261105_v1`
Status: local-apply accepted (seven paths/six synthetic tests); first isolated full-suite stage blocked by three stale commissioned-runtime pin tests (1,168 passed). Narrow regression-fixture correction pending local validation and restaging. No publication, portable synchronization or commissioned decision authority.

## Authority and motivation

The Thursday Week 9 read-only roster triage returned 15 owned players, 9 starters and 6 bench, no post-frozen roster membership change. Prior IR state was active 15/16 and IR 0/1. The Thursday new prospective snapshot/capture/native receipt has hashes:

- Snapshot: `e2cc6d26e347453aee6bd69c177b33d651a2b7f8217611aa42c2dca2368071b1`.
- Capture: `3d93d1958196b1be3f5ad8abe907092450896ed5c332687b099c5020841c05fd`.
- Native MC: `71cec7edaf59d726adea1fb5df09ddc036824fac803346d2902cb67b4209e7e4`.

A later live diagnostic isolated two market-status changes: Jacoby Brissett (QB) and Emanuel Wilson (RB), WAIVERS to FREEAGENT. They did not appear in four frozen specialist-inclusive trade packages, all uncertified. The complete player acquisition source `src/transaction_manager.py` constructs only add/drop pairs. A currently vacant active slot could therefore lack its own `S -> S + add` response. This is a representation gap, not a proven positive acquisition value or executable transaction. The user authorized the narrow structural source correction.

## Narrow source change

- New `src/open_slot_actions.py` evaluates `S -> S + player` for existing real **active** vacancies using the current `ir_roster_state.build_ir_roster_state` legal capacity evidence and the same QB/RB/WR/TE preselected pool. Unknown/blocked IR state or position maxima fail closed. IR move-plus-add is **not** implicitly treated as direct capacity.
- Existing `src/transaction_manager.py` runs its commissioned add/drop machinery without changes and appends an independent, bounded add-only candidate frontier to its report. Add-only rows carry `drop_espn_id=None`; a strictly internal MC progress sentinel never represents an actual released player. Without a dropped player there is no release-response kernel or field-reallocation credit.
- The helper uses the original native predictive paired-MC stage, deterministic common random numbers, existing status-specific screening/pruning and classification, and a separate manager `p_acquire` for WAIVERS. Cheap screens are not action authority. Existing model parameters are unchanged.
- `src/weekly_decision_cycle.py` exposes the resulting add-only evidence. Where a not-yet-commissioned add-only path finds an otherwise positive candidate, it remains explicitly `INCOMPLETE_COVERAGE:OPEN_SLOT_ADD_ONLY_CERTIFICATION_REQUIRED`, never an automatically authorized acquisition.
- `tests/test_week9_add_only_open_slot.py` supplies synthetic capacity, position limit, no-release, waiver-probability, blocked IR, and weekly receipt regressions.

## Still excluded

No ESPN POST, live action-screen proof, automatic roster actions, broad new waiver claim semantics, same-channel specialist pairs, B2b absence horizon, IR move-plus-add expansion, full roster legal action certification, schedule activation, native MC replay, 2026-based v0.X tuning, or portable runtime change. The last commissioned Week 9 captures remain immutable.

## Expected gates

A guarded local apply must verify exact predecessor source Git blobs, apply only reviewed source/tests/memory paths, run targeted regression against an isolated copy of the installed portable source, and leave staging/commit/push untouched. Subsequently perform full isolated staging, `pytest`, `compileall`, strict memory health, Git blob/index manifest validation, separate authorized publication and separately guarded portable sync/acceptance. Until all applicable gates pass the new path is *source-only* and non-authoritative.

## November 5 full-staging test failure and recovery classification

- Exact failed staged-tree OID: `e0a8bc4600e18b0a75f7596a7e74a7ff479c5dcd`; source scope seven plus schema-2 manifest, 239 memory entries, strict memory and exact index/allowlist checks passed. Full pytest: **1,168 passed, 3 failed** in `tests/test_week9_guard_pin_reconciliation.py`.
- Production guarded launcher continues to pin the **commissioned portable** `src/weekly_decision_cycle.py` blob `1c4c40ffc856e27d7b8c0919ee363ec15ce21f89`. The authorized add-only **developing control root** source has blob `6e8bdd0f1ac904cdbabfa5ccfe8b659f64f27fb1`. These distinct authorities must not be conflated.
- The three failures arose because the historic regression directly asserted the control-root cycle was the pinned portable source, and its synthetic runtime copied that newly edited control-root source. The second failure masked the intended unrelated `src/closure.py` corruption test.
- Narrow repair changes only the regression fixture: the production pin literal and guard identity continue to be checked unchanged; synthetic success and mutation tests bind the fixture's *copied* cycle bytes to an isolated per-test expected hash. No production guard pin change, no model retuning, no MC rerun. The exact restaged source/test scope gains only this existing test path; the evidence and CURRENT revisions are already within the original scope.
- Classification: **STAGING FULL QA BLOCKED, LOCAL-APPLIED VALID**, zero committed/pushed/portable/source-runtime changes. Do not publish the failed stage; repair its test gate and rerun full staged QA before a separate publication package.

`durable_memory_updated: true`

## November 5 correction-carrier v1 rollback and recovery

The first `week9_player_open_slot_guard_pin_test_reconciliation_20261105_v1` local correction passed six isolated guard-pin regressions but rolled back all three files when its postwrite `tools/check_memory_health.py --strict --json` subprocess failed. Its proposed `CURRENT.md` was 9,160 bytes, exceeding the 8,192-byte SOFT threshold, and strict treats SOFT as an issue. The v1 entrypoint suppressed the checker details in its generic `STRICT_MEMORY_HEALTH_PROCESS_FAILED` error. This is package preflight/diagnostic design debt, not a football-regression result. The seven-path add-only control-root change and prior failed isolated staging remain intact; no commit, push, portable sync, ESPN POST, or fresh MC occurred.

The corrective v2 carrier keeps the test fixture and production runtime pin unchanged, moves obsolete active-memory chronology to this evidence record, and uses a temporary copy of the **entire** current `docs/memory` tree plus required sibling documents and the pinned real health checker to perform strict memory validation on the exact candidate **before any target writes**. It must surface subprocess issues and stderr on failure, then independently revalidate after control-root apply with rollback. Previous six isolated tests remain the only targeted football-independent checks. Publication and runtime commissioning are separate gates.
