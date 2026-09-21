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
## Pre-state authority depends on the synchronization surface

A Git object comparison is valid only when the Git metadata being compared is
the authority for that working surface.

The project control root can be synchronized from an isolated staging clone
after remote verification without advancing the control root's own local
`HEAD`/index. In that state, comparing every control-root file to local
`HEAD:<path>` creates systematic false drift even when the synchronized files are
correct.

Required separation:
1. **local apply:** validate only package overwrite targets against the package's
   known predecessor checkpoint identities; for tracked UTF-8 text, canonicalize
   UTF-8 BOM and CRLF/CR representation before comparing the expected Git blob;
2. **local unrelated files:** do not scan/authorize them merely because the
   control root's Git metadata is stale;
3. **push staging clone:** the fresh isolated clone's `HEAD`, index, and staged
   blobs are authoritative for allowlist, manifest, commit, and push;
4. **remote:** re-check remote movement immediately before push and verify the
   pushed SHA afterward.

This supersedes the earlier over-general rule that local control-root text should
always be compared with its own `HEAD:<path>`.
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

<!-- FANTASY_LEARNING_GUI_SHADOW_LIFECYCLE_20260917:BEGIN -->
## Observe GUI lifecycle without becoming lifecycle policy

Background-task diagnostics must preserve the framework's existing scheduling,
cancellation, and exception behavior. Page/client lifecycle events are evidence,
not permission for the observer to cancel, retry, mutate, or suppress work.

Use generated correlation IDs rather than raw framework client identifiers.
A task terminal event after page deletion should be classified with explicit
lifecycle-violation evidence while returning/raising exactly as the production
task would have done.
<!-- FANTASY_LEARNING_GUI_SHADOW_LIFECYCLE_20260917:END -->

<!-- FANTASY_LEARNING_PRESERVE_GUI_SCHEDULING_CONTRACTS_20260917:BEGIN -->
## Preserve established GUI scheduling contracts during observation

Source-shape regression tests can encode real concurrency/lifecycle contracts.
When an existing test freezes a scheduling expression such as
`background_tasks.create(apply_mc_size(new_n))` or
`asyncio.create_task(progress_pump())`, observability must not rewrite that
scheduler boundary merely because an equivalent awaitable wrapper seems
semantically harmless.

Keep the scheduler expression intact and move observation inside the scheduled
coroutine. Include the frozen source-contract tests in preflight before apply.
<!-- FANTASY_LEARNING_PRESERVE_GUI_SCHEDULING_CONTRACTS_20260917:END -->

<!-- FANTASY_LEARNING_BOOTSTRAP_AND_ACTOR_BOUNDARY_20260918:BEGIN -->
## Continuity rules must be executable, not merely present somewhere

A project can contain the correct procedure and still fail operationally if a
fresh session is not required to read it.

For substantial work:
- read the complete bootstrap set in `AGENTS.md`;
- read the current handoff before acting;
- if repository changes are possible, read `patches/PATCH_PROTOCOL.md`;
- do not infer the workflow from previous chat recollection.

Repository actor separation is itself a safety invariant:
assistant constructs the package; the user executes it locally; the assistant
verifies returned output; only then does the assistant provide separate push
commands for the user to execute.

Direct repository mutation through a connector bypasses this evidence boundary
and must not be used.
<!-- FANTASY_LEARNING_BOOTSTRAP_AND_ACTOR_BOUNDARY_20260918:END -->

<!-- FANTASY_LOCAL_APPLY_HEAD_AUTHORITY_20260920:BEGIN -->
## Local apply pre-state is not remote-head equality

A read-only GitHub SHA is history/reference state. It is not automatically the
required `HEAD` of the authoritative local control tree. For a package whose
job is only to update local memory/tooling before a later human-reviewed push,
do not block solely because local `git rev-parse HEAD` differs from the remote
reference observed when the package was built.

Local apply authorization should instead establish:
1. the expected repository/control root;
2. no pre-existing changes on the exact affected scope;
3. semantic/exact predecessor identity for the affected files;
4. package integrity and allowlist;
5. post-write validation with rollback on failure.

