# Week 8 v2 — Supervised Live Acceptance / Fresh M1a Receipt Bridge

**Classification:** structural commissioning circularity, source-only repair.
**Predecessor:** remote `b43b98596c5d5da24464e444fe24e0abb5a2dbdf` with tree
`00e4c43e212abbe0a358c2db3347450436714205`; 1053 isolated full QA tests.

## Direct source observation

The published `weekly_operator_v2.execute` checked
`weekly_operator_v2_commissioning.json` for `commissioned=true` before it could
perform the very first native end-to-end live acceptance run. Meanwhile M1a
`_identity_pair` required a less-than-two-hour validated v0.36 commissioning
identity and strict-memory receipt, neither created by the v2 coordinator.
A manual multi-step process would be required for every weekly MC, contrary to
the product contract.

## New narrow source behavior

- An explicitly invoked `--mode trial --ack-live-readonly` skips only the *v2*
  commissioning requirement. All existing runtime source, memory, clock,
  six-provider, immutable capture, MC launch budget, and M1a safety checks
  remain enforced. It does not schedule itself or create a v2 commissioning file.
- M1a's already-commissioned-v0.36 identity is freshly derived from exact
  installed source and independent strict memory validation. Verified hashes
  and timestamps are stored in private local receipts; no ESPN credentials,
  responses, or player IDs are exported. The receipt explicitly records that
  v2 itself is **not** commissioned.
- Trial and production have disjoint source-bound slot markers. One live trial
  cannot silently cause a second production sync/MC in the same slot. A
  successful scoped trial may report the full five phases through REVIEW,
  while the complete-roster outcome remains `INCOMPLETE_COVERAGE` pending the
  separate transaction-action certification contract. No auto-POST or v0.X
  empirical calibration occurs.

## Validation boundary

Local synthetic integration validates safe trial routing, memory failure,
source/dep binding, duplicate prevention, explicit acknowledgment, and
uncertified action state. It is not real Windows commissioning or an ESPN
availability/waiver cutoff certificate. The operator is not fully autonomous
until live trial, causal action certification, ranked reporting, and scheduler
activation have each passed separate receipt gates. Preserve Week 8 prospective
capture dates before any further optional source expansion.

`durable_memory_updated: true`
