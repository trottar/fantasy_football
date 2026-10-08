# Current Project State

---
state_updated: 2026-10-07
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: historical_counterfactual_replay
active_workstream: week3_historical_replay_phase_b
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Continue Week 3 historical replay from immutable blind Phase-A receipts and the
now-frozen Week 3 postgame outcome authority. The active task is Phase-B scorer
implementation and validation; attachment/regret computation remains blocked
until that scorer is validated.

## Current Work Item

**WEEK 3 HISTORICAL REPLAY - OUTCOME AUTHORITY FROZEN / PHASE-B SCORER NEXT.**

Phase A remains immutable at source commit
`58fd202fdcdcfc997d95860df0b51fa63b3b0463`, tree
`c6e17cacb8e6b20a7c49ce2f9629121cf079294a`.

Retrospective Week 3 outcome authority is now captured locally under contract
`WEEK3_PHASE_B_OUTCOME_AUTHORITY_V001`, hash-linked to the Phase-A receipt set.
Raw authenticated ESPN responses remain local-only and are not Git material.

## Verified State

- Final Phase-A receipt-set SHA-256:
  `54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`.
- Four Phase-A receipts remain immutable and reload/hash-verified; Phase-B
  attachment is still `NONE`.
- Final commissioned/default Phase-A settings: player MC `16384`, specialist MC
  `2048`, trade MC `4096`, trade frontier limit `6`.
- Frozen action pattern: lineup ACTION at all four states; specialist-inclusive
  trade ACTION at the final three; all other action families HOLD at all four.
- Outcome authority manifest SHA-256:
  `892763082b1a03e5f9789c31e7c2961692392e027413611403ffa7e93649fd11`.
- ESPN candidate exact Week 3 actual scoring: `144 / 144`.
- ESPN Week 3 historical boxscore: `6 / 6` matchups, `12` lineup sides,
  `199` lineup entries, `108` starter entries.
- ESPN candidate coverage inside the boxscore itself: `43` candidate IDs with
  `43` applied scoring values; candidate-playercard supplies the complete
  candidate-wide exact scoring-period-3 response.
- nflverse 2026 roster mapping: `142 / 144` candidate ESPN IDs mapped;
  Week 3 direct player-stat rows: `105` candidate assets across `1114` total
  Week 3 rows.
- Existing cached PBP specialist cross-check SHA-256:
  `f4e671b46c24a81b6d57b9581367a2100afe4bf24f0dd34e987cf44f65774286`.
- Outcome authority artifacts were persisted by temp-directory write, per-file
  hash verification, manifest hash verification, then atomic directory rename.
- Outcome authority capture performed no scoring, Phase-B attachment, source
  mutation, runtime mutation, transaction execution, or football-model tuning.
- Weekly production authorities and commissioned runtime remain unchanged.

## Calendar / Evidence Gates

The fresh corrected Week 4 side-state remains preserved but is not the active
development workstream. Its pending Alvin Kamara -> Bills D/ST specialist trade
was Week 5 effective under the 48-hour review window and was not executed.

If operational Week 4/5 action resumes, refresh weekly authority first whenever
material roster, injury, market, lock, or transaction state has changed.
Irreversible prospective capture gates still outrank nonessential development.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; compose only at complete-roster utility/state boundaries.
- Historical replay is retrospective and is never relabeled prospective.
- Phase-A receipts are immutable; Phase B may reference but never regenerate them.
- Outcome authority is immutable input evidence; scorer outputs remain derived.
- ESPN fantasy scoring response is the direct realized-response authority; public
  nflverse/PBP provides component/statistical cross-checks, not silent replacement.
- Reconstructed dependencies remain explicit; frozen Phase-A sub-surfaces stay frozen.
- Direct response, field response, and manager behavior remain separate.
- `screen != authority`; uncertainty-aware predictive machinery authorized Phase A.
- `v0.X` remains a-priori: observed 2026 outcomes may expose structural defects
  but may not tune coefficients, priors, thresholds, or weights.

## Exact Next Action

Implement the Week 3 Phase-B scorer against the frozen authority contract above.

The scorer must first re-verify the Phase-A receipt set and outcome-authority
manifest/artifact hashes. For each chronological decision point, it must score
the historical actual state, the frozen model-action set, and hindsight
oracle-best feasible comparators under the same Week 3 transaction timing and
lineup legality. It must calculate regret, matchup-flip, residual, and
channel-decomposition diagnostics while preserving `P ⊕ D ⊕ K`.

Do not attach Phase B to the immutable receipts until the scorer and its authority
joins are validated. Do not use observed Week 3 results to tune v0.X.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`
- `evidence/WEEK3_PHASE_A_FINAL_FREEZE_2026-10-07.md`
- `evidence/WEEK3_PHASE_B_OUTCOME_AUTHORITY_2026-10-07.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../KNOWN_ISSUES.md`
- `../../src/counterfactual_replay.py`
- `../../src/historical_replay_input.py`
- `../../src/historical_replay_phase_a.py`
