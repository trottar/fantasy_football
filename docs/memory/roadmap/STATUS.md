# Roadmap Status

## Phase 0 — Reconcile/freeze final 0.X

- [x] Git repository bootstrapped from commissioned v0.35-fixed1 source.
- [x] Durable-memory architecture established.
- [ ] Reconcile exact v0.36 source/release lineage.
- [ ] Reconcile v0.36 GUI fixed release/commissioning status.
- [ ] Preserve Week 2 prospective capture if still causally possible.

## v1.0 — Observability and durable evidence

- [ ] Immutable Week 1 observation ingestion.
- [ ] Link frozen Week 1 predictions to observed data.
- [ ] `week-recap` command.
- [ ] Player availability/workload/yield residuals.
- [ ] DST component closure.
- [ ] Kicker observed opportunity ledger.
- [ ] Full-league residual distributions.
- [ ] Transaction/event ledger.
- [ ] Anomaly classification/investigation generation.
- [ ] Cumulative weekly evidence index.
- [ ] No automatic calibration.

## v1.1 — General closure engine

- [ ] Cumulative residual/pull/coverage statistics.
- [ ] Calibration ledger and evidence thresholds.

## v1.2 — Waiver/FA resolver

- [ ] Ordered manager claim lists.
- [ ] League-wide priority/claim/drop resolver.
- [ ] Real transaction evidence integration.

## v1.3 — Trade engine rebuild

- [ ] Systematic 1-for-1, 1-for-2, 2-for-1, 2-for-2 search.
- [ ] Separate football response, roster construction, perception, and acceptance kernels.

## v1.4+

- Evidence-supported calibration.
- Specialist closure/calibration.
- Physical kicker opportunity model.
- Standings/playoff/championship-equity state.
- Integrated operational GUI.

<!-- FANTASY_ROADMAP_REVISION_2026_09_17_OBSERVABILITY:BEGIN -->
## Authoritative roadmap revision — 2026-09-17

This block supersedes the earlier coarse v1.0/v1.1 ordering above where they conflict.

### Phase 0 — reconcile/freeze final 0.X — ACTIVE
- [x] repository and durable-memory foundation
- [x] v1.4 raw baseline/v0.36 comparison measurements obtained
- [x] v1.4 classifier marked representation-incomplete; raw evidence retained
- [ ] inspect sanitized v1.4 evidence bundle
- [ ] establish final exact 0.X lineage and GUI fixed-release status
- [ ] freeze exact source/version/hash/test/commissioning state
- [ ] preserve Week 2 prospective capture while causally possible

### v1.0A — diagnostics/observability substrate — DEVELOPMENT-ONLY UNTIL PHASE 0 FREEZE
- [x] architecture/contract adopted
- [ ] static diagnostic-surface audit of current/baseline candidates
- [ ] immutable run/action context schema
- [ ] structured event schema and event registry
- [ ] human + machine-readable sinks
- [ ] provenance/config/input hashing
- [ ] invariant registry
- [ ] local snapshot/replay/diff contract
- [ ] failure-bundle contract
- [ ] privacy/redaction contract and tests
- [ ] subsystem adapters: player / DST / K / lineup / market / closure
- [ ] CLI/service/background-task correlation
- [ ] GUI diagnostics: lifecycle, client/session, page mount/unmount, actions, background tasks, services, render/refresh, stale-client protection
- [ ] diagnostic overhead/non-interference tests
- [ ] commissioning criteria and documentation

### v1.0B — immutable observation/evidence layer
- [ ] immutable Week 1 observations
- [ ] frozen prediction linkage
- [ ] transaction/event ledger
- [ ] availability/workload/opportunity observations
- [ ] DST component observations
- [ ] kicker opportunity/yield observations
- [ ] cumulative evidence index

### v1.0C — Data/MC closure
- [ ] `week-recap`
- [ ] player opportunity/efficiency/scoring residuals
- [ ] DST component closure
- [ ] kicker closure
- [ ] league residual distributions
- [ ] anomaly classification/investigation generation
- [ ] zero automatic calibration

### v1.1 — cumulative evidence / calibration authorization
- [ ] residual/pull/coverage accumulation
- [ ] availability Brier tracking
- [ ] calibration ledger
- [ ] evidence thresholds/authorization; no calibration without evidence

### v1.2 — waiver/FA resolver
- [ ] ordered contingent manager claim lists
- [ ] league-wide priority/claim/drop resolution
- [ ] direct vs field vs manager-behavior diagnostics
- [ ] real transaction evidence integration

### v1.3 — trade engine
- [ ] systematic 1-for-1 / 1-for-2 / 2-for-1 / 2-for-2 search
- [ ] football / roster / scarcity / behavior / acceptance diagnostics
- [ ] package-level response/replay evidence

### v1.4+ — evidence-supported expansion
- player calibration when authorized by evidence
- specialist closure/calibration
- physical kicker opportunity model
- standings/playoff/championship utility
- integrated operational GUI consuming typed services

The later integrated GUI phase does not defer GUI diagnostics: GUI observability is built in v1.0A and is a commissioning requirement for later UI work.
<!-- FANTASY_ROADMAP_REVISION_2026_09_17_OBSERVABILITY:END -->

<!-- FANTASY_MEMORY_INFRA_READY_ROADMAP:BEGIN -->
## Infrastructure readiness checkpoint

- [x] PrivyHub-style memory checkpoint delivery/push workflow
- [x] standing authorization boundary for memory + diagnostics
- [x] explicit production-code authorization boundary
- [x] exact memory staging allowlist
- [x] remote-moved and post-push verification
- [x] manifest self-exclusion / relative-path semantics
- [x] Git-index / committed-blob manifest semantics
- [x] GUI diagnostics included in v1.0A architecture

Memory/diagnostic infrastructure: `READY`.

Next active technical work remains:
- finish Phase 0 final 0.X lineage reconciliation;
- preserve prospective Week 2 evidence;
- continue v1.0A diagnostic/observability substrate.
<!-- FANTASY_MEMORY_INFRA_READY_ROADMAP:END -->

<!-- FANTASY_I001_V2_ROADMAP:BEGIN -->
## Phase 0 I-001 v2 checkpoint

- [x] v1.4 raw measurement history preserved
- [x] v1.4 name-only classifier superseded
- [x] v1 review failure recorded: missing ephemeral evidence ZIP
- [x] v2 evidence reconstructed from authoritative artifacts
- [ ] final 0.X freeze/commissioning decision

Current result: `V036_EXACT_RELEASE_PRESENT_FIXED1_NOT_ESTABLISHED`
Authority: `V036_LATEST_EXACT_ARTIFACT_FIXED1_UNPROVEN`

No football physics change is authorized by this diagnostic.
<!-- FANTASY_I001_V2_ROADMAP:END -->

<!-- FANTASY_ROADMAP_DIAGNOSTIC_QA_HOLD:BEGIN -->
## Phase 0 diagnostic QA checkpoint

- [x] exact v0.36 artifact established
- [x] v0.36-fixed1 exact artifact/provenance not established
- [x] GUI-lineage diagnostic failure classified
- [x] validation gap identified
- [x] diagnostic-tool QA release gate defined
- [ ] corrected GUI-lineage diagnostic passes exact-package QA
- [ ] corrected GUI-lineage diagnostic runtime
- [ ] final 0.X GUI/commissioning decision

This QA hold changes no football physics and does not supersede the successful
I-001 v2 evidence result.
<!-- FANTASY_ROADMAP_DIAGNOSTIC_QA_HOLD:END -->
