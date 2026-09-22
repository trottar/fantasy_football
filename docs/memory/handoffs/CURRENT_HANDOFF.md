# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

No exceptional transfer state is recorded.

## Resume

Follow `../CURRENT.md`'s `Exact Next Action` and load only its task-relevant
canonical references.

If a future transition is interrupted between local apply, staging, commit/push,
runtime synchronization, or commissioning, record only that exceptional
condition here and remove it once resolved.
