# 2026 Season Calendar / Development Gates

**Planning state:** 2026-10-05
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
| 3 | Sep 24-28 | none | Closed calendar window. Preserve secured week-open/decision-time evidence. **Week 3 closure recovery gate is satisfied** by the Oct. 5 fresh complete Week 4 receipt; resume closure after the current Week 4 action gate is handled. |
| 4 | Oct 1-5 | none | **Fresh corrected weekly authority secured.** The 15:22:25 UTC fresh corrected snapshot and immediate prospective capture passed integrity/firewall, operational health, all 9 channels, and lineup legality. Sole action: Kamara -> Bills D/ST, 4096-scenario specialist trade; 48-hour review makes ownership Week 5 effective with zero Week 4 effect. Execute only while material state remains unchanged; otherwise refresh first. B2b remains deferred/fail-closed with zero future IR-capacity credit. |
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

### Post-outcome counterfactual replay

After raw outcomes are frozen and ordinary prospective closure is evaluated:

- replay the just-completed week under
  `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`;
- classify each run as `CAUSAL_FROZEN_REPLAY` or
  `RECONSTRUCTED_RETROSPECTIVE_REPLAY`;
- freeze replay predictions and the model-preferred action before outcome
  attachment;
- compare historical actual, model-preferred replay, and oracle-best feasible
  counterfactual states;
- record regret, matchup-flip opportunities, predictive residuals, and structural
  classifications;
- add confirmed structural defects to the cumulative replay regression suite;
- rerun affected prior structural scenarios after decision-machinery changes;
- never tune v0.X to improve historical 2026 outcomes.

This is a standard weekly procedure after every completed week. Weeks 1-3 may
bootstrap the laboratory only under the replay-mode provenance rules above.

Bootstrap classification established on 2026-10-05:

- Weeks 1-2 have no frozen decision-state artifacts in the audited local evidence
  and therefore support only `RECONSTRUCTED_RETROSPECTIVE_REPLAY`.
- Week 3 is `RECONSTRUCTED_RETROSPECTIVE_REPLAY` overall. Frozen sub-surfaces
  cover all 174 rostered player predictions, all 24 owned specialist predictions,
  and the exact 40-player historical actionable specialist frontier. The broad
  player waiver/free-agent values layer is reconstructed because its historical
  decision-time identity is unproven.
- The first Phase-A replay tooling slice is source-validated. It freezes
  provenance, candidate rankings/model action, and a hash-addressed receipt before
  any Phase-B outcome attachment. It does not itself authorize a football action
  or empirical v0.X tuning.

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
