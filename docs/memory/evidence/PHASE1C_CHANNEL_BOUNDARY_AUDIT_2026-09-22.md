# Phase 1C Channel-Boundary Audit — 2026-09-22

## Authority

Read-only repository authority:

`340a2b87a5e4b3fc5c04848dff1db03280f148c7`

Tree:

`dd6d4d07a66a1e8774ccb803e148bcd7162fb501`

This audit follows Phase 1B closure-shadow runtime commissioning.

No production source, runtime source, model configuration, persistent sink, Git
index/history, or remote state was modified by the audit.

## Question

What is the narrowest existing production observability boundary for each
separate `P ⊕ D ⊕ K` channel?

The audit is architectural and source-based. It does not authorize a combined
P/D/K patch.

## Existing Integration Map

`src/observability/integration_plan.py` proposes:

- `subsystem.player.predictive`
  -> `src/transaction_manager.py::evaluate_roster_predictive`;
- `subsystem.dst.channel`
  -> `src/specialist_policy_v032.py::evaluate_defense_channel`;
- `subsystem.k.channel`
  -> `src/specialist_policy_v032.py::evaluate_kicker_channel`.

The map is a proposed shadow-integration surface; exact current source remains
the authority for whether each point is semantically valid.

## Player Audit

The planned player point is rejected as a **player-only** boundary.

Direct source evidence:

1. `transaction_manager.py` defines complete roster positions including
   `QB`, `RB`, `WR`, `TE`, `K`, and `DST`.
2. Production predictive action evaluation calls:
   - `evaluate_roster_predictive(ctx.roster, ctx, ...)`;
   - `evaluate_roster_predictive(row["new_roster"], ctx, ...)`.
3. The underlying predictive roster simulation explicitly has a DST component
   branch using `simulate_dst_component_points`.

Therefore `evaluate_roster_predictive` represents complete-roster predictive
utility/response rather than a pure `P = QB/RB/WR/TE` sector.

Classification:

`PLANNED_PLAYER_INTEGRATION_POINT_REJECTED_AS_CHANNEL_BOUNDARY`

It may remain a valid future complete-roster utility observability surface, but
it must not be labeled or used as a player-only Phase 1C channel observer.

No player source instrumentation is authorized until a narrower player-only
production boundary is established.

## DST Audit

Current public policy wrapper:

`src/specialist_policy_v032.py::evaluate_defense_channel`

The wrapper is:

`return _evaluate_policy_channel(..., position="DST", ...)`

The specialist machinery restricts the working specialist position and performs
same-channel candidate/configuration comparisons. The lower specialist channel
also states explicitly that a specialist is not compared directly with
QB/RB/WR/TE assets.

Cross-channel effects that do exist are complete-roster utility/state response
terms, which are the permitted coupling boundary under `P ⊕ D ⊕ K`.

Classification:

`DST_OUTER_CHANNEL_BOUNDARY_ACCEPTED`

Proposed observability namespace:

`subsystem.dst.channel`

## Kicker Audit

Current public policy wrapper:

`src/specialist_policy_v032.py::evaluate_kicker_channel`

The wrapper is:

`return _evaluate_policy_channel(..., position="K", ...)`

The same specialist policy machinery remains position-scoped.

Classification:

`K_OUTER_CHANNEL_BOUNDARY_ACCEPTED`

Proposed observability namespace:

`subsystem.k.channel`

## First Phase 1C Slice

DST is selected before K for the first targeted preflight.

Reason:

- the architecture requires DST closure at explicit component level:
  sacks, interceptions, fumble recoveries, defensive TDs, points allowed, yards
  allowed, and fantasy scoring response;
- current DST predictive machinery already carries component expectations;
- this creates a clearer physical/diagnostic contract than the current K model;
- the kicker representation is intentionally simpler aggregate yield plus team
  scoring environment pending prospective K closure.

This selection is a sequencing decision, not a ranking of cross-channel fantasy
value.

## DST Preflight Contract

The next step is diagnostic only. It must not modify production source.

Boundary:

`src/specialist_policy_v032.py::evaluate_defense_channel`

Namespace:

`subsystem.dst.channel`

Required properties:

- subsystem is `dst`;
- bounded in-memory observer only;
- no automatic persistence;
- no function arguments retained;
- no returned report payload retained;
- no authenticated/private input retained;
- no exception message retained;
- result and exception semantics identical to direct call;
- observer failure cannot suppress/replace the production result;
- Python/NumPy stochastic state and relevant mutable state are paired and
  unchanged by observation;
- paired overhead measured through the existing benchmark gate.

K and player instrumentation remain outside this preflight.

## Result

`PHASE1C_CHANNEL_BOUNDARY_AUDIT=COMPLETE`

Next classification target:

`PHASE1C_DST_TARGETED_PREFLIGHT`
