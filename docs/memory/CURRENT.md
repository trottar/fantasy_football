# Current Project State

---
state_updated: 2026-10-28
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_b2b5_frozen_trade_portfolio_safety_integration
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Deliver and commission a portable Windows 10/11 GUI-driven recurring fantasy decision workflow**, without relying on ChatGPT to choose football moves. Tuesday primary and Wednesday/Saturday/pre-lock follow-ups must produce one ranked uncertainty-aware lineup, player, DST, kicker, IR and trade report with independent ESPN legality and explicit human approval. Keep commissioned v0.36 physics, `P ⊕ D ⊕ K`, causal capture, no-repeat MC and no automatic ESPN transactions. Canonical gates: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Week 8 B2b5 frozen-trade risk integration, read-only and not action commissioned.** The user verified Wednesday's saved nine-channel native report with exactly seven individually `ACTIONABLE_OFFER` trade candidates (six specialist-inclusive and one multi-player) and native HOLD for player waiver, DST, K, and IR. Published source `6f7ee14a6689d9dbde622ee8a5f4bd0aa100e885` underlies the Wednesday portable runtime. A subsequent local uncommitted presentation hotfix displays specialist give/receive names and the frozen Wednesday report time correctly. Neither native offer status nor GUI display constitutes ESPN transaction authority. **This B2b5 candidate joins the existing published `tools/operations/action_certification.py` frozen provenance/roster-risk scaffold to the live GUI and assembles joint exposure conflicts without another MC run or modifying Wednesday evidence.** It maps all trade offers by exact native identities, shows modeled mandatory drops and remaining quarterbacks, flags trades that remove a frozen proposed starter, and flags incompatible direct asset overlaps. Every offer remains `BLOCKED` until all §5A quantitative joint/no-action/drop/fill/ESPN processing checks are commissioned. No manual ChatGPT football recommendations.

The frozen Wednesday receipt uses different numeric units for player waiver expected utility, conditional paired intervals, and trade expected offer value. Do not combine these scores across incomparable channels. A same-player or same-partner collision is structural risk evidence, not a joint football value or a calibrated correlated manager-response probability. The separate §5A eight-fixture acceptance gate remains open.

## Verified State

- **Remote source authority:** `6f7ee14a6689d9dbde622ee8a5f4bd0aa100e885` published/verified. Original commissioned `fantasy_season_v0_36_repack1` unchanged. The corrected portable tree at `L:\Projects\fantasy_football_portable_win10_11_20261027_v2\fantasy_football\fantasy_season_v0_36_repack1` is separate, with prior published evaluated-alternatives sync and the user's Wednesday GUI output.
- **Tuesday immutable source:** protected supervised six-provider sync, prospective capture and single MC receipt with SHA-256 `26fdac83015bca71cfdc341919e0d395645fb16193b9d05a79fecb129f25c285`. Do not rerun, backfill or rewrite it.
- **Wednesday live observation:** user-provided read-only panel shows native `COMPLETE / ACTION_REQUIRED`, 9 channels and alternatives, and unresolved `TRADES: BLOCKED_UNCERTIFIED_END_TO_END_TRADE`; exact full Wednesday receipt SHA and phase output have not been supplied and must not be invented. Native player acquisition HOLD is limited to its evaluated frontier. All actionable-looking trades remain native observations, not certified recommendations.
- **This checkpoint candidate:** bounded presentation-only specialist name recovery, conditional-interval labeling and slot/date visibility; source tests and durable memory belong in same checkpoint. After local apply, full isolated-staging pytest, compileall, schema-2 manifest and separate publication are required. No claim of full Windows 10/11 portability or recurring GUI commissioning.

## Calendar / Evidence Gates

The next Week 8 NFL kickoff is Thursday October 29; Saturday October 31 is the next protected follow-up. Preserve all prospectively valid Wednesday evidence; do not guess real league claim cutoffs, backfill completed games, rerun an uncertain MC, or treat a stale roster as action authority. Exact player locks, injury state and pending changes require live read-only reconciliation before user-facing transaction approval. Source development must not displace an irreversible prospective capture window.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. v0.X remains a-priori. The manager acceptance kernel cannot change intrinsic football utility; paired MC response and complete-roster state authorize football actions, while cheap screens only select frontiers. Missing exact assets, legality, review timing or contingency remain BLOCKED. Native `ACTIONABLE_OFFER` is not `RECOMMEND_FOR_APPROVAL`.

## Exact Next Action

**Validate the bounded B2b5 read-only source/portable GUI compositor under exact current hotfix/source/receipt identities, then complete isolated full-checkout staging and publication before calling it a durable source checkpoint.** Use the existing Slice-A frozen certification scaffold and trade evidence; reject mismatched snapshot/capture/receipt and stale proof. Do not rerun Wednesday MC, authorize ESPN writes, or claim unimplemented joint value. Next add legally and quantitatively supported §5A no-action/alternate-drop/fill/injury/effective-timing comparisons, followed by bounded live ESPN legality/cutoff certification and eventual single approval queue. Saturday's prospective capture gate outranks nonessential development.

## Relevant References

- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `evidence/WEEK8_EVALUATED_ALTERNATIVES_RETENTION_2026-10-28.md`; `evidence/WEEK8_WEDNESDAY_SPECIALIST_GUI_DISPLAY_2026-10-28.md`
- `../../src/gui/weekly_decision_view.py`; `../../src/weekly_trade_portfolio_gate.py`; `../../tools/operations/action_certification.py`; `../../tools/operations/action_frontier.py`; `../../tests/test_weekly_trade_portfolio_gate.py`
