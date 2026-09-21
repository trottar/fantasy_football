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

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_2:BEGIN -->
## v1.0A implementation checkpoint 2

Implemented slice:
- `src/observability/sinks.py`
  - explicit `EventSink` protocol;
  - thread-safe in-memory sink;
  - append-only JSONL machine sink;
  - concise human-text sink with payload omitted by default;
  - explicit fanout and batch emission helpers.
- `src/observability/provenance.py`
  - exact-byte SHA-256;
  - canonical semantic JSON SHA-256;
  - file and JSON-file hashing;
  - release-version reader;
  - Git HEAD + tracked-dirty provenance with untracked files ignored;
  - frozen `SourceProvenance` compatible with `RunContext`;
  - `collect_provenance()` returns hashes/identity only, never file contents.

No production call site emits events yet. No global logger/sink is installed. Persistent sinks are not wired to private/authenticated runtime data before the redaction contract exists.

Validation:
- targeted observability tests: PASS (22);
- full pytest: PASS (375);
- full compileall: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- sink/provenance RNG non-interference: PASS;
- human sink default payload omission: PASS;
- canonical JSON order-independence and exact-byte sensitivity: PASS;
- Git provenance dirty/untracked behavior: PASS;
- provenance-content non-disclosure test: PASS.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_2:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_3:BEGIN -->
## v1.0A implementation checkpoint 3

Implemented slice:
- `src/observability/invariants.py`
  - immutable invariant definitions/results/registry;
  - explicit `PASS`, `FAIL`, `SKIP`, `ERROR` states;
  - architecture-level physics, authority, causality, league-state, separation,
    and GUI lifecycle invariant names;
  - context correlation without production enforcement;
  - safe error results record exception type, not raw exception text.
- `src/observability/redaction.py`
  - conservative recursive key redaction;
  - inline Authorization/cookie/ESPN secret pattern redaction;
  - caller-supplied exact-value replacement;
  - binary and recursion-depth conservative fallbacks;
  - event-dictionary redaction without mutating the original event;
  - caller-keyed HMAC pseudonymization for correlation-safe identifiers.

No existing sink automatically redacts or persists private runtime data. No
production call site emits observability events. Integration remains deferred.

Validation:
- targeted observability tests: PASS (38);
- full pytest: PASS (391);
- full repository compileall: PASS;
- strict memory-health check: PASS;
- `git diff --check`: PASS;
- exact staged allowlist: PASS;
- invariant/redaction RNG non-interference: PASS;
- deep-copy/non-mutation redaction tests: PASS;
- secret-bearing exception-message non-disclosure: PASS.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_3:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_4:BEGIN -->
## v1.0A implementation checkpoint 4

Implemented:
- `snapshots.py`: atomic local replay-evidence bundles with redaction before
  persistence and exact-byte member manifests;
- `replay.py`: bundle integrity verification and immutable evidence loading;
- `diff.py`: bounded, redacted-by-default structural diffs.

Replay in this checkpoint is evidence loading, not football/MC execution.
Production automatic capture remains disabled.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_4:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_5:BEGIN -->
## v1.0A implementation checkpoint 5

Implemented `failure_bundle.py`: atomic local bounded failure bundles,
privacy-conservative exception summaries, redacted structured
state/reproduction/effects, bounded event/invariant tails, exact-byte integrity
verification, and immutable loading.

Failure bundles are explicit caller-owned evidence. No automatic capture,
exception recovery policy, or production control-flow integration is enabled.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_5:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_6:BEGIN -->
## v1.0A implementation checkpoint 6

Implemented typed subsystem adapter and correlation contracts. CLI, service,
background-task, and subsystem boundaries derive child `RunContext` values and
construct generic action start/complete/error events without owning sinks or
performing automatic persistence. Direct player/DST/kicker cross-channel
nesting is rejected at the observability contract boundary.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_6:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_7:BEGIN -->
## v1.0A implementation checkpoint 7

Implemented a shadow integration map plus non-interference/overhead gate before
production call-site instrumentation. The plan names real CLI, season-service,
GUI background-task, player, DST, kicker, trade, closure, and data-source source
surfaces. Every default point is shadow-only, non-persistent, and non-auto-emitting.

The paired benchmark restores captured probe state between baseline and observed
calls and after each pair; compares return/exception behavior and state-channel
outcomes; and applies a hardware-tolerant absolute/relative overhead budget.
This checkpoint changes no production call site.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_7:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_8:BEGIN -->
## v1.0A implementation checkpoint 8

Enabled the first narrow production shadow pilot. `fantasy.py` routes only the
final command dispatch through a bounded in-memory observer.
`SeasonGuiService` owns one bounded in-memory recorder and instruments only the
read-only `source_health()` method. Events retain boundary/correlation,
duration, and exception type only; they do not retain arguments, return values,
authenticated payloads, or exception messages.

Observer failures are explicitly non-interfering: the wrapped production call
still executes and its result/exception wins. No persistent sink is enabled.
Player/DST/K/market/closure/data-source paths remain untouched.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_8:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_9:BEGIN -->
## v1.0A implementation checkpoint 9

Enabled the narrow GUI background-task/lifecycle shadow pilot in
`src/gui/season_app.py`. A dedicated `gui_shadow.py` module records bounded
in-memory page/session/task correlation.

Instrumented call paths are limited to:
- selected-MC `background_tasks.create(...)`;
- the MC progress-pump coroutine while preserving its existing create/cancel/await
  semantics;
- page mount, initial client connection, disconnect, and final client deletion.

Task completion after page deletion emits `gui.lifecycle.violation` evidence but
does not alter control flow. No persistent sink or football/data-source
instrumentation is enabled.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_9:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_10:BEGIN -->
## v1.0A implementation checkpoint 10 candidate

The next narrow candidate adds an outer shadow boundary at
`src/season_snapshot.py::sync_season_snapshot` using the existing subsystem
adapter/correlation contracts and a bounded in-memory recorder.

Only outer boundary identity/correlation, duration, and exception type are
retained. Function arguments, authenticated/provider payloads, returned snapshot
contents/paths, and exception messages are not recorded. Provider internals,
persistent sinks, football channels, market behavior, and closure remain
separately gated.

A deterministic no-network paired probe compares successful outputs, exception
types, filesystem side effects, Python RNG state, privacy markers, and bounded
overhead from identical captured state. The retained candidate passed targeted
pytest, the paired probe, full pytest, compileall, and candidate-local diff /
allowlist inspection. Local source validation remains separate from control-root
memory and runtime synchronization remains a later gate.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_10:END -->

<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_10_COMMISSIONED:BEGIN -->
## v1.0A implementation checkpoint 10 commissioned

The data-source season-sync outer shadow boundary is commissioned in the
`v0.36-repack1` runtime from repository checkpoint
`24a7e57794b0325510349ae163cd36b2f6c19070`.

The commissioned runtime passed exact source-identity guards, dedicated runtime
tests, deterministic paired behavior/privacy/RNG/filesystem/overhead probing,
full pytest, compileall, and final runtime/rollback identity verification. The
observer remains bounded in memory, fail-open, argument/return/message-free,
provider-internal-free, and non-persistent.

Checkpoint 10 does not authorize closure, P/D/K, market/behavior, or persistence
expansion. Phase 1B closure instrumentation is the next separately gated surface.
<!-- FANTASY_DIAGNOSTICS_OBSERVABILITY_IMPLEMENTATION_V10A_10_COMMISSIONED:END -->
