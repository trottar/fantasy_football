# Current Project State

---
state_updated: 2026-10-28
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_signed_dst_frozen_trade_id_contract_repair
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver a commissioned Windows 10/11 portable, recurring GUI weekly decision workflow covering lineup, player, DST, kicker, IR, and trades, with uncertainty-aware response, preserved prospective capture, ESPN legality checks, and explicit human approval. Preserve unchanged v0.36 stochastic P/D/K kernels, `P ⊕ D ⊕ K`, the no-repeat native weekly MC boundary, and no automated ESPN transactions. Canonical acceptance: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Correct a confirmed signed-DST ESPN identifier schema defect in frozen structural trade diagnostics, source-only.** The published B2b6 checkpoint `809e6bda951ffa6ff4f82922d3db1d1fb891cf4e` (tree `6c38a6d3a3c231841b588cfca93b0be800e9bba9`) passed 1,083 staged tests and remote verification. Wednesday's frozen native nine-channel receipt still contains seven observed native trade candidates (six specialist-inclusive). The independent read-only preflight verified source/runtime identity, exact Wednesday snapshot/capture/receipt lineage and frozen certification but failed the B1 structural frontier on `NATIVE_OFFER_IDS_INVALID:receive_ids` before MC.

A subsequent no-write direct-schema probe reported six negative `receive_ids`, all six matching negative **DST** IDs on the partners' frozen rosters; there were 15 negative frozen roster IDs, all DST, and no non-integer trade IDs. Hence blanket `>= 0` checks in B1, B2b2, and B2b6 contradict the exact native ESPN roster representation. This candidate changes only structural identifier validation: signed nonzero integer IDs are permitted; a negative roster ID must be proven DST by frozen position; a negative prospective fill must match frozen DST market identity. Strings, floats, booleans, zero, duplicates, negative non-DST, missing ownership, league/roster infeasibility and unknown future acquisition remain fail-closed. Update B2b6 exact dependency pins to the patched source blobs and add cross-layer signed-DST synthetic tests. No scientific retuning, MC, runtime/GUI synchronization, or ESPN write is part of the repair.

## Verified State

- **Durable published baseline:** GitHub `main` verified `809e6bda951ffa6ff4f82922d3db1d1fb891cf4e`, parent `0992cc470615bd70eb1f8e0ef335431195f7aba3`, tree `6c38a6d3a3c231841b588cfca93b0be800e9bba9`, five exact changed paths; memory manifest schema 2, 224 unique entries. Published B2b6 source exists only in the control/checkout surface, not in the commissioned runnable model.
- **Native Tuesday:** protected frozen receipt SHA-256 `26fdac83015bca71cfdc341919e0d395645fb16193b9d05a79fecb129f25c285`; do not rerun/backfill. Wednesday GUI indicated saved timestamp `2026-10-28T19:20:05.393301+00:00` and seven native trade candidates; full native Wednesday receipt hash is not provided and must not be invented.
- **Read-only diagnostic evidence:** `week8_b2b6_wednesday_frozen_readonly_preflight_20261028_v2` passed provenance through certification, then explicitly blocked `NATIVE_OFFER_IDS_INVALID:receive_ids`. `week8_b2b6_wednesday_native_signed_ids_schema_probe_20261028_v1` reported 6/6 negative receive IDs paired with frozen DST roster identities, 15/15 negative frozen roster IDs DST, no malformed types, and zero writes/MC.
- **New signed-ID repair:** candidate only; local apply, full isolated staging QA, commit/push, strict memory postcheck and live structural preflight not yet performed. Synthetic tests and carrier checks are preparatory evidence only.
- **Original runtime and portable GUI:** v0.36-repack1 commissioned model unchanged. Corrected portable v2 GUI previously displayed seven trade candidates, seven structural pair conflicts, zero approval-ready actions. Native `ACTIONABLE_OFFER` never implies `RECOMMEND_FOR_APPROVAL`.

## Calendar / Evidence Gates

Thursday October 29 is the first Week 8 NFL game and Saturday October 31 is the protected follow-up. Capture gates outrank source development. Do not replay Wednesday native MC, silently backdate a missed capture, invent exact waiver/ESPN deadlines, or substitute old frozen states for current approval. Prospectively valid future lock, injury, transaction and live roster evidence requires a separate authorized check.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. Negative DST identifiers are **identity tokens**, not numeric performance or utility scores; preserve their sign and ownership. Do not treat two managers' MC scenario axes as common random numbers or sum standalone trade scores into joint utility. The B2b6 paired response remains opt-in, historical/conditional, uncalibrated for fill probabilities, and blocked on live ESPN transaction legality, injury, timing, and approval. `screen != authority`.

## Exact Next Action

**Apply and validate only this signed-DST schema repair under exact local source predecessor identities** via the deterministic text `.ffpkg` carrier. The installer must back up, roll back on error, run focused signed-DST regressions and strict memory health, and leave Git/runtime/ESPN/MC untouched. After user returns the local receipt, stage the exact source/test/memory allowlist via generic isolated staging with full repository pytest, compileall, index/manifest and whitespace QA. Only a separate guarded publication carrier may commit/push after assistant verification. Then retry the frozen Wednesday read-only structural preflight with its new exact source pins, classify **actual** drop-option/branch budget and future-fill limits, and only then consider a separately authorized bounded opt-in quantitative paired MC probe. Protect Saturday's prospective capture.

## Relevant References

- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `evidence/WEEK8_B2B6_MATCHED_FILL_ALTERNATE_DROP_2026-10-28.md`; `evidence/WEEK8_SIGNED_DST_FROZEN_TRADE_ID_CONTRACT_2026-10-28.md`
- `../../tools/operations/action_frontier.py`; `../../tools/operations/action_portfolio_b2b2.py`; `../../tools/operations/action_fill_predictive_b2b3.py`; `../../tools/operations/action_alt_drop_paired_b2b6.py`; `../../tests/test_frozen_signed_dst_trade_ids.py`
