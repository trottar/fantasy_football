# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1c_k_shadow_preflight
memory_refinement_step: M0_M7_complete_durable
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Advance the next separately gated Phase 1C specialist channel while
preserving `P ⊕ D ⊕ K`.

Phase 1C DST is complete, durable, source-published, runtime-commissioned, and
remote verified. The next task is a diagnostic-only preflight for the accepted K
outer channel boundary. Player instrumentation remains blocked pending a narrower
QB/RB/WR/TE production boundary.

## Current Work Item

**Phase 1B closure instrumentation: COMPLETE / SOURCE PUBLISHED / RUNTIME
COMMISSIONED.**

**Phase 1C channel boundary audit: COMPLETE / DURABLE.**

**Phase 1C DST shadow: COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED.**

**Phase 1C K shadow: TARGETED PREFLIGHT NEXT / NO SOURCE CHANGE YET.**

**Phase 1C player shadow: BOUNDARY UNRESOLVED / UNCHANGED.**

The Week 3 week-open prospective capture remains
**SECURED / VALID / PRE-KICKOFF**.

Canonical Phase 1C DST validation record:
`evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

## Verified State

- `v0.36-repack1` remains the commissioned runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1C DST source checkpoint:
  `9d174a25db3990f35dbf7a13b5421253c265baa9`.
- Published source tree:
  `65a1a8fed7f24906047b9e575d3ce9171ff4a9d7`.
- Phase 1C DST durable-memory closure commit:
  `c5eaa69613ca00a85081b76e37ab03a0d7aacea3`, tree
  `cfb22b38c6414535796cac0695033688a8398696`, pushed and remote verified.
- DST observer boundary:
  `src/specialist_policy_v032.py::evaluate_defense_channel`
  at `subsystem.dst.channel`.
- Only the DST wrapper is decorated. The K wrapper remains undecorated.
- New bounded observer:
  `src/observability/dst_shadow.py`.
- Persistent runtime evidence remains **DISABLED**.
- Corrected diagnostic preflight passed success/error equivalence, privacy,
  observer-failure fallthrough, P/D/K cross-channel guard, Python/NumPy RNG, and
  mutable-state preservation.
- Candidate validation v1 passed targeted pytest (**6 passed in 1.03 s**) but
  exposed an extra probe-harness comparison that failed to restore RNG/mutable
  state between sequential calls. The canonical paired benchmark already passed.
- Candidate validation continuation fixed only that harness, retained the DST
  production/shadow/test payloads, and passed:
  - paired probe: PASS;
  - full pytest: **497 passed in 47.21 s**;
  - full compileall: PASS;
  - exact four-path bytes: PASS;
  - candidate residue: NONE.
- Validated technical SHA-256:
  - `src/specialist_policy_v032.py`:
    `6ce0392a71535acd0c8c673c198ba0ba98ff06f6d8274830265ae9391d6c6be2`;
  - `src/observability/dst_shadow.py`:
    `e05be60c597d592dbd16e91e546b8badb08175bb23841b7c3d616e08a7a927b9`;
  - `tests/test_observability_dst_shadow_v10a.py`:
    `d10c5dd486cad98ba2341e1c23b13dcbabd9c42ba5eaa2ba37bc51beb2cc5a31`;
  - `tools/probe_observability_dst_shadow_v10a.py`:
    `b6ef38d427f94f721fa1bf6cf54f5cc9bf8466ff0169e1fb3d6393607b98f08d`.
- Paired candidate timing: baseline `7500 ns`, observed `79800 ns`, incremental
  `72300 ns`. The baseline is below the `1,000,000 ns` relative floor, so the
  relative factor is non-authoritative; the absolute gate passes.
- This is observability only. Specialist football policy, DST physics, K policy,
  player policy, scoring, manager behavior, and recommendation authority are
  unchanged.
- The commissioned `v0.36-repack1` runtime is synchronized with the exact DST
  production observer bytes.
- Runtime commissioning passed dedicated DST pytest (**6 passed in 0.85 s**),
  paired output/exception/state/privacy/RNG/mutable-state gates, K
  non-interference, observer-failure fallthrough, P/D/K guard, full runtime
  pytest (**353 passed in 45.97 s**), compileall, final target identity, and
  residue cleanup.
- Runtime paired timing: baseline `7500 ns`, observed `81900 ns`, incremental
  `74400 ns`; persistent sink remains disabled.

## Calendar / Evidence Gates

- Week 3 week-open capture remains **SECURED / VALID / PRE-KICKOFF**.
- Preserve separate decision-time captures for consequential Week 3 lineup,
  waiver, trade, and specialist actions.
- No observed 2026 outcome may tune the v0.X model.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.
- Week 5 remains the preferred broader v1.0 observability commissioning target.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players; DST only with DST; K only with K.
- `evaluate_defense_channel` remains DST-only.
- `evaluate_kicker_channel` remains undecorated and separately gated.
- Cross-channel coupling belongs only at complete-roster utility/state boundaries.
- Observability remains non-interfering and non-authoritative.
- Persistent evidence requires a separate authorization gate.

## Exact Next Action

Construct one diagnostic-only targeted preflight for the exact current
`src/specialist_policy_v032.py::evaluate_kicker_channel` boundary.

The preflight must not modify production source. It should establish the K
observer contract before instrumentation:

- boundary identity: `subsystem.k.channel`;
- subsystem: `k`;
- bounded in-memory only;
- no arguments, returned policy payloads, private/authenticated data, or exception
  messages retained;
- production result/exception wins over observer behavior;
- Python/NumPy stochastic state and relevant mutable input state remain unchanged;
- output/exception behavior is paired against the unobserved call;
- overhead uses the existing benchmark-gate contract;
- persistent sink remains disabled;
- DST observer behavior and player channel remain unchanged.

Do not instrument K or player production source during this preflight.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `architecture/SPECIALIST_CHANNELS.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/PHASE1C_CHANNEL_BOUNDARY_AUDIT_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/PHASE1C_DST_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `roadmap/STATUS.md`
- `patches/PATCH_PROTOCOL.md`
