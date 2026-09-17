# Fantasy Football Season Manager v0.35-fixed1

## v0.35-fixed1 predictive-confirmation correction

Live commissioning showed that the first v0.35 temporal player-state policy could let a deterministic expected-lineup screen authorize future roster changes, producing aggressive projected swaps such as dropping valuable bench assets for tiny lineup gains. fixed1 restores the mature player-channel hierarchy: the expected-lineup calculation is screening only, and a future QB/RB/WR/TE FREEAGENT swap changes P_w only after paired predictive H2H MC confirmation under common random numbers with the existing ACTIONABLE/POSSIBLE thresholds. The decision week must also be non-worsening. No 2026 game outcome is used for tuning.

## v0.35 causal temporal player-membership state

## v0.35 causal temporal player-membership state

v0.35 completes the next first-order state transition in the pre-data architecture. Future specialist decisions no longer evaluate the player slot on frozen synchronized membership: our QB/RB/WR/TE membership is propagated week by week under a causal expected player-channel policy using current guaranteed FREEAGENTs, byes/matchups, and expected availability only. Current Week-1 membership and immediate player actions remain the commissioned observed state. At a future specialist activation boundary the model expands locally around the evolved P_w and freezes post-perturbation player-market reaction at first order; full other-manager player-market evolution and higher-order transaction response are reserved for v0.36. No 2026 game outcome is used for tuning.


## v0.34 a priori prospective measurement contract

v0.34 freezes the complete decision-time measurement state needed for later 2026 Data/MC work before any game outcome is used to tune the model. The inherited v0.29 user/opponent player capture remains intact; the same immutable artifact now also stores all-league rostered QB/RB/WR/TE forward states, current-week D/ST and kicker prediction distributions, D/ST component expectations, explicit kicker component-model limitations, and the ESPN/league market covariates that drive uncalibrated waiver/trade/specialist behavior kernels. This release records the apparatus; it does not calibrate it. `closure-update` remains player-only until the Data-informed 1.X series.


## v0.33-fixed2 commissioning correction

v0.33 replaces the frozen-current player-slot release used by future two-DST activation rows with an explicit activation-week state. The existing specialist market continues to evolve ownership and next-week releases; v0.33 now records those market states, selects the sacrificed QB/RB/WR/TE slot from activation-boundary information without realized-score hindsight, and recomputes the fixed6-style released-player claimant/recipient response from that activation week under common random numbers. Future active/inactive revelation is an explicitly uncalibrated information proxy, and ordinary-player roster membership is not fabricated between season-sync observations.


## v0.32-fixed5 release-bootstrap commissioning fix

No numerical specialist-policy change from v0.32-fixed4. Fresh archives contain no materialization markers, reconstruct the full commissioned lineage before execution, and package an explicit data directory.


## v0.32-fixed4 policy-state commissioning fix

Live commissioning exposed candidate-invariant CARRY2 rows. fixed4 makes second-DST ownership an activation-time state transition: the evolving defense market chooses the acquired defense at the activation week, the player-slot release begins only then, and opening the slot now competes against deferring it. L2 also separates deterministic policy proposals from uncertainty-qualified recommendations. CLI output emits real newlines while remaining ASCII/cp1252 safe.


## v0.32-fixed3 commissioning metadata fix

No model or specialist-policy calculations change in this narrow release. The inherited fixed2 metadata regression is advanced atomically for VERSION, README, and DATA_SOURCES so release metadata cannot fail one stale assertion at a time.


## v0.32-fixed2 commissioning metadata fix

This narrow release changes no specialist-policy or player-model calculations. It advances the inherited README metadata regression to the current release header. v0.32 L1/L2/L3/L4 behavior is unchanged.


## v0.32-fixed1 commissioning compatibility fix

This narrow release does not change the v0.32 specialist policy model. It restores the inherited `SAME-CHANNEL STATIC SWAPS` CLI label as the L1 diagnostic heading and advances inherited release-version assertions to `0.32-fixed1`. The L2 dynamic one-slot and L3/L4 carry2 policy calculations are unchanged.


## v0.32: dynamic specialist league-state response

v0.32 turns the v0.31 specialist diagnostics into explicit week-to-week management policies while preserving the commissioned QB/RB/WR/TE player propagator.

The hierarchy is now:

```text
L1  static same-channel board
L2  one-slot specialist market policy pi_D^(1) / pi_K^(1)
L3  two-DST policy pi_D^(2)
L4  paired complete-roster response with player-slot release + fixed6 release externality
```

The authoritative two-defense denominator is no longer a static Detroit-only state.  It is the dynamic one-slot defense policy:

```text
delta D_carry2 = U_D(pi_D^(2)) - U_D(pi_D^(1))
```

The specialist market transition is deliberately explicit and coefficient-light:

- transactions use pregame expected same-channel yield only;
- realized MC never selects a transaction or starter;
- the initial guaranteed market contains current ESPN `FREEAGENT` specialists only;
- current `WAIVERS` specialists are excluded from that guaranteed pool instead of being assigned a fabricated success probability;
- a dropped specialist becomes available in the next modeled week, not to a second manager in the same week;
- future simultaneous demand uses current ESPN waiver priority only as an `UNCALIBRATED` ordering proxy;
- a manager changes specialists only for a strict pregame expected-yield improvement.

For carry2, v0.32 first computes D2-vs-D1 inside the defense channel, then removes the least-cost legal player-sector release and propagates that altered player roster through the existing predictive player MC.  The fixed6 released-player league-state response is retained, and the final action is classified from paired H2H utility under common random numbers.  This remains a comparison between two complete roster states, not a direct D/ST-vs-RB value chart.

The kicker channel gains the same L2 dynamic one-slot policy. Carrying two kickers remains disabled.

The v0.31-fixed3 static specialist board remains available as L1 diagnostic context, and the player market/trade channel remains QB/RB/WR/TE-only.


## v0.31-fixed3: Windows redirected-output compatibility

fixed3 changes CLI transport only; the fixed2 specialist calculations and player-channel physics are unchanged.

