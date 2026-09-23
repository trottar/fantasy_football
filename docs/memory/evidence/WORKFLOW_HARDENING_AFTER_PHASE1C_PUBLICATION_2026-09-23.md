# Workflow Hardening After Phase 1C Publication — 2026-09-23

## Classification

`WORKFLOW_HARDENING_AFTER_PHASE1C_PUBLICATION = MEMORY-ONLY / PROCESS EVIDENCE / NO FOOTBALL OR RUNTIME CHANGE`

## Remote-Verified Recovery Publication

The Phase 1C player recovery checkpoint was published and independently observed
on remote `main`:

- commit: `cb04abd9c574be735cd610748a998cff9c7138f2`;
- parent: `2b5515a3014925d737af51d03cfd934a3e72a939`;
- tree: `fd4339324c7530cea094820c4e0792611e0069ad`;
- staged source paths: 13;
- staged paths including manifest: 14;
- schema-2 manifest entries: 133.

The publication receipt reported exact raw control-root authorization,
clean-filter/index representation checks, strict memory health, both Git diff
checks, and zero unstaged/untracked residue. Publication did not modify the
control root or commissioned runtime.

## Deterministic-Artifact Failures

The continuation exposed repeated cases where assistant-side validation imposed
or assumed facts that were not derived from the exact representation:

- a memory-hardening package initially used stale predecessor identities for
  locally newer `CURRENT.md` and `CURRENT_HANDOFF.md`;
- a staging-spec audit incorrectly required `source_paths` list order to match
  prose order even though the canonical staging engine treats the paths as a
  unique allowlist and sorts the staged comparison;
- earlier M6 lineage had already shown the same class of defect through a guessed
  semantic marker and an unvalidated rendered EOF condition.

Classification:

`DERIVABLE_DETERMINISTIC_VALUES_MUST_NOT_BE_GUESSED`

## Publication-Interaction Failure

After the recovered isolated stage passed all gates, the assistant supplied a
large interactive PowerShell commit/push block. The user rejected that as a
direct violation of the project's packaged workflow preference.

The corrected transition used a deterministic publication `.ffpkg` that first
verified the exact identity of the proven local publisher, the owned stage, base
commit, staged tree, and path count, then invoked the proven publisher. The
publisher revalidated the manifest and remote-movement guards, committed,
pushed, and verified the exact remote SHA.

Classification:

`MULTI_STEP_PUBLICATION_MUST_USE_PACKAGE_PROVEN_PUBLISHER_BOUNDARY`

Running the separate publication carrier is the human authorization for
commit/push at the already-validated stage; local-update packages still stop
before staging/commit/push.

## Windows Owned-Stage Cleanup Failure

A rerun of generic staging correctly recognized the existing stage as owned by
the checkpoint sentinel but failed while deleting a Git object with `WinError 5`.

Targeted read-only evidence showed:

- exact checkpoint sentinel matched;
- `.git` existed;
- failing object was a normal Git object carrying the Windows read-only attribute;
- parent directories were writable;
- ACLs allowed modification;
- no `git.exe` process was active.

After clearing read-only attributes only inside that verified owned stage, the
same generic staging spec completed successfully.

Classification:

`GENERIC_STAGE_RECREATE_READONLY_DEFECT = TOOLING / DEFERRED`

The durable rule is to verify exact stage ownership before any permission repair.
A repository tooling fix should be a separate infrastructure checkpoint.

## Durable Rules Promoted

1. Derive inspectable deterministic literals, markers, hashes, identities, paths,
   and semantic constraints from exact source/package/result representations.
2. Validate final rendered/extracted artifacts before delivery.
3. Do not make the operator the first validator of deterministic generated
   content.
4. Keep local update, isolated staging, publication, runtime synchronization, and
   commissioning as distinct states.
5. Package multi-step publication around a generic/proven publisher rather than
   sending a long interactive PowerShell block.
6. Treat the Windows owned-stage read-only deletion issue as a separate tooling
   defect, not as football/source evidence.

## Scope

This hardening changes durable memory/procedure only. It does not change player
football/model/application source, the published player candidate, runtime files,
persistent evidence authorization, or frozen 2026 football state.

`durable_memory_updated: true`
