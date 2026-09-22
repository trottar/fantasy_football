# Phase 1C K Shadow Source Validation — 2026-09-22

## Authority

Repository predecessor:

`af20e84f61e7b4ef86d7f03b568fa1ef8ce1d9a5`

Tree:

`fc94799408d37985390e1e6a2f465b5549296b09`

Validated boundary:

`src/specialist_policy_v032.py::evaluate_kicker_channel`

Namespace:

`subsystem.k.channel`

The candidate was constructed and validated in an isolated temporary clone.
Authoritative control-root source, commissioned runtime source, durable memory,
repository staging/index, commit history, and remote state were not modified by
candidate validation.

## Technical Scope

Exactly five technical paths:

1. `src/specialist_policy_v032.py`
2. `src/observability/k_shadow.py`
3. `tests/test_observability_dst_shadow_v10a.py`
4. `tests/test_observability_k_shadow_v10a.py`
5. `tools/probe_observability_k_shadow_v10a.py`

The only production-source change is the K observer import/decorator. The
existing DST decorator remains semantically unchanged. Specialist football
policy below the outer wrappers is unchanged.

## Exact Validated Identities

- `src/specialist_policy_v032.py`
  - SHA-256: `d9124bb51a9baa93a0a8f53768a4b41af9b08ed690c5e0f8ebc98c32d28ad271`
  - raw Git object ID: `41d08dc53c3a2d7f1d861cad728033c4d5ab4756`
- `src/observability/k_shadow.py`
  - SHA-256: `81e324a432f3ace85bb9032e2deb60af945607891131d00ee787381880a45ab0`
  - raw Git object ID: `f865c75817c2ce92765cb07a89eae1b44f9b0b84`
- `tests/test_observability_dst_shadow_v10a.py`
  - SHA-256: `b601521b92df7b287a691f0a7cbdaa318929507ea1fcd55d75239ee98cad7ee2`
  - raw Git object ID: `b2cca1516d735376e200cea182b2fc37891a94c7`
- `tests/test_observability_k_shadow_v10a.py`
  - SHA-256: `645ca361309e47c0eb4a19a8b89f5e1b5a516f00ffdb006a2442540a2edf191a`
  - raw Git object ID: `2af374c900e480f0b4cd6cb24c5d716b741bacf0`
- `tools/probe_observability_k_shadow_v10a.py`
  - SHA-256: `4708fe4c2b7dc32cd8763e15bda49bb7e60ab7c5ca53467e8a5f46c960f340c3`
  - raw Git object ID: `3d7b641415b8be37d6e49400343ab7b868d79846`

## Validation

Structural gates:

- P/D/K wrapper structure: PASS;
- commissioned DST wrapper semantic structure: PASS;
- K wrapper decorated only at `subsystem.k.channel`: PASS;
- changed-path Python compilation: PASS.

Targeted validation:

**12 passed in 1.30 s**

The targeted set covered both K and DST observability tests.

Paired K probe:

- baseline median: `7300 ns`;
- observed median: `80250 ns`;
- incremental overhead: `72950 ns`;
- relative fraction: `9.993150684931507`;
- success/error privacy and production semantics: PASS;
- DST non-interference: PASS;
- P/D/K cross-channel guard: PASS;
- Python/NumPy RNG and mutable state: preserved;
- persistent sink: false.

Because the baseline is below the `1,000,000 ns` relative floor, the relative
factor is non-authoritative; the `72950 ns` absolute increment passes the
`1,000,000 ns` budget.

Full source gate:

- full pytest: **503 passed in 52.77 s**;
- compileall: PASS;
- `git diff --check`: PASS;
- exact changed allowlist: 5 paths;
- post-validation identity: PASS;
- remote-movement guard: PASS;
- temporary candidate cleanup: PASS.

## Scientific / Privacy Classification

This candidate is observability only. It adds no kicker football-policy logic,
does not alter specialist market/state response, does not couple K directly to
DST or players, and does not change recommendation authority.

The K recorder is bounded and in-memory only. Arguments, returned values,
authenticated/private payloads, and exception messages are not retained.
Production result/exception semantics remain authoritative. Persistent evidence
remains disabled.

No observed 2026 outcome was used to tune any v0.X football model.

## Result

`PHASE1C_K_CANDIDATE_FULLY_SOURCE_VALIDATED`

The exact validated bytes may be locally applied for checkpoint construction.
Repository publication and commissioned-runtime synchronization remain separate
later gates.
