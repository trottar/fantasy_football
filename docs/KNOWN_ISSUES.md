# Known Issues and Deferred Work

**As of:** 2026-10-05

This file owns open/deferred/blocker/debt state that should not clutter
`docs/memory/CURRENT.md`. It does not override current authority.

## Blocking Weekly Decision-Orchestration Issues

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Weekly decision completion orchestrator | RESOLVED / GATE A SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts the shared fail-closed receipt contract |
| Weekly operational health receipt | RESOLVED / GATE A RUNTIME-COMMISSIONED | No | Reopen only if the shared health interface fails its required contract |
| Specialist current-WAIVER authority | RESOLVED / B1 SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts the commissioned uncertain-acquisition response; WAIVERS remain distinct from guaranteed FREEAGENTs |
| Automated multi-asset player trade search | RESOLVED / B3 SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh source/runtime/weekly evidence contradicts the commissioned bounded 1x1/1x2/2x1/2x2 player-package search; `evaluate_trade` remains predictive authority |
| Specialist-inclusive trade evaluation | RESOLVED / MULTI-K CORRECTION SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No source/runtime blocker; fresh weekly rerun required for action | Reopen only if fresh post-commissioning evidence contradicts multi-K rejection, multi-DST preservation, or the commissioned single-K boundary |
| Weekly lineup lock legality | RESOLVED / SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No source/runtime blocker; fresh weekly rerun required for action | Reopen only if fresh post-commissioning evidence contradicts locked-starter freeze, locked-bench exclusion, or fail-closed unresolved lock/slot handling |
| Current IR/open-slot roster-state representation | RESOLVED / B2A SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts current ESPN-status-qualified IR legality or active/IR capacity representation |
| Current IR move-plus-add valuation/capacity adapter | RESOLVED / GATE B5 SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh weekly/runtime evidence contradicts the single-B2a scope, kickoff-aware locks, FA/WAIVER uncertainty, complete P/D/K branch coverage, or zero-future-capacity contract |
| IR replacement multiweek temporal horizon | DEFERRED / B2B FAIL-CLOSED / CLAIM-LOCAL QUALIFYING CLAIMS = 0 | Only if a future-capacity claim is needed | Reopen only with fresh qualifying decision-time evidence; do not infer from stale prose, injury type/start date, generic slot compatibility, or outcomes |
| Fresh Week 4 roster-wide cycle | RESOLVED / COMPLETE + ACTION_REQUIRED | No completeness blocker; current action remains state-sensitive | Fresh 15:22 UTC snapshot/capture passed health and all 9 channels. Sole action is Kamara -> Bills D/ST, Week 5 effective under 48-hour review. Reopen current authority with a fresh capture if material roster/injury/market/lock/transaction state changes before submission |

Canonical investigation:
`docs/memory/investigations/WEEKLY_DECISION_ORCHESTRATION_RECOVERY_2026-09-29.md`.

## Deferred Scientific / Operational Work

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Week 1/2 prospective-capture availability | UNCLASSIFIED | Blocks treating those weeks as prospective closure if no frozen capture exists | Inspect genuine frozen evidence only; never backfill |
| Week 3 Data/MC closure | READY / UNBLOCKED | No weekly-completeness blocker remains | Fresh Oct. 5 corrected cycle passed the full receipt matrix; resume after the current Week 4 action gate is handled |
| Three-clean-week prospective closure baseline | INSUFFICIENT EVIDENCE | Yes for broad empirical calibration | Accumulate/verify clean weekly closure before any calibration decision |
| Midseason calibration | DEFERRED PENDING EVIDENCE | No | Authorize only from repeated prospective residual/coverage evidence |
| Historical counterfactual replay / regret laboratory | PHASE-A TOOLING PUSHED / REMOTE VERIFIED | No current Week 4 action blocker | Checkpoint `b038c6b388f1a4aefc53c45ce1c924ed9e9bdb85` / tree `e59b6e7d2930b42d2a2af8e1e54e14756763c86e` published the provenance/receipt/outcome-firewall tooling. Provenance bootstrap remains: Weeks 1-2 reconstructed-only; Week 3 reconstructed overall with frozen roster/specialist sub-surfaces and reconstructed player-market values. Next: build the Week 3 input adapter and blind candidate evaluation before any outcome attachment |
| Persistent runtime evidence sink | INTENTIONAL / DISABLED | No | Enable only after separate privacy/non-interference authorization |
| Phase 1E activation | SEPARATELY GATED / NOT AUTHORIZED | No | Requires its own explicit authorization and commissioning evidence |
| Playoff production baseline | PLANNED | Becomes blocking before Week 14 | Commission before Week 14 |

