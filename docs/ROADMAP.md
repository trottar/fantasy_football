# Fantasy Football Project Roadmap — 2026 Season-Gated Development

**Accepted planning baseline:** 2026-09-20
**Commissioned football baseline:** `v0.36-repack1`
**Current engineering series:** v1.0A observability

This roadmap owns long-range phase intent and phase acceptance gates. It does
not own the current active task; `docs/memory/CURRENT.md` does. The active 2026
week-by-week calendar is maintained in
`docs/memory/roadmap/SEASON_2026.md`.

## 1. Governing model

Fantasy football is treated as a stochastic response problem:

`N_fantasy ~ L x sigma x A x epsilon`

with weekly state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

and specialist-channel separation:

`P ⊕ D ⊕ K`

The development sequence remains:

`MC -> Data -> closure -> diagnosis -> calibration`

and:

`observe -> measure -> diagnose -> calibrate -> expand`

## 2. Two clocks

### Calendar gates

Calendar gates protect information or operational opportunities that disappear
once games/outcomes occur.

Examples:

- week-open reference capture;
- decision-time lineup/waiver/trade state;
- playoff production freeze;
- pregame source/config/model provenance.

A missed prospective capture is recorded as missing. It is never reconstructed
after relevant outcomes and relabeled prospective.

### Evidence gates

Evidence gates decide whether prospective measurements support diagnosis,
calibration, or architectural change.

A planned date is a review point, not automatic authorization. If evidence is
insufficient, `DEFER / COLLECT MORE DATA` is the correct result.

## 3. Concurrent lanes

Throughout the season the project maintains three lanes.

### Production lane

The commissioned model remains usable and stable for real fantasy decisions.

### Measurement lane

Every usable week captures prospective state, predictions, decisions, outcomes,
closure, and provenance.

Measurement deadlines are normally harder than feature-development deadlines.

### Development lane

Diagnostics, model changes, behavior kernels, and calibration advance only from
classified evidence and may slip rather than contaminate prospective evidence.

---

# Phase 0 — A-priori physics/model baseline

**Status: COMPLETE / COMMISSIONED**

Purpose: establish the pre-outcome 2026 architecture.

Accepted scope includes:

- player predictive channel;
- DST specialist channel;
- kicker specialist channel;
- availability and matchup interactions;
- uncertainty-aware Monte Carlo;
- roster-state perturbations;
- waiver/trade response machinery;
- manager-behavior separation;
- data-source and GUI foundations;
- prospective closure machinery;
- `P ⊕ D ⊕ K`.

Final authority: `v0.36-repack1`.

Observed 2026 outcomes may not retroactively tune a `0.X` model and then be
described as a-priori.

Acceptance: already commissioned.

---

# Phase M — Repository / durable-memory authority checkpoint

**Status: ACTIVE TRANSITION**

Purpose: synchronize the accepted roadmap and memory contract before further
technical implementation.

Required:

- long-range roadmap;
- season calendar;
- known/deferred issue register;
- v1.X phase context;
- D-023 season-gate decision;
- weekly closure template;
- source-before-summary rule;
- memory/handoff reconciliation;
- schema-2 manifest regenerated later from staged Git blobs;
- human-in-the-loop commit/push/remote verification.

This phase changes documentation/continuity only.

Exit gate:

`PUSHED / REMOTE VERIFIED`

No technical season-sync work begins before this gate.

---

# Phase 1 — v1.0 measurement apparatus / observability commissioning

**Primary window:** Weeks 3-5
**Preferred operational target:** before Week 5 begins

Purpose: make production operation scientifically observable without changing
football/model semantics.

## 1A — Data-source season-sync shadow pilot

Instrument the predeclared season-sync boundary with:

- behavior equivalence;
- exception-type equivalence;
- privacy/redaction;
- no authenticated payload capture;
- no credential capture;
- bounded overhead;
- fail-open observer behavior;
- no football/model changes.

## 1B — Closure instrumentation

Add immutable provenance around:

- release/commit/config/input identity;
- NFL week;
- prediction time;
- `data_as_of`;
- channel;
- RNG/CRN identity where applicable;
- recommendation/action identity;
- later outcome linkage.

## 1C — Player / DST / kicker observability

Instrument each specialist channel separately.

Do not create a generic cross-channel ranking authority.

## 1D — Market / manager-behavior observability

Observe waiver/trade/ownership/field response without feeding perception into
intrinsic football value.

## 1E — Persistent evidence authorization

Persistence requires a separate privacy/non-interference gate.

Raw authenticated/private evidence remains local. Sanitized durable conclusions
may enter Git.

### Phase 1 acceptance

- data-source instrumentation commissioned;
- closure instrumentation commissioned;
- P/D/K instrumentation commissioned;
- market/behavior instrumentation commissioned;
- persistent local evidence explicitly authorized;
- non-interference and privacy proven;
- production football semantics unchanged.

---

# Phase 2 — Prospective Data/MC closure baseline

**Collection:** continuous
**Primary clean review window:** Weeks 3-5

Purpose: establish genuine prospective closure.

Track at minimum:

