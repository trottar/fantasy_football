# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only
exceptional cross-session transfer state and cannot override `CURRENT.md`.

## Transfer State

The 2026-09-23 chat ended because the assistant repeatedly misaligned with the
project's established repository/delivery workflow. The user explicitly requested
a memory-only checkpoint, remote push, and then a fresh-chat restart.

Do not continue from bespoke publication machinery generated in this chat.

Superseded / do not run:

- `phase1c_player_shadow_publish_v1_20260922.py`
- `generic_checkpoint_publication_infrastructure_v1_20260922.ffpkg`

Valid technical state to preserve:

- player candidate source validation remains valid;
- five player technical files remain unchanged;
- publication-state repair local apply passed;
- fresh isolated staging v2 passed;
- staged tree:
  `ff8aa263ac95075e096084399176053bb71d6fdb`;
- player source is not committed/pushed;
- runtime is unchanged / not commissioned.

The attempted generic publication-infrastructure package returned failure and has
no successful apply receipt. Its exact local modification state must be audited
in the fresh chat; do not assume either successful application or complete
absence without inspection.

The older tree
`4215991f4faa42b57bd2f88b78f8d59648398be6`
is superseded and must not be committed.

## Resume

Follow `../CURRENT.md`'s `Exact Next Action`. Start a new chat after this
memory-only checkpoint is remote verified, read the complete bootstrap set, and
inspect exact local state before any further publication or runtime work.
