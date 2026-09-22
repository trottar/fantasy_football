# Fantasy Football Project Roadmap — 2026 Season-Gated Development

**Accepted planning baseline:** 2026-09-21
**Commissioned football baseline:** `v0.36-repack1`
**Current engineering series:** v1.0A observability

This roadmap owns long-range phase intent and phase acceptance gates. It does not
own the exact active task; `docs/memory/CURRENT.md` does. The active weekly
calendar is `docs/memory/roadmap/SEASON_2026.md`.

## 1. Governing model

Fantasy football is treated as a stochastic response problem:

`N_fantasy ~ L x sigma x A x epsilon`

with weekly state:

`S_w = (P_w, D_w, K_w, M_w, I_w)`

and specialist-channel separation:

`P ⊕ D ⊕ K`

Development remains:

`MC -> Data -> closure -> diagnosis -> calibration`

and:

`observe -> measure -> diagnose -> calibrate -> expand`

## 2. Two clocks

**Calendar gates** protect prospective information or operational opportunities
that disappear once games/outcomes occur. A missed prospective capture is
recorded as missing and is never reconstructed later as if it were frozen in
advance.

**Evidence gates** authorize diagnosis/calibration only when accumulated
prospective evidence supports them. A review date does not force a gate to pass;
`DEFER / COLLECT MORE DATA` is a valid result.

## 3. Concurrent lanes

### Production lane

Keep the commissioned model stable and usable for real decisions.

### Measurement lane

Freeze usable prospective state, predictions, actions, outcomes, closure, and
provenance. Measurement deadlines outrank nonessential feature work.

### Development lane

Advance diagnostics, model changes, behavior kernels, and calibration only from
classified evidence. Development may slip rather than contaminate a prospective
window.

---

# Phase 0 — A-priori physics/model baseline

**Status: COMPLETE / COMMISSIONED**

Purpose: establish the pre-outcome 2026 architecture.

Accepted scope includes the player predictive channel, DST/kicker specialist
channels, availability/matchup interactions, uncertainty-aware Monte Carlo,
roster-state perturbations, waiver/trade response, manager-behavior separation,
data-source/GUI foundations, prospective closure machinery, and `P ⊕ D ⊕ K`.

Final authority: `v0.36-repack1`.

Observed 2026 outcomes may not retroactively tune a `0.X` model and then be
described as a-priori.

---

# Phase M — Repository / durable-memory authority transition

**Status: COMPLETE / PUSHED / REMOTE VERIFIED**

The season roadmap, calendar, known-issue register, v1.X context, causal capture
rules, memory/handoff policy, and human-in-the-loop checkpoint boundary were
established and published before Phase 1A commissioning.

The later M0-M7 memory-system refinement is maintenance of that continuity layer;
it does not roll Phase M back to an active gate and does not invalidate completed
football/observability work.

---

# Phase 1 — v1.0 measurement apparatus / observability commissioning

**Primary window:** Weeks 3-5
**Preferred operational target:** before Week 5 begins

Purpose: make production operation scientifically observable without changing
football/model semantics.

## 1A — Data-source season-sync shadow pilot

**Status: COMPLETE / RUNTIME COMMISSIONED**

The outer season-sync boundary is commissioned with behavior/exception
non-interference, privacy/redaction, bounded overhead, fail-open observation, and
no authenticated payload/credential capture. Persistent evidence remains disabled.

## 1B — Closure instrumentation

**Status: PREFLIGHT VALIDATED / RETAINED CANDIDATE / NOT YET CHECKPOINTED**

Add immutable provenance around release/commit/config/input identity, NFL week,
prediction time, `data_as_of`, channel, RNG/CRN identity where applicable,
recommendation/action identity, and later outcome linkage.

The retained candidate remains frozen during M0-M7 memory refinement unless new
evidence invalidates its established gates.

## 1C — Player / DST / kicker observability

**Status: NOT STARTED / SEPARATELY GATED**

Instrument each specialist channel separately. Do not create a generic
cross-channel ranking authority.

## 1D — Market / manager-behavior observability

**Status: NOT STARTED / SEPARATELY GATED**

Observe waiver/trade/ownership/field response without feeding perception into
intrinsic football value.

## 1E — Persistent evidence authorization

**Status: NOT STARTED / SEPARATELY GATED**

Persistence requires a separate privacy/non-interference gate. Raw
authenticated/private evidence remains local; sanitized durable conclusions may
enter Git.

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

Track at minimum residuals `r_i = D_i - M_i`, pulls
`z_i = (D_i - M_i) / sigma_i`, MAE, RMSE, pull mean/width, interval coverage,
availability Brier score, matchup outcomes, opportunity/efficiency/scoring,
transaction/lineup regret, and manager-behavior outcomes.

