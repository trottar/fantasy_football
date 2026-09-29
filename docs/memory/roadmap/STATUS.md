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
  **SOURCE PREFLIGHT VALIDATED / LOCAL-APPLIED / NOT YET PUBLISHED**
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

### 1E.2 — persistence controller

**SOURCE PREFLIGHT VALIDATED / LOCAL-APPLIED / PERSISTENCE DISABLED**

The accepted controller candidate is observability-owned and adds no football,
market, manager-behavior, Monte Carlo, or recommendation authority.

Contract:

- fixed runtime-local root: `logs/observability/`;
- source default: disabled;
- activation requires explicit `configure_shadow_persistence(...)`;
- persistence path uses only `RedactingJsonlSink`;
- segment rotation: UTC event day or 16 MiB;
- total storage ceiling: 256 MiB;
- no automatic retention deletion;
- at the storage ceiling, stop new persistence and preserve existing evidence;
- disk/redaction/path failures fail open and disable later writes for that
  controller instance;
- in-memory shadow observation remains primary and continues if disk persistence
  fails;
- recorder wiring is shared beneath `ShadowRecorder` and `GuiShadowRecorder`
  rather than duplicated across P/D/K/behavior boundaries.

Validated isolated-source receipt:

- base commit:
  `4833361b045cdc7c7bd97c6fd297560518de8e8b`;
- changed paths: `5/EXACT`;
- targeted: `34 passed in 6.74s`;
- observability: `152 passed in 5.12s`;
- full source: `531 passed in 48.21s`;
- `compileall`: PASS;
- strict memory health: HEALTHY;
- both Git diff checks: PASS;
- Git exclusion: PASS;
- persistence active: false;
- project/runtime modified by preflight: false;
- cleanup: PASS.

Canonical evidence:
`../evidence/PHASE1E_PERSISTENCE_CONTROLLER_SOURCE_VALIDATION_2026-09-28.md`.

### 1E.3 — source publication and runtime commissioning

**PENDING**

After local checkpoint verification:

1. declarative isolated staging;
2. guarded source publication;
3. remote read-only verification;
4. separate synchronization into `v0.36-repack1`;
5. runtime validation with persistence still disabled.

Source capability, runtime synchronization, and activation are distinct
authorities.

### 1E.4 — persistent activation

**SEPARATELY GATED / NOT AUTHORIZED**

Activation must prove the exact Git-excluded local path, real redacted bytes on
disk, privacy invariants, rotation behavior, disk-failure fail-open semantics,
and no football/model/behavior change.

Phase 1 is not complete until persistent local evidence is explicitly authorized
and commissioned.

## Relationship to Phase 2

Phase 2 prospective `MC -> Data -> closure` collection is already active and
does not wait for Phase 1E. Persistent observability evidence begins only when it
is actually commissioned and activated; earlier weeks must not be backfilled as
if telemetry had existed prospectively.

Weeks 3-5 remain the primary clean early review window. The first formal
multi-week diagnosis/calibration review is still evidence-gated rather than
calendar-forced.

## Football / Calendar Gate

Existing Week 3 frozen captures remain immutable. The Sep 24 operational state is
historical evidence and is not valid as a new decision-time state.

Any consequential new lineup, waiver, trade, or specialist action requires a
fresh prospective sync/capture. A material football lock/status gate preempts
nonessential engineering.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from market perception and manager behavior.
- `screen != authority`.
- Persistent evidence requires separate authorization and commissioning.
- Raw authenticated/private evidence remains local.
- No observed 2026 outcome may tune v0.X.
