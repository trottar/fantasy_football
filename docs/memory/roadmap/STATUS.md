# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 one-for-one player trade search: **VALID FOR NARROW SCOPE / HOLD**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Weekly decision orchestration/completion gate: **BLOCKING FAILURE**
- Weekly operational health receipt gate: **NOT ENFORCED / BLOCKING**
- Read-only source/design audit: **PUSHED / REMOTE VERIFIED**
- Active-memory semantic-integrity hardening: **CURRENT MEMORY/TOOLING CHECKPOINT**
- Production orchestration repair: **DESIGNED / NOT AUTHORIZED**
- Week 3 Data/MC closure: **BLOCKED BY ORCHESTRATION RECOVERY**
- Phase 1E persistence controller: **RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E activation: **SEPARATELY GATED / NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

A weekly roster decision may reach `COMPLETE` only after the current receipt
matrix in `architecture/WEEKLY_DECISION_COMPLETION.md` accounts for lineup,
player actions, DST, kicker, IR/injury-replacement state, required trade families,
prospective provenance, and weekly operational health.

Unsupported action families remain `INCOMPLETE_COVERAGE`. Missing/stale required
health remains `BLOCKED_HEALTH`. A narrow channel HOLD cannot become a roster-wide
HOLD.

## Known Capability Gaps

- no commissioned fail-closed weekly completion orchestrator;
- no mandatory unified weekly operational-health receipt;
- current specialist WAIVERS are outside guaranteed FREEAGENT specialist authority;
- automated player trade search remains narrower than evaluator capability;
- specialist-inclusive trade evaluation is absent;
- explicit IR-move-plus-add action generation is absent;
- explicit decision-time multiweek absence propagation is absent.

## Memory Integrity Boundary

Active memory must remain publication-stable and mutually coherent. The strict
checker may reject deterministic repository-state contradictions, incomplete
canonical decision indexing, stale stable-handoff residue, obsolete delivery
wording, and missing required weekly decision-template contracts. It does not
infer football truth or replace the weekly operational receipt.

Canonical decision:
`decisions/D-026_ACTIVE_MEMORY_SEMANTIC_INTEGRITY.md`.

## Next Gate

Finish the memory/tooling checkpoint through normal checkpoint publication. After
remote verification, production source repair remains behind explicit user
authorization. If authorized, Gate A is the fail-closed weekly receipt/state
machine plus operational-health interface before any broader capability repair.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Channel separation is valuation architecture, not transaction exclusion.
- User examples do not define search scope.
- `screen != authority`.
- Raw prospective evidence remains preserved when an interpretation is withdrawn.
- No observed 2026 outcome may tune v0.X.
