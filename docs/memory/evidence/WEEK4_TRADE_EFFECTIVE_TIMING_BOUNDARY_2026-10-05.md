# Week 4 Trade Effective Timing Boundary - 2026-10-05

---
evidence_type: structural_authority_defect
status: SOURCE_CANDIDATE_LOCAL_APPLIED_VALIDATED
football_model_tuning: false
reference_remote: 6baebc139e82decaf311adf4671518dfa4e100f7
runtime_release: v0.36-repack1
internal_version: "0.36"
nfl_week: 4
---

## Trigger Evidence

The fresh post-lineup-lock Week 4 cycle produced:

- snapshot UTC `2026-10-05T01:26:55.901034+00:00`;
- prospective capture UTC `2026-10-05T01:26:56.516701+00:00`;
- capture integrity PASS;
- pre-data firewall CLOSED;
- operational health PASS;
- all 9 required receipt channels present;
- lineup `PASS / HOLD:LINEUP_AVAILABILITY`;
- lineup legality PASS;
- no lineup changes;
- sole action channel `trade_specialist_inclusive`;
- exactly one actionable specialist offer.

The offer was:

- give Alvin Kamara;
- receive Bills D/ST;
- partner Clam Jammers;
- modeled season delta `+0.4410795191999014` PPG;
- modeled `p_better = 0.57666015625`;
- modeled `p_accept = 0.6670369822632631`.

A read-only offer audit established:

- Alvin Kamara: UNLOCKED;
- Bills D/ST: LOCKED;
- partner auto-drop Kendre Miller: UNLOCKED;
- partner auto-add Falcons D/ST: UNLOCKED;
- no unknown lock state among involved assets.

The offer therefore touched a locked incoming asset.

## Direct ESPN Settings Evidence

A read-only audit of the exact frozen `mSettings` payload from the same Oct. 5
snapshot established:

- `tradeSettings.revisionHours = 48`;
- `tradeSettings.vetoVotesRequired = 4`;
- `rosterSettings.lineupLocktimeType = INDIVIDUAL_GAME`;
- `rosterSettings.rosterLocktimeType = INDIVIDUAL_GAME`;
- `acquisitionSettings.transactionLockingEnabled = false`.

The diagnostic emitted only sanitized settings; raw authenticated responses,
cookies, league IDs, owner IDs, and other private identifiers were not emitted.

## Source Diagnosis

`specialist_trade.evaluate_specialist_trade` and
`market_manager.evaluate_trade` both modeled post-trade ownership as if it existed
immediately in the current scoring week. Neither authority had a shared
transaction-effective-time boundary.

The specialist path could also normalize an incoming cross-position asset to
bench state with `lineup_locked = False`, allowing an already-locked incoming
asset to participate in a synthetic current-week counterfactual.

Classification:

`TRADE_EFFECTIVE_TIMING_LOCK_BOUNDARY_DEFECT`.

The defect is structural state/causality representation, not empirical
calibration. The fresh Oct. 5 snapshot/capture remain valid prospective evidence,
but the sole trade action emitted by the pre-correction runtime is not executable
authority.

## Authorized Structural Correction

The user explicitly authorized the correction.

The candidate introduces a shared `src/trade_timing.py` authority and updates
both player and specialist trade evaluation.

v0.X causal rule:

1. Normalize ESPN trade-review and lineup/roster-lock settings into decision-time
   state.
2. Never assume commissioner early processing.
3. A positive configured review window defers modeled ownership until the next
   scoring week.
4. With zero review hours, a locked affected asset defers the package to the next
   week.
5. With zero review hours, unresolved affected-asset lock timing fails closed.
6. Only zero-review, fully unlocked packages may alter the current scoring week.
7. Preserve baseline ownership before the effective week and splice post-trade
   state only from the effective week onward.
8. Deferred `delta_current_week` is exactly zero.
9. Automatic post-trade drops/adds share the same effective-time boundary.
10. Preserve player-only versus specialist authority and `P ⊕ D ⊕ K`.
11. Manager response remains a separate behavior layer.

For the exact frozen Kamara/Bills package, the real-settings probe resolves the
earliest modeled ownership effect to Week 5.

## Validation Lineage

Source preflight v1 was non-mutating and failed one targeted legacy regression
because the new timing-settings guard ran before specialist authority rejected a
player-only package.

Source preflight v2 retained the timing design and corrected that validation
order. It reached full pytest with `594 passed / 1 failed`; the symmetric
player-trade legacy regression showed the player authority also needed to reject
DST/K packages before requiring timing settings.

