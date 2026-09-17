# Data-source contract — v0.35-fixed1

## v0.35-fixed1

No new external source and no calibration. The correction changes only decision authority inside the pre-data temporal player-state policy: deterministic expected-lineup response is a screen, while paired predictive H2H CRN from the commissioned player MC confirms any future self-player FREEAGENT transaction. Current WAIVERS remain excluded from guaranteed acquisition and the external player market remains first-order/frozen for v0.36. No 2026 game outcome is used for tuning.

## v0.35 — causal temporal player state

## v0.35 — causal temporal player state

No new external source and no paid API. v0.35 uses only the already-snapshotted player/market coordinates available to v0.34. Our future QB/RB/WR/TE membership is propagated with expected pregame player response and the current guaranteed FREEAGENT pool; current WAIVERS are excluded from guaranteed future acquisition and other managers' future player claims are not fabricated. The resulting external-player-market approximation is explicitly labeled `FROZEN_CURRENT_GUARANTEED_FREEAGENT_POOL_NO_EXTERNAL_CLAIMS_V035` and is scheduled for replacement by the wider league-state treatment in v0.36. Realized fantasy scores never select a future transaction. The v0.34 a-priori prospective measurement contract remains active and now also freezes the v0.35 temporal player-state prediction. No 2026 game outcome is used to tune the model.


## v0.34 — a priori prospective measurement

No new external source and no paid API. v0.34 serializes already-snapshotted ESPN, NFL.com, Sleeper and nflverse coordinates together with the already-commissioned player/DST/K forward-model state. No 2026 game outcome is consumed by v0.34, no model parameter is refit, and no behavior prior is calibrated. D/ST component expectations are recorded from the commissioned v0.23 component MC. The current kicker channel has no FG-attempt/distance/XP component generator; v0.34 records that limitation rather than fabricating component predictions. Behavioral covariates and their explicitly uncalibrated coefficients are frozen separately from football value. Record now. Calibrate in 1.X.


## v0.33-fixed2

No new external source and no paid API. The temporal specialist state reuses the already-snapshotted ESPN ownership/status and waiver-rank coordinates, the existing specialist matchup response, and the commissioned player predictive random streams. Future week-boundary active/inactive revelation is explicitly uncalibrated and is used only as a decision-time information proxy; realized fantasy scores and workload outcomes are not exposed to the future transaction selector. Ordinary-player roster membership is held at the latest synchronized state until a modeled specialist-slot release rather than fabricating future player-market transactions.


## v0.32-fixed5

No external data-source or model-source changes. Release-bootstrap/materialization fix only.


## v0.32-fixed4

No external data-source changes. Future second-DST activation uses the same dynamic FREEAGENT market; the fixed6 released-player claimant response is explicitly labeled as a frozen-current behavioral proxy when projected into a future activation week.


## v0.32-fixed3

No data-source or model-source changes. This release only repairs inherited release-metadata regression compatibility.


## v0.32-fixed2

No data-source or model-source changes. This release only repairs inherited release-metadata regression compatibility.


## v0.32-fixed1

No data-source or model-source changes. This release only repairs inherited CLI/version regression compatibility.


## v0.32 dynamic specialist state-transition source rule

v0.32 adds no external source and no paid API.  The new transition state uses already-snapshotted ESPN specialist ownership/status, `FREEAGENT`/`WAIVERS` state, current waiver rank, NFL roster eligibility, and the existing nflverse schedule/matchup coordinates consumed by the v0.31 defense/kicker response functions.

Current ESPN waiver priority is used only as an explicitly **uncalibrated future transaction-order proxy**.  It is not interpreted as a measured specialist acquisition probability and does not alter the football response model.  Current WAIVERS specialists are excluded from the guaranteed initial free-agent pool.  Released specialists enter the modeled pool in the following week.

Complete-state carry2 confirmation additionally reuses the existing fixed6 released-player counterfactual response; no generic cross-position value source is introduced.


## v0.31-fixed3 output-only correction

