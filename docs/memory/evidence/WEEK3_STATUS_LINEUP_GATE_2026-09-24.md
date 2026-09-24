# Week 3 Status / Lineup Gate — 2026-09-24

## Purpose

Refresh Week 3 status and lineup state prospectively without rerunning expensive
decision channels unless new evidence makes them relevant.

## Fresh Prospective State

Fresh authenticated snapshot:

- UTC: `2026-09-24T15:51:01.149554+00:00`;
- path:
  `data/season_snapshots/20260924T155042Z/snapshot.json`;
- SHA-256:
  `440e061603867ce59192709c22cefdf52a6eb2f437b2a10ab08ee359b2980644`;
- season/week: `2026 / 3`;
- ESPN, NFL official, NFL official rosters, nflverse matchups,
  nflverse rosters, and Sleeper: **OK**.

Fresh immutable prospective capture:

- path:
  `data/season_predictions/closure/pregame_2026_w03_20260924T155122Z.json`;
- SHA-256:
  `721331684b8f354e9d534545190bfdd6c20acdbbb24e5664086e475f13a828f0`;
- measurement contract:
  `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- integrity: **PASS**.

Prior Sep 24 trade-search snapshot/capture remained unchanged.

## Availability / Practice State

Compared with the earlier Sep 24 prospective state:

- changed roster records: `0`;
- expected-lineup identity changed: `false`.

Players below 95% modeled active probability:

| Player | Pos | Status | Source | P(active) | Practice |
| --- | --- | --- | --- | ---: | --- |
| Josh Jacobs | RB | EXEMPT | NFL_OFFICIAL_ROSTER | 0.0% | none |
| Jakobi Meyers | WR | QUESTIONABLE | SLEEPER+ESPN | 75.0% | none |
| J.K. Dobbins | RB | QUESTIONABLE | SLEEPER+ESPN | 75.0% | none |
| Puka Nacua | WR | QUESTIONABLE | ESPN | 75.0% | none |

Josh Jacobs was on the bench and hard-unavailable.

## Lineup Reconciliation

Fresh expected-value lineup:

- QB: Lamar Jackson
- RB1: Ashton Jeanty
- RB2: Jeremiyah Love
- WR1: Puka Nacua
- WR2: Carnell Tate
- TE: George Kittle
- FLEX: Mark Andrews
- K: Harrison Butker
- DST: Lions D/ST

Totals:

- nominal projection: `123.30`;
- availability-weighted expected: `118.02`.

The lineup identity was unchanged from the prior prospective state.

One-player captured contingencies remained:

- Puka OUT -> Carnell Tate + Rashid Shaheed at WR, J.K. Dobbins at FLEX;
- Jakobi Meyers OUT -> current starters remain supported;
- J.K. Dobbins OUT -> Mark Andrews remains FLEX.

## Initial Gate Classifier

The first package reported:

`decision_relevant=true`

with sole reason:

`USER_ROSTER_KICKOFF_WITHIN_12H`

The triggering row was Josh Jacobs:

- lineup slot: BENCH;
- status: EXEMPT;
- P(active): `0%`;
- kickoff approximately 8.39 hours away.

The package had treated every roster player's near lock as consequential without
checking whether the player could affect the captured planned lineup or a
captured contingency.

This was a diagnostic/package classifier defect, not a football-state change.

Original status-gate audit:

- path:
  `data/season_decisions/week3_status_lineup_gate_20260924T155122Z.json`;
- SHA-256:
  `c944b29ff05e83b7116d224c69cf7997217d43b5cad4b0e98e49a15a830ed817`.

## Bounded Relevance Recovery

Recovery reclassified near-lock relevance using only the already captured state.

A near-lock row is consequential only when:

1. the player appears in the captured expected lineup or a captured contingency;
2. the player is not hard-unavailable; and
3. modeled active probability is greater than zero.

Measured result:

- consequential near-lock rows: `0`;
- ignored near-lock rows: `1`;
- ignored row: Josh Jacobs, BENCH / EXEMPT / `P(active)=0%`.

Recovered classification:

`decision_relevant=false`

Operational classification:

**HOLD / NO HEAVY CHANNEL RERUN**

Reason:

`NO_MATERIAL_TRIGGER_OBSERVED`

Corrected recovery audit:

- path:
  `data/season_decisions/week3_status_gate_relevance_recovery_20260924T163345Z.json`;
- SHA-256:
  `cb1752c1bbe88c3f750198ad059602b3cb2e69c87d2cf77d018836222207c317`.

Original snapshot, capture, and audit remained unchanged.

## Channel / Action Boundary

Not rerun:

- player add/drop MC;
- DST channel;
- kicker channel;
- trade search.

No transaction was submitted.

No football/model/application source changed.

## Next Gate

Maintain HOLD.

Trigger a new decision cycle only when:

- material status/practice evidence changes for Puka Nacua, J.K. Dobbins,
  Jakobi Meyers, or another consequential roster player; or
- a player in the planned lineup or captured contingency approaches a
  consequential lock/reveal window.

At that point:

`fresh sync -> fresh prospective capture -> decision`

A hard-unavailable bench player's approaching kickoff alone is not a decision
trigger.
