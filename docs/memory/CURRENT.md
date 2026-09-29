# Current Project State

---
state_updated: 2026-09-28
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1e_persistence_controller
memory_refinement_step: none
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Finish the Phase 1 measurement apparatus without changing football/model
semantics or activating persistent evidence. Calendar-sensitive prospective
football work still preempts nonessential engineering.

## Current Work Item

**Phase 1E persistence controller: SOURCE CANDIDATE LOCAL-APPLIED /
PERSISTENCE DISABLED.**

The previously commissioned `RedactingJsonlSink` primitive remains unchanged.
The Phase 1E.2 controller candidate has now passed isolated-source preflight and
is installed only on the control-root checkpoint surface.

Validated isolated preflight:

- predecessor: `4833361b045cdc7c7bd97c6fd297560518de8e8b`;
- exact changed scope: 5 paths;
- targeted: `34 passed`;
- observability: `152 passed`;
- full source: `531 passed`;
- `compileall src`: PASS;
- strict memory health: HEALTHY;
- `git diff --check`: PASS;
- `git diff --cached --check`: PASS;
- Git exclusion for `logs/observability/`: PASS;
- temporary-clone cleanup: PASS;
- production persistence active: false.

The controller is observability-owned, explicitly disabled by default, and can
persist only through `RedactingJsonlSink`. It rotates by UTC event day or
16 MiB, stops accepting new writes at a 256 MiB total ceiling, performs no
automatic deletion, and fails open by disabling future persistence after a
disk/redaction/path failure.

This local apply does not alter the commissioned runtime and does not activate
persistent evidence.

## Verified State

- Commissioned runtime remains `v0.36-repack1`, internal `VERSION = 0.36`.
- Phase 1A-1D observability remain source-published and runtime-commissioned.
- Phase 1E redacting persistence primitive remains source-published and
  runtime-commissioned.
- Phase 1E.2 controller source preflight is validated and the candidate is now
  local-applied on the control-root checkpoint surface only.
- Persistent runtime sink remains **DISABLED**.
- No production activation call or local activation policy has been installed.
- No retention deletion is enabled; existing evidence is never deleted by the
  controller.
- No football/model/manager-behavior formula or recommendation authority changed.
- `P ⊕ D ⊕ K`, `screen != authority`, and football/behavior separation remain
  unchanged.
- Last frozen Week 3 football evidence remains preserved. Sep 24 operational
  state is historical evidence, not current decision-time authority for a new
  consequential action.
- No observed 2026 outcome has tuned v0.X.

Canonical validation:
`evidence/PHASE1E_PERSISTENCE_CONTROLLER_SOURCE_VALIDATION_2026-09-28.md`.

## Calendar / Evidence Gates

- Preserve the existing Week 3 frozen captures and closure lineage.
- Any new consequential lineup/transaction decision requires a fresh
  decision-time sync/capture; do not reuse the Sep 24 state as current.
- A material consequential football status/lock gate preempts nonessential
  engineering.
- Phase 2 prospective Data/MC collection continues independently of Phase 1E;
  persistent telemetry cannot be backfilled for earlier weeks.
- Persistent evidence activation remains a separate explicit authorization and
  commissioning gate.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Football utility, market perception, and manager behavior remain separate.
- `screen != authority`.
- Diagnostics observe; they do not become decision/control logic.
- Persistence may retain only redacted observability events.
- Raw authenticated/private evidence remains local and outside Git.
- No observed 2026 result may tune v0.X without the v1 evidence/calibration gate.

## Exact Next Action

After verifying this local-apply receipt, prepare the normal declarative isolated
stage with `tools/delivery/prepare_checkpoint_stage.py` for the reviewed
nine-path checkpoint plus regenerated `docs/memory/manifest.json`.

Then:

1. validate the staged tree/manifest/allowlist and zero residue;
2. publish through the separate guarded `.ffpkg` publication boundary;
3. verify remote `main` read-only;
4. only after source publication, commission the controller into
   `v0.36-repack1` with persistence still **OFF**;
5. treat persistent activation as a later, separately authorized gate.

Do not activate persistence during source publication or runtime synchronization.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `patches/PATCH_PROTOCOL.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `evidence/PHASE1E_REDACTING_PERSISTENCE_PRIMITIVE_PREFLIGHT_2026-09-24.md`
- `evidence/PHASE1E_REDACTING_PERSISTENCE_PRIMITIVE_RUNTIME_COMMISSIONING_2026-09-27.md`
- `evidence/PHASE1E_PERSISTENCE_CONTROLLER_SOURCE_VALIDATION_2026-09-28.md`
- `../../docs/ROADMAP.md`
- `../../src/observability/persistence.py`
- `../../src/observability/shadow_pilot.py`
- `../../src/observability/gui_shadow.py`
