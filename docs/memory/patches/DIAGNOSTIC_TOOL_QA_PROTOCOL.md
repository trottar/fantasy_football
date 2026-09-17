# Diagnostic Tool QA Protocol

<!-- FANTASY_DIAGNOSTIC_TOOL_QA_PROTOCOL_V1:BEGIN -->
## Purpose

Prevent diagnostic tooling from becoming the source of repeated investigation
failures.

## Required validation layers

### Static
- syntax/compile;
- undefined global names;
- parser-risk scans for PowerShell;
- explicit imports for runtime helpers;
- exact package allowlist.

### Executed unit/branch
- every runtime-critical helper called at least once;
- expected success path;
- expected nonzero/failure path without crashing the harness;
- classification boundary cases;
- redaction/privacy path where diagnostic output is persisted.

### Resource/lifecycle
- temporary extraction cleanup;
- staging clone cleanup on success and failure;
- no modification to authoritative source trees;
- no leftover diagnostic state that can alter later decisions.

### Git checkpoint
- runtime remote SHA captured;
- semantic predecessor verified;
- unique result marker / `ALREADY APPLIED` behavior;
- exact staging allowlist;
- `git diff --check`;
- schema-2 index manifest validation;
- committed `HEAD` manifest validation;
- remote-moved guard;
- post-push SHA verification.

### Exact delivery
- build ZIP;
- CRC/integrity test;
- extract the exact ZIP to a fresh directory;
- rerun all static and executed QA against the extracted package.

A tool is not `PACKAGE-VALIDATED` until all applicable layers pass.
<!-- FANTASY_DIAGNOSTIC_TOOL_QA_PROTOCOL_V1:END -->

<!-- FANTASY_DIAGNOSTIC_QA_RENDERED_OUTPUT_EXTENSION:BEGIN -->
## Rendered-output extension

The diagnostic QA protocol now explicitly includes generated durable output.

Required:
- render representative memory/evidence blocks during package QA;
- strip trailing spaces/tabs on generated Markdown;
- assert the rendered output is whitespace-clean;
- repeat the render/cleanliness test after extracting the exact delivery ZIP;
- where Git staging is part of the tool, `git diff --cached --check` remains the
  final authority before commit.

This requirement was added after the GUI-lineage v2 package failed on generated
evidence whitespace despite earlier synthetic QA passing.
<!-- FANTASY_DIAGNOSTIC_QA_RENDERED_OUTPUT_EXTENSION:END -->
