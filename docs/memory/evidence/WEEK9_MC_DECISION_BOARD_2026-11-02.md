# Week 9 MC decision board — source checkpoint, 2026-11-02

`durable_memory_updated: true`

## Purpose

The existing October 27 portable v2 already renders a nine-channel saved native MC receipt and alternative rows, but its information is fragmented across panels and a Week 8 report can remain visible during Week 9. That is a practical decision-support defect. This checkpoint implements a first-panel prioritized MC opportunity board over **existing validated saved evidence**. It does not create a new model or certification layer.

## Exact scope

- `src/gui/weekly_mc_decision_board.py`: pure presentation of saved MC actions and alternatives. Safety-first groups (lineup, IR, player, D/ST, kicker, trades); only within-group native score ranking. Show retained numerical scores, paired conditional intervals, and behavior probabilities with explicit non-guarantee labels. Reject nonfinite data, ungrounded trade identities, duplicate offer rows, and unreadable labels. When saved and current Monday-based Eastern NFL weeks differ, every item is labeled `HISTORICAL_DO_NOT_ACT`.
- `src/gui/weekly_decision_view.py`: add first ranked MC board above the existing detailed panels, with current/saved week and explicit stale status. Keep all existing evidence/report controls, saved Native MC views, and read-only refresh behavior.
- `tests/test_week9_mc_decision_board.py`: deterministic source-free business checks and GUI source integration contract.
- `docs/memory/CURRENT.md` and handoff: active-state update, not a redundant history entry.

## Boundary

The new board **never** invokes ESPN, other providers, MC, capture, or scheduler; it does not mutate model, league state, or private evidence. It is a read-only report of saved candidate MC, not a source of new waiver or trade advice in the absence of a current Week 9 native receipt. P/D/K channel score magnitudes are **not** compared across groups; only within-channel scores can rank alternatives. A native ACTION remains a model opportunity, not a league-legal ESPN transaction. `ACTION_AUTHORITY=NONE` persists.

Current Week 9 model coverage/approval readiness is unknown until a prospective Week 9 snapshot/capture/native receipt exists, and previously saved Week 8 outputs cannot become current advice. Full waiver queue semantics, trade effective-date/risk certification and operational commissioning remain outstanding. Source publication and existing portable runtime synchronization are independent subsequent gates; the generic `.ffpkg` source apply will not modify either runtime.
