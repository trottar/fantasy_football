# Memory M4R1 Maintenance Newline Repair — 2026-09-21

## Classification

`M4R1 MAINTENANCE NEWLINE REPAIR = CONTENT COMPLETE / STRUCTURAL MEMORY FIX / NO FOOTBALL OR RUNTIME CHANGE`

## Trigger

M4 was published and independently remote-verified at repository checkpoint
`0f4d7f872744ea82365c2b688da6d6958b1c1c8f`.

Read-only inspection of the committed `docs/memory/MAINTENANCE.md` then found a
rendering defect in `## Semantic Maintenance Triggers`: two intended line breaks
had been emitted as literal backslash-n text.

Committed malformed text:

`... CURRENT.md`;\n- the handoff retains ...;\n- the handoff does not make ...`

This made three semantic trigger bullets render as one malformed Markdown line.

## Root Cause

The M4 package generator constructed the replacement fragment with escaped
`"\\n"` sequences instead of actual newline characters.

The M4 package's semantic validation checked that the resulting phrases were
present but did not reject literal escape text in this section. Strict memory
health also did not detect the defect because semantic cross-file/content checks
are intentionally deferred to M6.

## Repair

M4R1 performs one narrow correction:

- replace the two literal `\n` sequences in the affected handoff-trigger fragment
  with actual line breaks;
- preserve the three intended semantic trigger bullets exactly;
- record the repair in active continuity state so M5 cannot begin until this
  correction is durable.

No other M4 handoff-contract semantics are changed.

## Validation Contract

The package must:

- authorize all four existing targets against the exact durable-M4 Git blob
  predecessors;
- require the exact malformed maintenance fragment before first apply;
- replace only that fragment in `MAINTENANCE.md`;
- preserve BOM/newline representation;
- reject any remaining literal `\n- the handoff` text;
- require all three handoff semantic-trigger bullets as distinct lines;
- update CURRENT/STATUS/KNOWN_ISSUES to M4R1 content-complete state;
- support exact idempotent rerun;
- roll back all affected paths on post-write validation failure;
- pass strict memory health;
- leave `docs/memory/manifest.json` and the control-root Git index unchanged;
- not touch football/model/application source or commissioned runtime.

## Next Step

Publish M4R1 as a separate corrective memory checkpoint. Only after M4R1 is
remote-verified may M5 — startup contract decision — begin.
