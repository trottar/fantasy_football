# D-013 — v1.0A Context/Event Contract

<!-- FANTASY_D013_V10A_CONTEXT_EVENT_CONTRACT:BEGIN -->
## Decision

Adopt a small immutable stdlib-only observability core before any subsystem
integration.

The initial contract consists of:
1. frozen `RunContext`;
2. schema-versioned `StructuredEvent`;
3. immutable `EventRegistry`;
4. reserved generic run/action and GUI lifecycle event names.

This checkpoint deliberately does **not** emit events from football, market, MC,
CLI, service, background-task, or GUI production paths. That separation makes
the observer contract testable before integration and preserves the commissioned
v0.36-repack1 semantics and random streams.
<!-- FANTASY_D013_V10A_CONTEXT_EVENT_CONTRACT:END -->
