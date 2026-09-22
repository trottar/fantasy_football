# Phase 1C K Targeted Preflight — 2026-09-22

## Authority

Repository checkpoint:

`af20e84f61e7b4ef86d7f03b568fa1ef8ce1d9a5`

Tree:

`fc94799408d37985390e1e6a2f465b5549296b09`

Boundary:

`src/specialist_policy_v032.py::evaluate_kicker_channel`

Namespace:

`subsystem.k.channel`

The preflight was diagnostic only. It modified no production source, runtime
source, durable memory, repository stage/index, commit, or remote state.

## Exact Boundary Contract

The current wrapper was confirmed undecorated before K instrumentation and
delegated exactly once through:

`_evaluate_policy_channel(..., position="K", ...)`

The commissioned DST wrapper remained decorated independently at
`subsystem.dst.channel`.

## Measurements

Success-path paired gate:

- baseline median: `7200 ns`;
- observed median: `79350 ns`;
- incremental overhead: `72150 ns`;
- relative fraction: `10.020833333333334`;
- outputs equal: true;
- states equal: true.

Error-path paired gate:

- baseline median: `8050 ns`;
- observed median: `83800 ns`;
- incremental overhead: `75750 ns`;
- exception behavior equal: true;
- states equal: true.

Both baselines are below the existing `1,000,000 ns` relative floor, so the
relative factors are non-authoritative. The absolute increments pass the existing
`1,000,000 ns` budget.

## Contract Gates

PASS:

- K wrapper structure and `position="K"` scope;
- success and error semantics;
- Python and NumPy RNG-state equivalence;
- relevant mutable-state equivalence;
- argument/return/error-message privacy;
- observer-failure fallthrough;
- DST observer non-interference;
- direct P/D/K cross-channel correlation guard;
- bounded in-memory observation;
- persistent sink disabled;
- source-stage residue unchanged.

The probe emitted 84 bounded in-memory K events during its repeated paired calls.
No event retained the private argument, returned payload marker, or exception
message.

## Result

`PHASE1C_K_TARGETED_PREFLIGHT_VALIDATED`

This result authorizes construction and source validation of a K-only
observability candidate. It does not commission K runtime instrumentation and
does not authorize player instrumentation or persistent evidence.
