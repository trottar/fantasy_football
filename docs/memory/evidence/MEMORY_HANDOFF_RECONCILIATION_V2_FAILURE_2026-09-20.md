# Memory / Handoff Reconciliation v2 Installer Failure — 2026-09-20

## Classification

`FAILED BEFORE MODIFICATION / INVALID INSTALLER / SUPERSEDED`

## User-observed terminal state

The delivered `install_fantasy_memory_handoff_reconciliation_20260918_v2.ps1`
stopped with:

```text
Project modification:   NONE
Git staging:            NOT ATTEMPTED
Commit/push:            NOT ATTEMPTED
Wrong repository pre-state. expected HEAD=0 actual HEAD=1
```

Therefore no durable-memory file, health tool, football/model/application file,
runtime tree, Git index, commit, or remote branch was modified by this attempt.

## Defect 1 — invalid authority boundary

The launcher embedded the read-only GitHub reference
`f22115e7c75357e4321912831a3f99d1ea3e5c3f` as `$ExpectedHead` and required the
local control checkout's `git rev-parse HEAD` to equal it before a memory-only
local apply.

That is not a justified precondition in this project's human-in-the-loop
checkpoint flow. The validated local tree is authoritative between checkpoints.
A remote SHA is reference/history state until the later commit/push stage. A
memory apply should instead validate the affected local scope and explicit
predecessor content.

## Defect 2 — rendered PowerShell format placeholders were corrupted

The generated launcher contained format expressions such as:

```powershell
throw ("Wrong repository pre-state. expected HEAD=0 actual HEAD=1" -f $ExpectedHead, $head)
```

instead of preserving literal PowerShell placeholders `{0}` and `{1}`. Similar
rendering damage affected other diagnostic strings. The likely generation layer
consumed the braces before the `.ps1` was emitted.

This made the failure message misleading and hid the actual local SHA. Package
QA had validated ZIP bytes and content but did not execute/inspect representative
PowerShell `-f` diagnostics strongly enough to catch the rendered-script defect.

## Successor requirements

The successor package must:

1. not require local `HEAD == remote reference` for this local memory apply;
2. require a clean exact affected scope;
3. validate semantic predecessor markers on the affected local files;
4. preserve repository/reference SHAs only as reported evidence;
5. preserve literal PowerShell `{0}`, `{1}`, ... placeholders;
6. self-test representative formatted messages;
7. retain backup/rollback and exact payload hashing;
8. leave Git staging, commit, and push untouched;
9. require the complete local output to be returned before separate push commands.

## Scope

Football/model/application source changed: `NO`.

Runtime tree changed: `NO`.

Git staging/commit/push: `NOT ATTEMPTED`.
