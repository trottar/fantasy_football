# Phase 1E Redacting Persistence Primitive Preflight — 2026-09-24

## Purpose

Establish the first persistent-evidence safety primitive without enabling
production persistence.

The existing raw `JsonlSink` writes `StructuredEvent.to_json()` verbatim while
redaction is caller-owned. Direct production wiring would therefore not satisfy
the persistent-evidence privacy gate.

## Accepted Candidate

The candidate adds an explicit `RedactingJsonlSink` that performs redaction before
each JSONL file write, preserves the source event, appends one complete event per
line, and does not advance Python RNG state. The existing raw `JsonlSink` remains
unchanged.

Exact preflight candidate Git blobs:

- `src/observability/sinks.py`:
  `110b50f101f05a77a2b4879c913067bdd8d083b3`;
- `src/observability/__init__.py`:
  `b872c6bc963dc2c41b3d206a59a31112b953068c`;
- `tests/test_observability_persistent_sink_v10a.py`:
  `b53afdeaa29e0fb4a67bc68dc1dd8ef8ae76728a`.

## Validation

The non-modifying isolated-clone preflight against source base
`9af4df1bcc848b525c1565ea6d054c9fb313cc89` passed:

- targeted privacy/persistence tests: `22 passed`;
- full observability family: `143 passed`;
- full source suite: `522 passed`;
- `compileall src`: PASS;
- `git diff --check`: PASS;
- candidate allowlist: `3 / EXACT`;
- raw `JsonlSink`: unchanged;
- commissioned runtime: unchanged;
- production persistence activation: false;
- persistence path/retention authorization: false.

## Cleanup Recovery

The preflight cleanup left only an orphaned partial Git pack after the working
tree and usable repository metadata had already been removed.

Read-only inventory measured exactly four residual directories and three readable
`.idx/.pack/.rev` files totaling `1,282,921` bytes. `HEAD`, config, index, refs,
logs, and all candidate working-tree source files were absent.

A guarded successor cleanup verified the exact seven-path inventory plus pack,
index, and reverse-index headers, then removed only that disposable residue.

Classification:

`ORPHANED_PARTIAL_GIT_PACK_ONLY`

Final cleanup boundary:

`PHASE1E-PREFLIGHT-RESIDUE-CLEAN`

The already-passed source preflight was not rerun because the cleanup defect did
not invalidate source/behavior evidence.

## Boundary

This checkpoint does not activate persistence, choose a persistence directory,
authorize retention policy, wire production shadow observers to disk, modify
football/model/business logic, or synchronize the commissioned runtime.

After accepted local apply, the next repository gate is isolated staging and
publication. Runtime synchronization/commissioning remains a separate later
transition.
