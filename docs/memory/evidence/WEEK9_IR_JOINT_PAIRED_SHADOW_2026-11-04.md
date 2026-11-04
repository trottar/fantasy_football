# Week 9 Joint Two-Acquisition Paired MC Shadow — Candidate Evidence

Date: 2026-11-04
Checkpoint candidate: `week9_ir_joint_paired_two_acquisition_shadow_source_20261104_v2`
Authority state: **candidate only**, before local Windows application and full staged QA.

## Source and motivating frozen evidence

The published mixed-slot structural response at GitHub commit `36ea137388c8d6e505f805a1e73667dc80aebeaa` and portable runtime blob `a0c1dffcf13385a44d7dbf6e4eb763e1a089e34e` handles one direct vacant active slot and an alternative IR-move-created opening but cannot assign authoritative joint football/manager response. The immutable Wednesday Week 9 audit reported active 15/16, IR 0/1, one direct vacancy and three alternatives for one IR opening. Those observations motivate a **structural** experiment, not empirical 2026 tuning.

## Narrow new implementation

- New `src/ir_joint_response.py` exposes five required conditional strategy states: original no-action, move-only, move plus first only, move plus second only, and move plus both additions. One common `UtilityContext` supplies the paired MC scenario draws; conditional current-week head-to-head distributions are compared to the original no-action state. The move is excluded from current-week starter availability but no future IR capacity or return date is simulated.
- P, DST and K are evaluated within their separate existing kernels. At the complete-roster boundary one player roster and up to one acquired DST and one acquired K policy can be composed. Both-of-same-specialist-channel additions, specialist IR movers, absent total-roster position headroom, invalid identities and unsupported statuses are rejected; omitted states cannot be implied covered.
- A separate behavior diagnostic supplies only sharp bounds `max(0,p1+p2-1) <= P(both) <= min(p1,p2)` from individual acquisition marginals; it explicitly does not infer claim-queue dependence, independence, or certification. No expected joint utility is authorized from those bounds.
- The existing mixed branch in `src/ir_replacement.py` invokes the shadow only with explicit `model.ir_joint_response.shadow_enabled=true`, bounded to at most four sampled joint states and 64–512 scenarios. Default prospective behavior is unchanged. In every case `coverage_complete=false`, `recommended_action=None`, `joint_complete_roster_response_evaluated=false`, `action_authority=NONE` for the overall IR decision.

## First carrier failure and corrected successor

The v1 carrier returned prewrite and postwrite import/targeted pytest PASS (21 tests each) on the local Windows stage-backed tree. The strict memory health tool subsequently returned ATTENTION because the candidate current-state document used noncanonical headings and the handoff omitted required literal authority language. The package reported complete rollback, with runtime, ESPN, capture, MC, and Git unchanged. The v2 carrier restores exact checker-owned headings and handoff literals, and prechecks that structure before writing. Joint-response source, regression test, and source transform remain byte-identical to the v1 tested payloads. No v2 local application, staging, publication, portable synchronization, or commissioning is yet claimed.

## Validation boundary

The pre-delivery synthetic package QA must prove aligned scenario arrays, nonadditive complete-roster response, source hook disabled by default, checked partial branches, same-specialist rejection, joint headroom, finite probabilities, current IR move exclusion, identity and rollback guards. Full Windows stage-backed targeted tests, full pytest, compileall, Git staging and runtime commissioning are **not** claimed until returned receipts demonstrate them. No private ESPN IDs, names, authenticated payloads, or frozen runtime snapshots are included.

## Unresolved promotion blockers

This is shadow-only; no legal-action authority. Additional same-channel specialist portfolios, specialist IR move alternatives, all available structural combinations, joint acquisition/waiver timing and manager behavior, prospective operational cost, and full section-5A transaction certification remain unimplemented or uncommissioned. The Tuesday/Wednesday native MC receipts are immutable and must not be replayed to validate this new source.

`durable_memory_updated: true`
