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
- Gate B2b multiweek absence horizon: **BLOCKED / EXPLICIT HORIZON FIELD ABSENT**
- Automated multi-asset/unequal trade search: **OPEN / COVERAGE GAP**
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

- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation;
- automated player trade package search beyond one-for-one;
- specialist-inclusive trade evaluation at the complete-roster boundary.

## Next Gate

Complete the B2a runtime-commissioning memory checkpoint through isolated
staging, guarded publication, and read-only remote verification.

After that checkpoint is remote-durable, begin B2b with a narrow audit of
explicit decision-time absence/return-horizon sources and capture
representation. Do not infer a horizon from injury type/start date or generic
slot compatibility.

Do not run a fresh roster-wide Week 4 cycle until remaining Gate B coverage is
commissioned or explicitly not applicable.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Manager acquisition behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
