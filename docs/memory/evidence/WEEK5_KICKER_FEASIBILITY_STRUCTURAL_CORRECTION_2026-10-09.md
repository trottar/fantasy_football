# Week 5 Kicker Mandatory-Feasibility Structural Correction — 2026-10-09

---
evidence_type: structural_authority_correction
status: SOURCE_PUBLISHED_RUNTIME_COMMISSIONED
source_checkpoint_predecessor: cb09994f3551153f93f1ef5a94ef003dbef1d6cb
runtime_baseline: v0.36-repack1
production_tuning: false
transaction_execution: USER_REPORTED_NOT_PROVIDER_VERIFIED
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

## October 9 publication, commissioning, and operational follow-through

The previously authorized structural candidate was published and remote-verified at Git commit `7ed9e65fab628b6446e9a03d26d13bf0362837ca`. Its separately commissioned `v0.36-repack1` runtime was verified by package `week5_kicker_feasibility_runtime_commission_20261009_v1`: published source identity PASS, targeted `9 passed`, full runtime `362 passed`, and compileall PASS. This corrects the earlier `LOCAL_APPLY_CANDIDATE` status without representing the original receipt as final current ESPN transaction authority.

October 9 provider sync gave Week 5 snapshot `data/season_snapshots/20261009T055123Z/snapshot.json`; the associated 05:54 UTC immutable pregame capture passed integrity (`174` all-league player predictions and `64` specialist predictions; `0` interaction component predictions). A read-only operational evidence preflight verified three exact production blobs, three dependency SHA-256s, capture/snapshot binding, and strict memory health. The resulting nine-channel `weekly_decision_receipt_20261009T070431Z.json` had operational health PASS; the lineup was incomplete only at mandatory K, while the kicker and specialist-inclusive trade channels returned `PASS / ACTION`; overall state remained `INCOMPLETE_COVERAGE`.

The action audit of that receipt identified Butker -> Bass as a guaranteed-FREEAGENT kicker swap: `17/17` eligible candidates completed paired complete-state MC, Bass's current-week expected K points `6.98037`, mean paired complete-state utility delta `+0.00769`, P(better) `0.18799`, P(tie) `0.69434`, and P(worse) `0.11768`. The optional-upgrade classifier was `NO_RESOLVED_EDGE`; mandatory feasibility remained independently actionable. Five specialist-inclusive trade offers were only modeled, not executed.

A refreshed October 9 15:41 UTC provider snapshot `data/season_snapshots/20261009T154132Z/snapshot.json` passed all source checks. Read-only current-state audit found Butker still owned and legally droppable, Bass a guaranteed eligible free agent with October 13 00:15 UTC kickoff, both sides unlocked at the snapshot/execution audit, K-for-K roster legality PASS, and post-swap lineup missing slots NONE. Other roster and broad market state had changed, invalidating reuse of previous full MC authority. A second immutable pregame capture at `data/season_predictions/closure/pregame_2026_w05_20261009T160258Z.json` passed integrity, with `174` all-league player and `64` DST/K predictions and zero interaction component predictions. Nothing here retroactively makes the October 9 captures prospective for previously observed games.

The user subsequently confirmed on October 9: **"Kickers swapped"** (Harrison Butker out, Tyler Bass in). This establishes **USER-REPORTED TRANSACTION**, not an independently verified ESPN post-transaction roster/starting-lineup receipt. No additional trade execution was reported. The exact previous complete-roster decision state remains incomplete at the frozen pre-transaction boundary; post-transaction and future-week decisions require fresh provider/lineup/health evidence.

As of the October 15 handoff, there is no evidence in this checkpoint of a timely Week 6 frozen capture, current Week 6 complete decision, or Week 5 observed-score closure. Those must be checked in the user's local runtime. Preserve immutable Week 5 artifacts, prevent missed calendar capture backfilling, and keep `component_predictions=0` as an unresolved measurement-coverage limitation.

`durable_memory_updated: true`
