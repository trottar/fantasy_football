# v0.36-repack1 Live GUI Commissioning

<!-- FANTASY_EVIDENCE_V036_REPACK1_LIVE_GUI_COMMISSIONED_20260917:BEGIN -->
## Live GUI commissioning closure

Timestamp: `2026-09-17T12:09:41.522486-04:00`

Pre-commission GitHub main:
`8d4d95f8a12f1168372280381c75285bf5133647`

Release:
`v0.36-repack1` artifact revision, internal `VERSION = 0.36`.

Automated validation already completed at the production checkpoint:
- exact repaired ZIP validated;
- targeted mock-calibration tests passed;
- candidate and exact-ZIP compileall passed;
- candidate and exact-ZIP full pytest passed;
- automated GUI gate passed across 17 GUI-focused test files;
- GUI lifecycle invariants passed;
- GUI safe-module imports passed;
- `gui` and `draft-gui` CLI/parser smoke passed.

Live GUI commissioning:
- operator completed the supplied live commissioning workflow;
- service-layer smoke and live GUI launch completed without reported issue;
- dashboard interaction/recompute/refresh workflow completed without reported issue;
- historical deleted-client lifecycle failure was not observed;
- operator reported: "everything ran with no issues".

Evidence classification:
`OPERATOR-CONFIRMED LIVE RUNTIME COMMISSIONING`.

This is intentionally distinct from instrumented/automated log evidence. The
live commissioning conclusion is based on direct operator confirmation; the
automated release/GUI validation is separately machine-measured and already
durable.

Result:
`v0.36-repack1 = COMMISSIONED`.

The pre-v1.0A release gate is closed. v1.0A observability implementation is
`READY TO BEGIN`.

This evidence record does not claim an independently captured browser trace. Automated validation and operator-confirmed live commissioning are retained as separate evidence classes.
<!-- FANTASY_EVIDENCE_V036_REPACK1_LIVE_GUI_COMMISSIONED_20260917:END -->
