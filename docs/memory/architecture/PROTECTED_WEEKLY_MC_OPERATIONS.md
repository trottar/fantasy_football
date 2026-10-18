# Protected Wednesday/Saturday Weekly MC Operations

## Purpose and status

This operating contract protects actionable fantasy decisions from competition with development and from long-running MC crossing an individual game lock. The default operating days are **Wednesday and Saturday**, not Sunday morning. The commissioned v0.36-repack1 system and nine-channel scientific decision gate remain unchanged. The standalone deadline-budget helper is an observational first slice; orchestration integration needs its own guarded source/runtime checkpoint.

## Weekly cadence

| Day | Protected operation | Completion target |
| --- | --- | --- |
| Monday | Immutable observed data/closure intake, review week boundaries | No unauthorized tuning of v0.X |
| Tuesday | Targeted diagnostics and validation of development candidates | Freeze unready changes rather than block Wednesday |
| Wednesday | First full six-provider refresh, immutable decision-time capture, healthy nine-channel paired MC, live legality and action review | Before any Thursday or earlier affected lock |
| Thursday | Apply prior legal/approved actions as appropriate; opportunistic status checks | No compulsory long MC |
| Friday | Finish development isolation; prepare Saturday run and verified fixture deadlines | Freeze unvalidated development for Saturday |
| Saturday | Second full six-provider refresh, immutable capture, healthy nine-channel MC, fresh ESPN slot/lock check, approval-ready actionable summary | In time to **execute** changes Saturday before affected kickoff |
| Sunday | Optional fast fresh ESPN injury/lineup/lock check; do not require an early wake-up or a 40-minute MC | Respect individual lock times; do not promote a cheap check into predictive authority |

Atypical Thursday, Friday, Saturday, Monday, international, and holiday games override the nominal cadence: calculate each affected player's earliest actionable lock from current evidence. If a Saturday MC cannot finish before a Saturday game, that action must have been decided at an earlier protected run. Transactions with effective-date/review delays have their own earlier deadlines.

## Hard control-plane rules

1. The known commissioned runtime remains the operating baseline. Unfinished model, IR, closure, feature, and observability work cannot preempt Wednesday/Saturday football operations. Development is held behind separate validation and release gates.
2. Before a full run, establish a **fresh, source-attributed next lock** for every action family under consideration; unknown locks block time-critical action assertions. No calendar assumptions or inferred single universal Sunday lock.
3. Budget run completion and implementation, not only snapshot-capture timing. For initial conservative planning use `MC=40 min`, `live validation=15 min`, `user approval/action=15 min`, `safety=10 min` (80-minute minimum lead). These are planning estimates, not empirically calibrated runtime guarantees; record actual runtimes to refine them without changing physics.
4. The preflight result `READY_TO_START_MC_NOT_ACTION_AUTHORITY` is only a latency-capacity check. No preflight, stale screen, or old receipt authorizes a roster transaction. If there is insufficient time, **do not initiate a full MC expecting a current-week action**; preserve the existing legal ESPN lineup, scope to unlocked alternatives with newly validated predictive authority if available, or classify the affected decision as deferred.
5. Immediately after each full MC, compare receipt identity to its frozen snapshot/capture and re-read live ESPN to verify individual locks, current roster/market, injuries, transaction history, and exact legal lineup-slot assignments. A material change means stale action authority. Even on unchanged state, require explicit user approval before ESPN writes.
6. A nine-channel overall `INCOMPLETE_COVERAGE` (including IR) stays incomplete. Scoped lineup or other channel findings may be discussed only with their own evidenced boundaries; no roster-wide COMPLETE/HOLD is inferred. `P ⊕ D ⊕ K`, utility composition, and manager behavior remain separate.
7. Keep both reference and consequential decision-time prospective captures immutable, exclude post-lock and unknown kickoffs from prospective closure, and avoid any backfill. Store secrets/raw authenticated data locally.

## First reusable preflight (not yet commissioned as an automatic gate)

`tools/operations/deadline_budget.py` is pure Python with no ESPN, network, MC, filesystem write, or Git operation. Example with an independently confirmed applicable individual lock:

```powershell
python .\tools\operations\deadline_budget.py --deadline-utc 2026-10-22T00:00:00Z --mc-minutes 40 --verification-minutes 15 --action-minutes 15 --safety-minutes 10
```

The example timestamp is **illustrative only, not a verified NFL kickoff**. `--deadline-utc` must be replaced by a freshly verified lock for the specific affected action set. Accept aware UTC/offset ISO 8601; reject naive or malformed inputs. The command is read-only. Use `--now-utc` only in tests/replay, never to backdate operational authority. A budget-pass is not permission to skip ESPN revalidation or to execute an ESPN action.

## Release / validation boundary

This first slice consists only of this canonical policy, sanitized evidence, coherent `CURRENT.md`, pure preflight helper, and deterministic tests. It does not edit v0.36 source, installed runtime, game schedule, ESPN, `.env`, MC scenarios, or transaction logic. Future integration must follow the full separate `local apply -> stage -> guarded publish -> runtime validation/commission` chain, with negative tests for near-lock and unknown-lock cases and a real read-only run receipt. A later control-plane implementation must guard before any costly MC starts; a CLI helper alone does **not** claim that protection is automated.
