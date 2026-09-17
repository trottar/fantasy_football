# Agent Operating Rules

## Startup contract

For substantial work, read this minimum authoritative set first:

1. `AGENTS.md`
2. `CURRENT.md`
3. `USER.md`

Then read only the architecture, decision, investigation, evidence, roadmap,
tooling, and source/test files relevant to the current task.

`CURRENT.md` is the sole authoritative active-state document. Historical files,
dated logs, and handoffs may explain how the project arrived there, but they do
not override it.

## Authority and evidence

When sources disagree, prefer:

1. exact current source plus fresh direct evidence;
2. successful exact validation/commissioning receipts and provenance;
3. `CURRENT.md`;
4. canonical architecture/decision/investigation/evidence records;
5. Git/checkpoint history;
6. older summaries and historical snapshots.

Raw measurements outrank derived classifiers when they conflict. Never claim
inspection, testing, validation, runtime acceptance, or commissioning that did
not actually occur.

## Development method

Use the evidence-led loop:

`authority -> narrow question -> targeted probe -> raw evidence -> classification -> one coherent patch/defer/close`

Do not reopen resolved/deferred work without new evidence. Preserve unrelated
validated subsystems.

Detailed method:
`architecture/PROBLEM_SOLVING_METHOD.md`

## Scientific constraints

- Preserve `P ⊕ D ⊕ K`.
- Keep manager behavior separate from football physics.
- Use decision-time information only for prospective actions.
- Preserve frozen prospective state; no hindsight authorization.
- Treat uncertainty as first-class output.
- `screen != authority`.
- `0.X` remains a-priori; observed 2026 outcomes may inform only `1.X`.
- Diagnostics/observability must remain non-interfering.

## Authorization boundary

Standing authorization covers:
- `docs/memory/**`;
- observational diagnostic/probe/audit/logging/observability/replay/failure
  tooling.

Explicit user authorization is required for football/model/application/business
logic changes. If a change mixes diagnostics with production behavior and cannot
be cleanly separated, treat it as production.

Repository checkpoint writes use the ZIP/PowerShell workflow, not direct
GitHub-connector writes.

## Policy ownership

- Memory maintenance: `MAINTENANCE.md`
- Work-session/checkpoint communication: `COMMUNICATION.md`
- Environment/tooling procedures: `TOOLS.md`
- Patch/release mechanics: `patches/PATCH_PROTOCOL.md`
- Reusable lessons: `LEARNINGS.md`
- User/environment preferences: `USER.md`

Do not duplicate those detailed policies here.
