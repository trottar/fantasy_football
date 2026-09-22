# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Phase M repository/season-roadmap authority transition: **COMPLETE / PUSHED /
  REMOTE VERIFIED**
- Active engineering series: **v1.0A observability**
- Generic `.ffpkg` delivery + declarative staging infrastructure: **PUSHED /
  REMOTE VERIFIED**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Memory-system refinement: **M0-M7 COMPLETE / DURABLE**
- Week 3 week-open capture: **SECURED / VALID / PRE-KICKOFF**
- Phase 1B closure instrumentation: **SOURCE VALIDATED / CONTROL-ROOT APPLIED /
  CHECKPOINT PENDING**
- Phase 1C player/DST/kicker observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**

## Memory-System Refinement

- M0 — read-only audit: **COMPLETE / DURABLE**
- M1 — active/planning reconciliation: **COMPLETE / DURABLE**
- M2 — checkpoint identity semantics: **COMPLETE / DURABLE**
- M3A — procedure ownership / delivery wording cleanup: **COMPLETE / DURABLE**
- M3B — curated `MEMORY.md` cleanup: **COMPLETE / DURABLE**
- M4 — handoff contract: **COMPLETE / DURABLE**
- M4R1 — maintenance newline repair: **COMPLETE / DURABLE**
- M5 — startup contract decision: **COMPLETE / DURABLE**
- M6 — memory-health enforcement: **COMPLETE / DURABLE**
- M7 — fresh-session integration audit: **COMPLETE / DURABLE**

The memory-refinement series is closed.

Canonical durability evidence:
`../evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`.

## Week 3 Prospective Capture

The first future hard Week 3 capture gate is secured.

Classification:
`PROSPECTIVE_WEEK_OPEN_CAPTURE_VALID`.

- captured UTC: `2026-09-22T14:10:53.254794Z`;
- snapshot UTC: `2026-09-22T14:10:51.714616Z`;
- deadline UTC: `2026-09-25T00:15:00Z`;
- runtime/model version: `0.36`;
- measurement contract: `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- capture integrity: **PASS**;
- pre-data firewall: **PASS**;
- source groups: ESPN, Sleeper, nflverse rosters, nflverse matchups, NFL.com
  team rosters, and NFL.com status — **ALL OK**;
- degraded sources: **NONE**;
- capture remained local/private; repository write: false; runtime source write:
  false; persistent runtime sink: false.

Canonical sanitized evidence:
`../evidence/WEEK3_WEEK_OPEN_PROSPECTIVE_CAPTURE_2026-09-22.md`.

Continue to preserve separate decision-time captures for consequential Week 3
lineup, transaction, and specialist actions.

## Phase 1A — Commissioned Result

The outer `sync_season_snapshot` observability boundary is commissioned with
privacy/non-interference and runtime validation complete. Production football
semantics remain unchanged and the persistent sink remains disabled.

Canonical evidence:
`../evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`.

## Phase 1B — Source Validated / Checkpoint Pending

The lost historical candidate was not reused.

Fresh v2 reconstructs Phase 1B as exactly four technical paths and instruments
only the final v0.34 closure-capture override. The commissioned shared
`shadow_pilot.py` remains unchanged.

Validation for this exact byte identity:

- structural final-v0.34 boundary: PASS;
- targeted pytest: **33 passed in 1.94 s**;
- paired output/exception/state/privacy/RNG gate: PASS;
- median incremental observer cost: **64,000 ns**;
- absolute overhead budget: **PASS**;
- full pytest: **491 passed in 51.83 s**;
- full compileall: PASS;
- `git diff --check`: PASS;
- post-validation exact-byte/four-path identity: PASS.

The measured relative timing fraction was `10.491803278688524`, but the baseline
median was only `6100 ns`, below the configured `50,000,000 ns` relative floor.
Under the declared `OverheadBudget`, the absolute `64,000 ns` increment is the
active criterion and is below the `2,000,000 ns` limit.

A v2 validation attempt failed before tests because the package incorrectly
merged a benign Git CRLF warning from stderr into stdout path enumeration. The v3
continuation separated stdout/stderr, verified the retained bytes exactly, and
continued without changing candidate source.

Current classification:

`PHASE 1B SOURCE VALIDATED / CONTROL-ROOT APPLIED / NOT YET STAGED OR COMMISSIONED`

Canonical source-validation evidence:
`../evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`.

Phase 1B still does not authorize P/D/K instrumentation, manager-behavior
instrumentation, persistent evidence, or football-model changes.

## 2026 Season Milestones

- Week 3 (Sep 24-28): week-open prospective capture **SECURED**; preserve
  decision-time captures for consequential actions.
- Week 5: preferred broader v1.0 observability commissioning target / first bye
  stress.
- After Week 5: first formal three-clean-week prospective closure review, if the
  captures are valid.
- Before Week 9: commission only evidence-supported calibration; otherwise defer.
- Weeks 12-13: playoff-readiness/model-freeze preparation.
- Before Week 14: playoff production baseline commissioned.
- Weeks 14-17: production-first; major empirical calibration frozen by default.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- No observed 2026 outcome may retroactively tune a v0.X model.
- Diagnostics remain observers, not decision/control logic.
- Missed prospective captures are recorded as missing, never backfilled.
- Persistent evidence requires a separate authorization gate.
- Authenticated/raw capture material remains local.
- Validation evidence is bound to the candidate byte identity that produced it.

## Canonical References

- active state: `../CURRENT.md`
- Phase 1B source-validation evidence:
  `../evidence/PHASE1B_CLOSURE_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- Phase 1B recovery evidence:
  `../evidence/PHASE1B_RECOVERY_FAILURE_LINEAGE_2026-09-22.md`
- Week 3 capture evidence:
  `../evidence/WEEK3_WEEK_OPEN_PROSPECTIVE_CAPTURE_2026-09-22.md`
- M7 durability evidence:
  `../evidence/MEMORY_M7_DURABILITY_CLOSURE_2026-09-22.md`
- Phase 1A runtime evidence:
  `../evidence/V10A_DATA_SOURCE_SEASON_SYNC_RUNTIME_COMMISSIONING_2026-09-21.md`
- startup/handoff health: `../MAINTENANCE.md`
- long-range roadmap: `../../ROADMAP.md`
- 2026 weekly map: `SEASON_2026.md`
- known issues: `../../KNOWN_ISSUES.md`
