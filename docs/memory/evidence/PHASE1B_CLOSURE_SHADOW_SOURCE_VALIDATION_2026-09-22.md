# Phase 1B Closure-Shadow Source Validation — 2026-09-22

## Scope

This record establishes the exact fresh Phase 1B closure-observability source
candidate after the prior retained candidate became unrecoverable.

It records source validation only. Runtime synchronization and commissioning are
separate future gates.

No football/model/scoring/manager-behavior semantics are changed.

## Predecessor Authority

Repository/source predecessor:

- commit: `724e87089cd7fe06f884d5d74c944df05622a532`;
- tree: `3bc39c0138404131f0b684d92c8db20db2471a40`;
- predecessor `src/closure.py` Git blob:
  `cd438a5fa0953f91cdeaa5a5b53887a79d50332b`.

The fresh candidate was built in the isolated local repository:

`_phase1b_closure_shadow_candidate_20260922_v2`.

## Structural Discovery

Exact `src/closure.py` inspection established that
`build_pregame_capture_from_context` is intentionally defined twice.

The first definition is retained as the inherited pre-v0.34 implementation and
is later bound to:

`_build_pregame_capture_from_context_pre_v034`.

The second/final definition is the v0.34 public override that calls the inherited
implementation and then enriches the immutable prospective capture.

Therefore the correct Phase 1B outer boundary is the **final v0.34 override
only**. Instrumenting both definitions would double-observe the same public
operation.

## Technical Scope

Exactly four validated paths:

1. `src/closure.py`
2. `src/observability/closure_shadow.py`
3. `tests/test_observability_closure_shadow_v10a.py`
4. `tools/probe_observability_closure_shadow_v10a.py`

The shared commissioned `src/observability/shadow_pilot.py` is unchanged.

`closure_shadow.py` reuses the existing bounded `ShadowRecorder` and
`call_subsystem(..., subsystem="closure")` machinery. It owns no persistent sink
and retains no arguments, returned values, private payloads, or exception
messages.

The decorated boundary is:

`subsystem.closure.capture`.

## Reconstruction v2 Validation-Layer Failure

Package:

`phase1b_closure_shadow_candidate_20260922_v2`

The package successfully established:

- structural-transform self-test: PASS;
- predecessor HEAD/tree/blob identity: PASS;
- the four intended candidate files had been written.

It then reported a false allowlist failure because the validator captured Git
stdout and stderr into one string. Git emitted a benign line-ending warning:

`warning: in the working copy of 'src/closure.py', LF will be replaced by CRLF the next time Git touches it`

That stderr text was parsed as if it were a fifth filename.

Classification:

`VALIDATOR PATH-PARSER DEFECT / RETAINED CANDIDATE BYTES NOT INVALIDATED`

No authoritative control-root source/memory, commissioned runtime, Git
index/history, or remote state changed.

## v3 Continuation / Targeted Gate

Package:

`phase1b_closure_shadow_candidate_continue_20260922_v3`

The continuation made **no candidate-source changes**.

It first verified the retained v2 candidate byte-for-byte against the deterministic
baseline transform and generated source/test/probe contents.

Results:

- retained candidate exact bytes: PASS;
- stdout-only four-path allowlist: PASS;
- Git stderr warning observed separately: 1;
- structural final-v0.34 boundary: PASS;
- `git diff --check`: PASS;
- `py_compile`: PASS;
- candidate import-root ownership: PASS;
- targeted pytest: **33 passed in 1.94 s**.

Paired probe results:

- outputs equal: true;
- exception behavior equal: true;
- state equal: true;
- success-path privacy: PASS;
- error-path privacy: PASS;
- Python RNG state preserved: true;
- persistent sink: false;
- arguments captured: false;
- returned values captured: false;
- exception messages captured: false.

Timing:

- baseline median: `6100 ns`;
- observed median: `70100 ns`;
- incremental: `64000 ns`;
- reported relative fraction: `10.491803278688524`.

The configured budget used:

- maximum incremental: `2,000,000 ns`;
- maximum relative fraction: `0.20`;
- relative floor: `50,000,000 ns`.

Because the baseline is below the relative floor, the relative percentage is
intentionally non-authoritative for this tiny operation. The active absolute
criterion passes: `64,000 ns < 2,000,000 ns`.

## Full Source Gate

Package:

`phase1b_closure_shadow_full_validation_20260922_v1`

The package reused the already-passed targeted gate and did not rerun the
targeted pytest or paired probe.

Results on the exact same retained bytes:

- exact retained bytes before full gate: PASS;
- exact four-path allowlist: PASS;
- full pytest: **491 passed in 51.83 s**;
- full `compileall`: PASS;
- `git diff --check`: PASS;
- exact retained bytes after full gate: PASS;
- exact four-path allowlist after full gate: PASS.

## Exact Validated Byte Identity

SHA-256:

- `src/closure.py`:
  `c3c1633e5b8843b15a450f0ad8cf38f4797856d4128c5d7a4b00f99012a886c6`
- `src/observability/closure_shadow.py`:
  `bd6182bdea76de1353468d37969b49b48d0d4d78363d61e626cee46d4c1aa1a2`
- `tests/test_observability_closure_shadow_v10a.py`:
  `7ae368b713d62b266c0037da0c49e9dffd62c3c668a54c84bb702b1b73a57056`
- `tools/probe_observability_closure_shadow_v10a.py`:
  `be7f7f13014339896a2177cd73d81e0ee5c9c758ae95250fb1d87599ced49eab`

## Classification

`FRESH_PHASE1B_FULLY_SOURCE_VALIDATED`

After the local checkpoint apply, those exact validated bytes are synchronized to
the control-root checkpoint surface together with this durable memory.

This is **not** runtime commissioning.

The commissioned `v0.36-repack1` runtime remains untouched until the source
checkpoint is staged, published, remotely verified, then separately synchronized
and runtime-validated.

Persistent evidence remains disabled.
