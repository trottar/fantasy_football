# Phase 1D Behavior Shadow Source Validation — 2026-09-23

## Authority

Source predecessor:

- commit: `c9ad2b383522038d03343ba04989ea206f1d8931`.

Accepted Phase 1D manager-behavior boundary:

- source: `src/market_manager.py::trade_response_probabilities`;
- observability name:
  `subsystem.behavior.trade_response_probabilities`;
- response model: `UNCALIBRATED_TRADE_RESPONSE_V030`.

The previously proposed `subsystem.trade.search` boundary at `search_trades`
remains rejected as behavior-only because it mixes football screening, predictive
roster response, manager-response probability, and offer ranking.

## Non-Modifying Runtime Boundary Probe

Diagnostic package:

`phase1d_trade_behavior_probe_20260923_v1`

Archive SHA-256:

`fb94eb03c0ea1dec4421bff9d3ccfde95b4057df25caa493b35481161dce7893`

Target runtime:

`L:\Projects\fantasy_football\fantasy_season_v0_36_repack1`

Measured results:

- favorable:
  - baseline median: `31,000 ns`;
  - observed median: `109,850 ns`;
  - incremental overhead: `78,850 ns`;
- neutral boundary:
  - baseline median: `32,400 ns`;
  - observed median: `117,600 ns`;
  - incremental overhead: `85,200 ns`;
- adverse/complex:
  - baseline median: `31,900 ns`;
  - observed median: `119,450 ns`;
  - incremental overhead: `87,550 ns`;
- controlled error:
  - baseline median: `6,400 ns`;
  - observed median: `80,500 ns`;
  - incremental overhead: `74,100 ns`.

All four paired gates passed. Because the kernel baseline is far below the
established `1,000,000 ns` relative floor, the large relative percentages are
non-authoritative; the authoritative absolute increments are all well below the
`1,000,000 ns` limit.

Additional probe results:

- output equivalence: PASS;
- exception-type equivalence: PASS;
- Python RNG non-interference: PASS;
- NumPy RNG non-interference: PASS;
- mutable config non-interference: PASS;
- probability/model contract: PASS;
- bounded behavior event structure/correlation: PASS, `560/560` events;
- privacy markers absent: PASS;
- observer fail-open behavior: PASS;
- primary observer failures: `0`;
- persistent sink: false;
- runtime source unchanged: true;
- production instrumentation performed: false.

Classification:

`PROBE-PASS / NARROW BEHAVIOR SHADOW CANDIDATE`

## Isolated Source Candidate

Source-preflight package:

`phase1d_behavior_shadow_source_preflight_20260923_v2`

Archive SHA-256:

`29c2c2a971c959a8ab95518813ef9a1f84bdd7dd605707133761eb1f4ae80237`

The package cloned the exact predecessor into an isolated temporary tree,
constructed the candidate there, validated it, captured exact identities, and
removed the temporary clone before reporting success. It changed neither the
control root nor the commissioned runtime.

Technical scope: exactly six paths.

1. `src/market_manager.py`
2. `src/observability/behavior_shadow.py`
3. `src/observability/integration_plan.py`
4. `tests/test_observability_behavior_shadow_v10a.py`
5. `tests/test_observability_integration_gate_v10a.py`
6. `tools/probe_observability_behavior_shadow_v10a.py`

Candidate behavior:

- adds one bounded in-memory `behavior` shadow recorder/decorator following the
  commissioned player-shadow fail-open/privacy contract;
- decorates only `trade_response_probabilities`;
- updates the integration map from rejected mixed `subsystem.trade.search` to
  accepted `subsystem.behavior.trade_response_probabilities`;
- leaves `search_trades`, `evaluate_trade`, and `perceived_market_value`
  uninstrumented;
- adds focused behavior-boundary tests and a retained paired probe.

No football, trade-value, roster-response, acceptance/counter/reject probability,
recommendation, or calibration formula is changed.

## Source Validation Results

Operator-executed isolated preflight:

- exact source predecessor: PASS;
- predecessor scope: `3 existing + 3 new` paths;
- targeted pytest: **46 passed in 6.65 s**;
- retained paired behavior probe: PASS;
- full pytest: **517 passed in 51.06 s**;
- `compileall`: PASS;
- strict memory health: HEALTHY;
- `git diff --check`: PASS;
- `git diff --cached --check`: PASS;
- output/exception/RNG/config/privacy/correlation: PASS;
- persistent sink: false;
- mixed trade surfaces instrumented: false;
- temporary clone cleanup: PASS / residue NONE.

