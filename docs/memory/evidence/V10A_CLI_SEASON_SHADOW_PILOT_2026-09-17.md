# v1.0A CLI + SeasonGuiService Shadow-Pilot Evidence

<!-- FANTASY_V10A_CLI_SEASON_SHADOW_PILOT_20260917_V5:BEGIN -->
## Validation Evidence

Pre-state GitHub main: `dd9529746cd293387672eba0fe4d2b52da0032b5`

Authorized production-source scope:
- `fantasy.py` final command dispatch;
- `src/gui/season_service.py` read-only `source_health()` boundary;
- observability export surface.

No player/DST/K/market/closure/data-source or GUI-background path was modified.

Measured validation:
- targeted tests: PASS (91);
- full repository pytest: PASS (443);
- full compileall: PASS;
- strict memory health: PASS;
- `git diff --cached --check`: PASS;
- exact staged allowlist: PASS.

Paired pilot gate:
- CLI baseline median: 12650 ns;
- CLI observed median: 97950 ns;
- CLI incremental: 85300 ns;
- CLI output/state/RNG gate: PASS;
- SeasonGuiService baseline median: 3850 ns;
- SeasonGuiService observed median: 65150 ns;
- SeasonGuiService incremental: 61300 ns;
- SeasonGuiService output/state/RNG gate: PASS.

Privacy/non-interference:
- persistent sink: NO;
- arguments captured: NO;
- returned values captured: NO;
- exception messages captured: NO;
- observer failure can replace production result/exception: NO.

Evidence class:
`SHADOW PILOT ENABLED / TEST-VALIDATED / NON-PERSISTENT`.
<!-- FANTASY_V10A_CLI_SEASON_SHADOW_PILOT_20260917_V5:END -->
