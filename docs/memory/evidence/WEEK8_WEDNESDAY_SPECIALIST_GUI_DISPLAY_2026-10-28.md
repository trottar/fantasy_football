# Week 8 Wednesday specialist trade identity display — 2026-10-28

**State:** source/portable local-apply candidate, not commissioned transaction authority. `durable_memory_updated: true`.

## Raw user-observed evidence

After the one-time October 28 Wednesday supervised native evaluation, the corrected portable GUI displayed native Week 8 `COMPLETE / ACTION_REQUIRED`, health PASS, one native actionable multi-player offer, six native actionable specialist-inclusive offers, and `TRADES: BLOCKED_UNCERTIFIED_END_TO_END_TRADE`. The six specialist offers displayed `Give assets -> Receive assets`, despite numerical native expected-offer values. Its retrospective Wednesday evaluated-alternatives section showed `Unavailable -> Unavailable`. The complete Wednesday native receipt SHA-256 is not known from the user-visible truncated hash; do not manufacture it.

The Wednesday acquisition frontier retained free-agent and waiver alternatives with native `NO_RESOLVED_EDGE`, including reported predictive futility stops at `SCREEN1`, distinct from the preselected asset count 80. The displayed waiver `expected_delta_utility` incorporates acquisition probability; the shown paired-resampled mean interval is conditional to acquisition and is not an interval around that acquisition-adjusted expectation. No football retuning follows from this presentational contrast.

## Exact source cause and bounded correction

`src/specialist_trade.py::screen_specialist_trade_packages` creates `give_names` and `receive_names` lists and `search_specialist_trades` carries them through the native action rows. `src/weekly_decision_alternatives.py::trade_alternatives` previously persisted only singular `give_name`/`receive_name`, producing absent names for specialist display evidence. `src/gui/weekly_decision_view.py::collect` also expected singular trade names for native actions. The frozen Wednesday native action rows still contain full asset names for actionable specialist offers; a deterministic read-only join of evidence against a **unique** native action on family, classification, exact expected offer value, accept probability and both manager PPG deltas can recover names for those rows. Ambiguous or missing joins yield `Trade assets not uniquely retained — do not act`. No ESPN, reclassification, fresh provider data, prospective capture or MC is used. Ordinary player-trade labels remain intact. The GUI additionally labels operator slot and report creation timestamp, and distinguishes conditional intervals from acquisition-adjusted expectations.

## Safety and validation boundaries

Synthetic tests cover precise names from saved native lists, unique matching, ambiguous refusal, missing-row refusal, numerical-drift refusal, untrusted name refusal, player-trade preservation, WED slot/report label and absence of action certification. This is a display-only repair. The existing native classifications, acceptance-behavior priors, startup scheduler state, and transactional authority remain unchanged. Local package pre-state must match exact source/portable bytes; back up and roll back on failure. Full source checkout QA, schema-2 manifest, staging, separate publication, GUI acceptance and transaction certification remain independent gates.
