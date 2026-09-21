# Memory/Handoff Reconciliation v4 Failure — 2026-09-20

## Classification

`FAILED BEFORE MODIFICATION / INVALID INSTALLER / SUPERSEDED`

The user reported that
`install_fantasy_memory_handoff_reconciliation_20260920_v4.ps1`
reproduced the same broad pre-existing memory/health-tool drift failure as v3.

The failing guard executes before payload backup/copy, Git staging, commit, or
push. Therefore this run did not authorize or perform a checkpoint transition.

## v4 intent

v4 attempted to repair v3 by:
- treating raw porcelain as diagnostic only;
- comparing tracked worktree files with `HEAD:<path>`;
- manually normalizing CRLF/CR to LF before byte comparison;
- continuing to block staged, untracked, missing, or non-newline content drift.

That construction passed synthetic CRLF tests but did not close the real Windows
checkout representation problem.

## Diagnosis

The remaining defect is the representation boundary itself. Manual byte
normalization is still an imitation of Git's checkout/clean behavior. The
repository's authoritative question is not whether two filesystem byte streams
match after a custom transform; it is whether the local tracked file would stage
to the same Git blob as `HEAD:<path>` under the repository's actual
attributes/clean filters.

## Successor rule

For every tracked scoped file:

```text
expected = git rev-parse HEAD:<path>
actual   = git hash-object --path=<path> <worktree-file>
```

Require `expected == actual`.

Separately reject:
- any staged scoped change;
- unexpected untracked scoped files;
- missing tracked scoped files.

Raw worktree porcelain remains diagnostic only.

## Scope

No football/model/application behavior is changed by this incident or its
successor. The technical frontier remains the data-source season-sync shadow
pilot after memory reconciliation is successfully applied and checkpointed.

## Subsequent supersession

v5 subsequently failed before modification with the same broad pattern. The
Git-cleaned worktree comparison was representation-correct but still used the
wrong authority surface by comparing against the synchronized control root's
local `HEAD`.

Canonical successor diagnosis:
`MEMORY_HANDOFF_RECONCILIATION_ROOT_CAUSE_2026-09-20.md`.
