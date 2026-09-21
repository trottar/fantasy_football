# Memory/Handoff Reconciliation v4 Build QA — 2026-09-20

## Pre-delivery construction failures

Two assistant-side QA failures occurred before the final v4 package was accepted:

1. the first v4 builder run reached helper validation and failed with Python
   `NameError: name 'sys' is not defined`; no user project state was involved and
   that build was rejected;
2. the corrected builder then ran strict memory health, which rejected the new
   handoff at 127 lines (`SOFT` threshold). The handoff was compacted to 123
   lines and the entire package QA gate was rerun.

Final accepted construction state:
- normalized scoped-drift helper `py_compile`: PASS;
- CRLF-only raw-dirty/substantive-clean regression: PASS;
- substantive-content drift regression: PASS;
- staged-change regression: PASS;
- untracked-file regression: PASS;
- strict memory health: PASS;
- exact ZIP CRC/manifest integrity: PASS;
- launcher embedded-ZIP byte round-trip: PASS.

No user project, Git index, commit, remote branch, or runtime tree was modified by
these assistant-side construction failures.

## Post-delivery status

Despite the assistant-side synthetic QA above, the real Windows control checkout
reproduced the broad false-drift failure. Therefore v4 is
`INVALID / SUPERSEDED`; synthetic CRLF coverage was insufficient to validate the
real Git clean-filter boundary. See
`MEMORY_HANDOFF_RECONCILIATION_V4_FAILURE_2026-09-20.md`.
