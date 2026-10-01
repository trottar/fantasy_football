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
- Gate B2a current IR/open-slot representation: **PATCHABLE / SOURCE PREFLIGHT PENDING**
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

## Gate B2 Audit Classification

The Week 4 sanitized audits found one configured/open IR slot, no current IR
occupant, and one ESPN `OUT` player. Normalized `injury_status` matches raw ESPN
`player.injuryStatus` for all 16 roster rows. All 16 players advertise IR in
`eligibleSlots`, including active players, so that field is generic slot
compatibility rather than current IR eligibility.

No normalized or raw ESPN field provides an explicit multiweek absence/return
horizon. B2 therefore splits:

- **B2a:** represent current ESPN-status-qualified IR/open-slot transitions and
  resulting immediate capacity state;
- **B2b:** remain fail-closed for multiweek capacity/replacement valuation until
  explicit decision-time horizon evidence exists.

The B2a source candidate changes exactly three source/test paths and preserves
commissioned B1/player/specialist physics. Source-preflight v1 failed before
modification only because the prior `CURRENT.md` crossed strict memory-health's
soft-size threshold on Windows; no operator full B2a source validation completed.

Canonical audit evidence:
`evidence/WEEKLY_DECISION_GATE_B2_IR_ABSENCE_AUDIT_2026-10-01.md`.

## Known Capability Gaps

- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation;
- automated player trade package search beyond one-for-one;
- specialist-inclusive trade evaluation at the complete-roster boundary.

## Next Gate

After this active-memory maintenance checkpoint is durable, regenerate and run
the unchanged B2a source preflight against the new remote predecessor. Do not
advance to B2a local apply unless targeted/full tests, compileall, strict memory
health, diff checks, and exact result identities all pass.

Do not run a fresh roster-wide Week 4 cycle until the remaining Gate B coverage
is commissioned or explicitly not applicable. Week 3 closure remains blocked
until a later fresh complete receipt matrix passes.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Current IR legality and future roster-capacity value are separate state layers.
- Do not infer a return horizon from injury type, start date, or generic slot
  compatibility.
- Manager acquisition behavior remains separate from intrinsic football utility.
- User examples do not define production search scope.
- `screen != authority`; raw measurements outrank derived classifiers.
- No observed 2026 outcome may tune v0.X.
