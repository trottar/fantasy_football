# Known Issues and Deferred Work

**As of:** 2026-09-22

This file owns open/deferred/blocker/debt state that should not clutter
`docs/memory/CURRENT.md`. It does not override current authority.

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Memory-system refinement M0-M7 | M7 CONTENT COMPLETE / DURABILITY CONTEXT | Blocks only declaring memory refinement durable if the containing M7 state is not remote; does not outrank Week 3 capture | If remote `main` contains the exact M7 state, classify M0-M7 COMPLETE / DURABLE and close the maintenance series |
| Current memory-step durability gate | GATE CONDITION | Yes for the next transition only when the current step exists only as local/unpublished state | Resolve from the repository context containing the current files; if remote `main` contains the current step, the gate is satisfied |
| M7 fresh-session integration audit | CONTENT COMPLETE | Yes only for formal M0-M7 closure until durable | Publish the reviewed M7 evidence/continuity scope if needed; once remote-durable, proceed to Week 3 prospective capture |
| Closure production instrumentation | NEXT TECHNICAL SLICE / RETAINED CANDIDATE | Deferred until the Week 3 week-open capture is secured | Resume Phase 1B after the hard capture gate; do not rerun established candidate gates without new evidence |
| Player/DST/K production instrumentation | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1C |
| Market/manager-behavior production instrumentation | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1D |
| Persistent runtime evidence sink disabled | INTENTIONAL / DEFERRED | No | Enable only after separate privacy/non-interference authorization |
| Week 1/2 prospective-capture availability not classified here | UNCLASSIFIED | Blocks treating those weeks as prospective closure if no frozen capture exists | Inspect genuine frozen evidence only; never backfill |
| Week 3 week-open capture | UPCOMING HARD CALENDAR GATE | Yes for causal 2026 measurement quality | Freeze prospective state before the first Sep 24 game using the commissioned baseline; do not delay for Phase 1B or other nonessential development |
| Three-clean-week prospective closure baseline | INSUFFICIENT EVIDENCE | Yes for broad empirical calibration | Accumulate/verify clean weekly closure; first formal review after Week 5 if W3-W5 are valid |
| Midseason calibration | DEFERRED PENDING EVIDENCE | No | Authorize only from repeated prospective residual/coverage evidence |
| Playoff production baseline | PLANNED | Becomes blocking before Week 14 | Commission before Week 14 |
| Season-readiness checker | PLANNED TOOLING | No | Implement after memory/observability foundations are stable |

## Standing scientific non-issues

Do not reopen without new evidence:

- `P ⊕ D ⊕ K`;
- `0.X` a-priori / `1.X` empirical boundary;
- manager behavior versus intrinsic football utility;
- `screen != authority`;
- frozen prediction / decision-time causality;
- raw observation versus derived/calibrated state;
- human-in-the-loop checkpoint actor separation;
- Phase 1A season-sync shadow commissioning.

## Missed-Capture Policy

A missing pregame or decision-time capture is an evidence gap, not permission to
reconstruct a prospective state from hindsight. Record which capture is missing,
when its deadline passed, what downstream analysis is unavailable, and the next
causally valid capture opportunity.

## Reopen Rule

A resolved/deferred item reopens only when new source, runtime, weekly closure,
or operational evidence contradicts the standing classification.
