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
