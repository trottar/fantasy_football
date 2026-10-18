# Week 6 Sunday MC Latency / Lock Incident — 2026-10-18

## Evidence and classification

Operator-provided exact generic runner receipts establish successful six-provider and capture integrity, followed by a completed nine-channel MC and a later material-drift/live-lineup failure. The Sunday operation was **not** an ESPN transaction failure and does **not** prove the MC math wrong. It was a workflow that allowed a long full MC to complete after an actionable individual lock, compounded by an avoidable Sunday-morning required run and a lack of exact executable slots in the native receipt.

- First Sunday kickoff: 2026-10-18 09:30 EDT (13:30 UTC). Earlier Saturday execution attempts were rejected by a hard-coded 06:00–09:30 Sunday-only gate; the user's Windows clock correctly showed Saturday. A required Sunday early run was unsuitable for the user's availability.
- Successful immutable Sunday snapshot: UTC `2026-10-18T13:14:28.631418+00:00`; file `data/season_snapshots/20261018T131404Z/snapshot.json`; six-provider health and capture binding PASS.
- Frozen capture SHA-256: `120761014402f7c145c5b80a4f78a71467cc30be024b7266b6ea39ba6ab35c1b`; record-level 190 PRE / 15 POST_LOCK / 33 UNKNOWN.
- Full native nine-channel receipt: `data/season_decisions/weekly_decision_receipt_20261018T135542Z.json`; SHA-256 `937501f0a6b28e5297aa693b98679fb10542f3766b0071c271d011e38d411984` (approx. 09:55 EDT, already post-kickoff). Health PASS, lineup ACTION proposed Meyers in / Andrews out, IR INCOMPLETE_COVERAGE, native overall INCOMPLETE_COVERAGE. No auto-transaction.
- Later live ESPN-only verification at UTC `2026-10-18T16:46:27.085465+00:00`: proposed saved lineup `BLOCKED:SAVED_SELECTED_PLAYER_NOW_LOCKED_ON_BENCH`; 2 ownership moves, 33 roster-state changes, 2 market-membership changes, 101 market-state changes, changed transaction history. Snapshot/receipt identities PASS, but `CURRENT_ACTION_AUTHORITY=NONE`; ESPN writes NONE. Never treat the frozen 114.8884 expected points as an executable lineup after the lock.

## Root cause

The package protected *time of capture* before first kickoff, **not** completion time plus verification plus user action, despite an approximately 40-minute paired MC. The weekly receipt omitted exact ESPN legal slot assignments; the later guard correctly refused an illegal bench-to-starter movement. Saturday had a prior recommendation and legal slots but live injury-status changes were material, so no retroactive Saturday authority can be claimed. The relevant failure is the schedule/procedural control plane, not the physics model or bad operator timing.

## Corrective contract / boundaries

Default full MC Wednesday and Saturday; no mandatory early Sunday MC or weekend wake-up. Preserve a complete current-week decision window for both run and implementation with player-specific locks. Reserve initial 40+15+15+10 minutes for MC, validation, action, and uncertainty; treat budget as a conservative configurable planning hypothesis, not MC uncertainty. If an existing legal lineup is unchanged, it may stay; no stale or cheap-screen result becomes execution authority. Isolate development from recurring operational runs. Preserve `P ⊕ D ⊕ K`, full nine-channel completion classifications, source/runtime commissioning, decision-time causality, and user's explicit ESPN approval.

## Checkpoint boundary

This evidence is public-safe and contains no ESPN raw records, account IDs, credentials, player IDs or secrets. It authorizes no ESPN change and no retrospective prediction. First deliver a pure deadline preflight, tests, operating contract, and memory update as a guarded local-apply checkpoint. **Actual Windows apply, staging, publication, remote verification, and integration into commissioned MC remain separate future states until evidenced.**
