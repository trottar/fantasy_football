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
