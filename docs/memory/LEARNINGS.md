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