- Specialist CLI output is ASCII-only so standard Windows PowerShell redirection / `Tee-Object` cannot fail on cp1252 when printing symbols such as Greek delta.
- Human-readable equivalents are used: `delta`, `+/-`, `|`, and `x`.
- A regression encodes the complete specialist CLI report as cp1252, reproducing the exact redirected-output environment that failed in fixed2.
- Decision-audit release provenance is `0.31-fixed3`; specialist physics-method provenance remains fixed2 because no numerical model changed.


## v0.31-fixed2: specialist commissioning corrections

fixed2 is a narrow commissioning patch; the `P + D + K` channel architecture and mature player channel are unchanged.

- Specialist team identifiers now pass through the shared nflverse team normalizer before bye/schedule lookup. This fixes aliases such as `WAS -> WSH` in the kicker channel.
- Same-channel K/DST season comparisons are labeled **static swaps**, not a dynamic future streaming policy.
- Two-DST rotation still selects starters from pregame modeled expectation (never realized MC outcomes), but a positive result is now `CARRY_SYNERGY_SCREEN`, not an authoritative carry recommendation. Its baseline is explicitly the best static one-DST state.
- Player-slot coupling reports lineup cost, insurance cost, configured insurance weight, total slot cost, and method provenance separately.
- Specialist CLI action blocks are emitted atomically so a numbered header cannot be separated from its diagnostics.
- Player-channel production, availability, K, interaction-grid, trade, waiver-release, and hierarchical-MC physics are unchanged.

A future dynamic one-slot specialist policy must model the state transition and future availability of streamed specialists rather than assuming today's free-agent pool remains available all season. fixed2 deliberately does not fabricate that kernel.


v0.31 is the **sector-separated roster-response architecture**. The commissioned QB/RB/WR/TE player channel is preserved. Defense and kicker management are now separate specialist channels, and the system no longer asks physically ill-posed questions such as whether a D/ST is directly more valuable than an RB.

The model decomposition is

```text
P = {QB, RB, WR, TE}   player channel
D = {DST}              defense channel
K = {K}                kicker channel

complete roster state = P ⊕ D ⊕ K
```

Channels are compared internally and combined only when evaluating a complete roster configuration.

## v0.31: channel-separated roster response

### Player channel

The ordinary FA/waiver and trade markets now contain **QB/RB/WR/TE only**. This retains the detailed player MC, matchup K, v0.28 Data/MC interaction corrections, v0.27 availability/workload model, lock-aware lineup policy, fixed5 hierarchical futility stopping, and fixed6 first-order released-player league-state response.

- `roster-actions` preselection, legal drops and reported actions exclude K/DST.
- `trade-search` and `trade-eval` are player-channel only. Manual specialist trades fail explicitly instead of silently entering the player valuation coordinate.
- The player-market report schema is 12 and identifies `market_channel=PLAYER_QB_RB_WR_TE_V031`.

### Defense channel

D/ST is treated as a weekly lineup/configuration response, not a player-market asset.

For a defense configuration `D`, the channel produces weekly predictive response vectors and evaluates same-channel state changes such as

```text
HOLD DET
SWAP DET -> NO
CARRY {DET, NO}
```

For multiple owned defenses, the weekly starter is selected from the **pregame modeled expectation**. Realized MC points score that already-selected defense; the optimizer never takes a hindsight maximum over realized outcomes.

The two-defense quantity is therefore a matchup/bye **complementarity** response relative to the best one-defense state:

```text
ΔD_rotation = U_D({D1,D2}) - max[U_D({D1}), U_D({D2})]
```

This prevents a defense that is simply better every week from creating artificial second-D/ST value; that case is a same-channel `SWAP`, not rotation synergy.

If carrying another D/ST requires a bench slot, v0.31 asks the player sector for the least-cost legal QB/RB/WR/TE release **after** calculating defense synergy. The report keeps these coordinates separate:

```text
rotation_synergy_ppg
player_slot_cost_ppg
net_complete_state_ppg
```

This is not a direct `DST > RB` comparison. It is the response difference between two complete roster states whose internal channels were propagated separately.

The D/ST weekly distribution continues to use the commissioned v0.23 component model: sacks, turnovers, defensive TDs, points allowed and yards allowed with the exact ESPN scoring response and matchup context.

### Kicker channel

Kicker management is also same-channel only:

```text
HOLD K1
SWAP / STREAM K1 -> K2
```

A second kicker is disabled by default. The existing specialist projection is supplemented by a simple weekly team-scoring-environment response derived from the already-snapshotted nflverse schedule/game-total coordinate. The v0.31 kicker matchup elasticity is explicitly **uncalibrated** pending prospective kicker closure; it is not presented as commissioned player physics.

### CLI / GUI

New commands:

```powershell
python fantasy.py roster-actions      # PLAYER channel only
python fantasy.py defense-channel     # D/ST swaps + rotation synergy
python fantasy.py kicker-channel      # K swaps / streams
```

The NiceGUI control room now labels the FA/waiver surface **Player market**, excludes specialists from player add/drop and trade selectors, and adds a **Specialists** tab backed by the same defense/kicker channel service used by the CLI. Specialist decisions obey the same current-week lock boundary as the player channel: a locked/past-kickoff specialist cannot be swapped out, and a locked current starter remains immutable for that week.

### Scope boundary

v0.31 deliberately does **not** rebuild the already-commissioned player propagator and does not yet implement the proposed dynamic week-to-week league-state kernel. The architecture is corrected first: player, defense and kicker channels have distinct response functions and only meet at the complete-state level.

## v0.30-fixed6: paired counterfactual league-state response

The fixed5 commissioning run established that raw-only futility stopping works (31+ minutes -> about five minutes for a resolved HOLD), but it also exposed the remaining conceptual problem: a dropped player still effectively vanished from the modeled system. That is inconsistent with the physics foundation of the project. The state to perturb is the **league**, not only our roster.

For an action operator \(T_a\) and common-random-number universe \(\omega\), fixed6 makes the authoritative quantity

```text
ΔU_a(ω) = U[T_a(X), ω] - U[X, ω]
```

where `X` contains our roster, all opponent rosters, the available/waiver pool, schedule, player latent states, and current information state.

