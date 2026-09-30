# Weekly Decision Completion Contract

## Purpose

This is the canonical operational contract for declaring a fantasy-football
weekly roster decision cycle complete.

It exists because the project demonstrated that functioning subsystems are not
enough: Week 3 exercised broad player and specialist evaluation, yet Week 4
regressed to a partial workflow because no hard completion gate required those
channels to run again.

## Central Invariant

**No weekly cycle may report `COMPLETE`, roster-wide `HOLD`, `NO ACTION`, or
advance to closure as if roster decisions were exhausted unless every required
decision channel and every required health gate has a current explicit receipt.**

A missing, unsupported, stale, failed, or skipped required channel is not a
negative recommendation. It is `INCOMPLETE_COVERAGE`.

A missing, stale, or failed required health receipt is `BLOCKED_HEALTH`.

## Decision-State Vocabulary

- `COMPLETE / ACTION_REQUIRED` — coverage and health complete; at least one
  authorized action exists.
- `COMPLETE / NO_ACTION` — coverage and health complete; no authorized action
  survives the relevant authority gates.
- `INCOMPLETE_COVERAGE` — one or more required action families lack a valid
  receipt or are unsupported.
- `BLOCKED_HEALTH` — decision search cannot be trusted because a required health
  gate is missing/stale/failed.
- `CAPTURE_REQUIRED` — information changed materially and a fresh decision-time
  capture is required before consequential action.
- `CHANNEL_HOLD:<scope>` — a narrow channel result only; it must name its scope
  and may not be promoted to roster-wide HOLD.

## Required Weekly Coverage Matrix

### 1. Lineup / availability

Receipt must include:

- complete legal starting lineup;
- current status/provenance;
- active probability and workload uncertainty where modeled;
- locked-player constraints;
- material contingency states.

### 2. Player waiver / free-agent channel

Run the broad QB/RB/WR/TE add/drop engine over the whole actionable pool and all
legal drops. User-mentioned players are not privileged search targets.

Cheap screens may prune. Predictive paired MC remains authority.

### 3. DST waiver / free-agent channel

Run the **commissioned specialist policy**, not merely a lower-level static
channel diagnostic.

The receipt must distinguish FREEAGENT and WAIVERS acquisition states. If current
waiver claims are excluded from authoritative policy, the channel is
`INCOMPLETE_COVERAGE` for those candidates.

### 4. Kicker waiver / free-agent channel

Same requirements as DST: commissioned specialist authority, current actionable
market, and explicit acquisition-state coverage.

### 5. IR / reserve / open-slot / injury replacement

Evaluate roster capacity and league-legal state transitions, including:

- open active slots;
- IR/reserve capacity and eligibility;
- IR-move-plus-add where legal;
- replacements for unavailable players;
- multiweek absence state when decision-time evidence supports it.

If a required state transition cannot be represented, record an explicit
capability gap.

### 6. Trade families

The required search is the league-legal transaction family, not whatever the
current automated helper happens to generate.

At minimum the receipt must state coverage for:

- one-for-one player trades;
- supported multi-player packages;
- unequal package sizes supported by the evaluator;
- DST/K-inclusive packages when league rules permit them;
- post-trade roster legality/fill/drop effects;
- both teams' football utility;
- manager-response probability as a separate behavior layer.

Unsupported families block roster-wide completion; they do not imply HOLD.

### 7. Specialist/player coupling

Preserve `P ⊕ D ⊕ K` internally. A transaction may include assets from multiple
channels. Value each channel with its own response model, then compose the
complete-roster perturbation:

`Delta U = U(S + delta S) - U(S)`.

Channel separation must never be misread as specialist transaction exclusion.

### 8. Prospective capture / provenance

Any consequential decision uses decision-time information and an explicit
capture/provenance boundary. A material new status, practice, roster, or market
change invalidates stale action authority.

## Search-Scope Rule

The system, not the user, owns search completeness.

A user naming Justice Hill, an injured player, a defense, a kicker, or any other
asset may open an investigation but may not narrow the production search to that
example. The cycle must enumerate the full relevant state/action space defined by
this contract.

## Weekly Operational Health Gate

A fresh weekly operational-health receipt is required before decision completion.

It must establish, at minimum:

- authoritative repository/checkpoint identity;
- commissioned runtime identity/version;
- expected source/config/data dependency identities;
- live provider/source health;
- prospective capture integrity and pre-data firewall;
- persistence/observability state relevant to non-interference;
- strict durable-memory health;
- no unresolved failed diagnostic that invalidates the active decision state;
- completion-receipt inventory for all required action channels.

If any item is missing or stale, state is `BLOCKED_HEALTH`.

## Source / Change Health Gate

Whenever production source, decision orchestration, diagnostic tooling, runtime,
or health tooling changes, the change checkpoint must additionally carry the
applicable engineering receipts:

- targeted tests;
- full `pytest`;
- `compileall`;
- exact generated-artifact/package validation;
- `git diff --check`;
- `git diff --cached --check` at staging;
- strict changed/staged allowlist;
- schema-2 manifest validation when memory changes;
- runtime synchronization/commissioning when runtime behavior changes;
- remote verification after publication.

Do not rerun passed gates without cause, but any subsequent change that could
invalidate a receipt requires that gate again.

## Freshness

A weekly completion receipt is state-bound, not calendar-permanent.

Reopen affected channels when material information changes: injury/practice
evidence, transactions, waiver state, roster ownership, lineup lock, source
correction, runtime/source change, or another state transition capable of
changing the decision.

Elapsed time alone does not require expensive reruns when state is unchanged.

## Historical Qualification Rule

If later audit proves that a prior "complete" or "HOLD" statement lacked required
coverage:

1. preserve the original raw prospective evidence;
2. retain valid narrow channel conclusions;
3. explicitly withdraw the broader completion claim;
4. record the missing receipts/capability gaps;
5. never backfill the omitted prospective search and call it contemporaneous.

## Completion Receipt

A final weekly decision receipt must list every required channel with one of:

- `PASS / ACTION`;
- `PASS / HOLD:<scope>`;
- `NOT APPLICABLE:<reason>`;
- `INCOMPLETE_COVERAGE:<gap>`;
- `BLOCKED_HEALTH:<gate>`.

Only a matrix with no incomplete or blocked required entries may authorize
roster-wide `COMPLETE / NO_ACTION` or `COMPLETE / ACTION_REQUIRED`.
