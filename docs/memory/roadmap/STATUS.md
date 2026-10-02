# Roadmap Status

## Current Frontier

- Runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE / CURRENT IR MOVE-PLUS-ADD VALUE ADAPTER**
- Gate A fail-closed weekly control plane: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B capability closure: **CURRENT IR MOVE-PLUS-ADD VALUE ADAPTER OPEN / B2B DEFERRED**
- Gate B1 specialist current-WAIVER coverage: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2a current IR/open-slot representation: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2b multiweek absence horizon: **DEFERRED / FAIL-CLOSED / CLAIM-LOCAL FRESHNESS AUDIT = 0 QUALIFYING CLAIMS**
- Gate B3 automated multi-asset/unequal player trade search: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Specialist-inclusive trade composition: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Current IR move-plus-add value/capacity adapter: **STRUCTURAL GAP CONFIRMED / PRODUCTION AUTHORIZATION REQUIRED**
- Week 3 Data/MC closure: **BLOCKED PENDING A FRESH COMPLETE WEEKLY RECEIPT**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

Roster-wide completion requires the receipt matrix in
`architecture/WEEKLY_DECISION_COMPLETION.md`. Unsupported required action
coverage is `INCOMPLETE_COVERAGE`; missing/stale required health is
`BLOCKED_HEALTH`; stale material decision information is `CAPTURE_REQUIRED`.

## Trade Coverage Boundary

Gate B3 remains the commissioned player-only authority for bounded 1x1, 1x2, 2x1,
and 2x2 packages. Its cheap screen remains non-authoritative and paired
`market_manager.evaluate_trade` remains predictive authority.

Specialist-inclusive packages are now separately commissioned through
`specialist_trade.evaluate_specialist_trade`. Player ownership and DST/K response
remain channel-separated and compose only at the complete-roster state boundary.
Mixed equal/unequal packages model explicit legal drop/fill normalization.
Guaranteed FREEAGENT fills never imply waiver success, and manager response
remains a separate behavior layer.

Canonical commissioning evidence:
`evidence/WEEKLY_DECISION_GATE_B_SPECIALIST_TRADE_COMPOSITION_RUNTIME_COMMISSIONING_2026-10-01.md`.

## Remaining Capability Boundary

The fresh Week 4 cycle is healthy but incomplete only on the IR/replacement
channel. B2a proves one legal current `IR_MOVE_PLUS_ADD` transition, while source
audit shows the player open-slot adapter and specialist IR-capacity coupling are
absent. This is the active structural production frontier.

B2b remains separate and deferred. The v1 frontier audit's five candidates came
from an over-broad parent-record timestamp fallback; corrected claim-local
freshness retained zero qualifying claims. Do not backfill a horizon.

## Next Gate

Obtain explicit production authorization before changing football/application
logic. If authorized, close only the current IR move-plus-add value/capacity
adapter under the existing B2a legality state and channel/uncertainty boundaries.

Do not rerun the full Week 4 cycle until that coverage is commissioned or fresh
material decision-time information requires a new capture.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition/trade behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
