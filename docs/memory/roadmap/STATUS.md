# Roadmap Status

## Current Frontier

- Runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 roster-wide decision completion: **COMPLETE / ACTION_REQUIRED / FRESH POST-TIMING AUTHORITY**
- Gate A fail-closed weekly control plane: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B capability closure: **CURRENT-WEEK ACTION COVERAGE COMMISSIONED / B2B DEFERRED**
- Gate B1 specialist current-WAIVER coverage: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2a current IR/open-slot representation: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2b multiweek absence horizon: **DEFERRED / FAIL-CLOSED / CLAIM-LOCAL QUALIFYING CLAIMS = 0**
- Gate B3 automated multi-asset/unequal player trade search: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Specialist-inclusive trade composition: **MULTI-K CORRECTION SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Current IR move-plus-add adapter: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED / GATE B5**
- Week 3 Data/MC closure: **UNBLOCKED BY FRESH COMPLETE WEEKLY RECEIPT**
- Active development workstream: **WEEK 3 HISTORICAL REPLAY / V002 OUTCOME AUTHORITY FROZEN / IR TRANSITION CHECK NEXT**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Historical Counterfactual Replay / Regret

- Status: **PHASE-A TOOLING PUSHED / REMOTE VERIFIED** at `b038c6b388f1a4aefc53c45ce1c924ed9e9bdb85` (tree `e59b6e7d2930b42d2a2af8e1e54e14756763c86e`).
- Provenance bootstrap is closed: Weeks 1-2 are reconstructed-only; Week 3 is
  `RECONSTRUCTED_RETROSPECTIVE_REPLAY` overall with frozen rostered-player and
  specialist sub-surfaces but a reconstructed player waiver/free-agent values
  layer.
- Week 3 exact frozen coverage: `174 / 174` rostered QB/RB/WR/TE predictions,
  `24 / 24` owned DST/K predictions, and historical eligibility reproduces the
  captured `40 / 40` actionable specialist frontier in all four frozen pairs.
- Phase-A source: `src/counterfactual_replay.py` SHA-256
  `791af42c910d47967bd371d9feddaf50ae45319f707c3608a10cfee7172606b7`;
  focused pytest `14 passed`; exact isolated full-repository candidate
  `609 passed`, `compileall` PASS, exact 2-path staged allowlist, and
  `git diff --cached --check` PASS.
- The module supplies per-dependency provenance, replay-mode classification,
  immutable hash-addressed Phase-A receipts, frozen rankings/model action, and a
  hard Phase-A/Phase-B outcome firewall. Football candidate evaluation and
  historical outcome attachment are not yet wired.
- Weekly integration: after ordinary prospective closure, replay each completed
  week and retain cumulative structural regression scenarios.
- Modes: `CAUSAL_FROZEN_REPLAY` and
  `RECONSTRUCTED_RETROSPECTIVE_REPLAY`.
- Phase A predictions/model choice freeze before Phase B observed-outcome/oracle
  attachment.
- v0.X outcome-driven empirical tuning remains prohibited.
- Active development focus is the Week 3 previous-week replay checks. The pending
  Week 4 Kamara -> Bills D/ST action remains preserved, unexecuted, and
  state-sensitive, but is not the active development workstream.
- Week 3 replay-input adapter: **IMPLEMENTED / VALIDATED IN THIS CHECKPOINT**.
  Exact input-contract audit found `4 / 4` integrity-valid captures canonically
  linked to `4 / 4` frozen snapshots with zero outcome files read. Adapter source
  `src/historical_replay_input.py` SHA-256 `4145ca8c3eb7673d17c563c834292f2ff9c2333d78644be7c5b710a529d51d42`; test SHA-256 `88265d8dcb5e4f2444d518e482c5a3d641a0ad5b7012c0c33a10718386515504`.
- The first adapter apply candidate was non-mutating and failed correctly during
  its first real-pair probe because it incorrectly required every eligible player
  to exist in the reconstructed values CSV. Source authority showed the
  commissioned evaluator instead uses positive latent value when available, else
  frozen ESPN season/weekly projection fallback. v2 mirrors and validates that
  exact branch.
- Authority-frontier repair probe: all eight required Week 3 action families are
  representable when the immutable adapter state is deep-thawed for authority
  execution and trade timing is normalized from frozen raw ESPN mSettings.
- All four Week 3 raw mSettings artifacts preserve the same 48-hour review and
  individual-game lineup/roster locks; no current ESPN state is substituted.
- Replay-only Phase-A evaluator: **SOURCE-PUBLISHED / REMOTE VERIFIED** at commit
  `58fd202fdcdcfc997d95860df0b51fa63b3b0463`, tree
  `c6e17cacb8e6b20a7c49ce2f9629121cf079294a`; production authority remains
  unchanged, frozen capture values are injected only inside the replay context,
  and uncaptured player-market values remain explicitly reconstructed.
