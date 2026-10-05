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

The mixed-provenance Week 3 replay-input adapter is implemented and validated in
this checkpoint against all four frozen Week 3 snapshot/capture pairs. It binds
the frozen rostered-player and specialist surfaces and marks only the
player waiver/free-agent predictive-values layer as reconstructed.

The next implementation slice is complete legal Phase-A candidate generation and
uncertainty-aware evaluation for each replayable Week 3 decision point.

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

Use the validated Week 3 replay-input adapter to materialize the four chronological
mixed-provenance decision states, then implement the **complete supported legal
Phase-A candidate enumerator/evaluator**.

For each decision point, cover the weekly-contract families supported by the
historical state: lineup/availability, player waiver/free agent, DST, kicker,
IR/open-slot/injury replacement, one-for-one player trades, supported unequal or
multi-player trades, and specialist-inclusive trades. Preserve transaction timing,
locks, roster legality, availability state, and `P ⊕ D ⊕ K`.

Cheap screens may generate frontiers, but predictive uncertainty-aware response
machinery must authorize rankings and model choice. Freeze a separate immutable
Phase-A receipt for each replayable decision point with candidate predictions,
uncertainty, ranking, selected action, source identities, and provenance.

Do **not** attach Week 3 outcomes, compute hindsight oracles, calculate realized
regret, or use any result for v0.X tuning until each corresponding Phase-A receipt
is frozen and verified.

If a historical dependency or legal branch cannot be represented without leakage,
classify it explicitly and fail closed rather than silently narrowing the action
space.

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
