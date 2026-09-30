# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Week 4 prospective week-open capture:
  **COMPLETE / VALID**
- Week 4 first player-channel trade-search cycle:
  **COMPLETE / HOLD / NO ACTIONABLE OR MUTUAL-GAIN OFFER**
- Week 4 immediate calendar gate:
  **PRE-LOCK AVAILABILITY RECHECK**
- Phase 1E persistence controller:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED / PERSISTENCE DISABLED**
- Phase 1E persistent activation:
  **SEPARATELY GATED / NOT AUTHORIZED**
- Persistent runtime evidence: **DISABLED**
- Phase 2 prospective Data/MC collection: **ACTIVE / CONCURRENT**
- Week 3 closure: **PENDING / DEFERRED BEHIND WEEK 4 CALENDAR GATE**
- No observed 2026 outcome has tuned v0.X.

## Week 4 Prospective Operations

The accepted week-open snapshot is
`data/season_snapshots/20260930T014535Z/snapshot.json`
with SHA-256
`9c0270713a2c902b2a9e13004fe9b4b655250dfa7b88df82b86d79045e76a367`.

The accepted prospective capture is
`data/season_predictions/closure/pregame_2026_w04_20260930T014558Z.json`
with SHA-256
`4bc538cc935ab878b918bbadc8726e6408e2e6e79c9f69d651715a3ecd244734`.

Acceptance:

- live source health `6/6`;
- measurement contract `A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034`;
- integrity PASS;
- pre-data firewall PASS;
- Week 3 captures preserved `4/4`;
- persistence remained disabled.

The pinned Week 4 trade search used the accepted frozen state, kept the trade
channel player-only, and evaluated screened one-for-one candidates with 4096
predictive MC scenarios. It returned zero `ACTIONABLE_OFFER` and zero
`MUTUAL_MODEL_GAIN` results. The top six were all
`OUR_EDGE_PARTNER_LOSS`.

**Current trade decision: HOLD / NO TRADE.**

Manager response remains
`UNCALIBRATED_TRADE_RESPONSE_V030` and is separate from football utility.

## Week 4 Availability Gate

A targeted reporting recovery established four roster players below 95% modeled
active probability:

- Baker Mayfield: OUT, 0%;
- Josh Jacobs: EXEMPT, 0%;
- Mark Andrews: QUESTIONABLE, 75%;
- Puka Nacua: QUESTIONABLE, 75%.

Puka is the only one in the current expected starting lineup. The original
decision package's zero uncertainty count was a package-renderer representation
defect caused by treating missing raw `active_probability` as 1.0 instead of
using the optimizer's status-prior fallback.

The football calculations and trade MC were not rerun and remain accepted.

**Next calendar action:** fresh pre-lock Week 4 decision-time status sync/capture,
with Puka's availability evidence as the primary starting-lineup uncertainty.

## Phase 1E — Measurement-Apparatus Closure

The redacting persistence primitive and disabled-by-default persistence
controller are source-published and runtime-commissioned.

Persistent evidence remains **DISABLED**. Phase 1E.4 activation is separately
gated and has not been authorized.

Activation must still prove the exact Git-excluded local path, real redacted
bytes on disk, rotation/storage-cap behavior, fail-open disk behavior,
privacy/non-interference, and no football/model/behavior change.

## Phase 2 / Closure

Prospective `MC -> Data -> closure` collection continues concurrently. Week 3
Data/MC closure remains required, but the Week 4 pre-lock calendar gate outranks
that deferrable analysis.

No missed prospective evidence may be reconstructed after outcomes.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- `screen != authority`.
- Diagnostics/reporting defects do not become decision logic.
- Football utility remains separate from market perception and manager behavior.
- Persistent activation requires separate authorization.
- Raw authenticated/private evidence remains local.
- No observed 2026 outcome may tune v0.X.
