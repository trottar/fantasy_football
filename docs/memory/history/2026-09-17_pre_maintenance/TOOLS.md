# Tools and Proven Procedures

## Local root

`L:\Projects\fantasy_football\`

## GitHub

Repository: `trottar/fantasy_football`

Baseline commit:

`c85434a6be7852310c47fc8d1847c61a0a023209`

Baseline release:

`0.35-fixed1`

## Git safety boundary

Tracked/public:
- source
- tests
- non-secret config
- curated memory/evidence
- sanitized fixtures

Local-only:
- `config/secrets.json`
- `.env*`
- keys
- `data/raw/`
- `data/season_snapshots/`
- `data/season_predictions/`
- `data/season_decisions/`
- `data/season_closure/`
- generated reports/runtime state
- release ZIPs/source bundles unless deliberately published elsewhere

## Windows workflow

For multi-step local work, prefer a ZIP containing PowerShell 5.1-compatible `.ps1` scripts. Assume the ZIP is placed in `L:\Projects\fantasy_football\` and provide one root-level command that extracts and runs it.

## Release validation

When a full release is being built:
- full `pytest`
- `compileall`
- package integrity inspection
- extraction of exact delivered package
- full tests from extracted package where environment permits
- `compileall` from extracted package
- version/provenance agreement

Distinguish code validation from commissioning when local runtime data is required.

<!-- FANTASY_OBSERVABILITY_TOOLS_RULE:BEGIN -->
## Observability tooling rule

Prefer shared diagnostic contracts and reusable static/runtime audit tools over one-off debug scripts.

Initial v1.0A tooling includes a source-safe static diagnostic-surface audit that inventories existing logs, prints, exception handling, diagnostics modules, GUI modules, async/background-task/lifecycle surfaces, and likely integration boundaries without executing football/model code.

GUI diagnostics are part of the same toolchain and should retain correlation across UI action -> controller/service -> background task -> render/refresh.
<!-- FANTASY_OBSERVABILITY_TOOLS_RULE:END -->

<!-- FANTASY_PRIVYHUB_STYLE_TOOLING_RULE:BEGIN -->
## PrivyHub-style tooling workflow

Diagnostic tools are treated similarly to durable memory:
- they may be created and iterated proactively;
- they travel in self-contained ZIPs;
- they include provenance, failure history, and validation;
- they may be checkpointed/pushed without separate production-code authorization;
- they must remain observational/non-interfering.

Production football/model/application logic does not share this standing authorization.
<!-- FANTASY_PRIVYHUB_STYLE_TOOLING_RULE:END -->

<!-- FANTASY_MANIFEST_INDEX_TOOL_RULE:BEGIN -->
## Git-index manifest tooling

When validating durable-memory checkpoint bytes, use Git index/commit objects as
the authority:
- pre-commit: staged index bytes;
- post-commit: `HEAD` blob bytes;
- post-push: verified remote commit SHA.

Do not use Windows worktree byte hashes as a substitute for Git checkpoint blob
hashes when `core.autocrlf` or attributes may normalize line endings.
<!-- FANTASY_MANIFEST_INDEX_TOOL_RULE:END -->

<!-- FANTASY_DIAGNOSTIC_QA_TOOLING_RULE:BEGIN -->
## Diagnostic tooling QA rule

Diagnostic tools may advance continuously, but they must be treated as software
under test.

Do not release a probe merely because it compiles. Exercise runtime-critical
helpers and branch behavior before packaging, then repeat QA on the exact
delivered ZIP.

For lineage/GUI diagnostics specifically:
- launcher (`fantasy.py`) divergence is not automatically GUI-only;
- non-GUI `src/**`, config, or unrelated-test changes force a broader-divergence
  classification unless separately isolated;
- GUI lifecycle evidence should remain observational.
<!-- FANTASY_DIAGNOSTIC_QA_TOOLING_RULE:END -->
