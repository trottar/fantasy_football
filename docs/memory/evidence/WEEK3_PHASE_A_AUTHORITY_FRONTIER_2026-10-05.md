# Week 3 Phase-A Authority Frontier / Frozen Overlay Evidence — 2026-10-05

## Purpose

Record the authority-frontier diagnosis that followed publication of the Week 3
replay-input adapter, the recovered historical trade-timing evidence, and the
implementation boundary for the blind Phase-A evaluator.

No observed Week 3 outcome was read or attached. No football-model tuning or
transaction execution occurred.

## Published Starting Authority

Replay-input adapter publication:

- commit `e1ca97d74198ec5db545c78603fe9e43a2943a2e`;
- parent `a9c1fda993170d0e59bbfe4150ad4533fb426714`;
- tree `7e9514141d21c3b517287ef680aa329b2223084b`;
- focused replay pytest `25 passed`;
- full repository pytest `620 passed`;
- runtime unchanged.

The Phase-A authority audit bound source through exact Git commit/tree/blob
identities rather than checkout-byte SHA identities.

## Superseded Harness Failures

Three pre-authority diagnostic failures were harness defects only:

1. v1 imported repository modules from the extracted `.ffpkg` directory and
   failed with `ModuleNotFoundError: src`.
2. v2 added the synchronized control root to `sys.path`; that surface is sparse
   and failed on `src.weekly_manager`.
3. v3 used an isolated exact Git checkout but incorrectly compared the checkout
   worktree SHA-256 of `src/historical_replay_input.py` with the raw control-root
   SHA-256. The staging contract explicitly treats raw control-root bytes and
   Git clean-filter/index bytes as separate identity representations.

All three runs reported zero outcome reads, no Phase-B attachment, and no
mutation.

v4 corrected source identity to exact Git commit/tree/blob OIDs and reached the
football authorities.

## v4 Authority Findings

Earliest Week 3 state:

- snapshot UTC `2026-09-22T14:10:51.714616+00:00`;
- capture UTC `2026-09-22T14:10:53.254794+00:00`;
- replay mode `RECONSTRUCTED_RETROSPECTIVE_REPLAY`.

Lineup and IR roster-state authority passed directly.

Four channels failed because the immutable replay adapter returns recursive
`MappingProxyType`/tuple structures while production authority expects an
isolated mutable working representation:

- player waiver/free-agent;
- DST;
- kicker;
- IR replacement.

This is a replay handoff representation issue, not a football-model failure.

Player and specialist-inclusive trade searches failed closed because the old
normalized Week 3 snapshot did not contain `espn.transaction_settings`.

## Frozen Raw ESPN Trade Settings

Source history established that the Week 3-era ESPN sync already requested
`mSettings` and wrote the complete raw league response to each snapshot
directory at:

`espn/espn_league_raw.json`

The later October 5 trade-timing correction added only the normalized
`transaction_settings` projection. Therefore the required timing evidence
exists as a genuine frozen decision-time artifact and does not require a current
ESPN read.

All four Week 3 raw payloads produce the same required settings:

- `trade_review_hours = 48`;
- `lineup_locktime_type = INDIVIDUAL_GAME`;
- `roster_locktime_type = INDIVIDUAL_GAME`.

Raw artifact SHA-256 identities:

- `20260922T141026Z`: `62bb9d68575ef30bb892f34bd9d4b0793be703d5cbaa04b5ed8eb99254be8b43`;
- `20260923T175449Z`: `ab21c43f36be3ba27115397306340e0a8cf7c6e478c96e5375d6b228fb99ce21`;
- `20260924T070144Z`: `93f995189e4e07900e0d698df52904dd2fa03bb1a34f11ea9ee43eb890fe0119`;
- `20260924T155042Z`: `b4bbec50df7245c140415c9eda9ce17f4f630373d124a2ee477131aa23eee237`.

The Phase-A receipt must carry this raw settings artifact as an additional frozen
material transaction-timing dependency.

## Repair Probe

`week3_phase_a_frontier_repair_probe_v1_20261005`:

- deep-thawed the immutable replay state into an isolated authority working copy;
- normalized trade timing only from the same snapshot's frozen raw ESPN
  `mSettings`;
