# D-025 — Generic `.ffpkg` Delivery Infrastructure

**Status:** ACTIVE
**Date:** 2026-09-21

## Context

Repeated Phase 1B checkpoint attempts failed in delivery mechanics rather than in
the validated closure-shadow candidate. Binary ZIP transfers arrived as zero-byte
files, manual chunk transport increased operator error surface, and interactive
PowerShell exposed known paste/control-flow hazards. Building another
phase-specific wrapper would reproduce the same class of failure across the 2026
roadmap.

## Decision

Adopt one permanent repository delivery subsystem under `tools/delivery/`.

A package is a deterministic UTF-8 text `.ffpkg` carrier containing a Base64-
encoded deterministic ZIP plus exact archive byte count and SHA-256. The ZIP
contains `package.json` and an exact inventoried payload.

The permanent runner owns:
- carrier parsing and format validation;
- archive byte-count and SHA-256 validation;
- safe-path/symlink/collision checks;
- exact payload inventory and per-file integrity checks;
- isolated extraction;
- declared entrypoint launch;
- exit-code propagation;
- extraction cleanup.

Package-specific entrypoints own:
- target/surface predecessor authorization;
- exact affected-scope allowlists;
- backup and rollback;
- idempotence / `ALREADY APPLIED` behavior;
- domain-specific post-write validation;
- the explicit modifications authorized for that package.

Supported package classes are `diagnostic`, `local_apply`, `runtime_sync`,
`release_install`, and `maintenance`.

## Repository checkpoint staging

Repository publication preparation is also generic infrastructure. The permanent
`tools/delivery/prepare_checkpoint_stage.py` consumes a declarative staging spec,
rechecks remote movement, creates a fresh isolated clone, copies only reviewed
paths, regenerates the schema-2 memory manifest from staged Git blob bytes, and
stops before commit/push.

Identity checks distinguish representation layers:

- `exact_sha256` in a staging spec authorizes **raw control-root/worktree bytes**;
- after `git add`, the staging engine derives the expected Git blob OID by
  applying that checkout's clean filters with
  `git hash-object --path <path> --stdin`;
- that filtered blob OID must equal the index blob OID.

A raw worktree SHA-256 must never be compared directly to staged blob bytes.
CRLF/LF normalization may legitimately change byte-level SHA-256 while preserving
the exact Git representation intended for commit.

## Human actor boundary

The infrastructure does not stage, commit, push, or modify a runtime merely by
executing a carrier. The default repository sequence remains:

`assistant .ffpkg -> user generic local run -> returned summary -> assistant verification -> separate staging/manifest/commit/push -> user push -> read-only remote verification`

## Supersession

This decision supersedes earlier ZIP/PowerShell wording only for **delivery
mechanics**. It does not supersede the human-in-the-loop repository-write boundary,
control-root versus staging-clone authority, manifest semantics, privacy rules,
or production-change authorization.

Manual Base64 chunk assembly and phase-specific launch wrappers are not normal
fallbacks when the generic runner is available.

## First consumer

The first real package executed through this infrastructure is a durable-memory
`local_apply` checkpoint recording the delivery architecture itself. Phase 1B
source remains separately gated and resumes only after the infrastructure/memory
checkpoint is committed and remote-verified.
