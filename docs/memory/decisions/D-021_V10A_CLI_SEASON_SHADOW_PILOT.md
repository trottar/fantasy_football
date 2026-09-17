# D-021 — v1.0A CLI + SeasonGuiService Shadow Pilot

<!-- FANTASY_D021_V10A_CLI_SEASON_SHADOW:BEGIN -->
## Decision

Authorize and commission only the first narrow in-memory production shadow
pilot at the final CLI dispatch and the read-only
`SeasonGuiService.source_health()` method.

The pilot records bounded boundary/correlation/timing/error-type evidence only.
It owns no persistent sink and stores no command arguments, returned values,
authenticated payloads, or exception messages. Observer failures must never
replace production behavior.

Passing this pilot does not authorize player/DST/K/market/closure/data-source or
broad GUI instrumentation. Expansion remains perturbative and gated.
<!-- FANTASY_D021_V10A_CLI_SEASON_SHADOW:END -->
