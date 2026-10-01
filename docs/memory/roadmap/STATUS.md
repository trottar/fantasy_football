# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 one-for-one player trade search: **VALID FOR NARROW SCOPE / HOLD**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Active-memory semantic-integrity hardening: **PUSHED / REMOTE VERIFIED**
- Gate A fail-closed weekly control plane: **LOCAL-APPLIED / SOURCE-VALIDATED / NOT PUBLISHED**
- Gate A weekly operational-health interface: **LOCAL-APPLIED / SOURCE-VALIDATED / NOT COMMISSIONED**
- Gate A commissioned runtime state: **UNCHANGED / v0.36-repack1**
- Gate B capability closure: **NOT STARTED / BLOCKED BEHIND GATE A COMMISSIONING**
- Week 3 Data/MC closure: **BLOCKED BY ORCHESTRATION RECOVERY**
- Phase 1E persistence controller: **RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E activation: **SEPARATELY GATED / NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

A weekly roster decision may reach `COMPLETE` only after the current receipt
matrix in `architecture/WEEKLY_DECISION_COMPLETION.md` accounts for lineup,
player actions, DST, kicker, IR/injury-replacement state, required trade families,
prospective provenance, and weekly operational health.

Gate A now provides the fail-closed control plane in the locally validated source
candidate. It does not make missing capabilities complete. Unsupported action
families remain `INCOMPLETE_COVERAGE`; missing/stale required health remains
`BLOCKED_HEALTH`; a narrow channel HOLD cannot become a roster-wide HOLD.

## Known Capability Gaps

- Gate A control plane is not yet source-published or runtime-commissioned;
- current specialist WAIVERS are outside guaranteed FREEAGENT specialist authority;
- automated player trade search remains narrower than evaluator capability;
- specialist-inclusive trade evaluation is absent;
- explicit IR-move-plus-add action generation is absent;
- explicit decision-time multiweek absence propagation is absent.

## Source Validation Boundary

Diagnostic package `weekly_decision_gate_a_source_preflight_v1_20260930` validated
the exact five-path candidate against repository predecessor
`457e085a0acddc1ee9d6871a1bd85b10c8deb394` in an isolated clone. Targeted Gate A
pytest, full repository pytest, compileall, strict memory health, diff checks,
and exact result identities passed. That diagnostic changed neither control root
nor commissioned runtime.

The first local-apply carrier subsequently failed before modification because its
root-layout guard incorrectly required full application-source presence on the
sparse checkpoint surface. The corrected v2 local apply reconstructs modified
existing source from the exact remote predecessor and preserves the preflight
result identities; this is a packaging/synchronization-surface correction, not a
football/source-semantics change.

Canonical evidence:
`evidence/WEEKLY_DECISION_GATE_A_SOURCE_VALIDATION_2026-09-30.md`.

## Memory Integrity Boundary

Active memory must remain publication-stable and mutually coherent. The strict
checker may reject deterministic repository-state contradictions, incomplete
canonical decision indexing, stale stable-handoff residue, obsolete delivery
wording, and missing required weekly decision-template contracts. It does not
infer football truth or replace the weekly operational receipt.

Canonical decision:
`decisions/D-026_ACTIVE_MEMORY_SEMANTIC_INTEGRITY.md`.

## Next Gate

Isolated-stage the exact locally validated Gate A source-plus-memory allowlist,
regenerate the schema-2 memory manifest from staged Git blobs, publish through the
separate guarded publication carrier, and verify remote state. Then synchronize
the exact published source into the commissioned runtime and commission Gate A.
Do not begin Gate B capability repair before Gate A commissioning succeeds.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Gate A is orchestration/operability, not a second optimizer.
- Channel separation is valuation architecture, not transaction exclusion.
- User examples do not define search scope.
- `screen != authority`.
- Raw prospective evidence remains preserved when an interpretation is withdrawn.
- No observed 2026 outcome may tune v0.X.
