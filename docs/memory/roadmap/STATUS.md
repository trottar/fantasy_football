# Roadmap Status

## Current Frontier

- Runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Gate A fail-closed weekly control plane: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B capability closure: **AUTHORIZED / ACTIVE**
- Gate B1 specialist current-WAIVER coverage: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2 audit: **COMPLETE / SPLIT INTO B2A + B2B**
- Gate B2a current IR/open-slot representation: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Gate B2b multiweek absence horizon: **DEFERRED / FAIL-CLOSED / CURRENT ESPN NARRATIVES NOT AUTHORITATIVE**
- Gate B3 automated multi-asset/unequal player trade search: **SOURCE-PUBLISHED / RUNTIME-COMMISSIONED**
- Specialist-inclusive trade composition: **SOURCE-VALIDATED / LOCAL-APPLIED / PUBLICATION + RUNTIME COMMISSIONING PENDING**
- Week 3 Data/MC closure: **BLOCKED BY CAPABILITY RECOVERY**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

Roster-wide completion requires the receipt matrix in
`architecture/WEEKLY_DECISION_COMPLETION.md`. Unsupported required action
coverage is `INCOMPLETE_COVERAGE`; missing/stale required health is
`BLOCKED_HEALTH`.

## Gate B3 Commissioned Boundary

Gate B3 remains the commissioned player-only trade authority. It provides bounded
family-balanced 1x1, 1x2, 2x1, and 2x2 player-package search. The cheap screen is
non-authoritative and paired `market_manager.evaluate_trade` remains predictive
authority.

The specialist patch does not modify `src/market_manager.py` and does not convert
Gate B3 into a cross-channel evaluator.

## Specialist Trade Source Boundary

Read-only audit v3 classified the gap as
`B_SPECIALIST_TRADE_COMPOSITION_PRIMITIVES_PRESENT_ADAPTER_PLUS_MIXED_CAPACITY_GAP_PATCHABLE`.

Authorized source preflight v2 and source local apply v1 have now validated the
smallest production repair:

- a separate `specialist_trade` authority handles packages containing DST and/or K;
- player ownership is propagated separately;
- DST and K ownership response uses existing specialist machinery;
- P/D/K composition occurs only at the complete-roster boundary;
- mixed equal/unequal packages model explicit legal drop/fill normalization;
- guaranteed specialist FREEAGENT fill is used only to restore the same-channel
  roster minimum when necessary;
- waiver success is never assumed;
- manager response remains a separate behavior layer;
- `screen_authority=false`.

The source is locally applied but not yet source-published or runtime-commissioned.

Canonical evidence:
`evidence/WEEKLY_DECISION_GATE_B_SPECIALIST_TRADE_COMPOSITION_SOURCE_VALIDATION_2026-10-01.md`.

## Known Capability Gaps

- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation remain deferred until fresh qualifying evidence;
- specialist-inclusive trade source publication and exact runtime commissioning
  remain unfinished;
- Week 4 cannot be called roster-wide complete until those runtime coverage
  receipts pass.

## Next Gate

Publish the exact validated source+memory checkpoint through isolated staging and
guarded publication, then commission those exact source identities into
`v0.36-repack1`. Do not run a fresh roster-wide Week 4 cycle before commissioning.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition/trade behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
