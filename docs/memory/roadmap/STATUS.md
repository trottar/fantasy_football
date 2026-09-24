# Roadmap Status

## Current Frontier

- Authoritative runtime baseline: `v0.36-repack1` — **COMMISSIONED**
- Internal version: `0.36`
- Active engineering series: **v1.0A observability**
- Phase 1A data-source season-sync shadow: **COMPLETE / RUNTIME COMMISSIONED**
- Phase 1B closure shadow: **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1C P/D/K observability: **COMPLETE / SOURCE PUBLISHED / RUNTIME
  COMMISSIONED**
- Phase 1D market/manager-behavior observability:
  **COMPLETE / SOURCE PUBLISHED / RUNTIME COMMISSIONED**
- Phase 1E persistent evidence authorization: **NOT STARTED / SEPARATELY GATED**
- Persistent runtime sink: **DISABLED**
- Week 3 prospective evidence: **SECURED / CAUSALLY PROTECTED**
- Week 3 current P/D/K transaction posture: **HOLD / HOLD / HOLD**
- Week 3 planning FLEX: **MARK ANDREWS**
- Trade-search operational dependency: **READY**
- First prospective league-wide trade search:
  **COMPLETE / NO ACTION / FROZEN EVIDENCE PRESERVED**

## Phase 1C Commissioned State

DST boundary:
`src/specialist_policy_v032.py::evaluate_defense_channel`
at `subsystem.dst.channel`.

K boundary:
`src/specialist_policy_v032.py::evaluate_kicker_channel`
at `subsystem.k.channel`.

Player boundaries:

- CLI: `transaction_manager.evaluate_actions`
  at `subsystem.player.evaluate_actions`;
- GUI: `SeasonGuiService.evaluate_single_add_drop`
  at `subsystem.player.evaluate_single_add_drop`.

All accepted Phase 1C boundaries are source-published and runtime-commissioned
with bounded in-memory observation and persistent evidence disabled.

## Week 3 Operational Gate

The Sep 22 week-open reference remains immutable and the separate Sep 23
decision-time capture is frozen before outcomes.

Wednesday operational classification:

- player add/drop channel: HOLD;
- DST: HOLD Lions D/ST;
- K: HOLD Harrison Butker;
- expected-value FLEX: Mark Andrews;
- principal live status uncertainty: Puka Nacua.

The waiver/free-agent search is complete for the Wednesday state.

The first prospective league-wide one-for-one trade search is also complete from
a fresh Sep 24 decision-time state. Six predictive-MC candidates survived the
cheap screen, but none is actionable:

- Andrews -> Matthew Golden: small positive mean delta (`+0.104` PPG),
  `P(better)=51.5%`, partner loss `-0.490`, `P(accept)=8.0%`;
- Kittle -> Emeka Egbuka: small positive mean delta (`+0.196` PPG),
  `P(better)=52.1%`, partner loss `-1.387`, `P(accept)=1.3%`;
- the remaining four candidates are negative for our roster.

Operational classification: **HOLD / NO TRADE ACTION**.

A later Sep 24 fresh status/lineup gate then found no roster status/practice
change and no expected-lineup identity change. The lineup remained Mark Andrews
at FLEX with `123.30` nominal projected points and `118.02` availability-weighted
expected points.

The first gate classifier escalated only because bench RB Josh Jacobs was within
12 hours of kickoff. Jacobs was EXEMPT, hard-unavailable, and modeled at
`P(active)=0%`. A bounded replay/reclassification against the same frozen
snapshot/capture/audit proved this was a package-only relevance-classifier false
positive.

Recovered operational classification:

**HOLD / NO HEAVY CHANNEL RERUN**

A near lock is consequential only when it belongs to the captured planned lineup
or a captured contingency and the player is not already hard-unavailable.

The next football gate remains a fresh decision-time sync/capture when material
status/practice information changes or a consequential lineup/contingency lock
approaches.

Canonical evidence:

