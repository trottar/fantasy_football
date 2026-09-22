# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

Phase 1B recovery/reconstruction has advanced past source validation.

The exact fresh v2 candidate byte identity passed:
- retained-byte verification;
- exact four-path allowlist;
- structural final-v0.34 boundary verification;
- targeted pytest: 33 passed;
- paired output/exception/state/privacy/RNG/overhead probe;
- full pytest: 491 passed;
- full compileall;
- `git diff --check`;
- post-validation exact-byte verification.

The validated technical paths are:

- `src/closure.py`
- `src/observability/closure_shadow.py`
- `tests/test_observability_closure_shadow_v10a.py`
- `tools/probe_observability_closure_shadow_v10a.py`

The v2 validator initially failed because Git stderr containing a CRLF warning was
merged into stdout and treated as an extra path. The v3 continuation fixed only
that validation-layer defect and reused the exact retained candidate bytes.

Those exact validated bytes are now applied to the control-root checkpoint
surface together with durable memory.

The commissioned `v0.36-repack1` runtime has not been modified. Phase 1B is not
runtime commissioned.

Repository staging/commit/push for this source checkpoint remain pending.

## Resume

Follow `../CURRENT.md`'s `Exact Next Action`.

Do not reconstruct or retest a different Phase 1B candidate. The authoritative
source candidate is the exact four-file byte identity recorded in
`../evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

Repository actor sequence remains:

`assistant audit/package -> user local run -> returned evidence -> assistant verification -> isolated staging -> user publication -> remote verification -> separate runtime synchronization/commissioning`
