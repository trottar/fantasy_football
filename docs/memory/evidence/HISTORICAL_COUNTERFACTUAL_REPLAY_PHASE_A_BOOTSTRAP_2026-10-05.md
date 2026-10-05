# Historical Counterfactual Replay Phase-A Bootstrap Evidence — 2026-10-05

## Purpose

Record the first historical-replay provenance audit and the validated standalone
Phase-A receipt/outcome-firewall implementation without changing current Week 4
football authority.

## Authority Boundary

- Repository predecessor: `f9023a9d165d1079a91d0dbcf060ee1709b1a16b`.
- Commissioned runtime: `fantasy_season_v0_36_repack1`, internal `0.36`.
- Replay work is diagnostic/replay tooling under standing authorization.
- Runtime remained unchanged.
- No observed outcome was attached to a replay.
- No football-model tuning occurred.
- No transaction was executed.
- The Week 4 Kamara -> Bills D/ST execution gate remains the authoritative active
  workstream and exact next action in `CURRENT.md`.

## Weeks 1-3 Evidence Inventory

Read-only inventory found:

- Week 1: no frozen snapshot, prospective capture, or weekly receipt.
- Week 2: no frozen snapshot, prospective capture, or weekly receipt.
- Week 3: four exact snapshot/capture pairs with capture-integrity PASS,
  pre-data-firewall PASS, and exact canonical snapshot linkage; no weekly receipt
  or material-dependency provenance receipt.

Weeks 1-2 are therefore reconstructed-only. Week 3 required a dependency audit.

## Week 3 Frozen / Reconstructed Split

Corrected scope analysis established:

- `174 / 174` rostered QB/RB/WR/TE predictions are frozen in every Week 3
  capture.
- `24 / 24` owned DST/K predictions are frozen in every Week 3 capture.
- The frozen snapshot contains 66 market specialist records.
- Applying the exact historical Week 3 eligibility rule derives 40 actionable
  specialists and matches the captured available-specialist set exactly in all
  four pairs.
- The broad frozen player market contains 780 QB/RB/WR/TE records.
- None of those records contains the three predictive values required by current
  player-market evaluation:
  `latent_mean_ppg`, `latent_mean_sd_ppg`, or `predictive_weekly_sd_ppg`.
- The surviving `data/processed/player_values_2026.csv` has SHA-256
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.
- Its local mtime precedes two later Week 3 captures, and a Week 3 trade-search
  artifact created at `2026-09-24T07:15:14.838531+00:00` references that hash,
  but no evidence predating the earliest Week 3 capture proves that exact values
  identity.
- Git contains no pre-Week-3 history for that values artifact.

Classification:

`WEEK3_REPLAY_MODE = RECONSTRUCTED_RETROSPECTIVE_REPLAY`

Frozen Week 3 sub-surfaces remain frozen; only the unproven material player-market
values layer is reconstructed.

## Phase-A Source Slice

New paths:

- `src/counterfactual_replay.py`
  - SHA-256:
    `791af42c910d47967bd371d9feddaf50ae45319f707c3608a10cfee7172606b7`
- `tests/test_counterfactual_replay.py`
  - SHA-256:
    `1fed93e8e1352c6b78a3e44b5e52941d85cbd71ab54822dc8847f02275de6a8b`

Implemented contract:

- per-dependency provenance;
- causal-versus-reconstructed replay-mode classification;
- immutable candidate predictions/uncertainty/rankings/model action;
- recursive Phase-A rejection of observed/actual/realized/oracle fields;
- canonical SHA-256-addressed Phase-A receipts;
- exclusive no-overwrite receipt persistence;
- receipt hash verification on reload;
- hard outcome access/attachment firewall before Phase-A freeze;
- Phase-B linkage to the frozen Phase-A receipt hash.

The module is standalone replay infrastructure only. It is not wired into
`weekly_decision_cycle.py`, `closure.py`, `historical.py`, or
`observability/replay.py`.

## Validation

Exact candidate was validated in an isolated complete checkout of predecessor
`f9023a9d165d1079a91d0dbcf060ee1709b1a16b`:

- focused replay tests: `14 passed in 0.20s`;
- full repository suite: `609 passed in 51.74s`;
- `compileall src`: PASS;
- exact staged allowlist: `2 / EXACT`;
- `git diff --cached --check`: PASS;
- candidate tree:
  `65cb05b7a2458464c2f7e57887e0e31c27390b50`.

After isolated validation, the exact same source/test bytes were applied to the
synchronized control root:

- focused replay tests: `14 passed in 0.78s`;
- `py_compile`: PASS;
- real package import smoke: PASS;
- rendered whitespace: PASS.

## Superseded Validation-Harness Failures

### Local apply v1

The candidate focused suite passed, but the package attempted a full repository
suite from the synchronized control root. That surface is intentionally sparse
and lacks repository files including `pytest.ini`,
`tests/test_closure_v029.py`, and `src/data_sources/espn.py`. The resulting
`887 errors` were a validation-context failure, not source evidence. Rollback
removed both candidate paths.

### Local apply v2

The exact already-validated source was written, but the package used
`module_from_spec(...); exec_module(...)` without registering the temporary module
in `sys.modules`. Under Python 3.13, dataclass processing dereferenced the absent
module and raised:

`AttributeError: 'NoneType' object has no attribute '__dict__'`

Rollback again removed both candidate paths. v3 replaced the custom loader with
the application's real package import and passed.

## Memory Local-Apply v1 Threshold Failure

The first memory package performed no write. Its temporary candidate passed all
semantic integrity checks but rendered `CURRENT.md` at 179 lines, crossing the
strict checker's 175-line soft threshold. The failure was correctly classified as
memory-structure debt rather than implementation failure. The successor keeps
`CURRENT.md` concise and places replay detail in this evidence record and the
canonical replay architecture.

## Published Checkpoint

The source+memory checkpoint was subsequently published and independently
remote-verified:

- commit: `b038c6b388f1a4aefc53c45ce1c924ed9e9bdb85`;
- parent: `f9023a9d165d1079a91d0dbcf060ee1709b1a16b`;
- committed tree: `e59b6e7d2930b42d2a2af8e1e54e14756763c86e`;
- remote `main`: `b038c6b388f1a4aefc53c45ce1c924ed9e9bdb85`;
- changed paths: `9 / EXACT` including the regenerated schema-2 memory manifest;
- manifest entries: `181`;
- final focused replay pytest: `14 passed in 0.17s`;
- final full repository pytest: `609 passed in 48.39s`;
- `compileall src`: PASS;
- strict memory health: PASS.

Read-only remote verification confirmed `main` points to the exact commit/tree/parent
above and the predecessor-to-head comparison contains exactly the intended nine
paths.

## State Boundary

- Phase-A source: `PUSHED / REMOTE VERIFIED`;
- durable replay bootstrap memory: `PUSHED / REMOTE VERIFIED`;
- runtime: unchanged;
- football-model tuning: false;
- observed replay outcome attachment: none;
- transaction execution by replay work: none.
- The separate Week 4 Kamara -> Bills D/ST action gate remains state-sensitive
  and authoritative in `CURRENT.md`.

## Next Replay Development Gate

Bind a Week 3 replay-input adapter to:

1. frozen rostered-player predictions;
2. frozen owned/actionable specialist state;
3. explicitly reconstructed player waiver/free-agent values.

Then enumerate/evaluate legal Phase-A candidates with observed outcomes
unavailable. Only after the Phase-A receipt is frozen may Phase B attach outcomes,
score historical/model/oracle states, and compute regret diagnostics.
