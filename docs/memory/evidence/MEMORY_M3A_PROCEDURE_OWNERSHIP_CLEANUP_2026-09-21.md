# Memory M3A Procedure Ownership Cleanup — 2026-09-21

## Classification

`M3A PROCEDURE OWNERSHIP CLEANUP = CONTENT COMPLETE / NO FOOTBALL OR RUNTIME CHANGE`

M3A is the first half of M3. It resolves the procedural contradiction identified
by M0 without simultaneously rewriting curated `MEMORY.md` knowledge.

M3B remains a separate checkpoint.

## Predecessor

M2 checkpoint identity semantics is durable on remote `main`. Its containing
repository state establishes the predecessor context; this evidence record does
not require active memory to embed the predecessor's SHA as a "latest state"
field.

## Problem

The repository already had the correct policy ownership model:

- `AGENTS.md` — startup/authority/guardrails;
- `COMMUNICATION.md` — communication lifecycle;
- `TOOLS.md` — environment/tool commands and proven operational facts;
- `patches/PATCH_PROTOCOL.md` — repository checkpoint mechanics;
- `MAINTENANCE.md` — memory health/cleanup.

But older procedure text remained in several places:

- `COMMUNICATION.md` still prescribed ZIP/PowerShell delivery and complete-log
  return behavior;
- the top of `TOOLS.md` still prescribed ZIP + `.ps1` while later sections
  described `.ffpkg`;
- `README.md` repeated an older generic actor sequence;
- D-009 in `DECISION_LOG.md` still called ZIP/PowerShell the checkpoint workflow
  even though D-025 had superseded those delivery mechanics.

This created a fresh-session ambiguity: a reader could follow a structurally
valid but obsolete procedure.

## Adopted Ownership

### `patches/PATCH_PROTOCOL.md`

Canonical owner of repository checkpoint mechanics:

- package/local-apply boundaries;
- staging/manifest semantics;
- commit/push/remote movement guards;
- representation layers;
- runtime/control-root separation;
- rollback and release gates.

### `COMMUNICATION.md`

Canonical owner of how checkpoint state is communicated:

- progress updates;
- package identity/scope/validation claims;
- concise success summary versus full failure output;
- explicit epistemic state labels;
- handoff/end-of-work communication.

It points to the patch protocol instead of duplicating detailed mechanics.

### `TOOLS.md`

Canonical owner of environment and operational commands:

- `.ffpkg` build/verify/run commands;
- declarative staging command;
- PowerShell/native-process rules;
- memory-health invocation;
- public/private operational boundary;
- validation tool inventory.

It points to the patch protocol for repository publication mechanics.

### `README.md`

Navigation/role map only. It identifies canonical owners and the current startup
contract but does not become another procedure manual.

### D-009 / D-025

D-009 remains active for:

- standing memory/diagnostic authorization;
- explicit authorization for football/application changes;
- human-in-the-loop repository publication boundary;
- no direct connector checkpoint writes.

Its ZIP/PowerShell delivery mechanics are explicitly superseded by D-025.

D-025 remains the active owner of generic text `.ffpkg` delivery/execution and
declarative isolated staging.

## M3A Scope

Rewritten procedure/index surfaces:

- `docs/memory/COMMUNICATION.md`;
- `docs/memory/TOOLS.md`;
- `docs/memory/README.md`;
- `docs/memory/decisions/DECISION_LOG.md`.

Continuity surfaces updated for the M3A/M3B split:

- `docs/memory/CURRENT.md`;
- `docs/memory/handoffs/CURRENT_HANDOFF.md`;
- `docs/memory/roadmap/STATUS.md`;
- `docs/KNOWN_ISSUES.md`.

New evidence:

- this file.

## Explicitly Unchanged

M3A does not modify:

- `docs/memory/MEMORY.md`;
- startup membership/ordering in `AGENTS.md` (M5 owns that decision);
- `MAINTENANCE.md`;
- `patches/PATCH_PROTOCOL.md`;
- generic delivery/staging implementation;
- football/model/application source;
- commissioned runtime;
- retained Phase 1B candidate;
- persistent evidence authorization.

## Validation Contract

The M3A package must:

- authorize every existing target against the exact Git-blob predecessor from the
  durable M2 checkpoint while tolerating only BOM/newline representation
  differences;
- preserve each target's existing BOM/newline representation;
- write the exact reviewed M3A replacement content;
- support exact idempotent rerun;
- roll back all affected paths on a post-write validation failure;
- reject obsolete active procedure markers such as "self-contained ZIP /
  PowerShell entry point" and "exact delivered-ZIP";
- preserve the active `.ffpkg` / `tools/delivery/` contract;
- run strict memory health;
- leave `docs/memory/manifest.json` unchanged during local apply;
- leave the control-root Git index unchanged;
- not touch the commissioned runtime.

## Next Memory Step

Resolve M3A durability from the containing Git/ref. Once M3A is on remote `main`,
perform **M3B — curated `MEMORY.md` cleanup** as a separate checkpoint.

Week 3 prospective capture remains a harder calendar gate than nonessential M3B
progress.