- `../evidence/WEEK3_DECISION_TIME_CHECKPOINT_2026-09-23.md`;
- `../evidence/WEEK3_PROSPECTIVE_TRADE_SEARCH_2026-09-24.md`;
- `../evidence/WEEK3_STATUS_LINEUP_GATE_2026-09-24.md`.

## Phase 1D Accepted Boundary

Read-only discovery classified the trade path into distinct layers.

**Football/roster response**

- `evaluate_roster_season_scenarios`;
- roster legality and post-trade automatic release/fill machinery;
- `_need_multiplier`;
- `_coarse_trade_score`;
- `screen_one_for_one_trades`.

**Manager perception / market feature**

- `_espn_market_ppg`;
- `perceived_market_value`.

**Manager behavior**

- `trade_response_probabilities`.

**Mixed complete trade response / orchestration**

- `evaluate_trade`;
- `search_trades`.

The former integration-plan proposal `subsystem.trade.search` at `search_trades`
is rejected as a behavior-only Phase 1D boundary.

The accepted first Phase 1D behavior boundary is:

`src/market_manager.py::trade_response_probabilities`
at `subsystem.behavior.trade_response_probabilities`.

Its model remains explicitly `UNCALIBRATED_TRADE_RESPONSE_V030`.

`perceived_market_value` remains a separate later market-perception candidate and
is not instrumented in the first behavior checkpoint.

Canonical discovery evidence:
`../evidence/PHASE1D_MARKET_MANAGER_BOUNDARY_DISCOVERY_2026-09-23.md`.

## Phase 1D Source Validation

The non-modifying commissioned-runtime paired probe passed across favorable,
neutral-boundary, adverse/complex, and controlled-error cases.

Validated properties:

- output and exception-type equivalence;
- Python and NumPy RNG non-interference;
- mutable-config non-interference;
- bounded behavior correlation/event structure;
- privacy markers absent;
- observer fail-open behavior;
- no persistent sink;
- runtime source unchanged.

The isolated source candidate then passed:

- 46 targeted tests;
- 517 full-suite tests;
- retained paired behavior probe;
- `compileall`;
- strict memory health;
- `git diff --check`;
- `git diff --cached --check`;
- exact six-path candidate allowlist;
- temporary-clone cleanup with no residue.

The first local-apply carrier (`..._v1`) failed before any write because the
partial control root does not contain `src/market_manager.py`. A read-only
inventory confirmed the split source/runtime layout and no unexpected (`OTHER`)
identity.

Corrected carrier `..._v2` then used the exact runtime predecessor read-only,
wrote and identity-checked all nine targets, but failed because it attempted to
run source-suite pytest from the intentionally partial control root. Independent
audit proved exact rollback and no residue.

Carrier `..._v3` preserved the isolated source-preflight authority and passed
post-write identity/semantic gates, but strict memory health rejected an
oversized `CURRENT.md` (`8465` bytes / `191` lines). The package therefore did
not reach an accepted local checkpoint.

Carrier `..._v4` kept `CURRENT.md` below both soft limits but contained an
invalid installer assertion requiring the carrier package ID inside
`CURRENT.md`. It failed after exact target identity validation and rolled back.

Final corrected carrier `..._v5` removes carrier-ID coupling from active memory,
accepts only the exact predecessor or exact v5 target, and self-tests the same
rendered-memory semantic predicates used after installation. The isolated
46-targeted/517-full-suite source-validation authority remains unchanged.

The source candidate changes observability only:

1. add `src/observability/behavior_shadow.py`;
2. decorate only `trade_response_probabilities`;
3. update the integration plan to the accepted behavior boundary;
4. add dedicated behavior-shadow tests;
5. update the existing integration-plan test;
6. add the retained behavior-shadow probe.

`search_trades`, `evaluate_trade`, and `perceived_market_value` remain
uninstrumented. No football, trade-value, acceptance-probability, recommendation,
or calibration formula changes.

Canonical validation evidence:
`../evidence/PHASE1D_BEHAVIOR_SHADOW_SOURCE_VALIDATION_2026-09-23.md`.

