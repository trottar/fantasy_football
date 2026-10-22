# Week 8 Action Certification — Slice B2b1, Two-Manager Conditional Native MC

**State:** read-only opt-in source diagnostic only; uncommissioned, not a recommendation or ESPN action authority. Predecessor: independently remote-verified B2a checkpoint `60ca28207f075ac412e32f59637a862220e57a7a` (tree `9c63998ab0afb618203613d9c2c4995b2b383fa8`).

## Narrow evidence question

B2a evaluates conditional user-side complete-roster utility for a bounded set of structurally different trade drop choices, but cannot establish a mutually acceptable trade. Does the same frozen transaction also improve or harm the partner's conditional complete-roster utility, including the no-future-free-agent-fill state? Can both sides be compared against HOLD under internally paired common random numbers, without interpreting the two independent managers' scenario arrays as a joint acceptance distribution?

## Scope and interpretation

`tools/operations/action_partner_b2b.py` imports B1 frozen offer/frontier and B2a source-bound guard/summary functions. The opt-in diagnostic evaluates both sides of each selected frozen trade under the existing `src.specialist_trade` v0.36 channel-composition helpers. The positive trade-review window is conservatively spliced to next week's ownership; zero or unsupported review timing blocks. The native code is verified against exact source blobs and unchanged commissioned `VERSION=0.36` before any MC.

The engine reconstructs two complete rosters from the frozen trade and explicitly **does not insert** native projected future `FREEAGENT` additions for either manager. If either resulting roster is not legal under the currently supplied, decision-time league rules, the option is blocked rather than given replacement points it cannot earn. Partner mandatory drops need explicit `droppable=True` and `lineup_locked=False` in the frozen snapshot to proceed; this evidence is *not* post-review legality. Player, defense and kicker internals remain distinct in valuation and only compose at complete-roster utility.

A single paired baseline MC is shared across selected alternatives *within each manager*; scenario arrays are paired against HOLD for their own roster state and against the native selected drop option for that same manager when available. Distinct managers' scenario arrays are not assumed to be correlated or interchangeable. Sample count is 16–512, option count at most three. Unevaluated structurally eligible alternatives are counted and remain unresolved. The absence of future fills is a conditional stress branch, not a claim about acquisition probabilities.

An injected kernel supports synthetic tests. Real native MC is never started during package installation and requires an explicit `--execute-native` CLI flag, valid frozen snapshot/capture/receipt, approved runtime source identities, and private local config/values paths. Default invocation is only frozen-input CHECK_ONLY. Optional report output is restricted to a new file beneath commissioned runtime `data/` and is never committed.

**All reports remain `BLOCKED_B2B1_CONDITIONAL_TWO_MANAGER_MC_ONLY / ESPN_ACTION_AUTHORITY=NONE`.** The existence of paired utility deltas cannot convert a native `ACTIONABLE_OFFER` into an executable trade or approval-ready recommendation. No ESPN GET/POST or football production code modifications occur.

## Acceptance and limitations

Synthetic regression covers conditional user+partner paired shapes, native versus alternative drop baselines, roster reconstruct/no-fill, reuse of manager baseline streams, unknown or locked partner drops, no-future-fill roster illegality, zero-review fail-closed, frozen input mutation, scenario/option budgets, and read-only/no-transaction boundary. The external isolated full-checkout test and subsequent human-authorized staged publication are separate gates; live native MC on private data has **not** been executed merely by packaging.

Still required before certification: both managers' complete legal drop/fill portfolios, alternative timing/processing scenarios, jointly uncertain waiver/free-agent acquisition, credible manager acceptance/counter behavior, coupled and mutually exclusive multi-trade/waiver strategies, complete injury/availability downside and future-week scenario propagation, live ESPN event-epoch reconciliation and exact app action-screen legality, explicit human approval. Unknown dimensions must remain blockers and never be replaced by static scoring or a guessed probability.

## Calendar / causal protection

Thursday October 22 and Saturday October 24 affected locks, and the Saturday Week 7 protected six-provider prospective capture and full nine-channel MC, outrank engineering work. A frozen Wednesday receipt that subsequently drifted cannot regain current trade authority merely because a new diagnostic evaluates its counterfactuals. Preserve original captures unmodified and do not retroactively call any later capture prospective.
