# v1.0A Data-Source Season-Sync Shadow Pilot — Preflight Evidence

## Authority

Remote predecessor:
`8592989b78b6e94cd08d8618694b8168c62cf715`.

Commissioned runtime baseline:
`v0.36-repack1`.

Runtime tree modification during these attempts: **NO**.

## Narrow Hypothesis

The outer `sync_season_snapshot` boundary can be observed with bounded in-memory
correlation/timing/error-type evidence without changing returned data, exception
behavior, filesystem effects, Python RNG state, or authenticated-data privacy.

## Attempt v1

Package:
`fantasy_v10a_data_source_shadow_pilot_v1.zip`

SHA-256:
`f18adafc9ac9b309b0802483ae22cb236f61f20b36593d387cdcf8795011d2f0`

Classification:
`FAILED BEFORE MODIFICATION`.

Failure:
its prestate verifier incorrectly required `src/season_snapshot.py` under the
control root `L:\Projects\fantasy_football`, contradicting the established
control-root/application-source separation.

No source, memory, runtime, Git-index, commit, or remote state changed.

## Attempt v2

Package:
`fantasy_v10a_data_source_shadow_pilot_v2.zip`

SHA-256:
`96e808f828e282a54378e7a2ad12682b88b7c31bc16cf50c13daa0a709574106`

The corrected package established:

- package integrity/static QA: PASS;
- helper self-test: PASS;
- control-root memory-only regression self-test: PASS;
- observed remote HEAD matched expected predecessor: PASS;
- isolated exact-remote clone HEAD guard: PASS;
- source patch in isolated clone: PASS;
- candidate memory rendering: PASS;
- targeted observability tests: **39 passed in 7.37 s**.

It then launched the deterministic probe with:

`python tools/probe_observability_data_source_shadow_v10a.py ...`

without explicitly prepending the repository root to `PYTHONPATH`. Python used
the `tools` directory as the leading import location and failed with:

`ModuleNotFoundError: No module named 'src'`.

Classification:
`FAILED BEFORE CONTROL-ROOT MODIFICATION / PROBE LAUNCH CONTEXT DEFECT`.

The isolated candidate was retained for diagnosis. The source candidate itself
had not failed.

## Manual Corrected Probe Retry

The retained candidate was rerun with:

- working directory = retained repository root;
- `PYTHONPATH` prepended with that repository root.

Result:
`PROBE RETRY PASS`.

Measured JSON evidence:

- schema: 1;
- boundary: `subsystem.data_source.season_sync`;
- success behavior preserved: true;
- outputs equal: true;
- exception behavior equal: true;
- error type equal: true;
- original error message preserved to caller: true;
- paired state probes equal: true;
- probe names: `python_random`, `snapshot_tree`;
- arguments captured: false;
- return values captured: false;
- exception messages captured: false;
- persistent sink: false;
- privacy success check: true;
- privacy error check: true;
- event shape: true;
- trials: 15;
- baseline median: **1,123,700 ns**;
- observed median: **1,296,200 ns**;
- incremental overhead: **172,500 ns**;
- relative overhead fraction: **0.15351072350271425**;
- absolute overhead gate: PASS;
- relative overhead gate: PASS;
- overall benchmark: PASS.

## Full Repository Validation Continuation

Validation resumed from the retained candidate without rerunning the targeted
tests or paired probe.

Results:

- full repository pytest: **459 passed in 52.73 s**;
- full repository compileall: **PASS**.

## Candidate Diff / Allowlist Validation

Read-only candidate inspection then established:

- `git diff --check`: PASS;
- LF-to-CRLF messages were conversion warnings only; no whitespace error was
  reported;
- initial `git status --short` contained the intended candidate paths plus one
  temporary manual-probe output, `_probe_data_source_shadow_retry.json`;
- that JSON was removed as probe output, not repository evidence;
- final status contained exactly the 14 intended candidate paths.

The 14 paths are a candidate-local validation set. They include candidate memory
that predates subsequent control-root memory micro-checkpoints. Therefore the
future staging checkpoint must not copy candidate memory wholesale. It must take
only the four validated source/test/probe paths from the retained candidate and
combine them with the latest control-root durable memory before deriving the
final staged allowlist and schema-2 manifest.

## Current Evidence Class

`SOURCE CANDIDATE PRE-STAGING VALIDATED / EXACT 14-PATH CANDIDATE ALLOWLIST / CONTROL ROOT SOURCE UNCHANGED / RUNTIME UNCHANGED`

Not yet claimed:

- repository commit/push/remote verification;
- commissioned-runtime synchronization/commissioning.

## Durable Workflow Lesson

Two distinct package errors occurred before the candidate reached its full gate.
After such a failure, resume from the last validated state and execute the next
single gate directly. Do not rerun unrelated passed work unless new evidence
invalidates it.

The existing runtime-probe import-context rule remains authoritative: repository
root as `cwd`, repository root explicitly prepended to `PYTHONPATH`, and the
actual launcher path tested.

## Fresh Staging-Clone Assembly Preflight

A fresh isolated staging clone was created from remote
`8592989b78b6e94cd08d8618694b8168c62cf715` and its `HEAD` matched exactly.

The staging clone was assembled incrementally rather than by copying the retained
candidate wholesale:

- the four validated technical files were copied from the retained candidate;
- all four were SHA-256 byte-identical to the files already exercised by the
  targeted/full tests and paired probe;
- the current control-root durable-memory delta versus the fresh clone was
  measured as exactly 10 paths, excluding `docs/memory/manifest.json`;
- those 10 memory paths were copied from the control root and confirmed
  byte-identical;
- combined staging-clone working-tree status contained exactly 14 intended paths;
- strict memory health: **HEALTHY**;
- combined `git diff --check`: PASS.

The 14 intended paths were then staged. The staged allowlist was exact and there
was no unstaged or untracked residue.

## Schema-2 Manifest Preflight

`docs/memory/manifest.json` was regenerated from the **staged Git blob bytes**,
not from Windows worktree bytes.

Validation results:

- schema: `2`;
- representation: `git_index_blob_bytes`;
- durable memory updated: true;
- manifest entries: **100**;
- staged path count including manifest: **15**;
- exact 15-path staged allowlist: PASS;
- unstaged residue: none;
- untracked residue: none;
- cached `git diff --check`: PASS.

The manifest-generation script completed with exit code 0 and the staging status
showed the expected 15 staged paths, including modified
`docs/memory/manifest.json`.

## Pre-Commit Memory Closure Rule

This v4 memory checkpoint records the staging/manifest preflight after it was
measured. Consequently, the staging clone's current manifest predates this v4
control-root memory state and is **not yet the final commit-ready manifest**.

Before commit, refresh only the v4-updated memory files into the existing staging
clone, re-stage those paths, regenerate the schema-2 manifest from the resulting
staged Git blobs, and repeat the staged allowlist/residue/cached-diff checks.
That final refresh is execution of an already-recorded rule; do not open another
recursive pre-commit memory bookkeeping checkpoint.

## Current Evidence Class

`STAGING PREFLIGHT VALIDATED / SCHEMA-2 MANIFEST PREFLIGHT PASS / 15 PATHS STAGED / NOT COMMITTED / RUNTIME UNCHANGED`

Repository commit/push/read-only remote verification and commissioned-runtime
synchronization remain separate future gates.
