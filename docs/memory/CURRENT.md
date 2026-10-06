# Current Project State

---
state_updated: 2026-10-05
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: historical_counterfactual_replay
active_workstream: week3_historical_replay_phase_a
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Continue the previous-week checks by replaying Week 3 under the published
historical counterfactual replay contract.

The active development task is the mixed-provenance Week 3 Phase-A replay:
construct the historical input state, enumerate the complete legal decision space,
evaluate candidates with observed Week 3 outcomes unavailable, and freeze the
Phase-A receipt/model choice before any Phase-B outcome attachment.

## Current Work Item

**WEEK 3 HISTORICAL REPLAY - BLIND PHASE-A CANDIDATE ENUMERATION / EVALUATION.**

The replay-input adapter is published and the replay-only Phase-A evaluator is
implemented and validated in this checkpoint. A read-only authority-frontier
repair probe established that all eight required action families are representable
when immutable replay state is deep-thawed into an isolated authority working copy
and transaction timing is bound from the same snapshot's frozen raw ESPN mSettings.

The next replay operation is the final blind Phase-A freeze across all four
chronological Week 3 decision points under commissioned/default predictive
scenario settings.

Week 3 replay mode is:

`RECONSTRUCTED_RETROSPECTIVE_REPLAY`

because the player waiver/free-agent predictive-value layer cannot be proved from
a decision-time artifact. Proven frozen sub-surfaces remain frozen and must not be
recomputed merely because another material layer is reconstructed.

## Verified State

- Weeks 1-2: no frozen decision-state snapshot/capture/weekly-receipt artifacts
  were found; replay is reconstructed-only.
- Week 3 rostered-player predictions: `174 / 174` frozen.
- Week 3 owned DST/K predictions: `24 / 24` frozen.
- Week 3 historical actionable specialist frontier: `40 / 40` exactly reproduced
  under the historical eligibility rule.
- Week 3 broad player market: 780 QB/RB/WR/TE records, but the frozen records do
  not contain `latent_mean_ppg`, `latent_mean_sd_ppg`, or
  `predictive_weekly_sd_ppg`.
- Surviving player-values identity:
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`;
  its exact pre-capture decision-time authority remains unproven.
- Phase-A source checkpoint:
  `b038c6b388f1a4aefc53c45ce1c924ed9e9bdb85`.
- `src/counterfactual_replay.py` SHA-256:
  `791af42c910d47967bd371d9feddaf50ae45319f707c3608a10cfee7172606b7`.
- `tests/test_counterfactual_replay.py` SHA-256:
  `1fed93e8e1352c6b78a3e44b5e52941d85cbd71ab54822dc8847f02275de6a8b`.
- Validation: 14 focused replay tests passed; exact complete-repository candidate
  passed 609 tests plus `compileall`, staged allowlist, manifest, and diff gates.
- Phase-A receipt/outcome firewall: published and validated.
- Week 3 input-contract audit: `4 / 4` captures integrity-valid and canonically
  linked to `4 / 4` frozen snapshots; outcome files read: `0`.
- Replay-input adapter: `src/historical_replay_input.py`; real-data probe:
  `4 / 4` Week 3 pairs PASS.
- Adapter validation: `25` focused replay tests and `620` full-repository tests
  pass in the isolated predecessor checkout; `compileall` PASS.
- Player-values fallback: eligible players without a positive reconstructed
  latent mean follow the commissioned frozen ESPN season/weekly projection
  fallback; this is explicit adapter metadata, not a missing dependency.
- Week 3 authority-frontier repair probe: all eight required action families are
  representable on the earliest state; zero outcome reads and no mutation.
- Frozen raw ESPN trade settings exist for all four Week 3 snapshots: 48-hour
  review, `INDIVIDUAL_GAME` lineup lock, and `INDIVIDUAL_GAME` roster lock.
- Phase-A evaluator: `src/historical_replay_phase_a.py`; production authority is
  unchanged and replay-only frozen numerical overlays are restored after use.
- Phase-A evaluator validation: 37 focused replay tests and 632 full-repository
  tests plus `compileall`, strict memory health, `git diff --check`, and a
  `4 / 4` real-state 64-scenario no-outcome commissioning probe.
- Observed Week 3 outcomes attached to replay: none.
- Football-model tuning from 2026 outcomes: false.
- Replay transaction execution: none.

## Calendar / Evidence Gates

The fresh corrected Week 4 decision evidence remains preserved but is **not the
active development workstream** in this session.

The last validated Week 4 receipt identified an Alvin Kamara -> Bills D/ST
specialist-inclusive trade, Week 5 effective under the 48-hour review window, with
no Week 4 ownership effect. No transaction was executed.

Do not substitute that pending operational item for the selected previous-week
replay work. If transaction execution is later resumed, first re-establish that
the material roster/injury/market/lock/transaction state is still current; if it
has changed, take a fresh snapshot/capture and rerun weekly authority.

An irreversible calendar capture gate still outranks nonessential development if
a genuinely new capture deadline arises.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; compose only at complete-roster boundaries.
- Historical replay is retrospective and is never relabeled prospective.
- Frozen historical sub-surfaces remain frozen.
- Reconstructed material dependencies must be explicit in the Phase-A receipt.
- Observed outcomes are unavailable to Phase-A generation, screening, evaluation,
  ranking, and model-action selection.
- `screen != authority`; uncertainty-aware response machinery authorizes model
  choices.
- Manager behavior remains separate from intrinsic football utility.
- Missing legal/action coverage fails closed.
- No future IR-capacity credit while B2b is deferred.
- `v0.X` remains a-priori; observed 2026 outcomes may expose structural defects
  but may not tune coefficients, priors, thresholds, or weights.

## Exact Next Action

Execute the final blind Phase-A freeze for all four chronological Week 3 decision
points using the published replay-input/evaluator contract and commissioned/default
uncertainty-aware scenario settings.

Persist one immutable Phase-A receipt per decision point, then immediately reload
and hash-verify every receipt. Preserve the per-channel weekly-authority selection
semantics; do not invent a cross-channel asset ranking.

Do **not** attach Week 3 outcomes, compute hindsight oracles, calculate realized
regret, or use any result for v0.X tuning until all four Phase-A receipts are
frozen and verified.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`
- `evidence/HISTORICAL_COUNTERFACTUAL_REPLAY_PHASE_A_BOOTSTRAP_2026-10-05.md`
- `evidence/WEEK3_REPLAY_INPUT_ADAPTER_2026-10-05.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
- `../../src/counterfactual_replay.py`
- `../../src/historical_replay_input.py`
- `../../tests/test_counterfactual_replay.py`
- `../../tests/test_historical_replay_input.py`