- **Direct response remains diagnostic.** The normal paired action MC still reports the response obtained when our roster changes while the opponent/field reference is held fixed.
- **Released players remain in the system.** For every unique serious drop candidate, fixed6 constructs a first-order waiver transition over the other managers. Roster legality, waiver priority and the existing uncalibrated manager-claim behavior model define the discrete transition kernel.
- **Recipient value uses the commissioned football model.** A plausible receiving roster is evaluated before and after the claim with the same player-yield/K/interaction/availability/lineup generator and common random numbers. No static trade-value chart, player-name rule, or hand-added Kamara/Kittle penalty is introduced.
- **The league reference is perturbed.** Expected recipient responses are propagated into the same opponent/field reference used by our paired H2H calculation. Week 1 uses the actual scheduled opponent when that manager is the claimant; future weeks use the field-average response.
- **The league-state paired distribution is authoritative.** `ACTIONABLE_EDGE` / `POSSIBLE_EDGE` classification and 1,024 -> 4,096 -> 16,384 escalation use the counterfactual league-state response. The direct-roster distribution is reported separately as a diagnostic coordinate.
- **Old option/scarcity utility is demoted.** The fixed4/fixed5 contingent future-roster ensemble remains available as a screening/diagnostic response probe, but its additive utility contribution is exactly zero in fixed6. It can no longer create or rescue an action classification.
- **Small-N response, large-N only when needed.** The released-player league response defaults to 256 paired universes and is cached by dropped player. The main action MC retains the existing hierarchical futility logic, so a resolved league-state HOLD can still stop after SCREEN1.
- **First-order boundary is explicit.** If another manager claims our released player, fixed6 surfaces the player that manager would release, but does not recursively propagate that second release through another waiver cascade. That is a documented approximation, not hidden value loss.
- **CLI and GUI use the same transaction physics.** Both surfaces report direct paired H2H response, league-state paired response, release claimant probability / recipient gain / field shift, and contingent-depth diagnostics separately.

This formulation follows the project design principle: **change the initial condition, propagate it through the same commissioned model, and measure the paired system response.**

## v0.30-fixed5: raw-only futility + option-edge parking

The fixed4 live trace showed that low-probability direct football edges were still reaching 4,096 and 16,384 universes whenever the separate contingent-roster adjustment made the combined probability look strong. fixed5 corrected that execution mismatch by making predictive escalation raw-only, parking option-only rows at their current stage, strengthening the broad contingent screen, preserving same-N baselines, and printing each CLI action atomically. Those runtime/reporting improvements are preserved in fixed6, but option depth is no longer part of authoritative transaction utility.

## v0.30-fixed4: paired contingent roster states + MC futility stopping

The full fixed3 trace showed two distinct remaining problems: deep bench skill players could still look nearly valueless in the deterministic one-starter-out option model, and low-probability add/drop actions continued through **1,024 -> 4,096 -> 16,384** even when their `P(better)` was already far below the 67% `POSSIBLE_EDGE` threshold.

fixed4 changes only the market decision layer:

- **Paired future-roster-state ensemble.** Bench option value is now estimated with a small, separate common-random-number MC over future player availability, LIMITED workload, and latent role/mean uncertainty. Each sampled state is optimized as a legal lineup for HOLD and for the action roster. This captures multi-player availability/role contingencies that the fixed3 one-starter-out stress test missed.
- **Diminishing portfolio value.** Redundant players can still have real injury/role insurance, but only the best legal lineup scores in each state. A second or third player competing for the same TE/RB/WR/FLEX path therefore has diminishing marginal value rather than an additive standalone premium.
- **Provenance-aware auxiliary value is preserved.** Weak `MODEL_LATENT_PPG_FALLBACK` states are shrunk toward the actual free-agent replacement coordinate in the contingent market ensemble only; the commissioned predictive player mean is untouched.
- **Scarcity is diagnostic by default.** `StressDepth` is reported from states where at least one current skill-position starter is unavailable/limited, but its default utility weight is zero so it is not double-counted on top of the same contingent option-depth ensemble.
- **Classification-aware futility stopping.** After each predictive stage, fixed4 computes a conservative Wilson upper bound for raw and combined `P(better)`. If neither channel can plausibly reach the configured 67% `POSSIBLE_EDGE` threshold, the action does not advance to a larger MC stage. A resolved HOLD therefore no longer pays for 4k/16k refinement merely because its mean delta is slightly positive.
- **Visible opponent-reference progress.** The lazy whole-league opponent-reference simulation is now explicitly reported as its own phase instead of appearing as a multi-minute silent gap inside the HOLD baseline.
- **Cheaper screening stages.** SCREEN1/SCREEN2 omit the starter-only insurance simulation; those display-only diagnostics are evaluated at FINAL or restored from the already-computed fast utility when futility stopping ends early.

The default requested hierarchy remains **1,024 -> 4,096 -> 16,384**, but `roster-actions` now reports the stages actually executed and whether the run stopped for statistical futility. The small contingent roster ensemble defaults to 512 states (64 in the broad screen) and is independent of the main fantasy-score MC.

## v0.30-fixed3: roster-level option/scarcity + evidence separation

The fixed2 auxiliary bench utility summed standalone player option/scarcity values. That could double-count redundant future lineup paths and could amplify a weak `MODEL_LATENT_PPG_FALLBACK` projection into an apparently actionable transaction even when raw paired H2H MC was essentially neutral.

fixed3 changes only that auxiliary market layer:

- **Future-role option is roster-level.** The current mean season lineup is compared with a provenance-discounted upside lineup for non-starting QB/RB/WR/TE players. Only the best legal lineup can realize the upside, so overlapping third-TE / sixth-RB / FLEX paths do not add independently.
- **Replacement scarcity is marginal.** The roster is evaluated in one-starting-skill-player-out stress tests. The full roster's depth advantage is compared with the original starter core plus freely available replacement-level fills. This measures portfolio depth rather than summing standalone player scarcity gaps.
- **Auxiliary confidence is provenance-aware.** The commissioned predictive mean is never changed. Only the extra stash/option premium is discounted when its projection provenance is weak or when the model strongly disagrees with an explicit ESPN anchor. The support factor is recorded diagnostically.
- **Raw predictive evidence remains separate.** `ACTIONABLE_EDGE` now requires the raw paired predictive MC itself to reach the actionable criterion. If only the auxiliary roster portfolio term creates a positive resolved combined utility, the action is labeled `ROSTER_OPTION_EDGE` and the immediate recommendation remains HOLD.
- **Reporting is explicit.** CLI/GUI/chat diagnosis expose raw H2H delta and probability, combined roster utility, portfolio-option delta, replacement-stress delta, and candidate support separately.
- **Section reporting is unambiguous.** An empty waiver section no longer prints a global "HOLD" statement when positive free-agent rows exist.

