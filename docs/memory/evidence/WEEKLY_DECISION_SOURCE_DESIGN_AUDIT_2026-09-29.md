# Weekly Decision Source / Design Audit — 2026-09-29

---
evidence_type: read_only_source_design_audit
source_checkpoint: c21bfce9a5dd94f9269b7749ea10ea916d7c91e3
production_source_write: false
runtime_write: false
football_model_tuning: false
---

## Scope

Read-only audit of the exact production entry points that must satisfy the
published Weekly Decision Completion Contract.

## Exact Source Identities

- `fantasy.py` Git blob:
  `2f2c10cd67c96afe74a84cbf7a36a70342ec5c99`
- `src/market_manager.py`:
  `b384776b7bf1338af778a1ef146700755d87b340`
- `src/transaction_manager.py`:
  `4f800454408851d179e35c5dd462fb8f5ecb675c`
- `src/weekly_manager.py`:
  `15a2f734b8b379fe54fac885c756c6dd7dec7398`
- `src/specialist_policy_v032.py`:
  `38ba984b599ac1a642bb8ff1da774a12e71ed2f3`
- `src/prospective_measurement_v034.py`:
  `a1cafdec30458af1e0d9a285e08b7a8a5a90cd8a`
- `src/observability/persistence.py`:
  `02a2a11c1cd320d713c934fc1f6a90ac00772420`
- `src/gui/season_service.py`:
  `733d32d7a8a62cf3dc9e88163971d0bd285edf87`
- `src/data_sources/espn_league.py`:
  `24f1ce8ce6b2c8e8dc47b387e7d827ec63c1c907`
- `tools/check_memory_health.py`:
  `077d8da7858cc7f9fd17c94d0cf13ee19f7a0d62`
- `config/league.json`:
  `a2d8ffac5f814fbc16267975caf8b1b68865043a`

## Findings

### No completion orchestrator

CLI and GUI/service expose the required operations independently. There is no
shared receipt inventory or state machine that prevents a subset from being
mistaken for a complete weekly cycle.

### Player action authority is reusable

The player action engine already owns broad candidate/drop enumeration, predictive
MC, waiver claim behavior, and released-player league response.

### Specialist authority is reusable but current-waiver coverage is incomplete

The commissioned specialist policy performs same-channel dynamic policy plus
complete-state confirmation. Its initial dynamic pool contains current
FREEAGENTs and explicitly excludes current WAIVERS.

### Trade search is narrower than evaluator capability

The player evaluator permits up to the configured two assets per side and
supports unequal packages with modeled legal release/fill behavior.

Automated search enumerates only one-for-one player offers.

The evaluator rejects DST/K assets.

### IR facts are already captured

ESPN normalization stores slot 21 as `IR`, preserves each roster player's current
`lineup_slot_id` and `eligible_slots`, and records team move-to-IR counters.

League config has one IR slot.

### Multiweek injury state is incomplete

Current-week availability uses explicit evidence/timing states. Future weeks
retain the commissioned generic availability approximation pending separate
forecast calibration, so decision-time known absence duration is not an explicit
future roster-state input.

### Health primitives are fragmented

Provider health, prospective capture integrity, persistence state, runtime
version/dependency identity, and structural memory health all exist separately.

No unified weekly operational-health receipt binds them to decision completion.

## Classification

`READ_ONLY_SOURCE_DESIGN_AUDIT_COMPLETE`

The root defect remains structural orchestration/operability, not football-model
calibration.

## Next Boundary

Make this audit/design durable.

Then stop for explicit user authorization before modifying production source.
