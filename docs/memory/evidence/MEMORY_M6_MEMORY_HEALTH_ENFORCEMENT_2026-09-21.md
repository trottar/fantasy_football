# Memory M6 Memory-Health Enforcement — 2026-09-21

## Classification

`M6 MEMORY HEALTH ENFORCEMENT = CONTENT COMPLETE / SEMANTIC CONTRACT CHECKER / NO FOOTBALL OR RUNTIME CHANGE`

## Predecessor

M5 is durable on remote `main` at repository checkpoint
`bc925d356459baddd25829b0216a1842e0b115d0`.

That SHA is predecessor evidence only. Active memory does not need to predict the
commit that will contain M6.


## M6 v1 Local Failure / M6R1 Correction

The first M6 package,
`memory-m6-memory-health-enforcement-20260921-v1`, passed package preflight,
predecessor checks, payload verification, application, compile, checker self-test,
and its original seven focused tests. It then failed the strict actual-repository
health gate and rolled back its reviewed scope.

Fresh raw failure evidence:

`AGENTS.md startup contract does not require selective post-core expansion`

The durable M5 `AGENTS.md` contract did encode bounded post-core retrieval, but
without the literal substring `select`: it directs work to CURRENT/task-linked
frontiers, loads only task-relevant material, consults deep memory only when the
task requires it, and explicitly rejects eager loading of the wider hierarchy.

Root cause: M6 v1 reduced that semantic contract to
`"select" in section.casefold()`. Its synthetic fixture used the word
`selectively`, so the fixture passed while the actual M5 AGENTS surface failed.

M6R1 corrects only that enforcement defect. A startup surface now passes the
post-core condition when it establishes expansion after the five-file core and
then expresses either explicit selective wording or the equivalent bounded
task-relevant plus anti-eager wording used by M5.

The checker self-test and focused pytest now exercise the no-`select` wording.
No M5 contract text is changed merely to satisfy the checker.

The failed M6 v1 package did not stage, commit, push, or touch the commissioned
runtime. Its post-write exception handler restored the predecessor files and
removed the new test/evidence files.

## Hypothesis

M0-A06 identified a checker-coverage gap: the existing memory-health tool could
validate size, duplicate headings, one active objective, one next action,
append-style markers, and the AGENTS startup order while still missing semantic
contract drift across the active memory surfaces.

M1-M5 deliberately finalized the state/ownership/startup contracts before M6 so
the checker would not freeze a transitional structure.

## Implemented Enforcement

M6 keeps the checker observational and adds stable contract checks for the
structures selected by M1-M5.

### Startup contract consistency

The checker requires the same five-file core, in the same order, in the three
startup-policy surfaces:

1. `AGENTS.md`
2. `CURRENT.md`
3. `MEMORY.md`
4. `handoffs/CURRENT_HANDOFF.md`
5. `USER.md`

Each startup section must also require a full core read before selective
post-core expansion.

### CURRENT structure

The checker requires these active-state headings exactly once and in order:

- `## Active Objective`
- `## Current Work Item`
- `## Verified State`
- `## Calendar / Evidence Gates`
- `## Scientific / Architectural Boundaries`
- `## Exact Next Action`
- `## Relevant References`

This prevents accidental whole-file rewrites from silently deleting the selected
active-state structure.

### Handoff contract

The checker requires:

- one `# Current Handoff` title;
- one `## Transfer State` section;
- one `## Resume` section;
- explicit CURRENT authority/non-override language;
- non-empty transfer state;
- a resume pointer to CURRENT;
- absence of routine CURRENT-style headings from the live handoff.

The checker does not require the stable-state sentence specifically because a
future interrupted transition may legitimately populate exceptional transfer
state.

### Durable-memory role separation

`MEMORY.md` may not acquire exact active/transfer headings such as Active
Objective, Current Work Item, Exact Next Action, or Transfer State.

### Rendered-text regression protection

Active memory/policy surfaces are checked for literal escaped-newline artifacts.
This closes the exact failure class that produced the M4 maintenance rendering
defect while allowing historical/evidence records to quote that defect.

### Required active surfaces

The checker now requires the active bootstrap/policy/status files that the
current memory architecture depends on, rather than only the three thresholded
memory documents.

## Deliberate Non-Goals

M6 does not attempt to infer arbitrary football or roadmap truth from prose. It
cannot prove that a phase-completion statement is empirically correct, and it
does not replace opening canonical decision/evidence/investigation records.

It also does not:

- redesign the M5 startup contract;
- make handoff state authoritative;
- rewrite memory automatically;
- alter repository checkpoint mechanics;
- alter football/model/application source;
- alter the commissioned runtime;
- authorize persistent evidence.

The checker enforces stable representation contracts; fresh evidence remains the
authority for substantive project truth.

## Test Coverage

A dedicated `tests/test_memory_health.py` verifies:

- healthy selected-contract fixture using the M5 no-`select` AGENTS semantics;
- explicit bounded-post-core/no-`select` regression coverage;
- startup-order drift detection;
- CURRENT heading drift detection;
- second-CURRENT handoff heading detection;
- empty transfer-state detection;
- active-heading leakage into durable MEMORY detection;
- escaped-newline rendering regression detection.

The checker self-test covers the same critical branches independently of pytest.

The M6 local-apply gate must compile the checker/test, run the checker self-test,
run the targeted pytest file, run strict health against the actual control root,
and roll back on deterministic failure.

## PrivyHub Adaptation

The PrivyHub reference checker demonstrates the value of making active-state
structure executable policy rather than prose only. Fantasy adapts that
principle to its own M5 five-file core, explicit exceptional handoff, scientific
memory separation, and Windows checkpoint workflow rather than copying
PrivyHub's exact startup model.

## M6R1 Staging Failure / M6R2 Correction

M6R1 local apply passed its exact package gates, including the corrected
actual-repository semantic-health contract. The subsequent isolated staging
attempt then failed at `git diff --cached --check` with:

`tests/test_memory_health.py:119: new blank line at EOF.`

This was a generated-test rendering defect, not a checker-contract or runtime
failure. Staging stopped before commit/push, and the control root was not
modified by the failed staging attempt.

Root cause: the M6R1 package generator appended the new no-`select` regression
test with one extra terminal newline, producing a blank line at EOF. The package
and pytest gates did not reject that representation, while the canonical staging
gate correctly did.

M6R2 removes exactly that extra terminal blank line and records this staging
failure lineage in the existing M6 evidence. It does not alter checker semantics,
M5/M6 contracts, football/model/application logic, or the commissioned runtime.

The correction requires:

- the exact locally-applied M6R1 test/evidence predecessors;
- the established M6 semantic markers on the remaining reviewed M6 surfaces;
- exactly one terminal newline in `tests/test_memory_health.py`;
- no trailing spaces/tabs in either corrected path;
- checker/test compile, checker self-test, focused pytest, and strict actual-root
  memory health to remain passing;
- manifest and control-root Git index to remain unchanged.

## Next Step

Once M6 is durable on remote `main`, proceed to
**M7 — fresh-session integration audit**.

M7 should test repository-only recovery of the active task and actor boundaries
without relying on a giant chat continuation prompt.

The Week 3 prospective-capture gate still outranks nonessential M7 work.
