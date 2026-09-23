# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

Fresh-chat recovery has resolved the unknown local state from the failed
2026-09-23 publication workflow: canonical delivery tooling and authority files
are exact, the validated player candidate is exact, and no canonical drift from
the failed infrastructure attempt was detected.

The historical v2 stage
`ff8aa263ac95075e096084399176053bb71d6fdb` remains evidence only. It must not be
used as the successor publication stage because its predecessor is older than the
current remote checkpoint and its roadmap-status bytes contain a truncated
sentence repaired by the recovery checkpoint.

Do not run the superseded publication artifacts. Publication durability must be
resolved from the containing Git/ref using the permanent declarative staging and
human commit/push boundary described by `CURRENT.md`.

## Resume

Use `../CURRENT.md` as authority. If the exact recovery state is not yet on remote
`main`, continue the generic declarative publication path from the current remote
head; if it is already remote, treat source publication as satisfied and proceed
only to the separately gated runtime synchronization/commissioning step.