## Memory / Workflow Debt

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Active-memory semantic-integrity gap | RESOLVED / PUSHED / REMOTE VERIFIED | No | Reopen only if fresh deterministic repository-state contradictions appear |
| Historical replay Phase-A source local-apply v1 full-suite control-root validation | SUPERSEDED VALIDATION-CONTEXT FAILURE / ROLLED BACK | No | Exact replay candidate passed its focused suite, but unrestricted full-suite validation ran against the synchronized sparse control root, which lacks repository paths such as `pytest.ini`, `tests/test_closure_v029.py`, and `src/data_sources/espn.py`; 887 errors were therefore non-authoritative. Rollback removed both new paths |
| Historical replay Phase-A source local-apply v2 import smoke | SUPERSEDED VALIDATION-HARNESS FAILURE / ROLLED BACK | No | Custom `module_from_spec` / `exec_module` smoke did not register the module in `sys.modules`; Python 3.13 dataclass processing raised `AttributeError: 'NoneType' object has no attribute '__dict__'`. Source bytes were unchanged and rollback removed both paths |
| Historical replay Phase-A isolated full-repository preflight + local-apply v3 | RESOLVED / SOURCE LOCAL-APPLIED + VALIDATED | No | Exact source/test candidate passed 14 focused tests, 609 full-repository tests in isolated predecessor checkout `f9023a9d...`, `compileall`, exact two-path staging, cached diff check, corrected real-package import smoke, local focused tests, SHA identities, and whitespace validation |
| Historical replay Phase-A memory local-apply v1 CURRENT threshold | SUPERSEDED MEMORY-HARNESS FAILURE / NO WRITE | No | Candidate strict memory health correctly blocked before write because the rendered `CURRENT.md` grew to 179 lines, crossing the 175-line soft threshold. v2 keeps CURRENT active-state only and moves detail to architecture/evidence |
| Gate B3 source-preflight v1 legacy expectation mismatch | SUPERSEDED TEST-HARNESS FAILURE / NO MODIFICATION | No | Candidate closed the multi-asset blocker correctly; legacy Gate A regression expectation was updated and v2 preflight passed |
| Gate B3 source local-apply v1 clone-head guard | SUPERSEDED PACKAGING FAILURE / FAILED BEFORE SOURCE WRITE | No | Fresh-clone `HEAD:<path>` checks were invalid on the synchronized control root; v2 removed only that redundant guard |
| Gate B3 source local-apply v2 sparse-test validation | SUPERSEDED VALIDATION-HARNESS FAILURE / ROLLED BACK | No | Control root lacks the full repository test inventory; v3 preserved exact local guards and validated the applied four-file result in a fresh remote-clone overlay |
| Gate B3 runtime commissioning v1 control-root remote assumption | SUPERSEDED COMMISSIONING HARNESS FAILURE / FAILED BEFORE MODIFICATION | No | v1 incorrectly assumed the synchronized control root had a usable Git `origin`; corrected v2 queries the canonical repository URL directly and commissioned successfully |
| Specialist trade audit v1 runner-argument mismatch | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / FAILED BEFORE PROBE | No | Entrypoint omitted the generic runner's injected arguments; corrected successors preserved the generic runner contract |
| Specialist trade audit v2 import-absence guard | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / FAILED BEFORE FOOTBALL PROBE | No | Harness incorrectly required `src.market_manager` to be globally unimportable outside the runtime root; v3 verified exact module origins under the runtime cwd/PYTHONPATH contract |
| Specialist trade source preflight v1 porcelain parser | SUPERSEDED PREFLIGHT-HARNESS FAILURE / NON-MUTATING | No | `git_text(...).strip()` removed the first porcelain status line's leading space and shifted the path slice to `rc/...`; v2 reads raw status stdout and regression-tests the exact first-line case |
| Specialist trade runtime-memory v1 handoff/MEMORY health | SUPERSEDED MEMORY-HARNESS FAILURE / ROLLED BACK | No | v1 used a noncanonical no-exception handoff representation and expanded `MEMORY.md` beyond the strict soft line threshold; v2 restores the canonical handoff structure and compacts the durable specialist commissioning update |
| Specialist trade multi-K preflight v1 | SUPERSEDED HARNESS PATH-PARSER FAILURE / NON-MUTATING | No | Git CRLF warnings on stderr were merged into stdout and misread as changed paths; v2 separated streams |
| Specialist trade multi-K preflight v2 | SUPERSEDED TEST-HARNESS FAILURE / NON-MUTATING | No | Production candidate compiled and 26 targeted tests passed; one new regression referenced `Path` without importing it; v3 used builtin `open` |
| Specialist trade multi-K preflight v3 | RESOLVED / PASS / NON-MUTATING | No | Exact two-path candidate passed user/partner multi-K rejection, multi-DST preservation, targeted/full pytest, compileall, strict memory health, and `git diff --check` |
| Specialist trade multi-K runtime commission v1 | RESOLVED / COMMISSIONED + VALIDATED | No | Exact published source retained as the sole production change; focused multi-K rejection and multi-DST preservation probes, targeted/full pytest, compileall, import-root, identity, and residue checks passed; rollback false |
| Week 4 post-multi-K fresh-cycle carrier v2 | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / NON-MUTATING | No | `os.chdir(runtime)` did not alter the running interpreter's import path, causing `ModuleNotFoundError: src` before live capture; v3 explicitly installed the runtime root and succeeded |
| Weekly lineup lock source preflight v1 | SUPERSEDED HARNESS PATH-PARSER FAILURE / NON-MUTATING | No | Candidate validations passed, but a Git CRLF warning from stderr was merged into stdout and misread as a changed filename; v2 separated streams |
| Weekly lineup lock source preflight v2 | RESOLVED / PASS / NON-MUTATING | No | Exact source/test candidate passed lock regressions, frozen Oct. 4 Meyers/Kamara timing probe, prior targeted/full/compileall/memory/diff gates, and exact changed-path inventory |
| Weekly lineup lock runtime commission v1 | RESOLVED / COMMISSIONED + VALIDATED | No | Exact published source retained as the sole production change; frozen Oct. 4 lock probe, targeted/full runtime pytest, compileall, import-root, identity, residue, and rollback checks passed; rollback false |
| Trade effective-timing source preflight v1 | SUPERSEDED CANDIDATE VALIDATION-ORDER FAILURE / NON-MUTATING | No | Timing settings were required before specialist authority rejected a player-only package; no source/runtime/stage changed |
| Trade effective-timing source preflight v2 | SUPERSEDED CANDIDATE VALIDATION-ORDER FAILURE / NON-MUTATING | No | Symmetric player authority regression: timing settings were required before DST/K rejection; full suite reached 594 passed / 1 failed |
| Trade effective-timing source preflight v3 | SUPERSEDED DETERMINISTIC RENDERING FAILURE / NON-MUTATING | No | Targeted tests, real Oct. 5 probe, full pytest 595 passed, compileall, and strict memory health passed; `git diff --check` caught one generated blank line at EOF |
| Trade effective-timing source preflight v4 | RESOLVED / PASS / NON-MUTATING | No | Exact 9-path candidate passed effective-week boundaries, real Kamara/Bills Week 5 probe, carried-forward 595-test suite, compileall/memory health, EOF validation, `git diff --check`, and exact path inventory |
| Trade effective-timing source local apply v1 | SUPERSEDED SPARSE-CONTROL-ROOT PRESTATE FAILURE / FAILED BEFORE WRITE | No | Package incorrectly required every remote-tracked predecessor path to exist in the split control root; source/runtime/memory remained unchanged |
| Trade effective-timing source local apply v2 | RESOLVED / LOCAL-APPLIED + VALIDATED | No | Exact v4 candidate rendered from remote `6baebc...`, absent reviewed control-root paths were safe-to-create, all nine post-write SHA/blob/AST/whitespace identities passed |
| Trade effective-timing runtime commission v1 | SUPERSEDED VALIDATION-HARNESS FAILURE / ROLLED BACK | No | Production paths passed import/frozen timing probe, but stale runtime `test_market_manager_v030.py` fixtures lacked `transaction_settings`; full runtime pytest failed 4 tests and all four production paths rolled back |
| Trade effective-timing runtime commission v2 | RESOLVED / COMMISSIONED + VALIDATED | No source/runtime blocker; fresh weekly rerun required | Exact four published production paths installed; frozen Oct. 5 timing probe, published full test suite over actual runtime bytes, compileall, identities, and residue checks passed; rollback false |
| Specialist ranked-row timing representation | OPEN / NONBLOCKING DIAGNOSTIC REPRESENTATION GAP | No | `search_specialist_trades()` compact result rows omit the evaluator's `trade_timing` and current-week delta fields. Fresh action remained valid because timing was already applied inside evaluation; a read-only extractor recovered Week 5 timing from the exact frozen snapshot without rerunning MC. Address only as a reporting/observability improvement |
| IR adapter source preflight v1 | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / NON-MUTATING | No | Windows denied cleanup of a read-only Git pack index in the disposable clone; no tracked source/runtime/stage changed |
| IR adapter source preflight v2 | SUPERSEDED CANDIDATE VALIDATION FAILURE / NON-MUTATING | No | Targeted Gate A/B tests passed; full pytest reached 576 passed / 1 failed on the pre-existing B4 weekly-contract literal. Later source audit also invalidated the candidate design as complete |
| IR adapter source preflight v3 | SUPERSEDED DETERMINISTIC PACKAGE-CONSTRUCTION FAILURE / NON-MUTATING | No | A test-file transform was put in a global transform list and incorrectly required against `src/weekly_decision_cycle.py`; future packages must route transforms by file and execute the exact routing logic in QA |
| IR adapter source preflight v4 | RESOLVED / PASS / NON-MUTATING | No | Redesigned candidate passed exact path-keyed transform-routing QA, targeted/full pytest, compileall, strict memory health, and `git diff --check`; exact five-path result was then local-applied/validated with source publication and runtime commissioning still pending |
| IR adapter runtime commissioning v1 | SUPERSEDED VALIDATION-HARNESS FAILURE / ROLLED BACK | No | Production candidate was written, but targeted pytest could not start because the sparse runtime lacked `test_weekly_decision_gate_b2a_ir_roster_state.py`; rollback verified the predecessor runtime |
| IR adapter runtime commissioning v2 | RESOLVED / COMMISSIONED + VALIDATED | No | Six targeted regressions were verified from published control-root blobs, temporarily overlaid, targeted/full pytest plus compileall/import checks passed, validation paths were restored/removed, and the three production runtime files retained exact published identities |

## Standing Scientific Non-Issues

Do not reopen without new evidence:

- `P ⊕ D ⊕ K` valuation/channel separation;
- channel separation is not transaction exclusion;
- `0.X` a-priori / `1.X` empirical boundary;
- manager behavior versus intrinsic football utility;
- `screen != authority`;
- frozen prediction / decision-time causality;
- raw observation versus derived/calibrated state;
- human-in-the-loop checkpoint actor separation;
- commissioned v1.0A shadow boundaries already proven by their canonical receipts.

## Missed-Capture Policy

A missing pregame or decision-time capture is an evidence gap, not permission to
reconstruct a prospective state from hindsight. Record what is missing, when its
window passed, what downstream analysis is unavailable, and the next causally
valid capture opportunity.

## Reopen Rule

A resolved/deferred item reopens only when new source, runtime, weekly closure, or
operational evidence contradicts the standing classification.
