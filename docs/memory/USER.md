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
