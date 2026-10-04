# Week 4 Lineup Lock Authority Defect - 2026-10-04

---
evidence_type: structural_authority_defect
status: SOURCE_CANDIDATE_LOCAL_APPLIED_VALIDATED
football_model_tuning: false
reference_remote: 1cfce15ba6838901883dfcfd60132a87bbe3f2f7
runtime_release: v0.36-repack1
internal_version: "0.36"
nfl_week: 4
---

## Trigger Evidence

The fresh post-multi-K cycle produced:

- snapshot UTC `2026-10-04T21:30:24.707083+00:00`;
- prospective capture UTC `2026-10-04T21:30:25.525534+00:00`;
- operational health `PASS`;
- all 9 required receipt channels present;
- overall raw receipt `COMPLETE / ACTION_REQUIRED`;
- action channels `lineup_availability` and `trade_specialist_inclusive`;
- player lock scope 13 locked / 1 unlocked / 0 unknown;
- specialist lock scope 1 locked / 1 unlocked / 0 unknown;
- four corrected specialist-inclusive offers.

A read-only audit showed the lineup action selected locked-bench Jakobi Meyers into
the starting lineup. The audit's simplified Kamara lock label was not authoritative;
the commissioned cycle itself had zero unknown player locks.

## Source Diagnosis

`weekly_decision_cycle._default_lineup` constructed `UtilityContext` and reported
locked ESPN IDs, but called `weekly_manager.optimize_lineup` on the unconstrained
roster and set `action_required` from `selected != current`.

The commissioned timing authority already existed in
`UtilityContext.lock_timing -> availability_timing.player_lock_timing`.
Therefore the defect was orchestration/authorization logic, not projection or MC
calibration.

Classification:
`WEEKLY_LINEUP_LOCK_AUTHORITY_CONSTRAINT_DEFECT`.

## Authorized Structural Correction

The correction is intentionally confined to `src/weekly_decision_cycle.py`:

- explicit ESPN locks remain locked;
- kickoff at/before snapshot time remains locked through `ctx.lock_timing`;
- locked starters are frozen in their current slots;
- locked bench players cannot enter the lineup;
- unlocked players optimize only over remaining legal slots;
- unresolved lock timing or unsupported current lineup slots fail closed as
  `INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY`;
- `action_required` is computed only from a legally executable selected lineup.

`weekly_manager.optimize_lineup`, player MC, DST/K policy, trade valuation,
manager behavior, IR logic, and empirical calibration remain unchanged.

## Validation Lineage

Fresh-cycle diagnostic carrier v2 failed before data capture with
`ModuleNotFoundError: src` because changing cwd did not update the running
interpreter's import path. Corrected v3 explicitly installed the runtime root,
then captured the authoritative October 4 evidence above.

Lineup source preflight v1 reached all validation gates but failed final changed-path
inventory because a Git CRLF warning from stderr was merged into stdout and treated
as a filename. It was non-mutating.

Lineup source preflight v2 preserved the exact candidate and separated stderr from
inventory stdout. Result:

- changed paths 2 / exact;
- locked bench excluded: PASS;
- locked starter frozen: PASS;
- kickoff lock enforced: PASS;
- unknown lock state: FAIL-CLOSED;
- unsupported current slot: FAIL-CLOSED;
- frozen Oct. 4 Meyers locked-bench exclusion: PASS;
- frozen Oct. 4 Kamara lock state resolved through commissioned timing: PASS;
- targeted pytest: carried-forward PASS from v1;
- full pytest: carried-forward PASS from v1;
- compileall: carried-forward PASS from v1;
- strict memory health: carried-forward PASS from v1;
- `git diff --check`: carried-forward PASS from v1.

Exact validated candidate:

- `src/weekly_decision_cycle.py`
  - SHA-256 `b48162719044e625e32f23b882d9030c1bf22323a473b11a48d200f30731b852`
  - Git blob `7969052173582e7b10bbdd846fb9f72ad104d676`
- `tests/test_weekly_decision_lineup_lock_authority.py`
  - SHA-256 `c9046463d090088f6ff290420a185c77c245f10a4558de0a42101f7632a4461d`
  - Git blob `4cd790e3cf82c3a5dd66e1aece8f4d5272e68c79`

## Decision Boundary

The October 4 snapshot/capture are preserved as valid prospective evidence. The
receipt is also valid evidence of the authorization defect, but its lineup action
is not executable. The four specialist offers are post-multi-K diagnostic evidence
only until the lineup correction is published, commissioned, and a fresh weekly
cycle reauthorizes current actions.

B2b remains **DEFERRED / FAIL-CLOSED / NO FUTURE CAPACITY CREDIT**.

`durable_memory_updated: true`
