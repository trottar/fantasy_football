# Week 8 frozen trade signed-DST asset-ID contract repair — 2026-10-28

`durable_memory_updated: true`

## Authority and observed failure

The native Wednesday frozen nine-channel receipt was prospectively captured before the October 29 Week 8 first kickoff. B2b6's exact source/runtime identity, Wednesday snapshot/capture/receipt chain, and frozen certification passed the no-write preflight v2, but the B1 structural frontier refused `NATIVE_OFFER_IDS_INVALID:receive_ids`. The direct no-write schema probe then counted seven native offers, six specialist-inclusive; six negative integer `receive_ids` and no malformed identifier types. All six negative receive IDs matched the partner's frozen **DST** roster position; all 15 negative frozen owned IDs were DST. Two earlier preflight attempts never wrote state or ran MC; v1 hid the reason class, v2 exposed the exact B1 guard. Do not treat v1's generic exception as an independent football regression.

## Narrow source diagnosis and correction

`action_frontier._ids_strict` assumes nonnegative ESPN trade identifiers, while native `specialist_trade.search_specialist_trades` retains ESPN's signed DST IDs. `action_portfolio_b2b2._owned` repeats the nonnegative-only assumption for frozen roster identities and `_future_fill_rows` repeats it for conditional acquisitions. `action_alt_drop_paired_b2b6._signature` rejects signed future-fill identities. These checks are inconsistent with observed native data and would create successive failures if corrected independently.

The source-only repair admits *signed nonzero Python `int`* asset IDs while preserving frozen position/ownership proof: any negative owned roster ID must be DST, and a negative future conditional fill must be a DST in the frozen market. Strict raw type checks reject booleans, floats, strings, null, zero and duplicate IDs. Trade matching, provenance, roster legality, static drop/lock proof, fill uncertainty, partner identity, user/partner MC axes, and ESPN action permission remain unchanged. B2b6's source-blob dependency pins are updated to the exact transformed B1 and B2b2 blobs. The original commissioned v0.36 and corrected portable GUI are not modified.

## Scope and remaining authority

Reviewed control-root paths: `tools/operations/action_frontier.py`, `tools/operations/action_portfolio_b2b2.py`, `tools/operations/action_alt_drop_paired_b2b6.py`, `tests/test_frozen_signed_dst_trade_ids.py`, `docs/memory/CURRENT.md`, and this evidence file. No repository `manifest.json` edit occurs until the separate isolated staging step. The new tests cover one synthetic signed-DST offer through B1, B2b2 and B2b6 with a mock quantitative kernel, negative non-DST rejection, valid signed FREEAGENT DST identities, and invalid types. No private identities or authenticated artifacts are included.

The source candidate is not an MC completion or trade certification. B2b6 action authority remains `NONE`, including if future structural preflight succeeds. Separate live preflight must prove budgets, action-time configurations and constraints before an opt-in quantitative run. Future fill acquisition/partner response correlation, injury contingency, effective processing time, third-party field response and exact ESPN legality remain unresolved. Saturday October 31's prospective capture outranks optional further development.
