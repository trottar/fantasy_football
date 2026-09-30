# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective captures: **VALID / PRESERVED**
- Week 4 one-for-one player trade search: **VALID FOR NARROW SCOPE / HOLD**
- Week 4 roster-wide decision completion: **INCOMPLETE_COVERAGE**
- Weekly decision orchestration/completion gate: **BLOCKING FAILURE**
- Weekly operational health receipt gate: **NOT ENFORCED / BLOCKING**
- Memory-contract hardening: **PUSHED / REMOTE VERIFIED**
- Read-only source/design audit: **COMPLETE / MEMORY CHECKPOINT PENDING**
- Production orchestration repair: **DESIGNED / NOT YET AUTHORIZED**
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

## Read-Only Source / Design Audit

The production surface is fragmented by command rather than governed by a
weekly completion state machine. `fantasy.py` and the GUI/service expose
lineup, player actions, DST, kicker, and trade functions independently.

The repair must reuse the commissioned authorities rather than replace them:

- player actions: `transaction_manager.evaluate_actions`;
- DST/K: `specialist_policy_v032`;
- lineup/availability: `weekly_manager` plus `UtilityContext` evidence state;
- provenance: prospective capture integrity/firewall;
- roster-state facts: ESPN lineup slot / eligible slot normalization;
- non-interference: observability persistence state.

New production control-plane requirements:

1. fail-closed weekly decision receipt/state machine;
2. weekly operational-health receipt;
3. specialist current-WAIVER acquisition authority;
4. automated supported multi-asset trade package search;
5. specialist-inclusive trade evaluation with `P ⊕ D ⊕ K` composition;
6. explicit IR/open-slot/injury-replacement transitions;
7. decision-time multiweek absence state where authoritative evidence exists;
8. one authoritative CLI/service path for roster-wide completion language.

## Next Gate

Publish the source/design audit memory checkpoint. After remote verification,
production source repair requires explicit user authorization.

Week 3 closure and nonessential Phase 1E work remain deferred behind this repair.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Channel separation is valuation architecture, not transaction exclusion.
- User examples do not define search scope.
- `screen != authority`.
- Missing channel/health receipts block completion.
- Raw prospective evidence is preserved even when interpretation is superseded.
- No observed 2026 outcome may tune v0.X.
