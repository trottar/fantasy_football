# 2026 Season Calendar / Development Gates

**Planning state:** 2026-10-04
**Configured fantasy regular season:** Weeks 1-13
**Configured fantasy playoffs:** Weeks 14-17
**Configured playoff Round 1:** Week 14

This file owns the active 2026 temporal plan. `docs/ROADMAP.md` owns long-range
phase intent; `roadmap/STATUS.md` owns current roadmap position; `CURRENT.md` owns
the exact active task.

## Gate Types

**Calendar gate:** irreversible deadline for a prospective capture or operational
freeze.

**Evidence gate:** review/calibration gate that passes only when prospective
evidence supports it.

A date can trigger an evidence review. It cannot force the evidence gate to pass.

## Week-by-Week Map

| Week | NFL window | Bye teams from league config | Project posture / deadline |
| --- | --- | --- | --- |
| 1 | Sep 9-14 | none | Closed. Use as prospective evidence only if a genuine frozen capture already exists. Never backfill. |
| 2 | Sep 17-21 | none | Closed. Preserve any genuine frozen W2 evidence and classify gaps explicitly. Never backfill. |
| 3 | Sep 24-28 | none | Closed calendar window. Preserve secured week-open/decision-time evidence; Week 3 closure remains deferred until a fresh complete weekly receipt proves recovery. |
| 4 | Oct 1-5 | none | **Gate B5 and the multi-K correction are commissioned.** A fresh Oct. 4 decision-time capture passed health and produced 9/9 receipt rows, but the lineup channel authorized moving locked-bench Jakobi Meyers into the starting lineup. The lock-aware lineup correction is local-applied/validated and must be published/commissioned before a fresh rerun can authorize any lineup or trade action. B2b remains deferred/fail-closed with zero future IR-capacity credit. |
| 5 | Oct 8-12 | CAR, KC | Preferred broader observability/operability target after Week 4 recovery; first bye-week operational stress. |
| 6 | Oct 15-19 | CIN, DET, MIA, MIN | First formal review of three clean prospective weeks if evidence quality supports it. Open calibration investigations only; no automatic tuning. |
| 7 | Oct 22-26 | BUF, JAX, LAC, WSH | Test availability/opportunity and waiver-response closure; shadow calibration only when justified. |
| 8 | Oct 29-Nov 2 | HOU, NO, NYG, SF | Midseason calibration decision review. Commission only evidence-supported changes; otherwise defer. |
| 9 | Nov 5-9 | PIT, TEN | Prefer any justified early calibration commissioned by this point. Shift attention toward transaction/field response. |
| 10 | Nov 12-16 | CHI, DEN, PHI, TB | Waiver/trade behavior closure and manager-kernel validation. |
| 11 | Nov 19-23 | ATL, CLE, GB, LAR, NE, SEA | Largest bye cluster. Playoff-readiness candidate should be operational by week end. |
| 12 | Nov 26-30 | none | Thanksgiving-compressed week. Start explicit playoff future utility. Avoid late high-risk development. |
| 13 | Dec 3-7 | BAL, IND, LV, NYJ | Final configured fantasy regular-season week. **Major empirical calibration freeze / playoff baseline commissioning.** |
| 14 | Dec 10-14 | ARI, DAL | **Fantasy playoff Round 1.** Production-first; explicit bye management; structural repairs only. |
| 15 | Dec 17-21 | none | Fantasy playoffs. Closure continues; no reactive broad retuning. |
| 16 | Dec 24-28 | none | Holiday scheduling. Production state should be validated by Dec 23. |
| 17 | Dec 31-Jan 4 | none | Final configured fantasy playoff week. Preserve all frozen decisions/outcomes. |
| 18 | Jan 9-10 | none | Fantasy season complete. Out-of-sample football evidence and full-season closure. |

## Standard Weekly Scientific Cycle

### Final game -> Tuesday: observation

- ingest final outcomes;
- preserve raw observations;
- finalize availability/transaction outcomes;
- link frozen predictions/actions to outcomes.

### Tuesday: Data/MC closure

Evaluate channel-separated residuals, pulls, MAE/RMSE, pull mean/width, interval
coverage, availability Brier scores, matchup outcomes,
opportunity/efficiency/scoring, market/behavior outcomes, and
lineup/transaction regret.

### Tuesday-Wednesday: diagnosis

For each meaningful anomaly:

`one narrow hypothesis -> one targeted diagnostic -> raw evidence -> classification`

No broad retuning from a recap alone.

### Wednesday: development window

Evidence-supported patches may advance. A missed development goal is preferable
to rushing an unvalidated change into the next game window.

### Before first game: week-open reference capture

Freeze state, model/release/config identity, source/data-as-of, inputs,
projections, uncertainty, roster/league state, availability, matchup context, and
provenance.

### During the week: decision-time captures

Preserve a separate prospective capture for each consequential lineup change,
waiver/add/drop, trade evaluation, DST/kicker stream, and injury replacement.

### Weekly decision completion gate

Before the weekly roster cycle may be called complete, require the current receipt
matrix in `architecture/WEEKLY_DECISION_COMPLETION.md` and record it using
`templates/WEEKLY_DECISION_RECEIPT.md` or an equivalent canonical evidence record.

Required domains include lineup/availability, broad player waiver/free-agent
search, DST, kicker, IR/injury-replacement state, required trade families,
prospective provenance, and weekly operational health.

Missing/unsupported coverage is `INCOMPLETE_COVERAGE`. Missing/stale required
health is `BLOCKED_HEALTH`. Stale material decision information is
`CAPTURE_REQUIRED`. None may be translated to HOLD.

The search scope is system-defined across the full relevant roster/market, not
restricted to examples named by the user.

## Trade-Search Operational Requirement

Gate B3 is commissioned for player-only 1x1/1x2/2x1/2x2 packages through a
family-balanced cheap screen into paired predictive `evaluate_trade`.

Specialist-inclusive trade composition is separately commissioned for bounded
1x1/1x2/2x1/2x2 packages containing DST and/or K. Player, DST, and K response
remain channel-separated and compose only at the complete-roster state boundary.
Mixed-package drop/fill normalization is explicit; guaranteed FREEAGENT fills do
not imply waiver success. Post-trade K states with more than one owned kicker are
unsupported while general K `CARRY2` is disabled; specialist-trade authority must
fail closed rather than assign uncommissioned multi-K portfolio option value.

## Calibration Evidence Ladder

- one surprising game -> investigation candidate only;
- repeated player discrepancy -> diagnose role/input/structure before population tuning;
- repeated channel/population discrepancy -> calibration candidate;
- multiple prospective weeks plus validation improvement -> may authorize v1.X calibration;
- Weeks 14-17 -> major empirical calibration frozen by default.

## Irreversible Rule

Code and memory maintenance can be completed later. A missed prospective
information state cannot be recreated later without hindsight.
