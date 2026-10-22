# Week 8 Weekly Operator — M1a Restart-Safe Phase Controller

**Boundary:** Source-only, noncommissioned control-root diagnostic. Published predecessor: permanent read-only triage commit `42470bf0bf0d060d3d842b52db8dac4cdfc144b5` (tree `50f7e5c244e3266dc3c5ceca061447d06c66fd79`). Native `v0.36-repack1` and P/D/K stochastic response are unchanged. The Week 7 Saturday protected six-provider capture and MC take priority. No ESPN transactions or autonomous refresh, capture or scheduling are implemented by this slice.

## Narrow implementation

`tools/operations/weekly_operator_controller.py` is the first **phase-state** entrypoint for the permanent operator. It reuses exact source-bound `weekly_operator_review.py` and `guarded_weekly_cycle.py`, rather than copying the football model or replacing the MC. Default `--mode review` discovers a unique latest immutable six-provider snapshot, bound prospective capture, and native receipt for that epoch. When a receipt exists, the published read-only reviewer repeats its current ESPN GETs and reports the same scoped decision queue. No expensive phase is repeated. `--mode status` is offline read-only phase inventory; it makes no ESPN GET.

The phase inventory also identifies: `NEW_SNAPSHOT_REQUIRED`, `CAPTURE_REQUIRED`, `MC_READY_TO_GUARD`, `MC_OUTCOME_UNCERTAIN` and `NATIVE_RECEIPT_READY`. The controller rejects ambiguous snapshots/captures/receipts, failed six-provider health, snapshot/capture mismatches, pre-data firewall violations, future-dated artifacts and incorrectly selected weeks. A stale unlaunched capture cannot be promoted to MC start authority. The raw existing native MC receipt must still pass strict provenance, complete nine-channel health, source/dependency identity and live review before any scope is presented; this layer cannot certify an ESPN action.

An explicit `--mode resume-mc` **only** attempts to complete an already-frozen, as-yet-unlaunched native MC. It requires the same recent verified identity and strict memory evidence demanded by `guarded_weekly_cycle.inspect`; rechecks its 80-minute protected window and immutable snapshot/capture hash; writes a private, exclusive `weekly_operator_m1a_mc_launch_<capture SHA>.json` marker before invoking the unmodified native launcher; and on successful MC runs the existing read-only ESPN reviewer. A matching old or new MC launch without a complete native receipt is `MC_OUTCOME_UNCERTAIN`, not a reason to rerun MC. A failed read-only review after completed MC preserves the native receipt for a later cheap retry. The launch marker is private local runtime evidence, not a public Git file. No `--execute` path can launch the six-provider sync, produce a new prospective capture or issue ESPN POSTs.

### Local commands (after a separately validated source-only checkpoint)

```powershell
cd L:\Projects\fantasy_football
python -B .\tools\operations\weekly_operator_controller.py --project-root . --mode status --week 8
python -B .\tools\operations\weekly_operator_controller.py --project-root . --mode review --week 8
```

The optional `--mode resume-mc` is **not a normal scheduled command**. It needs an already verified current capture and fresh commissioned identity/memory evidence; the default review command never launches MC. The deliberately scoped result can still be `CAPTURE_REQUIRED`, `BLOCKED`, or `SCOPED_REVIEW_REQUIRED`.

## Limitations / exact next slice

M1a is neither the complete M1 unified controller nor an automatic Week 8 run. In **M1b**, integrate the native six-provider refresh and immutable prospective capture with an early, independently sourced per-player deadline calendar, immutable phase receipts, and a fail-closed new-epoch policy. It must preserve successful phases after interruption, bound drift recovery to one epoch, and prioritize Saturday October 24 evidence collection. Do not backfill missed prospective observations. Subsequent M2/B2b3 phases handle ESPN slot-level legality and complete-roster trade certification. No new decision thresholds, manager probabilities or football production behavior are introduced here.

## Tests and publication gates

Deterministic synthetic tests cover each phase, no prior evidence, missing capture, restart reuse of completed MC, uncertain launch, old capture, exact frozen identities, week mismatch, duplicate artifacts, source health, absence of automatic execution, and no backdated authority. Exact extracted-package validation, local apply, full isolated staged QA, schema-2 Git manifest, separate guarded publication and remote verification remain separate gates. Synthetic tests cannot stand in for live private M1b commissioning.

`durable_memory_updated: true`
