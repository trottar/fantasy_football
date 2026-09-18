# D-022 — v1.0A GUI Background-Task/Lifecycle Shadow Pilot

<!-- FANTASY_D022_V10A_GUI_LIFECYCLE_SHADOW:BEGIN -->
## Decision

Authorize the second production observability pilot only at NiceGUI page
lifecycle and the two existing background-task boundaries in `season_app.py`.

The observer may record generated session/page/task correlation, event kind,
duration, and exception type. It must not store raw client IDs, task
arguments/results, authenticated payloads, or exception messages.

The observer must not cancel work on page deletion. Stale-page task termination
is evidence, not GUI control policy. Passing this checkpoint does not authorize
player/DST/K/market/closure/data-source instrumentation.
<!-- FANTASY_D022_V10A_GUI_LIFECYCLE_SHADOW:END -->
