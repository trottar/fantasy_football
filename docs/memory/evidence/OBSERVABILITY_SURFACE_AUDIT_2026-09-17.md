# Observability Surface Audit — 2026-09-17

<!-- FANTASY_OBSERVABILITY_SURFACE_AUDIT_V1:BEGIN -->
## v1.0A static diagnostic-surface audit

Timestamp: `2026-09-17T02:38:22.205156-04:00`

Audited roots:
- `L:\Projects\fantasy_football`
- `L:\Projects\fantasy_football\fantasy_season_v0_36`

This audit is static only. It does not execute football/model/application code. It inventories existing diagnostic/logging/error/async/GUI surfaces to guide modular v1.0A integration after final 0.X freeze.

```text
# v1.0A Diagnostic Surface Audit

## L:\Projects\fantasy_football
- Python source files: 0
- GUI Python files: 0
- diagnostics-named files: none
- print calls: 0
- logging-like calls: 0
- try blocks: 0
- raises: 0
- async functions: 0
- task creation calls: 0
- GUI logging-like calls: 0
- GUI try blocks: 0
- GUI async functions: 0
- GUI task creation calls: 0

## L:\Projects\fantasy_football\fantasy_season_v0_36
- Python source files: 61
- GUI Python files: 10
- diagnostics-named files: src/diagnostics.py
- print calls: 273
- logging-like calls: 5
- try blocks: 148
- raises: 128
- async functions: 25
- task creation calls: 3
- GUI logging-like calls: 0
- GUI try blocks: 39
- GUI async functions: 25
- GUI task creation calls: 3

## Interpretation boundary

Static surface inventory only. Counts identify integration surfaces; they do not prove logging quality, correctness, lifecycle safety, or runtime behavior.


```

Interpretation boundary: counts identify candidate instrumentation surfaces; they do not prove runtime safety, logging quality, or GUI lifecycle correctness.
<!-- FANTASY_OBSERVABILITY_SURFACE_AUDIT_V1:END -->