- Validation: 37 focused replay tests, 632 full-repository tests, `compileall`,
  strict memory health, `git diff --check`, and `4 / 4` real Week 3 states through
  a 64-scenario no-outcome commissioning probe.
- Final blind Phase-A freeze: **COMPLETE / IMMUTABLE / RELOAD-HASH VERIFIED**.
  Receipt-set SHA-256:
  `54171a0681a1fd4a36f971fac33e591f1e5d1228b0e4de437f1d67dc9391bc51`.
- Final commissioned/default settings: player MC `16384`, specialist MC `2048`,
  trade MC `4096`, trade frontier limit `6`.
- Receipt candidate counts: `237`, `77`, `75`, `73`; authorized counts:
  `1`, `7`, `4`, `4`.
- Frozen action pattern: lineup ACTION at all four decision points;
  specialist-inclusive trade ACTION at the final three; all other action
  families HOLD at all four.
- Independent receipt-set verifier confirmed exact set/file/receipt hashes and
  `8 / 8` channel selections per receipt with outcome reads `0`, Phase B `NONE`,
  and no mutation.
- Week 3 Phase-B authority V001 remains immutable predecessor evidence; manifest
  `892763082b1a03e5f9789c31e7c2961692392e027413611403ffa7e93649fd11`.
- V001 correction: `144 / 144` covered positive Phase-A asset IDs only because
  its collector excluded IDs `<= 0`.
- Corrected V002 authority: **CAPTURED / IMMUTABLE / HASH-VERIFIED**; manifest
  `00946e70c53cfd3eeab74c74b2397a196c514ab75ac437246079b6f6383ab4db`.
- Signed Phase-A universe: `172 = 144` positive + `28` negative D/ST IDs; direct
  ESPN exact Week 3 actuals: `172 / 172`.
- Negative D/ST ESPN actuals, position shape, and pro-team mapping: `28 / 28`.
- Historical boxscore remains `6 / 6` matchups, `12` lineup sides, `199`
  entries, `108` starters; user starter sum reproduces the final team score.
- nflverse cross-check remains positive-ID mapping `142 / 144`, direct Week 3
  candidate rows `105`; cached PBP SHA-256 remains
  `f4e671b46c24a81b6d57b9581367a2100afe4bf24f0dd34e987cf44f65774286`.
- Sufficiency audit: frozen user rosters and lineup candidates have realized
  response coverage; Week 3 trade football effect is zero under the frozen
  48-hour review period.
- Remaining question: compact Phase-A `IR_MOVE_PLUS_ADD` rows omit the explicit
  `move_to_ir` ID retained by commissioned B2a authority.
- Raw authenticated ESPN remains local-only.
- Replay next gate: resolve the IR open-slot transition from frozen
  decision-time evidence before Phase-B scorer implementation.

## Blocking Recovery Contract

Roster-wide completion requires the receipt matrix in
`architecture/WEEKLY_DECISION_COMPLETION.md`. Unsupported required action coverage
is `INCOMPLETE_COVERAGE`; missing/stale required health is `BLOCKED_HEALTH`; stale
material decision information is `CAPTURE_REQUIRED`.

## Current IR Adapter Boundary

The fresh Week 4 cycle is operationally healthy and incomplete only on the
IR/replacement channel. B2a proves exactly one current legal
`IR_MOVE_PLUS_ADD` transition: one unlocked `OUT` QB can move to the one open IR
slot, opening one active-roster slot.

Production authorization is granted. The first three source preflights are
superseded and non-mutating:

- v1 failed during disposable Git-clone cleanup on Windows;
- v2 reached full pytest with 576 passed and one stale B4 contract assertion;
- v3 failed because the package applied a test-file transform to the weekly source
  transform list.

Post-v3 source audit also invalidated the v2 design as a release candidate:
player candidate locking was weaker than the commissioned kickoff-aware lock
boundary, and the adapter could silently skip a league-legal additional-kicker
open-slot branch while claiming IR-channel completeness.

The next candidate must therefore be redesigned, not merely repackaged.

That redesign is now source-published and runtime-commissioned. Source checkpoint
`d254e569f7c4dc5a3e27f85f6ba1386e4a6c98eb` passed exact-tree publication.
Runtime commissioning v1 failed only because the sparse runtime lacked one
targeted regression and rolled back cleanly. Corrected v2 sourced all six
targeted regressions from published control-root blobs, passed targeted/full
runtime pytest, compileall, import smoke, identity/residue checks, and
commissioned the three production runtime files.

## Specialist Trade Multi-K Boundary

The October 3 fresh Gate B5 cycle passed operational health and all nine required
coverage channels, but its sole action channel produced six specialist-inclusive
trade offers. Exact reproduction and decomposition showed four offers ending with
two K assets and receiving future best-of-week kicker option value while general
K `CARRY2` remains disabled.

Classification:
`SPECIALIST_TRADE_MULTI_K_FIXED_OWNERSHIP_BOUNDARY_DEFECT`.