The base predictive model, K, v0.28 interaction grids, availability/timing policy, 16,384 default MC, waiver `P(acquire)` behavior model, and trade valuation/acceptance model are unchanged.

## Preserved fixed2/fixed1 execution behavior

`roster-actions` retains live PowerShell progress output and the hierarchical action-MC frontier. The default path is **1,024 -> 4,096 -> 16,384** universes; only a small status-balanced finalist set reaches full N. The command still accepts `--mc` as a temporary runtime override without mutating `config/model.json`.

The expensive higher-priority-manager waiver blocker analysis remains deferred until a waiver candidate reaches the final action frontier. Every displayed waiver `P(acquire)` still uses the detailed manager best-add/drop model; the cheap estimate is pruning-only.

Examples:

```powershell
python fantasy.py roster-actions
python fantasy.py roster-actions --mc 4096
python fantasy.py gui
```

## v0.30: market decision layer

The key separation is:

```text
shared predictive player model
        ↓
our roster utility          partner roster utility
        ↓                         ↓
trade value if executed     partner modeled benefit
        └──────────────┬──────────┘
                       ↓
          separate manager-behavior model
          P(accept) / P(counter) / P(reject)
```

Trade response probabilities are intentionally tagged `UNCALIBRATED_TRADE_RESPONSE_V030`. They are not generic trade-chart values and do not alter the underlying player valuation. The partner market-perception channel uses only information already available to the project (ESPN projected production/ownership and Sleeper trend context) and stays separate from our modeled roster utility.

The trade evaluator supports up to **two players per side**. Unequal packages explicitly model the best legal post-trade release; a consolidation trade that opens a roster slot may also receive the best currently guaranteed `FREEAGENT` fill, which is surfaced in the report rather than hidden. No waiver success is assumed for that fill.

Trade search is deliberately two-stage: a cheap league-wide one-for-one screen generates candidates, then the best candidates are evaluated using paired predictive MC. Search-stage MC defaults to 4,096 so the normal 16,384-universe GUI/model state is not mutated.

Waiver acquisition probability remains separate from value-if-acquired. For each higher-priority manager, v0.30 evaluates the candidate against that manager's actual roster, finds the modeled best legal drop, and estimates a provisional claim probability from the resulting season/current-week benefit plus public ownership/trend context. These probabilities are tagged `UNCALIBRATED_MANAGER_CLAIM_UTILITY_V030` until real 2026 league claims provide calibration data.

### v0.30 commands

```powershell
python fantasy.py roster-actions
python fantasy.py trade-search --limit 6
python fantasy.py trade-eval --partner-team-id <TEAM_ID> --give <ESPN_ID[,ESPN_ID]> --receive <ESPN_ID[,ESPN_ID]>
python fantasy.py gui
```

The GUI adds a **Trades** tab with a read-only Trade Lab. It displays our modeled season/current-week change, the partner's modeled change, the independent accept/counter/reject probabilities, expected accepted-offer value, and any modeled release/free-agent fill. No ESPN trade, waiver, add/drop, or lineup write is submitted.

## v0.29 closure subsystem (preserved in v0.30)

The new commissioning loop is deliberately append-only at the prediction boundary:

```text
latest pregame snapshot + exact GUI/service model state
        ↓
closure-capture / Capture Pregame State
        ↓ immutable
data/season_predictions/closure/pregame_<season>_w<week>_<timestamp>.json
        ↓ after games
closure-update (fresh nflverse stats_player weekly data)
        ↓
data/season_closure/ledger.csv
data/season_closure/summary.json
data/season_closure/snapshots/closure_<timestamp>.json
```

The frozen player record stores Base MC, interaction-corrected MC, the complete uncertainty budget, availability posterior, lock timing, and every underlying football component currently exposed by the v0.28 interaction layer. Fantasy points are retained as the downstream yield; component closure remains in football-stat space.

For fantasy-yield closure, v0.29 uses the **availability-marginalized** pregame mean and variance. A player's conditional 20-point active projection is therefore not compared directly with a zero produced by an OUT branch. For opportunity/count components (`attempts`, `carries`, `targets`) the closure prediction is also marginalized over FULL/LIMITED/OUT workload. Efficiency quantities such as catch rate and yards/target remain conditional football observables.

The postgame ledger reports, where observable:

- observed − corrected-MC residuals;
- Data/MC ratios;
- Base-MC vs interaction-corrected RMSE;
- pull `z=(Data-MC)/sigma`;
- position/component bias, MAE and RMSE;
- availability Brier score **only when an explicit active/inactive truth field exists**. Missing nflverse stat rows are never silently interpreted as inactive.

The Data/MC GUI tab now shows accumulated prospective closure and a component-level table. It also has **Capture Pregame State**, which writes the exact in-memory GUI/service state rather than constructing a separate optimizer.

### Weekly closure workflow

Before the first relevant game locks:

```powershell
python fantasy.py closure-capture
```

The same action is available from the Data/MC tab as **Capture Pregame State**. Multiple captures are allowed; when building closure, v0.29 selects the latest capture for each player that was still before that player's kickoff. Post-lock captures cannot replace a valid pregame state.

After games have produced nflverse weekly observations:

```powershell
python fantasy.py closure-update
python fantasy.py closure-status
```

`closure-update` refreshes the current-season nflverse weekly-stat asset by default. Use `--cached` only when an explicit network refresh is not wanted.

The closure pipeline never refits the predictive model automatically. Calibration remains an audited offline step for later releases.

