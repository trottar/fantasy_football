# Collaboration Preferences

## Environment

- Windows 10
- Windows PowerShell
- Local project root: `L:\Projects\fantasy_football\`
- GitHub: `trottar/fantasy_football`
- Prefer free data sources when equivalent information is reasonably available
  without paid APIs.

## Working Style

- Be technical, rigorous, and explicit about provenance.
- Treat the physics analogy as a primary design criterion.
- Prefer auditable Monte Carlo/state-response machinery over generic fantasy
  heuristics.
- Preserve uncertainty and causal information boundaries.
- Do not claim source/test/runtime validation unless it actually occurred.
- Prefer incremental, evidence-led work over reconstruction from memory.
- Do not ask for information already available from source, logs, durable
  memory, or evidence.
- For longer work, provide concise progress updates when findings materially
  change direction.

## Windows Delivery Preference

For multi-step local procedures, prefer:
- one self-contained ZIP;
- PowerShell 5.1-compatible scripts;
- one root-level execution block;
- safety checks, backup/rollback, validation, and progress output inside the
  package rather than reconstructed from multiple snippets.

## Publication Boundary

The repository may remain public.

Keep secrets, authenticated raw data, private runtime material, and private
account identifiers local. Public Git may contain source, tests, architecture,
sanitized evidence, durable memory, and public-safe fixtures.

## Authorization Preference

Repository writes follow the project checkpoint ZIP/PowerShell workflow.

Detailed standing authorization and production-code boundaries are canonical in
`AGENTS.md` and `decisions/DECISION_LOG.md`; do not duplicate or silently widen
them here.
