# D-020 — v1.0A Production Integration Gate

<!-- FANTASY_D020_V10A_INTEGRATION_GATE:BEGIN -->
## Decision

Require an explicit shadow integration plan and paired non-interference/overhead
gate before broad production observability wiring.

Initial integration points must remain shadow-only, must not own persistent
sinks, and must not automatically emit/persist private evidence. Paired gate
runs begin baseline and observed calls from the same captured state, compare
outputs or exception types, compare state probes including Python RNG, restore
probe state after each pair, and evaluate both absolute and relative runtime
overhead where meaningful.

A passing contract-level gate authorizes only the next narrow shadow pilot. It
does not by itself commission broad CLI/GUI/service/subsystem instrumentation.
<!-- FANTASY_D020_V10A_INTEGRATION_GATE:END -->
