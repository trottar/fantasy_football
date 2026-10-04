# Roadmap Status

## Current Frontier

- Runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 roster-wide decision completion: **9/9 COMPLETE MATRIX / SPECIALIST TRADE ACTION FRONTIER BLOCKED BY MULTI-K DEFECT**
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

## B2b Boundary

B2b remains separate and deferred. The v1 frontier audit's five candidates came
from an over-broad parent-record timestamp fallback; corrected claim-local
freshness retained zero qualifying claims. Do not backfill a horizon and do not
credit future IR capacity.

## Next Gate

Create a new decision-time Week 4 snapshot/capture through the commissioned
multi-K correction and rerun the complete nine-channel weekly receipt. Do not
reuse or execute the pre-correction six-offer frontier.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition/trade behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- A disabled general specialist policy is not evidence that a distinct
  league-legal open-slot transaction branch can be omitted.
- No observed 2026 outcome may tune v0.X.
