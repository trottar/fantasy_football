# Week 8 M1b — Pre-refresh live owned-roster/lock evidence (third narrow slice)

**Status:** source-only read-only diagnostic candidate; not runtime commissioned and
not the automatic six-provider refresh/capture controller. Existing M1a and the
first two M1b calendar gates are unchanged.

## Question and fresh Week 7 evidence

M1b independent calendar checkpoint `0964d0a4fd4b252ef83a958d10381375119866e5`
was remote verified. Its private read-only October 22 Week 7 acceptance measured
14 NFL games, four official byes, 16 owned records (15 corroborated kickoff,
one corroborated bye), and frozen snapshot age 22,930 seconds. Status was
`CORROBORATED_CALENDAR_STALE_FROZEN_ROSTER`. This proves source calendar joins,
**not** that the owned roster/locks or ESPN app legality are currently valid.

The next narrow missing observation is fresh owned-player lock scope *before*
a costly provider refresh: `tools/operations/weekly_operator_live_lock_evidence.py`.
It uses **one unauthenticated public ESPN NFL scoreboard GET** followed by
**one authenticated private ESPN league GET**, normalized by the unchanged
`src.data_sources.espn_league` reader. It holds raw private material in memory,
never prints player IDs, names, league IDs, cookies or raw authenticated data,
and never writes runtime/private artifacts. Synthetic tests inject plain normalized
state; there are no network calls in test execution.

### Evaluation boundary

- Verify unique immutable frozen snapshot and commissioned root; compare current
  scoreboard with frozen nflverse per-team opponent/exact kickoff and the
  published 2026 NFL byes and league configuration using the *already published*
  calendar comparison module.
- Compare the fresh normalized league identity, season/week, exact owned team,
  owned ESPN asset identity and position/team/slot/injury/lock fields to frozen
  ownership. Any added, removed or changed owned asset is **material new-capture
  evidence**, not permission to rerun a past MC or rewrite a frozen capture.
- For each *live owned* P/D/K record, join independent public kickoffs or
  corroborated bye against frozen full-team nflverse schedule; classify elapsed
  games, ESPN-explicit future locks, confirmed future unlocked assets, and
  unknown lock flags separately. Missing or nonboolean future lock data fail
  closed. Do not treat an elapsed Thursday kickoff as prospective on Saturday.
- Require source retrieval chronology: one public fetch no older than 120s,
  one authenticated roster GET no older than 60s; reject reversed ordering.
- Report earliest still-future **owned unlocked** kickoff and conservative
  80-minute MC/validation/approval/safety budget. A budget pass is only an
  observation; refresh margin, waiver/trade cutoff, and app legality are NOT
  certified or inferred.

### Public-safe statuses

`READONLY_LIVE_CALENDAR_LOCK_CORROBORATED`,
`READONLY_PARTIAL_SCOPE_CALENDAR_LOCK_CORROBORATED`,
`READONLY_LIVE_ROSTER_DRIFT_NEW_CAPTURE_REQUIRED`,
`BLOCKED_UNKNOWN_LIVE_LOCK`, `BLOCKED_NO_FUTURE_UNLOCKED_OWNED_GAME`,
`BLOCKED_INSUFFICIENT_PROTECTED_LEAD`, or a fixed, fail-closed `LIVE_LOCK_BLOCKED`.
All outputs retain `refresh_authority=NONE`, `capture_authority=NONE`,
`action_authority=NONE`, `automatic_refresh_or_capture=false` and
`espn_writes=false`. Even an apparently clean live preflight does not establish
an ESPN claim/transaction deadline or authorize MC.

Run after local apply/publication with existing private ESPN secrets only:

```powershell
cd L:\Projects\fantasy_football
python -B .\tools\operations\weekly_operator_live_lock_evidence.py --project-root . --week 7
```

Do not use this read-only diagnostic as the protected Saturday October 24
full six-provider refresh/capture/MC command. The calendar gate remains
independent from roster freshness; historical prospective state stays frozen.

## M1b continuation

After private acceptance, implement explicit per-action and transaction deadline
source verification with bounded refresh margin; only then connect the existing
commissioned six-provider sync and immutable prospective capture with exact
private phase receipt identities. Next integrate existing native nine-channel MC
with restart-safe finite one-epoch material-drift recovery. M2 action certification,
portfolio consequences and optional M3 scheduling follow separately.

`durable_memory_updated: true`
