# Collaboration Preferences

## Environment

- Windows 10
- Windows PowerShell
- Local project root: `L:\Projects\fantasy_football\`
- GitHub: `trottar/fantasy_football`
- Free data sources only when equivalent information is reasonably available without paid APIs.

## Working style

- Be technical, rigorous, and explicit about provenance.
- Treat the physics analogy as a primary design criterion.
- Prefer auditable Monte Carlo/state-response machinery over generic fantasy heuristics.
- Preserve uncertainty and causal information boundaries.
- Do not claim a test/source validation happened unless it actually happened.
- Prefer incremental work over reconstruction from memory.
- For Windows-side multi-step operations, package scripts in a ZIP and provide a single PowerShell execution command when practical.
- Raw/private logs may be supplied ad hoc; durable conclusions should be promoted to repository memory.

## Publication boundary

The repository may remain public. Keep secrets and raw authenticated/private data local. Public Git may contain source, tests, architecture, sanitized evidence, durable memory, and non-sensitive fixtures.

<!-- FANTASY_PROCEDURAL_COLLABORATION:BEGIN -->
## Procedural collaboration preferences

- Prefer self-contained ZIP + Windows PowerShell 5.1-compatible `.ps1` + a short root-level run block.
- Put complexity, safety checks, backup/rollback, and validation logic inside the ZIP/script rather than in long interactive command sequences.
- Long-running scripts should print plentiful timestamped debug/progress messages.
- Log every meaningful update, patch, fix, diagnostic result, probe revision, validation/commissioning result, and roadmap/state change in durable project memory.
- Treat ChatGPT GitHub access as read-only unless the user explicitly authorizes a write action.
- Use GitHub for audit/reference; deliver project changes as local ZIP patches by default.
<!-- FANTASY_PROCEDURAL_COLLABORATION:END -->

<!-- FANTASY_PRIVYHUB_STYLE_AUTHORIZATION:BEGIN -->
## PrivyHub-style checkpoint authorization

This rule supersedes narrower earlier wording where it conflicts.

- Durable-memory updates under `docs/memory/**` are part of meaningful checkpoints and should be applied, validated, committed, and pushed by the delivered ZIP/PowerShell workflow without requiring a separate user authorization step for the memory push itself.
- Diagnostic/probe/audit/logging/observability/replay/failure-bundle tooling may be developed, revised, validated, checkpointed, and pushed with the same standing authorization as durable memory.
- Football/model/application/business-logic code remains gated: do not modify or push it unless the user explicitly authorizes that production-code step at the end of the relevant checkpoint.
- If a change mixes diagnostics with production behavior and cannot be cleanly separated, treat it as production code and wait for explicit authorization.
- Repository pushes should use the project ZIP/PowerShell checkpoint workflow, not direct GitHub connector writes.
- Checkpoints must use an exact staged allowlist, preserve failure lineage, validate generated memory/manifest output, and respect the public/private data boundary.
<!-- FANTASY_PRIVYHUB_STYLE_AUTHORIZATION:END -->
