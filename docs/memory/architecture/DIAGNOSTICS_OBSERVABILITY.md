# Diagnostics and Observability Architecture

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_V1:BEGIN -->
## Status

`v1.0A` is the cross-cutting diagnostics/observability substrate for all later 1.X work. It is engineering infrastructure around the physics, not a physics retune.

Implementation against football/application source remains gated on freezing the final 0.X lineage. Design, static surface audit, schemas, and diagnostic tooling may proceed before that freeze.

## Design objective

Every significant subsystem must expose enough structured state to answer:

1. What exact state/input/config/source produced this result?
2. What computation or state transition occurred?
3. What uncertainty and random stream were used?
4. Which invariant checks passed or failed?
5. What happened immediately before a failure?
6. Can the run or decision be replayed/diffed without reconstruction from chat or screenshots?

Target flow:

```text
input state
  -> typed computation
  -> typed output
  -> structured diagnostics
  -> invariant checks
  -> replayable evidence
```

Diagnostics are observers. They must not alter football utility, manager behavior, random draws, recommendation authority, or GUI business logic.

## Core modules

The eventual source substrate should be modular rather than one monolithic `diagnostics.py`:

```text
observability/
    context.py
    events.py
    sinks.py
    logging.py
    snapshots.py
    invariants.py
    provenance.py
    replay.py
    diff.py
    failure_bundle.py
    redaction.py
    registry.py
    gui.py
```

The existing `src/diagnostics.py` remains a useful data-coverage diagnostic and should not be opportunistically rewritten merely to create this substrate.

## Run context

Every meaningful run/action should support a common immutable context where applicable:

- `run_id`
- timestamp
- model/release version
- source commit/hash
- week
- decision time
- `data_as_of`
- subsystem
- scenario/counterfactual ID
- random seed and/or CRN group ID
- config hash
- input snapshot hash
- parent run/action ID

Context propagation must work across player, DST, kicker, roster, market, closure, CLI, background tasks, and GUI service boundaries.

## Event model

Use machine-readable structured events (JSONL or equivalent) plus concise human-readable console/log output.

Minimum event envelope:

```text
timestamp
level
event_name
subsystem
run_id
correlation/action ID
payload
source/version provenance
```

Levels:
- `NORMAL` — operational milestones and decisions
- `DIAGNOSTIC` — component-level summaries
- `TRACE` — detailed search/MC/lifecycle flow
- `AUDIT` — decision-critical provenance and immutable evidence

Subsystem namespaces remain explicit: `player`, `dst`, `k`, `lineup`, `waiver`, `trade`, `behavior`, `data_source`, `closure`, and `gui`.

## Physics/channel invariants

Diagnostics must preserve and eventually check:
- `P ⊕ D ⊕ K`
- players compare only to players
- DST compares only to DST
- K compares only to K
- `screen != authority`
- prediction frozen before outcome
- decision information time <= decision time
- paired comparisons use CRNs where required
- dropped players remain in league state
- football utility is separate from manager behavior
- raw observations remain separate from derived/calibrated state

Invariant failure is evidence and should emit an explicit event/failure bundle.

## Snapshot and replay contract

Important runs should optionally emit a compact local replay package:

```text
run_manifest.json
inputs_manifest.json
config_snapshot.json
decision_snapshot.json
events.jsonl
summary.json
```

Private/raw authenticated inputs remain local. Public durable memory stores sanitized summaries and hashes.

## Failure bundles

Meaningful exceptions should capture, subject to privacy/redaction:
- exception type/message/stack
- run context
- last bounded diagnostic events
- source/version/config/input hashes
- subsystem state summary
- active invariant results
- reproduction command/instructions
- GUI lifecycle context when relevant

The bundle must distinguish project-file modification state from temporary/runtime side effects.

## GUI diagnostics are first-class

GUI diagnostics are part of v1.0A, not deferred until the integrated GUI phase.

The GUI event namespace should cover at minimum:

```text
gui.app.start
gui.app.stop
gui.client.connect
gui.client.disconnect
gui.page.mount
gui.page.unmount
gui.action.start
gui.action.complete
gui.action.error
gui.task.spawn
gui.task.cancel
gui.service.start
gui.service.complete
gui.service.error
gui.state.read
gui.state.write
gui.render.start
gui.render.complete
gui.refresh.request
gui.refresh.complete
gui.notification
gui.lifecycle.violation
```

Useful correlation fields:
- `session_id`
- redacted/ephemeral `client_id`
- `page_id`
- `action_id`
- `task_id`
- `service_call_id`
- parent run/action ID

GUI lifecycle invariants include:
- no UI mutation after client/page deletion or unmount;
- background tasks have an owning session/action and explicit cancellation behavior;
- service completion does not blindly write into a stale UI context;
- refresh/render callbacks expose start/end/error and duration;
- exceptions crossing service/controller/UI boundaries retain correlation IDs.

This is specifically intended to make failures such as historical `Client has been deleted but is still being used` classifiable from lifecycle evidence rather than screenshots or guesswork.

GUI diagnostics must not contain hidden recommendation/football business logic. The GUI remains a consumer/orchestrator of typed services and observability.

## Performance diagnostics

Capture timings where useful without changing semantics: data-source latency, MC/search duration, queue/wait time, service-call duration, GUI action duration, render/refresh duration, and failure/retry counts.

## Redaction/privacy

Structured diagnostics must support explicit redaction before persistence or publication. Secrets, ESPN cookies, SWID, `espn_s2`, private account identifiers, and raw authenticated payloads remain local.

## Commissioning rule

A significant new subsystem is not fully commissioned until, where applicable:
1. structured events exist;
2. provenance/context propagation is tested;
3. relevant invariants are testable;
4. failure output is actionable;
5. replay/diff evidence is sufficient for debugging;
6. GUI-facing behavior has lifecycle/action/service diagnostics;
7. diagnostic output itself is tested for privacy/redaction;
8. diagnostics do not alter model results.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_V1:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_1:BEGIN -->
## v1.0A implementation checkpoint 1

Implemented contract:
- `src/observability/context.py`
  - frozen `RunContext`;
  - run/action correlation;
  - timezone-aware timestamps normalized to UTC;
  - release/source/config/input provenance fields;
  - week / decision-time / data-as-of / scenario / seed / CRN fields;
  - child-action derivation without mutating the parent context.
- `src/observability/registry.py`
  - immutable event registry;
  - `NORMAL`, `DIAGNOSTIC`, `TRACE`, `AUDIT` levels;
  - generic run/action events;
  - GUI lifecycle/action/service/task/state/render/refresh event names reserved exactly at the contract layer.
- `src/observability/events.py`
  - schema version 1;
  - frozen structured event envelope;
  - recursively immutable JSON-safe payload;
  - deterministic JSON rendering;
  - registry, subsystem, and required-payload validation.

No sink, logger, adapter, invariant engine, replay layer, or production call site is introduced by this checkpoint.

Validation:
- targeted observability tests: PASS (11);
- full pytest: PASS (364);
- full repository compileall: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- no existing football/model/application source file modified;
- context/event construction RNG non-interference tests: PASS;
- caller payload immutability/deep-freeze tests: PASS.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_1:END -->
