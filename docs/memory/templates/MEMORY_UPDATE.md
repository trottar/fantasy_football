# Memory Update Checklist

<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V2:BEGIN -->
## Checklist

- Update the dated `memory/YYYY-MM-DD.md` log with the actual question, probe/patch, measured result, and outcome.
- Update `CURRENT.md` if task/checkpoint/blocker/next action changed.
- Update `MEMORY.md` only for evidence-supported durable cross-session facts.
- Update `decisions/DECISION_LOG.md` when a decision is made, accepted, deferred, superseded, or reopened.
- Update the relevant investigation with question, decision boundary, fresh evidence, classification, limitations, and successor action.
- Update runtime/evidence files only when validation status actually changes.
- Update architecture/debt/roadmap when scope or stable boundaries change.
- Rewrite `handoffs/CURRENT_HANDOFF.md` so a new chat starts from the newest authoritative state.
- Record probe/tooling defects when they materially affect evidence interpretation or procedure.
- Include memory changes in the same ZIP as the work.
- Set `durable_memory_updated: true`.
- Distinguish source inspection, source validation, package validation, runtime validation, and commissioning.
- Never claim a validation ran if it did not run.
- Never silently merge contradictory current states; record and supersede explicitly.
<!-- FANTASY_MEMORY_UPDATE_CHECKLIST_V2:END -->
