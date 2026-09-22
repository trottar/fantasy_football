# Memory M5 Startup Contract Decision — 2026-09-21

## Classification

`M5 STARTUP CONTRACT DECISION = CONTENT COMPLETE / RETAIN FIVE-FILE CORE + SELECTIVE EXPANSION / NO FOOTBALL OR RUNTIME CHANGE`

## Predecessor

M4R1 is durable on remote `main` at repository checkpoint
`bdfdafde92bb0003d4d62eca6cea3ebd69f2d2d8`.

That concrete SHA is predecessor evidence only. Active memory does not need to
predict the commit that will contain M5.

## Question

M0-A07 identified the startup contract as a design question rather than a
correctness defect. The then-mandatory five-file bootstrap was coherent but
relatively heavy, while the PrivyHub reference model used a more selective
CURRENT-first retrieval pattern.

M3 and M4 subsequently changed the economics of that decision:

- `MEMORY.md` was curated back to durable cross-phase knowledge;
- `CURRENT_HANDOFF.md` became a very small exceptional-transfer note;
- procedure duplication was removed from active memory;
- `CURRENT.md` remained the sole authoritative resumable state.

M5 therefore decides the startup contract after those role cleanups rather than
from the pre-cleanup bootstrap size alone.

## Alternatives Considered

### A — Eagerly load the wider memory hierarchy

Rejected.

Reading architecture, evidence, investigations, decisions, history, patches,
roadmap, source, and tests on every substantial session would increase cost,
encourage summary-of-summary reasoning, and violate the established typed-memory
model.

### B — PrivyHub-style CURRENT-first selective startup with MEMORY/handoff optional

Not adopted for Fantasy.

That pattern is efficient, but Fantasy has project-specific reasons to retain a
small fixed core:

- `AGENTS.md` contains authority, causality, authorization, and checkpoint actor
  boundaries that must be known before action;
- `CURRENT.md` is the sole authoritative active frontier;
- curated `MEMORY.md` contains compact scientific invariants and commissioned
  cross-phase facts whose omission can cause architectural drift;
- `CURRENT_HANDOFF.md` is now small enough to read cheaply and is the designated
  surface for exceptional interrupted-transition state;
- `USER.md` contains Windows/PowerShell, delivery, privacy, and collaboration
  constraints that materially affect safe execution.

The project-level working contract also already requires these five files at the
start of substantial work.

### C — Fixed five-file core plus selective expansion

Adopted.

Every substantial session reads, in full and in order:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

After that fixed core, retrieval becomes selective:

1. use `CURRENT.md`'s exact next action and references as the primary frontier;
2. open the canonical record before restating a decision, gate, classification,
   deadline, or architectural constraint;
3. load only task-relevant architecture, decisions, investigations, evidence,
   roadmap, patch/procedure, source, and tests;
4. do not traverse history or the wider memory hierarchy merely because it
   exists.

This retains deterministic continuity while taking the main efficiency benefit
of the PrivyHub pattern where it matters: expansion beyond the stable core.

## Ownership

- `AGENTS.md` owns the operational startup contract.
- `MAINTENANCE.md` owns startup-contract health/coherence checks and lifecycle
  expectations.
- `README.md` summarizes the contract for navigation.
- `CURRENT.md` owns the active frontier; it does not own startup policy.
- `CURRENT_HANDOFF.md` remains exceptional-transfer state only.
- `MEMORY.md` remains curated durable cross-phase knowledge.
- `USER.md` remains collaboration/environment preference authority.

## Explicit Non-Changes

M5 does not:

- change the five startup files or their order;
- make the handoff authoritative;
- make `MEMORY.md` optional;
- eagerly load the wider memory hierarchy;
- modify `tools/check_memory_health.py` — enforcement changes are M6;
- modify football/model/application source;
- modify the commissioned runtime;
- change persistent-evidence authorization.

## Validation Contract

The M5 package must:

- authorize all six existing changed targets against exact durable-M4R1 Git blob
  predecessors;
- preserve BOM/newline representation;
- make `AGENTS.md` the explicit startup-contract owner;
- keep the same five startup files in the same order in AGENTS, MAINTENANCE, and
  README;
- explicitly require full core reading before selective expansion;
- remove transitional wording that startup might still change at M5;
- preserve `USER.md`, `MEMORY.md`, and the live handoff without modification;
- validate those three read-only role surfaces remain compatible;
- update CURRENT/STATUS/KNOWN_ISSUES to M5 content-complete state;
- support idempotent rerun and rollback on post-write failure;
- pass strict memory health;
- leave `docs/memory/manifest.json` and the control-root Git index unchanged
  during local apply;
- not touch football/model/application source or commissioned runtime.

## Next Step

Once M5 is durable on remote `main`, proceed to
**M6 — memory-health enforcement**.

M6 may then encode the selected contract in tooling; it must not redesign the
startup contract while implementing the checker.

Week 3 prospective capture remains a harder calendar gate than nonessential
M6-M7 progress.
