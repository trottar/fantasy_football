# Week 3 Phase-A Final Freeze — 2026-10-07

## Purpose

Record the immutable blind Phase-A freeze for all four chronological Week 3
historical replay decision points before any observed-outcome attachment.

This evidence is retrospective replay infrastructure. It is not a prospective
prediction capture and it does not authorize v0.X empirical tuning.

## Published Replay Authority

The final freeze used the source-published replay evaluator checkpoint:

- commit `58fd202fdcdcfc997d95860df0b51fa63b3b0463`;
- tree `c6e17cacb8e6b20a7c49ce2f9629121cf079294a`;
- subject `Add Week 3 Phase-A replay evaluator`;
- weekly production authorities unchanged;
- commissioned runtime unchanged.

The evaluator preserves frozen Week 3 player/specialist numerical surfaces,
reconstructs only the explicitly classified player waiver/free-agent values
dependency, and normalizes transaction timing from the same snapshot's frozen
raw ESPN `mSettings`.

## Final Blind Freeze Contract

Package:

`week3_phase_a_final_freeze_v1_20261006`

Local-only immutable receipt directory:

`data/historical_replay/phase_a/2026_w03/engine_58fd202fdcdcfc997d95860df0b51fa63b3b0463`

Receipt-set SHA-256:

`54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`

Replay mode for every receipt:

`RECONSTRUCTED_RETROSPECTIVE_REPLAY`

Commissioned/default predictive settings were used without an evaluator override:

- player predictive MC: `16384`;
- specialist MC: `2048`;
- player/specialist trade search MC: `4096`;
- trade frontier limit: `6`.

Persistence was all-or-nothing:

1. evaluate all four states behind the Phase-A outcome firewall;
2. save each receipt with the existing `O_EXCL + fsync` persistence contract;
3. immediately reload and content-hash verify each receipt;
4. build and hash the four-receipt set manifest;
5. verify every receipt again;
6. atomically rename the complete temporary receipt directory into its final
   engine-addressed location.

The run reported:

- `OUTCOME_FILES_READ=0`;
- `PHASE_B_ATTACHMENT=NONE`;
- `FOOTBALL_MODEL_TUNING=false`;
- `TRANSACTION_EXECUTION=NONE`;
- control-root source unchanged;
- commissioned runtime unchanged.

## Frozen Receipts

| Decision state | Candidates | Authorized candidates | Zero-base P | Zero-base specialists | Receipt SHA-256 | File SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `20260922T141026Z` | 237 | 1 | 6 | 1 | `ef6e4007b5831f71154f7dab620d8c03bf3e89924163fdbae217fd6a443e1c7d` | `6e78cb06723f387e75f3f3ac211d35ed520fafa44f056b1f3fa2ea98dd68edb8` |
| `20260923T175449Z` | 77 | 7 | 5 | 1 | `28de7a8df3441bf8aab31ad94d6ee7bbfc5f1a4a73cf6144b28748e0dece10e9` | `15cfe84010c3bd529ea44e7066bb66173e18787da4d79f299c9950df8473ee36` |
| `20260924T070144Z` | 75 | 4 | 0 | 1 | `f2d1bef78831507e9c5128becea6a851d6366fa71b16c58f50904b8566d5c9b2` | `112aa76b6bbb8d1d5c9b06dd63cfe18976f26d4967d89fa42c17f678c347dc2d` |
| `20260924T155042Z` | 73 | 4 | 0 | 1 | `4f9e7f7ad1daad3f90a7be52c8906c370585d82c4f52d73fafbd65047ddf65ed` | `5e174d9e6139083e0d3cf4a867f865d1d9ba0e5bbaf02b093bf853e731ad002e` |

## Frozen Model-Action Set

Selection semantics are identical in all four receipts:

`PER_CHANNEL_WEEKLY_AUTHORITY_SET_NO_CROSS_CHANNEL_ASSET_RANKING`

The receipt-level contiguous rank is deterministic serialization order only.
Preference/authorization remains channel-local under the weekly authority
contract.

### `20260922T141026Z`

