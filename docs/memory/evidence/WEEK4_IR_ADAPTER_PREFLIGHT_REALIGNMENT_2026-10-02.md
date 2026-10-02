# Week 4 IR Adapter Preflight Realignment — 2026-10-02

---
evidence_type: production_preflight_reconciliation
status: CLASSIFIED
football_model_tuning: false
production_authorization: granted
reference_remote: 24e09e586d113d10e8884f1fb4173a58b3fd1297
runtime_release: v0.36-repack1
internal_version: "0.36"
nfl_week: 4
---

## Objective

Reconcile three consecutive non-mutating IR-adapter source-preflight failures,
audit the candidate against the authoritative memory/source boundary, and define
the next safe production-design frontier before another carrier is issued.

## Stable Scientific State

The fresh Week 4 decision cycle remains valid evidence:

- snapshot UTC: `2026-10-02T05:25:32.944434+00:00`;
- prospective capture UTC: `2026-10-02T05:25:33.654991+00:00`;
- operational health: PASS;
- overall weekly state: `INCOMPLETE_COVERAGE`;
- eight of nine required channels: valid receipts;
- sole unsupported channel: `ir_reserve_open_slot_injury_replacement`.

B2a proves one current legal transition:

- active roster: 16 / 16;
- IR occupancy: 0 / 1;
- direct open active slots: 0;
- one unlocked `OUT` QB IR-move candidate;
- `IR_MOVE_PLUS_ADD_CAPACITY=1`;
- IR blockers: none.

Corrected B2b claim-local freshness retained zero qualifying horizon claims.
B2b remains **DEFERRED / FAIL-CLOSED**.

## Production Authorization

The user explicitly authorized the current IR move-plus-add value/capacity adapter
production change on 2026-10-02.

Authorization does not waive the source/change health gate, causal boundaries, or
weekly completion contract.

## Preflight Failure Lineage

### v1 — cleanup harness

Package:
`weekly_decision_gate_b2_ir_move_plus_add_source_preflight_v1_20261002`.

Failure:
Windows `PermissionError` while removing a read-only Git pack index from the
disposable clone.

Classification:
**DIAGNOSTIC HARNESS CLEANUP FAILURE / NON-MUTATING**.

No source, runtime, staging, commit, or push occurred.

### v2 — candidate/full-suite mismatch

Package:
`weekly_decision_gate_b2_ir_move_plus_add_source_preflight_v2_20261002`.

The preflight reached full `pytest`:

- 576 passed;
- 1 failed.

The failure was:
`test_weekly_contract_identifies_multi_asset_player_trade_search_gate`, whose
existing assertion still required
`WEEKLY_DECISION_COMPLETION_GATE_B4_SPECIALIST_TRADE_COMPOSITION_V001`
after the candidate intentionally advanced the weekly contract.

Because the package ran its targeted test set before full pytest, those targeted
Gate A/B regressions passed.

Classification:
**CANDIDATE VALIDATION FAILURE / NON-MUTATING**.

This is historical validation evidence only; later source audit invalidated the v2
candidate as a release candidate.

### v3 — deterministic transform-routing defect

Package:
`weekly_decision_gate_b2_ir_move_plus_add_source_preflight_v3_20261002`.

Failure:
the package appended the existing-test contract transform to one global
`TRANSFORMS` list, then called that list against `src/weekly_decision_cycle.py`.
The test-only assertion was therefore incorrectly required to occur in the weekly
source and failed with transform-anchor count 0.

Classification:
**DETERMINISTIC PACKAGE-CONSTRUCTION FAILURE / NON-MUTATING**.

This should have been caught before delivery. Future deterministic transform
packages must key transforms by target path and execute the exact production
routing algorithm in package QA.

## Source-Audit Corrections

The post-v3 audit found substantive defects in the v2 candidate design.

### Decision-time locks

The candidate player frontier excluded only rows with `lineup_locked=true`.

The commissioned specialist lock boundary also treats a current-week asset as
locked when kickoff has passed relative to the snapshot. The IR adapter must use
the commissioned decision-time kickoff-aware lock semantics rather than a weaker
flag-only test.

### Legal specialist branch completeness

League position maximums allow up to three DST and three K.

The candidate skipped an additional-kicker open-slot branch when one kicker was
already owned because the general specialist `CARRY2` policy disables two
kickers.

That disabled policy is not evidence that a distinct league-legal open-slot
transaction branch may be omitted. Under the weekly completion contract, any
unsupported relevant legal branch must remain explicit
`INCOMPLETE_COVERAGE`.

### Capacity scope

The observed Week 4 state has no direct open active slot. Its sole proven new
capacity is exactly one active slot created by the legal B2a IR move.

The next candidate should target that one-slot transition and fail closed on
broader unsupported current-capacity states instead of conflating persistent
direct open slots with IR-created capacity.

## Redesigned Production Contract

The next non-mutating source preflight must:

1. consume the current B2a legality authority without changing it;
2. support exactly the proven one-slot IR-move-plus-add transition and fail closed
   on broader unsupported capacity states;
3. use kickoff/snapshot-aware current-week lock semantics;
4. preserve FREEAGENT versus WAIVER acquisition uncertainty;
5. preserve `P ⊕ D ⊕ K` and compose only at complete-roster boundaries;
6. cover every league-legal QB/RB/WR/TE/DST/K acquisition branch made relevant by
   the opened slot, or explicitly leave the IR channel incomplete for any
   unsupported branch;
7. credit no future IR capacity while B2b remains deferred;
8. preserve mature player add/drop and commissioned specialist authorities unless
   exact source evidence requires a minimal reusable primitive;
9. route deterministic transforms by exact target path and regression-test the
   actual routing helper before package delivery;
10. rerun targeted tests, full pytest, compileall, strict memory health, and
    `git diff --check` because the production design is changing from v2.

## Boundary

The v1-v3 candidate line is superseded. No production source/runtime modification
has been applied, staged, committed, pushed, or commissioned.

The active blocker remains:
`CURRENT_IR_MOVE_PLUS_ADD_VALUE_ADAPTER_GAP`.

`durable_memory_updated: true`
