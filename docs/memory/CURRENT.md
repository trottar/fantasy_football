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

**WEEK 3 HISTORICAL REPLAY - PHASE-A INPUT ADAPTER + BLIND EVALUATION.**

Phase-A provenance/receipt/outcome-firewall tooling is pushed and remote-verified.
The next implementation slice is the Week 3 replay-input adapter and blind
candidate evaluation.

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

Implement and validate the **Week 3 mixed-provenance replay-input adapter** as
standalone diagnostic/replay tooling.

The adapter must bind:

1. frozen Week 3 rostered-player predictions;
2. frozen owned/actionable specialist state;
3. the explicitly reconstructed player waiver/free-agent predictive-values layer;
4. historical league/lock/transaction/availability state needed for legality.

Then enumerate the complete supported Week 3 legal action space and evaluate it
with observed Week 3 outcomes unavailable. Freeze candidate predictions,
uncertainty, ranking, model-preferred action, source/dependency identities, and
replay-mode provenance into the immutable Phase-A receipt.

Do **not** attach Week 3 outcomes, compute the hindsight oracle, calculate realized
regret, or use any result for v0.X tuning until the Phase-A receipt is frozen and
verified.

If a material historical dependency cannot be proved or reconstructed without
leakage, classify it explicitly and fail closed rather than silently inferring it.

After the Phase-A receipt is frozen, proceed separately to Phase B: attach actual
Week 3 outcomes and compare historical actual vs model-preferred vs oracle-best
feasible states, then classify structural/search/state/data discrepancies.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`
- `evidence/HISTORICAL_COUNTERFACTUAL_REPLAY_PHASE_A_BOOTSTRAP_2026-10-05.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
- `../../src/counterfactual_replay.py`
- `../../tests/test_counterfactual_replay.py`