> **v0.28-fixed3 source fix:** `sync-nflverse` now downloads the current nflverse `stats_player` season-level weekly assets (`stats_player_week_<season>.csv`) for the seasons configured under `interaction_grid.fit.seasons`, then rebuilds the local `data/raw/nflverse/player_stats.csv.gz`. The obsolete aggregate player-stats URL is no longer the historical feeder source.

> **v0.28-fixed3 schema fix:** current weekly player-stat files can provide `recent_team` without `opponent_team`. Historical interaction fitting now retains that team identity and recovers the opponent from the same season/week nflverse PBP `posteam -> defteam` mapping before joining the pregame defense state. Explicit opponent fields, when present, remain authoritative.

> **v0.28-fixed3 fit-status fix:** failed interaction fits write `fit_failure.json`. `interaction-status` reports the latest failure and labels any older manifest as **STALE** instead of presenting a previous artifact as though it were the current fit. Successful fitting clears the failure marker.

> The v0.28-fixed2 chronological protections remain: defense coordinates and population/player baselines are strictly pregame, validation coverage is audited before commissioning, and a zero-coverage holdout fails explicitly.

The central v0.28 modeling change is:

```text
commissioned base MC (including v0.23 K + v0.27 availability)
        ↓
precomputed football-stat Data/MC interaction grids
        ↓ interpolation at player-state × defense-state coordinates
higher-order interaction correction I ± sigma_I
        ↓
existing ESPN scoring response / predictive MC / lineup utility
```

> **v0.28-fixed4 shadow-grid invariant:** with the default `interaction_grid.commissioned_only=true`, a SHADOW component now contributes exactly `C=1`, `delta=0`, and `sigma_interaction=0` to operational MC. Its fitted surface remains stored in the artifact for offline diagnostics/validation only. This fixes the case where a player could display `I=1.000` yet still receive live interaction variance from rejected grids.

The v0.27 `OUT / ACTIVE_LIMITED / ACTIVE_FULL` state model and the v0.26 lock-aware information policy are unchanged.

The design invariant remains:

```text
CLI ---------┐
             ├── season model / predictive MC / matchup model
GUI service -┘
```

The GUI is a control/visualization layer, not a second optimizer.

## Main command

```powershell
python fantasy.py gui
```

The season GUI defaults to port 8080. The archived draft cockpit remains available separately:

```powershell
python fantasy.py draft-gui
```




## v0.28: precomputed Data/MC interaction correction grids

The interaction layer follows a calibration-table workflow rather than fitting anything inside the weekly MC:

```text
historical player-game football observations
        +
pregame defensive state (no current-game leakage)
        +
pregame rolling player-component baseline
        ↓
Data / base-MC component ratios
        ↓
small 2D correction grids
        ↓
chronological holdout validation
        ↓
versioned artifact under data/fitted_models/interaction_grids/
        ↓
weekly MC interpolates the saved grid only
```

For each component `k`, the historical calibration target is an underlying football-stat ratio:

\[
C_k(x,d) = E\left[\frac{D_k}{MC_k^{(0)}} \middle| x,d\right],
\]

where `x` is the player's pregame/base component value and `d` is a pregame defense coordinate. The fit never uses fantasy points, fantasy rank-vs-position, start/sit grades, or external fantasy matchup scores.

The initial component grids are deliberately small rather than one sparse high-dimensional table. The default v001 artifact contains candidate surfaces for QB passing/rushing volume and efficiency, RB rushing/receiving volume and efficiency, and WR/TE target/catch/receiving-efficiency components. Each surface is evaluated against the defense coordinate most directly associated with that component. Raw cell ratios are shrunk toward unity, lightly neighbor-smoothed, and saved together with interpolation axes, uncertainty, effective support, and chronological validation metadata.

The latest configured training season is held out chronologically. A component is marked `COMMISSIONED` only when the correction improves held-out component-ratio closure; otherwise it remains `SHADOW` and is forced to a neutral correction operationally by default.

At weekly runtime, the already-fit artifact is cheap to evaluate. A player baseline and current opponent defense state select a point on each relevant grid; bilinear interpolation returns the correction and finite-grid uncertainty. The corrected football components are passed through the league scoring response to obtain an additive higher-order point correction to the existing commissioned base MC. The existing v0.23 K layer therefore remains the base matchup term in v0.28 rather than being silently replaced.

The predictive uncertainty decomposition is now:

\[
\sigma_{pred}^2 = \sigma_{game}^2 + \sigma_{model}^2 + \sigma_K^2 + \sigma_I^2,
\]

where `I` is the precomputed interaction-grid correction. `sigma_I` is propagated through a separate deterministic player-keyed random stream so paired/common-random-number comparisons remain reproducible.

The interaction artifact is generated explicitly:

```powershell
python fantasy.py interaction-fit
python fantasy.py interaction-status
```

`interaction-fit` uses the local combined weekly player-stat file produced by `sync-nflverse` plus historical play-by-play inputs. `sync-nflverse` obtains each configured season explicitly from the nflverse `stats_player` release (`stats_player_week_<season>.csv`), avoiding stale aggregate-release coverage. Missing historical PBP is downloaded through the same public nflverse release path used by the matchup model. The normal GUI/MC never retrains the grids.

Current player-component baselines are saved with the artifact. When a player has a matching nflverse/GSIS history, the runtime uses that player baseline; otherwise it falls back transparently to the position baseline. That fallback is surfaced in Player Diagnostics and the chat report rather than hidden. Refining the neutral component projector, especially for rookies/very-low-history players, is intentionally left for later work rather than being fabricated inside the grid fit.

Player Diagnostics now exposes `I`, `Delta I`, `sigma_I`, artifact ID, baseline provenance, support, and the component-level correction factors. The chat report shows the same correction for both user and opponent starters and retains the shared-pipeline symmetry diagnostic. Once observed games exist, Data/MC closure records both the base-MC and interaction-corrected RMSE so the correction can be falsified directly.

## v0.27: evidence-conditioned availability/workload

The weekly designation remains the prior rather than the entire posterior. For the current week, the availability layer now retains a structured evidence ledger and computes:

