# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Active development series: **v1.0A observability**
- Current repository gate: **2026 season-roadmap durable-memory checkpoint**
- Latest completed technical slice: **GUI background-task/lifecycle shadow pilot**
- Exact next technical slice after the repository gate:
  **data-source season-sync shadow pilot**
- Persistent runtime sink: **DISABLED**
- Broad football-channel instrumentation: **DEFERRED / SEPARATELY GATED**

## Accepted Long-Range Plan

`docs/ROADMAP.md` owns the accepted multi-phase project plan.

`roadmap/SEASON_2026.md` owns the week-by-week 2026 calendar/deadline map.

The roadmap now separates:

- **calendar gates** — irreversible prospective capture / operational deadlines;
- **evidence gates** — scientific review/calibration gates that pass only when
  prospective closure supports them.

A date never forces an evidence gate to pass.

## v1.0A — Evidence / Diagnostics / Observability Substrate

Completed:

- [x] architecture/contract adopted
- [x] immutable run/action context
- [x] structured event schema/registry
- [x] human + machine sinks
- [x] provenance/config/input hashing
- [x] invariant registry/results
- [x] privacy/redaction primitives
- [x] local snapshot bundle contract
- [x] exact-byte replay verification/loading
- [x] bounded structural diff contract
- [x] bounded privacy-safe failure-bundle contract
- [x] subsystem adapter contracts
- [x] CLI/service/background-task correlation contracts
- [x] P/D/K observability channel separation guard
- [x] production integration surface map
- [x] paired result/exception/RNG/state non-interference gate
- [x] absolute/relative overhead budget contract
- [x] final CLI dispatch shadow pilot
- [x] read-only `SeasonGuiService.source_health()` shadow pilot
- [x] GUI selected-MC/progress-pump lifecycle shadow pilot
- [x] page/connect/disconnect/delete correlation
- [x] bounded in-memory / non-persistent evidence

Repository checkpoint gate:

- The **2026 season-roadmap durable-memory checkpoint** is satisfied when this
  roadmap content is committed on `main`, the push succeeds without remote
  movement, and the resulting remote SHA is verified read-only.
- Until that condition is established, technical implementation remains gated.

Exact next technical checkpoint after that gate:

- [ ] **data-source season-sync shadow pilot**

Later v1.0A work, separately gated:

- [ ] closure instrumentation
- [ ] player channel instrumentation
- [ ] DST channel instrumentation
- [ ] kicker channel instrumentation
- [ ] market/manager-behavior instrumentation
- [ ] persistent runtime sink authorization/commissioning
- [ ] v1.0A commissioning gate

## 2026 Season Milestones

- Week 3: first future hard prospective-capture gate under the new roadmap.
- Week 5: preferred v1.0 observability commissioning target / first bye-week
  operational stress.
- After Week 5: first formal three-clean-week closure review.
- Before Week 9: commission only evidence-supported early calibration; otherwise
  explicitly defer.
- Weeks 12-13: playoff-readiness and model-freeze preparation.
- Before Week 14: playoff production baseline commissioned.
- Weeks 14-17: production-first; major empirical calibration frozen by default.
- Week 18 / postseason: complete full-season closure and open broader v2 research.

Exact dates, byes, artifacts, and deadline classes are in `SEASON_2026.md`.

## Scientific Sequence

Use:

`observe -> measure -> diagnose -> calibrate -> expand`

and:

`MC -> Data -> closure -> diagnosis -> calibration`

Observability is the experimental measurement apparatus supporting prospective
model evolution.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- No observed 2026 outcome may retroactively tune a v0.X prospective model.
- Diagnostics remain observers, not decision/control logic.
- Data-source instrumentation must preserve authenticated-data privacy.
- Broad football/model instrumentation remains separately authorized.
- Historical evidence enters as contextual prior information, not direct truth.
- Missed prospective captures are recorded as missing, never backfilled.
- Calendar gates protect capture/operations; evidence gates authorize calibration.
- Playoff production is frozen by default against broad empirical retuning.

## Canonical References

- Long-range roadmap: `../../ROADMAP.md`
- 2026 weekly map: `SEASON_2026.md`
- Open/deferred issues: `../../KNOWN_ISSUES.md`
- v1.X context: `../architecture/PHASE_V1_CONTEXT.md`
- D-023: `../decisions/D-023_2026_SEASON_GATED_ROADMAP.md`
- Canonical evidence/decisions: `../evidence/`, `../decisions/`
- Detailed chronology: `../memory/2026-09-20.md`
