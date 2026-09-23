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
13. Preserve the human-in-the-loop repository actor boundary.

Release notes should explicitly state:

`durable_memory_updated: true`

## Deterministic artifact derivation

For deterministic checkpoint artifacts, derive expected literals, semantic
markers, paths, hashes, object identities, and assertions from the exact
source/package/result representation whenever that representation can be
inspected.

Do not invent an expected value that can be inspected. Validate the final
rendered/extracted artifact itself before delivery. The operator must not be the
first validator of deterministic generated content.

If a required safety assertion cannot be grounded in an inspectable exact
representation, stop, classify the uncertainty, or narrow the assertion rather
than substituting a guessed value.

## Publication-package boundary

A publication package is distinct from a local-update package. It is permitted
to commit/push only after an isolated stage has already passed its own validation
gate and the user explicitly runs the publication carrier.

The publication package/proven publisher must, at minimum:

1. verify exact stage ownership/sentinel where applicable;
2. verify expected base commit and exact staged tree;
3. validate cached diff/allowlist and schema-2 manifest;
4. re-check remote movement before commit;
5. verify resulting commit parent and committed tree;
6. re-check remote movement immediately before push;
7. push only the exact validated commit;
8. verify the remote branch resolves to that exact commit;
9. leave the control root and commissioned runtime untouched unless a separate
   transition explicitly authorizes them.

Do not create a phase-specific publisher when a generic/proven publisher can be
invoked through the package boundary.

## Human-in-the-loop checkpoint boundary

This section is the canonical project repository-write workflow.

Default sequence:

1. assistant performs read-only audit/reconciliation;
2. assistant constructs and validates a deterministic text `.ffpkg` local-update
   carrier with `tools/delivery/build_package.py`;
3. assistant delivers the carrier with exact scope, hashes, and validation claims;
4. user runs it through `tools\delivery\run_package.cmd` locally;
5. user returns the concise success summary, or the complete failure output;
6. assistant verifies the returned local evidence;
7. assistant provides the declarative isolated-staging invocation/spec;
8. user runs staging and returns the concise staging receipt;
9. assistant verifies the exact staged tree, manifest, allowlist, and residue
   state;
10. assistant constructs and validates a separate deterministic publication
    `.ffpkg` that invokes a generic/proven publisher under exact stage/base/tree
    guards;
11. user runs that publication carrier, explicitly authorizing commit/push for
    that validated stage;
12. assistant verifies the remote state read-only afterward.

Local-update packages stop before staging, commit, and push. Publication is a
separate package and state transition after independent staging validation. Do
not replace this multi-step publication transition with a long interactive
PowerShell block when the same guards can be carried by the package/proven
publisher boundary.

Direct GitHub connector writes are not permitted as project checkpoint writes.

## Generic `.ffpkg` delivery boundary

Delivery mechanics are permanent infrastructure, not phase-specific patch logic.
The generic runner owns text-carrier parsing, Base64/archive integrity, safe ZIP
inspection, exact payload inventory validation, isolated extraction, entrypoint
launch, exit-code propagation, and extraction cleanup.

Package-specific entrypoints own only their domain contract: target predecessor
checks, affected-scope allowlists, backup/rollback, idempotence, post-write
validation, and permitted project modifications. They may not reimplement the
transport/runner layer without a separately justified infrastructure change.

Supported package classes are `diagnostic`, `local_apply`, `runtime_sync`,
`release_install`, and `maintenance`. The first real consumer of this contract is
a durable-memory `local_apply` package.

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

## Memory / diagnostic checkpoint protocol

For memory/diagnostic checkpoints:
- inspect the current reference/remote head read-only;
- verify the authoritative local pre-state before modification;
- apply only the reviewed memory/diagnostic payload;
- validate exact generated output;
- validate a strict changed-file allowlist;
- stop before staging/commit/push;
- return the complete local output to the assistant;
- after assistant verification, stage only the reviewed allowlist;
- regenerate/validate the manifest from staged Git blob bytes;
- commit locally;
- re-check the remote head immediately before push;
- push only if the remote has not moved;
- verify the remote SHA after push.

Do not use direct GitHub connector writes as the project checkpoint mechanism.

Memory/diagnostic tooling has standing authorization; football/model/application/
business-logic changes require explicit user authorization.

## Checkpoint identity semantics

Repository publication uses different identities at different boundaries. Do not
collapse them or force active memory to predict its own future commit SHA.

1. **Local apply** — authorize affected files with package-specific predecessor
   identities and validate target/result identities. The package ID plus local
   receipt identifies the applied candidate.
