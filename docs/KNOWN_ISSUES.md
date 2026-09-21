# Known Issues and Deferred Work

**As of:** 2026-09-20

This file owns open/deferred/blocker/debt state that should not clutter
`docs/memory/CURRENT.md`. It does not override current authority.

| Item | Status | Blocks current work? | Owner / resolve condition |
| --- | --- | --- | --- |
| Season-roadmap durable-memory checkpoint transition | GATE CONDITION | Only while the accepted checkpoint content is not `PUSHED / REMOTE VERIFIED` | Complete local apply, verified staging/manifest commit, push, and read-only remote verification |
| Data-source season-sync observability not integrated | NEXT TECHNICAL SLICE | No, until memory gate closes | v1.0A Phase 1A |
| Closure production instrumentation not integrated | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1B |
| Player/DST/K production instrumentation not integrated | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1C |
| Market/manager-behavior production instrumentation not integrated | PLANNED / SEPARATELY GATED | No | v1.0A Phase 1D |
| Persistent runtime evidence sink disabled | INTENTIONAL / DEFERRED | No | Enable only after separate privacy/non-interference authorization |
| Week 1/2 prospective-capture availability not classified here | UNCLASSIFIED | No; blocks treating those weeks as prospective closure if no frozen capture exists | Inspect existing frozen evidence; never backfill |
| Three-clean-week prospective closure baseline not yet accumulated under the new season plan | INSUFFICIENT EVIDENCE | Yes for broad empirical calibration | Accumulate/verify clean weekly closure; first formal review after Week 5 |
| Midseason calibration | DEFERRED PENDING EVIDENCE | No | Authorize only from repeated prospective residual/coverage evidence |
| Playoff production baseline | PLANNED | Becomes blocking before Week 14 | Commission before Week 14 |
| Season-readiness checker | PLANNED TOOLING | No | Implement after memory roadmap and observability foundations are stable |

## Standing scientific non-issues

Do not reopen these as problems without new evidence:

- `P ⊕ D ⊕ K`;
- `0.X` a-priori / `1.X` empirical boundary;
- manager behavior versus intrinsic football utility;
- `screen != authority`;
- frozen prediction / decision-time causality;
- raw observation versus derived/calibrated state;
- human-in-the-loop checkpoint actor separation.

## Missed-capture policy

A missing pregame or decision-time capture is an evidence gap, not permission to
reconstruct a prospective state from hindsight.

Record:

- which capture is missing;
- when the deadline passed;
- what downstream analyses are therefore unavailable;
- the next causally valid capture opportunity.

## Reopen rule

A resolved/deferred item reopens only when new source, runtime, weekly closure,
or operational evidence contradicts the standing classification.
