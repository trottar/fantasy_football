# Week 8 M1b — Independently corroborated first-lock calendar (second narrow source slice)

**Boundary:** read-only control-root tool and synthetic tests only. No automatic provider
refresh, prospective capture, MC, action certification, scheduler, runtime changes,
authenticated ESPN requests or ESPN writes. This does not finish M1b.

## Evidence question

The first M1b preflight observed an intact Thursday Week 7 snapshot with 16 owned
records, 15 corroborated nflverse kickoff records, one configured bye and no
unknown non-bye schedule. It properly returned `BLOCKED_STALE_SNAPSHOT` after
16,040 seconds of age. The bye was merely configured, not independently corroborated.

**Hypothesis:** an independently sourced complete league game schedule and an
independently published season bye table can validate the underlying kickoff/
bye classifications without treating a stale frozen owned roster as live.

`tools/operations/weekly_operator_calendar_evidence.py` makes **one unauthenticated
public ESPN NFL scoreboard GET** scoped to the exact 2026 NFL week and regular
season; validates the full 32-team partition into nonduplicated games and
published NFL-official byes; compares opponent and exact UTC kickoff to the
frozen nflverse `team_week` for every currently frozen owned P/D/K asset;
checks the league's configured bye-week table against the published NFL table;
checks frozen six-provider health and exact snapshot-byte identity; and
outputs only public-safe aggregates and SHA-256 identifiers. All event data are
read-only and retained only in memory. No raw private player/league IDs are printed.

The independently published bye assignment comes from the **NFL 2026 season
schedule release**: https://www.nfl.com/_amp/2026-nfl-schedule-release-every-team-bye-week.
This is a **pinned published season table**, not a live NFL.com fetch. The
ESPN scoreboard is freshly fetched public schedule information, not proof of
NFL official present-time rescheduling, live ownership, app legality or event
execution. Either schedule disagreement fails closed. Week 18 later flex games
can change; never infer ESPN-action authority from an earlier calendar match.

Run, after source-only local installation:

```powershell
cd L:\Projects\fantasy_football
python -B .\tools\operations\weekly_operator_calendar_evidence.py --project-root . --week 7
```

When the frozen snapshot is stale, the expected successful inspection state is
`CORROBORATED_CALENDAR_STALE_FROZEN_ROSTER` rather than a fresh roster or
refresh authorization. With a young snapshot, the state remains
`CORROBORATED_CALENDAR_LIVE_OWNED_ROSTER_STILL_REQUIRED`: public schedule plus
old roster is insufficient to authorize automatic refresh/capture/MC. A live
owned-roster/lock check with exact source provenance and transaction/waiver
cutoffs remains an additional M1b dependency. A clean calendar is evidence,
not action authority. `--week` must match the frozen snapshot week and real
public scoreboard epoch. Network failures and incomplete public games block.

## Next narrow integration sequence

1. Obtain a fresh **pre-refresh owned roster/lock** authority; couple it to
   public independently corroborated first-lock schedule and exact deadline
   before initiating an expensive six-provider refresh.
2. Integrate existing commissioned six-provider sync + immutable prospective
   capture behind a guarded explicit invocation. Write nonsecret immutable
   phase receipts with exact inputs/outputs and reject ambiguous replays.
3. Integrate bounded native nine-channel MC and current ESPN state reconciliation;
   permit at most one new material-drift epoch, with no repeat of completed or
   uncertain expensive work.
4. Advance separately into the complete action certification/portfolio gate;
   leave all ESPN writes subject to explicit human approval.

Saturday October 24 Week 7 prospective capture and nine-channel MC remain
higher priority than any source-only checkpoint. Never backfill post-lock
prospective predictions or label historical observations prospective.

`durable_memory_updated: true`
