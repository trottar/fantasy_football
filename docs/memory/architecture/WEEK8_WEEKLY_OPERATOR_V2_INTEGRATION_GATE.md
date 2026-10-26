# Week 8 v2 — One-Entry-Point Weekly Procedure Integration

**Authority:** `WEEKLY_DECISION_OPERATOR_V2_SPEC.md` §§3-6 and `WEEKLY_DECISION_COMPLETION.md`.
**Checkpoint:** `week8_v2_integrated_operator_source_candidate_20261025_v1`.
**Status:** partial integrated source candidate, NOT installed as operational workflow, NOT commissioned or scheduled.

## Required product and explicit rejection of diagnostic drift

The product is a *self-running weekly procedure*, not a collection of ChatGPT-directed probes. One scheduled process discovers the configured fantasy/NFL week, protects actual action deadlines, obtains six-provider current state, freezes immutable prospective predictions, executes the commissioned nine-channel stochastic MC once per validated epoch, reconciles actual ESPN state, certifies complete legal roster/transaction consequences, and publishes one intelligible ranked decision/contingency report. Only approval/submission is manual. Missing evidence yields a precise blocker and recovery route; it never silently becomes HOLD.

## Source candidate and limitations

The first integration candidate adds `tools/operations/weekly_operator_v2.py` as one explicit entrypoint, using existing installed native `fantasy.py season-sync` and `closure-capture` APIs, M1a MC controller, and read-only reviewer rather than replacing football simulation. It derives NFL-week work scheduling from Monday reference (October 25 = Week 7; October 26 = Week 8), requires independent public schedule corroboration and 80-minute lead to the next future game, explicitly excluding already-elapsed games, validates six-provider snapshot identity, ties capture to the exact frozen timestamp, writes create-only local private launch/report receipts, redacts backend output, and does not call ESPN transaction writes. It cannot run unless a separate commissioning receipt binds its exact source SHA to v0.36. Running tests or installing source never creates that receipt.

This is **not yet a functioning autonomous weekly system**: the native phase-chain and commissioning evidence path require live runtime acceptance; controller may stop without recent identity/health receipts; restart needs phase-granular resume rather than only no-repeat guards; present positive trade/waiver candidates cannot be certified by existing scaffolding. Saturday captures only the *future game* subset after elapsed Thursday locks; elapsed outcomes never become prospective predictions. The preliminary report is *always* `INCOMPLETE_COVERAGE` or blocked on a completed route, never `COMPLETE_READY` or `RECOMMEND_FOR_APPROVAL`. No task scheduler is installed or enabled. These deficits must be resolved within the main v2 effort, not deferred indefinitely to unrelated research.

## Mandatory continuous build / commissioning gates

1. **Native execution:** prove one local command refreshes all six providers, creates an exact immutable Week 8 prospective capture before locks, preserves model/version and snapshot binding, and runs or reuses *one* 9-channel MC. Certify same-epoch phase reuse and restart after process kill. One bounded material-drift recovery epoch and exact dependency-based invalidation; a second drift blocks without runaway reruns.
2. **Complete action risk:** implement §5A full legal drops/fills, open slots, auto-normalization versus ESPN executable state, lineup/injury contingencies, traded partner state, uncertainty, trade review/effective date, and released-player league response. Pass the eight mandatory §5A fixtures including Lamar/Lamb/Ravens and future 49ers DST fill loss. Preserve separate P/D/K response and manager kernel; independent current app legality. No invented acquisition/cutoff probabilities.
3. **One decision report:** show full nine-channel coverage/health, every required waiver/FA/specialist/IR/trade family, complete legal roster after each proposed action, ranked mutually feasible strategy states, response distributions, confidence/uncertainty, verified deadline, and exact human action or blocker. Only fully certified choices may say `RECOMMEND_FOR_APPROVAL` and even then never auto-POST.
4. **Unattended scheduling:** install/update a protected Windows Task Scheduler task for Monday reference, Tuesday pre-waiver, Wednesday primary, Saturday secondary, and cheap state-driven checks. Derive real league waiver/claim cutoff from independent current evidence. Distinguish scheduler health and user-notification delivery; do not embed secrets in scheduled arguments/logs. Disabled until end-to-end live commissioning and the exact installation receipt.
5. **QA and commissioning:** synthetic and deterministic calendar/locks/no-backfill tests, crash/restart/duplicate suppression, transient provider failure/drift, private-output nonleakage, absence of ESPN POST, full `pytest`/compileall, exact package extraction, Git identities/schema-2 manifest, isolated staging, separate publication, exact local runtime sync, two safe real read-only runs with verified source/prospective state and report, scheduler dry-run plus activation/one-run receipt. Distinguish source publication, runtime sync, scheduler activation and football action authority.

## Week 8 calendar correction

