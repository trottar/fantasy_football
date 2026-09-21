# Tools and Proven Procedures

## Environment

- Local root: `L:\Projects\fantasy_football\`
- Primary shell: Windows PowerShell 5.1
- Repository: `trottar/fantasy_football`

Current release/project state belongs in `CURRENT.md`, not in this file.

## Repository Write Workflow

For multi-step memory/diagnostic work, use a self-contained ZIP plus a
PowerShell 5.1-compatible `.ps1` entry point.

Actor flow:

`assistant package -> user local apply/validate -> return output -> assistant verify -> separate staging/push block -> user push -> remote verification`

The control root and push staging clone have different authority roles:

- **control root local apply:** validate only package targets against the known
  predecessor checkpoint contract; do not require local `HEAD` equality and do
  not treat whole-tree `git status` as apply authority;
- **isolated staging clone:** inspect current remote head, apply the verified
  local payload, stage the exact allowlist, regenerate/validate the Git-blob
  manifest, commit, re-check remote movement, push, and verify remote SHA;
- **runtime tree:** synchronize separately only when the checkpoint actually
  changes runtime/application files.

Detailed mechanics: `patches/PATCH_PROTOCOL.md`.
Direct GitHub-connector writes are not project checkpoint pushes.

## Public / Private Boundary

Tracked/public may include:
- source and tests;
- non-secret config;
- durable memory;
- sanitized evidence;
- public-safe fixtures.

Keep local:
- `config/secrets.json`;
- `.env*` and keys;
- ESPN cookies / SWID / `espn_s2`;
- raw authenticated API responses;
- private account identifiers;
- sensitive runtime snapshots;
- caches/temp files.

## Validation

For meaningful releases/tooling, use the applicable subset of:
- targeted tests;
- full pytest;
- `compileall`;
- `git diff --check`;
- strict memory health;
- exact changed/staged allowlist;
- package CRC/integrity;
- exact delivered-ZIP extraction;
- exact-package retest;
- runtime commissioning where local data/UI is required.

Never claim a validation not actually executed.

Keep these states distinct:
- package constructed;
- package validated;
- local preflight passed;
- local apply passed;
- committed;
- pushed;
- remote verified;
- runtime synchronized/commissioned.

## Git / Manifest Representation

`docs/memory/manifest.json` represents staged/committed Git blob bytes, not
Windows worktree bytes.

Authority:
- pre-commit: staged index bytes;
- post-commit: `HEAD:<path>` bytes;
- post-push: verified remote commit SHA.

The manifest excludes itself.

Because the manifest represents staged/committed bytes, a local apply package
does not finalize the manifest before the later commit/push step. The push
commands/procedure must regenerate and validate it from the staged index.

## Windows Native Commands

PowerShell 5.1 may surface normal native stderr as `NativeCommandError` under
`$ErrorActionPreference = 'Stop'`.

Judge native success from `$LASTEXITCODE`; preserve/restore PowerShell error
preference around native calls.

Avoid unsafe `"$variable:"` interpolation; prefer `${variable}:` or `-f`.

Reusable incident-derived rules live in `LEARNINGS.md`.

Never use `Args` as a PowerShell function/script formal parameter name.
PowerShell already defines `$args` as an automatic variable; use `GitArgs` or
`CommandArgs` and execute a non-modifying wrapper self-test before staging.

## Diagnostic Tool QA

Diagnostic/observability tools are software under test. Apply the release gate
in `patches/DIAGNOSTIC_TOOL_QA_PROTOCOL.md` and
`patches/PATCH_PROTOCOL.md`, including exact-ZIP QA and rendered-memory
cleanliness where applicable.

## Memory Health

Run:

```powershell
python .\tools\check_memory_health.py --root L:\Projects\fantasy_football
```

Use `--strict` at maintenance checkpoints. The tool is observational and never
rewrites repository files.

## Local-apply versus remote-head checks

A local memory/diagnostic apply package may print the local `HEAD` and the remote
reference used during construction, but it must not equate them as a mandatory
precondition unless that equality is specifically part of the checkpoint
contract. Before the later push, re-read the remote head and enforce the
remote-moved guard there.

For generated PowerShell, validate the final rendered script so `-f` placeholders
remain literal `{0}`, `{1}`, etc. A generator-level test is insufficient.

## Control-root target identity for local apply

The synchronized control root can contain checkpoint files newer than its own
local Git `HEAD`/index. Do not compare local apply targets against control-root
`HEAD:<path>`.

For a control-root memory/diagnostic apply:
- validate only files the package will overwrite/create;
- compare overwrite targets with the package's known predecessor checkpoint
  identities;
- require expected-new paths to be absent unless already applied exactly;
- keep control-root Git metadata informational.

Use `HEAD`/index/worktree Git-object comparisons inside the fresh isolated
staging clone, where that checkout is the actual commit/push authority.

<!-- FANTASY_GENERIC_FFPKG_DELIVERY_20260921:BEGIN -->
## Generic `.ffpkg` delivery infrastructure

Permanent project delivery tooling lives under `tools/delivery/`.

Build a deterministic text carrier:

```powershell
python .\tools\delivery\build_package.py <package-source-dir> <output.ffpkg>
```

Verify without executing:

```powershell
.\tools\delivery\run_package.cmd <output.ffpkg> --verify-only
```

Execute:

```powershell
.\tools\delivery\run_package.cmd <output.ffpkg>
```

The text carrier contains a Base64-encoded deterministic ZIP with exact byte-count
and SHA-256 metadata. The generic runner validates the carrier, archive, safe
paths, exact file inventory, and package manifest before isolated extraction and
entrypoint launch. It propagates the package exit code and removes the temporary
extraction tree.

The runner owns transport/execution mechanics only. Package entrypoints own
scope-specific predecessor checks, backup/rollback, idempotence, and validation.
Supported package types are `diagnostic`, `local_apply`, `runtime_sync`,
`release_install`, and `maintenance`.

Do not build phase-specific launch wrappers or manual Base64 chunk procedures
when this infrastructure is available.
<!-- FANTASY_GENERIC_FFPKG_DELIVERY_20260921:END -->

<!-- FANTASY_GENERIC_CHECKPOINT_STAGING_20260921:BEGIN -->
## Generic repository checkpoint staging

Permanent staging infrastructure:

```powershell
python .\tools\delivery\prepare_checkpoint_stage.py <checkpoint.stage.json>
```

A declarative staging spec supplies the remote predecessor, control/staging
roots, exact reviewed source scope, raw-byte identities, semantic markers,
manifest contract, and validation commands.

Representation is explicit:
- spec `exact_sha256` values describe raw control-root/worktree bytes;
- staged source identity is verified as Git clean-filtered blob identity;
- `docs/memory/manifest.json` continues to hash staged Git blob bytes.

The engine creates an isolated staging clone, regenerates the schema-2 manifest,
validates strict allowlists/residue/diffs/health, and always stops before commit
or push.
<!-- FANTASY_GENERIC_CHECKPOINT_STAGING_20260921:END -->