Source preflight v3 retained both authority-order fixes. Targeted pytest, the
real Oct. 5 settings/timing probe, full pytest (`595 passed`), compileall, and
strict memory health passed. It failed only `git diff --check` because the package
renderer produced one blank line at EOF in the specialist test file.

Source preflight v4 changed no production semantics. It normalized that rendered
test EOF and resumed from the last validated gate. Result:

- exact changed paths: 9 / exact;
- ESPN transaction settings normalization: PASS;
- positive review-window boundary: PASS;
- zero-review unlocked current-week behavior: PASS;
- zero-review locked deferral: PASS;
- zero-review unresolved timing: FAIL-CLOSED;
- player-trade deferred current-week delta: zero / PASS;
- specialist-trade deferred current-week delta: zero / PASS;
- specialist complete-state temporal splice: PASS;
- search-level missing timing evidence: FAIL-CLOSED;
- real Oct. 5 Kamara/Bills effective week: 5 / VERIFIED;
- targeted pytest: carried-forward PASS from v3;
- full pytest: carried-forward PASS from v3 / `595 passed`;
- compileall: carried-forward PASS from v3;
- strict memory health: carried-forward PASS from v3;
- exact rendered EOF normalization: PASS;
- `git diff --check`: PASS;
- football-model tuning: false.

Local apply v1 failed before write because it incorrectly required all
remote-tracked predecessor paths to exist in the sparse control root.

Local apply v2 rendered the exact candidate in a fresh clone pinned to
`6baebc139e82decaf311adf4671518dfa4e100f7`, accepted absent reviewed
control-root paths as safe-to-create, and post-write validated all nine result
identities. State: `LOCAL-APPLIED / VALIDATED`.

## Exact Candidate Identities

Production:

- `src/data_sources/espn_league.py`
  - SHA-256 `84cce5210f851b31d127a066de27207a476a5b1d64345a52c5b523f3b227b8b2`
  - Git blob `081cacdc913529497bf0070aa7845a27da7f388b`
- `src/market_manager.py`
  - SHA-256 `f8aeb8a642da5d22b5fd9950275477487b0b460f1ffe62f6fca506493b366e80`
  - Git blob `3036bac8baad2c70e5f019e365c6796ca85a4447`
- `src/specialist_trade.py`
  - SHA-256 `c05859808c85638e825f568aa70713d1e2d3fde768baeccbce8cf0dcf1923221`
  - Git blob `79bc906337748025857e504e9a3fc739fa8284e4`
- `src/trade_timing.py`
  - SHA-256 `34672c6a7538247969e92f77fa5da20431d5275cea25b2c5eb4f2e622299d476`
  - Git blob `b462bd4c3a622c4ee00b12a4543e2b8bbc801e84`

Tests:

- `tests/test_espn_league_v020.py`
  - SHA-256 `321a2b7d5d0f135e6979f7e4932142c6d229f8a6807599cfb12c08f71cfda459`
  - Git blob `e898928a3f52067b28f0fb95c65d4cf5378c698a`
- `tests/test_market_manager_v030.py`
  - SHA-256 `9f002f6299d3db420e958e5ce964c2524a8e87247161ff67b51c493538c82c8e`
  - Git blob `931ec929a96ffcdce6d021484b59e910a0a99a19`
- `tests/test_trade_effective_timing.py`
  - SHA-256 `e301e2aebb2ccbf2aa60b2bfff328488b88ca066d6681b7c6cfce689bca54713`
  - Git blob `475ae5642bb6b2a118083f2c49394f25dcd295a9`
- `tests/test_weekly_decision_gate_b_multi_asset_player_trade_search.py`
  - SHA-256 `3b5e4dc22d578a7c80170f17f2097f39fe97fa303d8076b8f2f27833796b9aca`
  - Git blob `c1810ea385d13f26d9099760f8a2983b726b89eb`
- `tests/test_weekly_decision_gate_b_specialist_trade_composition.py`
  - SHA-256 `5864616b5b0a7e75ba0a33972b9a1a1aea4ddce13eda4bd410c6d69152dd4885`
  - Git blob `1a20978a2df8c82b34dc558cd20d4683669c2175`

## Decision Boundary

The source correction is locally applied but not yet staged, published, or
runtime-commissioned.

The commissioned runtime remains pre-correction. Do not execute the current
Kamara -> Bills D/ST offer and do not treat the raw Oct. 5
`COMPLETE / ACTION_REQUIRED` state as executable roster-wide authority.

Next: stage and publish the exact source+memory checkpoint, then separately
commission the exact published production source into `v0.36-repack1`, then take
a new prospective decision-time capture and rerun the complete nine-channel
cycle.

B2b remains **DEFERRED / FAIL-CLOSED / NO FUTURE CAPACITY CREDIT**.

`durable_memory_updated: true`
