# Current Project State

---
state_updated: 2026-09-29
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week4_prospective_operations
active_workstream: week4_prelock_availability
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Protect Week 4 prospective causality and make only decision-time-authorized roster moves.
The Week 4 week-open capture and first trade-search cycle are complete; the immediate calendar gate is a fresh pre-lock availability check for the current expected lineup, especially Puka Nacua.

## Current Work Item

**Week 4 prospective state: CAPTURED / TRADE SEARCH EVALUATED / HOLD.**

The accepted Week 4 snapshot is:

`data/season_snapshots/20260930T014535Z/snapshot.json`

SHA-256:
`9c0270713a2c902b2a9e13004fe9b4b655250dfa7b88df82b86d79045e76a367`

The accepted enriched prospective capture is:

`data/season_predictions/closure/pregame_2026_w04_20260930T014558Z.json`

SHA-256:
`4bc538cc935ab878b918bbadc8726e6408e2e6e79c9f69d651715a3ecd244734`

Canonical payload SHA-256:
`c262f5e0831ca035f356f19c33446365b4a03ea1f71a43bba42da0f129091aa5`

Capture status:

- live source health: `6/6 PASS`;
- measurement contract: `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- capture integrity: PASS;
- pre-data firewall: PASS;
- matchup players: 32;
- all-league players: 174;
- specialists: 64 (`DST=32`, `K=32`);
- behavior teams: 12;
- market players: 851;
- bounded cascade: depth 3 / 64 N2+ scenarios;
- Week 3 captures preserved: `4/4`;
- persistence remained disabled.


## Verified State

- Week 4 week-open snapshot/capture: **VALID / FROZEN**.
- Week 4 first player-channel trade cycle: **EVALUATED / HOLD / NO TRADE**.
- Trade search authority: predictive MC; screen remained candidate generation only.
- Availability recovery classification:
  `PACKAGE_RENDERER_REPRESENTATION_DEFECT_ONLY`.
- Current recovered sub-95% roster states: Baker Mayfield 0%, Josh Jacobs 0%, Mark Andrews 75%, Puka Nacua 75%.
- Puka Nacua is the only recovered sub-95% player in the current expected starting lineup.
- Runtime remains `v0.36-repack1`; persistence remains **DISABLED**.
- No transaction, football/model tuning, production-source write, persistence activation, commit, or push occurred.

## Week 4 Decision Result

Pinned decision audit:

`data/season_decisions/week4_pinned_lineup_trade_search_20260930T020844Z.json`

SHA-256:
`24807320c6e9dd0f2b87c94464efbfff24e8e4b211fad2525a607a2b49f87ca8`

Expected lineup was complete at 125.78 nominal / 120.12 availability-weighted points.

The league-wide one-for-one player-channel trade search used 4096 predictive MC scenarios per screened candidate and returned:

- actionable offers: 0;
- mutual-model-gain offers: 0;
- top six results: all `OUR_EDGE_PARTNER_LOSS`;
- transaction submitted: false.

**Decision: HOLD / NO TRADE.**

The cheap screen remains candidate generation only; predictive MC remains football authority.
`UNCALIBRATED_TRADE_RESPONSE_V030` remains a separate manager-behavior layer and does not alter football value.

## Availability Recovery

The original decision carrier had a reporting-only defect: its helper treated a
missing roster `active_probability` field as 1.0, while the lineup optimizer
correctly falls back to the status-derived prior. The original trade and lineup
calculations remain valid.

Corrective audit:

`data/season_decisions/week4_roster_uncertainty_recovery_20260930T021530Z.json`

SHA-256:
`953fdd0ada043f1770220ed09f02123db009439cc91afb44f004d8b7a79d3a8a`

Recovered roster states below 95% active probability:

- Baker Mayfield — OUT — 0%;
- Josh Jacobs — EXEMPT — 0%;
- Mark Andrews — QUESTIONABLE — 75%;
- Puka Nacua — QUESTIONABLE — 75%.

Puka is the only recovered sub-95% player in the current expected starting lineup.
Mark Andrews is not in that lineup because George Kittle is the expected TE starter.

Classification:
`PACKAGE_RENDERER_REPRESENTATION_DEFECT_ONLY`.

No trade search rerun, transaction, football tuning, production-source write,
repository write, persistence activation, or observability-log mutation occurred
during recovery.

## Observability / Engineering State

- Runtime: `v0.36-repack1`, internal `VERSION = 0.36`.
- Persistence controller source: published.
- Persistence controller runtime: commissioned.
- Persistence: **DISABLED**.
- Phase 1E.4 activation: **SEPARATELY GATED / NOT AUTHORIZED**.
- No automatic retention deletion is enabled.
- No football/model/manager-behavior formula changed.

## Calendar / Evidence Gates

- Week 4 week-open capture is causally valid and immutable evidence.
- Any consequential new lineup/waiver/trade/specialist action requires fresh
  decision-time information.
- A material pre-lock status change preempts Week 3 closure or persistence work.
- Do not rerun the trade search merely because time passed; rerun only after a
  material state change that could alter the decision.
- Missing earlier telemetry remains missing and is not backfilled.
- No observed 2026 outcome may tune v0.X.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Football utility, market perception, and manager behavior remain separate.
- `screen != authority`.
- Common-random-number paired response remains preferred where practical.
- Diagnostics/reporting defects do not authorize football retuning.
- Raw authenticated/private evidence remains local and outside Git.

## Exact Next Action

Before the first Week 4 game, perform a **fresh decision-time status sync/capture**
focused on the expected lineup and Puka Nacua's availability evidence.

If Puka's status/evidence materially changes, re-evaluate the lineup from that
fresh state before lock. Do not automatically rerun the trade search.

After the Week 4 pre-lock status gate is secured, resume the deferred Week 3
Data/MC closure. Phase 1E.4 persistence activation remains behind separate
explicit authorization.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `evidence/WEEK4_PROSPECTIVE_CAPTURE_AND_DECISION_2026-09-29.md`
- `evidence/PHASE1E_PERSISTENCE_CONTROLLER_RUNTIME_COMMISSIONING_2026-09-29.md`
