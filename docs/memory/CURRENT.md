# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: week3_prospective_capture
memory_refinement_step: M0_M7_complete_durable
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Preserve the first future causally valid Week 3 week-open state before the Sep 24
first game using the commissioned baseline and only decision-time information.

The irreversible prospective-capture deadline outranks Phase 1B or other
nonessential development.

## Current Work Item

**Week 3 week-open prospective capture: ACTIVE HARD CALENDAR GATE.**

M7 fresh-session integration evidence is durable on remote `main` at
`b49104b84e34d3169d1b4876a3e1748e6553800a`, so the M0-M7 memory-system
refinement is **COMPLETE / DURABLE**.

Canonical durability evidence:
`evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`.

## Verified State

- `v0.36-repack1` remains the commissioned 0.X runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow is **COMPLETE / RUNTIME COMMISSIONED**.
- Generic `.ffpkg` delivery and declarative staging infrastructure are **PUSHED /
  REMOTE VERIFIED**.
- M0-M7 memory-system refinement is **COMPLETE / DURABLE**.
- The retained Phase 1B closure-shadow candidate remains **PREFLIGHT VALIDATED /
  NOT APPLIED**. Do not rerun established candidate gates without new evidence.
- Persistent runtime evidence remains **DISABLED**.
- This durability transition changes no football/model/application semantics and
  does not touch the commissioned runtime.

## Calendar / Evidence Gates

- Weeks 1/2 count as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 (Sep 24-28) is the first future hard prospective-capture gate.
- Freeze the Week 3 week-open state before the first game using the commissioned
  baseline and decision-time information available at capture.
- A valid Week 3 capture outranks Phase 1B and any nonessential development.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from intrinsic football utility.
- `screen != authority`.
- Only decision-time information may influence prospective actions.
- `0.X` remains a-priori; observed 2026 outcomes may tune only `1.X`.
- Observability remains non-interfering and non-authoritative.

## Exact Next Action

Prepare and execute the Week 3 week-open prospective-capture package against the
commissioned `v0.36-repack1` runtime before the Sep 24 first game.

The capture must use the current decision-time state, preserve authenticated/raw
runtime data locally, keep persistent observability disabled, produce immutable
prospective evidence with provenance/integrity, and return only a sanitized
validation summary for classification.

Do not resume or checkpoint Phase 1B until the Week 3 capture is secured.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `MAINTENANCE.md`
- `README.md`
- `evidence/MEMORY_M7_FRESH_SESSION_INTEGRATION_AUDIT_2026-09-22.md`
- `evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `../../ROADMAP.md`
- `../../KNOWN_ISSUES.md`
- `patches/PATCH_PROTOCOL.md`
