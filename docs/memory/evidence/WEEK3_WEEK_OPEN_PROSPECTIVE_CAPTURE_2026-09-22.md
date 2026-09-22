# Week 3 Week-Open Prospective Capture — 2026-09-22

## Classification

`PROSPECTIVE_WEEK_OPEN_CAPTURE_VALID`

The first future hard Week 3 week-open capture gate was secured before the first
Week 3 NFL game.

## Execution Boundary

Diagnostic package:
`week3_week_open_capture_20260922_v1`.

Executed through the repository generic `.ffpkg` runner.

Delivered carrier SHA-256:
`53ee4786fc8075e063e4073ce11099390f13e2355ad9c09f7672854e294d15b3`.

Executed embedded archive:
- bytes: `6098`;
- SHA-256:
  `6025baa2ce976b63af30ba52c1651855cc4eb69d41d769f9a3cbe90e316e16b7`.

Commissioned runtime:
`v0.36-repack1`, internal/runtime/model version `0.36`.

Measurement contract:
`A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`.

## Prospective Timing

- snapshot UTC: `2026-09-22T14:10:51.714616Z`;
- capture UTC: `2026-09-22T14:10:53.254794Z`;
- capture-gate deadline UTC: `2026-09-25T00:15:00Z`.

Both snapshot and prediction capture precede the deadline.

## Sanitized Measurement Summary

- matchup player records: `32`;
- all-league rostered QB/RB/WR/TE predictions: `174`;
- specialist predictions: `64`;
- DST predictions: `32`;
- kicker predictions: `32`;
- behavior teams: `12`;
- market players: `846`;
- temporal player-state predicted transactions: `0`;
- bounded league-response cascade:
  `PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE`;
- cascade max depth: `3`;
- cascade scenarios: `64`.

Source status:
- ESPN: OK;
- Sleeper: OK;
- nflverse rosters: OK;
- nflverse matchups: OK;
- NFL.com team rosters: OK;
- NFL.com status: OK;
- degraded sources: NONE.

## Integrity / Provenance

- capture integrity: PASS;
- pre-data firewall: PASS;
- snapshot canonical SHA-256:
  `fc15f5773710debebceb2d1ee24a76baa3e8190fd396288b3c4b441120b97526`;
- snapshot file SHA-256:
  `8fcd03841a65cd76f3afbc04e1cb40ec16034b8d0e988467a9c24d6b2da7acde`;
- model-config SHA-256:
  `fa963697ba61e9662e5d44b5bbdaf5140d15e894b56b1a8cc84a160e85b0358c`;
- league-config SHA-256:
  `d340d9dd76cc9b472037c7eb1af88ce56b323bfbdaa07e9c42507ce2443d726a`;
- capture file SHA-256:
  `82ee7e89a328930931aa88d9a0af4b5217586cbe4792d50b7b384fcf71125154`;
- canonical capture payload SHA-256:
  `953beecee15d05d62c27fa8ef2394f515f179913ec3bbbf0d9885528b31d5e11`.

The timestamped local capture basename is
`pregame_2026_w03_20260922T141055Z.json`.

## Privacy / Scientific Boundary

Authenticated/raw snapshot and capture contents remain local.

The diagnostic package reported:
- persistent runtime sink: false;
- repository write: false;
- runtime source write: false;
- evidence artifacts preserved: true.

The capture does not authorize hindsight tuning. The v0.X model remains a-priori,
and observed 2026 outcomes may inform only the separately gated v1.X evidence and
calibration process.

## Frontier Transition

The Week 3 week-open hard calendar gate is secured.

Phase 1B closure instrumentation may resume from its retained
preflight-validated candidate. Already-passed Phase 1B gates remain valid unless
new evidence invalidates them.
