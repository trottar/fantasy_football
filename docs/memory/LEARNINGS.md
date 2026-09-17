# Durable Learnings

1. Git history is not a substitute for the actual validated working tree.
2. Never equate planned validation with passed validation.
3. Validate generated output, not merely the generator.
4. If a classifier contradicts raw measurement, inspect the measurement/classifier boundary first.
5. Do not opportunistically improve stable subsystems during unrelated fixes.
6. Historical baseline imports preserve the historical tree; style cleanup belongs in explicit later patches.
7. Source correctness and runtime commissioning are distinct claims.
8. Structural representation defects can justify immediate architectural fixes; empirical calibration requires evidence.
9. One week of outcomes can open investigations but does not justify broad retuning.
10. Manager behavior is not football physics.
11. `screen != authority` is durable.
12. Local/private evidence can remain outside Git while sanitized durable conclusions are committed.

<!-- FANTASY_WINDOWS_NATIVE_STDERR_RULE:BEGIN -->
## Windows PowerShell native-process stderr rule

On Windows PowerShell 5.1, native tools can write legitimate progress text to
stderr. Under `$ErrorActionPreference = 'Stop'`, that stderr can surface as a
terminating `NativeCommandError` before the script evaluates `$LASTEXITCODE`.

For Git/native-process wrappers:
- temporarily use non-terminating PowerShell error handling during the native call;
- capture stdout/stderr for diagnostics;
- capture `$LASTEXITCODE` immediately after the native call;
- restore the caller's PowerShell error preference in `finally`;
- treat nonzero native exit code as failure;
- never treat zero-exit stderr/progress text alone as failure.

This rule was established by the 2026-09-17 memory-checkpoint clone failure.
<!-- FANTASY_WINDOWS_NATIVE_STDERR_RULE:END -->

<!-- FANTASY_POWERSHELL_VARIABLE_COLON_RULE:BEGIN -->
## Windows PowerShell variable-colon interpolation rule

In double-quoted PowerShell strings, avoid an unbraced variable immediately
followed by a colon, for example:

`"$rel: message"`

PowerShell can interpret the colon as part of a scoped/drive-style variable
reference and fail at parse time.

Use one of these forms instead:
- `"${rel}: message"`
- `("{0}: message" -f $rel)`

For delivered PowerShell packages, statically scan for `$name:` patterns inside
double-quoted strings when practical. A parser-level failure is classified
`FAILED BEFORE MODIFICATION` because no script body executes.
<!-- FANTASY_POWERSHELL_VARIABLE_COLON_RULE:END -->

<!-- FANTASY_MANIFEST_GIT_REPRESENTATION_RULE:BEGIN -->
## Registry representation must match the authority being verified

A manifest generated from Windows worktree bytes can disagree with the committed
Git blob when line-ending normalization is active even though the logical text
is unchanged.

If a registry is intended to verify a Git checkpoint, its bytes/hashes must be
computed from the staged Git index representation (and then checked against the
committed `HEAD` representation), not from the platform worktree representation.

Keep these concepts explicit:
- worktree-byte integrity;
- staged/index-byte integrity;
- committed Git-blob integrity.

Do not claim one from validation of another.
<!-- FANTASY_MANIFEST_GIT_REPRESENTATION_RULE:END -->

<!-- FANTASY_DIAGNOSTIC_RELEASE_GATE_LEARNING:BEGIN -->
## Diagnostic tools require runtime-path QA, not only syntax QA

`py_compile` plus a narrow synthetic test is not sufficient for checkpoint
diagnostic tooling.

Before delivery, diagnostic tooling must execute the same important helper paths
used in runtime, including success and failure branches.

Minimum release gate:
1. Python compile/syntax validation;
2. undefined-global / symbol-table audit;
3. direct helper-function execution tests;
4. success and expected-failure branch tests;
5. classifier boundary tests;
6. cleanup/finally tests;
7. Git index + committed-HEAD manifest tests where applicable;
8. exact delivered-ZIP extraction;
9. rerun the full QA gate against the exact extracted ZIP.

A diagnostic package that does not exercise its runtime-critical path is not
package-validated.
<!-- FANTASY_DIAGNOSTIC_RELEASE_GATE_LEARNING:END -->
