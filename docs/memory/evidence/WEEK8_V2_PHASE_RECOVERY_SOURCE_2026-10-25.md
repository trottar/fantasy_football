# Week 8 v2 — Source-Bound Phase Recovery Candidate

**Classification:** structural workflow gap / source-only repair candidate.
**Observed predecessor:** GitHub remote `bc3575407f73bc1dc282deb208632af0746b9000`, tree `6a0dd6dd74f38339974e5bfd1bfa50f4d02720fe` (published 2026-10-25); 1046 isolated full repository tests. Source publication is not runtime commissioning.

## Original observed defect

`tools/operations/weekly_operator_v2.py` wrote one create-only launch marker
before calendar/sync/capture/MC. An interrupted process with no final report
could never resume a validated successful sync or prospective capture from the
same slot: `PRIOR_SLOT_ATTEMPT_UNCERTAIN_DO_NOT_REPEAT` prevented all progress.
Repeated manual operator intervention would be necessary and could risk losing a
prospective Week 8 capture gate.

## Repair contract

- Create and commit phase-start evidence before the external native sync,
  prospective capture, or M1a MC call. The start binds exact source hash,
  immutable slot launch marker and necessary input SHA-256 identities.
- Write a separate completion only after fresh source-native bytes and epoch
  validate; reuse requires that receipt, matching dependency identities,
  unique immutable snapshot/capture and bounded age (two hours).
- A started native sync/capture lacking completion is **uncertain**, even if
  someone suspects that the external command finished. Never auto-repeat it.
- Re-invoke M1a only under its independent native MC launch-marker/receipt
  contract; no duplicate MC and no post-game retrospective capture.
- The existing optional commissioning file must bind the exact new source;
  source/test installation alone never executes this workflow, performs an ESPN
  GET/POST, activates scheduling, or makes a football action certificate.

## Testing and authority limits

Deterministic synthetic tests cover process kill after durable capture, aborted
sync/capture, changed phase dependencies, receipt corruption, saved-evidence
freshness and integrity, MC receipt omission, idempotent slot/report reuse and
transaction-authority non-escalation. These tests are **not** evidence of real
local Windows runtime operation, source-health receipt availability, full ESPN
transaction timing, §5A action certification, complete-roster report, scheduler
installation or first prospective Week 8 capture.

Subsequent required gates: strict local apply; isolated full repository QA and
Git-index schema-2 manifest; guarded publication; live read-only integration
commissioning; bounded drift recovery; action/risk certification; one ranked
report; scheduler dry-run and explicit activation. Protect Week 8 calendar gates
before optional nonessential development.

`durable_memory_updated: true`