Retained source-candidate paired timings:

- favorable:
  baseline `30,350 ns`, observed `111,700 ns`, increment `81,350 ns`;
- neutral boundary:
  baseline `30,650 ns`, observed `116,300 ns`, increment `85,650 ns`;
- adverse/complex:
  baseline `31,150 ns`, observed `119,350 ns`, increment `88,200 ns`;
- controlled error:
  baseline `6,900 ns`, observed `94,100 ns`, increment `87,200 ns`.

All absolute and relative gate classifications reported PASS under the established
benchmark contract.

Temporary candidate staged tree:

`75b2a7ff73c53db7e099d10b217dc5953e3b370d`

This tree identifies only the six-path isolated technical candidate before
durable-memory checkpoint files are added. It is not the later repository
checkpoint tree.

## Exact Validated Technical Target Identities

`src/market_manager.py`

- raw SHA-256:
  `a0c24bf005f13ee81d2c80d82761f5c1def15c85f850f99fcdebf28d5b57798b`;
- Git blob:
  `b384776b7bf1338af778a1ef146700755d87b340`.

`src/observability/behavior_shadow.py`

- raw SHA-256:
  `a3e921bbdf00f8d2971576bec73da2f1bc416847a3d5333b13fae59e83186316`;
- Git blob:
  `3eaae04b5b3d9c1eb4f07b8b1be1137c3daaa1aa`.

`src/observability/integration_plan.py`

- raw SHA-256:
  `e8d34314f13ee05bbfbfb1ee1ea3f4884111a6d26f69ff5d9ec53c05274f2333`;
- Git blob:
  `d2ac3bea41bded0f8abff697b516b35825168be6`.

`tests/test_observability_behavior_shadow_v10a.py`

- raw SHA-256:
  `a2beccb1f036b095588d087412fc0b2ebcbbb992abcb06d98b388bf4f64551b2`;
- Git blob:
  `5a869d09deeb1c7bc77083903b4bb79c1a7ec3f4`.

`tests/test_observability_integration_gate_v10a.py`

- raw SHA-256:
  `f93195514c0eaaffe330345c0e78c3962ada22ea89501e12cd311fa8a7045e70`;
- Git blob:
  `5480f99d718bb40fc566b69b91ab77e2fe91932c`.

`tools/probe_observability_behavior_shadow_v10a.py`

- raw SHA-256:
  `2224b57a22384c01fe19820aa0c3fc6d21e89c2c82df42f0b5c4e44f5e28ac64`;
- Git blob:
  `334d01c04aaa823cd271814145ca8f23cfa77c39`.

## Scientific / Privacy Classification

This candidate observes manager behavior, not football physics. It therefore
preserves:

- `P ⊕ D ⊕ K`;
- separation of football utility from manager behavior;
- `screen != authority`;
- the v0.X no-hindsight/no-empirical-retuning boundary.

Arguments, return values, authenticated/private payloads, raw identifiers, and
exception messages are not retained. Observation is bounded in memory and
fail-open. Persistent evidence remains disabled.

No observed 2026 outcome was used to tune the uncalibrated trade-response model.

## Local Checkpoint Recovery

Initial package:

`phase1d_behavior_shadow_source_local_apply_20260923_v1`

Result:

`FAILED BEFORE WRITE / CONTROL-ROOT MARKET_MANAGER ABSENT`

The initial local apply assumed `src/market_manager.py` already existed on the
control-root checkpoint surface. The package stopped during predecessor
validation with `actual=None`; it performed no source/memory write, no staging,
no runtime modification, and no rollback was required.

Read-only recovery diagnostic:

`phase1d_control_root_source_inventory_20260923_v1`

Measured layout:

- control root:
  - `src/observability/integration_plan.py`: exact predecessor;
  - `tests/test_observability_integration_gate_v10a.py`: exact predecessor;
  - `src/market_manager.py`: absent;
  - `behavior_shadow.py`, its dedicated test, and retained probe: absent;
- commissioned runtime:
  - `src/market_manager.py`: exact predecessor
    `4ffa2f9ead68c9933dd6d1ab06deb425b4a17278`;
  - `src/observability/integration_plan.py`: exact predecessor;
  - Phase 1D target/new files: absent;
- inspected `OTHER` paths: `0`.

