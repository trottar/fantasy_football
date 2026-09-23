# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C channel boundary audit: **COMPLETE / DURABLE**
- Phase 1C DST shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C K shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C player boundary discovery: **COMPLETE / READ-ONLY**
- Phase 1C player shadow: **SOURCE-VALIDATED / RECOVERY-AUDITED / PUBLICATION DURABILITY RESOLVES FROM CONTAINING GIT / RUNTIME NOT COMMISSIONED**
- Phase 1D market/manager-behavior observability: **NOT STARTED / SEPARATELY GATED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 week-open capture: **SECURED / VALID / PRE-KICKOFF**

## Phase 1C Specialist State

DST boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`
at `subsystem.dst.channel`.

K boundary:
`src/specialist_policy_v032.py::evaluate_kicker_channel`
at `subsystem.k.channel`.

Both specialist shadows are source-published and runtime-commissioned. Their
observers remain bounded and in-memory only.

Canonical runtime evidence:

- `../evidence/PHASE1C_DST_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`
- `../evidence/PHASE1C_K_SHADOW_RUNTIME_COMMISSIONING_2026-09-22.md`

## Phase 1C Player Boundary State

Rejected as player-only:

`transaction_manager.evaluate_roster_predictive`

Reason: it is complete-roster P/D/K response machinery and therefore cannot be
treated as a pure player-channel boundary.

Accepted and fully source-validated player-only shadow boundaries remain:

- CLI: `transaction_manager.evaluate_actions` at `subsystem.player.evaluate_actions`;
- GUI: `SeasonGuiService.evaluate_single_add_drop` at
  `subsystem.player.evaluate_single_add_drop`.

The five technical player files remain exact to the validated candidate.
Fresh-chat recovery audits established that canonical delivery tooling and
handoff authority are exact and that the failed publication-infrastructure
attempt caused no canonical drift.

The historical v2 isolated stage passed its representation, manifest, health,
and allowlist gates and remains exact evidence. It is not the successor
publication authority because its predecessor predates the current remote
checkpoint. A later read-only semantics audit also exposed a truncated final
sentence in its `roadmap/STATUS.md`; this recovery checkpoint repairs that text.

Publication durability is intentionally resolved from the containing Git/ref
rather than hard-coded into this file. If this exact recovery checkpoint is on
remote `main`, source publication is complete; otherwise the permanent generic
declarative staging path is the publication route. Runtime commissioning remains
a separate later gate.

Canonical evidence:

- `../evidence/PHASE1C_PLAYER_SHADOW_SOURCE_VALIDATION_2026-09-22.md`
- `../evidence/PHASE1C_PLAYER_SHADOW_PUBLICATION_STATE_REPAIR_2026-09-22.md`
- `../evidence/PHASE1C_PLAYER_PUBLICATION_RECOVERY_2026-09-23.md`

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Players compare only with players.
- Diagnostics remain observers, not decision/control logic.
- Player instrumentation must preserve output/exception semantics, RNG, mutable
  state, privacy, and the established overhead gate.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
