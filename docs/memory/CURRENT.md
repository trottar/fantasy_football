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
- Internal `VERSION` remains `0.36`; `repack1` is an artifact revision, not a
  historical `v0.36-fixed1`.
- Phase 0 lineage investigation I-001 is resolved.
- Latest completed v1.0A implementation checkpoint:
  `a4e84ed5c1433e29292b53b4e7d62bbb3b255386`
  (`sinks` + provenance/config/input hashing).

## Active Objective

Build the modular, non-interfering v1.0A observability substrate on top of the
commissioned v0.36-repack1 baseline without changing football decision
semantics, manager behavior, GUI business logic, or random streams.

## Current Work Item

Completed observability foundation:
- immutable `RunContext` and action correlation;
- schema-versioned immutable structured events;
- immutable event registry and GUI lifecycle namespace;
- explicit memory/JSONL/human/fanout sinks;
- provenance/config/input hashing helpers;
- source commit + tracked-dirty provenance.

No production football/market/service/controller/GUI call site emits events yet.
No global sink/logger is installed.

The exact next implementation slice is:

**invariant registry + privacy/redaction primitives before production event emission**

## Verified State

- v0.36 source lineage: resolved and durably imported.
- v0.36-repack1 packaging repair: validated; four public mock-calibration
  fixtures restored with no football/model behavior repair.
- Automated release validation: targeted tests, full pytest, compileall,
  exact-ZIP checks, and 17-file GUI-focused gate passed.
- Live GUI commissioning: **operator-confirmed PASS**; historical deleted-client
  lifecycle failure was not observed.
- v1.0A slice 1 — context/events:
  - 11 targeted observability tests passed;
  - full repository pytest passed: 364 tests;
  - full compileall and `git diff --check` passed.
- v1.0A slice 2 — sinks/provenance:
  - 22 targeted observability tests passed;
  - full repository pytest passed: 375 tests;
  - full compileall and `git diff --check` passed;
  - human sink payload is omitted by default;
  - canonical JSON hashing and exact-byte snapshot hashing are tested;
  - persistent private/authenticated event logging remains intentionally
    unintegrated before redaction.

## Scientific / Architectural Boundaries Affecting This Work

- v0.36-repack1 remains the frozen commissioned 0.X runtime baseline.
- Observed 2026 outcomes do not retune 0.X.
- Diagnostics observe; they do not change football physics, behavior kernels,
  recommendation authority, GUI business logic, or random draws.
- Public/private data boundaries remain intact.
- Production behavior changes retain the explicit authorization boundary.
- Persistent private/authenticated event emission stays blocked until
  privacy/redaction and integration contracts are implemented and tested.

## Current Implementation State

Implemented:
- `src/observability/context.py`
- `src/observability/events.py`
- `src/observability/registry.py`
- `src/observability/sinks.py`
- `src/observability/provenance.py`
- `src/observability/__init__.py`
- focused context/event/sink/provenance tests

Not yet implemented:
- invariant registry;
- privacy/redaction;
- snapshot/replay/diff;
- failure bundles;
- subsystem adapters;
- CLI/service/background-task correlation;
- GUI event emission/integration.

## Current Validation State

Current v1.0A foundation:

`CHECKPOINTED / TEST-VALIDATED / NOT YET INTEGRATED INTO PRODUCTION CALL SITES`

No blocker exists for the next observational slice.

## Exact Next Action

Implement the **v1.0A invariant registry + privacy/redaction primitives**.

That checkpoint should:

1. define explicit invariant/result contracts without production integration;
2. define recursive redaction/privacy policy before any private persistent event
   emission;
3. add deterministic, non-interference, and secret-redaction tests;
4. keep existing sinks/provenance/context/event contracts backward-compatible;
5. leave production call sites unchanged;
6. run targeted tests, full pytest, compileall, `git diff --check`, exact
   staging validation, and durable-memory update.

## Success Criterion

The next checkpoint succeeds only if invariants and redaction are test-validated,
non-interfering, conservative by default, and no private/authenticated runtime
persistence or production event emission is enabled.

## Do Not Reopen Without New Evidence

- I-001 final 0.X lineage reconciliation.
- Historical `v0.36-fixed1` artifact search.
- v0.36 mock-fixture packaging diagnosis.
- v0.36-repack1 GUI commissioning.
- resolved manifest/diagnostic-tool QA defects.

## Relevant References

- Operating method: `architecture/PROBLEM_SOLVING_METHOD.md`
- Observability architecture: `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- Context/event decision: `decisions/D-013_V10A_CONTEXT_EVENT_CONTRACT.md`
- Sinks/provenance decision: `decisions/D-014_V10A_SINKS_PROVENANCE.md`
- v0.36 authority: `decisions/D-010_PHASE0_FINAL_0X_AUTHORITY.md`
- Commissioning decision: `decisions/D-012_V036_REPACK1_COMMISSIONED_V10A_READY.md`
- Slice-1 evidence: `evidence/V10A_CONTEXT_EVENTS_2026-09-17.md`
- Slice-2 evidence: `evidence/V10A_SINKS_PROVENANCE_2026-09-17.md`
- Roadmap: `roadmap/STATUS.md`
- Detailed chronology: `memory/2026-09-17.md`
