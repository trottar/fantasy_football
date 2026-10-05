# Roadmap Status

## Current Frontier

- Runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 roster-wide decision completion: **TRADE EFFECTIVE-TIMING DEFECT / SOURCE CANDIDATE LOCAL-APPLIED / RUNTIME COMMISSIONING PENDING**
- Gate A fail-closed weekly control plane: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B capability closure: **CURRENT-WEEK ACTION COVERAGE COMMISSIONED / B2B DEFERRED**
- Gate B1 specialist current-WAIVER coverage: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2a current IR/open-slot representation: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2b multiweek absence horizon: **DEFERRED / FAIL-CLOSED / CLAIM-LOCAL QUALIFYING CLAIMS = 0**
- Gate B3 automated multi-asset/unequal player trade search: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Specialist-inclusive trade composition: **MULTI-K CORRECTION SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Current IR move-plus-add adapter: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED / GATE B5**
- Week 3 Data/MC closure: **BLOCKED PENDING A FRESH COMPLETE WEEKLY RECEIPT**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

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
immediately to the current scoring week. The authorized candidate now normalizes
ESPN transaction timing, defers positive-review-window packages to the next
scoring week, fails closed on unresolved zero-review lock timing, and temporally
splices ownership only from the legal effective week. The exact nine-path
candidate passed source preflight v4 and is locally applied/validated in the
control root; runtime commissioning is still pending.

The Oct. 5 snapshot/capture remain valid prospective evidence, but the
pre-correction Kamara -> Bills offer is not executable.

## Next Gate

Stage and publish the exact nine-path trade-effective-timing source/test candidate
together with its durable-memory update. Then separately commission the published
production source into `v0.36-repack1` and take a new decision-time snapshot,
prospective capture, and complete nine-channel weekly receipt before any trade
execution.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition/trade behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- A disabled general specialist policy is not evidence that a distinct
  league-legal open-slot transaction branch can be omitted.
- No observed 2026 outcome may tune v0.X.
