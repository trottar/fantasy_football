# Decision Log

## D-001 — Repository-backed durable memory

**Status:** ACTIVE

Use `docs/memory/` as the canonical continuity layer. Chat history is not authoritative when it conflicts with current source/evidence/memory.

## D-002 — Public repository with local secret/raw boundary

**Status:** ACTIVE

The repository may remain public. Secrets, authenticated raw data, and private runtime material stay local. Sanitized conclusions and evidence summaries may be committed.

## D-003 — 0.X / 1.X scientific boundary

**Status:** ACTIVE

0.X remains a-priori architecture. Observed 2026 outcomes may only inform 1.X.

## D-004 — Player/DST/K channel separation

**Status:** ACTIVE

Maintain `P ⊕ D ⊕ K`. Cross-channel comparison is prohibited except at complete-roster utility boundaries.

## D-005 — Screen is not decision authority

**Status:** ACTIVE

Cheap/deterministic screens may generate a frontier. Predictive uncertainty-aware response machinery authorizes meaningful football actions.

## D-006 — Behavior separate from football utility

**Status:** ACTIVE

Manager behavior kernels may use market/perception features, but football value remains physically modeled.

## D-007 — v1.0 is observability/memory, not retuning

**Status:** ACTIVE

The first 1.X release establishes Week 1 ingestion, weekly recap, immutable evidence, residual diagnostics, transaction ledger, and investigation machinery with zero automatic parameter adjustment.

<!-- FANTASY_D008_FIRST_CLASS_OBSERVABILITY:BEGIN -->
## D-008 — First-class diagnostics/observability substrate

**Status:** ACTIVE

The first 1.X engineering layer is `v1.0A`: a modular observability substrate shared by football channels, data sources, market behavior, closure, services, background work, CLI, and GUI.

Diagnostics are observers and may not change physics, decision authority, manager behavior, or random draws.

GUI diagnostics are included from the beginning: lifecycle, session/client, page, action, background-task, service-call, render/refresh, correlation, and stale-client/state-transition evidence are part of the same substrate.

A significant subsystem is not fully commissioned until its relevant structured events, provenance, invariant/failure diagnostics, privacy behavior, and debug/replay evidence are adequate.
<!-- FANTASY_D008_FIRST_CLASS_OBSERVABILITY:END -->

<!-- FANTASY_D009_PRIVYHUB_STYLE_CHECKPOINTS:BEGIN -->
## D-009 — PrivyHub-style checkpoint authorization and push workflow

**Status:** ACTIVE

Fantasy Football adopts the PrivyHub-style checkpoint boundary:

- durable memory is continuously maintained and pushed through the checkpoint ZIP;
- diagnostic/probe/audit/observability tooling may advance and be pushed with the same standing authorization;
- production football/model/application/business logic requires explicit user authorization at the end of the checkpoint;
- repository writes use the ZIP/PowerShell checkpoint workflow with exact staging allowlists and remote verification;
- direct GitHub connector writes are not used for project checkpoint pushes.

This decision supersedes earlier generic collaboration wording where it conflicts.
<!-- FANTASY_D009_PRIVYHUB_STYLE_CHECKPOINTS:END -->

<!-- FANTASY_D015_MEMORY_MAINTENANCE_INDEX:BEGIN -->
## D-015 — Durable Memory Maintenance Policy

**Status:** ACTIVE

`CURRENT.md` is the sole authoritative active frontier. Substantial-work startup
is:

`AGENTS.md -> CURRENT.md -> MEMORY.md -> CURRENT_HANDOFF.md -> USER.md`

`MAINTENANCE.md` owns memory-health thresholds, semantic triggers,
safe-checkpoint behavior, and cleanup procedure. `CURRENT_HANDOFF.md` is
non-authoritative and remains small/rewriteable.

Before restating a decision/gate/classification/deadline, read the canonical
record that defines it.

See `D-015_MEMORY_MAINTENANCE_POLICY.md`.
<!-- FANTASY_D015_MEMORY_MAINTENANCE_INDEX:END -->

<!-- FANTASY_D017_V10A_SNAPSHOT_REPLAY_DIFF_INDEX:BEGIN -->
## D-017 — v1.0A Local Snapshot / Replay / Diff

**Status:** ACTIVE

Adopt privacy-aware local replay-evidence bundles, integrity verification, and
bounded redacted structural diffs. Replay is evidence loading only in this
slice; production automatic capture and computation replay remain deferred.
<!-- FANTASY_D017_V10A_SNAPSHOT_REPLAY_DIFF_INDEX:END -->

<!-- FANTASY_D021_V10A_CLI_SEASON_SHADOW_INDEX:BEGIN -->
## D-021 — CLI + SeasonGuiService shadow pilot

**Status:** ACTIVE

The first production-source observability pilot is limited to final CLI dispatch
and read-only `SeasonGuiService.source_health()`, using bounded in-memory events
with no persistence. See `D-021_V10A_CLI_SEASON_SHADOW_PILOT.md`.
<!-- FANTASY_D021_V10A_CLI_SEASON_SHADOW_INDEX:END -->

<!-- FANTASY_D022_V10A_GUI_LIFECYCLE_SHADOW_INDEX:BEGIN -->
## D-022 — GUI background-task/lifecycle shadow pilot

**Status:** ACTIVE

The GUI pilot is limited to selected-MC/progress-pump task lifecycle plus
page/connect/disconnect/delete correlation using bounded in-memory evidence.
See `D-022_V10A_GUI_LIFECYCLE_SHADOW_PILOT.md`.
<!-- FANTASY_D022_V10A_GUI_LIFECYCLE_SHADOW_INDEX:END -->

<!-- FANTASY_D023_SEASON_GATED_ROADMAP_INDEX:BEGIN -->
## D-023 — 2026 Season-Gated Development Roadmap

**Status:** ACTIVE

Separate calendar gates from evidence gates. Prospective capture deadlines are
irreversible; calibration gates pass only when prospective Data/MC closure
supports them. Week 14 begins the configured fantasy playoff window, so the
playoff production baseline must be commissioned before it.

See `D-023_2026_SEASON_GATED_ROADMAP.md`.
<!-- FANTASY_D023_SEASON_GATED_ROADMAP_INDEX:END -->

<!-- FANTASY_D024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_INDEX:BEGIN -->
## D-024 — v1.0A Data-Source Season-Sync Shadow Pilot

**Status:** ACTIVE

Authorize one privacy-conservative outer shadow boundary around
`sync_season_snapshot`. The observer may retain generated correlation, boundary
identity, duration, and exception type only. Provider internals, arguments,
returned snapshot/path data, authenticated payloads, exception messages, and
persistent sinks remain outside this slice.

See `D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`.
<!-- FANTASY_D024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_INDEX:END -->
