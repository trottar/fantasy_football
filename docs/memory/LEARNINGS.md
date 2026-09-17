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

<!-- FANTASY_RENDERED_MEMORY_WHITESPACE_LEARNING:BEGIN -->
## Generated memory must be validated as rendered text

A diagnostic package can pass Python/runtime helper QA and still fail its actual
checkpoint if generated memory content is not validated.

New rule:
- normalize generated Markdown line-by-line;
- remove trailing spaces/tabs from every generated line;
- validate representative rendered memory before packaging;
- rerun the same rendered-output validation against the exact delivered ZIP;
- only then claim `PACKAGE-VALIDATED`.

A package that fails `git diff --check` on its own generated memory was not fully
package-validated, regardless of prior synthetic QA claims.
<!-- FANTASY_RENDERED_MEMORY_WHITESPACE_LEARNING:END -->

<!-- FANTASY_HASH_ALGORITHM_REPRESENTATION_RULE:BEGIN -->
## Hash algorithm and representation must match

A Git blob object ID and a SHA-256 checksum of file bytes are different
representations and must never be compared as if they were the same value.

For every hash guard, state all three explicitly:
1. authority layer (`worktree`, staged index, committed `HEAD`, remote object);
2. byte/object representation being hashed;
3. hash/object-ID algorithm and expected length.

Examples:
- Git blob predecessor guard: compare `git rev-parse HEAD:<path>` to an expected
  Git blob object ID from the same Git repository/object model;
- file-byte integrity guard: compare SHA-256 to SHA-256 over the same bytes;
- schema-2 memory manifest: compare SHA-256 over staged/committed Git blob bytes,
  not a Git object ID and not normalized worktree bytes.

A length mismatch (for example 64-character SHA-256 versus 40-character Git
blob OID) is itself evidence of a representation error and must fail QA before
delivery.
<!-- FANTASY_HASH_ALGORITHM_REPRESENTATION_RULE:END -->

<!-- FANTASY_LEARNING_CONTROL_ROOT_VS_RUNTIME_TREE_20260917:BEGIN -->
## Separate checkpoint/control root from runnable release tree

`L:\Projects\fantasy_football` is the checkpoint/control root. The commissioned
v0.36-repack1 application tree is a distinct installed release directory created
by the release workflow.

An installer that touches application source must not assume
`ProjectRoot/<repository-path>` is runnable. It must:
1. use the established release-directory contract when available;
2. verify `VERSION` plus exact/normalized predecessor source identity;
3. fail before modification if the runnable tree is missing or ambiguous;
4. keep control-root synchronization and runtime-tree synchronization separate;
5. back up and roll back both surfaces independently.

This rule is distinct from Git staging authority and from artifact ZIP identity.
<!-- FANTASY_LEARNING_CONTROL_ROOT_VS_RUNTIME_TREE_20260917:END -->

<!-- FANTASY_LEARNING_GIT_OBJECT_VS_WORKTREE_PRESTATE_20260917:BEGIN -->
## Compare checkpoint identity at the Git-object layer

A committed text file and a Windows working-tree checkout can represent the same
content with different line endings. Fresh-clone worktree bytes are therefore
not a valid byte-for-byte authority for a previously synchronized control tree.

For pre-state guards on tracked text:
1. read expected content from the committed object (`git show HEAD:<path>`);
2. compare local content after normalizing CRLF/CR to LF only;
3. preserve every other byte distinction;
4. fail on path-set changes or any non-line-ending content change;
5. report normalized hashes on failure.

Do not compare independently checked-out working-tree bytes as if they were Git
object identity.
<!-- FANTASY_LEARNING_GIT_OBJECT_VS_WORKTREE_PRESTATE_20260917:END -->

<!-- FANTASY_LEARNING_RUNTIME_PROBE_EXECUTION_CONTEXT_20260917:BEGIN -->
## Runtime probes must reproduce the application import context

Executing `python tools/probe.py` makes the probe directory the leading Python
import location; it is not equivalent to launching `python fantasy.py` from the
application root.

For application/runtime probes:
1. set the working directory to the validated application/repository root;
2. prepend that root to `PYTHONPATH` explicitly;
3. preserve any existing `PYTHONPATH` after the validated root;
4. include a negative regression that reproduces the missing-root import
   failure;
5. include a positive regression proving imports work under the corrected
   environment;
6. make preflight execute the actual staged patch plus runtime probe before it
   can report `PASS`.

A file-existing check or successful compile is not runtime-context validation.
<!-- FANTASY_LEARNING_RUNTIME_PROBE_EXECUTION_CONTEXT_20260917:END -->
