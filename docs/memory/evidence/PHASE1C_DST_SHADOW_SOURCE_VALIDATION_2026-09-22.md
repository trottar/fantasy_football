# Phase 1C DST Shadow Source Validation — 2026-09-22

## Authority

Remote source predecessor:
`37f841b7aec0280fa695f60e5285ff34646f9a10`

Predecessor tree:
`e4ff60adc5db0559c57bb72e55f30b282a4b7337`

Accepted DST boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`

Observer namespace:
`subsystem.dst.channel`

This is observability-only. It does not change DST football physics, specialist
policy decisions, scoring, manager behavior, recommendation authority, or the
separately gated K/player channels. Persistent evidence remains disabled.

## Diagnostic Preflight

The first preflight package failed before the observer probe because it required
a literally clean staging clone.

Read-only residue diagnosis proved:

- stage HEAD/tree/remote main: exact;
- relevant source blobs: exact;
- tracked diff: none;
- cached diff: none;
- sole untracked path: `.checkpoint_stage_id`.

The generic staging helper intentionally creates `.checkpoint_stage_id` as its
ownership sentinel and explicitly permits it.

Classification:
`PREFLIGHT VALIDATOR DEFECT / SOURCE AUTHORITY NOT INVALIDATED`

The corrected preflight allowed only the exact ownership sentinel and passed:

- success path: outputs/state/privacy PASS;
- error path: exception/state/privacy PASS;
- observer failure fallthrough: PASS;
- P/D/K direct cross-channel guard: PASS;
- Python RNG / NumPy RNG / mutable state preserved;
- persistent sink: false.

Corrected success timing: baseline `7000 ns`, observed `81400 ns`, incremental
`74400 ns`.

Corrected error timing: baseline `7600 ns`, observed `84200 ns`, incremental
`76600 ns`.

Classification:
`PHASE1C_DST_TARGETED_PREFLIGHT_VALIDATED`

## Source Candidate

Exact technical scope:

1. `src/specialist_policy_v032.py`
2. `src/observability/dst_shadow.py`
3. `tests/test_observability_dst_shadow_v10a.py`
4. `tools/probe_observability_dst_shadow_v10a.py`

Candidate architecture:

- `dst_shadow.py` owns a lazy bounded in-memory `ShadowRecorder`;
- `shadow_dst_call("subsystem.dst.channel")` decorates only
  `evaluate_defense_channel`;
- no arguments, returned payloads, or exception messages are retained;
- observer failure falls through to production behavior;
- `evaluate_kicker_channel` remains undecorated;
- no persistent sink is enabled.

## Candidate Validation v1

Passed before the probe-harness failure:

- candidate render: PASS;
- DST-only structure: PASS;
- K structure unchanged: PASS;
- Python compile: PASS;
- exact four-path allowlist: PASS;
- diff check: PASS;
- targeted pytest: **6 passed in 1.03 s**.

The canonical paired benchmark in the probe also reported outputs, exception
behavior, states, overhead, privacy, K non-interference, observer-failure
fallthrough, P/D/K guard, and RNG/mutable-state gates PASS.

A separate `success_behavior_preserved` field was false because the probe made an
extra observed/direct sequential comparison without restoring Python RNG, NumPy
RNG, and mutable state between calls. The fake policy intentionally consumed RNG.

Classification:
`PROBE HARNESS DEFECT / CANDIDATE SOURCE NOT INVALIDATED`

## Candidate Validation Continuation

The continuation recovered the exact v1 generator payloads. It retained the DST
production/shadow/test payloads and changed only the probe harness to restore
Python RNG, NumPy RNG, input payload, and mutable state before the extra direct
comparison.

Results:

- corrected paired probe: PASS;
- success behavior preserved: true;
- outputs equal: true;
- exception behavior equal: true;
- states equal: true;
- privacy success/error: PASS;
- K non-interference: true;
- observer-failure fallthrough: true;
- P/D/K cross-channel guard: true;
- Python RNG / NumPy RNG / mutable state: preserved;
- full pytest: **497 passed in 47.21 s**;
- full compileall: PASS;
- exact bytes after validation: PASS;
- four-path allowlist after validation: PASS;
- candidate residue: NONE;
- persistent sink: false.

Paired candidate benchmark:

- baseline median: `7500 ns`;
- observed median: `79800 ns`;
- incremental: `72300 ns`;
- relative fraction: `9.64`.

The repository benchmark default has a `1,000,000 ns` relative floor and
`1,000,000 ns` maximum incremental overhead. Because the baseline is below the
relative floor, the relative factor is non-authoritative; the absolute criterion
passes.

## Exact Candidate Identity

- `src/specialist_policy_v032.py`
  - SHA-256:
    `6ce0392a71535acd0c8c673c198ba0ba98ff06f6d8274830265ae9391d6c6be2`
  - candidate Git blob:
    `98da6102da86e7e41a1f0b0c2ab29e3fcb1d2661`
- `src/observability/dst_shadow.py`
  - SHA-256:
    `e05be60c597d592dbd16e91e546b8badb08175bb23841b7c3d616e08a7a927b9`
  - candidate Git blob:
    `71dee84d5eabfb102f832ad4bfbd04b85768dc9d`
- `tests/test_observability_dst_shadow_v10a.py`
  - SHA-256:
    `d10c5dd486cad98ba2341e1c23b13dcbabd9c42ba5eaa2ba37bc51beb2cc5a31`
  - candidate Git blob:
    `273ebeb6eff662943d2a8477ff20087b1f6c20b9`
- `tools/probe_observability_dst_shadow_v10a.py`
  - SHA-256:
    `b6ef38d427f94f721fa1bf6cf54f5cc9bf8466ff0169e1fb3d6393607b98f08d`
  - candidate Git blob:
    `09ef08dd05d615034eb121e35511235b005e3262`.

## Result

`PHASE1C_DST_CANDIDATE_FULLY_SOURCE_VALIDATED`

The exact candidate is authorized for the normal source-checkpoint workflow.
Runtime synchronization remains a later, separate gate after source publication
and remote verification.
