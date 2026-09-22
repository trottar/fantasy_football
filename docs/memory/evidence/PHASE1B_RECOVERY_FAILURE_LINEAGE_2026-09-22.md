# Phase 1B Recovery Failure Lineage — 2026-09-22

## Scope

This record classifies the recovery of the previously retained Phase 1B
closure-instrumentation candidate and the first fresh reconstruction attempt.

It is a workflow/observability-development record only. No football/model
semantics are changed by this evidence.

## Prior Validated State

Before recovery began, durable history recorded a retained Phase 1B candidate
that had passed:

- exact four-path technical allowlist;
- targeted 48-test gate;
- paired non-interference/privacy probe;
- full repository pytest;
- compileall;
- `git diff --check`.

Those measurements remain valid for the candidate bytes that produced them.

## Recovery Measurements

Read-only recovery probes established:

1. the project contained 16 Git roots;
2. none was the retained four-file Phase 1B candidate;
3. the control root was unsuitable as a candidate authority because it contains
   a large synchronized/local working surface;
4. retained `.ffpkg` inventory contained no Phase 1B source carrier;
5. the remaining 21-change
   `_stage_generic_delivery_infrastructure_20260921_v2` root contained only
   generic delivery/memory checkpoint files, not Phase 1B technical files;
6. semantic search still confirmed the declared integration boundary
   `subsystem.closure.capture`, but did not recover the lost candidate bytes.

## Classification of Lost Candidate

`PRIOR PHASE1B VALIDATION = HISTORICAL / BYTE IDENTITY NOT RECOVERABLE`

This does not invalidate the historical measurements. It does prevent those
measurements from being used to authorize different reconstructed bytes.

## Fresh Reconstruction v1 Failure

Package:

`phase1b_closure_shadow_fresh_candidate_20260922_v1`

The package successfully:

- passed generic `.ffpkg` runner preflight;
- verified the intended baseline staging root;
- verified baseline HEAD
  `661f0a16faa3c7f91f8ab19447ba84867b65297d`;
- verified predecessor Git blob identities for the intended source files;
- created its owned isolated candidate.

It then failed during its source-transformation step. The byte-marker helper
expected one occurrence of the
`build_pregame_capture_from_context` definition marker and reported two.

Trace classification:

`FAILED IN OWNED ISOLATED CANDIDATE / SOURCE-TRANSFORM ASSUMPTION DEFECT`

The failure happened before:

- targeted pytest;
- paired Phase 1B non-interference/privacy probe;
- full pytest;
- compileall;
- staging;
- commit;
- push;
- runtime synchronization or commissioning.

Authoritative control-root source and commissioned runtime source were not
modified. Git index/history and remote state were not modified.

The isolated path may remain:

`_phase1b_closure_shadow_candidate_20260922_v1`

A successor must verify ownership, expected HEAD, and changed-path confinement
before deleting or replacing it.

## Root Cause / Reusable Lesson

The failed package relied on a byte-substring cardinality assertion for a Python
function boundary even though exact source structure was available.

For the successor:

- inspect exact source first;
- locate the target top-level function structurally rather than by an ambiguous
  raw substring;
- self-test the transform against the exact predecessor representation before
  delivery;
- preserve stable commissioned observability modules unless the new slice
  genuinely requires modifying them;
- bind every validation claim to the exact candidate byte identity.

## Successor Boundary

The next Phase 1B candidate is a fresh candidate, not a continuation of the lost
candidate.

It must be independently target/probe validated before any full-validation,
staging, publication, or runtime-commissioning step.

Persistent evidence remains disabled.
