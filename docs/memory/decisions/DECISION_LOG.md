# Decision Log

This file is the compact index of accepted durable decisions. Canonical decision
records own full rationale, evidence, and boundaries.

## D-001 — Repository-backed durable memory

**Status:** ACTIVE

Use `docs/memory/` as canonical continuity. Chat history does not override current
source/evidence/repository memory.

## D-002 — Public repository with local secret/raw boundary

**Status:** ACTIVE

The repository may remain public; secrets, authenticated raw data, and private
runtime/account material remain local.

## D-003 — 0.X / 1.X scientific boundary

**Status:** ACTIVE

`0.X` remains a-priori architecture. Observed 2026 outcomes may inform only
`1.X` calibration.

## D-004 — Player/DST/K channel separation

**Status:** ACTIVE

Maintain `P ⊕ D ⊕ K` inside valuation/response: players compare to players, DST
to DST, and kickers to kickers. Cross-channel composition occurs only at the
complete-roster utility/state boundary. This does **not** exclude DST/K assets
from league-legal multi-channel transactions.

## D-005 — Screen is not decision authority

**Status:** ACTIVE

Cheap screens may generate a frontier; predictive uncertainty-aware response
machinery authorizes meaningful football actions.

## D-006 — Behavior separate from football utility

**Status:** ACTIVE

Manager behavior kernels may use market/perception features, but those features
do not change intrinsic football value.

## D-007 — v1.0 is observability/memory, not retuning

**Status:** ACTIVE

The first 1.X engineering release builds measurement/closure infrastructure with
zero automatic parameter adjustment.

## D-008 — First-class diagnostics/observability substrate

**Status:** ACTIVE

Use a shared structured observability substrate across football/data/service/GUI
boundaries. Diagnostics observe but do not alter physics, decisions, behavior, or
random draws.

## D-009 — Human-in-the-loop checkpoint authorization

**Status:** ACTIVE / DELIVERY MECHANICS SUPERSEDED BY D-025

Keep durable memory continuous, diagnostics standing-authorized, production
football semantics explicitly authorized, and repository publication
human-in-the-loop. D-025 supersedes ZIP-era transport mechanics.

## D-010 — Phase 0 Final 0.X Authority

**Status:** ACTIVE

Treat v0.36 as the latest source-validated 0.X candidate while rejecting the
original packaged v0.36 ZIP for commissioning. Do not infer a historical
`v0.36-fixed1`. See `D-010_PHASE0_FINAL_0X_AUTHORITY.md`.

## D-011 — v0.36-repack1 Release Gate

**Status:** ACTIVE

Use `v0.36-repack1` as a packaging revision only: exact validated v0.36 plus the
four omitted public fixtures, with internal `VERSION = 0.36`. See
`D-011_V036_REPACK1_RELEASE_GATE.md`.

## D-012 — v0.36-repack1 Commissioned / v1.0A Ready

**Status:** ACTIVE

The repaired release passed automated validation and operator live-GUI
commissioning, establishing the commissioned final 0.X runtime baseline. See
`D-012_V036_REPACK1_COMMISSIONED_V10A_READY.md`.

## D-013 — v1.0A Context/Event Contract

**Status:** ACTIVE

Adopt immutable stdlib-only run/action context, structured event, and registry
contracts before production emission. See `D-013_V10A_CONTEXT_EVENT_CONTRACT.md`.

## D-014 — v1.0A Sinks and Provenance

**Status:** ACTIVE

Keep sinks explicit/dependency-injected with no hidden global logger; persistent
JSONL production/private integration remains blocked until redaction is applied
and proven. See `D-014_V10A_SINKS_PROVENANCE.md`.

## D-015 — Durable Memory Maintenance Policy

**Status:** ACTIVE

`CURRENT.md` is sole active frontier; substantial startup reads the five-file
core in full; `MAINTENANCE.md` owns memory-health policy. See
`D-015_MEMORY_MAINTENANCE_POLICY.md`.

## D-016 — v1.0A Invariants and Privacy/Redaction

**Status:** ACTIVE

Adopt explicit immutable invariant-result contracts and conservative copy-only
redaction/pseudonymization before persistent production evidence. See
`D-016_V10A_INVARIANTS_REDACTION.md`.

## D-017 — v1.0A Local Snapshot / Replay / Diff

**Status:** ACTIVE

Adopt privacy-aware local integrity-verified replay evidence and bounded
structural diffs. Replay is evidence loading, not computation execution. See
`D-017_V10A_SNAPSHOT_REPLAY_DIFF.md`.

## D-018 — v1.0A Failure-Bundle Contract

**Status:** ACTIVE

Failure bundles are bounded privacy-safe local evidence only; they do not alter
control flow, define recovery, or enable automatic private persistence. See
`D-018_V10A_FAILURE_BUNDLE_CONTRACT.md`.

## D-019 — v1.0A Adapter / Correlation Contract

**Status:** ACTIVE

Use thin opt-in adapters over the existing immutable context/event correlation
model; preserve direct P/D/K separation and non-interference. See
`D-019_V10A_ADAPTER_CORRELATION_CONTRACT.md`.

## D-020 — v1.0A Production Integration Gate

**Status:** ACTIVE

Require explicit shadow integration plus paired output/exception, RNG/state, and
overhead evidence before each production observability pilot. See
`D-020_V10A_INTEGRATION_GATE.md`.

## D-021 — CLI + SeasonGuiService shadow pilot

**Status:** ACTIVE

Limit the first production shadow pilot to final CLI dispatch and read-only
`SeasonGuiService.source_health()` with bounded in-memory evidence. See
`D-021_V10A_CLI_SEASON_SHADOW_PILOT.md`.

## D-022 — GUI background-task/lifecycle shadow pilot

**Status:** ACTIVE

Observe selected-MC/progress task lifecycle and page lifecycle with bounded
correlation while preserving scheduling/cancellation semantics. See
`D-022_V10A_GUI_LIFECYCLE_SHADOW_PILOT.md`.

## D-023 — 2026 Season-Gated Development Roadmap

**Status:** ACTIVE

Separate irreversible calendar capture gates from evidence/calibration gates and
protect prospective information windows. See `D-023_2026_SEASON_GATED_ROADMAP.md`.

## D-024 — v1.0A Data-Source Season-Sync Shadow Pilot

**Status:** ACTIVE

Authorize a privacy-conservative outer shadow boundary around
`sync_season_snapshot` with bounded in-memory evidence and no authenticated
payload persistence. See `D-024_V10A_DATA_SOURCE_SEASON_SYNC_SHADOW_PILOT.md`.

## D-025 — Generic `.ffpkg` Delivery Infrastructure

**Status:** ACTIVE

Use deterministic text `.ffpkg` transport, reusable runner/extraction integrity,
and declarative isolated staging. Package-specific code owns only target-specific
predecessor/rollback/idempotence/domain validation. See
`D-025_GENERIC_DELIVERY_INFRASTRUCTURE.md`.

## D-026 — Active Memory Semantic Integrity

**Status:** ACTIVE

Strict memory health must reject deterministic repository-state contradictions
that can be known mechanically while remaining unable to infer football truth.
Use publication-stable active state, exact stable-handoff semantics, complete
canonical decision indexing, current weekly template contracts, and `.ffpkg`
delivery wording. See `D-026_ACTIVE_MEMORY_SEMANTIC_INTEGRITY.md`.
