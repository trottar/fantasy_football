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
