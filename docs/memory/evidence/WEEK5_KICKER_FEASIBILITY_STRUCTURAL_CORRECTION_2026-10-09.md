# Week 5 Kicker Mandatory-Feasibility Structural Correction — 2026-10-09

---
evidence_type: structural_authority_correction
status: LOCAL_APPLY_CANDIDATE
source_checkpoint_predecessor: cb09994f3551153f93f1ef5a94ef003dbef1d6cb
runtime_baseline: v0.36-repack1
production_tuning: false
transaction_execution: false
---

## Frozen evidence and narrow hypothesis

Read-only local diagnostics on October 9 found one owned K on a configured Week 5 bye, zero non-bye owned K, and 19 NFL-actionable non-bye FREEAGENT K in the frozen October 8 snapshot. The complete-roster optional kicker policy classified the one-slot/HOLD paired response `NO_RESOLVED_EDGE` (mean `+0.006483734631147542`, `P(better)=0.169921875`), producing a scoped kicker HOLD while lineup legality remained `INCOMPLETE_COVERAGE:LINEUP_MISSING_SLOTS`. An unfiltered expected-response screen proposed a legal K-for-K swap at `7.148611` expected points from MIN K, with verified `NFLVERSE_SCHEDULE` kickoff. No current acquisition authority was established.

The defect is conflating **mandatory feasible lineup repair** with **optional improvement significance**. It is structural, not an empirical miscalibration of the v0.X football model.

## Authorized candidate contract

On October 9 the operator explicitly approved a narrow feasibility-first correction without roster transactions. In `src/specialist_policy_v032.py`, only when the user has exactly one owned K on an explicit configured bye and a legal unlocked drop: enumerate the entire guaranteed same-channel K FREEAGENT pool, reject configured byes and unresolved/already-locked kickoffs, use pregame K expected response only to order the legal frontier, and evaluate **every feasible same-channel swap** with existing paired complete-roster MC using common random numbers. Rank repairs by modeled complete-roster response, not by the screen. Feasibility is lexicographically required; retain the MC uncertainty classification, but do not require statistical superiority to the infeasible HOLD state. If evidence, legal drop, lineup capacity, acquisition status, or MC response cannot authorize repair, record `INCOMPLETE_COVERAGE` rather than pretending HOLD is operationally complete.

In `src/weekly_decision_cycle.py`, consume the explicit feasibility record as `PASS / ACTION` only for a validated paired legal FREEAGENT swap, or as an explicit incomplete-coverage gap. Preserve all other K optional-upgrade thresholds, DST/player channels, waiver uncertainty, trade/IR behavior, and the weekly health gate. Screen output remains non-authoritative. No observed 2026 outcome tunes v0.X.

## Validation and authority boundaries

The separate `.ffpkg` local-apply must enforce exact Git-blob predecessors, isolate targeted regressions, validate the installed candidate and memory, use backup/rollback, run targeted and full pytest plus compileall, and stop before staging/commit/push and runtime sync. The machine-generated memory manifest is independently rebuilt from Git index blobs at staging.

Frozen October 8 evidence is immutable and not actionable on October 9. The October 9 corrected source cannot authorize ESPN submission until it is staged, published, remote verified, runtime commissioned, and followed by fresh decision-time roster/market, prospective capture, provider, memory health, and nine-channel completion evidence.

`durable_memory_updated: true`
