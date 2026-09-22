# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Phase M repository/season-roadmap authority transition: **COMPLETE / PUSHED /
  REMOTE VERIFIED**
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C channel boundary audit: **COMPLETE**
- Phase 1C DST shadow: **TARGETED PREFLIGHT NEXT**
- Phase 1C K shadow: **DEFERRED BEHIND DST GATE**
- Phase 1C player shadow: **BOUNDARY UNRESOLVED / OLD PLANNED POINT REJECTED**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 week-open capture: **SECURED / VALID / PRE-KICKOFF**

## Phase 1C Boundary Audit

The existing v1.0A integration map was checked against exact current production
source.

### Player

Planned map point:

`src/transaction_manager.py::evaluate_roster_predictive`

Classification:

`REJECT AS PLAYER-ONLY OBSERVABILITY BOUNDARY`

Reason:

- production calls pass complete `ctx.roster` and complete action `new_roster`;
- transaction-manager roster positions include `K` and `DST`;
- the predictive simulation explicitly handles DST component scoring.

This is a complete-roster response/utility boundary. It may be useful at a
future complete-roster observability layer, but naming it `subsystem.player` would
violate `P ⊕ D ⊕ K`.

A narrower player-only production boundary must be identified before player
instrumentation.

### DST

Accepted outer channel point:

`src/specialist_policy_v032.py::evaluate_defense_channel`

The public wrapper fixes `position="DST"` and routes into specialist policy
machinery whose candidate/configuration comparisons remain within that selected
specialist position. Cross-channel effects are used only at permitted
complete-roster utility/state boundaries.

DST is selected as the first Phase 1C preflight because its current physical
response already exposes explicit defensive components and therefore has the
strongest immediate closure/diagnostic value.

### Kicker

Accepted outer channel point:

`src/specialist_policy_v032.py::evaluate_kicker_channel`

The wrapper fixes `position="K"` and remains a separately gated K channel.

K is deferred until the DST gate is complete. The current K model remains the
deliberately simpler aggregate-yield/team-environment representation pending
prospective kicker closure.

### Audit Result

`PHASE1C_CHANNEL_BOUNDARY_AUDIT=COMPLETE`

No production or runtime source was modified.

Canonical evidence:
`../evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- No observed 2026 outcome may retroactively tune a v0.X model.
- Diagnostics remain observers, not decision/control logic.
- Persistent evidence requires a separate authorization gate.
- Authenticated/raw capture material remains local.
- Validation evidence is bound to the byte identity that produced it.
