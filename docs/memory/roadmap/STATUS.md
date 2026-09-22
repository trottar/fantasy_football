# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C channel boundary audit: **COMPLETE / DURABLE**
- Phase 1C DST shadow: **FULLY SOURCE VALIDATED / LOCALLY APPLIED / STAGING NEXT**
- Phase 1C DST runtime: **NOT SYNCHRONIZED**
- Phase 1C K shadow: **DEFERRED BEHIND DST GATE**
- Phase 1C player shadow: **BOUNDARY UNRESOLVED / OLD PLANNED POINT REJECTED**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 week-open capture: **SECURED / VALID / PRE-KICKOFF**

## Phase 1C DST Source Candidate

Boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`

Namespace:
`subsystem.dst.channel`

The source candidate adds a lazy bounded `dst_shadow` recorder and decorates
only the DST public policy wrapper. The K wrapper remains unchanged and
undecorated.

Validated exact technical scope:

1. `src/specialist_policy_v032.py`
2. `src/observability/dst_shadow.py`
3. `tests/test_observability_dst_shadow_v10a.py`
4. `tools/probe_observability_dst_shadow_v10a.py`

Validation:

- targeted pytest: **6 passed in 1.03 s**;
- corrected paired probe: PASS;
- outputs/exception behavior/state: PASS;
- success/error privacy: PASS;
- K non-interference: PASS;
- observer-failure fallthrough: PASS;
- P/D/K cross-channel guard: PASS;
- Python RNG / NumPy RNG / mutable state: preserved;
- full pytest: **497 passed in 47.21 s**;
- full compileall: PASS;
- exact four-path bytes after validation: PASS;
- candidate residue: NONE.

Paired benchmark: baseline `7500 ns`, observed `79800 ns`, incremental `72300 ns`.
The baseline is below the `1,000,000 ns` relative floor, so the relative factor is
non-authoritative; the absolute `1,000,000 ns` limit passes.

Two diagnostic-tooling defects were isolated without invalidating source:

1. preflight v1 incorrectly rejected the staging-helper ownership sentinel;
2. candidate-validation v1 performed an extra sequential RNG-consuming
   comparison without restoring state, despite the canonical benchmark gate
   already passing.

Current classification:

`PHASE1C_DST_CANDIDATE_FULLY_SOURCE_VALIDATED / LOCALLY_APPLIED`

Canonical evidence:
`../evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- DST instrumentation does not authorize K or player instrumentation.
- No observed 2026 outcome may tune a v0.X model.
- Diagnostics remain observers, not decision/control logic.
- Persistent evidence requires a separate authorization gate.
- Validation evidence is bound to the exact candidate byte identity.
- Runtime commissioning follows source publication; it does not precede it.
