# M1b — Independent cutoff evidence and protected refresh planning (source-only slice)

**Checkpoint candidate:** `week8_m1b_deadline_authority_source_20261023_v1`.
**Status:** observational, pure source-only helper and deterministic tests. Not installed,
not source-published, not runtime-commissioned, not a live proof of exact waiver
submission times, and not authorization to start a six-provider refresh, MC, or ESPN write.

## Narrow evidence and problem

The published pre-refresh live owned-roster/lock diagnostic is remote verified at
`0d0b59b290df97bbdf1416564c2cb84373befc8e` with 833 passing isolated tests.
A private October 23 acceptance saw 16 frozen and live owned records, zero
adds/removals, four material changes, 14 future unlocked, one elapsed, one bye,
zero unknown live locks, and independently corroborated NFL calendar. It returned
`READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED`, with explicit refresh,
capture and action authority all `NONE`. The report is not itself durable live
source freshness; it must be reacquired and timestamp-bound at each future use.

Two private `mSettings` field-shape probes ran without ESPN writes. The v3 report
observed `acquisitionType` (string), `waiverProcessHour` (integer), `waiverHours`
(integer), `waiverProcessDays` (six strings), `transactionLockingEnabled`
(boolean), trade `deadlineDate` (integer), `revisionHours` (integer), and roster
`lineupLocktimeType` / `rosterLocktimeType` (strings). Raw league values and
credentials remain private. **None of those shapes certifies an exact claim
submission cutoff, per-asset acquisition transition, legal effective timestamp,
or ESPN app legality.** Waiver processing time is not claim-submission time.

The next testable missing piece is to classify independently supplied evidence
without inventing those deadlines or confusing a planning window with authority.

## Implementation

`tools/operations/weekly_operator_deadline_authority.py` exports a pure
`classify(now, live_lock_result, live_observed_at_utc,
rule_source_shapes=None, refresh_measurement=None, cutoff_proofs=None)` helper.
It uses only Python's standard library. No direct provider calls, network, local
filesystem, import of commissioned production code, phase launch, or persistence.
Its explicit clock comes from the caller; no backdated operational authority.

- **Game/lineup:** accept only the exact source-labeled live lock diagnostic's
  known non-blocked statuses, corroboration label, one authenticated GET, zero
  unknown live owned locks, future owned unlocked assets, strictly future known
  earliest kickoff, `NONE` authority, and a caller-provided independently bound
  fresh (at most 60-second-old) observation timestamp. Public and private
  check ages are individually bounded. Its aggregate earliest future owned
  kickoff can establish a *planning floor*, never a legal roster action or
  per-asset lineup executable state. Expired games, byes, ambiguous locks and
  specific candidate eligibility must be separately excluded/reconciled.
- **Refresh duration:** require a recent locally measured six-provider sync
  duration, explicit additional buffer, commissioned runtime version and a
  receipt checksum. Treat the evidence envelope as provisional, not cryptographic
  validation of the referenced receipt. Sum `ceil((duration + buffer)/60)` with
  the existing 40+15+15+10 = 80-minute minimum. Unknown, stale, malformed or
  unbounded measurement blocks a protected planning pass; equality with kickoff
  also blocks. No hard-coded claim that 40 minutes is a certified refresh margin.
- **Waiver:** refuse to derive exact claim cutoff from `mSettings` names or types.
  An optional fresh, candidate-scoped, independently verified live ESPN
  action-screen envelope must state an explicit submission cutoff. The helper
  validates shape/chronology/source labels and planning slack **only**;
  accepting a supplied object does not authenticate the source or prove ESPN
  submission legality. Without that envelope, waiver remains blocked even if
  lineup planning is possible.
- **Trade:** independently require an explicit submission cutoff **and** modeled
  effective timestamp from a fresh, candidate-scoped action-screen envelope.
  Processing/review duration and final league deadline cannot be silently
  promoted into a timestamp. An effect may precede the *league-wide final
  deadline*; reject only an effect already elapsed relative to `now`, not
  ordinary early processing. Additional trade review, transaction-effective
  semantics and partner/roster consequences remain mandatory elsewhere.
- **Reporting:** each family has an independent fail-closed classification.
  All results always retain `refresh_authority=NONE`,
  `capture_authority=NONE`, `action_authority=NONE`, `espn_writes=false`,
  `native_mc_started=false`, and `automatic_refresh_or_capture=false`.
  Returning `PROVISIONAL_PLANNING_WINDOW_NOT_REFRESH_AUTHORITY` is **not**
  permission to launch native refresh or MC.

The existing published `deadline_budget.py`, `weekly_operator_live_lock_evidence.py`,
`guarded_weekly_cycle.py`, commissioned `fantasy_season_v0_36_repack1`, native
physics, manager behavior and all immutable Week 7 captures remain unchanged.
This slice intentionally does **not** compose into production orchestration.

## Acceptance and next gate

Deterministic tests cover current/stale/unknown lock evidence, invalid or stale
measured refresh provenance, positive-slack strictness, missing or merely shaped
ESPN waiver rules, independent waiver/trade envelopes, bad/elapsed cutoffs,
trade effect chronology, invalid source envelopes, sanitized outputs, and no
network/ESPN writes. Local package acceptance, full isolated suite, exact
schema-2 staged manifest, separate guarded publication and remote verification
are independent future gates; do not claim them from synthetic testing.

After publishing this source slice, integrate a *live source owner* for the
independent timestamps/receipt lookup and exact per-candidate ESPN transaction
cutoff verification, then compose it with the existing separate six-provider
refresh/capture and restart-safe native MC phases. Preserve at most one recovery
epoch and never backfill frozen prospective predictions. Do not mistake the
status of any individual channel for roster-wide certification.

`durable_memory_updated: true`
