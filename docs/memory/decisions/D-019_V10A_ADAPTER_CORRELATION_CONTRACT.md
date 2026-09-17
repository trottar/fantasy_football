# D-019 — v1.0A Adapter / Correlation Contract

<!-- FANTASY_D019_V10A_ADAPTER_CORRELATION:BEGIN -->
## Decision

Adopt thin opt-in observability adapters over the existing `RunContext` and
structured-event contracts rather than creating a second correlation model.

Correlation hierarchy is represented by immutable run/action IDs and
`parent_action_id`. CLI, service, background-task, and subsystem boundaries
construct evidence only. They do not own sinks, persist events, alter control
flow, or change random streams.

P/D/K remain distinct specialist channels: direct nested transitions between
player, DST, and kicker adapters are invalid; complete-roster/root contexts may
enter each channel independently.
<!-- FANTASY_D019_V10A_ADAPTER_CORRELATION:END -->