## Phase 1D Runtime Commissioning

Published source checkpoint:

`7a3bf1503b5d32be9846d9f7ad110fcff3cff179`

Runtime:

`L:\Projects\fantasy_football\fantasy_season_v0_36_repack1`

Commissioned boundary:

`src/market_manager.py::trade_response_probabilities`
at `subsystem.behavior.trade_response_probabilities`.

Attempt 1 (`phase1d_behavior_shadow_runtime_commission_20260923_v1`) applied
the exact three production targets, then pytest selected a user-profile root
and failed on inaccessible `C:\Users\papatrott\privateGPT`. The package
reported `ROLLBACK_PERFORMED=true` and restored the exact predecessor.

Corrected attempt 2
(`phase1d_behavior_shadow_runtime_commission_20260923_v2`) constrained temporary
validation files, pytest rootdir/confcutdir, and full-suite scope to the
commissioned runtime. Measured result:

- published source identities: `PASS (6/6)`;
- runtime production identities: `PASS (3/3)`;
- observability substrate identities: `PASS (7/7)`;
- dedicated behavior test: `8 passed in 8.55s`;
- targeted integration/market tests: `38 passed in 7.41s`;
- retained paired behavior probe: `PASS`;
- full runtime pytest: `353 passed in 45.35s`;
- `compileall src`: `PASS`;
- validation residue: `NONE`;
- rollback performed: `false`.

Paired incremental overhead medians were 82.0-82.95 us for success cases and
78.4 us for the controlled-error case; all absolute/relative gates passed.
Output, exception, Python/NumPy RNG, mutable config, privacy, and correlation
contracts passed.

No football/model/trade-response formula changed. `search_trades`,
`evaluate_trade`, and `perceived_market_value` remain uninstrumented. Persistent
sink remains disabled.

Canonical evidence:
`../evidence/PHASE1D_BEHAVIOR_SHADOW_RUNTIME_COMMISSIONING_2026-09-23.md`.

## Trade Search Before Week 4

The trade engine already exists and is covered by market-manager tests. The
automatic search:

1. screens league-wide one-for-one QB/RB/WR/TE offers;
2. runs predictive MC on the screened frontier;
3. keeps both managers' football deltas separate;
4. adds the uncalibrated manager-response layer;
5. ranks offers by expected offer value.

Dependency inventory on 2026-09-24 measured the exact automatic default as
`data/processed/player_values_2026.csv`. The commissioned repack target was
absent, while the control root, `v0.35-fixed1`, and `v0.36` each contained the
same 361778-byte, 939-row artifact with SHA-256
`4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d`.

That exact artifact has now been synchronized from the control root into the
commissioned `v0.36-repack1` runtime under hash and schema guards and loaded
through the runtime's own `transaction_manager` and `weekly_manager` value
loaders. This is an operational dependency repair only; no source/model formula
changed and no trade search was executed during synchronization.

Trade-search dependency readiness is **READY**.

The first prospective league-wide search was then run from a fresh authenticated
Sep 24 Week 3 snapshot and immutable v0.34 prospective capture. The cheap screen
produced candidates that predictive MC subsequently rejected or reduced to
near-noise, directly demonstrating `screen != authority`.

No one-for-one candidate justified action. No transaction was submitted. The
search state and corrected identity-recovery audit are preserved as prospective
evidence and must not be reused as a later decision-time state.

Canonical evidence:

- `../evidence/TRADE_SEARCH_PLAYER_VALUES_RUNTIME_SYNC_2026-09-24.md`;
- `../evidence/WEEK3_PROSPECTIVE_TRADE_SEARCH_2026-09-24.md`.

## Boundary Conditions

- Preserve `P ⊕ D ⊕ K`.
- Diagnostics remain observers, not decision/control logic.
- Football utility remains separate from manager behavior.
- Ownership, trend, and perception may affect behavior kernels but not intrinsic
  football value.
- `screen != authority`.
- Persistent evidence requires a separate authorization gate.
- No observed 2026 outcome may tune a v0.X model.
