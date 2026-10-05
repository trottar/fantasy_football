# Current Project State

---
state_updated: 2026-10-05
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: weekly_decision_gate_b_capability_closure
active_workstream: fresh_post_trade_timing_week4_cycle
memory_refinement_step: none
nfl_week: 4
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Take a new decision-time Week 4 snapshot and prospective capture through the
fully corrected commissioned runtime, then rerun the complete 9-channel weekly
decision cycle before any trade execution.

The prior Oct. 5 snapshot/capture remains valid immutable prospective evidence,
but its sole Kamara -> Bills D/ST trade action was produced before the trade
effective-time correction and is not executable authority.

## Current Work Item

**TRADE EFFECTIVE TIMING BOUNDARY - SOURCE-PUBLISHED / RUNTIME-COMMISSIONED.**

Published checkpoint:
`a404f61c77a1449b8275928d877d3c39c0a624a6`
(tree `3af8b01bb8451d7d9e32962e664e99dadff1d19d`).

Commissioned runtime:
`fantasy_season_v0_36_repack1`, VERSION `0.36`.

Production identities:

- `src/data_sources/espn_league.py`: SHA-256 `84cce5210f851b31d127a066de27207a476a5b1d64345a52c5b523f3b227b8b2`, blob `081cacdc913529497bf0070aa7845a27da7f388b`.
- `src/market_manager.py`: SHA-256 `f8aeb8a642da5d22b5fd9950275477487b0b460f1ffe62f6fca506493b366e80`, blob `3036bac8baad2c70e5f019e365c6796ca85a4447`.
- `src/specialist_trade.py`: SHA-256 `c05859808c85638e825f568aa70713d1e2d3fde768baeccbce8cf0dcf1923221`, blob `79bc906337748025857e504e9a3fc739fa8284e4`.
- `src/trade_timing.py`: SHA-256 `34672c6a7538247969e92f77fa5da20431d5275cea25b2c5eb4f2e622299d476`, blob `b462bd4c3a622c4ee00b12a4543e2b8bbc801e84`.

Runtime commissioning v1 wrote the candidate but validated against stale runtime
test fixtures that lacked normalized `transaction_settings`; 4 trade tests failed
closed and all 4 production paths were rolled back. v2 retained runtime-local
tests unchanged, overlaid the actual runtime production bytes into a fresh clone
of published commit `a404f61...`, and passed the complete published test suite,
compileall, import smoke, exact identities, frozen Oct. 5 probe, and residue
checks. Rollback was false.

## Verified State

- Trade effective-time correction: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**.
- Frozen Oct. 5 transaction settings probe: PASS.
- Frozen Kamara/Bills timing: earliest modeled ownership effect Week 5.
- Frozen Week 4 ownership effect for that package: exactly zero.
- Published test suite over actual runtime production bytes: PASS.
- Published/runtime compileall: PASS.
- Runtime validation residue: NONE.
- Gate A, B1, B2a, B3, Gate B5, multi-K, lineup-lock, and trade-effective-time corrections are commissioned.
- B2b remains deferred / fail-closed / no future IR-capacity credit.
- General K `CARRY2` remains disabled.
- Football-model tuning remains false.

Causal rule: normal trade review latency is real; commissioner early processing
is never assumed. Positive review defers ownership to the next scoring week.
With zero review, locked assets defer and unresolved timing fails closed. Only
zero-review, fully unlocked packages may affect the current week. Automatic
drops/adds share the same effective-time boundary.

## Calendar / Evidence Gates

- Preserve all prior Week 4 prospective captures; never backfill.
- The pre-correction Oct. 5 Kamara -> Bills offer remains evidence only.
- A new prospective decision-time capture is required before current trade action.
- Refresh state again before execution if material roster, injury, market, lock,
  or transaction information changes.
- Week 3 Data/MC closure remains blocked until a fresh complete weekly receipt
  passes through the corrected commissioned authority.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; compose only at complete-roster boundaries.
- Player-only and specialist trade authorities remain distinct.
- Ownership perturbations must respect transaction effective time.
- Manager behavior remains separate from intrinsic football utility.
- `screen != authority`; raw measurements outrank derived classifiers.
- Missing legal coverage fails closed.
- No future IR-capacity credit while B2b is deferred.
- `v0.X` remains a-priori; observed 2026 outcomes may not tune it.

## Exact Next Action

Create a new live Week 4 snapshot and prospective pre-data capture through
commissioned `v0.36-repack1`, verify capture integrity, and rerun all 9 required
weekly decision channels plus operational health.

The fresh receipt must report lineup legality, action/incomplete channels,
trade-effective-time state, lock scopes, source health, dependency identities,
and specialist offer count. Do not reuse or execute the pre-correction Oct. 5
trade frontier.

After the fresh cycle, analyze the exact result before any football action and
update durable memory with the new operational evidence.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `architecture/WEEKLY_DECISION_COMPLETION.md`
- `evidence/WEEK4_TRADE_EFFECTIVE_TIMING_BOUNDARY_2026-10-05.md`
- `evidence/WEEK4_TRADE_EFFECTIVE_TIMING_RUNTIME_COMMISSIONING_2026-10-05.md`
- `roadmap/SEASON_2026.md`
- `roadmap/STATUS.md`
- `../KNOWN_ISSUES.md`
