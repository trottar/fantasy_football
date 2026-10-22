# Week 8 M1b — Frozen-source first-lock preflight (first narrow slice)

**Status:** Read-only diagnostic control-root implementation candidate. It is not
M1b's six-provider refresh, prospective capture, phase receipt, drift recovery,
or automatic scheduler. It is not commissioned. Native v0.36 and M1a remain
unchanged; no ESPN writes or MC work.

## Scientific and source boundary

`tools/operations/weekly_operator_lock_preflight.py` resolves the user's full
owned P/D/K roster from the immutable, exact-copy six-provider `latest.json`
and the commissioned league-configured team name. It consults only the verified
snapshot `matchup_context.team_week` NFLverse schedules and parses `gameday` /
`gametime` as the same Eastern-clock forms used by the native
`src.availability_timing.player_lock_timing`. Output is aggregate, omits private
roster/league IDs, and cannot authorize any roster decision.

Require current season/week, six healthy providers, unique owned team, valid
individual positions/IDs, and an exact single immutable latest-snapshot copy.
Unknown NFL team or unparseable game time fail closed. A configured bye does not
by itself prove that NFLverse independently confirmed the bye: it is counted
separately and blocks whole-roster deadline completeness. Snapshot older than
two hours also fails closed. The initial 80-minute MC + live validation + user
action + safety lead remains a *planning* budget. Passed time budget is not
ESPN legality or prospective prediction authority. Previously locked players
are retained in the report; any passing future deadline is explicitly marked
partial-scope when previously locked records remain.

This is deliberately a *source inspection only*, not a source refresh. It must
not become the only calendar authority for a future automated M1b refresh;
independent live provider/first-lock evidence and verified bye source must be
integrated before promoting the controller to autonomous operation.

## Local invocation after source installation

```powershell
cd L:\Projects\fantasy_football
python -B .\tools\operations\weekly_operator_lock_preflight.py --project-root . --week 7
```

It is safe to run without touching the prospective capture or MC. A nonzero
exit is a **preflight blocker**, not permission to override freshness, byes,
individual locks, or deadlines.

## Follow-on M1b boundary

Confirm live snapshot's schedule field and owned-record coverage. Then integrate
fresh independently sourced first-lock verification **before** six-provider
refresh/capture launch, with immutable phase receipts and restart/recovery
policy. At most one material-drift recovery epoch. No new MC after uncertain
prior execution. Keep Saturday October 24 Week 7 prospective operations
protected above engineering. Do not infer complete M1b commissioning from this
first preflight.

`durable_memory_updated: true`
