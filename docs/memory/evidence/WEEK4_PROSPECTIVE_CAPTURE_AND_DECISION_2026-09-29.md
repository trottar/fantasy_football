# Week 4 Prospective Capture and Decision — 2026-09-29

---
evidence_type: prospective_capture_and_decision
season: 2026
week: 4
runtime: v0.36-repack1
source_checkpoint: 69ed2d39e3f0df6c503a0a29c808e16785150318
trade_decision: HOLD
transaction_submitted: false
persistence_active: false
football_model_tuning: false
---

## Coverage Qualification — 2026-09-29

The raw Week 4 prospective evidence remains valid.

The player trade result in this record is now explicitly scoped to the automated
one-for-one QB/RB/WR/TE search. It does not establish roster-wide HOLD or weekly
decision completeness.

Later workflow audit found that the Week 4 cycle had not required current
receipts from the broad player waiver/free-agent channel, commissioned DST/K
policy, IR/injury-replacement state, all required trade families, and weekly
operational health.

Any broader prior interpretation is superseded by
`WEEKLY_DECISION_ORCHESTRATION_FAILURE_AUDIT_2026-09-29.md`.

## Purpose

Record the causally valid Week 4 week-open state, first player-channel trade
decision cycle, and targeted recovery of a package-layer uncertainty-reporting
defect without changing football/model semantics.

## Week 4 Week-Open Capture

Accepted carrier:
`week4_week_open_capture_20260929_v2.ffpkg`.

The v1 carrier failed pre-mutation because canonical JSON semantic hashes for
`model.json` and `league.json` were mistakenly used as raw file SHA-256 values.
v2 separated representation identity from canonical JSON identity.

Accepted snapshot:

`data/season_snapshots/20260930T014535Z/snapshot.json`

SHA-256:
`9c0270713a2c902b2a9e13004fe9b4b655250dfa7b88df82b86d79045e76a367`

Snapshot canonical SHA-256:
`f95aa3665043fe1b975f601a7f5954d03b9f470645ee2d6994d9c516781f33cf`

Accepted prospective capture:

`data/season_predictions/closure/pregame_2026_w04_20260930T014558Z.json`

SHA-256:
`4bc538cc935ab878b918bbadc8726e6408e2e6e79c9f69d651715a3ecd244734`

Canonical payload SHA-256:
`c262f5e0831ca035f356f19c33446365b4a03ea1f71a43bba42da0f129091aa5`

Validation:

- source health: `6/6 PASS`;
- ESPN, Sleeper, nflverse rosters/matchups, NFL official rosters and NFL official
  transaction/injury state all healthy;
- measurement contract:
  `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- capture integrity: PASS;
- pre-data firewall: PASS;
- matchup players: 32;
- league players: 174;
- specialists: 64;
- DST: 32;
- K: 32;
- behavior teams: 12;
- market players: 851;
- bounded cascade:
  `PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE`,
  depth 3, 64 N2+ scenarios;
- Week 3 capture set preserved: `4/4`;
- persistence active: false.

## Pinned Lineup and Trade Search

Accepted carrier:
`week4_pinned_lineup_trade_search_20260929_v1.ffpkg`.

Pinned decision audit:

`data/season_decisions/week4_pinned_lineup_trade_search_20260930T020844Z.json`

SHA-256:
`24807320c6e9dd0f2b87c94464efbfff24e8e4b211fad2525a607a2b49f87ca8`

Expected lineup:

- Lamar Jackson — QB;
- Ashton Jeanty — RB;
- Jeremiyah Love — RB;
- Puka Nacua — WR;
- Carnell Tate — WR;
- George Kittle — TE;
- Jakobi Meyers — FLEX;
- Harrison Butker — K;
- Lions D/ST — DST.

Lineup total:
125.78 nominal points / 120.12 availability-weighted points.

Puka Nacua was rendered correctly as QUESTIONABLE at 75% active probability.

The league-wide trade search:

- remained player-channel-only (`QB/RB/WR/TE`);
- used a cheap screen only to generate candidates;
- evaluated 12 screened candidates with 4096 predictive MC scenarios;
- returned 6 ranked results;
- returned 0 `ACTIONABLE_OFFER`;
- returned 0 `MUTUAL_MODEL_GAIN`;
- returned 6 `OUR_EDGE_PARTNER_LOSS`;
- used `UNCALIBRATED_TRADE_RESPONSE_V030` only as a separate manager-response
  layer;
- submitted no transaction.

Decision:
**HOLD / NO TRADE.**

No candidate justified giving the partner a modeled loss merely to create our
own edge.

## Reporting Defect and Recovery

The original decision package printed
`ROSTER_UNCERTAINTIES_BELOW_95PCT=0` while the lineup row correctly showed Puka
at 75%.

Targeted recovery carrier:
`week4_roster_uncertainty_recovery_20260929_v1.ffpkg`.

Corrective audit:

`data/season_decisions/week4_roster_uncertainty_recovery_20260930T021530Z.json`

SHA-256:
`953fdd0ada043f1770220ed09f02123db009439cc91afb44f004d8b7a79d3a8a`

Raw finding:

- roster `active_probability` field present: 0;
- roster `active_probability` field missing: 16.

The package helper incorrectly converted a missing field to 1.0. The production
lineup optimizer instead uses the status-prior fallback.

Recovered roster states below 95%:

1. Baker Mayfield — OUT `[SLEEPER+ESPN]` — 0%;
2. Josh Jacobs — EXEMPT `[NFL_OFFICIAL_ROSTER]` — 0%;
3. Mark Andrews — QUESTIONABLE `[SLEEPER]` — 75%;
4. Puka Nacua — QUESTIONABLE `[ESPN]` — 75%.

Classification:
`PACKAGE_RENDERER_REPRESENTATION_DEFECT_ONLY`.

The original decision audit, frozen snapshot, and frozen capture remained
byte-identical. The trade search was not rerun. No observability logs changed.

## Current Decision Boundary

- Week 4 week-open prospective capture: VALID.
- One-for-one player trade channel: HOLD.
- Weekly roster decision completion: INCOMPLETE_COVERAGE.
- Current expected lineup from this checkpoint: complete.
- Immediate starting-lineup availability risk: Puka Nacua, 75% active.
- Mark Andrews is also 75% but is not the expected TE starter.
- Baker Mayfield and Josh Jacobs are currently modeled unavailable.
- Persistence: DISABLED.
- Transaction submitted: false.
- Football/model tuning: false.

## Next Action

Before Week 4 lock, obtain a fresh decision-time status sync/capture focused on
the expected lineup and Puka Nacua.

If Puka's availability evidence materially changes, re-evaluate the lineup from
that fresh state. Do not rerun the trade search unless a material state change
could change the football decision.

After the pre-lock status gate is secured, resume Week 3 Data/MC closure.
Phase 1E.4 persistence activation remains separately gated.
