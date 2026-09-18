# v1.0A GUI Background-Task/Lifecycle Shadow-Pilot Evidence

<!-- FANTASY_V10A_GUI_LIFECYCLE_SHADOW_PILOT_20260917_V2:BEGIN -->
## Validation Evidence

Pre-state GitHub main: `eb7fc236a61f50459397cf3e2f58cd1cdbb1091b`

Authorized production-source scope:
- `src/gui/season_app.py` only;
- new observer-only `src/observability/gui_shadow.py`;
- focused tests/probe and durable memory.

No player/DST/K/market/closure/data-source or service/CLI behavior was changed.

Measured validation:
- targeted tests: PASS (107);
- full repository pytest: PASS (452);
- full compileall: PASS;
- strict memory health: PASS;
- `git diff --cached --check`: PASS;
- prior CLI/SeasonGuiService paired probe: PASS;
- GUI lifecycle paired probe: PASS;
- GUI baseline median: 690700 ns;
- GUI observed median: 810650 ns;
- GUI incremental: 119950 ns;
- cancellation propagation: PASS;
- stale-page result preservation: PASS.

Privacy/non-interference:
- persistent sink: NO;
- raw NiceGUI client ID captured: NO;
- task arguments/results captured: NO;
- exception messages captured: NO;
- page deletion changes task control flow: NO.

Evidence class:
`GUI LIFECYCLE SHADOW ENABLED / TEST-VALIDATED / NON-PERSISTENT`.
<!-- FANTASY_V10A_GUI_LIFECYCLE_SHADOW_PILOT_20260917_V2:END -->
