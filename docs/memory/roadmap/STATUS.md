# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 one-for-one player trade search: **VALID FOR NARROW SCOPE / HOLD**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Active-memory semantic-integrity hardening: **PUSHED / REMOTE VERIFIED**
- Gate A fail-closed weekly control plane: **PUSHED / REMOTE VERIFIED / RUNTIME COMMISSIONED**
- Gate A weekly operational-health interface: **RUNTIME COMMISSIONED**
- Gate A commissioned runtime: **v0.36-repack1 / VALIDATED**
- Gate B capability closure: **AUTHORIZED / ACTIVE**
- Gate B1 specialist current-WAIVER source: **SOURCE-VALIDATED / LOCAL-APPLIED / NOT PUBLISHED**
- Gate B1 commissioned runtime: **NOT YET SYNCHRONIZED / NOT COMMISSIONED**
- Week 3 Data/MC closure: **BLOCKED BY CAPABILITY RECOVERY**
- Phase 1E persistence controller: **RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E activation: **SEPARATELY GATED / NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Blocking Recovery Contract

A weekly roster decision may reach `COMPLETE` only after the current receipt
matrix in `architecture/WEEKLY_DECISION_COMPLETION.md` accounts for lineup,
player actions, DST, kicker, IR/injury-replacement state, required trade families,
prospective provenance, and weekly operational health.

Gate A enforces the fail-closed control plane in the commissioned runtime. B1 now
has a source-validated candidate for explicit current specialist-WAIVER
acquisition-state coverage, but that capability is not operational until source
publication and runtime commissioning complete. Unsupported action families
remain `INCOMPLETE_COVERAGE`; missing/stale required health remains
`BLOCKED_HEALTH`; a narrow channel HOLD cannot become a roster-wide HOLD.

## Known Capability Gaps

- current specialist WAIVERS: B1 source validated/local-applied, but not yet
  published or runtime-commissioned;
- automated player trade search remains narrower than evaluator capability;
- specialist-inclusive trade evaluation is absent;
- explicit IR-move-plus-add action generation is absent;
- explicit decision-time multiweek absence propagation is absent.

## Gate B1 Source Boundary

Predecessor checkpoint:
`d80ed56a75f034516b8d5387894b4899375d61f7`.

Source-validation package:
`weekly_decision_gate_b1_specialist_waivers_source_preflight_v1_20261001`.

Accepted operator receipt:

- remote/predecessor: exact `d80ed56a75f034516b8d5387894b4899375d61f7`;
- changed source/test paths: 3;
- targeted B1 pytest: PASS;
- full repository pytest: PASS;
- compileall: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS;
- exact result identities: PASS;
- control root: untouched by diagnostic;
- commissioned runtime: untouched;
- staging/commit/push: not performed.

B1 semantics preserve current WAIVERS as uncertain acquisitions, reuse the
existing manager-claim behavior kernel, retain DST/K football authority, and
cover both one-slot specialist actions and current-week DST carry-two state.

Canonical evidence:
`evidence/WEEKLY_DECISION_GATE_B1_SPECIALIST_WAIVERS_SOURCE_VALIDATION_2026-10-01.md`.

## Memory Integrity Boundary

Active memory must remain publication-stable and mutually coherent. The strict
checker may reject deterministic repository-state contradictions, incomplete
canonical decision indexing, stale stable-handoff residue, obsolete delivery
wording, and missing required weekly decision-template contracts. It does not
infer football truth or replace the weekly operational receipt.

Canonical decision:
`decisions/D-026_ACTIVE_MEMORY_SEMANTIC_INTEGRITY.md`.

## Next Gate

Stage and publish the exact B1 source-plus-memory checkpoint, verify it remotely,
then separately synchronize and commission B1 into `v0.36-repack1`. Do not begin
the next Gate B capability sub-gate until B1 runtime commissioning is complete.
A fresh complete Week 4 cycle and Week 3 closure remain blocked until all required
Gate B coverage is commissioned and a fresh receipt matrix passes.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Gate A is orchestration/operability, not a second optimizer.
- Current WAIVERS remain uncertain acquisition states, never guaranteed free agents.
- Manager acquisition behavior remains separate from intrinsic football utility.
- Channel separation is valuation architecture, not transaction exclusion.
- User examples do not define search scope.
- `screen != authority`.
- Raw prospective evidence remains preserved when an interpretation is withdrawn.
- No observed 2026 outcome may tune v0.X.
