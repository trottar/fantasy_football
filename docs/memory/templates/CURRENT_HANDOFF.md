# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

No exceptional transfer state is recorded.

## Resume

Follow `../CURRENT.md`'s `Exact Next Action` and load only its task-relevant
canonical references.

<!--
If an exceptional transition exists, replace the "No exceptional..." sentence
with only the unresolved condition needed by the next session, such as:
- local-applied but not staged/published state;
- staged/committed but not pushed state;
- repository checkpoint published but runtime synchronization incomplete;
- temporary tool/access/operator condition that changes the normal resume path.

Optional temporary warning text may follow the Resume section only when required
to prevent an invalid transition. Remove resolved detail; do not append history.
-->
