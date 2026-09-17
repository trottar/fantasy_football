# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Phase 0 final lineage: **COMPLETE**
- Active development series: **v1.0A observability**
- Exact next slice: **failure-bundle contract**

## v1.0A — Diagnostics / Observability Substrate

Completed:
- [x] architecture/contract adopted
- [x] immutable run/action context
- [x] structured event schema/registry
- [x] human + machine sinks
- [x] provenance/config/input hashing
- [x] invariant registry/results
- [x] privacy/redaction primitives
- [x] local snapshot bundle contract
- [x] exact-byte replay verification/loading
- [x] bounded structural diff contract

Next:
- [ ] failure-bundle contract

Then:
- [ ] subsystem adapters: player / DST / K / lineup / market / closure
- [ ] CLI/service/background-task correlation
- [ ] GUI event emission/integration
- [ ] diagnostic overhead/non-interference benchmarks
- [ ] v1.0A commissioning criteria

Production call-site event emission remains deferred.

<!-- FANTASY_ROADMAP_V10A_FAILURE_BUNDLE_20260917:BEGIN -->
## v1.0A failure-bundle checkpoint

- [x] bounded privacy-safe failure-bundle contract
- [x] project-file modification state separated from runtime side effects
- [x] exact-byte integrity verification
- [ ] subsystem adapter contracts
- [ ] CLI/service/background-task correlation
- [ ] GUI event emission/integration
- [ ] diagnostic overhead/non-interference benchmarks
- [ ] v1.0A commissioning gate

Next narrow checkpoint: subsystem adapter contracts +
CLI/service/background-task correlation. Automatic production emission remains
disabled.
<!-- FANTASY_ROADMAP_V10A_FAILURE_BUNDLE_20260917:END -->

<!-- FANTASY_ROADMAP_V10A_ADAPTERS_CORRELATION_20260917:BEGIN -->
## v1.0A adapters/correlation checkpoint

- [x] subsystem adapter contracts
- [x] CLI/service/background-task correlation contracts
- [x] P/D/K observability channel separation guard
- [ ] production integration design
- [ ] diagnostic overhead/non-interference benchmark gate
- [ ] GUI event emission/integration
- [ ] v1.0A commissioning gate

Next narrow checkpoint: production integration design + overhead/non-interference
benchmark gate before broad instrumentation.
<!-- FANTASY_ROADMAP_V10A_ADAPTERS_CORRELATION_20260917:END -->

<!-- FANTASY_ROADMAP_V10A_INTEGRATION_GATE_20260917:BEGIN -->
## v1.0A integration-gate checkpoint

- [x] production integration surface map
- [x] observer-only shadow defaults
- [x] paired result/exception non-interference gate
- [x] Python RNG/custom state-probe comparison and restoration
- [x] absolute/relative overhead budget contract
- [ ] narrow CLI + SeasonGuiService shadow-integration pilot
- [ ] GUI/background lifecycle integration
- [ ] player/DST/K/market/closure/data-source integration
- [ ] v1.0A commissioning gate

Next narrow checkpoint: CLI command boundary + SeasonGuiService shadow pilot.
No persistent sink or broad automatic emission is enabled.
<!-- FANTASY_ROADMAP_V10A_INTEGRATION_GATE_20260917:END -->