Remote movement/equality belongs to the later commit/push stage, after the user
returns the local apply output and the assistant verifies it.
<!-- FANTASY_LOCAL_APPLY_HEAD_AUTHORITY_20260920:END -->

<!-- FANTASY_GENERATED_POWERSHELL_FORMAT_PLACEHOLDER_20260920:BEGIN -->
## Preserve PowerShell format placeholders through code generation

When another language generates PowerShell containing the `-f` operator, literal
PowerShell placeholders such as `{0}` and `{1}` must survive generation. Python
f-strings, `.format`, templating engines, or replacement layers can consume the
braces and silently render broken diagnostics such as `expected HEAD=0 actual
HEAD=1`.

Package QA must inspect the rendered `.ps1`, not only the generator, and execute
a self-test that proves representative formatted messages contain the supplied
values. Prefer template substitution that does not interpret PowerShell braces.
<!-- FANTASY_GENERATED_POWERSHELL_FORMAT_PLACEHOLDER_20260920:END -->

<!-- FANTASY_LEARNING_CONTROL_ROOT_TARGET_AUTHORITY_20260920:BEGIN -->
## Control-root local apply uses package predecessor authority, not local Git metadata

The synchronized control root can contain checkpoint files newer than its local
Git `HEAD`/index. Therefore neither raw porcelain nor a cleaned worktree blob
compared with local `HEAD:<path>` is sufficient local-apply authority there.

For control-root memory/diagnostic apply:
1. validate only package overwrite/create targets;
2. compare overwrite targets with identities from the known predecessor
   checkpoint embedded in the package;
3. require expected-new paths to be absent unless the exact package is already
   applied;
4. keep the control-root Git metadata informational;
5. use a fresh isolated staging clone for `HEAD`/index/manifest/commit/push
   authority.

This supersedes the earlier v3-v5 whole-control-root `HEAD` drift classifiers.
<!-- FANTASY_LEARNING_CONTROL_ROOT_TARGET_AUTHORITY_20260920:END -->

<!-- FANTASY_LEARNING_POWERSHELL_ARGS_COLLISION_20260920:BEGIN -->
## Never name a PowerShell formal parameter `Args`

PowerShell defines `$args` as an automatic variable and names are
case-insensitive. A helper declared with a formal parameter such as
`[string[]]$Args` can therefore lose the caller's intended argument array.

For native/Git wrappers:
- use `GitArgs` or `CommandArgs`, never `Args`;
- update all named call sites consistently;
- statically reject formal parameters named `Args`;
- execute a real non-modifying wrapper command before any modifying Git action
  and assert that the expected subcommand/output is present.

This rule was established by the 2026-09-20 memory-reconciliation push-v1
failure, where `rev-parse HEAD` became bare `git -C <repo>`.
<!-- FANTASY_LEARNING_POWERSHELL_ARGS_COLLISION_20260920:END -->


<!-- FANTASY_LEARNING_CANONICAL_SOURCE_BEFORE_SUMMARY_20260920:BEGIN -->
## A decision record is a source, not a summary

Before restating what a decision, gate, classification, deadline, or stable
constraint says, read the canonical record that defines it. Repeating a previous
summary can silently propagate missing qualifiers or superseded wording.

Use active memory as an index into canonical decisions/evidence/architecture,
not as a substitute for them.
<!-- FANTASY_LEARNING_CANONICAL_SOURCE_BEFORE_SUMMARY_20260920:END -->

<!-- FANTASY_LEARNING_IRREVERSIBLE_PROSPECTIVE_WINDOWS_20260920:BEGIN -->
## Prospective capture windows are irreversible

Code can be written later; a missed pregame information state cannot be
recreated causally after outcomes are known.

During the NFL season:
- protect week-open and consequential decision-time captures before relevant
  games/outcomes;
- if a capture is missed, record the missing measurement;
- do not backfill and label it prospective;
- let nonessential development slip before sacrificing an irreversible evidence
  window;
- do not confuse a calendar deadline with evidence that a calibration gate has
  passed.
<!-- FANTASY_LEARNING_IRREVERSIBLE_PROSPECTIVE_WINDOWS_20260920:END -->

<!-- FANTASY_LEARNING_MEMORY_THRESHOLD_PACKAGE_QA_20260920:BEGIN -->
## Package QA must exercise real memory-health semantics

