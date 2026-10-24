# M1b — Installed native six-provider observer adapter (source-only candidate)

**Checkpoint:** `week8_m1b_native_sync_observer_adapter_20261024_v1`.
**Predecessor:** verified remote `54a083e74ebc355d074426a25e4ed13a25ec915a`.
**Current gate:** candidate, NOT local applied, staged, published, commissioned, or live tested.

## Narrow evidence and binding

On October 24 the read-only preflight verified the installed `v0.36-repack1`
`src/season_snapshot.py` Git blob is `eabcbee3ea2a06e7f68dfea5cbe0e4a2eb768609`.
The installed `fantasy.py` blob is `dd3a0a2b39ea1c6b424e71f6a11273f2503ccc64`.
The separately published duration observer is Git blob
`da0250350e0a6419455412af172887960f11025e`.
No control-root `src/season_snapshot.py` copy is required or treated as authority.
The native callable's five argument names and both optional provider switches
were checked in the published native entrypoint; the adapter rechecks source.

## Narrow source-only implementation

`weekly_operator_native_sync_adapter.py` offers an **opt-in Python function**
`observe_approved_sync_once`, with no executable CLI/scheduler and no import-time
provider calls. It refuses absent explicit execution approval; before invoking
anything, it checks the exact commissioned version, installed CLI/sync and
published observer source blobs. It then loads the native runtime module from
that exact installed source and runs the sync exactly once with `week`, default
local secrets, the commissioned snapshot path, `include_sleeper=True` and
`include_nfl=True`. The published observer owns monotonic duration and exact
six-provider snapshot binding. The adapter rechecks source identity afterward.
The result is an **in-memory non-authoritative measurement**. The existing
`persist_private()` is a distinct explicit step; installation never persists.

The adapter does not retry failed provider calls, launch native MC, construct a
prospective capture, submit ESPN actions, modify v0.36, or infer transaction
cutoffs. Synthetic injection exists for tests only and does not prove an actual
provider was consulted. A checksum is byte integrity, not refresh authorization.
No component may treat an in-memory measurement as permission to run MC or to
certify a roster decision (`screen != authority`).

## Evidence and deferred authorization

The Week 7 Saturday six-provider refresh, immutable capture and MC are protected
calendar operations. They must occur prospectively before affected verified
locks; any missed gate cannot be backfilled. This source checkpoint must not
compete with that work, and no actual sync is authorized by merely installing
or invoking a generic package. An explicit independent operational decision
must first verify eligibility, single-epoch ownership, time budget, and user
approval. Per-candidate waiver and trade action-screen semantics and M2
complete-roster certification remain separate blocked producers.

## Checkpoint procedure

One guarded source-only local apply of `CURRENT.md`, this record, the adapter and
synthetic regression tests; targeted tests, compileall, strict memory health;
then independent exact isolated staging, full suite, explicit separate guarded
publication and read-only remote verification. No runtime changes or live
commissioning are claimed.

`durable_memory_updated: true`
