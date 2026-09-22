# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

Phase 1C DST source candidate is fully source validated and locally applied to
the control root. Repository staging/publication is the next gate; the
commissioned runtime has not been synchronized.

Source predecessor:
`37f841b7aec0280fa695f60e5285ff34646f9a10`.

Exact technical candidate scope:

1. `src/specialist_policy_v032.py`
2. `src/observability/dst_shadow.py`
3. `tests/test_observability_dst_shadow_v10a.py`
4. `tools/probe_observability_dst_shadow_v10a.py`

Only `evaluate_defense_channel` is observed at `subsystem.dst.channel`.
`evaluate_kicker_channel` remains undecorated.

Validation lineage:

- preflight v1 failed only because its validator rejected the staging helper's
  intentional `.checkpoint_stage_id` sentinel;
- corrected preflight passed non-interference/privacy/RNG/mutable-state,
  observer-failure, and P/D/K gates;
- candidate validation v1 passed targeted pytest (6 passed) but exposed an
  invalid extra probe comparison that did not restore RNG/mutable state;
- validation continuation fixed only the harness and passed corrected paired
  probe, full pytest (497 passed), compileall, exact-byte, diff, and residue
  gates.

Canonical evidence:
`../evidence/PHASE1C_DST_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

## Resume

Follow `../CURRENT.md`'s `Exact Next Action`.

Stage the exact validated source + memory scope against predecessor `37f841b7...`.
Do not synchronize the runtime until the source checkpoint is pushed and remotely
verified.

K and player instrumentation remain separately gated.
