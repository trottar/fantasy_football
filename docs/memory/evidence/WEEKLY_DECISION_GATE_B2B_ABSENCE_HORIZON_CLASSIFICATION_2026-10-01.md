# Weekly Decision Gate B2b Absence-Horizon Classification — 2026-10-01

---
evidence_type: diagnostic_classification
status: FAIL_CLOSED_DEFERRED_CURRENT_EVIDENCE
production_source_change: false
runtime_change: false
football_model_tuning: false
remote_predecessor: a552cc4101285a824dd9fcfab8f0551c9fe3833f
---

## Objective

Determine whether current decision-time data supplies an explicit, semantically
usable multiweek absence/return horizon for IR replacement and future
roster-capacity valuation without inferring recovery timing from injury type,
start date, generic slot compatibility, or observed outcomes.

## Diagnostic Lineage

### Source/capture audit v1

Package:
`weekly_decision_gate_b2b_absence_horizon_source_capture_audit_v1_20261001`

Result: **FAILED BEFORE AUDIT EXECUTION**.

The diagnostic attempted to parse an indented class method with `ast.parse`
without dedenting `inspect.getsource()`, producing
`IndentationError: unexpected indent`. Control root, commissioned runtime source,
staging, commit, and push were untouched. This receipt is tooling-failure
lineage only and supplies no scientific evidence.

### Source/capture audit v2

Package:
`weekly_decision_gate_b2b_absence_horizon_source_capture_audit_v2_20261001`

Archive SHA-256:
`e38cc6a52f2d31a4976b49f406c521ce99b33aaf3628e643ab1f7a999a86b3e7`

Fresh temporary Week 4 sync covered ESPN, Sleeper, NFL official injury/transaction
sources, NFL team rosters, and nflverse rosters. Raw authenticated data was not
exported or persisted.

Findings:

- no explicit horizon field names in raw or normalized source surfaces;
- no explicit horizon field in prospective market, closure-player, or temporal
  player capture representations;
- ESPN private raw and NFL official raw text contained return-language hits;
- initial classification:
  `B2B_EXPLICIT_HORIZON_SIGNAL_PRESENT_CAPTURE_REPRESENTATION_GAP`.

That classification was intentionally provisional because free-text hits had not
yet been proven player-scoped, current, or semantically bound to a horizon.

### Text-hit provenance audit

Package:
`weekly_decision_gate_b2b_horizon_text_hit_provenance_audit_v1_20261001`

Archive SHA-256:
`71d29ad62494ab12cfe00f700eede06a3f67d475a85d416a0dc3615b9dfa4fee`

Fresh temporary Week 4 probe found five sanitized hit records:

- four player-scoped ESPN records;
- one unscoped NFL official record;
- ESPN paths were `seasonOutlook` and `outlooks.outlooksByWeek`;
- ESPN claims included quantified return language;
- no process-only overlap authorized;
- raw text and player identifiers were not exported.

Classification:
`B2B_QUANTIFIED_PLAYER_SCOPED_NARRATIVE_HORIZON_CANDIDATE_SEMANTIC_REVIEW_REQUIRED`.

`SEMANTIC_PATCH_AUTHORIZED=false`.

### ESPN semantic/freshness audit

Package:
`weekly_decision_gate_b2b_espn_horizon_semantic_freshness_audit_v1_20261001`

Archive SHA-256:
`1df1fee7e82d0ac18a3add71ebb51519e8cd106f1b4acbe1c8c8b07f88ca49fb`

Fresh temporary Week 4 probe found five ESPN claims:

- roster-scoped claims: 2;
- market-scoped claims: 3;
- strong guarded claims: 0;
- stale/missing-news claims: 1;
- weak-binding claims: 0.

Sanitized claim classes:

1. QUESTIONABLE market player, fresh <=24h, past Week 3 outlook, target Week 3.
2. ACTIVE roster player, fresh <=7d, past Week 2 outlook, target Week 2.
3. ACTIVE market player, >14d old, unquantified season outlook.
4. ACTIVE roster player, fresh <=72h, season outlook, quantified 10-game return
   duration mapped conservatively to Week 14.
5. ACTIVE market player, fresh <=7d, past Week 3 outlook, target Week 3.

No claim was attached to a player currently hard-unavailable. The quantified
weekly claims were past-week text. The fresh quantified season-outlook claim
belonged to an ACTIVE player.

Accepted classification:

`B2B_ESPN_NARRATIVE_HORIZON_FOUND_BUT_NOT_STRONG_ENOUGH_FAIL_CLOSED`

`SEMANTIC_PATCH_AUTHORIZED=false`

Raw narrative storage was not authorized.

## Scientific Interpretation

The current source set can contain useful narrative return language, so the prior
simpler statement "no horizon source exists" is no longer accurate.

However, **narrative availability is not horizon authority**. A future B2b parser
or representation patch requires, at minimum:

1. current hard-unavailable player state relevant to IR/replacement handling;
2. fresh decision-time evidence;
3. quantified future return/absence semantics;
4. unambiguous binding between the quantity and return horizon;
5. source-week/current-state consistency;
6. no reliance on process-only events such as "designated to return";
7. no use of observed outcomes to backfill prospective state.

The current Week 4 claims satisfy none of the complete guarded-authority cases.

## Classification / Decision

B2b current status:

**DEFERRED / FAIL-CLOSED UNTIL FRESH GUARDED HORIZON EVIDENCE**

No production parser, capture-schema change, future-capacity propagation, or
replacement-valuation patch is authorized from the current evidence.

B2b may be reopened by a later fresh decision-time capture if a claim satisfies
the guarded semantic contract above.

## Remaining Gate B Frontier

Current active gaps after this classification:

- automated multi-asset/unequal player trade search;
- specialist-inclusive trade composition preserving `P ⊕ D ⊕ K`.

Week 4 roster-wide completion remains `INCOMPLETE_COVERAGE`; do not infer HOLD
from the B2b fail-closed result.

`durable_memory_updated: true`
