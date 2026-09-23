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

For multi-step local procedures, prefer the permanent generic delivery path:
- one deterministic **text** `.ffpkg` carrier;
- the repository-owned `tools\delivery\run_package.cmd` entry point;
- package-specific behavior declared in `package.json` and implemented in the
  package entrypoint, not in a new phase-specific wrapper;
- safety checks, backup/rollback, idempotence, validation, and progress output
  inside the package/runner boundary rather than reconstructed from chat snippets.

Binary ZIP attachment transport has produced zero-byte files in practice, while
text transfer was verified independently. Do not fall back to manual Base64 chunk
assembly or long interactive PowerShell pastes when the generic `.ffpkg` path is
available. A bootstrap is appropriate only when the generic runner itself is
absent or must be repaired.

Default checkpoint actor sequence:
1. assistant provides the validated `.ffpkg` update;
2. user runs `tools\delivery\run_package.cmd <package.ffpkg>` locally;
3. user returns the concise success summary, or full failure output;
4. assistant verifies the result;
5. assistant provides the short declarative isolated-staging invocation/spec;
6. user runs staging and returns its concise success summary;
7. assistant verifies the exact staged tree/manifest;
8. assistant provides a separate deterministic publication `.ffpkg` that wraps
   the generic/proven publisher with exact stage/base/tree guards;
9. user runs that publication package;
10. assistant verifies the remote read-only afterward.

Do not directly write to GitHub through a connector. Do not make a local-apply
package commit/push. For an already validated isolated stage, running the
separate publication package is the user's explicit authorization for that
checkpoint's guarded commit/push.

Do not send long interactive PowerShell commit/push blocks when the same
multi-step operation can be expressed through the generic `.ffpkg`/publisher
workflow.

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

<!-- FANTASY_USER_OUTPUT_SUMMARY_PREFERENCE_20260921:BEGIN -->
## Local-Step Output Preference

For successful local PowerShell/checkpoint steps, ask for the concise final
summary block rather than the entire console transcript. Request the full log
only when a step fails, a summary omits evidence needed for classification, or a
specific diagnostic line must be inspected.
<!-- FANTASY_USER_OUTPUT_SUMMARY_PREFERENCE_20260921:END -->
