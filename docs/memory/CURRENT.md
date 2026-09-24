# Current Project State

---
state_updated: 2026-09-23
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1d_behavior_shadow_source_checkpoint
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Publish and commission the source-validated Phase 1D manager-behavior shadow at
`trade_response_probabilities`, while preserving Week 3 prospective evidence
gates. Trade-search operational readiness remains a preferred pre-Week-4 target.

## Current Work Item

**Phase 1D behavior shadow: SOURCE CANDIDATE VALIDATED / LOCAL-APPLIED /
ISOLATED STAGING NEXT.**

Accepted boundary:
`src/market_manager.py::trade_response_probabilities` at
`subsystem.behavior.trade_response_probabilities`.

The candidate adds bounded, in-memory, fail-open observation only at this narrow
behavior kernel. `search_trades`, `evaluate_trade`, and
`perceived_market_value` remain uninstrumented. No football value, trade-response
formula, recommendation authority, or persistent sink is changed.

## Verified State

- Commissioned runtime remains **v0.36-repack1**, internal `VERSION = 0.36`.
- Phase 1A, 1B, and 1C observability are runtime commissioned; Phase 1C preserves
  separate player/DST/K boundaries.
- Persistent observability sink remains **DISABLED**.
- Phase 1D boundary discovery rejected mixed `search_trades` and
  `evaluate_trade` as behavior-only surfaces.
- Non-modifying Phase 1D paired runtime probe passed output/error equivalence,
  Python/NumPy RNG and mutable-state non-interference, privacy/correlation,
  fail-open behavior, and absolute-overhead gates. Response model remains
  `UNCALIBRATED_TRADE_RESPONSE_V030`.
- Isolated source preflight at predecessor
  `c9ad2b383522038d03343ba04989ea206f1d8931` passed 46 targeted tests,
  retained paired probe, 517 full-suite tests, `compileall`, strict memory
  health, exact six-path identities, and cleanup with no residue.
- Local-apply v1 failed before write because the partial control root lacks
  `src/market_manager.py`.
- Inventory proved the split layout: the control root has only selected source
  surfaces while commissioned runtime carries the exact `market_manager.py`
  predecessor.
- Local-apply v2 wrote and identity-checked all targets, then failed because it
  attempted source-suite pytest from the partial control root. Independent audit
  proved exact rollback and no backup residue.
- Local-apply v3 wrote and identity-checked all targets but failed strict memory
  health on an oversized `CURRENT.md`; rollback restored the predecessor.
- Local-apply v4 used a healthy compressed `CURRENT.md` but its installer
  incorrectly required the carrier package ID to appear inside active memory.
  It failed after target identity validation and rolled back. The source
  candidate remains unchanged; v5 removes that invalid carrier-ID coupling.
- Week 3 operational posture remains player HOLD / Lions DST HOLD / Butker K
  HOLD / planning FLEX Mark Andrews. Puka Nacua remains the principal live
  status uncertainty.
- No Week 3 league-wide trade search has been run. Automatic trade search still
  has a known processed-player-values dependency that must be made explicit
  before Week 4 prospective use.
- No observed 2026 outcome has tuned v0.X.

Canonical Phase 1D records:
- `evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`;
- `evidence/PHASE1D_BEHAVIOR_SHADOW_SOURCE_VALIDATION_2026-09-23.md`.

## Calendar / Evidence Gates

- Preserve the Sep 22 week-open and Sep 23 decision-time Week 3 captures.
- A material Puka/Dobbins status change or relevant lineup lock preempts
  nonessential engineering and requires a fresh prospective decision-time state.
- Trade-search readiness before Week 4 is an operational target, not permission
  to tune v0.X or backfill evidence.
- Consequential future trade decisions require their own prospective capture.
- Manager-response probabilities remain explicitly uncalibrated until
  prospective behavior evidence supports calibration.
- Persistent evidence remains separately gated.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Football utility, market perception, and manager behavior remain separate
  response layers.
- Ownership/trend/perception may affect behavior but not intrinsic football
  value.
- `screen != authority`.
- The Phase 1D shadow may observe only the narrow response kernel; mixed trade
  orchestration remains outside this observer.
- Diagnostics must remain non-interfering, fail-open, privacy-preserving, and
  non-persistent unless separately authorized.
- No observed 2026 result may tune v0.X.

## Exact Next Action

Use the generic isolated-staging workflow to stage the exact locally applied
Phase 1D technical + durable-memory checkpoint, regenerate the schema-2 memory
manifest from staged Git blobs, and validate tree/allowlist/health/diff gates.
Stop before commit/push.

After source publication is remote verified, runtime synchronization and
commissioning remain a separate guarded step. Trade-search dependency readiness
should then be resolved before the Week 4 decision window if Week 3 calendar
gates permit.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`
- `evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`
- `evidence/PHASE1D_BEHAVIOR_SHADOW_SOURCE_VALIDATION_2026-09-23.md`
- `../../src/market_manager.py`
- `../../src/observability/behavior_shadow.py`
- `../../src/observability/integration_plan.py`
