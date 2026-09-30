# Week 4 Pre-Lock Status Gate — 2026-09-29

---
evidence_type: prospective_prelock_status_gate
season: 2026
week: 4
runtime: v0.36-repack1
source_checkpoint: ed2a3bf430f4d08a7eb3eb5925ddbfa7b7d8eb15
trade_search_run: false
transaction_submitted: false
persistence_active: false
football_model_tuning: false
---

## Purpose

Record the fresh Week 4 decision-time availability gate required after the
week-open capture and first trade-search HOLD decision.

The gate refreshes live source state, freezes one additional prospective capture,
computes evidence-conditioned current-week availability/workload state, and
re-optimizes the expected lineup without rerunning trade search.

## Fresh Snapshot and Capture

Accepted carrier:
`week4_prelock_status_capture_20260929_v1.ffpkg`.

Fresh snapshot:

`data/season_snapshots/20260930T024153Z/snapshot.json`

SHA-256:
`782f2549ca254c6fd5810c4d3f3ab28929eebbdb67e48c03aecaf1be7d4f6cfb`

Snapshot canonical SHA-256:
`911f35615890adee4a113a9a2addc8724ba1d58f00bf49f1030d7d84c575b58b`

Fresh prospective capture:

`data/season_predictions/closure/pregame_2026_w04_20260930T024216Z.json`

SHA-256:
`43f59678af69935bcfb6a1de84d8ae823ccdd4de7ebf738e43651e7afb8343fe`

Canonical payload SHA-256:
`8e5507b49c7615e95bfd1e60301488aa03cd27700295bbc93985ae8c375f47a2`

Validation:

- source health: `6/6 PASS`;
- measurement contract:
  `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- capture integrity: PASS;
- pre-data firewall: PASS;
- matchup players: 32;
- league players: 174;
- specialists: 64;
- DST: 32;
- K: 32;
- baseline Week 4 evidence preserved: `4/4`;
- Week 3 captures preserved: `4/4`;
- pre-existing Week 4 captures preserved: `1/1`;
- exactly one new Week 4 capture;
- observability log evidence unchanged;
- persistence active: false.

## Puka Availability State

Frozen baseline:

- status: QUESTIONABLE `[ESPN]`;
- active probability: 75%.

Fresh decision-time state:

- status: QUESTIONABLE `[ESPN]`;
- active probability: 75%;
- probability delta: `+0.000`;
- full-workload probability given active: 65%;
- expected workload given active: 87.8%;
- evidence level: `STATUS_ONLY`;
- posterior method: `STATUS_PRIOR_FALLBACK`;
- practice source: none;
- practice sequence: none;
- status changed: false;
- source changed: false.

The fresh source state therefore does not show a status/probability transition.
The richer availability model does add a workload penalty conditional on playing.

## Expected Lineup

Fresh expected lineup:

- Lamar Jackson — QB;
- Ashton Jeanty — RB;
- Jeremiyah Love — RB;
- Puka Nacua — WR;
- Carnell Tate — WR;
- George Kittle — TE;
- Jakobi Meyers — FLEX;
- Harrison Butker — K;
- Lions D/ST — DST.

The lineup signature is unchanged from the frozen baseline.

Fresh totals:

- nominal: 125.78;
- availability/workload weighted: 117.33.

Puka:

- nominal projection: 20.51;
- expected points: 13.50.

Roster states below 95% active probability:

1. Baker Mayfield — OUT — 0%;
2. Josh Jacobs — EXEMPT — 0%;
3. Mark Andrews — QUESTIONABLE — 75%;
4. Puka Nacua — QUESTIONABLE — 75%.

## Decision Boundary

- Lineup changed: false.
- Trade search rerun: false.
- Transaction submitted: false.
- Football/model tuning: false.
- Persistence activation: false.
- Production-source write: false.
- Repository write: false.

**Availability/lineup gate: HOLD / NO LINEUP TRANSACTION FROM THIS GATE.**

This status gate does not establish roster-wide HOLD. Later workflow audit found
that the complete weekly action matrix had not been required before the broader
decision interpretation.

Weekly roster decision state is therefore `INCOMPLETE_COVERAGE` pending the
orchestration repair. The 117.33 expected lineup total reflects the richer
current-week workload state, not a v0.X calibration change.

## Audit

Local pre-lock audit:

`data/season_decisions/week4_prelock_status_gate_20260930T024217Z.json`

SHA-256:
`8366806c8faefc127abfc8793f1704c0880957d81f57949dc43db0b84dbe987a`

## Next Action

This record's prior Week 3-closure next action is superseded by the blocking
weekly decision-orchestration audit.

Make the memory completion/health contract durable first, then repair and
commission the production weekly orchestrator. Only after a fresh complete
decision cycle may Week 3 closure resume.

If a material Week 4 status/practice update appears before an affected player's
lock, perform another fresh decision-time capture before acting.
