# Durable-memory manifest registry repair — 2026-09-17

<!-- FANTASY_MANIFEST_REGISTRY_REPAIR_RECORD:BEGIN -->
## Scope

Repair only the durable-memory manifest generator/registry checkpoint.

Pre-repair GitHub checkpoint:
`28485d27bd436f6f158da2a4d34671497238559a`.

The underlying procedure-memory content is preserved. Football/model/application
source is out of scope.

## Defect

`docs/memory/manifest.json` contained `y/...` paths and a self-entry for
`y/manifest.json`. This made the registry structurally invalid as an exact
inventory.

## Narrow hypothesis

The defect is caused by treating absolute paths as strings and computing relative
paths with `Substring($Root.Length)` across differing Windows path
representations.

## Repair decision boundary

The repair may checkpoint only if:
- provider-derived relative paths contain no erroneous prefix;
- `manifest.json` is absent from its own registry;
- actual non-manifest file set equals registry file set exactly;
- all registered byte counts and SHA-256 values match;
- `git diff --check` passes;
- all staged changes remain under `docs/memory/**`;
- remote `main` has not moved since staging began.

Otherwise the operation must fail without push.

## Validation state

The delivered package is statically validated and ZIP-integrity checked in the
assistant environment. Windows PowerShell 5.1 runtime validation occurs when the
installer runs locally. A remote checkpoint is accepted only after its own
runtime validations pass and post-push SHA verification succeeds.
<!-- FANTASY_MANIFEST_REGISTRY_REPAIR_RECORD:END -->
