# Current Project State

---
state_updated: 2026-09-21
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: v1.0A_observability
active_workstream: data_source_season_sync_shadow_pilot
nfl_week: 2
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Complete the v1.0A data-source season-sync shadow pilot through repository
checkpoint and separate runtime synchronization while preserving authenticated-
data privacy, production behavior, random state, and the commissioned
`v0.36-repack1` runtime.

## Verified State

- `v0.36-repack1` remains **COMMISSIONED** and runtime-unchanged.
- Last remote-verified repository checkpoint:
  `8592989b78b6e94cd08d8618694b8168c62cf715`.
- Active integration point:
  `src/season_snapshot.py::sync_season_snapshot` /
  `subsystem.data_source.season_sync`.
- Persistent runtime sink remains disabled.
- Provider internals remain uninstrumented.

## Candidate Validation

The retained source candidate has passed:

- exact predecessor/source patch guards;
- targeted observability pytest: **39 passed in 7.37 s**;
- corrected deterministic paired probe: **PASS**;
- outputs, exception behavior/type, Python RNG, and snapshot-tree state equal;
- privacy checks: PASS; no arguments, return values, returned paths, or exception
  messages captured; no persistent sink;
- probe baseline median **1,123,700 ns**, observed **1,296,200 ns**,
  incremental **172,500 ns**, relative fraction **0.15351072350271425**;
- full repository pytest: **459 passed in 52.73 s**;
- full repository compileall: **PASS**;
- candidate `git diff --check`: PASS;
- exact 14-path candidate allowlist after removal of temporary probe JSON.

## Staging / Manifest Preflight

A fresh isolated staging clone was created at the same remote checkpoint and
validated incrementally:

- staging-clone `HEAD` exactly
  `8592989b78b6e94cd08d8618694b8168c62cf715`;
- four technical files copied from the retained candidate and confirmed
  byte-identical;
- current control-root memory delta measured as exactly 10 paths, then copied;
- all 10 memory files confirmed byte-identical to the control root;
- combined working tree: exact 14-path allowlist;
- strict memory health: **HEALTHY**;
- combined `git diff --check`: PASS;
- exact 14 paths staged with no unstaged/untracked residue;
- schema-2 `docs/memory/manifest.json` regenerated from staged Git blob bytes;
- manifest entries: **100**;
- staged path count including manifest: **15**;
- exact 15-path staged allowlist: PASS;
- no unstaged/untracked residue: PASS;
- cached diff check: PASS.

This manifest result is a **preflight**, not yet the commit-ready final manifest,
because this v4 memory checkpoint advances control-root memory after that
measurement. Before commit, refresh these updated memory files into the staging
clone and regenerate/validate the manifest once more from the resulting staged
Git blobs. Do not create another recursive pre-commit memory bookkeeping update.

## Failure Lineage

- package v1: **FAILED BEFORE MODIFICATION** because it confused control root
  with application source;
- package v2: **FAILED BEFORE CONTROL-ROOT MODIFICATION** because its probe
  launcher omitted the repository root from `PYTHONPATH`;
- manual probe retry under the correct import context passed.

Canonical detail:
`evidence/V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT_PREFLIGHT_2026-09-21.md`.

## Scientific / Architectural Boundaries

- Preserve `P ⊕ D ⊕ K`; this slice touches none of those channels.
- Manager behavior and closure remain separately gated.
- No observed 2026 outcome tunes a v0.X model.
- Diagnostics remain observers; no provider/return/filesystem/RNG semantics may
  change.
- No authenticated/provider payload, secret, returned snapshot/path, or exception
  message may enter observability evidence.
- Week 3 remains the first future hard prospective-capture gate.

## Current Validation State

`STAGING PREFLIGHT VALIDATED / SCHEMA-2 MANIFEST PREFLIGHT PASS / 15 PATHS STAGED / NOT COMMITTED / RUNTIME UNCHANGED`

## Exact Next Action

Apply this memory-only v4 checkpoint to the control root. Then refresh only the
v4-updated memory files into the existing staging clone, re-stage those paths,
regenerate `docs/memory/manifest.json` from staged Git blob bytes, and rerun the
exact staged-allowlist/residue/cached-diff checks. Do **not** commit or push in
that refresh step.

## Repository / Handoff Boundary

Repository writes remain:

`assistant package -> user local run -> returned log -> assistant verification -> separate push commands -> user push -> read-only remote verification`

No direct GitHub connector writes are used for checkpoints.

## Success Criterion

The pilot is complete only after repository commit/push/read-only remote
verification and a later, separate synchronization/validation against the
commissioned runtime tree.

## Relevant References

- `decisions/D-020_V10A_INTEGRATION_GATE.md`
- `decisions/D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`
- `architecture/DIAGNOSTICS_OBSERVABILITY.md`
- `roadmap/STATUS.md`
- `patches/PATCH_PROTOCOL.md`
- `evidence/V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT_PREFLIGHT_2026-09-21.md`
- `memory/2026-09-21.md`
