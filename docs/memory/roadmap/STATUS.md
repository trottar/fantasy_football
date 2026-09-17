# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Active development series: **v1.0A observability**
- Latest checkpoint: **sinks + provenance hashing — COMPLETE**
- Exact next slice: **invariant registry + privacy/redaction primitives**

## Phase 0 — Final 0.X Freeze

- [x] reconcile exact v0.36 lineage
- [x] establish no exact historical v0.36-fixed1 artifact/provenance
- [x] isolate packaged-test failures
- [x] prove fixture-only packaging defect
- [x] import validated v0.36 source
- [x] build exact packaging-only repack
- [x] automated full/GUI validation
- [x] operator-confirmed live GUI commissioning
- [x] close I-001

Do not reopen without new evidence.

## v1.0A — Diagnostics / Observability Substrate

Completed:
- [x] architecture/contract adopted
- [x] static diagnostic-surface audit
- [x] immutable run/action context
- [x] structured event schema
- [x] immutable event registry
- [x] generic run/action event namespace
- [x] GUI lifecycle/action/service/task/state/render/refresh namespace
- [x] context/event immutability and RNG non-interference tests
- [x] human-readable sink contract
- [x] JSONL machine sink contract
- [x] in-memory/fanout sink contracts
- [x] provenance/config/input hashing helpers
- [x] source commit + tracked-dirty provenance
- [x] sink/provenance non-interference tests

Next:
- [ ] invariant registry
- [ ] privacy/redaction contract and tests

Then:
- [ ] local snapshot/replay/diff contract
- [ ] failure-bundle contract
- [ ] subsystem adapters: player / DST / K / lineup / market / closure
- [ ] CLI/service/background-task correlation
- [ ] GUI event emission/integration
- [ ] diagnostic overhead/non-interference benchmarks
- [ ] v1.0A commissioning criteria

Production call-site event emission and persistent private/authenticated logging
remain deferred until privacy/redaction and integration contracts are ready.

## v1.0B — Immutable Observation / Evidence Layer

- [ ] immutable Week 1 observations
- [ ] frozen prediction linkage
- [ ] transaction/event ledger
- [ ] availability/workload/opportunity observations
- [ ] DST component observations
- [ ] kicker opportunity/yield observations
- [ ] cumulative evidence index

## v1.0C — Data / MC Closure

- [ ] `week-recap`
- [ ] player opportunity/efficiency/scoring residuals
- [ ] DST component closure
- [ ] kicker closure
- [ ] league residual distributions
- [ ] anomaly classification/investigation generation
- [ ] zero automatic calibration

## v1.1 — Cumulative Evidence / Calibration Authorization

- [ ] residual/pull/coverage accumulation
- [ ] availability Brier tracking
- [ ] calibration ledger
- [ ] evidence thresholds; no calibration without evidence

## v1.2 — Waiver / FA Resolver

- [ ] ordered contingent manager claim lists
- [ ] league-wide priority/claim/drop resolver
- [ ] direct vs field vs manager-behavior diagnostics
- [ ] real transaction evidence integration

## v1.3 — Trade Engine

- [ ] systematic 1-for-1 / 1-for-2 / 2-for-1 / 2-for-2 search
- [ ] football / roster / scarcity / behavior / acceptance diagnostics
- [ ] package-level response/replay evidence

## v1.4+

- evidence-supported player calibration
- specialist closure/calibration
- physical kicker opportunity model
- standings/playoff/championship utility
- integrated operational GUI consuming typed services
