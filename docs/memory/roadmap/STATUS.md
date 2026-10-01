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
- Gate B3 automated multi-asset/unequal player trade search: **SOURCE-VALIDATED / LOCAL-APPLIED / PUBLICATION PENDING**
- Specialist-inclusive trade composition: **OPEN / COVERAGE GAP**
- Week 3 Data/MC closure: **BLOCKED BY CAPABILITY RECOVERY**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

Roster-wide completion requires the receipt matrix in
`architecture/WEEKLY_DECISION_COMPLETION.md`. Unsupported required action
coverage is `INCOMPLETE_COVERAGE`; missing/stale required health is
`BLOCKED_HEALTH`.

## Gate B2a Commissioned Boundary

B2a is source-published at
`073d36447858f0b23391a0f4cf28e6d71023101a` and runtime-commissioned in
`v0.36-repack1`.

It represents current active-roster capacity, IR occupancy, ESPN-status-qualified
move-to-IR legality, and the immediate open-slot consequence. It does not infer
or propagate a future recovery/absence horizon, and therefore does not make B2b
replacement/temporal capacity complete.

Canonical commissioning evidence:
`evidence/WEEKLY_DECISION_GATE_B2A_IR_ROSTER_STATE_RUNTIME_COMMISSIONING_2026-10-01.md`.

## Known Capability Gaps

- Gate B3 source publication and runtime commissioning;
- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation remain deferred until fresh qualifying evidence;
- specialist-inclusive trade evaluation at the complete-roster boundary.

## Gate B2b Current Classification

Fresh Week 4 source/capture, provenance, and semantic/freshness audits found
quantified ESPN player-scoped return narratives but no structured horizon field
and zero claims satisfying the strict current hard-unavailable + freshness +
quantification + binding guards.

Current classification:
`B2B_ESPN_NARRATIVE_HORIZON_FOUND_BUT_NOT_STRONG_ENOUGH_FAIL_CLOSED`.

No production parser or temporal-capacity propagation patch is authorized from
this evidence. B2b may reopen only on fresh qualifying decision-time evidence.

## Gate B3 Source Boundary

The Gate B3 audit proved the existing player trade evaluator already supports
1x1, 1x2, 2x1, and 2x2 packages with a two-player-per-side cap, explicit
unequal-package post-trade drop/fill effects, and paired predictive MC.

The structural gap was automated enumeration. The validated Gate B3 source
candidate adds a family-balanced cheap package frontier and routes those packages
into the existing `evaluate_trade` predictive authority. The screen remains
non-authoritative and specialist-inclusive packages remain excluded.

Source preflight v2 passed targeted and full repository validation. Corrected
source local-apply v3 passed exact control-root identities plus a fresh
remote-clone overlay with targeted/full pytest, `compileall`, strict memory
health, and diff checks.

Canonical evidence:
`evidence/WEEKLY_DECISION_GATE_B3_MULTI_ASSET_PLAYER_TRADE_SEARCH_SOURCE_VALIDATION_2026-10-01.md`.

## Next Gate

Stage and publish the exact Gate B3 source-validation checkpoint, including the
four validated source/test paths plus the typed durable-memory update and
regenerated schema-2 manifest.

After remote verification, run a separate non-mutating runtime preflight and
explicit runtime commissioning against `v0.36-repack1`.

Then audit specialist-inclusive trade composition as the next separate Gate B
gap. Do not run a fresh roster-wide Week 4 cycle until required remaining Gate B
coverage is commissioned or explicitly not applicable.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
