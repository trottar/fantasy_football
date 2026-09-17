# v1.0A Context/Event Validation Evidence

<!-- FANTASY_EVIDENCE_V10A_CONTEXT_EVENTS_20260917:BEGIN -->
## Validation evidence

Timestamp: `2026-09-17T12:22:28.118480-04:00`

Pre-state GitHub main:
`4e7f5277cd4a3d98378e3bdeaf8f965ab27df14b`

Checkpoint:
`v1.0A context/events slice 1`

Implemented contract:
- `src/observability/context.py`
  - frozen `RunContext`;
  - run/action correlation;
  - timezone-aware timestamps normalized to UTC;
  - release/source/config/input provenance fields;
  - week / decision-time / data-as-of / scenario / seed / CRN fields;
  - child-action derivation without mutating the parent context.
- `src/observability/registry.py`
  - immutable event registry;
  - `NORMAL`, `DIAGNOSTIC`, `TRACE`, `AUDIT` levels;
  - generic run/action events;
  - GUI lifecycle/action/service/task/state/render/refresh event names reserved exactly at the contract layer.
- `src/observability/events.py`
  - schema version 1;
  - frozen structured event envelope;
  - recursively immutable JSON-safe payload;
  - deterministic JSON rendering;
  - registry, subsystem, and required-payload validation.

No sink, logger, adapter, invariant engine, replay layer, or production call site is introduced by this checkpoint.

Validation:
- targeted observability tests: PASS (11);
- full pytest: PASS (364);
- full repository compileall: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- no existing football/model/application source file modified;
- context/event construction RNG non-interference tests: PASS;
- caller payload immutability/deep-freeze tests: PASS.

State:
`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`.

The commissioned v0.36-repack1 football/model/GUI behavior remains unchanged.
<!-- FANTASY_EVIDENCE_V10A_CONTEXT_EVENTS_20260917:END -->
