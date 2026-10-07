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

Continue the Week 3 historical replay from the immutable blind Phase-A receipts.
Phase A is closed. The active task is Phase-B outcome attachment and regret /
residual diagnosis without altering the frozen receipts or tuning v0.X.

## Current Work Item

**WEEK 3 HISTORICAL REPLAY - PHASE-A FROZEN / PHASE-B OUTCOME ATTACHMENT NEXT.**

Replay mode remains `RECONSTRUCTED_RETROSPECTIVE_REPLAY`: frozen rostered-player
and specialist surfaces remain frozen, while the player waiver/free-agent values
layer is explicitly reconstructed.

The final Phase-A evaluator is source-published at
`58fd202fdcdcfc997d95860df0b51fa63b3b0463`, tree
`c6e17cacb8e6b20a7c49ce2f9629121cf079294a`.

## Verified State

- Week 3 input coverage: `174 / 174` frozen rostered QB/RB/WR/TE predictions,
  `24 / 24` owned DST/K predictions, and `40 / 40` actionable specialist
  predictions.
- Reconstructed player-values dependency identity:
  `4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.
- Frozen transaction timing exists in all four raw ESPN decision-time payloads:
  48-hour review with `INDIVIDUAL_GAME` lineup and roster locks.
- Replay evaluator validation: `37` focused tests, `632` full-repository tests,
  `compileall`, strict memory health, diff checks, and `4 / 4` real-state
  no-outcome probes.
- Final Phase-A receipt-set SHA-256:
  `54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`.
- Final commissioned/default settings: player MC `16384`, specialist MC `2048`,
  trade MC `4096`, trade frontier limit `6`.
- Receipt candidate counts by chronological state: `237`, `77`, `75`, `73`.
- Authorized candidate counts: `1`, `7`, `4`, `4`.
- Frozen action pattern: lineup ACTION at all four states; specialist-inclusive
  trade ACTION at the final three states; player waiver/free-agent, DST, kicker,
  IR, one-for-one player trade, and unequal/multi-player player trade are HOLD
  at all four states.
- Zero-base frozen player counts: `6`, `5`, `0`, `0`; specialist count: `1` in
  every state. Captured zero is valid frozen evidence, not a reconstruction cue.
- Four receipts are immutable and reload/hash-verified. A separate read-only
  verifier confirmed the exact set/file/receipt hashes and `8 / 8` channel
  selections in every receipt.
- Phase-A outcome files read: `0`. Phase-B attachment: `NONE`.
- Football-model tuning from observed 2026 outcomes: false.
- Replay transaction execution: none.
- Weekly production authorities and commissioned runtime remain unchanged.

## Calendar / Evidence Gates

The fresh corrected Week 4 side-state remains preserved but is not the active
development workstream. Its pending Alvin Kamara -> Bills D/ST specialist trade
was Week 5 effective under the 48-hour review window and was not executed.

If operational Week 4/5 action is resumed, refresh weekly authority first when
material roster, injury, market, lock, or transaction state has changed.
Irreversible prospective capture gates still outrank nonessential development.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; compose only at complete-roster utility/state boundaries.
- Historical replay remains retrospective and is never relabeled prospective.
- Phase-A receipts are immutable; Phase B may only attach outcomes to them.
- Reconstructed dependencies remain explicit; frozen sub-surfaces stay frozen.
- `screen != authority`; uncertainty-aware predictive machinery authorizes
  football decisions.
- Manager behavior remains separate from intrinsic football utility.
- Missing legal/action coverage fails closed.
- No future IR-capacity credit while B2b remains deferred.
- `v0.X` remains a-priori: observed 2026 outcomes may expose structural defects
  but may not tune coefficients, priors, thresholds, or weights.

## Exact Next Action

Reload and hash-verify the immutable four-receipt Phase-A set, then attach
observed Week 3 outcomes in Phase B.

For each chronological decision point, score the historical actual state, the
frozen model-action set, and the hindsight oracle-best feasible comparator;
calculate regret, matchup-flip, residual, and decomposition diagnostics; and
classify discrepancies under the historical replay taxonomy.

Do not regenerate or mutate Phase A. Preserve transaction timing, provenance,
`P ⊕ D ⊕ K`, and direct/field/behavior separation. A surprising historical
result may open a structural investigation but may not authorize v0.X tuning.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `evidence/HISTORICAL_COUNTERFACTUAL_REPLAY_PHASE_A_BOOTSTRAP_2026-10-05.md`
- `evidence/WEEK3_REPLAY_INPUT_ADAPTER_2026-10-05.md`
- `evidence/WEEK3_PHASE_A_AUTHORITY_FRONTIER_2026-10-05.md`
- `evidence/WEEK3_PHASE_A_FINAL_FREEZE_2026-10-07.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../KNOWN_ISSUES.md`
- `../../src/counterfactual_replay.py`
- `../../src/historical_replay_input.py`
- `../../src/historical_replay_phase_a.py`
