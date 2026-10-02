# Week 4 IR Move-Plus-Add Source Validation — 2026-10-02

---
evidence_type: production_source_validation
status: LOCAL_APPLIED_VALIDATED
football_model_tuning: false
production_authorization: granted
reference_remote: 1c61e1b3574f6797be518061c03a2b4e66d1c373
runtime_release: v0.36-repack1
internal_version: "0.36"
nfl_week: 4
---

## Objective

Validate and locally apply the redesigned Gate B2 current-week
`IR_MOVE_PLUS_ADD` source candidate without publishing or commissioning it.

## Validated Preflight

Package:
`weekly_decision_gate_b2_ir_move_plus_add_source_preflight_v4_20261002`.

Preflight state:
`SOURCE-PREFLIGHT / NON-MUTATING`.

Changed paths:
5 / exact.

Validation:

- path-keyed transform routing self-test: PASS;
- targeted pytest: PASS;
- full pytest: PASS;
- compileall: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS;
- control root: untouched during preflight;
- commissioned runtime: untouched;
- staging/commit/push: not performed.

## Production Design

The validated candidate:

- consumes only the proven single B2a IR-created open slot;
- fails closed on direct/multiple unsupported capacity states;
- uses the commissioned kickoff/snapshot-aware current-week lock boundary;
- preserves FREEAGENT versus WAIVER uncertainty;
- preserves `P ⊕ D ⊕ K` until the complete-roster response boundary;
- covers league-legal player/DST/K acquisition branches made relevant by the
  opened slot;
- introduces specialist mode `OPEN_SLOT_PLUS_ONE_CURRENT_ONLY` solely for the
  current decision week;
- leaves the general two-kicker `CARRY2` policy disabled;
- credits no future IR capacity while B2b remains deferred;
- leaves `transaction_manager.py` and `ir_roster_state.py` unchanged.

## Exact Candidate Identities

- `src/ir_replacement.py`
  - SHA-256: `0c38ca30ede9250a96203373287bb3498a57a9153d808149f7495b5341f0ed99`
  - Git blob: `6344a0b21d0a2397acb10d66d9e8e59932004f22`
- `src/specialist_policy_v032.py`
  - SHA-256: `6c0620575442b56740548c210cb4baaf4a9a574d3ff7411d41759cc30f34a2fd`
  - Git blob: `653c67a4fa87edb20da2dd752b2e8409510b30fa`
- `src/weekly_decision_cycle.py`
  - SHA-256: `bb553c0678b98f8cd166110c16d8aa7444a4773e412e9366ff7a83888d6de18e`
  - Git blob: `b4a9b702cc58067e7dff5d91eae11cd65c6aeb81`
- `tests/test_weekly_decision_gate_b2_ir_move_plus_add.py`
  - SHA-256: `5e7ad1ad81aee52f2585cf750252744e6f4897568e2fee78224f8681d264fa8e`
  - Git blob: `fffc28f0f02dab23ad940ed1e842c6518cc0c4da`
- `tests/test_weekly_decision_gate_b_multi_asset_player_trade_search.py`
  - SHA-256: `f87ba933643693ef7985697379f49ee63b7dfd9a34113ba0c4643f1727ed9e16`
  - Git blob: `fafa0637e4c009bb58beab1f5a281b14cbadc4d6`

## Boundary

This checkpoint is local source validation only.

Source publication:
**PENDING**.

Commissioned runtime:
**UNCHANGED**.

B2b:
**DEFERRED / FAIL-CLOSED / NO FUTURE CAPACITY CREDIT**.

The Week 4 weekly receipt matrix must not be rerun from this source candidate
until the exact source is published and separately runtime-commissioned.

`durable_memory_updated: true`
