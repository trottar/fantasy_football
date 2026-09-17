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
