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
corrected frozen Week 3 outcome authority. Direct realized-response coverage is
complete for all signed Phase-A assets. The active task is the remaining IR
open-slot transition sufficiency check before scorer implementation.

## Current Work Item

**WEEK 3 HISTORICAL REPLAY - V002 OUTCOME AUTHORITY FROZEN / IR TRANSITION CHECK NEXT.**

Phase A remains immutable at source commit
`58fd202fdcdcfc997d95860df0b51fa63b3b0463`.

Corrected outcome authority contract:
`WEEK3_PHASE_B_OUTCOME_AUTHORITY_V002`.

## Verified State

- Phase-A receipt-set SHA-256:
  `54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`.
- Phase-B attachment remains `NONE`.
- V001 manifest:
  `892763082b1a03e5f9789c31e7c2961692392e027413611403ffa7e93649fd11`.
- V001 `144 / 144` meant positive Phase-A asset IDs only; its collector excluded
  negative synthetic D/ST IDs.
- V002 manifest:
  `00946e70c53cfd3eeab74c74b2397a196c514ab75ac437246079b6f6383ab4db`.
- Signed Phase-A asset universe: `172 = 144` positive + `28` negative D/ST IDs.
- Direct ESPN exact Week 3 actual scoring: `172 / 172`.
- Negative D/ST exact actuals, position shape, and pro-team mapping: `28 / 28`.
- Historical ESPN boxscore: `6 / 6` matchups, `12` lineup sides, `199` entries,
  `108` starters; historical user starter re-sum matches final team score.
- nflverse cross-check: `142 / 144` positive IDs mapped and `105` direct Week 3
  candidate rows. Cached PBP SHA-256:
  `f4e671b46c24a81b6d57b9581367a2100afe4bf24f0dd34e987cf44f65774286`.
- V002 has six hash-verified artifacts. Five are copied byte-exact from V001; the
  new negative-DST player-card response is authenticated ESPN and local-only.
- Sufficiency audit: all frozen user rosters and lineup candidates have realized
  response coverage. All Week 3 trades have zero current-week football effect
  under the frozen 48-hour review period.
- Remaining issue: Phase-A compact `IR_MOVE_PLUS_ADD` rows omit the explicit
  `move_to_ir` ID that existed in the commissioned B2a authority.
- Production authorities and commissioned runtime remain unchanged.

## Calendar / Evidence Gates

Week 4 operational side-state remains preserved and inactive. The pending
Kamara -> Bills D/ST specialist trade was Week 5 effective under the 48-hour
review window and was not executed.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Phase-A receipts are immutable.
- V002 corrects V001 coverage classification; V001 bytes remain immutable.
- ESPN fantasy scoring response is the primary realized-response authority.
- nflverse/PBP remain statistical/component cross-checks.
- Waiver acquisition and trade acceptance remain separate from football response.
- Historical replay is retrospective and never relabeled prospective.
- No observed 2026 outcome may tune v0.X.

## Exact Next Action

Resolve the Week 3 IR open-slot transition from frozen decision-time evidence.

Determine whether every Phase-A `IR_MOVE_PLUS_ADD` candidate can be joined
deterministically to the unique legal `move_to_ir` transition required by the
commissioned B2a authority before its add frontier was emitted. If the join is
exact, document it as reconstructed replay state and proceed to Phase-B scorer
implementation without mutating Phase A. Otherwise classify a state-representation
gap and repair replay representation first.

Do not attach Phase B until this transition boundary and scorer joins are validated.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/HISTORICAL_COUNTERFACTUAL_REPLAY.md`
- `evidence/WEEK3_PHASE_A_FINAL_FREEZE_2026-10-07.md`
- `evidence/WEEK3_PHASE_B_OUTCOME_AUTHORITY_2026-10-07.md`
- `evidence/WEEK3_PHASE_B_OUTCOME_AUTHORITY_V002_CORRECTION_2026-10-07.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../KNOWN_ISSUES.md`
- `../../src/counterfactual_replay.py`
- `../../src/historical_replay_input.py`
- `../../src/historical_replay_phase_a.py`
