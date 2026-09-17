# Patch Protocol

Every meaningful patch/release must:

1. Identify exact source/pre-state.
2. State one narrow hypothesis/objective.
3. Preserve validated subsystem boundaries.
4. Make one coherent change.
5. Run targeted diagnostics/tests.
6. Inspect actual evidence/output.
7. Run full tests and `compileall` where applicable.
8. Validate generated artifacts, not just generator code.
9. Re-test exact delivered package for releases when environment permits.
10. Include rollback/recovery for risky local procedures.
11. Update durable memory in the same Git checkpoint.
12. Never include secrets/private raw data/caches.

Release notes should explicitly state:

`durable_memory_updated: true`

<!-- FANTASY_NATIVE_PROCESS_EXITCODE_PROTOCOL:BEGIN -->
## Native-process execution on Windows PowerShell 5.1

Patch/install/push scripts invoking native tools such as Git must distinguish
native stderr from native failure.

Required wrapper behavior:
1. preserve the current `$ErrorActionPreference`;
2. temporarily use non-terminating PowerShell error handling for the native call;
3. capture combined process output for logging;
4. capture `$LASTEXITCODE` immediately after the native call;
5. restore `$ErrorActionPreference` in `finally`;
6. fail on nonzero `$LASTEXITCODE`;
7. do not fail solely because a zero-exit native command wrote progress to stderr.
<!-- FANTASY_NATIVE_PROCESS_EXITCODE_PROTOCOL:END -->

<!-- FANTASY_GENERATED_MANIFEST_VALIDATION_PROTOCOL:BEGIN -->
## Generated manifest/registry validation

Any generated file registry must be validated after generation and before
checkpointing.

Required invariants:
1. paths are normalized repository-relative paths, never derived by raw
   absolute-string slicing;
2. the manifest does not list/hash itself unless the format explicitly uses a
   non-recursive self-integrity scheme;
3. registered paths are unique and safe (no absolute or `..` traversal paths);
4. every registered file exists;
5. every registered byte count and SHA-256 matches the actual file;
6. the set of registered paths exactly equals the set of intended actual files;
7. any invariant failure blocks commit/push.

For `docs/memory/manifest.json`, the intended set is every file recursively under
`docs/memory` except `docs/memory/manifest.json` itself.
<!-- FANTASY_GENERATED_MANIFEST_VALIDATION_PROTOCOL:END -->

<!-- FANTASY_PRIVYHUB_STYLE_PUSH_PROTOCOL:BEGIN -->
## ZIP-only checkpoint push protocol

Project repository writes should be performed through the delivered self-contained ZIP/PowerShell workflow.

For memory/diagnostic checkpoints:
- inspect the current remote head at runtime;
- clone/stage in isolation;
- apply only the reviewed memory/diagnostic payload;
- validate exact generated output;
- use an explicit staged allowlist;
- reject out-of-scope files;
- re-check the remote head immediately before push;
- push only if the remote has not moved;
- verify the remote SHA after push.

Do not use direct GitHub connector writes as the project checkpoint mechanism.

Memory/diagnostic tooling has standing authorization; football/model/application/business-logic changes require explicit user authorization.
<!-- FANTASY_PRIVYHUB_STYLE_PUSH_PROTOCOL:END -->

<!-- FANTASY_MANIFEST_GIT_BLOB_PROTOCOL:BEGIN -->
## Durable-memory manifest checkpoint semantics

`docs/memory/manifest.json` is a registry of the durable Git checkpoint
representation, not the Windows worktree byte representation.

For memory checkpoint generation:
1. apply memory changes;
2. stage all intended non-manifest memory files;
3. read each staged file from the Git index;
4. compute registry byte count and SHA-256 from those staged bytes;
5. write and stage `manifest.json`;
6. validate every manifest entry against the staged index;
7. commit;
8. validate every manifest entry again against `HEAD:<path>`;
9. only then push;
10. verify the remote commit SHA.

The manifest continues to exclude itself from its `files` registry.
<!-- FANTASY_MANIFEST_GIT_BLOB_PROTOCOL:END -->

<!-- FANTASY_DIAGNOSTIC_QA_RELEASE_GATE:BEGIN -->
## Diagnostic-tool release gate

Diagnostic/probe/observability tooling has standing development authorization,
but delivery requires its own QA gate.

