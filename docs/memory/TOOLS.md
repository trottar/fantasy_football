# Tools and Proven Procedures

## Environment

- Local root: `L:\Projects\fantasy_football\`
- Primary shell: Windows PowerShell 5.1
- Repository: `trottar/fantasy_football`

Current release/project state belongs in `CURRENT.md`, not in this file.

## Generic Delivery Commands

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

Prepare an isolated declarative repository stage:

```powershell
python .\tools\delivery\prepare_checkpoint_stage.py <checkpoint.stage.json>
```

The runner owns transport/integrity/extraction/entrypoint execution. Package
entrypoints own target-specific predecessor checks, rollback, idempotence, and
domain validation. The staging engine owns isolated clone/staged representation
and schema-2 manifest preparation. Repository commit/push mechanics remain
canonical in `patches/PATCH_PROTOCOL.md`.

Do not recreate phase-specific launch wrappers, manual Base64 chunk workflows, or
binary-ZIP transport when the generic `.ffpkg` path is available.

## Control Root / Stage / Runtime Roles

- **control root local apply:** validate only package targets against the known
  predecessor/result contract; local Git metadata may lag synchronized files;
- **isolated staging clone:** remote predecessor, index, staged Git blobs, staged
  tree, manifest, commit/push preparation authority;
- **commissioned runtime:** synchronize separately only when an authorized
  checkpoint actually changes runtime/application files.

These are distinct state surfaces.

## Public / Private Boundary

Tracked/public may include source, tests, non-secret config, durable memory,
sanitized evidence, and public-safe fixtures.

Keep local:

- `config/secrets.json`;
- `.env*` and keys;
- ESPN cookies / SWID / `espn_s2`;
- raw authenticated API responses;
- private account identifiers;
- sensitive runtime snapshots;
- caches/temp files.

## Validation Tools

Use the applicable subset:

- targeted tests;
- full pytest;
- `compileall`;
- `git diff --check`;
- `git diff --cached --check`;
- strict memory health;
- exact changed/staged allowlist;
- deterministic `.ffpkg` carrier verification;
- exact extracted-carrier/package retest where applicable;
- staged Git-blob/manifest validation;
- runtime commissioning when local data/UI is required.

Never claim a validation not actually executed.

Keep these states distinct:

- package constructed;
- package validated;
- local apply passed;
- staged;
- committed;
- pushed;
- remote verified;
- runtime synchronized;
- commissioned.

## Git / Manifest Representation

`docs/memory/manifest.json` represents staged/committed Git blob bytes, not
Windows worktree bytes.

Authority:

- local apply: package predecessor/result contract;
- pre-commit publication: isolated staging index/staged tree;
- post-commit: commit/tree/`HEAD:<path>`;
- post-push: verified remote ref -> commit SHA.

The manifest excludes itself. Local apply does not finalize the manifest; the
later isolated staging step regenerates and validates it from staged Git blob
bytes.

Raw worktree SHA-256 and Git index blob identity are different representation
layers when clean filters such as CRLF-to-LF normalization apply.

## Windows PowerShell / Native Commands

PowerShell 5.1 may surface normal native stderr as `NativeCommandError` under
`$ErrorActionPreference = 'Stop'`.

Judge native success from `$LASTEXITCODE`; preserve/restore PowerShell error
preference around native calls.

Avoid unsafe `"$variable:"` interpolation; prefer `${variable}:` or `-f`.

Never use `Args` as a PowerShell function/script formal parameter name because
`$args` is automatic and names are case-insensitive. Prefer `GitArgs` or
`CommandArgs`.

Validate final rendered PowerShell rather than trusting only generator source.

## Diagnostic Tool QA

Diagnostic/observability tools are software under test. Apply the relevant gate
in `patches/DIAGNOSTIC_TOOL_QA_PROTOCOL.md` and `patches/PATCH_PROTOCOL.md`.

Where applicable, include exact `.ffpkg` carrier verification, controlled
success/failure branches, cleanup tests, rendered-memory cleanliness, and the
same import-root/runtime context as the application under test.

## Memory Health

Run:

```powershell
python .\tools\check_memory_health.py --root L:\Projects\fantasy_football
```

Use `--strict` at maintenance checkpoints. The tool is observational and never
rewrites repository files.

## Canonical Procedure Pointers

- repository checkpoint mechanics: `patches/PATCH_PROTOCOL.md`
- memory maintenance: `MAINTENANCE.md`
- communication lifecycle: `COMMUNICATION.md`
- reusable incident-derived rules: `LEARNINGS.md`
- generic delivery implementation: `../../tools/delivery/README.md`