- residual `r_i = D_i - M_i`;
- pull `z_i = (D_i - M_i) / sigma_i`;
- MAE;
- RMSE;
- pull mean/width;
- interval coverage;
- availability Brier score;
- matchup outcomes;
- opportunity/efficiency/scoring decomposition;
- transaction and lineup regret;
- manager-behavior outcomes.

Weeks 1-2 may enter prospective closure only where genuine frozen captures
already exist. Never reconstruct them after the fact.

Exit gate: enough clean prospective weekly cycles to open serious calibration
investigations. Three weeks may justify investigation; they do not automatically
justify broad tuning.

---

# Phase 3 — Early-season diagnosis / evidence-supported calibration

**Primary window:** Weeks 6-8
**Review target:** before Week 9

For each systematic discrepancy ask:

1. Was the relevant information available?
2. Was the input correct?
3. Could the architecture represent the process?
4. Is the expected value biased?
5. Is uncertainty miscalibrated?
6. Is the observation consistent with fluctuation?

Candidate calibration areas include:

- availability;
- workload/opportunity;
- efficiency dispersion;
- matchup acceptance;
- variance/correlation;
- player temporal transitions;
- DST component distributions;
- kicker opportunity/yield.

No player-specific overreaction to one game.

A v1.X calibration may be commissioned only with repeated prospective evidence
and a validation showing the correction improves the relevant closure without
breaking uncertainty or subsystem boundaries.

If not supported: defer.

---

# Phase 4 — Midseason decision / market-response model

**Primary window:** Weeks 9-11
**Target:** mature before Week 12

Focus:

- ordered contingent waiver claims;
- actual league resolution mechanics;
- competing-manager behavior;
- dropped-player field response;
- ownership/market behavior;
- supported trade-package structures;
- utility change to both teams;
- league-state response.

Keep:

football utility != manager behavior.

Acceptance: behavioral probabilities/transaction mechanics are closure-tested or
explicitly classified as insufficient evidence.

---

# Phase 5 — Playoff readiness / production freeze

**Primary window:** Weeks 12-13
**Hard operational gate:** before Week 14

Purpose: switch from generic regular-season utility toward conditional playoff
utility.

Required:

- actual playoff qualification/bracket state when known;
- Week 14-17 future utility;
- byes and replacement-level availability;
- bench/injury contingency value;
- specialist schedules;
- win-now versus future-round value.

By the end of Week 13, major empirical calibration freezes by default.

Acceptance: a commissioned playoff production baseline exists before Week 14.

---

# Phase 6 — Fantasy playoff operations

**Window:** Weeks 14-17
**Mode:** production-first / development-restricted

Week 14 is configured as playoff Round 1 and contains Arizona/Dallas byes.

Rules:

- use only decision-time information;
- preserve all consequential action captures;
- continue closure after outcomes;
- no reactive broad retuning;
- structural correctness fixes remain separately reviewable;
- playoff observations normally enter postseason calibration rather than
  immediate production tuning.

Acceptance: complete frozen playoff decisions/outcomes with no hindsight
contamination.

---

# Phase 7 — NFL Week 18 / complete 2026 closure

**Window:** after fantasy competition ends

Week 18 is additional out-of-sample football-process evidence rather than a
configured fantasy-playoff week.

Build full-season closure by:

- player;
- position;
- DST;
- kicker;
- availability;
- matchup;
- uncertainty;
- waivers;
- trades;
- field response;
- regular-season versus playoff segments.

Question:

> What did the frozen model predict, what occurred, why did the discrepancy
> arise, and what evidence-supported change should the next prior inherit?

Do not optimize retrospectively to make 2026 look better.

---

# Phase 8 — Postseason / v2 research architecture

**Primary window:** January-March 2027

Use the complete prospective 2026 dataset to evaluate:

- alternate priors;
- uncertainty redesign;
- correlation structure;
- opportunity-process refinements;
- specialist-channel recalibration;
- manager-behavior kernels;
- roster utility;
- field response;
- runtime/performance simplification;
- unnecessary complexity.

Prefer simpler models when evidence is equivalent.

Negative results are architecture evidence.

---

# Phase 9 — 2027 offseason prior construction

**Primary window:** March-June 2027

Incorporate new state:

- free agency;
- retirements;
- coaching changes;
- team changes;
- NFL Draft;
- schedule/byes;
- role competition.

Separate inherited 2026 evidence from new 2027 state and uncertainty.

---

# Phase 10 — 2027 preseason / draft system

**Primary window:** July-August 2027

Refresh:

- player universe;
- rookie priors;
- depth-chart uncertainty;
- preseason availability;
- roster cuts;
- draft state;
- replacement pools;
- positional scarcity;
- full draft/GUI regression.

Exit gate:

`2027 A-PRIORI BASELINE COMMISSIONED`

The prospective cycle then repeats.

---

# Season success criteria

The 2026 project is successful when:

1. consequential decisions respect causal information boundaries;
2. predictions/captures are frozen before outcomes;
3. uncertainty is recorded;
4. `P ⊕ D ⊕ K` is preserved;
5. manager behavior stays separate from football physics;
6. weekly Data/MC closure is retained;
7. failures are diagnosable;
8. calibration is evidence-supported;
9. negative results are durable;
10. the season yields a reproducible dataset that improves the next model.

A fantasy championship is a desirable stochastic outcome, not the sole
scientific acceptance criterion.