No data source, source authority, model coordinate, or calibration prior changes in fixed3. The patch only makes specialist CLI text safe when native Python stdout is redirected through Windows PowerShell `Tee-Object` under a cp1252 encoder.


## v0.31-fixed2 specialist source correction

No new external source is introduced. Specialist NFL-team keys are normalized with the already-existing nflverse alias map before accessing the snapshotted `team_week` schedule/implied-points coordinate. This changes identifier reconciliation, not source authority or the kicker response prior.

Two-DST carry output is explicitly diagnostic in fixed2. The existing static one-DST baseline remains a schedule-complementarity screen, but it is not relabeled as a dynamic streaming policy and cannot by itself authorize a second-DST transaction.


## v0.31 channel-separation source rule

v0.31 adds **no new external source and no paid API**. It changes which model channel is allowed to consume the already-snapshotted inputs.

- **Player channel (QB/RB/WR/TE):** source authority and commissioned predictive stack are unchanged from fixed6. ESPN remains the fantasy-state/projection anchor, NFL.com the official status source, Sleeper the metadata/trend source, and nflverse the historical football-stat/matchup source.
- **Defense channel (DST):** same-channel weekly response uses the existing nflverse matchup context and v0.23 D/ST component expectation/simulation (sacks, turnovers, defensive TDs, points allowed, yards allowed) plus exact league scoring. No generic defense ranking or cross-position trade-value source is introduced.
- **Kicker channel (K):** same-channel weekly response uses the existing ESPN specialist projection plus `team_implied_points` already present in the nflverse schedule matchup context. Those implied points come from nflverse `total_line` and `spread_line` when available. The v0.31 implied-points elasticity is an explicitly **uncalibrated local channel prior** until prospective kicker Data/MC closure is available.

The ordinary FA/waiver and trade market consumes QB/RB/WR/TE only. D/ST and K may still contribute to complete-lineup scoring, but they do not enter the player-market response coordinate. If a second defense consumes a bench slot, the slot cost is computed from the existing player-sector roster response; no external cross-position valuation is used.

## v0.30-fixed6 counterfactual league-state source rule

No new external source is added. fixed6 changes how already-snapshotted information is propagated through the transaction counterfactual.

The released-player transition kernel uses ESPN league state (other-team rosters, waiver order, roster legality, ownership/projection context), Sleeper trend metadata already present in the snapshot, and the existing explicitly uncalibrated manager-claim behavior prior. The **value** of a recipient roster change is not taken from that behavior model or from an external trade-value source: the before/after roster is propagated through the same commissioned predictive football model used for our own roster, including the existing K, interaction, availability/workload and lineup machinery.

The fixed4/fixed5 contingent option/stress ensemble remains a local diagnostic/screening calculation only. Its additive utility weight is zero in fixed6 and it does not determine action classification. No paid fantasy API, generic trade chart, or player-name-specific release penalty is introduced.

The first-order waiver response explicitly stops after the likely recipient's required release; a recursive second waiver cascade is not yet propagated. Claim probabilities remain uncalibrated manager-behavior priors until league-specific observations accumulate.


## v0.30-fixed4 contingent-roster source rule

No new external source is added. The fixed4 contingent-roster ensemble uses only already-snapshotted local model inputs: roster composition, position, season-level modeled value/latent uncertainty, ESPN projection provenance/anchor diagnostics, and the existing free-agent replacement pool. Future availability/limited-role probabilities in this auxiliary market ensemble are explicit **uncalibrated configuration priors** used only to estimate contingent roster option value; they do not overwrite the v0.27 current-week availability posterior or the commissioned predictive player mean.

Classification-aware MC futility stopping is purely computational. It uses the paired predictive action universes already generated by the local model and does not add any external source or alter source authority.


## v0.30-fixed3 market-utility source rule

No new external source is added. The roster-level option/scarcity layer uses only the already-snapshotted player projections, latent uncertainty, free-agent replacement pool, ESPN anchor provenance, and the shared predictive model state. Projection provenance may discount only the **auxiliary market option premium**; it does not overwrite or force the commissioned player mean toward ESPN. Trade-search expansion remains deferred.

