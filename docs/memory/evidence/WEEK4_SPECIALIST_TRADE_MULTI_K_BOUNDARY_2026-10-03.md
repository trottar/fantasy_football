# Week 4 Specialist Trade Multi-K Boundary - 2026-10-03

---
evidence_type: structural_diagnostic_and_source_validation
status: LOCAL_APPLIED_VALIDATED
football_model_tuning: false
reference_remote: 75e0806e50d4b7d4fbc873a870db3281c80b45ad
runtime_release: v0.36-repack1
internal_version: "0.36"
---

## Objective

Classify the surprising October 3 specialist-inclusive trade frontier and, if a
structural defect is proven, validate the narrowest correction without empirical
retuning.

## Frozen Decision-Time Evidence

Fresh Gate B5 cycle:

- snapshot UTC: `2026-10-03T07:07:57.420185+00:00`;
- prospective capture UTC: `2026-10-03T07:07:58.070713+00:00`;
- weekly state: `COMPLETE / ACTION_REQUIRED`;
- operational health: PASS;
- required channels: 9/9;
- sole action channel: `trade_specialist_inclusive`;
- frozen actionable offers: 6.

No source or runtime mutation occurred during capture or the subsequent audits.

## Frontier Reproduction and Decomposition

The non-mutating action-frontier audit reproduced all six stored offers exactly
and verified the decomposition identity for all six:

`total specialist-trade response = player-ownership response + specialist-ownership response`

Five of six offers were primarily driven by specialist response. This ruled out a
receipt-reproduction or Monte Carlo bookkeeping anomaly and narrowed the problem
to specialist ownership-state semantics.

## Policy-Boundary Audit

The second non-mutating audit directly confirmed:

- general K `CARRY2` remains disabled;
- four of six frozen offers ended with two owned K;
- three of six ended with multiple DST;
- all six ended with at least one multi-specialist channel;
- the fixed-ownership evaluator set K capacity to 2 for the four two-K states and
  valued the best owned kicker week by week.

Observed K specialist season-PPG contributions from the unsupported two-K state
were approximately:

- Offer 1: `+1.067397`;
- Offer 2: `+1.067397`;
- Offer 4: `+0.612094`;
- Offer 5: `+1.067397`.

DST multi-ownership was not invalidated by this evidence. The architecture treats
DST as a portfolio channel, while K is modeled as the current kicker and the
commissioned general two-kicker policy is disabled.

## Classification

`SPECIALIST_TRADE_MULTI_K_FIXED_OWNERSHIP_BOUNDARY_DEFECT`

The defect is structural, not empirical calibration. A league-legal transaction
may contain a K, but the specialist-trade authority may not assign future
multi-kicker portfolio option value when no commissioned K-channel policy supports
that state.

The October 3 six-offer frontier is preserved as immutable evidence but is **not
executable**.

## Authorized Correction

The user explicitly authorized the narrow structural correction.

Candidate behavior:

- finish existing legal mixed-package normalization first;
- reject user-side final states containing more than one K;
- reject partner-side final states containing more than one K;
- preserve multi-DST states;
- preserve the disabled general K `CARRY2` policy;
- preserve non-authoritative screening;
- preserve player-only trade authority and manager behavior separation;
- preserve Gate B5 IR behavior and B2b fail-closed state.

No new kicker strategy is introduced.

## Source Validation

Source preflight lineage:

- v1: failed non-mutating because Git CRLF warnings on stderr were merged into the
  changed-path stdout parser;
- v2: candidate compiled and 26 targeted tests passed; one new test failed only
  because its test implementation referenced `Path` without importing it;
- v3: PASS / NON-MUTATING.

v3 validated:

- exact changed paths: 2;
- `src/specialist_trade.py` candidate SHA-256:
  `2a7b34f1b8c82cafb194eb13a984d222c7f76aae6757aa095a37dd041e93a1ed`;
- candidate Git blob:
  `c2d420f08ed31debb95d5ac8478411479e67907c`;
- `tests/test_weekly_decision_gate_b_specialist_trade_composition.py` candidate
  SHA-256:
  `09f3c0a35f3f14680d77a2885a9bac40412cba974b7060f1674de52c2699013b`;
- candidate Git blob:
  `4d5d7e076057fdf574927f693cdc31ef17fdeaab`;
- user multi-K rejection: PASS;
- partner multi-K rejection: PASS;
- multi-DST preservation: PASS;
- targeted pytest: PASS;
- full pytest: PASS;
- compileall: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS.

## Local Apply State

The exact validated two-path source/test candidate and this durable-memory update
are **LOCAL-APPLIED / VALIDATED** in the control root.

Source publication, runtime commissioning, and a fresh post-correction decision
cycle remain pending.

`durable_memory_updated: true`
