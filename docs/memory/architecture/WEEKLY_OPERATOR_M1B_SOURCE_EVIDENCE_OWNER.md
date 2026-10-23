# M1b — Source-bound live evidence owner (read-only candidate)

**Checkpoint candidate:** `week8_m1b_source_evidence_owner_20261023_v3`.
**State:** v2 was locally applied and staged but failed one Windows full-suite
regression (899 passed, 1 failed). This v3 correction is a source-only candidate,
not yet locally applied/published or runtime commissioned. No private live
acceptance of this source-bound owner has occurred.

## Exact evidence and narrow question

Published deadline authority `tools/operations/weekly_operator_deadline_authority.py`
(commit `4d4808cdc14c79d56d9e55662204eb6838386e40`) classifies separately
live-owned game lock scope, measured refresh time, and per-candidate waiver/trade
submission cutoffs. The classifier explicitly accepts *shape envelopes* rather
than authenticating their actual producing bytes. Its successful structural
classifications cannot be promoted into execution certificates.

The published `weekly_operator_live_lock_evidence.py` already performs a single
public ESPN NFL calendar GET and a single authenticated *read-only* ESPN league GET
and corroborates owned player/DST/kicker lock scope against the immutable prior
snapshot and frozen nflverse schedule. A second market/roster fetch is not
needed merely to source-bind that result.

**Hypothesis:** a trusted control-root read-only wrapper can verify the exact
installed source and immutable frozen snapshot before and after this single
live read, and bind its result to the published pure classifier, without
inventing waiver/trade cutoffs, refresh measurements, or action authority.

## Implemented candidate

`tools/operations/weekly_operator_source_evidence_owner.py`:

1. Validates the control-root name, week, and exact Git-blob identities of the
   previously published live-lock reader, its calendar/lock dependencies, and deadline classifier (BOM/CRLF
   representation equivalence only). Uses the existing `guarded_weekly_cycle`
   runtime identity validator; does not modify the commissioned release.
2. Requires `latest.json` to be bytewise identical to exactly one immutable
   `*/snapshot.json` in the local private runtime, with the requested season and
   week. Computes SHA-256 of actual snapshot bytes, not a guessed identity.
3. Runs exactly one invocation of the published live-lock reader. The source
   owner timestamps the call, bounds it to at most 60 seconds, rechecks the
   snapshot and source after the call, and requires the result's frozen SHA and
   season/week to match. Existing public/private fetch ordering and freshness
   checks remain owned by the published live reader.
4. Feeds that **fresh, bound observation** to the published deadline classifier.
   Crucially passes `refresh_measurement=None` and `cutoff_proofs=None`. A
   field-shape probe, an unverified JSON envelope, a raw timestamp, or a claimed
   SHA string cannot become certified refresh/waiver/trade authority.
5. Prints only fixed-field aggregate findings, hashes and clock timestamps.
   Does not print names, IDs, credentials, raw ESPN responses, source URLs or
   private exception messages. No filesystem writes, ESPN POST, provider sync,
   prospective capture, MC, staging, or Git mutations.

An accepted `lineup_window` is a *planning observation*, not a legal ESPN
lineup action or roster-wide COMPLETE. `refresh_authority`, `capture_authority`
and `action_authority` are always `NONE`. A provisional window is not a command
to launch native MC. Expired and unknown player-specific locks remain excluded.

## Remaining unproven evidence producers

The existing six-provider `season-sync` returns a snapshot, not a commissioned,
source-bound start/end duration receipt. Measuring latency from one snapshot
creation timestamp or accepting a free-form JSON duration would be a fabricated
refresh certificate. Therefore protected refresh budgeting remains blocked
without a separately commissioned duration observer bound to the exact snapshot.

`mSettings` exposes waiver processing and trade review configuration but does
**not** establish exact per-candidate claim submission/effective timestamps.
No authenticated ESPN action-screen source adapter currently proves these.
Waiver/trade cutoffs remain blocked until actual source provenance, candidate
identity, observation freshness and processing semantics can be verified in a
subsequent separate slice.

## Local-apply v1 rollback and corrective gate

The v1 local runner passed 24 targeted tests and compileall, then strict memory
health failed because `CURRENT.md` exceeded its 8-KiB soft limit (8,454 bytes).
The runner restored the predecessor `CURRENT.md` and removed all new paths;
**no local apply, staging, push or runtime change was accepted**. The v2
successor keeps diagnostic source and tests byte-identical, rewrites active
memory to retain authoritative state without checkpoint diary duplication, and
requires strict health to pass before local apply is reported. Do not rerun
passed gates except as needed to verify the exact corrected delivery package.

## Isolated Windows regression: v2 source fixture defect

The guarded v2 local apply passed targeted tests, compilation and strict memory
health; its isolated staging passed with tree `3d54f2aba3cd8b71206a383e5a4573742deaa67b`
and 206 schema-2 memory entries. Full Windows QA then returned **899 passed and
one failed**, at `test_source_guard_git_normalized_bom_and_crlf`; commit/push
were not attempted. The test prepended a BOM and expanded LF to CRLF without
first canonicalizing its starting checkout bytes. A checkout that already
contains BOM/CRLF can thereby create a *different* blob and must be rejected
by the correct source guard. V3 changes only the test fixture to normalize the
starting representation before generating exactly one BOM and CRLF sequence,
then tests both starting formats. The production read-only source guard,
classifier, and commissioned runtime remain unchanged. V2's staged tree is
superseded; new staged/tested tree and separate publication receipts are required.

## Test and next gate

25 synthetic tests cover accepted evidence and missing authority, source
mutation before/during live read, immutable snapshot identity and collision,
wrong runtime, wrong week/hash, unknown locks, probe duration, reversed or naive
clocks, private-output redaction, and classifier authority escalation. Tests
inject a synthetic live reader and perform **no network** operations.

Next: guarded local apply and targeted validation, isolated staging/index and
schema-2 manifest validation, full repository QA, separate guarded publication,
then read-only remote verification. Later add a measured six-provider receipt
producer and actual ESPN candidate-cutoff source adapter before joining the
refresh/capture phases and finite one-epoch MC recovery. M2 certification and
M3 scheduling remain distinct. No football physics or manager-behavior change.

`durable_memory_updated: true`
