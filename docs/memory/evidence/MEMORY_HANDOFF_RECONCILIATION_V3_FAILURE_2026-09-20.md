# Memory/Handoff Reconciliation v3 Failure — 2026-09-20

## Classification

`FAILED BEFORE MODIFICATION / INVALID INSTALLER / SUPERSEDED`

## User-observed boundary

The v3 launcher stopped before any project write, Git staging, commit, or push.
Reported terminal state:

```text
Project modification:   NONE
Git staging:            NOT ATTEMPTED
Commit/push:            NOT ATTEMPTED
```

It reported a large set of pre-existing changes covering essentially the tracked
`docs/memory/**` tree and `tools/check_memory_health.py`.

## Root cause

v3 replaced the incorrect remote/local `HEAD` equality requirement from v2, but
its `Get-ScopedStatusPaths` implementation still classified every path emitted by
raw `git status --porcelain=v1` as substantive local drift.

That is not representation-safe for the established Windows control checkout.
Tracked text can differ from the committed Git blob only by checkout line-ending
representation while still representing the same checkpoint content. The project
already has a durable Git-object pre-state rule requiring CRLF/CR-to-LF
normalization only before tracked-text comparison.

## Successor correction

The successor classifier must:
- fail on staged scoped changes;
- fail on unexpected untracked scoped files;
- fail on missing tracked scoped files;
- compare tracked local text to `HEAD:<path>` after normalizing only line endings;
- fail on every remaining substantive difference;
- use the same classifier after apply for the changed-file allowlist;
- report raw porcelain state only as diagnostic context.

This preserves local validated-tree authority without weakening later remote-head
movement checks before push.

## Scope

No football/model/application/runtime file changed. No memory file changed. No
Git index, commit, or remote branch changed during the failed v3 run.