```text
status prior
    -> preferred practice evidence (NFL.com, else Sleeper)
    -> one latest-practice likelihood update
    -> one practice-trajectory likelihood update
    -> P(active), P(full | active)
    -> FULL / LIMITED / OUT state probabilities
```

NFL.com practice supersedes Sleeper practice so correlated reports are not double counted. Daily practice rows are also not treated as independent observations: v0.27 uses the latest state plus one trajectory summary (`IMPROVING`, `WORSENING`, `STABLE_*`, or `MIXED`). Hard unavailable roster/game states remain exact `P(active)=0`.

Every posterior exposes the base status prior, evidence level, practice source/sequence, likelihood ratios actually used, hours to kickoff at snapshot time when schedule data are available, posterior method, and calibration status. The Player Diagnostics GUI and compressed chat report expose the same evidence for both user and opponent players. Status-only or default-prior fallbacks are explicitly flagged.

The v0.27 likelihood-ratio values are configuration-visible and marked `UNCALIBRATED_LIKELIHOOD_PRIORS`; they are not claimed as historical frequencies. The architecture is intended for later Brier/reliability/workload closure calibration without changing the downstream MC state model.

The default predictive MC sample count is now **16,384**. The GUI retains 1,024 / 4,096 / 16,384 / 65,536 choices and the fixed6 memory-release behavior for large-N opponent-reference construction.

## v0.26-fixed6: opponent diagnosis and bounded large-N opponent memory

The compressed chat diagnosis now contains an `OPPONENT LINEUP` section using the same `build_weekly_yield_state`, `availability_state_model`, `player_lock_timing`, and `optimize_lineup` path as the user lineup. For each planned opponent starter it exposes operational mean/SD, K, defensive opponent, P(active), P(full|active), FULL/LIMITED/OUT probabilities, status, lock group, kickoff, and reveal time. Opponent key-uncertainty and ESPN-anchor sections are generated through the same `player_diagnostic` service method. The GUI opponent card likewise surfaces matchup and availability coordinates directly.

A `PREDICTION PIPELINE SYMMETRY` report section explicitly records the shared yield/availability/timing/lineup components, making future accidental user/opponent divergence easier to detect.

Large-N performance is also tightened without changing any sampled universe. Each player-keyed predictive stream is a deterministic function of seed, player id, and N. During whole-league opponent-reference construction, fixed5 retained five large RNG caches for every opponent player after that team had already been accumulated. At N=65,536 this can create multi-gigabyte memory pressure and Windows paging. fixed6 releases those opponent-only streams at each team boundary; if regenerated later they are bitwise identical. Only the current-week vector of the actual opponent is retained for the Week 1 override rather than an unnecessary N x 17 copy.

The fixed5 lazy opponent-reference construction, fast N reset, visible progress/ETA, no-duplicate-opponent simulation, stochastic seeds, common-random-number pairing, availability/workload model, lock-aware policy, and read-only ESPN boundary are otherwise unchanged.

## v0.26-fixed5: visible opponent-reference MC and fast N reset

Changing the MC-universe count no longer calls a full `SeasonGuiService.reload()`. The existing static snapshot, league configuration, enriched players, availability states, and lock timing are retained. Only arrays/caches whose shape depends on predictive N are cleared and regenerated.

The predictive opponent reference is built lazily as the first explicit dashboard MC phase, so progress reports opponent-reference team/week work before the realistic / ideal-active / ideal-full policy passes. The league-reference builder accumulates team simulations in place and reuses the already-simulated actual weekly opponent instead of simulating it a second time.

The stochastic seeds, common-random-number pairing, MC batching, availability/workload model, lock-aware policy, and read-only ESPN boundary remained unchanged.

## v0.26-fixed4: reliable MC click acknowledgement and background launch

The MC-universe selector is now intentionally two-step:

1. choose **1,024 / 4,096 / 16,384 / 65,536** universes;
2. press **Run selected MC**.

The selector still uses plain formatted string options. Pressing **Run selected MC** now executes a synchronous click handler which immediately changes the persistent status panel to `MC REQUEST RECEIVED`, disables only the selector/run pair for that accepted request, and schedules the expensive async rebuild with NiceGUI `background_tasks`. The context-rebuild phase is itself shown before the policy MC begins. This removes the interval in which a valid click could look like a dead button while `SeasonGuiService.set_mc_scenarios` was rebuilding the deterministic context.

The generic MC-progress lockout no longer owns the selector or Run button, avoiding stale disabled state after a long startup run. Attempts made while another run is active receive an explicit visible message. GUI-event exceptions are also routed to the persistent MC status panel via `ui.on_exception`, rather than being visible only in server logs.

**Recompute Dashboard** retains the v0.26-fixed3 same-N cache invalidation behavior.

The stochastic model, seeds, common-random-number pairing, batching, availability/workload model, lock-aware policy, and read-only ESPN boundary are unchanged.

## v0.26-fixed2: connection-safe GUI initialization

The first-load dashboard no longer depends on a one-shot `ui.timer`. The page is built first, then waits for `client.connected()` before starting the long dashboard evaluation. MC progress is refreshed by an asyncio progress pump while the worker thread only updates numeric progress state.

This fixes the failure mode where the browser displayed a complete shell with blank cards while the literal startup labels remained stuck at `MC ready` / `No Monte Carlo job running`. A persistent **Recompute Dashboard** button is also available, and refresh failures are left visible in the MC status panel rather than being shown only as a transient notification.

The stochastic model, MC sample count, deterministic seeds, batching, lock-aware policy, and read-only ESPN boundary are unchanged from v0.26-fixed.

## v0.26-fixed: large-MC execution and GUI run state

The predictive MC default is now **4,096 universes**. The season GUI exposes selectable run sizes of **1,024 / 4,096 / 16,384 / 65,536** universes. The selection is in-memory for the current process and does not rewrite `config/model.json`. CLI overrides are also available:

```powershell
python fantasy.py gui --mc 16384
python fantasy.py chat-report --mc 16384
```

Long MC jobs run through NiceGUI's background I/O worker so the interface remains responsive. A persistent status panel shows:

