# Week 3 Phase-B Outcome Authority — 2026-10-07

## Purpose

Freeze the retrospective observed-outcome authority required to score the
already-immutable Week 3 Phase-A receipts. This checkpoint establishes observed
data authority only; it does not perform Phase-B scoring, attachment, regret
analysis, or v0.X tuning.

## Phase-A Linkage

The authority is bound to:

- Phase-A evaluator source commit
  `58fd202fdcdcfc997d95860df0b51fa63b3b0463`;
- immutable Phase-A receipt-set SHA-256
  `54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`.

The receipt set was reverified before capture. Phase-B attachment remained
`NONE`.

## Authority Contract

Contract:

`WEEK3_PHASE_B_OUTCOME_AUTHORITY_V001`

Local-only authority directory:

`data/historical_replay/phase_b/outcome_authority/2026_w03/v001`

Manifest SHA-256:

`892763082b1a03e5f9789c31e7c2961692392e027413611403ffa7e93649fd11`

Persistence contract:

1. fetch the required retrospective sources;
2. write all artifacts into a temporary local directory;
3. hash every artifact;
4. build and hash the authority manifest;
5. reread and verify all identities;
6. atomically rename the complete set into the final immutable directory.

## Authenticated ESPN Authority

ESPN historical Week 3 boxscore/matchup capture returned:

- `6 / 6` scored matchups;
- `12` lineup sides;
- `199` lineup entries;
- `108` starter entries.

Candidate-specific ESPN scoring-period-3 actuals cover exactly `144 / 144`
frozen candidate asset IDs. The `kona_playercard` response supplied complete
candidate-wide exact actual scoring; the targeted `kona_player_info` request
did not expose those historical actual rows.

The boxscore itself contains `43` frozen candidate IDs and `43` corresponding
applied scoring values. This surface provides historical actual-lineup state,
while the candidate player-card supplies realized-response coverage outside the
actual boxscore roster.

Authenticated ESPN raw responses remain local-only.

Artifact identities:

- `espn_week3_boxscore_raw.json`
  - bytes `727714`
  - SHA-256
    `55e26225c390e5b4d5a5826f0c4281bd94b29e52c664a33433ac82a024e0702d`;
- `espn_week3_candidate_player_info_raw.json`
  - bytes `1216572`
  - SHA-256
    `d0c05b6481041f712c415a874ccd1101c7047653a512a05830bf2dd44c8cb43b`;
- `espn_candidate_playercard_raw.json`
  - bytes `1959492`
  - SHA-256
    `ced36292ee8de065d6ada4a0a895600e4a930ff82adba2003b104274f1e35eb3`.

No cookie, SWID, `espn_s2`, league identifier, or raw authenticated payload is
durable Git memory.

## Public Cross-Checks

nflverse public 2026 assets were frozen alongside the ESPN authority:

- `nflverse_stats_player_week_2026.csv`
  - bytes `1981105`
  - SHA-256
    `4783f7c943064e80793d221edfd5db211303a69a32a0bcad9c3176b1e4a8b7cb`;
- `nflverse_roster_2026.csv`
  - bytes `961758`
  - SHA-256
    `5d440f44acd215d724d8aa06a953a78f6bc13e146f43acd2a3a4d2b33bb659b6`.

Coverage:

- candidate ESPN -> GSIS mapping `142 / 144`;
- candidate assets with direct Week 3 nflverse player-stat rows `105`;
- total 2026 Week 3 nflverse player-stat rows `1114`.

The existing cached play-by-play specialist cross-check remains:

`f4e671b46c24a81b6d57b9581367a2100afe4bf24f0dd34e987cf44f65774286`

This PBP surface contains the required kicker and DST field families previously
verified by the corrected outcome-authority inventory.

## Authority Roles

Use ESPN fantasy scoring response as the primary realized fantasy-response
authority because it directly reflects the league scoring system.

Use nflverse weekly player stats and cached PBP as component/statistical
cross-checks and decomposition inputs. They must not silently replace direct
ESPN realized fantasy points where the direct response exists.

The `2 / 144` candidate IDs without nflverse ESPN-to-GSIS mapping do not block
Phase-B scoring because direct ESPN response coverage is complete; they are a
cross-check limitation that must remain explicit.

## Privacy / Mutation Boundary

The capture:

- persisted no secret value into the manifest;
- printed no private identifier or raw authenticated response;
- changed no source file;
- changed no commissioned runtime file;
- executed no transaction;
- attached no Phase-B payload to the immutable Phase-A receipts;
- performed no football-model tuning.

## Next Gate

Implement a Phase-B scorer that first re-verifies both the immutable Phase-A
receipt set and this exact outcome-authority set.

For each of the four chronological decision points, score historical actual,
frozen model-action, and hindsight oracle-best feasible comparator states under
the same transaction timing and lineup legality. Calculate regret, matchup-flip,
residual, and channel-decomposition diagnostics.

Preserve `P ⊕ D ⊕ K`, direct/field/behavior separation, and the v0.X
no-empirical-tuning boundary. Do not attach Phase B to Phase A until the scorer
and authority joins are validated.