Sunday October 25 belongs to Week **7**; Week **8** runs October 29–November 2. The 29-archive inventory on October 25 was a bounded observation before the Week 8 frozen-capture window and was not evidence of a missed Week 8 prediction. This correction does not invalidate the actual inventory values. Protect Week 8 captures starting Monday October 26 and the exact pre-waiver/first-game deadlines, not a fabricated Week 9 pivot.

`durable_memory_updated: true`

## Successor: source-bound phase receipts and restart gate (2026-10-25)

`week8_v2_phase_receipt_recovery_20261025_v1` addresses the original
single-launch-marker limitation without changing commissioned physics or live
permissions. The v2 entrypoint stores create-only `SYNC`, `CAPTURE`, and `MC`
phase intents and verified completions under the private runtime
`data/season_decisions` directory. Each intent binds the immutable launch
marker, exact operator source hash and immediate input dependencies. Saved sync
and capture identities must still match the actual immutable files, week,
source and launch and remain no more than two hours old. A started phase without
its completion has uncertain external effects; the controller must not rerun
sync or prospective capture. MC recovery remains delegated to M1a's
launch-before-execute/validated-native-receipt guard, not a new predictive
shortcut. Previously completed MC phases are never repeated merely to refresh
an ESPN review. Receipt corruption blocks the run.

Tests exercise a kill after completed capture (reuse without new refresh or
capture), kills during sync/capture (no duplicate side effect), source/dependency
identity drift, output-receipt tampering, insufficient freshness and a missing
native MC receipt. This is a **source-only** candidate, not a scheduler,
transaction certificate, permission escalation, validated live commissioning,
or complete v2 operator. Next acceptance gate is a real source-bound phase-chain
and bounded drift recovery, followed by all v2 §5A transaction/risk fixtures and
one coherent recommendation report before scheduler activation. A missed Week 8
prospective capture is never repaired by running this code after outcomes.

`durable_memory_updated: true`

## Successor: supervised v2 live acceptance and fresh M1a receipts (2026-10-25)

`week8_v2_supervised_trial_m1a_evidence_20261025_v1` removes the first-run
commissioning circularity without inventing a positive operational receipt.
The v2 `trial --ack-live-readonly` mode is an explicitly authorized one-slot
acceptance attempt, **not** the scheduled/commissioned `run` mode. Both routes
require published runtime source and strict-memory preflight. The trial can
run the protected existing six-provider native sync, exact-bound prospective
capture, M1a MC, and ESPN GET-only review; it reports `INCOMPLETE_COVERAGE`
until full action certification is provided. It never commissions v2,
installs a Windows task, calibrates v0.X, or submits ESPN transactions. A
trial slot is idempotent, source-bound and distinct from scheduled production;
production is barred in a slot already used by a trial.

Prior to MC, the coordinator re-attests the *already commissioned* v0.36
runtime through the existing exact-source `guarded_weekly_cycle.validate_root`,
hashes exact model/league/value dependencies, runs strict memory health
from actual source, and persists fresh, private, create-only M1a identity and
memory receipts. `commissioned=true` in the v0.36 identity attests the
pre-existing v0.36 runtime only; `operator_v2_commissioned=false` explicitly
prevents upgrading that fact into v2 commissioning. Failure to verify source,
health or dependencies blocks MC and cannot fabricate a successful receipt.

Synthetic integration tests cover uncommissioned trial eligibility, explicit
acknowledgment, end-to-end phase routing, duplicate-suppression across trial
and production, runtime dependency identity, strict-memory failure, privacy
and transaction-authority boundaries. They are **not** evidence that the real
2026 Week 8 six-provider capture/MC has already run. Live commissioning,
positive action certification and Task Scheduler activation require separate
real acceptance receipts.

`durable_memory_updated: true`

## Monday Week 8 live acceptance — native health checkpoint mismatch (2026-10-26)

Checkpoint `week8_v2_native_health_checkpoint_join_20261026_v2` is the source-only
correction; it does not rewrite any runtime evidence.

A user-run `trial --ack-live-readonly` completed CALENDAR/SYNC/CAPTURE and
left a verified immutable Week 8 snapshot and capture. Independent read-only
triage found one launch marker, one corresponding native decision receipt,
no v2 MC-done receipt, and a rejected native health/chronology check.
Native Gate A (`src/weekly_operational_health.py`) requires its `memory_health`
input's `source_checkpoint` to equal the commissioned runtime identity
`source_checkpoint`. The v2 `write_verified_mc_evidence` bridge omitted it.
Only add that source-owned checkpoint to **new** memory-health evidence. Do not
recreate or reclassify the Monday native receipt, silently reenter MC, or treat
subsystem existence as a certified transaction. Full root-cause classification
of all Monday operational blockers requires inspecting that native receipt's
individual health items; never infer that the single identified defect was the
only blocker. New Week 8 decision-time snapshots need independently confirmed
calendar/claim locks and native Gate A health acceptance before read-only review.

`durable_memory_updated: true`
