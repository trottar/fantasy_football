# Specialist Channels

## Core Boundary

Preserve `P ⊕ D ⊕ K`.

Players compare only to players, defenses only to defenses, and kickers only to
kickers inside valuation/response models. Cross-channel coupling belongs only at
complete-roster utility/state boundaries.

This separation is **not** a prohibition on league-legal transactions containing
DST or kicker assets. A mixed trade or roster perturbation may contain P, D,
and/or K assets provided each channel is valued with its own model and the
combined consequence is evaluated only at the complete-roster boundary.

## Defense

DST is a separate channel. Weekly operations must evaluate the current DST
portfolio against the actionable DST market whenever the weekly decision cycle
is open.

Closure should be component-level:

- sacks;
- interceptions;
- fumble recoveries;
- defensive TDs;
- points allowed;
- yards allowed;
- fantasy scoring response.

Defense value is primarily lineup/team synergy, weekly matchup, specialist-market
state, and roster-slot opportunity cost rather than head-to-head ranking against
offensive players.

## Kicker

K is a separate channel. Weekly operations must evaluate the current kicker
against the actionable kicker market whenever the weekly decision cycle is open.

The historical model is aggregate yield plus team scoring environment. Observed
evidence should record:

- scoring drives/environment;
- FG attempts/makes/distances;
- XP opportunities/makes.

A more physical kicker opportunity model is a later 1.X investigation, not a
reactive 0.X retune.

## Operational Completeness

A weekly cycle that evaluates the player channel but omits DST or K is
`INCOMPLETE_COVERAGE`.

A specialist candidate on WAIVERS cannot be treated as fully evaluated merely
because a static same-channel diagnostic exists if the commissioned authoritative
policy excludes that acquisition state.

Specialist-inclusive trades are a required supported action family for a
complete production workflow when league rules permit them. Until commissioned,
their absence must be reported as an explicit blocking capability gap.
