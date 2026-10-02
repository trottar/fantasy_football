# Known Issues and Deferred Work

**As of:** 2026-10-01

This file owns open/deferred/blocker/debt state that should not clutter
`docs/memory/CURRENT.md`. It does not override current authority.

## Blocking Weekly Decision-Orchestration Issues

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Weekly decision completion orchestrator | RESOLVED / GATE A SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts the shared fail-closed receipt contract |
| Weekly operational health receipt | RESOLVED / GATE A RUNTIME-COMMISSIONED | No | Reopen only if the shared health interface fails its required contract |
| Specialist current-WAIVER authority | RESOLVED / B1 SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts the commissioned uncertain-acquisition response; WAIVERS remain distinct from guaranteed FREEAGENTs |
| Automated multi-asset player trade search | RESOLVED / B3 SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh source/runtime/weekly evidence contradicts the commissioned bounded 1x1/1x2/2x1/2x2 player-package search; `evaluate_trade` remains predictive authority |
| Specialist-inclusive trade evaluation | SOURCE-VALIDATED / LOCAL-APPLIED / PUBLICATION + RUNTIME COMMISSIONING PENDING | Yes when league rules permit | Exact four-path patch passed source preflight and local apply while leaving Gate B3 market authority unchanged; close only after guarded source publication and exact runtime commissioning/probe |
| Current IR/open-slot roster-state representation | RESOLVED / B2A SOURCE-PUBLISHED + RUNTIME-COMMISSIONED | No | Reopen only if fresh runtime/weekly evidence contradicts current ESPN-status-qualified IR legality or active/IR capacity representation |
| IR replacement / multiweek temporal roster state | DEFERRED / B2B FAIL-CLOSED / CURRENT NARRATIVES NOT AUTHORITATIVE | Yes when known absence horizon affects replacement or future capacity value | Fresh ESPN narratives can contain quantified return language, but current Week 4 claims fail hard-unavailable/freshness/current-binding guards. Reopen only with fresh qualifying decision-time evidence; do not infer from stale prose, injury type/start date, generic slot compatibility, or outcomes |
| Fresh complete Week 4 cycle | BLOCKED PENDING SPECIALIST TRADE COMMISSIONING | Yes | Run only after the exact specialist-inclusive trade source checkpoint is remote-verified and runtime-commissioned; do not backfill missing earlier searches |

Canonical investigation:
`docs/memory/investigations/WEEKLY_DECISION_ORCHESTRATION_RECOVERY_2026-09-29.md`.

## Deferred Scientific / Operational Work

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Week 1/2 prospective-capture availability | UNCLASSIFIED | Blocks treating those weeks as prospective closure if no frozen capture exists | Inspect genuine frozen evidence only; never backfill |
| Week 3 Data/MC closure | DEFERRED / BLOCKED | Yes for Week 3 closure only | Resume after required Gate B coverage is commissioned and a fresh complete weekly cycle proves the full receipt matrix |
| Three-clean-week prospective closure baseline | INSUFFICIENT EVIDENCE | Yes for broad empirical calibration | Accumulate/verify clean weekly closure before any calibration decision |
| Midseason calibration | DEFERRED PENDING EVIDENCE | No | Authorize only from repeated prospective residual/coverage evidence |
| Persistent runtime evidence sink | INTENTIONAL / DISABLED | No | Enable only after separate privacy/non-interference authorization |
| Phase 1E activation | SEPARATELY GATED / NOT AUTHORIZED | No | Requires its own explicit authorization and commissioning evidence |
| Playoff production baseline | PLANNED | Becomes blocking before Week 14 | Commission before Week 14 |

## Memory / Workflow Debt

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Active-memory semantic-integrity gap | RESOLVED / PUSHED / REMOTE VERIFIED | No | Reopen only if fresh deterministic repository-state contradictions appear |
| Gate B3 source-preflight v1 legacy expectation mismatch | SUPERSEDED TEST-HARNESS FAILURE / NO MODIFICATION | No | Candidate closed the multi-asset blocker correctly; legacy Gate A regression expectation was updated and v2 preflight passed |
| Gate B3 source local-apply v1 clone-head guard | SUPERSEDED PACKAGING FAILURE / FAILED BEFORE SOURCE WRITE | No | Fresh-clone `HEAD:<path>` checks were invalid on the synchronized control root; v2 removed only that redundant guard |
| Gate B3 source local-apply v2 sparse-test validation | SUPERSEDED VALIDATION-HARNESS FAILURE / ROLLED BACK | No | Control root lacks the full repository test inventory; v3 preserved exact local guards and validated the applied four-file result in a fresh remote-clone overlay |
| Gate B3 runtime commissioning v1 control-root remote assumption | SUPERSEDED COMMISSIONING HARNESS FAILURE / FAILED BEFORE MODIFICATION | No | v1 incorrectly assumed the synchronized control root had a usable Git `origin`; corrected v2 queries the canonical repository URL directly and commissioned successfully |
| Specialist trade audit v1 runner-argument mismatch | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / FAILED BEFORE PROBE | No | Entrypoint omitted the generic runner's injected arguments; corrected successors preserved the generic runner contract |
| Specialist trade audit v2 import-absence guard | SUPERSEDED DIAGNOSTIC HARNESS FAILURE / FAILED BEFORE FOOTBALL PROBE | No | Harness incorrectly required `src.market_manager` to be globally unimportable outside the runtime root; v3 verified exact module origins under the runtime cwd/PYTHONPATH contract |
| Specialist trade source preflight v1 porcelain parser | SUPERSEDED PREFLIGHT-HARNESS FAILURE / NON-MUTATING | No | `git_text(...).strip()` removed the first porcelain status line's leading space and shifted the path slice to `rc/...`; v2 reads raw status stdout and regression-tests the exact first-line case |

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

A resolved/deferred item reopens only when new source, runtime, weekly closure,
or operational evidence contradicts the standing classification.
