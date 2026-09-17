# Current Project State

---
state_updated: 2026-09-17
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
maintenance_status: healthy
---

## Authority Metadata

- Final `0.X` runtime baseline: **`v0.36-repack1` — COMMISSIONED**.
- Internal `VERSION` remains `0.36`; `repack1` is an artifact revision.
- Phase 0 I-001 is resolved.
- Latest completed v1.0A slice: **local snapshot/replay/diff contract**.

## Active Objective

Build the modular, non-interfering v1.0A observability substrate without
changing football decision semantics, manager behavior, GUI business logic, or
random streams.

## Current Work Item

Completed observability foundation:
- immutable run/action context;
- structured events and event registry;
- explicit sinks;
- provenance/config/input hashing;
- invariant registry/results;
- conservative privacy/redaction primitives;
- local redacted snapshot bundle writer;
- exact-byte replay-bundle verification/loading;
- bounded structural replay/value diffing.

No production football/market/service/controller/GUI call site emits events yet.
No automatic snapshot capture or private/authenticated persistent logging is
enabled.

The exact next implementation slice is:

**failure-bundle contract**

## Verified State

- v0.36-repack1 remains commissioned.
- Prior v1.0A slices remain test-validated.
- Snapshot/replay/diff slice:
  - targeted observability tests passed: 48;
  - full repository pytest passed: 401;
  - full compileall and `git diff --check` passed;
  - strict memory health passed;
  - persisted structured values are redacted before local write;
  - bundle member byte lengths/SHA-256 are verified before replay loading;
  - tampering is detected;
  - structural diffs are bounded and redacted by default;
  - replay does not execute football/model logic;
  - RNG non-interference tests passed.

## Scientific / Architectural Boundaries Affecting This Work

- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Production behavior changes retain the explicit authorization boundary.
- Persistent private/authenticated event emission remains blocked until an
  integration layer explicitly applies redaction and is tested.
- Replay currently means verified evidence loading only, not computation
  execution.

## Current Implementation State

Implemented under `src/observability/`:
- `context.py`, `events.py`, `registry.py`;
- `sinks.py`, `provenance.py`;
- `invariants.py`, `redaction.py`;
- `snapshots.py`, `replay.py`, `diff.py`.

Not yet implemented:
- failure bundles;
- subsystem adapters;
- CLI/service/background-task correlation;
- GUI event emission/integration.

## Current Validation State

`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`

No blocker exists for the next observational slice.

## Exact Next Action

Implement the **v1.0A failure-bundle contract** while keeping production event
emission disabled.

## Success Criterion

The next checkpoint must produce privacy-safe, bounded, actionable failure
evidence without changing model results or requiring reconstruction from chat
history.

## Do Not Reopen Without New Evidence

- I-001 final 0.X lineage reconciliation;
- historical v0.36-fixed1 artifact search;
- v0.36 packaging diagnosis;
- v0.36-repack1 GUI commissioning;
- resolved memory/manifest/diagnostic-tool QA defects.

## Relevant References

- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Decisions D-013, D-014, D-016, D-017
- Current roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
