# Phase 1D Market / Manager-Behavior Boundary Discovery — 2026-09-23

## Purpose

Classify the existing trade-search path into intrinsic football/roster response,
manager perception, manager behavior, and mixed orchestration before any Phase 1D
production instrumentation.

This is a read-only source audit. It changes no football/model/application source,
does not enable persistence, and does not tune any manager-response parameter.

## User Direction and Operational Context

After the Week 3 Wednesday decision checkpoint:

- waiver/free-agent QB/RB/WR/TE search is considered complete for that frozen
  state and the accepted result is HOLD;
- the Week 3 league-wide trade search was not run;
- trade search may be deferred this week because it is a more complex decision
  surface;
- preferred operational target is to have trade search validated/ready before the
  Week 4 decision window;
- Phase 1D may proceed between Week 3 prospective calendar gates;
- current MC architecture is recognized as materially evolved from preseason and
  state-aware, while observed Weeks 1-2 2026 outcomes have **not** empirically
  tuned v0.X.

The Week 4 trade-search target does not supersede prospective Week 3 injury/status
capture obligations.

## Authority

Repository checkpoint inspected:
`979727acdedbf7502471450c6b3704686ec9a202`.

Exact source identities:

- `src/market_manager.py`:
  `4ffa2f9ead68c9933dd6d1ab06deb425b4a17278`;
- `src/observability/integration_plan.py`:
  `c8ef2dbcf8a9e30bf3f77497f270c4bb8fbedcbd`;
- `src/observability/registry.py`:
  `910f92bef0c998420cd4fefe1921ab831414fb41`;
- `tests/test_market_manager_v030.py`:
  `1dcd38be513c588c6c374b40516e2fdc4e90bc7c`.

The integration plan currently proposes:

`subsystem.trade.search -> src/market_manager.py::search_trades`

as a shadow/non-persistent integration point. That proposal is a discovery lead,
not an accepted behavior boundary.

## Source Classification

### Football / roster response

`evaluate_roster_season_scenarios`

- calls the predictive weekly-player simulation machinery;
- evaluates remaining-season roster scoring;
- preserves player-keyed common-random-number structure;
- is football/roster response, not manager behavior.

Roster legality and trade-package transition helpers:

- `roster_is_legal`;
- `_best_auto_drops`;
- `_best_auto_fills`;
- `apply_trade_package`.

These represent legal roster-state transitions and football utility consequences.

Trade candidate screening:

- `_need_multiplier`;
- `_coarse_trade_score`;
- `screen_one_for_one_trades`.

This is a cheap football/roster screen used to choose candidates for full
predictive evaluation. It is not recommendation authority.

### Manager perception / market feature

`_espn_market_ppg`

selects the public projection input used by the perception feature.

`perceived_market_value`

is explicitly separate from roster utility. It combines:

- ESPN projected production;
- position-relative replacement surplus;
- public ownership;
- Sleeper add/drop trend;
- configured market-perception weights.

It is a manager-perception/market feature. It must not change intrinsic football
value.

### Manager behavior

`trade_response_probabilities`

is the narrow response kernel.

Inputs:

- partner predictive season-PPG delta;
- partner probability of being better;
- partner market-perception delta;
- package size;
- manager-behavior configuration.

Output:

- `p_accept`;
- `p_counter`;
- `p_reject`;
- model identity `UNCALIBRATED_TRADE_RESPONSE_V030`.

The function does not run football simulation and is the narrowest shared
manager-response surface beneath both manual trade evaluation and automatic trade
search.

### Mixed complete trade response

`evaluate_trade`

combines:

1. both managers' baseline/after predictive roster MC;
2. paired football deltas for both managers;
3. post-trade legal releases/fills;
4. partner market-perception delta;
5. `trade_response_probabilities`;
6. `expected_offer_value = p_accept * mean(user_delta)`;
7. a classification that may use the behavior probability threshold.

It is therefore a mixed complete trade-response surface, not a behavior-only
boundary.

### Mixed orchestration

`search_trades`

combines:

