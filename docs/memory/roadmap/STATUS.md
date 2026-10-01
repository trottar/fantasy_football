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
- Gate B2a current IR/open-slot representation: **SOURCE-VALIDATED / LOCAL-APPLIED / PUBLICATION PENDING**
- Gate B2b multiweek absence horizon: **BLOCKED / EXPLICIT HORIZON FIELD ABSENT**
- Automated multi-asset/unequal trade search: **OPEN / COVERAGE GAP**
- Specialist-inclusive trade composition: **OPEN / COVERAGE GAP**
- Week 3 Data/MC closure: **BLOCKED BY CAPABILITY RECOVERY**
- Phase 1E persistence: **RUNTIME COMMISSIONED / DISABLED / ACTIVATION NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

Roster-wide completion requires the receipt matrix in
`architecture/WEEKLY_DECISION_COMPLETION.md`: lineup/availability, broad player
actions, DST, kicker, IR/injury-replacement state, required trade families,
prospective provenance, and weekly operational health. Unsupported coverage is
`INCOMPLETE_COVERAGE`; stale/missing health is `BLOCKED_HEALTH`.

## Gate B2a Source Boundary

B2a represents current IR/open-slot state only. The source-preflight v2 package
`weekly_decision_gate_b2a_ir_roster_state_source_preflight_v2_20261001`
passed against predecessor `f6900878c97ef4dd9148b924fa41167337086a2c`
with targeted regressions, full repository pytest, `compileall`, strict memory
health, diff checks, and exact result identities.

The validated candidate changes exactly:

- `src/ir_roster_state.py`;
- `src/weekly_decision_cycle.py`;
- `tests/test_weekly_decision_gate_b2a_ir_roster_state.py`.

It preserves commissioned player/DST/K football physics and does not authorize a
replacement recommendation without temporal capacity evidence. This local
checkpoint does not publish or commission the runtime.

Canonical source-validation evidence:
`evidence/WEEKLY_DECISION_GATE_B2A_IR_ROSTER_STATE_SOURCE_VALIDATION_2026-10-01.md`.

## Known Capability Gaps

- B2a source publication and runtime commissioning;
- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation;
- automated player trade package search beyond one-for-one;
- specialist-inclusive trade evaluation at the complete-roster boundary.

## Next Gate

Stage and publish the exact B2a source-validation checkpoint. After remote
verification, run a separate non-mutating runtime preflight and explicit runtime
commissioning against `v0.36-repack1`.

Do not reopen the passed B2 audits or source preflight without new evidence. Do
not run a fresh roster-wide Week 4 cycle until remaining Gate B coverage is
commissioned or explicitly not applicable.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Do not infer a return horizon from injury type, start date, or generic slot
  compatibility.
- Manager acquisition behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
