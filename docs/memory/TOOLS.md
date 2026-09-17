# Tools and Proven Procedures

## Environment

- Local root: `L:\Projects\fantasy_football\`
- Primary shell: Windows PowerShell 5.1
- Repository: `trottar/fantasy_football`

Current release/project state belongs in `CURRENT.md`, not in this file.

## Repository Write Workflow

For multi-step memory/diagnostic work, use a self-contained ZIP plus a
PowerShell 5.1-compatible `.ps1` entry point.

Checkpoint flow:

`inspect -> ZIP -> local apply/validate -> exact allowlist -> commit -> remote-moved check -> push -> remote verification -> local synchronization`

Detailed patch mechanics:
`patches/PATCH_PROTOCOL.md`

Do not use direct GitHub-connector writes for project checkpoint pushes.

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
- exact staged allowlist;
- package CRC/integrity;
- exact delivered-ZIP extraction;
- exact-package retest;
- runtime commissioning where local data/UI is required.

Never claim a validation not actually executed.

## Git / Manifest Representation

`docs/memory/manifest.json` represents staged/committed Git blob bytes, not
Windows worktree bytes.

Authority:
- pre-commit: staged index bytes;
- post-commit: `HEAD:<path>` bytes;
- post-push: verified remote commit SHA.

The manifest excludes itself.

## Windows Native Commands

PowerShell 5.1 may surface normal native stderr as `NativeCommandError` under
`$ErrorActionPreference = 'Stop'`.

Judge native success from `$LASTEXITCODE`; preserve/restore PowerShell error
preference around native calls.

Avoid unsafe `"$variable:"` interpolation; prefer `${variable}:` or `-f`.

Reusable incident-derived rules live in `LEARNINGS.md`.

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
