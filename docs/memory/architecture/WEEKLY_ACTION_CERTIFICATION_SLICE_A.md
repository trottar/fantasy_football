# Week 8 Procedure — Action-Certification Slice A

**State:** uncommissioned read-only certification scaffold; not the full weekly operator.

The frozen Week 7 Wednesday nine-channel MC yielded `COMPLETE / ACTION_REQUIRED`, but post-MC ESPN changes invalidated current action authority. The Lamar Jackson → CeeDee Lamb + Ravens D/ST modeled 1×2 trade contained an automatic Brissett release and questionable-only remaining QB. A native actionable label by itself was therefore insufficient for execution.

## Implemented scope

`tools/operations/action_certification.py` reads existing immutable snapshot, prospective capture and native receipt, verifies same snapshot/season/week provenance, checks the canonical snapshot/capture SHA-256 bindings, inventories each native actionable trade offer, exposes implied roster drops and quarterback consequences, notes known positive review timing, and **always** returns `BLOCKED_CERTIFICATION_NOT_COMMISSIONED / ESPN_ACTION_AUTHORITY=NONE`. It executes no MC, no ESPN GET/POST, no transaction, and does not change `v0.36` valuation. A local optional report remains private.

Missing or mismatched evidence fails closed. In particular, an automatic Brissett drop leaving one questionable QB yields explicit `POST_TRADE_QB_SINGLETON_CONTINGENCY_UNEVALUATED` and `POST_TRADE_QB_AVAILABILITY_UNCERTAINTY_NOT_PROPAGATED`. Assumed future FREEAGENT additions also get a blocker. The output is observability, **not** a revised trade recommendation. Roster-player comparisons remain inside P and DST/K comparisons inside D/K; full-roster action utility remains the later coupled boundary.

## Deferred prerequisites / promotion gate

Before any `RECOMMEND_FOR_APPROVAL` status: targeted paired MC for alternative legal drops, per-position injury/availability contingency and replacement opportunity; finite pending-waiver/future-free-agent uncertainty; mutually exclusive multi-action portfolio; exact trade/waiver/lineup timing and ESPN app legality; fresh live ESPN reconciliation; explicit transaction approval. The real one-command six-provider → prospective capture → nine-channel MC → bounded event recovery → certification/report controller is **not implemented** in this slice. The canonical `WEEKLY_DECISION_OPERATOR_V2_SPEC.md` is the implementation contract, not a commissioned system.

## Week 7 calendar guard

Protect Thursday 2026-10-22 and Saturday 2026-10-24 relevant individual kickoff and capture gates. The Week 7 frozen evidence stays immutable, and no engineering package may cause an ESPN transaction. Development is staged and published separately, then commissioned for a Week 8 read-only trial only after acceptance tests.
