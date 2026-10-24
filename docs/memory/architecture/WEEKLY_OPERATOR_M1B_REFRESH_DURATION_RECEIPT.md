# M1b — Measured six-provider refresh-duration source receipt (source-only)

**Candidate:** `week8_m1b_sync_duration_receipt_source_20261023_v1`.
**Gate:** synthetic source-only code; no local runtime commissioning, no live sync
execution, no evidence from an actual measured six-provider run yet.

## Authority and narrow missing observation

The source-bound live owner checkpoint at remote commit
`98371db7a152d071a3f2ac831dd3d7b85bf26f26` passed 901 isolated tests
and left the commissioned v0.36-repack1 runtime untouched. The earlier pure
`weekly_operator_deadline_authority.py` requires a *recent measured* sync duration,
an explicit extra buffer, a valid `0.36` runtime version and a receipt checksum;
it cannot determine a duration from an ending `snapshot_utc` or a fabricated
JSON envelope. The source-bound live owner therefore deliberately supplied
`refresh_measurement=None`, blocking refresh planning.

`src/season_snapshot.py:sync_season_snapshot()` performs six-provider acquisition
and only stamps its final `snapshot_utc` immediately before writing both a
unique `*/snapshot.json` and `latest.json`. It does not record the call start,
monotonic elapsed duration or a measurement receipt. A trusted observation
must be captured *inside the very same authorized sync call*; guessing from
post-hoc file creation times is not a valid substitute.

## Implemented diagnostic, and its limits

`tools/operations/weekly_operator_refresh_duration_receipt.py` contains only
in-process measurement and verification functions, with no CLI, scheduler,
`season-sync` import, network client, or standalone refresh launcher:

- `measure_authorized_sync(...)` requires a caller-supplied existing authorized
  sync callable, validates the published source-owner Git blob and its exact
  dependencies plus the commissioned runtime identity, observes before/after
  UTC and monotonic nanosecond clocks, and invokes **exactly one** callback.
  A failed callback is never retried. The helper itself has no permission to
  trigger a fresh provider acquisition independently.
- A successful measurement requires valid nonnegative wall chronology agreeing
  with the monotonic clock, all six source-health channels passing, the returned
  snapshot matching the actual bounded immutable file, a unique immutable copy
  bytewise equal to `latest.json`, exact 2026/week identity, and the snapshot
  timestamp inside the measured interval. Source identity is rechecked afterward.
- It returns only sanitized measurement fields: actual integer-ceiled duration,
  explicit extra buffer, public version/week, snapshot SHA-256/UTC and fixed
  non-authority flags. No roster, account IDs, raw authenticated provider
  responses, credentials, URLs, filesystem paths, or private exception text.
- `persist_private()` is **separate** and opt-in. It exclusively creates a
  receipt under the already-private runtime `data/season_decisions/` path.
  An existing epoch cannot be overwritten; failure does not authorize retry of
  the original refresh. The emitted checksum is computed from written bytes.
- `verify_private()` independently re-reads the receipt bytes and actual unique
  immutable snapshot, checks both hashes, source labels, six-provider health,
  chronology, explicit duration/buffer, 14-day freshness, and `NONE` action
  authority before returning a shape-compatible planning envelope.

All receipt hashes are **integrity checks against local bytes, not signatures or
proof that a caller held ESPN transaction rights**. A caller must separately
establish that the wrapped sync was explicitly scheduled/authorized, verify
its private runtime and trusted dependency provenance, and independently bind
fresh live locks and exact transaction cutoffs. The planning classifier's
potential `PROVISIONAL_PLANNING_WINDOW_NOT_REFRESH_AUTHORITY` remains **planning
only**, not permission for MC, capture, trade, waiver, lineup or ESPN writes.

No automatic integration has been made into the commissioned runtime or
M1a/M1b orchestration. The function is *not executed* merely by installing the
source checkpoint; the protected Saturday capture is a separate priority.

## Acceptance and follow-up

Synthetic tests cover one-call behavior, no retry on error, source tampering,
invalid runtime/week/buffer, monotonic and UTC disagreement, incomplete six
providers, stale or mismatched snapshot bytes, duplicates, exclusive private
receipt writing, independent read-back, hash tampering and stale measurement.
No actual six-provider duration claim exists until a permitted live run returns
an exact receipt. No synthetic test authorizes a refresh or transaction.

Next repository gates: guarded local apply and targeted tests; isolated staging
and schema-2 manifest; full isolated pytest and compileall; separate guarded
publication; remote read-only verification. Following publication, explicitly
integrate the opt-in observer into the operator's separately authorized native
sync path and perform a real source-bound measurement without repeating or
backfilling a prior prospective epoch. Per-candidate ESPN claim/trade submission
cutoffs remain a separate missing source adapter.

`durable_memory_updated: true`