Weeks 1-2 count only where genuine frozen captures already exist. Never
reconstruct them after the fact.

Exit gate: enough clean prospective weekly cycles to open serious calibration
investigations. Three weeks may justify investigation; they do not automatically
justify broad tuning.

---

# Phase 3 — Early-season diagnosis / evidence-supported calibration

**Primary window:** Weeks 6-8
**Review target:** before Week 9

For each systematic discrepancy ask whether the information was available,
whether the input was correct, whether the architecture could represent the
process, whether expectation/uncertainty is biased, and whether the observation
is consistent with fluctuation.

Candidate areas include availability, workload/opportunity, efficiency
dispersion, matchup acceptance, variance/correlation, player temporal
transitions, DST component distributions, and kicker opportunity/yield.

No player-specific overreaction to one game. Commission v1.X calibration only
with repeated prospective evidence plus validation that improves the relevant
closure without breaking uncertainty or subsystem boundaries. Otherwise defer.

---

# Phase 4 — Midseason decision / market-response model

**Primary window:** Weeks 9-11
**Target:** mature before Week 12

Focus on ordered contingent waiver claims, actual league resolution mechanics,
competing-manager behavior, dropped-player field response, ownership/market
behavior, supported trade packages, utility change to both teams, and league
state response.

Keep `football utility != manager behavior`.

Acceptance: behavioral probabilities and transaction mechanics are closure-tested
or explicitly classified as insufficient evidence.

---

# Phase 5 — Playoff readiness / production freeze

**Primary window:** Weeks 12-13
**Hard operational gate:** before Week 14

Use actual playoff qualification/bracket state when known, Week 14-17 future
utility, byes/replacement availability, bench/injury contingency value,
specialist schedules, and win-now versus future-round value.

By the end of Week 13, major empirical calibration freezes by default.

Acceptance: a commissioned playoff production baseline exists before Week 14.

---

# Phase 6 — Fantasy playoff operations

**Window:** Weeks 14-17
**Mode:** production-first / development-restricted

Week 14 is configured as playoff Round 1 and contains Arizona/Dallas byes.

Use only decision-time information, preserve consequential action captures,
continue closure after outcomes, avoid reactive broad retuning, and reserve
structural correctness fixes for separate review. Playoff observations normally
enter postseason calibration rather than immediate production tuning.

Acceptance: complete frozen playoff decisions/outcomes with no hindsight
contamination.

---

# Phase 7 — NFL Week 18 / complete 2026 closure

Week 18 is additional out-of-sample football-process evidence rather than a
configured fantasy-playoff week.

Build full-season closure by player, position, DST, kicker, availability,
matchup, uncertainty, waivers, trades, field response, and regular-season versus
playoff segments.

Question:

> What did the frozen model predict, what occurred, why did the discrepancy
> arise, and what evidence-supported change should the next prior inherit?

Do not optimize retrospectively to make 2026 look better.

---

# Phase 8 — Postseason / v2 research architecture

**Primary window:** January-March 2027

Use the complete prospective 2026 dataset to evaluate alternate priors,
uncertainty redesign, correlation structure, opportunity-process refinements,
specialist-channel recalibration, manager-behavior kernels, roster utility,
field response, runtime/performance simplification, and unnecessary complexity.

Prefer simpler models when evidence is equivalent. Negative results are
architecture evidence.

---

# Phase 9 — 2027 offseason prior construction

**Primary window:** March-June 2027

Incorporate free agency, retirements, coaching/team changes, the NFL Draft,
schedule/byes, and role competition. Separate inherited 2026 evidence from new
2027 state and uncertainty.

---

# Phase 10 — 2027 preseason / draft system

**Primary window:** July-August 2027

Refresh player universe, rookie priors, depth-chart uncertainty, preseason
availability, roster cuts, draft state, replacement pools, positional scarcity,
and full draft/GUI regression.

Exit gate: `2027 A-PRIORI BASELINE COMMISSIONED`.

---

# Season success criteria

The 2026 project is successful when consequential decisions respect causal
information boundaries, predictions/captures are frozen before outcomes,
uncertainty is recorded, `P ⊕ D ⊕ K` is preserved, manager behavior stays
separate from football physics, weekly Data/MC closure is retained, failures are
diagnosable, calibration is evidence-supported, negative results are durable,
and the season yields a reproducible dataset that improves the next model.

A fantasy championship is a desirable stochastic outcome, not the sole
scientific acceptance criterion.
