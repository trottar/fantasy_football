# Week 3 Phase-B Outcome Authority V002 Correction — 2026-10-07

## Purpose

Correct the scope classification of Week 3 Phase-B outcome authority before
scorer implementation. V001 remains immutable predecessor evidence; Phase A is
unchanged.

## Trigger and Classification

A scorer-sufficiency probe found D/ST realized-point gaps despite V001 claiming
`144 / 144` candidate coverage. Inspection showed the V001 collector retained
only IDs `> 0`, excluding negative synthetic D/ST IDs.

A read-only authenticated ESPN probe then tested every negative Phase-A asset ID:

- signed Phase-A asset IDs: `172`;
- positive IDs: `144`;
- negative D/ST IDs: `28`;
- ESPN returned all `28 / 28`;
- exact Week 3 actuals: `28 / 28`;
- D/ST position shape: `28 / 28`;
- pro-team mapping: `28 / 28`;
- `kona_playercard` supplied the exact Week 3 actuals.

Classification:
`DIRECT_ESPN_DST_AUTHORITY_COMPLETE / V001_CAPTURE_CLASSIFICATION_DEFECT_CONFIRMED`.

## V002 Authority

Contract: `WEEK3_PHASE_B_OUTCOME_AUTHORITY_V002`

Local-only directory:
`data/historical_replay/phase_b/outcome_authority/2026_w03/v002`

V002 manifest SHA-256:
`00946e70c53cfd3eeab74c74b2397a196c514ab75ac437246079b6f6383ab4db`

V001 predecessor manifest SHA-256:
`892763082b1a03e5f9789c31e7c2961692392e027413611403ffa7e93649fd11`

Phase-A receipt-set SHA-256:
`54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`

V002 copies all five V001 artifacts byte-exact and adds:

- `espn_phase_a_negative_dst_playercard_raw.json`
- bytes `683723`
- SHA-256
  `3f3244feec5d7c42033156620525be5446f8fdcbcdaf95f8ab39736cc13c6a93`.

## Corrected Coverage

The authoritative signed Phase-A asset universe is
`172 = 144 positive + 28 negative synthetic D/ST assets`.

Direct ESPN exact Week 3 realized response is `172 / 172`.

Historical boxscore remains `6 / 6` matchups, `12` lineup sides, `199` entries,
and `108` starters. nflverse cross-check remains `142 / 144` positive-ID mapping
with `105` direct Week 3 candidate rows. Cached PBP remains hash
`f4e671b46c24a81b6d57b9581367a2100afe4bf24f0dd34e987cf44f65774286`.

The V001 statement `144 / 144` must henceforth be read as positive-ID coverage,
not full signed-asset coverage.

## Scorer Consequences

The earlier D/ST acquisition gap was a capture-scope artifact, not absent
outcome evidence. Frozen user rosters and lineup candidates have realized
response coverage. Week 3 trades have zero current-week football effect under the
frozen 48-hour review period.

The remaining narrow blocker is IR transition representation: commissioned B2a
had an exact `move_to_ir` object, but compact Phase-A `IR_MOVE_PLUS_ADD` rows do
not retain that explicit move ID.

## Privacy / Mutation Boundary

Raw authenticated ESPN remains local-only. V001 is preserved byte-for-byte.
No production source/runtime changes, transaction execution, Phase-B attachment,
or football-model tuning occurred.

## Next Gate

Resolve whether every Phase-A `IR_MOVE_PLUS_ADD` row can be joined
deterministically to the unique legal `move_to_ir` transition from frozen
decision-time evidence. If yes, record the join as reconstructed replay state and
proceed to scorer implementation without mutating Phase A. If not, classify a
state-representation gap and repair replay representation before scoring.
