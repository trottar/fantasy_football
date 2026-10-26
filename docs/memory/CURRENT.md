# Current Project State

---
state_updated: 2026-10-25
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_b2b4d_authenticated_transaction_source_shape_candidate
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

Deliver the source-bound weekly operator in `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`: protect prospective capture/deadlines, guarded nine-channel MC, live ESPN drift, full-roster legal transaction certification, and one approval-ready report. Preserve commissioned `v0.36-repack1`, stochastic `P ⊕ D ⊕ K` and manager-behavior separation. No automatic ESPN writes or 2026-result tuning of v0.X.

## Current Work Item

**Week 8 M1/M2 B2b4d source-only candidate:** `tools/operations/weekly_operator_transaction_source_b2b4d.py`, synthetic tests, and `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4D.md`. Source audit found commissioned v0.36's `fetch_private_league` already supports `mTransactions2`; its normalized transactions have reported `processDate`, but neither complete history nor actual effect-time/action-cutoff semantics are proved. B2b4d is a deliberately limited optional single-authenticated-GET **source coverage** probe: raw private data is not persisted or printed; a fresh exact-epoch view may contain transaction shapes, but no supplied event becomes authenticated B2b4c history and no cutoff or acquisition probability becomes certified. Installation is source-only: no GET, runtime modification, native MC or prospective capture. Initial v1 carrier rolled back on a legacy ESPN normalizer test import error in the synchronized control root; v2 scopes this one unrelated test to the full isolated Git checkout only if `src/data_sources/espn.py` is absent locally, with all diagnostic/action regressions still mandatory. This is not a full-QA pass.

## Verified State

- **Commissioned baseline:** `fantasy_season_v0_36_repack1` / `VERSION=0.36` remains unchanged. Source publication and diagnostic source do not commission the runtime or any operator.
- **B2b4c predecessor verified:** remote `e4cc77c9bed192c2642206ac4b4c849477decd24`, parent `792805a2d23ac9727b25ad9920f406bf2382189a`, exact tree `ed55ebd36cb0ceb580fcbf0169408a56476e472f`, 5 staged/committed paths, schema-2 manifest 213, full isolated pytest 1017 passed. B2b4c independently checks **caller-supplied post-freeze** event-order and release-state claims only; caller source labels/hashes are not ESPN authentication. No live event producer or transaction legality yet.
- **Week 7 protected evidence:** Saturday Oct 24 frozen six-provider snapshot SHA256 `f7ba8ac8ba8511a9f26dc8e579a36ecc3a227a6850be0df64aaeade62ec759e7`, capture SHA256 `a1ba36bd6b2008a2ea432c116aed1b8f56d0b356d381de8fde927ddafd41424a`, nine-channel native MC receipt SHA256 `5a2fe4a85a6db4cba0408d3e27c15082c260cea6621f319ae05af43dc02f5705`. Later owned/market/partner drift blocked action authority. Week 7 closed; no replay/backfill.
- **M1/M2 gaps:** transaction action-screen/cutoff and processing evidence, correlated manager/acquisition behavior, released-asset uptake/field response, injury downside, complete legal portfolios, M3 scheduler and end-to-end operator remain uncertified. Week 5 P/D/K closure incomplete; B2b multiweek absence horizon deferred without claim-local evidence. B2b4a/b/c remain uncommissioned diagnostic source.

## Calendar / Evidence Gates

Week 8 prospective captures and any first waiver/trade/player lock are irreversible and outrank B2b4d engineering. Sunday October 25 diagnostics do not retroactively freeze earlier information; later ESPN transaction data is **post-freeze observation**, never an earlier prediction. Before any football action obtain fresh causally prior evidence, full live state/cutoffs and independent legal action-screen verification. Evidence review does not authorize 2026-based v0.X calibration or ESPN writes.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. CRN within supported manager paired comparisons; no cross-manager fabricated joint draws. Manager behavior, intrinsic response, live observations and transaction execution are different sources of uncertainty. `screen != authority`; source `processDate` is NOT proof of actual effective timestamp; observed FREEAGENT is not future guaranteed fill. No B2b4d output authorizes actions, MC, refresh or capture.

## Exact Next Action

Guardedly **local apply only** B2b4d diagnostic source, 13 synthetic tests, architecture and coherent `CURRENT.md`. Require exact B2b4c + CURRENT predecessor Git blobs, new paths absent, runner package-ID/preflight checks, coherent rendered memory, BOM/CRLF-preserving backup/rollback and safe reruns. Run targeted B2b4d/B2b4c/B2b4b/B2b4a/B2b3/B2b2/B2b1/B2a/B1 regressions, compileall, strict memory health. If the synchronized root lacks the tracked legacy `src/data_sources/espn.py`, defer only `test_espn_league_v020.py` to full isolated Git staging, where it is mandatory; never claim this deferred test passed locally. Leave manifest, staging/commit/push, runtime, native MC, refresh/capture, authenticated/private ESPN GET and all ESPN writes untouched during local apply. Then isolated declarative stage/schema-2 manifest and full pytest; separate user-authorized publication and read-only remote verification. Following publication, separately run the **opt-in one-GET read-only shape probe** only under valid Week 8 calendar/evidence gates, inspect sanitized counts, and establish exact source semantics before any authenticated event/cutoff evidence producer, B2b4c event claim or action authority. No prospective backfill or 2026-outcome tuning.

## Relevant References

- `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4D.md`; `architecture/WEEKLY_ACTION_CERTIFICATION_SLICE_B2B4C.md`; `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `../../tools/operations/weekly_operator_transaction_source_b2b4d.py`; `../../tools/operations/action_joint_event_evidence_b2b4c.py`; `../../src/data_sources/espn_league.py`; `../../tests/test_weekly_operator_transaction_source_b2b4d.py`