This confirms the normal split control-root/runtime layout. The correction does
not treat the commissioned runtime as the checkpoint write target.

Corrected package v2:

`phase1d_behavior_shadow_source_local_apply_20260923_v2`

The package correctly used per-path predecessor authority, wrote and
identity-checked all nine targets, and then failed during post-write validation
because it attempted to run source-suite pytest from the intentionally partial
control root. The first missing test was
`tests/test_market_manager_v030.py`.

Classification:

`V2_LOCAL_APPLY = TARGETS_WRITTEN_AND_VERIFIED / VALIDATION_ENVIRONMENT_INVALID / ROLLED_BACK`

Read-only recovery audit:

`phase1d_post_v2_failure_audit_20260923_v1`

proved:

- rollback-to-prestate: PASS;
- backup residue: NONE;
- all nine affected control-root paths returned to exact predecessor/absent
  state;
- commissioned-runtime `market_manager.py` remained at the exact predecessor;
- the control root lacks several source-suite files/dependencies by design.

Final corrected package v3:

`phase1d_behavior_shadow_source_local_apply_20260923_v3`

preserves the isolated source-preflight results instead of rerunning them from
the partial control root. Its local post-write gate is limited to checks that the
control root can authoritatively perform:

- exact target identities;
- AST/static boundary semantics;
- direct `py_compile` of all six technical files;
- memory-health self-test and strict health;
- affected-scope `git diff --check`;
- unchanged Git index;
- unchanged commissioned-runtime predecessor identity.

The v3 package writes only the control-root checkpoint surface, stops before
isolated staging/commit/push, and does not modify the commissioned runtime.

### Local Apply v3 Memory-Health Failure

Package:
`phase1d_behavior_shadow_source_local_apply_20260923_v3`

The package again passed split-layout predecessor validation, constructed and
wrote all nine exact targets, and passed immediate target identity/semantic
validation. It then failed strict memory health because the rendered
`CURRENT.md` was `8465` bytes and `191` lines, crossing the repository soft
limits of `8192` bytes or `175` lines.

Classification:

`V3_LOCAL_APPLY = TARGETS_WRITTEN_AND_VERIFIED / CURRENT_SOFT_LIMIT_EXCEEDED / ROLLBACK_REQUIRED`

This is an active-memory composition defect, not a technical-source or behavior
observer defect. The successor does not weaken the health gate. It compresses
`CURRENT.md` to active state only and leaves detailed chronology in this
canonical evidence record.

Final corrected package v4:
`phase1d_behavior_shadow_source_local_apply_20260923_v4`

The v4 package accepts either the exact predecessor state or the exact v3 target
state as a recovery pre-state, but rejects any mixed/other state. It preserves
the already-passed isolated source preflight and validates locally with exact
identities, static Python compilation, strict memory health, rendered whitespace
checks, unchanged index, and unchanged commissioned-runtime predecessor identity.

### Local Apply v4 Invalid Memory Assertion

Package:
`phase1d_behavior_shadow_source_local_apply_20260923_v4`

The package passed:

- exact predecessor classification;
- exact 9/9 target construction;
- exact payload write;
- exact 9/9 post-write target identities.

It then failed its semantic gate because the installer required the literal
carrier ID `phase1d_behavior_shadow_source_local_apply_20260923_v4` to appear
inside `CURRENT.md`. The rendered `CURRENT.md` was intentionally package-agnostic
and already below the repository soft limits.

The runner reported `ROLLBACK_PERFORMED=true`, so the package returned the
control-root affected scope to its previous validated state and did not modify
the commissioned runtime.

Classification:

`V4_LOCAL_APPLY = TARGETS_WRITTEN_AND_VERIFIED / INVALID_CARRIER_ID_MEMORY_ASSERTION / ROLLED_BACK`

This is a package-QA defect, not a source candidate, behavior observer, or memory
content defect. The successor removes carrier-ID coupling from active memory and
its extracted-package self-test executes the same rendered-memory semantic
predicate used after installation, including controlled negative cases.

Final corrected package v5:
`phase1d_behavior_shadow_source_local_apply_20260923_v5`

## Result

`PHASE1D_BEHAVIOR_SHADOW_SOURCE_CANDIDATE_VALIDATED`

Next boundary after local apply:

`LOCAL-APPLIED -> isolated staging -> guarded source publication -> separate runtime commissioning`

A Week 3 material status/capture gate preempts those nonessential engineering
steps if it arrives first.
