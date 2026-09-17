# v1.0A Adapter / Correlation Package-Build Failures

<!-- FANTASY_EVIDENCE_V10A_ADAPTERS_CORRELATION_BUILD_FAILURES_20260917:BEGIN -->
## Pre-delivery QA failures

Three assistant-side QA/environment defects occurred before delivery:

1. **Container network unavailable.** An attempted Git clone of the exact
   predecessor failed because the container could not resolve `github.com`.
   Classification: `QA ENVIRONMENT FAILURE / BEFORE DELIVERY / NO PROJECT
   MODIFICATION`. This was not treated as repository validation.
2. **Historical-package extraction-path assumption.** The first local
   dependency reconstruction looked for extracted historical payload files at a
   directory path that was no longer present. The exact historical ZIPs were
   still available and were used instead. Classification: `QA PATH ASSUMPTION
   FAILURE / BEFORE DELIVERY / NO PROJECT MODIFICATION`.
3. **Focused-test API assumption.** The first exact-dependency focused run used
   `sink.events`, but the committed `MemorySink` API exposes `__len__()` and
   `snapshot()` rather than an `events` attribute. The test was corrected to
   `len(sink) == 0`; the exact focused suite then passed 9/9. Classification:
   `PRE-DELIVERY TEST DEFECT / NO PROJECT MODIFICATION`.

No project source, durable memory, Git commit, or remote state was modified by
these pre-delivery failures.

Reusable rule: focused observability tests must exercise the exact committed
dependency API rather than assumed helper attributes.
<!-- FANTASY_EVIDENCE_V10A_ADAPTERS_CORRELATION_BUILD_FAILURES_20260917:END -->
