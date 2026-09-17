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
