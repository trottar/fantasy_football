# Memory Update Checklist

<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V4:BEGIN -->
## Checklist

- Update the dated `memory/YYYY-MM-DD.md` log when chronology, a failure, or an
  operational transition matters.
- Rewrite `CURRENT.md` only when task/checkpoint/blocker/next action changes; keep
  exactly one authoritative next action and use publication-stable wording.
- Keep active status coherent across `CURRENT.md`, `roadmap/STATUS.md`,
  `roadmap/SEASON_2026.md`, and `docs/KNOWN_ISSUES.md`.
- Update `MEMORY.md` only for evidence-supported durable cross-session facts.
- Before restating a decision/gate/classification/deadline, open the canonical
  record that defines it.
- Keep `decisions/DECISION_LOG.md` complete for all canonical `D-NNN_*.md`
  records and update it when a decision is accepted, deferred, superseded,
  rejected, or reopened.
- Update the relevant investigation/evidence record with the actual question,
  evidence, classification, limitations, and successor action.
- Update runtime/evidence files only when validation status actually changes.
- For weekly football work, preserve prospective captures, write/link the weekly
  closure record, and write/link the current decision-completion / operational-
  health receipt. Missing captures or action coverage remain missing; never
  backfill or translate them to HOLD.
- Preserve `P ⊕ D ⊕ K` inside valuation and avoid wording that implies specialist
  assets are excluded from league-legal transactions.
- Update `docs/ROADMAP.md` only when accepted long-range phase intent or phase
  gates change.
- Update `roadmap/STATUS.md` when current roadmap position changes.
- Update `roadmap/SEASON_2026.md` when the active calendar/deadline plan changes;
  past weeks must not remain active/upcoming gates.
- Update `docs/KNOWN_ISSUES.md` when blocker/deferred/debt/reopen state changes;
  remove completed items from active issue state.
- Keep calendar gates distinct from evidence/calibration gates.
- Update `handoffs/CURRENT_HANDOFF.md` only for exceptional transfer state. At a
  normal stable checkpoint use the canonical no-exception state plus a pointer to
  `CURRENT.md`; do not mirror routine phase/status prose.
- Record material probe/tooling/package failures with exact modification state and
  promote reusable lessons.
- Use the deterministic text `.ffpkg` workflow for multi-step local delivery;
  do not reintroduce ZIP-era or manual Base64 transport instructions.
- Set `durable_memory_updated: true` in checkpoint/release records where
  applicable.
- Distinguish source inspection, source validation, package validation, runtime
  validation, operator confirmation, commissioning, local apply, staging,
  commit, push, and remote verification.
- Validate exact rendered Markdown, run strict memory health, and run the
  applicable diff/test/package gates before delivery/publication.
- Never claim a validation ran if it did not run.
- Never silently merge contradictory current states; record and supersede them
  explicitly.
<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V4:END -->
