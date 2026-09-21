# Memory Update Checklist

<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V3:BEGIN -->
## Checklist

- Update the dated `memory/YYYY-MM-DD.md` log with the actual question,
  probe/patch/planning change, measured result where applicable, and outcome.
- Update `CURRENT.md` only when task/checkpoint/blocker/next action changed.
- Keep exactly one authoritative next action in `CURRENT.md`.
- Update `MEMORY.md` only for evidence-supported durable cross-session facts.
- Before restating a decision/gate/classification/deadline, open the canonical
  record that defines it.
- Update `decisions/DECISION_LOG.md` when a decision is accepted, deferred,
  superseded, rejected, or reopened.
- Update the relevant investigation with question, decision boundary, fresh
  evidence, classification, limitations, and successor action.
- Update runtime/evidence files only when validation status actually changes.
- For weekly football work, write/link the canonical weekly closure record and
  preserve missing prospective captures as missing rather than backfilling.
- Update `docs/ROADMAP.md` only when accepted long-range phase intent or phase
  gates change.
- Update `roadmap/STATUS.md` when current roadmap position changes.
- Update `roadmap/SEASON_2026.md` when the active season calendar/deadline plan
  changes.
- Update `docs/KNOWN_ISSUES.md` when blocker/deferred/debt/reopen state changes.
- Keep calendar gates distinct from evidence/calibration gates.
- Rewrite `handoffs/CURRENT_HANDOFF.md` so a new chat starts from the newest
  authoritative state and can distinguish package/apply/commit/push state.
- Record probe/tooling defects when they materially affect evidence
  interpretation or procedure.
- Include memory changes in the same ZIP as the work.
- Set `durable_memory_updated: true` in release/checkpoint records where
  applicable.
- Distinguish source inspection, source validation, package validation, runtime
  validation, operator confirmation, commissioning, local apply, commit, push,
  and remote verification.
- Never claim a validation ran if it did not run.
- Never silently merge contradictory current states; record and supersede
  explicitly.
<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V3:END -->
