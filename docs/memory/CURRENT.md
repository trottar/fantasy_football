# Current Project State

---
state_updated: 2026-09-22
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: phase1b_closure_instrumentation
memory_refinement_step: M0_M7_complete_durable
nfl_week: 3
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Checkpoint the fresh Phase 1B closure-shadow source candidate after independent
validation of its new byte identity.

The retained pre-recovery candidate remains historical only and does not
authorize these reconstructed bytes.

## Current Work Item

**Phase 1B closure instrumentation: SOURCE VALIDATED / CONTROL-ROOT APPLIED /
CHECKPOINT PENDING.**

The Week 3 week-open prospective capture remains
**SECURED / VALID / PRE-KICKOFF**.

Canonical Phase 1B source-validation evidence:
`evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

## Verified State

- `v0.36-repack1` remains the commissioned 0.X runtime baseline with internal
  `VERSION = 0.36`.
- Phase 1A data-source season-sync shadow remains
  **COMPLETE / RUNTIME COMMISSIONED**.
- M0-M7 memory-system refinement remains **COMPLETE / DURABLE**.
- Week 3 week-open capture remains **PROSPECTIVE_WEEK_OPEN_CAPTURE_VALID**.
- Persistent runtime evidence remains **DISABLED**.
- The lost Phase 1B retained candidate remains historical-only evidence.
- Fresh Phase 1B v2 reconstructs the intended closure observer as exactly four
  technical paths:
  - `src/closure.py`
  - `src/observability/closure_shadow.py`
  - `tests/test_observability_closure_shadow_v10a.py`
  - `tools/probe_observability_closure_shadow_v10a.py`
- The observer instruments only the final v0.34
  `build_pregame_capture_from_context` override. The pre-v0.34 definition and
  `_build_pregame_capture_from_context_pre_v034` alias remain uninstrumented.
- Commissioned `src/observability/shadow_pilot.py` is unchanged.
- The v2 package's first local validation attempt failed after writing only the
  isolated candidate because Git stderr containing a CRLF warning was merged into
  stdout and misclassified as an extra changed path.
- The v3 continuation verified the retained v2 bytes exactly and fixed only the
  validator's stdout/stderr interpretation; it made no candidate-source changes.
- Targeted gate: **33 passed in 1.94 s**.
- Paired probe: outputs equal, exception behavior equal, state equal, success/error
  privacy PASS, Python RNG preserved.
- Paired timing measurement: baseline median `6100 ns`, observed median
  `70100 ns`, incremental `64000 ns`. The reported relative fraction
  `10.491803278688524` is not the active overhead criterion because the baseline
  is below the configured `50,000,000 ns` relative floor; the `64,000 ns`
  increment passes the `2,000,000 ns` absolute budget.
- Full source gate: **491 passed in 51.83 s**.
- Full `compileall`: **PASS**.
- `git diff --check`: **PASS**.
- Exact validated source SHA-256:
  - `src/closure.py`:
    `c3c1633e5b8843b15a450f0ad8cf38f4797856d4128c5d7a4b00f99012a886c6`
  - `src/observability/closure_shadow.py`:
    `bd6182bdea76de1353468d37969b49b48d0d4d78363d61e626cee46d4c1aa1a2`
  - `tests/test_observability_closure_shadow_v10a.py`:
    `7ae368b713d62b266c0037da0c49e9dffd62c3c668a54c84bb702b1b73a57056`
  - `tools/probe_observability_closure_shadow_v10a.py`:
    `be7f7f13014339896a2177cd73d81e0ee5c9c758ae95250fb1d87599ced49eab`
- Those exact four validated bytes are now synchronized to the control-root
  checkpoint surface.
- The commissioned runtime remains untouched; Phase 1B is **NOT COMMISSIONED**.
- Staging, commit, and push for this Phase 1B source checkpoint have not yet been
  performed.

## Calendar / Evidence Gates

- Weeks 1/2 count as prospective evidence only where a genuine frozen capture
  already exists; never backfill.
- Week 3 week-open capture gate is **SECURED**.
- Preserve separate decision-time captures for consequential Week 3 actions.
- Broad empirical calibration remains blocked until sufficient clean prospective
  closure evidence exists.
- Week 5 remains the preferred broader v1.0 observability commissioning target.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from intrinsic football utility.
- `screen != authority`.
- Only decision-time information may influence prospective actions.
- `0.X` remains a-priori; observed 2026 outcomes may tune only `1.X`.
- Observability remains non-interfering and non-authoritative.
- Authenticated/raw capture material remains local.
- Do not transfer validation claims between different candidate byte identities.
- Phase 1B changes closure observability only; it does not change football,
  scoring, MC, P/D/K, manager behavior, or recommendation authority.

## Exact Next Action

Stage the exact four validated Phase 1B technical files together with this
checkpoint's durable-memory updates in a fresh isolated staging clone based on
remote-verified predecessor
`724e87089cd7fe06f884d5d74c944df05622a532`.

Regenerate and validate the schema-2 durable-memory manifest from staged Git blob
bytes, verify the exact reviewed allowlist/tree, then publish through the
established staged-checkpoint helper.

Do not synchronize the commissioned runtime until the source checkpoint is
pushed and remotely verified. Runtime synchronization/commissioning remains a
separate gate.

## Relevant References

- `AGENTS.md`
- `MEMORY.md`
- `handoffs/CURRENT_HANDOFF.md`
- `USER.md`
- `evidence/PHASE1B_RECOVERY_FAILURE_LINEAGE_2026-09-22.md`
- `evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `evidence/WEEK3_WEEK_OPEN_PROSPECTIVE_CAPTURE_2026-09-22.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`
- `roadmap/STATUS.md`
- `roadmap/SEASON_2026.md`
- `patches/PATCH_PROTOCOL.md`
