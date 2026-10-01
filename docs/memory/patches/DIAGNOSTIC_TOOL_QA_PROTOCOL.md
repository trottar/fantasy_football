# Diagnostic Tool QA Protocol

<!-- FANTASY_DIAGNOSTIC_TOOL_QA_PROTOCOL_V2:BEGIN -->
## Purpose

Prevent diagnostic/tooling infrastructure from becoming the source of repeated
investigation or checkpoint failures.

## Required Validation Layers

### Static

- syntax/compile;
- undefined-global/symbol audit where applicable;
- parser-risk scans for rendered PowerShell;
- explicit imports for runtime helpers;
- exact affected/package allowlist.

### Executed Unit / Branch

- every runtime-critical helper called at least once;
- expected success path;
- expected nonzero/failure path without crashing the harness;
- classifier/semantic boundary cases;
- redaction/privacy path where diagnostic output is persisted;
- idempotence / already-applied behavior when applicable.

### Resource / Lifecycle

- temporary extraction cleanup;
- staging clone cleanup on success and failure;
- no modification to authoritative source trees during pre-delivery QA;
- no leftover diagnostic state capable of altering later decisions.

### Git Checkpoint

- exact predecessor/result authority represented at the correct layer;
- unique package/result identity;
- exact staging allowlist;
- `git diff --check`;
- schema-2 index manifest validation;
- committed `HEAD` manifest validation;
- remote-movement guard;
- post-push SHA verification.

### Validation Surface / Applicability

- select tests from the authority surface actually modified or commissioned;
- a synchronized control-root memory/tooling checkpoint must not require
  application/runtime imports that belong only to the commissioned release tree;
- run the complete applicable tooling tests for the changed tool, but record
  application/runtime pytest as not applicable when no application/runtime source
  is changed and the control root is not the runnable release;
- when application/runtime source is changed, execute its full regression gate in
  the validated complete staging/runtime import context rather than inferring
  coverage from control-root test-file presence;
- retained historical/release trees are separate validation artifacts unless an
  explicit procedure defines a combined environment.

### Exact Delivery

- build the deterministic text `.ffpkg` carrier with the generic delivery
  infrastructure;
- verify carrier format, archive byte count/SHA-256, safe member inventory,
  `package.json`, and every payload byte count/SHA-256;
- reconstruct/extract the **exact final carrier** into a fresh disposable
  directory;
- rerun all applicable static and executed QA against that extracted package;
- for mutation packages, execute the extracted package against an exact disposable
  predecessor and prove the intended success, controlled failure, rollback, and
  idempotence branches before operator delivery when the environment permits.

A tool is not `PACKAGE-VALIDATED` until all applicable layers have passed. If an
applicable layer cannot be run, report it explicitly rather than strengthening
the validation claim.
<!-- FANTASY_DIAGNOSTIC_TOOL_QA_PROTOCOL_V2:END -->

<!-- FANTASY_DIAGNOSTIC_QA_RENDERED_OUTPUT_EXTENSION:BEGIN -->
## Rendered-Output Extension

Diagnostic QA explicitly includes generated durable output.

Required:

- render representative memory/evidence blocks during package QA;
- strip trailing spaces/tabs on generated Markdown;
- assert rendered output is whitespace-clean;
- repeat render/cleanliness validation against the exact extracted `.ffpkg`
  payload;
- where Git staging is part of the tool, `git diff --cached --check` remains the
  final authority before commit.

This requirement was added after generated evidence passed synthetic QA but
failed checkpoint whitespace validation.
<!-- FANTASY_DIAGNOSTIC_QA_RENDERED_OUTPUT_EXTENSION:END -->
