# Week 3 Prospective Trade Search — 2026-09-24

## Purpose

Run the first league-wide trade search only after a fresh decision-time state is
captured prospectively, then preserve the result without hindsight mutation.

## Prospective State

Runtime:

`L:\Projects\fantasy_football\fantasy_season_v0_36_repack1`

Fresh snapshot:

- UTC: `2026-09-24T07:02:04.247873+00:00`;
- path:
  `data/season_snapshots/20260924T070144Z/snapshot.json`;
- SHA-256:
  `3a300ecd1971795888847d7fada1f2702f9e5afd1d3e7640d17ca3cbc081cd38`;
- season/week: `2026 / 3`;
- ESPN, NFL official, NFL official rosters, nflverse matchups,
  nflverse rosters, and Sleeper all reported successful source status.

Fresh immutable prospective capture:

- path:
  `data/season_predictions/closure/pregame_2026_w03_20260924T070228Z.json`;
- SHA-256:
  `5b05e1cd0e62b74df8a3a68b66c41dbc3dfb6be0e40cd424d3d161d891cd8bda`;
- contract:
  `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- integrity: **PASS**;
- league players: `174`;
- specialist records: `64` (`32` DST, `32` K);
- behavior teams: `12`;
- market players: `846`.

Decision-time roster uncertainties below 95% active probability:

- Puka Nacua — QUESTIONABLE, ESPN, `P(active)=75%`;
- Josh Jacobs — EXEMPT, NFL official roster, `P(active)=0%`;
- Jakobi Meyers — QUESTIONABLE, Sleeper+ESPN, `P(active)=75%`;
- J.K. Dobbins — QUESTIONABLE, Sleeper+ESPN, `P(active)=75%`.

## Trade Search

Scope:

- existing `search_trades`;
- player channel only;
- league-wide one-for-one screen;
- predictive MC authority after the cheap screen;
- `4096` scenarios per evaluated candidate;
- manager response:
  `UNCALIBRATED_TRADE_RESPONSE_V030`;
- no transaction execution.

Recovered ranked results:

| Rank | Offer | Our delta | P(better) | Partner delta | P(accept) | Offer EV | Classification |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Andrews -> Matthew Golden | +0.104 | 51.5% | -0.490 | 8.0% | +0.008 | OUR_EDGE_PARTNER_LOSS |
| 2 | Kittle -> Emeka Egbuka | +0.196 | 52.1% | -1.387 | 1.3% | +0.003 | OUR_EDGE_PARTNER_LOSS |
| 3 | Kittle -> Quinshon Judkins | -0.706 | 42.2% | -2.693 | 0.1% | ~0.000 | NO_RESOLVED_EDGE |
| 4 | Kittle -> Bucky Irving | -0.725 | 40.4% | -1.485 | 0.1% | -0.001 | NO_RESOLVED_EDGE |
| 5 | Kittle -> Travis Etienne Jr. | -0.943 | 39.5% | -2.126 | 0.3% | -0.003 | NO_RESOLVED_EDGE |
| 6 | Andrews -> Rachaad White | -0.040 | 49.7% | -0.445 | 12.0% | -0.005 | NO_RESOLVED_EDGE |

## Scientific Classification

**NO ACTION / HOLD.**

The two positive-mean candidates are weak, near-coin-flip improvements for our
roster and modeled as meaningful losses for the partner, producing low
uncalibrated acceptance probabilities.

The remaining four candidates are negative for our roster.

Several candidates looked favorable under the cheap screen but became negative
under predictive MC. This is direct prospective evidence for the architectural
boundary:

`screen != authority`

The screen generated a frontier; uncertainty-aware predictive MC authorized the
football decision.

## Renderer-Only Recovery

The first decision audit was written with missing partner/give/receive identities
because the package serializer expected nested objects while `search_trades`
returns flat fields:

- `partner_team_id`, `partner_name`;
- `give_id`, `give_name`, `give_position`;
- `receive_id`, `receive_name`, `receive_position`.

The football/model result was not affected.

Original decision audit:

- path:
  `data/season_decisions/prospective_trade_search_2026_w03_20260924T071514Z.json`;
- SHA-256:
  `8c4e4a635522936ae4a4ebdc2a60370d57904a547959de539a66f2f7e2c3ed6f`.

A diagnostic replay was bound to the exact frozen snapshot/capture and required
all six scalar result vectors to reproduce within `1e-12`.

Result:

- scalar reproduction: **PASS (6/6)**;
- frozen snapshot unchanged;
- frozen capture unchanged;
- original audit unchanged;
- identities recovered;
- corrected audit written separately.

Corrected audit:

- path:
  `data/season_decisions/prospective_trade_search_identity_recovery_2026_w03_20260924T141743Z.json`;
- SHA-256:
  `9eaafcfe4bb7e003f5622a5d8c901c286b7ddcb9139a82cd898a7ccbd1259e32`.

Classification:

`RENDERER_SCHEMA_DEFECT_ONLY`

No application/model source change is required from this package-only defect.

## Decision Boundary

No trade was submitted.

The Sep 24 frozen trade-search state is prospective evidence, not a reusable
later decision state.

Next gate:

- wait for material Week 3 availability/practice information or a relevant
  lineup lock;
- on material change, fresh sync -> fresh capture -> decision;
- do not rerun or reinterpret this trade search as if it were fresh.
