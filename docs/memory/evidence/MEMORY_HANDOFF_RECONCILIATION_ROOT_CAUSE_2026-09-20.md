# Memory Handoff Reconciliation Root-Cause Analysis — 2026-09-20

## Scope

This record reconciles the repeated v2-v5 installer failures before delivery of
the successor memory package. It concerns repository/checkpoint mechanics only;
football/model/application/runtime semantics are unchanged.

## Observed repeated pattern

All v2-v5 user runs stopped before modification. v3-v5 repeatedly classified
nearly the entire tracked memory tree plus `tools/check_memory_health.py` as
drift.

That repeated broad pattern is not consistent with independent accidental edits
to every memory file. It points to a systematic authority/representation error.

## Root cause

The project uses separate surfaces:

1. the local control root under `L:\Projects\fantasy_football`;
2. an isolated staging clone used for validated checkpoint commit/push;
3. the installed runtime/release tree when application files are involved;
4. GitHub as durable remote history.

Previous successful workflows may push from the isolated staging clone and then
synchronize validated files back to the control root. That synchronization does
not imply that the control root's own local Git `HEAD`/index advances to the same
commit.

v3, v4, and v5 all used the control root's Git metadata as if it were the
predecessor-content authority:
- v3: whole-tree porcelain status;
- v4: local worktree bytes versus local `HEAD:<path>` after newline
  normalization;
- v5: Git-cleaned local worktree blob versus local `HEAD:<path>`.

v4/v5 improved representation handling but did not change the authority surface,
so the same failure was expected to repeat.

## Correct authority split

### Local apply

- validate only files the package will overwrite;
- compare each target with the known predecessor checkpoint blob identity carried
  by the package;
- canonicalize only UTF-8 BOM and CRLF/CR representation for tracked text;
- require package-created paths to be absent unless the full payload is already
  applied;
- back up/rollback affected files;
- do not stage, commit, or push.

### Commit/push

After the user returns successful local output:
- use a fresh isolated staging clone;
- verify current remote head;
- copy the verified local payload into that clone;
- stage an exact allowlist;
- regenerate/verify the memory manifest from staged Git-blob bytes;
- run checkpoint validation;
- commit;
- re-check remote movement;
- push;
- verify remote SHA.

## Supersession

Any rule requiring the synchronized control root's local `HEAD` to equal the
expected predecessor checkpoint for a local memory apply is superseded.