For Python diagnostics, where applicable:
- `py_compile`;
- undefined-global/static symbol audit;
- helper-path execution tests;
- both success and controlled-failure branch tests;
- classifier boundary/regression tests;
- temporary-resource cleanup tests;
- schema-2 Git index/HEAD manifest tests;
- exact-ZIP extraction and full QA rerun.

Every successor package must have a unique ZIP name and recommended extraction
directory.

A successfully applied package should be safely rerunnable:
- validate semantic predecessor/result markers;
- return `ALREADY APPLIED` when appropriate;
- do not mistake its own successful remote advancement for a wrong-state error.

Runtime remote SHA should be captured at execution and rechecked immediately
before push. Semantic state, not only a build-time SHA, determines applicability.
<!-- FANTASY_DIAGNOSTIC_QA_RELEASE_GATE:END -->

<!-- FANTASY_RENDERED_MEMORY_CLEANLINESS_GATE:BEGIN -->
## Rendered-memory cleanliness gate

Before committing generated durable memory:

1. normalize every generated Markdown line with trailing spaces/tabs removed;
2. ensure no newly rendered line ends in whitespace;
3. stage the exact memory output;
4. run `git diff --cached --check`;
5. treat any whitespace error as a package/tool validation failure;
6. run the same rendered-output regression test on the exact extracted delivery
   package before release.

Do not label a diagnostic package `PACKAGE-VALIDATED` unless this gate passes.
<!-- FANTASY_RENDERED_MEMORY_CLEANLINESS_GATE:END -->

<!-- FANTASY_CONTROL_ROOT_RUNTIME_TREE_PROTOCOL_20260917:BEGIN -->
## Control root versus runnable release tree

For application-source patches, never infer that the checkpoint/control root is
also the runnable installed release.

Required procedure:
1. establish the commissioned release-directory contract from release evidence;
2. validate the candidate runtime tree using `VERSION` and predecessor source
   identity before any modification;
3. treat Git staging, control-root memory/tooling, and runtime-tree files as
   separate synchronization surfaces;
4. back up runtime files independently from control-root files;
5. only synchronize the runtime tree after repository validation, commit/push,
   and remote verification succeed;
6. if multiple runtime candidates satisfy the identity check, fail before
   modification rather than choosing heuristically.

A missing `ProjectRoot/fantasy.py` is not evidence that the application is
missing; it may indicate the normal split control/runtime layout.
<!-- FANTASY_CONTROL_ROOT_RUNTIME_TREE_PROTOCOL_20260917:END -->

<!-- FANTASY_GIT_OBJECT_PRESTATE_PROTOCOL_20260917:BEGIN -->
## Tracked-text pre-state identity

When an installer validates a local/control/runtime copy of a tracked text file,
the committed Git object is the authority. A fresh checkout's raw bytes are not.

Required procedure:
1. obtain expected bytes from `HEAD:<path>`;
2. compare the local file with CRLF/CR normalized to LF on both sides;
3. do not normalize any other byte/content difference;
4. validate the complete expected path set where a directory mirror is required;
5. include diagnostic normalized hashes when a mismatch blocks the patch.

This rule prevents Windows checkout line-ending representation from being
misclassified as repository drift.
<!-- FANTASY_GIT_OBJECT_PRESTATE_PROTOCOL_20260917:END -->

<!-- FANTASY_RUNTIME_PROBE_CONTEXT_PROTOCOL_20260917:BEGIN -->
## Application probe execution context

A runtime/application probe must execute under the same import-root boundary as
the application it validates.

Required procedure:
1. use the validated staged/runtime application root as `cwd`;
2. explicitly prepend that root to `PYTHONPATH`;
3. preserve pre-existing `PYTHONPATH` entries after the validated root;
4. run an import-context regression that fails without the root and passes with
   it;
5. make non-modifying preflight apply the candidate patch only to an isolated
   temporary clone and execute the real runtime probe there;
6. do not allow preflight to report PASS if staged imports, paired behavior,
   RNG/state equivalence, or overhead gating fail.

Production/local trees remain untouched until the full repository checkpoint is
validated, committed, pushed, and remotely verified.
<!-- FANTASY_RUNTIME_PROBE_CONTEXT_PROTOCOL_20260917:END -->