- used exact published Git source identities;
- used diagnostic `64`-scenario predictive MC;
- read zero outcome files;
- attached no Phase B evidence;
- performed no mutation.

Result:

`STATE=ALL_AUTHORITIES_REPRESENTABLE`

All eight required Phase-A action families reached commissioned authority:

1. lineup / availability;
2. player waiver / free-agent;
3. DST;
4. kicker;
5. IR / open-slot / injury replacement;
6. one-for-one player trades;
7. supported unequal / multi-player trades;
8. specialist-inclusive trades.

Earliest-state diagnostic frontier:

- player screen actions: `960`;
- player predictive rows: `36`;
- IR candidate rows: `112`;
- player trade rows: `6`, spanning `1x1`, `1x2`, and `2x1`;
- specialist-inclusive trade rows: `0` at this state;
- no authority coverage gap.

The probe is representability evidence only. Its 64-scenario outputs are not the
final frozen Phase-A prediction receipts.

## Frozen Numerical Overlay Contract

The final replay evaluator must not recompute a frozen current-week prediction
surface merely because another layer is reconstructed.

Replay execution therefore uses an isolated overlay around the unchanged
production `UtilityContext`:

- all `174` captured rostered QB/RB/WR/TE records supply frozen current-week
  yield, availability, and lock state;
- the `24` owned plus `40` actionable specialist records supply frozen
  current-week yield/lock state;
- captured model means and uncertainty become the base season-value coordinates
  for those frozen IDs when current response machinery propagates later weeks;
- uncaptured player-market candidates continue through the explicitly
  reconstructed `player_values_2026.csv` layer and the already validated frozen
  ESPN season/weekly fallback contract;
- production authority methods are restored after the replay evaluation.

This is replay tooling only. It does not alter weekly production authority or
the commissioned runtime.

### Zero-valued frozen prediction boundary

The first all-four-state commissioning attempt exposed rostered ESPN ID
`4259619` with no positive captured model/base coordinate. The failure was in
the replay evaluator: it had invented a positivity requirement that is absent
from the capture contract.

`Week3ReplayInput` requires `operational_mean_ppg` and `predictive_sd_ppg` to be
present, not positive. A finite captured zero is therefore a valid frozen value
and must remain zero rather than being replaced by the reconstructed market
layer. The evaluator now accepts nonnegative frozen base means and predictive
SDs, preserves exact zero values in the replay overlay, and reports zero-base
frozen-record counts during real-state commissioning.

## Phase-A Selection Semantics

The weekly contract does not define one global ranking across unrelated
P/D/K action channels. The replay must not invent one.

Candidate ordering is therefore channel-local. The Phase-A receipt's required
contiguous `rank` is deterministic serialization order only. Model choice is a
per-channel weekly-authority set:

`PER_CHANNEL_WEEKLY_AUTHORITY_SET_NO_CROSS_CHANNEL_ASSET_RANKING`

Player/specialist coupling remains allowed only where the commissioned complete-
roster transaction/IR machinery explicitly composes it.

## Implementation Slice

New replay-only source:

- `src/historical_replay_phase_a.py`

New regressions:

- `tests/test_historical_replay_phase_a.py`, including an explicit zero-valued frozen-record regression

The evaluator:

- binds a `Week3ReplayInput`;
- injects the frozen raw ESPN transaction settings;
- runs unchanged commissioned authorities under the frozen replay overlay;
- normalizes complete supported frontiers and explicit HOLD states;
- preserves bounded/family-balanced trade-search scope as defined by the weekly
  completion contract;
- records coverage and source/provenance identities;
- freezes the channel-local model action set into the existing immutable
  `PhaseAReceipt`;
- exposes no outcome attachment.

## Next Gate

After source validation/publication, execute the final blind Phase-A freeze for
all four chronological Week 3 decision points using the commissioned/default
uncertainty-aware scenario settings.

Persist one immutable receipt per decision point and immediately reload/hash-
verify each receipt. Do not attach outcomes, compute an oracle, calculate regret,
or tune v0.X until all corresponding Phase-A receipts are frozen and verified.
