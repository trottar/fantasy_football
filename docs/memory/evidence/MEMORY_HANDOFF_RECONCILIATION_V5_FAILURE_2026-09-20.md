# Memory Handoff Reconciliation v5 Failure — 2026-09-20

## Classification

`FAILED BEFORE MODIFICATION / INVALID INSTALLER / SUPERSEDED`

## User-observed result

v5 again reported essentially the entire tracked `docs/memory/**` tree plus
`tools/check_memory_health.py` as pre-existing substantive drift, then stopped.

Confirmed modification state from the failure path:
- project files modified: NO;
- runtime tree modified: NO;
- Git staging attempted: NO;
- commit/push attempted: NO.

## Why v5 was still wrong

v5 improved the representation test from manual newline normalization to
`git hash-object --path=<path>` but still compared the result with the **control
root's own** `HEAD:<path>`.

That retained the same false authority assumption. The project workflow may
commit/push in an isolated staging clone and subsequently synchronize files into
the control root without advancing the control root's local Git metadata. A
systematic all-memory-file mismatch is therefore evidence that the authority
surface is wrong, not evidence that every memory file was independently edited.

## Successor requirement

The local-apply phase must not compare the whole control root with local `HEAD`.
It must validate only package targets against expected predecessor checkpoint
blob identities supplied by the package. The later isolated staging clone owns
Git `HEAD`/index/manifest/commit/push authority.