2. **Isolated staging** — authorize the remote predecessor, exact reviewed
   allowlist, Git clean-filtered staged blobs, schema-2 manifest, and staged tree
   OID. The tree OID identifies staged content but is not a commit.
3. **Local commit** — verify commit SHA, parent SHA, and committed tree OID.
4. **Push/remote verification** — re-check the remote movement guard and then
   prove the remote branch/ref resolves to the exact commit SHA.

`CURRENT.md`, `CURRENT_HANDOFF.md`, and roadmap status should not require the SHA
of the commit that will contain their current text. When exact current checkpoint
identity is needed, resolve it from Git/ref context at read time.

Concrete SHAs remain appropriate in immutable evidence/history and in explicit
predecessor, commissioning, or lineage roles. Do not create a documentation-only
successor commit solely to record the SHA of the immediately preceding memory
checkpoint.

## Durable-memory manifest checkpoint semantics

`docs/memory/manifest.json` is a registry of the durable Git checkpoint
representation, not the Windows worktree byte representation.

For memory checkpoint generation:
1. apply memory changes;
2. after local apply validation and assistant review, stage all intended
   non-manifest memory files;
3. read each staged file from the Git index;
4. compute registry byte count and SHA-256 from those staged bytes;
5. write and stage `manifest.json`;
6. validate every manifest entry against the staged index;
7. commit;
8. validate every manifest entry again against `HEAD:<path>`;
9. only then push;
10. verify the remote commit SHA.

The manifest continues to exclude itself from its `files` registry.

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
- exact `.ffpkg` carrier verification, archive reconstruction/extraction, and full QA rerun.

Every successor package must have a unique `package_id` and carrier filename;
the generic runner owns isolated extraction and cleanup.

A successfully applied package should be safely rerunnable:
- validate semantic predecessor/result markers;
- return `ALREADY APPLIED` when appropriate;
- do not mistake a completed prior local apply for a wrong-state error.

Runtime reference SHA should be captured at execution and rechecked before the
later push step. Semantic state, not only a build-time SHA, determines
applicability.

## Rendered-memory cleanliness gate

Before committing generated durable memory:

1. normalize every generated Markdown line with trailing spaces/tabs removed;
2. ensure no newly rendered line ends in whitespace;
3. after user/local apply validation and assistant review, stage the exact memory
   output;
4. run `git diff --cached --check`;
5. treat any whitespace error as a package/tool validation failure;
6. run the same rendered-output regression test on the exact extracted delivery
   package before release.

Do not label a diagnostic package `PACKAGE-VALIDATED` unless the package-level
gate actually passed.

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
5. synchronize the runtime tree only when the checkpoint procedure explicitly
   reaches that authorized step;
6. if multiple runtime candidates satisfy the identity check, fail before
   modification rather than choosing heuristically.

A missing `ProjectRoot/fantasy.py` is not evidence that the application is
missing; it may indicate the normal split control/runtime layout.

## Git-checkout worktree identity (staging-clone scope only)

`git rev-parse HEAD:<path>` versus clean-filtered worktree identity is valid only
when the checkout's own `HEAD`/index is the authority for those files, such as a
fresh isolated staging clone. It is **not** the control-root local-apply rule.

For the synchronized control root, use the package's known predecessor target
identities as defined below in `Control-root pre-state authority versus
staging-clone Git authority`.

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
   temporary tree and execute the real runtime probe there;
6. do not allow preflight to report PASS if staged imports, paired behavior,
   RNG/state equivalence, or overhead gating fail.

## GUI/background-task shadow integration

For a GUI async instrumentation checkpoint:
1. preserve the existing task-creation primitive and any frozen scheduling
   expression required by regression tests;
2. when a scheduling expression is frozen, move observation inside the scheduled
   coroutine body instead of wrapping the scheduler argument;
3. preserve result identity, exception behavior, and cancellation propagation;
4. do not capture raw client IDs, arguments, returned values, or exception text;
5. treat page deletion/disconnect as observable lifecycle state, not automatic
   cancellation authority;
6. include paired RNG/state/overhead evidence and a stale-page terminal probe;
7. compile the fully patched staging tree before runtime probes/tests;
8. run established GUI source-contract tests in preflight;
9. keep persistence disabled until separately authorized.

<!-- FANTASY_LOCAL_APPLY_SEMANTIC_PRESTATE_PROTOCOL_20260920:BEGIN -->
## Local memory/diagnostic apply pre-state

