# Collaboration Preferences

## Environment

- Windows 10
- Windows PowerShell 5.1
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
- Challenge assumptions and implementation choices when evidence warrants it;
  agreement is not validation.
- Do not claim source/test/runtime validation unless it actually occurred.
- Prefer incremental, evidence-led work over reconstruction from memory.
- After a tooling/package failure, resume from the last validated gate and prefer
  small, auditable continuation steps over another large all-in-one rerun. Do not
  rerun already-passed gates unless new evidence invalidates them.
- Do not ask for information already available from source, logs, durable
  memory, evidence, or project chat context.
- For longer work, provide concise progress updates when findings materially
  change direction.
- When sources conflict, use the newest validated state unless the user says
  otherwise.

## Required Startup / Handoff Behavior

For substantial work, actually read the complete bootstrap set defined in
`AGENTS.md`, including `MEMORY.md` and `handoffs/CURRENT_HANDOFF.md`. Do not
substitute remembered chat summaries for those files.

The user should not have to restate the repository handoff workflow in a new
chat.

## Windows Delivery Preference

For multi-step local procedures, prefer:
- one self-contained ZIP;
- one PowerShell 5.1-compatible `.ps1` launcher/entry point;
- one root-level execution block;
- safety checks, backup/rollback, validation, and progress output inside the
  package rather than reconstructed from multiple snippets.

Default checkpoint actor sequence:
1. assistant provides the update/package;
2. user runs the `.ps1` locally;
3. user returns the complete output;
4. assistant verifies the result;
5. assistant then provides separate commit/push commands;
6. user performs the push;
7. assistant may verify the remote read-only afterward.

Do not directly write to GitHub through a connector. Do not silently make a
delivered installer commit/push unless the user explicitly requests that behavior
for that specific checkpoint.

## Publication Boundary

The repository may remain public.

Keep secrets, authenticated raw data, private runtime material, and private
account identifiers local. Public Git may contain source, tests, architecture,
sanitized evidence, durable memory, and public-safe fixtures.

## Authorization Preference

Memory/diagnostic work follows the standing authorization in `AGENTS.md`.

Football/model/application/business-logic changes require explicit user
authorization.

Repository writes follow `patches/PATCH_PROTOCOL.md` and the human-in-the-loop
checkpoint sequence above.