## v0.30 trade/waiver market source contract

v0.30 adds **no paid or private external market data source**. Market decisions are derived from the same locally snapshotted sources already used by the predictive model:

- ESPN: authoritative league rosters, waiver priority/status, droppable state, projections, ownership, completed transactions and available-player pool;
- Sleeper: public add/drop trend context and structured player metadata;
- nflverse/NFL.com: the existing football-state, matchup and roster/status inputs consumed by the player model.

Our trade valuation and the partner's modeled roster utility use the same player/K/interaction/availability pipeline. The independent partner behavior model may use ESPN public ownership/projection context and Sleeper trends as perception features, but does not import generic trade-value charts. `P(accept)`, `P(counter)`, `P(reject)` and waiver manager-claim probabilities are explicitly **uncalibrated v0.30 behavior priors** until actual league behavior is observed. No ESPN write endpoints are used.


## v0.29 prospective closure source contract

Postgame component closure uses nflverse's season-level `stats_player_week_<season>.csv` asset. The observation file is refreshed only when `closure-update` is explicitly run (unless `--cached` is requested), preserving the project's low-frequency polling policy.

Decision-time integrity rules:

- pregame predictions are immutable timestamped captures under `data/season_predictions/closure/`;
- the closure builder uses the latest capture for a player that predates that player's kickoff;
- post-lock captures never overwrite a valid pregame state;
- component observations are football statistics, not fantasy-point training targets;
- missing player-stat rows are recorded as missing observations and are **not** interpreted as inactive;
- availability calibration is scored only when an explicit active/inactive truth field is present;
- derived mutable convenience files (`ledger.csv`, `summary.json`) are backed by timestamped immutable closure snapshots under `data/season_closure/snapshots/`.


## v0.28-fixed4 operational shadow-grid rule

The historical sources and fitted artifacts are unchanged. With `commissioned_only=true`, SHADOW interaction surfaces are retained only for offline diagnostics and future validation; they contribute neither an operational mean correction nor operational MC variance. Only chronologically COMMISSIONED surfaces may contribute `delta` or `sigma_interaction` to live predictions.

## v0.28-fixed3 historical player-stat source correction

The interaction feeder no longer relies on the older aggregate nflverse `player_stats/player_stats.csv.gz` release, because that aggregate can lag the most recently completed season. `python fantasy.py sync-nflverse` now reads the configured interaction seasons and downloads the current season-level weekly assets from:

```text
https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_<season>.csv
```

Those files are cached under `data/raw/nflverse/player_stats_seasons/` and combined into the existing local compatibility path `data/raw/nflverse/player_stats.csv.gz`. Current `stats_player` weekly files may identify the offense with `recent_team` without carrying `opponent_team`; the interaction fitter therefore recovers missing opponent identity from the historical PBP season/week `posteam -> defteam` mapping before the pregame-defense join. Explicit source opponent fields remain preferred when present.

A failed fit writes `data/fitted_models/interaction_grids/v001/fit_failure.json`. `interaction-status` treats a newer failure marker as authoritative and labels any older manifest stale until a successful refit clears the marker.

## v0.28 offline interaction-grid calibration inputs

v0.28 adds no paid/private source. The higher-order interaction feeder uses the same free nflverse releases already used elsewhere in the project:

```text
weekly player stats: data/raw/nflverse/player_stats.csv.gz
players / position IDs: nflverse players release
historical PBP: data/raw/nflverse_matchups/play_by_play_<season>.csv.gz
```

`python fantasy.py interaction-fit` is an explicit offline calibration job. It reconstructs defensive coordinates using only plays completed **before** each historical player-game, constructs rolling pregame player-component baselines, forms underlying-football-stat Data/MC ratios, and freezes the resulting correction/uncertainty/support surfaces under `data/fitted_models/interaction_grids/v001/`. Missing historical PBP may be downloaded from the same public nflverse release URLs used by `season-sync`; no ESPN credentials are involved.

