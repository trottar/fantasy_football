# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 one-for-one player trade search: **VALID FOR NARROW SCOPE / HOLD**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Weekly decision orchestration/completion gate: **BLOCKING FAILURE**
- Weekly operational health receipt gate: **NOT ENFORCED / BLOCKING**
- Memory-contract hardening: **ACTIVE / MUST PRECEDE SOURCE REPAIR**
- Week 3 Data/MC closure: **BLOCKED BY ORCHESTRATION RECOVERY**
- Phase 1E persistence controller: **RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E activation: **SEPARATELY GATED / NOT AUTHORIZED**
- No observed 2026 outcome has tuned v0.X.

## Failure Classification

The project had functioning player, DST, and kicker decision subsystems but no
hard weekly completion gate requiring all of them to produce receipts before a
cycle could be called complete.

Week 3 demonstrates that broad player add/drop and separate DST/K evaluation were
available and used. Week 4 regressed to a partial workflow: lineup/status plus a
one-for-one player trade search were allowed to support language stronger than
their actual scope.

Classification:

`WEEKLY_DECISION_ORCHESTRATION_COMPLETION_GATE_FAILURE`

This is a structural workflow defect, not evidence for football calibration.

## Required Completion Contract

A weekly roster decision may reach `COMPLETE` only after current receipts exist
for:

1. lineup/status/availability;
2. whole-player-roster waiver/free-agent search;
3. commissioned DST waiver/free-agent policy;
4. commissioned kicker waiver/free-agent policy;
5. IR/reserve/open-slot/injury-replacement state;
6. required trade-search families;
7. decision-time capture/provenance;
8. weekly operational health.

Unsupported or missing action families must be explicit blockers. They may not be
silently converted to HOLD.

Canonical owner:
`architecture/WEEKLY_DECISION_COMPLETION.md`.

## Known Capability Gaps to Repair

- automated trade search is one-for-one player-only;
- underlying player trade evaluator can represent up to two assets per side but
  that package space is not automatically searched;
- specialist-inclusive trade evaluation is absent;
- authoritative specialist dynamic policy excludes current WAIVERS from its
  guaranteed-free-agent pool;
- explicit IR-move-plus-add action is absent;
- explicit multiweek injury-duration roster-state propagation is absent;
- no unified weekly orchestrator/completion receipt exists;
- no mandatory fresh weekly operational health receipt exists.

## Week 4 Evidence Boundary

The week-open and pre-lock captures remain valid prospective evidence. The earlier
trade HOLD is retained only as a one-for-one player-trade conclusion. Roster-wide
HOLD/NO-ACTION authority is withdrawn pending repaired complete coverage.

No transaction should be authorized from the incomplete cycle.

## Health Boundary

Weekly operational health must be current before cycle completion. Source/change
health becomes mandatory whenever source, tooling, runtime, or decision
orchestration changes.

Missing health evidence is `BLOCKED_HEALTH`, not PASS.

## Next Gate

Publish the memory-only failure audit and completion contract first. After remote
verification, audit/design the production orchestrator against that contract
before modifying source.

Week 3 closure and nonessential Phase 1E work remain deferred behind this repair.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Channel separation is valuation architecture, not transaction exclusion.
- User examples do not define search scope.
- `screen != authority`.
- Missing channel/health receipts block completion.
- Raw prospective evidence is preserved even when interpretation is superseded.
- No observed 2026 outcome may tune v0.X.
