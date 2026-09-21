# Generic package delivery infrastructure

This directory implements the reusable local package transport/execution boundary
for the fantasy-football project.

## Design

A `.ffpkg` file is UTF-8 JSON containing a Base64-encoded deterministic ZIP plus
its exact byte count and SHA-256. The ZIP contains `package.json` and a strictly
inventoried payload. The text carrier avoids relying on binary attachment
transport while preserving exact archive integrity.

The generic runner owns only transport and execution mechanics:

1. parse and validate the text carrier;
2. verify archive byte count and SHA-256;
3. reject unsafe ZIP paths/symlinks/duplicates;
4. validate `package.json` and the exact payload inventory;
5. verify every payload file byte count and SHA-256;
6. extract to an isolated temporary directory;
7. launch the declared entrypoint;
8. propagate the entrypoint exit code;
9. delete the temporary extraction tree.

Package-specific predecessor checks, backups, rollback, idempotence, validation,
and allowed project modifications remain inside the package entrypoint. The
runner does not stage, commit, push, or modify the commissioned runtime by
itself.

## Commands

Build:

```text
python tools/delivery/build_package.py <package-source-dir> <output.ffpkg>
```

Verify only:

```text
tools\delivery\run_package.cmd <output.ffpkg> --verify-only
```

Execute:

```text
tools\delivery\run_package.cmd <output.ffpkg>
```

`run_package.cmd` is intentionally tiny. It delegates package validation and
execution to `run_package.py`, reducing Windows PowerShell parsing/syntax surface.
The runner can still invoke a PowerShell 5.1 package entrypoint when a package
requires one.

## Manifest contract

Source package directories contain a `package.json` without a `files` field. The
builder owns the file inventory and injects exact byte counts and SHA-256 values.
The manifest requires:

- `schema_version = 1`;
- stable `package_id`;
- `package_type` in `diagnostic`, `local_apply`, `runtime_sync`, `release_install`, or `maintenance`;
- `entrypoint.type` in `python`, `powershell`, or `cmd`;
- safe repository-independent relative `entrypoint.path`.

The carrier/archive package ID must match the internal manifest package ID.

## Repository checkpoint staging

`prepare_checkpoint_stage.py` is the reusable staging/manifest boundary. It
consumes a declarative JSON staging spec and:

1. validates the reviewed control-root source scope;
2. rechecks the remote movement guard;
3. creates a fresh isolated staging clone;
4. copies and stages only the declared source paths;
5. regenerates the durable-memory schema-2 manifest from staged Git blob bytes;
6. validates exact staged allowlists, residue, diff cleanliness, and source
   representation before stopping prior to commit/push.

The staging spec distinguishes two representations deliberately:

- `exact_sha256` describes **raw control-root/worktree bytes**;
- staged identity is validated by applying the staging checkout's Git clean
  filters with `git hash-object --path ... --stdin` and comparing the resulting
  Git blob OID to the index blob OID.

Never compare a raw worktree SHA-256 directly with staged blob bytes. Text
normalization such as CRLF-to-LF is a legitimate Git representation transform,
not source drift.

Example:

```text
python tools/delivery/prepare_checkpoint_stage.py <checkpoint.stage.json>
```

The staging engine never commits or pushes.