A documentation package can be syntactically correct and still be invalid if
its rendered bootstrap files cross active maintenance thresholds. Synthetic QA
that replaces the production memory-health semantics with a permissive stub is
not sufficient.

For memory packages, validate rendered target bytes/line counts before delivery
and execute the repository's real strict memory-health checker in the local
apply path. A soft-threshold failure is a maintenance signal: relocate detail to
typed roadmap/evidence/context records rather than weakening the checker.

This rule was established when `fantasy_memory_season_roadmap_v1` correctly
rolled back after its proposed `MEMORY.md` reached 387 lines against the 350-line
soft threshold.
<!-- FANTASY_LEARNING_MEMORY_THRESHOLD_PACKAGE_QA_20260920:END -->

<!-- FANTASY_LEARNING_INTERACTIVE_POWERSHELL_CONTROL_FLOW_20260921:BEGIN -->
## Interactive PowerShell control flow must survive paste boundaries

When giving a micro-step intended for direct interactive pasting, do not rely on
`elseif`/`else` clauses being submitted in the same parser unit as a preceding
`if`. A console/editor can split the submission and make the later clause execute
as an invalid command.

Prefer either:
- one complete `.ps1` file for multi-branch control flow; or
- independent `if` blocks when the step is intentionally pasted interactively.

For successful micro-steps, print one concise final summary block so the operator
can return only that block. Full logs remain appropriate on failure or when an
omitted measurement is required.
<!-- FANTASY_LEARNING_INTERACTIVE_POWERSHELL_CONTROL_FLOW_20260921:END -->

<!-- FANTASY_LEARNING_GENERIC_DELIVERY_INFRASTRUCTURE_20260921:BEGIN -->
## Delivery mechanics belong in reusable infrastructure

The Phase 1B checkpoint exposed several delivery-path defects that were unrelated
to football or observability logic:

- binary ZIP attachments repeatedly arrived as zero-byte files;
- long clipboard/Base64 chunk transport was error-prone and operationally noisy;
- an unconditional PowerShell PASS line could execute after a prior command
  failed;
- interactive `else` parsing repeated a known PowerShell 5.1 paste-boundary
  failure;
- phase-specific wrappers duplicated execution mechanics;
- an initially silent bootstrap provided poor operator feedback.

The architectural correction is a permanent generic delivery layer:
`build_package.py` produces deterministic text `.ffpkg` carriers and
`run_package.cmd`/`run_package.py` own validation, extraction, entrypoint launch,
and exit propagation. Package-specific code is limited to its actual target
contract.

Operational rules:
1. prefer the generic runner over chat-assembled command sequences;
2. use text carriers when binary attachment transport is unreliable;
3. success output must be conditional on actual successful control flow;
4. long-running installers print an immediate splash and flushed progress;
5. validate the exact delivered carrier and its reconstructed archive;
6. do not make the user the first validator of deterministic package code.
<!-- FANTASY_LEARNING_GENERIC_DELIVERY_INFRASTRUCTURE_20260921:END -->

<!-- FANTASY_LEARNING_STAGE_FILTER_REPRESENTATION_20260921:BEGIN -->
## Staging identity must compare the same representation

The first generic staging attempt correctly failed on a bad declarative D-025
marker before modification. After that marker was corrected, staging reached the
final identity gate and exposed a deeper infrastructure defect: the helper
compared the raw control-root SHA-256 of `run_package.cmd` with staged Git blob
bytes.

That comparison is invalid when Git clean filters normalize text, such as
CRLF-to-LF conversion. It repeated the already-established rule that worktree,
index, and committed representations are distinct.

Permanent rule:
1. authorize the copied source with a raw worktree-byte SHA-256;
2. copy bytes exactly into the isolated staging worktree;
3. derive the expected staged Git blob OID using the staging checkout's clean
   filters (`git hash-object --path ... --stdin`);
4. compare that Git blob OID to the index blob OID;
5. generate memory-manifest SHA-256 values from staged Git blob bytes.

Never compare a raw worktree SHA-256 directly with staged bytes.
<!-- FANTASY_LEARNING_STAGE_FILTER_REPRESENTATION_20260921:END -->