The authorized correction rejects final user or partner trade states with more
than one K after legal normalization, while preserving multi-DST ownership.
Source checkpoint `285f34669e60593153b7a30f18016669c7b73f7e` is pushed/remote-verified and
the exact source is runtime-commissioned in `v0.36-repack1`; focused behavior,
targeted/full pytest, compileall, identity, import-root, and residue checks passed.

The October 3 six-offer frontier is evidence only and is not executable.

## Weekly Lineup Lock Authority

The October 4 post-multi-K fresh cycle passed operational health and emitted all
nine receipt rows, but its lineup action selected locked-bench Jakobi Meyers into
the starting lineup. Source inspection proved `_default_lineup` computed lock
metadata without constraining `optimize_lineup` or `action_required`.

Classification:
`WEEKLY_LINEUP_LOCK_AUTHORITY_CONSTRAINT_DEFECT`.

The authorized correction freezes locked starters in their current slots, excludes
locked bench players, optimizes only unlocked players over remaining legal slots,
and fails closed when required lock timing or current slot legality is unresolved.
Source checkpoint `5dba8ea39f5b0cdeb16203b7a423cc6fe7849b52` is pushed/remote-verified and
the exact source is runtime-commissioned in `v0.36-repack1`; published identity,
focused frozen-Oct. 4 behavior, targeted/full pytest, compileall, import-root, and
residue checks passed.

The October 4 four-offer specialist frontier is diagnostic evidence only until a
fresh post-commissioning weekly cycle reauthorizes current actions.

## B2b Boundary

B2b remains separate and deferred. The v1 frontier audit's five candidates came
from an over-broad parent-record timestamp fallback; corrected claim-local
freshness retained zero qualifying claims. Do not backfill a horizon and do not
credit future IR capacity.

## Trade Effective Timing Boundary

The October 5 fresh post-lineup-lock cycle passed all nine coverage channels,
operational health, and lineup legality, but its sole action was an
Alvin Kamara -> Bills D/ST specialist trade. The incoming Bills D/ST was already
locked, while frozen ESPN settings showed a 48-hour trade review period and
individual-game roster/lineup locks.

Classification:
`TRADE_EFFECTIVE_TIMING_LOCK_BOUNDARY_DEFECT`.

Both player and specialist trade evaluators were applying post-trade ownership
immediately to the current scoring week. The correction now normalizes ESPN transaction timing, defers positive-review
packages to the next scoring week, fails closed on unresolved zero-review lock
timing, and temporally splices ownership only from the legal effective week.
Source checkpoint `a404f61c77a1449b8275928d877d3c39c0a624a6` is
pushed/remote-verified and the exact four production paths are commissioned in
`v0.36-repack1`.

Runtime commissioning v1 rolled back after validating against stale runtime test
fixtures that lacked the new transaction settings. Corrected v2 kept runtime
tests unchanged, overlaid the actual runtime production bytes into the exact
published checkout, and passed the complete published suite, compileall, frozen
Oct. 5 effective-time probe, identity, and residue checks.

The Oct. 5 01:26 UTC snapshot/capture remain valid prospective evidence, but
the pre-correction Kamara -> Bills offer is not executable.

A fresh corrected cycle at snapshot UTC
`2026-10-05T15:22:25.546621+00:00` passed operational health, all nine required
channels, and lineup legality. The only action channel is specialist-inclusive
trade. The sole actionable offer is again Alvin Kamara -> Bills D/ST, now valued
under the corrected temporal boundary: 4096 predictive scenarios, our season PPG
delta `+0.5872324506228646`, our `P(better)=0.61767578125`, partner season PPG
delta `+0.7639320734790934`, partner `P(better)=0.599853515625`, and separate
uncalibrated `P(accept)=0.6579706454137803`.

The fresh 48-hour trade-review state makes the offer Week 5 effective with
exactly zero Week 4 ownership effect. No transaction has been executed.

The compact specialist ranked row does not retain the evaluator's `trade_timing`
object. A read-only extractor recovered timing from the matching frozen snapshot
through the commissioned timing authority without rerunning snapshot, capture,
MC, or the football decision. This is a nonblocking representation gap.

## Next Gate

Resolve the Week 3 IR open-slot transition from frozen decision-time evidence.
Determine whether every Phase-A `IR_MOVE_PLUS_ADD` candidate can be joined
deterministically to the unique legal `move_to_ir` transition required by
commissioned Gate B2a before its add frontier was emitted.

If exact reconstruction is possible, record the join and proceed to Phase-B
scorer implementation without mutating Phase A. Otherwise classify a
state-representation gap and repair replay representation before scoring.

Do not attach Phase B until this transition boundary and scorer joins are
validated. No observed Week 3 result may tune v0.X.

The Week 4 Kamara -> Bills D/ST side-state remains preserved and unexecuted.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition/trade behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- A disabled general specialist policy is not evidence that a distinct
  league-legal open-slot transaction branch can be omitted.
- No observed 2026 outcome may tune v0.X.