For the normal human-in-the-loop sequence
`assistant package -> user local apply -> returned log -> assistant verification -> separate push commands`,
the local apply script must not use a read-only remote SHA as its sole local
pre-state authority.

Required local apply gate:
1. verify the expected repository/control root;
2. inspect only the intended memory/tooling scope for pre-existing changes;
3. validate explicit semantic or exact predecessor markers for the affected
   files;
4. validate package hashes/allowlist;
5. apply with backups and rollback;
6. run local validation;
7. leave staging/commit/push untouched.

The local `HEAD` may be reported as evidence. Remote-head comparison becomes
mandatory when the later commit/push block is prepared/executed; re-check the
remote immediately before push.
<!-- FANTASY_LOCAL_APPLY_SEMANTIC_PRESTATE_PROTOCOL_20260920:END -->

<!-- FANTASY_RENDERED_POWERSHELL_FORMAT_QA_20260920:BEGIN -->
## Rendered PowerShell format-string QA

When `.ps1` text is generated by Python or another templating language, validate
the final rendered script for PowerShell formatting semantics. In particular,
literal `-f` placeholders (`{0}`, `{1}`, ...) must not be consumed by the outer
generator. A self-test must exercise at least one representative formatted
diagnostic and verify that supplied values appear in the output.
<!-- FANTASY_RENDERED_POWERSHELL_FORMAT_QA_20260920:END -->

<!-- FANTASY_CONTROL_ROOT_PRESTATE_AUTHORITY_20260920:BEGIN -->
## Control-root pre-state authority versus staging-clone Git authority

The project control root is a synchronization surface, not automatically the Git
checkout whose local `HEAD`/index identifies the latest synchronized file state.
A successful checkpoint may commit/push from an isolated staging clone and then
copy validated files back to the control root without advancing the control
root's Git metadata.

Therefore a local-apply installer must:
1. limit pre-state validation to files it will overwrite plus paths it expects to
   create;
2. compare overwrite targets with the package's known predecessor checkpoint
   identities, not with control-root `HEAD:<path>`;
3. for tracked UTF-8 text, tolerate only representation-equivalent UTF-8 BOM and
   CRLF/CR differences when deriving the expected Git blob identity;
4. require new payload paths to be absent unless an exact already-applied package
   is detected;
5. back up only affected existing files and roll back on post-write failure;
6. never stage, commit, or push during the local-apply phase by default.

The later push stage must use an isolated staging clone. In that clone, `HEAD`,
the index, staged Git-blob bytes, remote-movement checks, and remote verification
are authoritative.

Whole-control-root status scans may be diagnostic, but they must not block a
local memory apply solely because the control root's Git metadata lags a prior
file synchronization.
<!-- FANTASY_CONTROL_ROOT_PRESTATE_AUTHORITY_20260920:END -->

<!-- FANTASY_POWERSHELL_WRAPPER_ARGUMENT_BINDING_20260920:BEGIN -->
## PowerShell native/Git wrapper argument binding

Delivered PowerShell must not use `Args` as a formal parameter name because
`$args` is an automatic variable and PowerShell names are case-insensitive.

Required QA for native/Git wrappers:
1. use a specific formal name such as `CommandArgs` or `GitArgs`;
2. statically reject formal parameters named `Args`;
3. update every named invocation to the same formal name;
4. before staging/commit/push, run a non-modifying wrapper self-test such as
   `git -C <repo> rev-parse HEAD`;
5. verify the returned value has the expected shape, proving the subcommand and
   arguments survived binding;
6. continue to evaluate native success using `$LASTEXITCODE`.
<!-- FANTASY_POWERSHELL_WRAPPER_ARGUMENT_BINDING_20260920:END -->

<!-- FANTASY_GENERIC_STAGING_REPRESENTATION_PROTOCOL_20260921:BEGIN -->
## Generic staging representation protocol

Repository checkpoint staging should use
`tools/delivery/prepare_checkpoint_stage.py` with a declarative staging spec.

The staging contract separates:
- raw control-root/worktree SHA-256 authorization;
- exact raw-byte copy into the isolated staging worktree;
- Git clean-filtered index blob identity;
- schema-2 memory-manifest SHA-256 over staged Git blob bytes.

For each reviewed source path, derive the expected index blob with the staging
checkout's own clean filters and compare Git blob OIDs. Do not compare raw
worktree SHA-256 directly with staged content, because line-ending or other
declared Git filters may change the index representation without indicating
source drift.

The generic staging engine must stop before commit/push and preserve the existing
human actor boundary.
<!-- FANTASY_GENERIC_STAGING_REPRESENTATION_PROTOCOL_20260921:END -->
