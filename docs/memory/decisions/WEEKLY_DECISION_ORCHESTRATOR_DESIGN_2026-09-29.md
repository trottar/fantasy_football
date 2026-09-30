# Weekly Decision Orchestrator Design — 2026-09-29

---
decision_type: structural_operability
status: PROPOSED_AFTER_READ_ONLY_AUDIT
source_checkpoint: c21bfce9a5dd94f9269b7749ea10ea916d7c91e3
production_source_change: not_yet_authorized
football_model_tuning: false
---

## Objective

Make it mechanically impossible for a partial weekly fantasy workflow to be
reported as a complete roster decision.

The design implements
`architecture/WEEKLY_DECISION_COMPLETION.md`; it does not replace the existing
football models.

## Control Plane

Add one canonical weekly decision-cycle service, tentatively
`src/weekly_decision_cycle.py`.

It owns receipt/state orchestration only. Existing channel modules remain the
calculation authorities.

Core receipt types:

- `ChannelReceipt`
- `OperationalHealthReceipt`
- `WeeklyDecisionReceipt`

The final state is fail-closed:

- missing/unsupported channel -> `INCOMPLETE_COVERAGE`;
- missing/stale/failed health -> `BLOCKED_HEALTH`;
- material stale information -> `CAPTURE_REQUIRED`;
- only a complete matrix may emit `COMPLETE / ACTION_REQUIRED` or
  `COMPLETE / NO_ACTION`.

Existing standalone commands remain useful diagnostics but may emit only
scope-qualified results such as `CHANNEL_HOLD:ONE_FOR_ONE_PLAYER_TRADE`.

## Reused Authorities

### Lineup / availability

Use `weekly_manager` plus `UtilityContext.availability_state` and lock timing.

### Player waiver / free-agent

Use `transaction_manager.evaluate_actions`.

This remains the single player-channel paired-MC authority.

### DST / kicker

Use the commissioned `specialist_policy_v032` policy functions.

Lower-level static specialist diagnostics cannot substitute for this receipt.

### Prospective provenance

Use the frozen snapshot/capture identity plus
`prospective_measurement_v034.verify_capture_integrity` and firewall fields.

### Non-interference

Use `observability.persistence.shadow_persistence_state`.

## Weekly Operational Health

Add a shared operational-health builder, tentatively
`src/weekly_operational_health.py`, consumed by the orchestrator.

The receipt must combine:

1. source/checkpoint identity supplied by the commissioned runtime/operator
   boundary;
2. runtime version and commissioned dependency identity;
3. six-family live provider/source health;
4. capture integrity and pre-data firewall;
5. persistence/non-interference state;
6. strict memory-health result;
7. unresolved diagnostic blockers;
8. decision-channel receipt inventory.

The runtime/release workflow should provide machine-readable commissioning
identity rather than requiring weekly packages to hard-code source hashes.

## Missing Capability Work

### Specialist current WAIVERS

Extend specialist market state so current WAIVERS are modeled as uncertain
acquisitions using a separate manager/waiver behavior kernel. Do not treat them
as guaranteed FREEAGENTs.

### IR / reserve / open slot

Add explicit roster-state action generation using ESPN `lineup_slot_id`,
`eligible_slots`, current roster occupancy, and league IR capacity.

At minimum model legal:

- move eligible roster player to IR/reserve;
- add into the newly opened active slot;
- return-from-IR constraints when relevant;
- replacement of unavailable players.

Do not infer eligibility solely from a user-mentioned player or an injury label
when direct ESPN state is available.

### Multiweek absence

Where decision-time authoritative evidence gives an absence horizon, propagate
that information into future-week availability state without calibrating/tuning
v0.X from outcomes.

Unknown future status remains uncertain; do not fabricate a recovery date.

### Trade search

Separate candidate generation from predictive authority.

Expand automated search beyond one-for-one to the package shapes supported by
the transaction evaluator, including unequal packages and post-trade legal
release/fill effects.

Search must report its enumerated/screened/legal package counts and supported
shape coverage. Cheap screening may prune; full paired MC remains authority.

### Specialist-inclusive trades

General transaction composition must partition P/D/K assets, value each with its
commissioned channel physics, mutate ownership/market state, and combine only at
the complete-roster state boundary.

Manager acceptance remains a separate behavior layer.

Until this evaluator is commissioned, specialist-inclusive trade coverage stays
`INCOMPLETE_COVERAGE`.

## Interfaces

### CLI

Add one authoritative weekly-cycle command.

It produces one immutable JSON receipt with all channel/health states and never
prints roster-wide HOLD/NO_ACTION unless the matrix is complete.

### GUI / service

Expose the exact same receipt through `SeasonGuiService`; do not create a GUI
optimizer or a second completion classifier.

### Chat report

Surface completion state, missing coverage, stale health, narrow channel holds,
and authorized actions from the shared receipt.

## Test Contract

Minimum regressions:

1. omit player actions -> `INCOMPLETE_COVERAGE`;
2. omit DST -> `INCOMPLETE_COVERAGE`;
3. omit K -> `INCOMPLETE_COVERAGE`;
4. stale/failed health -> `BLOCKED_HEALTH`;
5. user-named player does not narrow broad market enumeration;
6. current specialist WAIVER cannot disappear from coverage;
7. IR move-plus-add is represented from direct ESPN slot state;
8. known multiweek absence changes future-week state without outcome tuning;
9. one-for-two / two-for-one player packages reach automated search;
10. specialist-inclusive trade preserves `P ⊕ D ⊕ K`;
11. CLI/GUI/chat cannot independently upgrade a narrow HOLD to roster-wide HOLD;
12. material information change invalidates stale receipts;
13. no omitted prospective search can be backfilled as contemporaneous.

## Implementation Sequence

### Gate A — fail closed first

Install the receipt/state machine, operational-health interface, and CLI/service
orchestration over existing authorities.

Any still-missing capability is explicitly blocking.

### Gate B — close capability gaps

Implement current specialist waiver claims, IR/open-slot transitions, multiweek
absence state, broader package search, and specialist-inclusive trade
composition.

The cycle remains incomplete until these are commissioned.

### Gate C — source/change health

Run targeted regressions, full pytest, compileall, exact package QA, diff checks,
isolated staging/manifest validation, publication, and runtime synchronization/
commissioning.

### Gate D — fresh football commissioning

From a fresh decision-time Week 4 state, run the entire weekly cycle without user
prompting and prove every required channel/health receipt.

Only then may the system emit a roster-wide completion state or resume deferred
Week 3 closure.

## Authorization Boundary

This design record does not authorize production-source modification.

After this memory checkpoint is remote-durable, source work requires explicit
user authorization.
