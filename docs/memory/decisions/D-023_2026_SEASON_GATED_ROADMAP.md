# D-023 — 2026 Season-Gated Development Roadmap

**Status:** ACTIVE
**Accepted:** 2026-09-20

## Context

The 2026 season creates deadlines that do not behave like ordinary software
milestones. A pregame information state cannot be recovered prospectively after
outcomes are known, while scientific calibration should not be forced merely
because a planned date arrives.

The configured league uses Weeks 1-13 as the fantasy regular season and
Weeks 14-17 as the fantasy playoff window. Week 14 is playoff Round 1.

## Decision

Adopt two explicit gate classes.

### Calendar gates

Protect irreversible prospective captures and operational freezes.

A missed calendar capture is recorded as missing and is never backfilled as
prospective.

### Evidence gates

Authorize diagnosis/calibration only when accumulated prospective closure
supports them.

A calendar review date never forces an evidence gate to pass.

## 2026 sequencing

- finish the roadmap/memory repository checkpoint before further implementation;
- Week 3 is the first future hard prospective-capture gate under this plan;
- prefer v1.0 observability commissioning by Week 5;
- first formal three-clean-week closure review occurs after Week 5;
- review early evidence-supported calibration through Weeks 6-8;
- prefer justified early calibration commissioned before Week 9;
- mature market/transaction response through Weeks 9-11;
- perform playoff-readiness/freeze work in Weeks 12-13;
- commission playoff production baseline before Week 14;
- Weeks 14-17 are production-first with major empirical calibration frozen by
  default;
- use Week 18/postseason for complete-season closure and broader v2 research.

## Weekly evidence decision

Preserve both:

1. a week-open reference capture;
2. consequential decision-time captures as new information becomes available.

This avoids treating a Thursday reference state and a Sunday decision state as
if they had the same information set.

## Consequences

- prospective measurement deadlines outrank nonessential feature work;
- development may slip rather than contaminate evidence;
- insufficient evidence produces `DEFER / COLLECT MORE DATA`;
- weekly closure becomes a first-class evidence artifact;
- long-range phase intent belongs in `docs/ROADMAP.md`;
- exact 2026 temporal gates belong in `roadmap/SEASON_2026.md`;
- current roadmap position remains in `roadmap/STATUS.md`;
- active authority remains `CURRENT.md`.

## Scientific boundary

This decision changes planning, evidence handling, and memory structure only.

It does not tune any football parameter, alter any production prediction, or
claim any new runtime validation.

## Supersedes / superseded by

No prior scientific decision is superseded.

This decision refines scheduling/closure expectations under D-003, D-004,
D-006, D-007, D-008, and the causality architecture.