- lineup / availability: `PASS / ACTION`;
- player waiver/free-agent: HOLD;
- DST: HOLD;
- kicker: HOLD;
- IR/open-slot/injury replacement: HOLD;
- one-for-one player trade: HOLD;
- unequal/multi-player trade: HOLD;
- specialist-inclusive trade: HOLD.

### `20260923T175449Z`

- lineup / availability: `PASS / ACTION`;
- player waiver/free-agent: HOLD;
- DST: HOLD;
- kicker: HOLD;
- IR/open-slot/injury replacement: HOLD;
- one-for-one player trade: HOLD;
- unequal/multi-player trade: HOLD;
- specialist-inclusive trade: `PASS / ACTION`, six authorized candidate IDs:
  - `trade_specialist_inclusive:3a3fcbc594fb501cc989`;
  - `trade_specialist_inclusive:a7114cee12a22680b1f9`;
  - `trade_specialist_inclusive:0446ee5fa3f3d93abf48`;
  - `trade_specialist_inclusive:cb305cfa53fb38e9d6ec`;
  - `trade_specialist_inclusive:4f85ad51554ae75607b3`;
  - `trade_specialist_inclusive:f40b8ef33c8730be1b84`.

### `20260924T070144Z`

- lineup / availability: `PASS / ACTION`;
- player waiver/free-agent: HOLD;
- DST: HOLD;
- kicker: HOLD;
- IR/open-slot/injury replacement: HOLD;
- one-for-one player trade: HOLD;
- unequal/multi-player trade: HOLD;
- specialist-inclusive trade: `PASS / ACTION`, three authorized candidate IDs:
  - `trade_specialist_inclusive:0b4480d94ab4b6164107`;
  - `trade_specialist_inclusive:272111b1c82ffc3c307e`;
  - `trade_specialist_inclusive:d93fa8b6752ed9b2d6ba`.

### `20260924T155042Z`

- lineup / availability: `PASS / ACTION`;
- player waiver/free-agent: HOLD;
- DST: HOLD;
- kicker: HOLD;
- IR/open-slot/injury replacement: HOLD;
- one-for-one player trade: HOLD;
- unequal/multi-player trade: HOLD;
- specialist-inclusive trade: `PASS / ACTION`, three authorized candidate IDs:
  - `trade_specialist_inclusive:399fad4baa8e7b9ad05e`;
  - `trade_specialist_inclusive:ee80c53bd5554afa3d9c`;
  - `trade_specialist_inclusive:c5bb5717dd4e73a3f121`.

## Independent Receipt-Set Verification

A separate read-only package,
`week3_phase_a_receipt_set_verify_v1_20261007`, re-opened the persisted receipt
set and verified:

- exact receipt-set SHA-256;
- four exact receipt labels;
- all four receipt-content hashes;
- all four file-byte SHA-256 identities;
- `8 / 8` channel selections in every receipt;
- replay mode unchanged;
- no missing material dependencies;
- Phase-A outcome-firewall metadata intact;
- `PHASE_B_ATTACHMENT=NONE`;
- no mutation.

This verification also resolved a malformed first-state `SELECTIONS=` console
summary from the freeze run. The persisted first receipt is internally complete:
lineup is ACTION and all seven other action families are HOLD.

## Phase-A Closure

Blind Week 3 Phase A is now closed for this engine checkpoint:

- candidate sets are immutable;
- predictive uncertainty and channel-local rankings are frozen;
- model-action sets are frozen;
- source/dependency identities are frozen;
- all four receipts have been reloaded and hash-verified;
- observed outcomes have not been attached.

No later Phase-B observation may alter these receipts.

## Next Gate

Proceed to Phase B only by first reloading and verifying the immutable Phase-A
receipt set above. Then attach observed Week 3 outcomes, score the historical
actual/model-preferred/oracle-feasible comparator states, calculate regret and
residual diagnostics, and classify discrepancies.

`P ⊕ D ⊕ K`, direct/field/behavior separation, the Phase-A source identities,
and the v0.X no-empirical-tuning boundary remain in force. A surprising or poor
historical result may open a structural investigation; it may not authorize
coefficient, prior, threshold, or weight tuning in v0.X.