1. `screen_one_for_one_trades`;
2. full `evaluate_trade` calls for the screened frontier;
3. football and partner-response summaries;
4. sorting by expected offer value and our football delta.

Classification:

`search_trades = MIXED ORCHESTRATION / REJECT AS BEHAVIOR-ONLY BOUNDARY`

## Call-Site Coverage

CLI:

- `cmd_trade_search` invokes `search_trades`;
- CLI output identifies the automatic search as player-channel, one-for-one;
- manual `trade-eval` remains a separate path.

GUI/service:

- `SeasonGuiService.trade_search_screen` invokes
  `screen_one_for_one_trades`;
- `SeasonGuiService.trade_search` invokes `search_trades`;
- GUI/manual trade evaluation uses the same market-manager module.

Because `search_trades` reaches `trade_response_probabilities` through
`evaluate_trade`, the narrow behavior kernel is shared by automatic and manual
trade evaluation.

## Existing Tests

`tests/test_market_manager_v030.py` already verifies, among other behaviors:

- accept/counter/reject form a three-way probability and identify the response
  model as uncalibrated;
- `evaluate_trade` values both managers and keeps response probability separate;
- league-wide screening sees all partner rosters;
- a trade-search MC override does not mutate the primary model;
- unequal packages surface modeled legal releases/fills;
- CLI trade commands exist;
- default transaction MC remains 16,384.

These tests establish functional lineage. They do not substitute for a Phase 1D
observability non-interference/overhead probe.

## Phase 1D Boundary Decision

Accepted discovery classification:

`PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY = COMPLETE`

Rejected as behavior-only boundary:

`src/market_manager.py::search_trades`

Also mixed, not behavior-only:

`src/market_manager.py::evaluate_trade`

Preferred first behavior shadow candidate:

`src/market_manager.py::trade_response_probabilities`

Deferred possible second observation surface:

`src/market_manager.py::perceived_market_value`

The observability subsystem already has both `trade` and `behavior` namespaces.
For the narrow response kernel, `behavior` is the semantically correct subsystem;
trade orchestration can remain separately classified.

## Why the Narrow Kernel Is Preferred

The scientific boundary is:

`football state/response -> perceived manager state -> manager response`

rather than one monolithic trade score.

Observing `trade_response_probabilities` preserves that separation:

- intrinsic player/roster value remains upstream;
- ownership/trend/perception remains a behavior feature;
- accept/counter/reject is the behavioral response;
- recommendation/search orchestration remains downstream.

Instrumenting `search_trades` as if it were manager behavior would erase these
distinctions.

## Next Probe

Before any source instrumentation, run one non-modifying paired probe around
`trade_response_probabilities` from the exact current source.

Required measurements:

- return-value equivalence;
- exception-type equivalence;
- Python RNG equivalence;
- NumPy RNG equivalence;
- mutable-state equivalence;
- privacy/correlation payload contract;
- absolute and relative overhead.

The kernel is small and fast, so absolute overhead must be inspected alongside
relative overhead. A large percentage overhead on a microsecond-scale function is
not by itself enough to classify the boundary as operationally unacceptable.

No production source is to be changed by the probe.

## Trade-Search Readiness Before Week 4

The automatic trade search is functionally present, but operational readiness has
one known dependency issue:

- `trade-search` defaults to `data/processed/player_values_2026.csv`;
- the commissioned `v0.36-repack1` runtime was observed during Week 3 recovery to
  lack that default artifact;
- an exact predecessor player-values artifact was recovered for Wednesday
  diagnostics, but that one-off recovery is not a permanent runtime dependency
  contract.

Before the Week 4 trade-search target is declared ready, explicitly validate or
repair/reroute that dependency through a separate operational checkpoint.

This readiness work must remain separate from Phase 1D behavior instrumentation
and from any empirical v0.X retuning.

## Scientific Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Trade assets in this channel remain QB/RB/WR/TE only; DST/K belong to their
  specialist channels.
- `screen != authority`.
- Manager perception and manager response remain separate from intrinsic football
  utility.
- The response model is explicitly uncalibrated.
- No observed 2026 outcome may tune v0.X.
- Persistent observability remains separately gated.
