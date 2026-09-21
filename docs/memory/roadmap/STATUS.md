# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- 2026 season-roadmap memory checkpoint: **PUSHED / REMOTE VERIFIED** at
  `8592989b78b6e94cd08d8618694b8168c62cf715`
- Active development series: **v1.0A observability**
- Active technical checkpoint: **data-source season-sync shadow pilot**
- Current pilot state: **staging preflight validated; schema-2 manifest preflight
  passed; not committed**
- Commissioned runtime tree: **UNCHANGED**
- Persistent runtime sink: **DISABLED**
- Broad football-channel instrumentation: **DEFERRED / SEPARATELY GATED**

## Active Data-Source Pilot

The candidate observes only the outer
`src/season_snapshot.py::sync_season_snapshot` boundary.

Candidate validation:

- targeted pytest: **39 passed in 7.37 s**;
- deterministic paired privacy/non-interference probe: PASS;
- full pytest: **459 passed in 52.73 s**;
- compileall: PASS;
- candidate diff-check: PASS;
- exact candidate 14-path allowlist: PASS.

Staging preflight:

- fresh staging clone at exact remote predecessor: PASS;
- four technical files byte-identical to validated candidate: PASS;
- exact 10-path latest control-root memory inventory/copy/byte identity: PASS;
- combined exact 14-path working-tree allowlist: PASS;
- strict memory health: HEALTHY;
- combined diff-check: PASS;
- exact 14-path staging with no residue: PASS;
- schema-2 manifest regenerated from staged Git blob bytes: PASS;
- manifest entry count: **100**;
- exact staged path count including manifest: **15**;
- exact 15-path staged allowlist / no residue / cached diff-check: PASS.

The manifest is still a **preflight** because the v4 memory checkpoint itself
advances control-root memory. Final pre-commit staging must refresh those v4
memory files and regenerate/validate the manifest again. No further recursive
memory bookkeeping update is required before commit.

## Remaining v1.0A Work

After this checkpoint:

1. final refresh + schema-2 manifest regeneration in staging clone;
2. repository commit/push/read-only remote verification;
3. separate commissioned-runtime synchronization/validation;
4. later separately gated closure / P / D / K / market / persistence work.

## 2026 Season Milestones

- Week 3: first future hard prospective-capture gate.
- Week 5: preferred v1.0 observability commissioning target / first bye-week
  operational stress.
- After Week 5: first formal three-clean-week closure review.
- Before Week 9: commission only evidence-supported calibration; otherwise defer.
- Weeks 12-13: playoff-readiness/model-freeze preparation.
- Before Week 14: playoff production baseline commissioned.
- Weeks 14-17: production-first; major empirical calibration frozen by default.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- No observed 2026 outcome may retroactively tune a v0.X model.
- Diagnostics remain observers, not decision/control logic.
- Data-source instrumentation must preserve authenticated-data privacy.
- Missed prospective captures are recorded as missing, never backfilled.

## Canonical References

- Long-range roadmap: `../../ROADMAP.md`
- 2026 weekly map: `SEASON_2026.md`
- D-024: `../decisions/D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`
- Current evidence:
  `../evidence/V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT_PREFLIGHT_2026-09-21.md`
- Detailed chronology: `../memory/2026-09-21.md`