The fit target never contains fantasy points, fantasy rank, points-allowed-to-position, or external fantasy recommendations. Fantasy scoring is applied only after a saved component correction is interpolated during forward prediction. Every artifact manifest records `fantasy_points_used_in_fit=false`, training seasons, chronological validation season, source file hashes, baseline method, and interpolation method.

The normal GUI/MC does **not** retrain or query nflverse for these corrections. It reads the frozen local artifact. If the artifact is missing or a component failed chronological commissioning, its operational correction is exactly neutral while the v0.23/v0.27 base model continues unchanged.

## v0.27 availability evidence policy

v0.27 adds no paid or private data source. It changes how already-snapshotted weekly status/practice observations are combined. The current-week availability posterior uses the reconciled weekly game designation as a prior, then prefers NFL.com practice evidence when the injury table is successfully parsed and matched; Sleeper practice participation is used only when official practice is absent. The source observations and the likelihood-ratio updates are retained separately in diagnostics.

NFL.com practice and Sleeper practice are never multiplied together as independent evidence. Daily official practice rows are also treated as correlated: only the latest practice state plus one trajectory summary are used. If neither source provides practice information, the model falls back explicitly to the status prior. Hard unavailable NFL roster/game states remain authoritative `P(active)=0`.

The v0.27 practice likelihood ratios are configuration-visible **uncalibrated priors**, not claimed empirical frequencies. They are tagged as such so later observed active/inactive and workload closure can replace them with calibrated values.

## v0.25-fixed GUI/chat-report data policy

v0.25-fixed adds **no new external data source**. The new chat-report export is derived entirely from the same loaded snapshot and SeasonGuiService state. The season GUI reads the same immutable/latest season snapshots and processed player-value files used by the CLI. The GUI's **Refresh Data** button invokes the existing `season-sync` pipeline; it does not bypass source authority, perform aggressive polling, or submit any ESPN league action.

The underlying predictive model remains v0.23, so references below to the v0.23 matchup/prediction treatment describe the model consumed by the v0.25 GUI.

## v0.23 prediction-channel and matchup treatment

ESPN remains authoritative for fantasy-league state. Its projections are additionally retained as an **external predicted-yield channel** with timestamps/provenance. A projection is never silently interpreted as observed truth. The predictive layer keeps both the internal latent prediction and the ESPN anchor so later data/MC closure can compare:

```text
observed NFL/fantasy outcome
vs internal model prediction
vs ESPN projection
```

The predictive-yield audit is written under `data/season_predictions/`. v0.23 additionally records the nflverse-derived matchup/kinematic acceptance coordinates used at prediction time, while ESPN remains an independent predicted-yield anchor.

## ESPN Fantasy Football

Role: **authoritative fantasy-league state**.

Authentication remains local-only through:

```text
L:\Projects\fantasy_football\config\secrets.json
```

v0.21 reads and snapshots:

```text
league settings
teams / rosters / lineup slots
matchups / standings
waiver rank
ESPN fantasy transactions
FREEAGENT + WAIVERS player pool
weekly and season projections
ESPN injury status
percent rostered / started
player droppable flag
lineup-locked flag
on-team ID
```

The reverse-engineered ESPN fantasy interface remains isolated in:

```text
src/data_sources/espn_league.py
```

Raw responses are retained before normalization because the interface is undocumented.

## Sleeper

Role: **public structured corroboration**.

No authentication.

v0.21 retains:

```text
ESPN/Sleeper cross IDs
injury/status metadata
practice participation
depth-chart position/order
24-hour trending adds
24-hour trending drops
```

Sleeper does not override successfully matched official NFL game status.

## NFL.com

### NFL.com compact roster statuses

The public team-roster pages expose compact status codes. The season manager preserves the raw code and derives a separate weekly-availability interpretation. In particular, `RSR` is treated as a reserve-list/stash-only state and mapped to hard-unavailable `IR` for the current week. Unknown codes are never guessed: they are excluded from ordinary actions and printed in diagnostics for review.


### Current team rosters (v0.21-fixed5)

