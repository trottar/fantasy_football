# D-024 — v1.0A Data-Source Season-Sync Shadow Pilot

**Status:** ACTIVE
**Accepted:** 2026-09-21

## Context

The next predeclared integration surface after the GUI lifecycle pilot is
`src/season_snapshot.py::sync_season_snapshot`, registered as
`subsystem.data_source.season_sync`.

This boundary handles authenticated ESPN league state, secondary public source
syncs, filesystem snapshot creation, and returned snapshot/path objects. It is
therefore privacy- and side-effect-sensitive.

## Decision

Authorize one outer shadow boundary around `sync_season_snapshot` only.

The observer may retain:

- generated run/action correlation;
- subsystem/boundary identity;
- start/complete/error event kind;
- duration;
- exception **type**.

It must not retain:

- `secrets_path` or other function arguments;
- ESPN cookies, SWID, `espn_s2`, league/private account identifiers;
- provider request/response payloads;
- returned snapshot contents;
- returned filesystem paths;
- exception messages;
- persistent runtime output.

Provider calls inside `sync_season_snapshot` remain uninstrumented in this slice.

## Non-Interference Gate

The pilot must demonstrate with private-data-free deterministic source stubs:

- successful return/output equivalence;
- exception-type equivalence and original exception propagation;
- identical filesystem side effects from the same captured state;
- Python RNG equivalence;
- bounded observer overhead;
- observer-internal failure does not replace production behavior;
- event output contains no argument, return-value, filesystem-path, or exception
  message marker.

## Validation Sequencing

After a tooling/package failure, resume from the last validated gate rather than
rerunning unrelated successful gates. Full pytest, compileall, repository
checkpointing, and runtime synchronization remain distinct later states.

## Scope Boundary

This decision does not authorize:

- individual ESPN/Sleeper/nflverse/NFL.com provider instrumentation;
- persistent sinks;
- player/DST/kicker instrumentation;
- market/manager-behavior instrumentation;
- closure instrumentation;
- football/model semantic changes.

Expansion remains perturbative and separately gated.
