# Known Issues and Deferred Work

**As of:** 2026-09-21

This file owns open/deferred/blocker/debt state that should not clutter
`docs/memory/CURRENT.md`. It does not override current authority.

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Memory-system refinement M0-M7 | ACTIVE MAINTENANCE | Blocks advancing the retained Phase 1B checkpoint while the current memory step is not durable; does not outrank the Week 3 capture | Complete each narrow M-step with its own validation; preserve prospective capture first |
| Current memory-step durability gate | GATE CONDITION | Yes for the next M-step only when the current step exists only as local/unpublished state | Resolve from the repository context containing the current memory files; if remote `main` contains the current step, the gate is satisfied |
| M4 handoff contract / M4R1 repair | M4 PUBLISHED / M4R1 CONTENT COMPLETE | Yes for M5 until M4R1 is durable | Publish the reviewed M4R1 maintenance-newline repair; startup membership remains unchanged until M5 |
| Closure production instrumentation | NEXT TECHNICAL SLICE / RETAINED CANDIDATE | Deferred during M0-M7 memory refinement | Resume Phase 1B only after memory refinement gate chosen in CURRENT; do not rerun established candidate gates without new evidence |
| Player/DST/K production instrumentation | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1C |
| Market/manager-behavior production instrumentation | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1D |
| Persistent runtime evidence sink disabled | INTENTIONAL / DEFERRED | No | Enable only after separate privacy/non-interference authorization |
| Week 1/2 prospective-capture availability not classified here | UNCLASSIFIED | Blocks treating those weeks as prospective closure if no frozen capture exists | Inspect genuine frozen evidence only; never backfill |
| Week 3 week-open capture | UPCOMING HARD CALENDAR GATE | Yes for causal 2026 measurement quality | Freeze prospective state before the first Week 3 game; do not delay for nonessential M5-M7 or Phase 1B work |
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
