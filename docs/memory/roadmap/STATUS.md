# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow:
  **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure observability:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C P/D/K observability:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1D market/manager-behavior observability:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1E redacting persistence primitive:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1E persistence controller:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E persistent activation:
  **SEPARATELY GATED / NOT AUTHORIZED**
- Persistent runtime evidence: **DISABLED**
- Phase 2 prospective Data/MC collection: **ACTIVE / CONCURRENT**
- No observed 2026 outcome has tuned v0.X.

## Phase 1E — Measurement-Apparatus Closure

Phase 1E is the final commissioning gate for the Phase 1 measurement apparatus,
not an independent logging feature.

### 1E.1 — mandatory-redaction primitive

**COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**

`src/observability/sinks.py::RedactingJsonlSink` applies redaction before bytes
reach disk. The raw `JsonlSink` remains unchanged and is not an authorized
production persistence path.

Canonical evidence:

- `../evidence/PHASE1E_REDACTING_PERSISTENCE_PRIMITIVE_PREFLIGHT_2026-09-24.md`
- `../evidence/PHASE1E_REDACTING_PERSISTENCE_PRIMITIVE_RUNTIME_COMMISSIONING_2026-09-27.md`

### 1E.2 — persistence controller source

**COMPLETE / SOURCE PUBLISHED / REMOTE VERIFIED**

The accepted controller is observability-owned and adds no football, market,
manager-behavior, Monte Carlo, or recommendation authority.

Contract:

- fixed runtime-local root: `logs/observability/`;
- source default: disabled;
- activation requires explicit `configure_shadow_persistence(...)`;
- persistence path uses only `RedactingJsonlSink`;
- segment rotation: UTC event day or 16 MiB;
- total storage ceiling: 256 MiB;
- no automatic retention deletion;
- at the storage ceiling, stop new persistence and preserve existing evidence;
- disk/redaction/path failures fail open and disable later writes;
- in-memory observation continues if disk persistence fails.

Published checkpoint:
`444900861d07e6ba910d81ce2d147d96e98d2d93`.

Canonical source evidence:
`../evidence/PHASE1E_PERSISTENCE_CONTROLLER_SOURCE_VALIDATION_2026-09-28.md`.

### 1E.3 — runtime commissioning with persistence off

**COMPLETE / RUNTIME COMMISSIONED / PERSISTENCE DISABLED**

Commissioned runtime:
`L:\Projects\fantasy_football\fantasy_season_v0_36_repack1`.

Accepted v4 receipt:

- production identities: `4/4`;
- temporary validation-test identities: `7/7`;
- dedicated controller: `9 passed`;
- targeted privacy/persistence/recorder: `51 passed`;
- full runtime: `404 passed`;
- `compileall`: PASS;
- temporary tests restored: true;
- runtime residue: NONE;
- rollback: false;
- persistence state:
  `enabled=False; failed=False; failures=0; active_path=None`.

Three earlier packages were pre-mutation harness failures and are superseded:
control-root remote assumption, raw-vs-normalized Git identity comparison, and one
incorrect deterministic SHA-256 literal.

Canonical runtime evidence:
`../evidence/PHASE1E_PERSISTENCE_CONTROLLER_RUNTIME_COMMISSIONING_2026-09-29.md`.

### 1E.4 — persistent activation

**SEPARATELY GATED / NOT AUTHORIZED**

Activation must prove the exact Git-excluded local path, real redacted bytes on
disk, privacy invariants, rotation/storage-cap behavior, disk-failure fail-open
semantics, and no football/model/behavior change.

Phase 1 remains open until persistent local evidence is explicitly authorized
and commissioned.

## Relationship to Phase 2

Phase 2 prospective `MC -> Data -> closure` collection is active and does not
wait for Phase 1E activation. Persistent observability evidence begins only when
it is actually commissioned and activated; earlier weeks must not be backfilled
as if telemetry had existed prospectively.

Week 4 prospective decisions require fresh decision-time state. The first formal
multi-week diagnosis/calibration review remains evidence-gated.

## Football / Calendar Gate

Existing frozen captures remain immutable. Sep 24 operational state is historical
evidence and is not valid as a new decision-time state.

Any consequential new lineup, waiver, trade, or specialist action requires a
fresh prospective sync/capture. A material football lock/status gate preempts
nonessential engineering.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from market perception and manager behavior.
- `screen != authority`.
- Persistent activation requires separate authorization and commissioning.
- Raw authenticated/private evidence remains local.
- No observed 2026 outcome may tune v0.X.