- a prominent `MONTE CARLO RUNNING` state and spinner;
- configured universe count `N`;
- percent completion;
- current policy/week phase;
- completed/total scenario-week work units;
- elapsed wall-clock time;
- a completed/failed state before controls are unlocked.

MC-invalidating controls are temporarily disabled while a run is active. Results update only after the requested calculation finishes.

The core scenario loops are processed in deterministic index batches (default batch size 512). **Batch size does not alter the random streams or universe contents**: all player-keyed random arrays and common-random-number pairing are generated exactly as before, and batching only partitions the existing scenario-index loop for progress reporting. A regression test verifies batch-size invariance.

The GUI and chat report retain the exact MC count used. `chat-report` accepts `--mc` for high-statistics diagnostic runs outside the GUI.

## v0.26: realistic information flow and workload states

The dashboard and chat diagnosis now expose four distinct policy coordinates:

```text
Fixed lineup
    Exact nine selected starters; no substitutions.

Realistic lock-aware policy
    Sequential kickoff locks. Uses only status information available by each decision time.
    Active/inactive is revealed at the modeled inactive deadline.
    FULL versus LIMITED remains latent.

Idealized-active policy
    All active/inactive outcomes are known before the first lock.
    FULL versus LIMITED remains latent.

Idealized-full policy
    Upper bound in which the complete OUT/FULL/LIMITED branch is known before any game locks.
```

This produces a sequential, order-dependent diagnostic decomposition:

\[
\Delta P_{status\ timing}=P_{win}^{idealized\ active}-P_{win}^{realistic},
\]

\[
\Delta P_{workload\ info}=P_{win}^{idealized\ full}-P_{win}^{idealized\ active},
\]

and therefore

\[
\Delta P_{total\ idealized\ info}=P_{win}^{idealized\ full}-P_{win}^{realistic}.
\]

The two components sum algebraically in this chosen order, but they are not claimed to be a unique causal/Shapley attribution because timing, redundancy, and slot flexibility interact.

The realistic backup-policy value is:

\[
\Delta P_{backup}^{real}=P_{win}^{realistic}-P_{win}^{fixed}.
\]

The report labels the status/workload split as **sequential and order-dependent** rather than pretending inactive coverage, FLEX optionality, redundancy, and late-swap timing have a unique additive decomposition. Those effects can interact.

Each current-week player diagnostic now retains:

- `P(active)`;
- `P(full | active)`;
- implied `P(FULL)`, `P(LIMITED)`, and `P(OUT)`;
- limited-workload fraction;
- kickoff time;
- inactive-reveal time;
- lock group/window;
- timing provenance.

If nflverse kickoff timing is unavailable, v0.26 does **not** invent a game window. It falls back to pre-lock active/inactive knowledge while keeping FULL/LIMITED workload latent for that evaluation and surfaces the timing fallback in dashboard/chat diagnostics.

The first v0.26 timing layer does not synthesize unobserved Friday/Saturday practice-report transitions. It conditions on the availability posterior present in the snapshot and models the final game-day active/inactive reveal at the configured inactive deadline. Future calibration can add explicit intermediate information states without changing the lock-policy interface.

## v0.25-fixed: compressed chat diagnosis

Numerical/model debugging no longer requires screenshots. Generate the exact same service-layer state used by the GUI with:

```powershell
python fantasy.py chat-report
```

The command prints a compact paste-friendly diagnosis and writes immutable copies to:

```text
data/chat_reports/chat_report_<timestamp>.txt
data/chat_reports/chat_report_<timestamp>.json
```

The GUI header also includes **Chat Diagnosis**. It captures the current lineup-laboratory selection and availability modes; if the currently selected ADD/DROP pair has already been evaluated, that paired-MC result is included too. The report is displayed in a read-only text area, printed to the terminal, and saved locally.

The report contains the matchup policy/fixed win probabilities, score distributions, nine-player planning lineup, K and availability states, uncertainty leaders, model-vs-ESPN anchor outliers, optional hypothetical changes, optional selected add/drop result, closure coverage, model flags, and source health.

The implementation invariant is:

```text
GUI display ----┐
chat-report ----┼── SeasonGuiService ── commissioned model/MC
CLI diagnostics ┘
```

No separate chat-only optimizer or projection calculation is introduced.

## v0.25 changes

### 1. Fixed-lineup vs contingent-policy distinction

The weekly dashboard and Lineup Laboratory now explicitly separate two different questions that were visually conflated in v0.24:

```text
Fixed lineup
    The exact nine pregame starters are held fixed.
    If one is inactive, that slot scores zero unless you manually choose another player.

Contingent policy
    The season model branches on availability and re-optimizes the legal lineup
    after the active/inactive state is known.
```

This is why a default fixed lineup can have a lower win probability than the top-dashboard policy result even though the displayed starters are identical.

The GUI now reports:

- selected fixed-lineup win probability;
- default fixed-lineup win probability;
- contingent-policy win probability;
- delta from the selected lineup/scenario relative to the default fixed lineup;
- explicit **backup-policy value**:

\[
\Delta P_{backup}=P(\text{win}|\text{contingent policy})-P(\text{win}|\text{default fixed lineup}).
\]

The Lineup Laboratory also shows a nine-slot comparison table so lineup and availability changes are visible directly.

### 2. Matchup-driver view

The Weekly Matchup page now includes a starter-by-starter diagnostic:

\[
\Delta Y_{slot}=Y_{us,slot}-Y_{opp,slot}.
\]

This is not a replacement for the full MC. It is a readable diagnostic showing where the conditional pregame projection edge or deficit is coming from by QB/RB/WR/TE/FLEX/K/DST slot.

The top win card is now labeled as the **contingent-policy MC** and also displays the fixed-lineup win probability and the value of backup flexibility when available.

### 3. Expanded player diagnostics

The Player Diagnostics view keeps the v0.23 prediction chain:

\[
\mathcal{L},\sigma \rightarrow K \rightarrow Y_{model} \leftrightarrow Y_{ESPN} \rightarrow Y_{operational}.
\]

It now exposes the chain more directly through metric cards and separate charts for:

