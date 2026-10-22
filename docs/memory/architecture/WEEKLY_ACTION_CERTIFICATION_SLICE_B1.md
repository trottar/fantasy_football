# Week 8 Slice B1 — Frozen Structural Trade Frontier

**Status:** uncommissioned read-only deterministic frontier; not predictive MC, current ESPN legality or permission to recommend/submit a trade. Source predecessor: Slice A checkpoint `ba5458a31f57d9227b6d528b635e2a8ec5cb9f5b`.

## Narrow question

When the native v0.36 trade search chooses one roster normalization (e.g. Lamar Jackson for CeeDee Lamb + Ravens D/ST, automatically modeling Brissett as the dropped QB), which **distinct complete-roster perturbation inputs** remain to be assessed before claiming a certified trade? And which native offers share assets or a partner, requiring a mutually exclusive or jointly coupled strategy analysis?

## Implemented boundary

`tools/operations/action_frontier.py` consumes one immutable snapshot, prospective capture, and native nine-channel receipt. It invokes the already-published Slice A provenance/integrity checks, requires all three native trade-channel receipts, and refuses missing/duplicate player identities or mismatched partner ownership at the frozen state. It does **not** fetch fresh ESPN data, rerun MC or change model/manager behavior.

For each native offer the frontier:

1. Binds `give_ids`, `receive_ids`, native forced drop/fill identities, partner and channel to exact frozen records; rejects missing evidence instead of guessing.
2. Computes the **count** of required user drops or fills from the exact frozen roster size; compares this structural count with native chosen normalization and flags disagreement.
3. Enumerates up to 64 alternative user-drop sets with explicitly `droppable=True` and `lineup_locked=False` in the frozen state. It **also includes** the native chosen drop even when this frozen eligibility evidence is absent or false, marking the unresolved legality instead of excluding it. Truncation is explicit. User and partner future `FREEAGENT` assumptions remain blocked and do not silently populate the static roster.
4. Emits full post-option player IDs and separate P-position, D and K counts, QB names and unresolved QB injury statuses as **candidate MC inputs**, not a fantasy ranking. The Lamar regression includes native `drop Brissett -> only questionable Baker`, versus other conditional drop options with different QB coverage.
5. Emits stable offer identities and a graph of offers sharing given/received assets or a partner, distinguishing direct asset conflict from mere partner coupling. It does not naively sum standalone trade gains or assert that two proposals can coexist.

Every candidate remains `BLOCKED_PENDING_PREDICTIVE_CERTIFICATION`; the entire report remains `BLOCKED_FROZEN_STRUCTURAL_FRONTIER_ONLY / ESPN_ACTION_AUTHORITY=NONE`. A static drop frontier is not an ESPN-proven legal set, especially across a positive trade-review period. Native trade search results are screens for this next valuation problem, not decision authority.

## Next acceptance gate (B2)

Implement **source-bound** paired native complete-roster MC over legally feasible normalized alternatives and no-future-fill contingencies using common random numbers; propagate player participation/injury, matchup, DST/K, effective trade week, opponent and manager-state coupling. Compare the jointly feasible portfolio against HOLD / waiver / other trades, then add finite event-epoch reconciliation and verified ESPN action-screen legality. Do not promote this B1 diagnostic to `RECOMMEND_FOR_APPROVAL` before those boundaries are independently validated and commissioned. If the native evaluator cannot accept an explicit normalized roster, change only the narrowly required application interface with dedicated user authorization, not the commissioned v0.36 physics or output calibration.

## Protected calendar / publication

Week 7 Thursday October 22 and Saturday October 24 capture/lock gates outrank B2. B1 uses guarded local text `.ffpkg` apply, strict targeted tests, independent full isolated-checkout suite, manifest/stage and separate commit/push package. Commissioned `fantasy_season_v0_36_repack1` remains unchanged.