`season-sync` fetches all 32 public NFL.com team roster pages once per sync. A unique normalized-name match is treated as the highest-priority current NFL roster/status observation for transaction eligibility. This catches states such as `RLS` (reserve/left squad) that can lag in ESPN, Sleeper, or nflverse. Raw HTML is retained under the timestamped snapshot.

Normal-action policy: `ACT` is eligible; reserve/PUP/IR/suspension/exempt/RLS states are stash-only; cut/retired/UFA states are excluded. Lower-priority roster feeds are used only when there is no safe NFL.com match.


Role: **official real-NFL transactions and official injury/practice observations when parseable**.

No private authentication is used.

v0.21 snapshots current-month public transaction category pages for:

```text
trades
signings
reserve-list
waivers
terminations
```

Raw HTML and normalized JSON are saved under each season snapshot.

The public injury page is also saved. Because NFL.com may render the report dynamically, the parser only accepts a static table when it can identify an explicit `Player`, `Injury`, and `Game Status` structure. If that structure is absent, no official injury override is generated.

This is intentionally fail-safe. A parser/layout failure cannot erase a successful ESPN snapshot.

## nflverse

Role: **performance/usage/statistical backbone**.

No authentication.

v0.21-fixed3 now consumes the public daily 2026 roster release directly during `season-sync` and joins it by ESPN ID. It is used to identify current NFL roster membership/status and to prevent stale ESPN pro-team metadata from making retired/released players look actionable. Raw roster CSV is retained under each season snapshot.

v0.23 now uses schedules and play-by-play for the opponent matchup layer. The next live-stat layer will additionally use current player-level snap counts, routes/targets/carries and other usage data to update exposure/rate posteriors.

nflverse roster status is a secondary current-roster cross-check; NFL.com remains authoritative for current team-roster status, official injury/game status, and transactions. nflverse is not treated as the authoritative 2026 injury feed.

## nflverse schedules + play-by-play matchup inputs (v0.23)

Role: **measured opponent/environment coordinates for the weekly acceptance layer**.

No authentication. The implementation uses the public nflverse release files:

```text
schedules:  releases/download/schedules/games.csv
players:    releases/download/players/players.csv
play-by-play releases/download/pbp/play_by_play_<season>.csv.gz
```

The full PBP files are cached under `data/raw/nflverse_matchups/`; timestamped season snapshots contain the compact derived matchup context and exact source hashes rather than duplicating the large raw PBP on every refresh.

v0.23 derives defense/offense observables from regular-season plays only. Current-season data only use completed weeks before the fantasy decision week. Current 2026 measurements are aggressively shrunk toward 2025 by play count before standardization.

The current schedule supplies opponent, home/away state, game total/spread and implied team points when those fields are populated. Missing lines do not cause a fabricated line; the game-environment contribution simply remains neutral.

For a current ESPN weekly projection, ESPN is interpreted as an external yield prediction already at ESPN's implicit acceptance point. Our independent `K` is applied to our internal model branch before the weak ESPN ensemble, avoiding double-counting matchup.

DST uses the same opponent/offense observations but is propagated through component-level sacks/turnovers/points/yards outcomes and the exact configured ESPN DST buckets.

## Public web/news

Role: contextual evidence for unusual cases only.

Examples:

```text
snap-count limitation reports
coach comments
breaking trade context
unexpected role/depth-chart changes
warmup aggravations
```

Analyst start/sit recommendations are not accepted as optimizer inputs.

## Authority hierarchy

```text
Fantasy roster / waiver / trade state -> ESPN
Official NFL status / transaction     -> NFL.com when successfully retrieved/matched
Current NFL roster/status              -> NFL.com team rosters
Secondary roster/status cross-check    -> nflverse rosters
Structured corroboration              -> Sleeper
Usage / performance                    -> nflverse
Context                                -> public reporting
```

## Refresh cadence

The design assumes low request volume:

```text
normal day: one complete refresh
game day: a few targeted refreshes around relevant kickoff windows
```

v0.23 does not aggressively poll any source. Prior-season PBP is cached; schedules and current-season PBP are refreshed at the same low season-sync cadence.