- base model mean;
- K-adjusted model mean;
- ESPN external anchor;
- operational prediction;
- K and K uncertainty;
- model-minus-ESPN residual and anchor z-score;
- game/model/kinematic uncertainty components;
- largest matchup-coordinate contributions and their z-scores;
- DST component expectations when applicable.

This preserves the data/MC and acceptance/kinematics interpretation rather than reducing the player to one fantasy-point number.

### 4. Richer FA/waiver experiments

A selected `ADD X / DROP Y` still uses exactly the same paired predictive MC as the CLI.

v0.25 adds absolute HOLD-vs-action context in addition to the deltas:

- HOLD current-week score distribution;
- action current-week score distribution;
- HOLD and action absolute season utility;
- paired utility-delta distribution;
- P(+), P(0), P(-);
- acquisition probability kept separate;
- week/season/insurance/bye-floor deltas.

The GUI therefore shows whether an apparently positive action actually moves the team-score distribution in a meaningful way.

### 5. Data/MC dashboard

The Data / MC page is no longer table-only.

Before observed games are available, it provides pregame closure diagnostics:

- base model vs ESPN anchor scatter with a 1:1 reference;
- ranked model-minus-ESPN residuals;
- ESPN-anchor coverage;
- mean and maximum absolute model/ESPN discrepancy.

Once supported observed fantasy data are present, the residual chart automatically switches to:

\[
Y_{data}-Y_{MC},
\]

and the page reports observed-data coverage and Data/MC RMSE.

The prediction ledger remains available underneath the charts.

## Existing v0.24 functionality retained

### Weekly matchup

- planning lineup;
- opponent planning lineup;
- our score MC;
- opponent score MC;
- margin MC;
- source health;
- snapshot timestamp.

### Lineup Laboratory

All nine legal slots are selectable:

```text
QB
RB1
RB2
WR1
WR2
TE
FLEX
K
DST
```

Each selected player supports local availability modes:

```text
MODEL
FULL
LIMITED
OUT
```

`LIMITED` remains a user-specified workload scaling scenario, not an inferred workload posterior.

### FA / waivers

The searchable actionable ESPN pool shows:

- player/position/team;
- ESPN fantasy status;
- operational mean and predictive SD;
- ESPN anchor;
- K/opponent;
- Sleeper adds/24h when available.

### Refresh Data

The header button invokes the existing low-frequency `season-sync` pipeline and reloads the new snapshot. It does not bypass the normal source hierarchy.

## Read-only league safety boundary

v0.30 may:

- read local snapshots;
- refresh the normal season snapshot;
- run predictive MC;
- evaluate local lineup scenarios;
- evaluate local add/drop counterfactuals;
- display model/ESPN/data closure diagnostics.

v0.30 does **not**:

```text
change an ESPN lineup
submit a free-agent acquisition
submit a waiver claim
submit/cancel a trade
write any league action to ESPN
```

## Data authority

Unchanged:

```text
Fantasy league state        -> ESPN
Official NFL status         -> NFL.com
Structured metadata         -> Sleeper
Stats / usage / performance -> nflverse
Context / breaking reports  -> public web/news
```

ESPN weekly projections remain an external predicted-yield anchor at ESPN's implicit acceptance point; they are not treated as truth and the v0.23 K correction is not double-counted onto an already weekly ESPN anchor.

## Migration from v0.30-fixed6

v0.31 adds no credentials and requires no new source download. Copy the current fixed6 data directory so snapshots, commissioned interaction grids, closure state and local decisions remain available.

```powershell
cd L:\Projects\fantasy_football

Copy-Item .\fantasy_season_v0_30_fixed6\data\* `
    .\fantasy_season_v0_31\data -Recurse -Force

cd .\fantasy_season_v0_31

pytest -q

python fantasy.py season-sync
python fantasy.py roster-actions
python fantasy.py defense-channel
python fantasy.py kicker-channel
python fantasy.py gui
```

## Validation target

The package test suite includes invariants for:

- GUI/core baseline consistency;
- fixed-lineup vs realistic vs idealized-active vs idealized-full policy separation;
- no-hindsight lineup sampling;
- OUT / ACTIVE_LIMITED / ACTIVE_FULL probability separation;
- nflverse kickoff/reveal-time parsing;
- sequential lock-aware information flow;
- preservation of already-locked starters/bench state from the snapshot;
- score-neutral FLEX tie-breaking that keeps late-swap eligibility open when legal;
- regression that removes timing advantage when candidate players share a lock window;
- position legality and duplicate-player rejection;
- paired add/drop MC;
- absolute HOLD/action distributions;
- player diagnostics;
- Data/MC summary calculations;
- EChart options serialization and in-place NiceGUI refresh behavior;
- explicit Run selected MC control, same-N cache invalidation, and true dashboard recomputation;
- lazy predictive-opponent construction, in-place N resize, visible opponent-reference progress, and no duplicate actual-opponent simulation;
- deterministic release/regeneration of opponent-only predictive RNG streams after each team is accumulated;
- chat-report opponent lineup, opponent uncertainty/anchor diagnostics, and explicit shared-pipeline metadata.
- v0.29 immutable pregame closure capture for user and opponent players;
- latest-valid-prekickoff capture selection with post-lock captures excluded from prospective closure;
- nflverse postgame component mapping and league scoring response;
- availability-marginal fantasy-yield and opportunity-count closure;
- missing stat rows do not become inactive truth;
- Base-MC vs interaction-corrected RMSE and pull-calibration summaries;
- GUI prospective component-closure and Capture Pregame State wiring.
- v0.28 grid interpolation, unit-correction fallback, and separate interaction uncertainty coordinate;
- offline interaction artifact schema with `fantasy_points_used_in_fit=false`;
- chronological component commissioning metadata and neutralization of uncommissioned grids;
- base-MC versus interaction-corrected closure coordinates.

v0.28 preserves the commissioned v0.23/v0.27 base predictive model and v0.26 lock-aware decision-information layer while adding a separately fitted higher-order interaction correction. The base K path remains visible and is the exact fallback when no commissioned grid is available. Trade and waiver market-decision expansion is implemented in v0.30; the v0.28 interaction model itself remains unchanged.
