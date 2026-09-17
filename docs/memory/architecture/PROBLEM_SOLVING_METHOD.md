# Problem-Solving Method

<!-- FANTASY_PROBLEM_SOLVING_METHOD_STANDALONE:BEGIN -->
This file defines the durable reasoning procedure for the fantasy-football project. It contains process, not football conclusions.

## Core loop

```text
authority check
-> narrow question / hypothesis
-> define decision boundary
-> targeted diagnostic or probe
-> fresh evidence
-> inspect raw measurements
-> classify result and limitations
-> one coherent patch, successor diagnostic, defer, or close
-> validate exact output
-> update durable memory
```

## 1. Authority check

Before reasoning from a state, establish what is authoritative.

Priority:
1. validated local working tree and fresh direct evidence;
2. exact successful installer/runtime receipts and hashes;
3. current durable-memory state for the same checkpoint;
4. subsystem/decision/evidence/investigation records;
5. Git/GitHub history;
6. older summaries/chats.

Contradictions are evidence. Record them. Do not silently merge them.

## 2. Ask one narrow question

A useful investigation has a bounded question that can be answered by one targeted measurement.

Bad pattern:
- collect many symptoms;
- infer a broad cause;
- patch several subsystems.

Preferred pattern:
- identify first uncertain boundary;
- formulate one testable question;
- measure that boundary;
- let the result select the next boundary.

## 3. Define the decision boundary before measurement

Before running a probe, state what each meaningful result would imply.

Example structure:

```text
If A is measured:
    production representation is sufficient -> patch narrow defect.
If B is measured:
    representation is incomplete -> run successor identity/state probe.
If evidence is inconclusive:
    do not patch production -> improve measurement.
```

This prevents the observed result from retroactively defining the test.

## 4. Prefer probes over speculative production changes

When cause or architecture is uncertain:
- use read-only/diagnostic probes first;
- reuse existing logs/snapshots/MC diagnostics before adding instrumentation;
- record provenance, timestamps, and exact scope;
- avoid changes that mix measurement with attempted repair.

## 5. Inspect raw evidence before classifiers

Derived classifications are useful summaries, not primary evidence.

If classifier and raw measurement disagree:
1. inspect raw measurement;
2. inspect representation/normalization;
3. inspect classifier assumptions;
4. only then change model/threshold/physics.

## 6. Preserve history; supersede interpretations

Later evidence can show that an earlier measurement was representation-incomplete.

Do not erase the old result. Record:
- what was measured correctly;
- what representation assumption was incomplete;
- which conclusion is superseded;
- which newer investigation owns the corrected interpretation.

## 7. Patch one coherent defect

A patch should:
- change one logical thing;
- preserve stable subsystems;
- avoid unrelated cleanup/refactoring;
- carry expected pre-state and rollback;
- fail before modification on wrong state;
- validate exact installed/generated output.

## 8. Separate validation states

Never collapse these:
- source inspected;
- source-validated;
- package/generated-output validated;
- runtime-validated;
- commissioned.

A compile pass does not imply runtime acceptance.

## 9. Use explicit failure state

Track:
- `FAILED BEFORE MODIFICATION`;
- `ROLLED BACK`;
- `INSTALLED SUCCESSFULLY`.

Also report runtime/temporary side effects separately from project-file modification state.

## 10. Close and defer deliberately

Resolved/deferred investigations stay closed until new evidence appears.

A surprising observation opens a narrow investigation; it does not authorize reopening every related subsystem.

## 11. Memory is part of the patch

The work is not complete until the durable record answers:
- What was the state?
- What question was asked?
- What was measured?
- What changed?
- What was actually validated?
- What remains uncertain?
- What is next?

Every meaningful ZIP/checkpoint carries its relevant memory update and declares `durable_memory_updated: true`.
<!-- FANTASY_PROBLEM_SOLVING_METHOD_STANDALONE:END -->
