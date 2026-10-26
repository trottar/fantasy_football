# Week 8 Monday native receipt: health checkpoint join mismatch

**Classification:** observed live acceptance blocker plus deterministic source contract defect, structural correction for future captures only.

## Frozen direct evidence

On October 26, 2026 the explicitly invoked Week 8 `trial --ack-live-readonly`
returned `BLOCKED_HEALTH` after `CALENDAR`, `SYNC`, `CAPTURE`, with a redacted
`STAGE_EXCEPTION_Blocked`. Two independent no-network diagnostics proved the
immutable snapshot/capture and phase completion bindings, prospective firewall
and canonical snapshot join. Exactly one matching native decision receipt and
one launch marker exist for the frozen Monday capture, with no v2 MC-done.
`weekly_operator_review.discover` and `weekly_operator_controller.inspect`
reported `NATIVE_RECEIPT_HEALTH_OR_CHRONOLOGY_INVALID`. Diagnostic ESPN
requests/MC launches/file writes were zero. Neither presence of a native receipt
nor a launch marker alone certifies nine-channel MC or roster action authority.

## Source-owned discrepancy and hypothesis

`tools/operations/weekly_operator_v2.py` constructs fresh strict-memory input
receipts with `status=PASS`, `strict=True`, `checked_utc` but omits
`source_checkpoint`. It correctly includes the commissioned v0.36
`source_checkpoint` in its parallel runtime-identity receipt. Native Gate A's
`build_operational_health_receipt` (`src/weekly_operational_health.py`) requires
the memory checkpoint to be equal to the identity checkpoint, otherwise it
appends a `memory_health:` blocker and returns `BLOCKED_HEALTH`. The previous
synthetic test asserted only the memory `strict` flag, missing this invariant.
This defect is guaranteed in the published source, but the live Monday receipt's
complete health blocker inventory has not been inspected; the defect cannot be
assumed to be the sole issue. Its chronology fields are not independently
classified by the two diagnostic receipts.

## Patch and boundary

Add `source_checkpoint=guarded.EXPECTED_SOURCE_CHECKPOINT` to **future** verified
M1a memory receipts; assert parity with the source-bound runtime identity and
test the actual native Gate A `PASS`/`BLOCKED_HEALTH` result for matching/missing
checkpoints. Preserve original v0.36 physics, channel separation, ESPN read-only
authority, and M1a no-repeat semantics. Do not rewrite frozen Monday prediction,
receipt, launch marker, or failed trial report; do not rerun the Monday MC. The
Tuesday/Wednesday Week 8 capture must be genuinely new and before independently
verified relevant game/transaction locks. Live Windows operational acceptance
and whole-action certification remain pending.

`durable_memory_updated: true`
