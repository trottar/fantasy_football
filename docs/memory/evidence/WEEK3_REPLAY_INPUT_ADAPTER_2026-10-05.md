# Week 3 Replay Input Adapter Evidence — 2026-10-05

## Purpose

Close the Week 3 mixed-provenance input-adapter gate before blind historical
candidate generation. This evidence is Phase-A only: no Week 3 observed outcome,
oracle score, realized regret, or v0.X empirical tuning is introduced.

## Corrected Input-Contract Audit

The first audit package was non-mutating and read zero outcome files, but searched
only the control-root `data/` surface and therefore found no Week 3 captures.
That was a path-discovery harness defect, not evidence of missing captures.

The corrected audit searched both the control root and commissioned runtime with a
path-first outcome firewall and established `4 / 4` integrity-valid prospective
captures canonically linked to `4 / 4` frozen snapshots, with zero outcome files
read and no mutation. Each capture freezes 174 rostered QB/RB/WR/TE predictions,
24 owned specialists, and the exact 40-player actionable specialist frontier.
The frozen broad player market contains 780 QB/RB/WR/TE records and none of
`latent_mean_ppg`, `latent_mean_sd_ppg`, or `predictive_weekly_sd_ppg`.

The surviving reconstructed player-values artifact is `data/processed/player_values_2026.csv`, SHA-256
`4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`, with the required latent/predictive columns. Its exact
authority before the earliest Week 3 capture remains unproven, so the replay mode
remains `RECONSTRUCTED_RETROSPECTIVE_REPLAY`.

## Superseded Adapter v1 Real-Pair Failure

The first adapter local-apply candidate performed no control-root write. Its
isolated focused/full tests passed, but the first real Week 3 pair blocked the
write because the adapter required every NFL-eligible QB/RB/WR/TE candidate to
have a row in the reconstructed values CSV.

The first pair exposed 12 eligible IDs absent from that CSV:

`3916071, 4384852, 4428993, 4429582, 4431196, 4431346, 4600597, 4635009,
4683308, 4685116, 4808759, 5081999`.

Exact source inspection of `transaction_manager.enrich_season_values()` proved
that this rule was stricter than commissioned authority. Production semantics use
a positive finite `latent_mean_ppg` when available; otherwise they use frozen
ESPN `season_projection / 17` when positive and then the frozen weekly projection.
CSV absence therefore is not itself a missing replay dependency.

## Corrected Adapter Contract

- `src/historical_replay_input.py` SHA-256 `4145ca8c3eb7673d17c563c834292f2ff9c2333d78644be7c5b710a529d51d42`;
- `tests/test_historical_replay_input.py` SHA-256 `88265d8dcb5e4f2444d518e482c5a3d641a0ad5b7012c0c33a10718386515504`.

The adapter validates exact Week 3 identity, capture integrity, canonical snapshot
linkage, pre-data firewall, frozen league/model identities, exact 174-player
rostered prediction coverage, exact 24-player owned-specialist coverage, exact
40-player specialist frontier reproduction, absence of latent/predictive fields
from the frozen broad market, and the known reconstructed values identity/schema.

Player-value source selection now mirrors commissioned enrichment exactly:
positive reconstructed latent mean when available, otherwise frozen ESPN
season/weekly projection fallback. The adapter records the exact actionable IDs on
that fallback branch. Historical state, player/specialist predictions, locks,
availability, transaction state, league config, and model config remain `FROZEN`;
the surviving player-values artifact remains `RECONSTRUCTED`.

The adapter exposes no outcome loader and marks outcomes unavailable to the input
state.

## Validation Boundary

The corrected local-apply package may write only after an isolated complete
checkout of predecessor `a9c1fda993170d0e59bbfe4150ad4533fb426714` passes:

- replay-focused pytest: `25 passed`;
- full repository pytest: `620 passed`;
- `compileall src`: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS;
- real-data adapter probe: `4 / 4 PASS`;
- adapter fallback IDs exactly equal the commissioned `UtilityContext`
  non-`MODEL_LATENT_PPG` actionable player set on every pair.

No observed outcomes are attached by the probe.

## State Boundary

- replay input adapter: diagnostic/replay source only;
- weekly production authorities: unchanged;
- commissioned runtime: unchanged;
- observed replay outcome attachment: none;
- football-model tuning from 2026 outcomes: false;
- transaction execution: none.

The next gate is blind Phase-A candidate enumeration/evaluation across all four
validated Week 3 states, with one immutable Phase-A receipt per replayable
decision point before Phase B.
