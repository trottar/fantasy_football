# Week 9 Joint IR/Acquisition — Source-Bound Synthetic Gap Audit

Date: 2026-11-04
Record type: sanitized read-only Windows operator diagnostic receipt
Package: `week9_joint_ir_acquisition_gap_source_bound_synthetic_diagnostic_20261104_v1`

## Provenance and safety boundary

- Runner preflight PASS, archive bytes `6945`, SHA-256 `9fe82a2d4b87bb40f09c82c6b41708cb4d6f128bc8506d3a96f9642ba52f8927`, exit code `0`.
- `PUBLISHED_STAGE_COMMIT=PASS;TREE=PASS;FIVE_SOURCE_BLOBS=PASS` at published predecessor checkpoint `0c5ea579354047a0dfca8a207feeba6be95984c5`; portable source/guard and `VERSION=0.36` checks PASS.
- `SYNTHETIC_GAP_FIXTURE=PASS`; posttest portable source identities PASS; final `SOURCE_BOUND_SYNTHETIC_GAP_AUDIT_PASS`. `READ_ONLY=TRUE`, no network, ESPN, capture, native MC, Git, control-root writes or portable source writes; `ACTION_AUTHORITY=NONE`.
- This is synthetic diagnostics against published source in the installed portable, **not** real-data native MC commissioning or evidence that the normal adapter generated an illegal roster operation.

## Raw measurements and supported classification

| Probe | Returned raw evidence | Classification |
| --- | --- | --- |
| Screened frontier | Three IR move alternatives, four single-add candidates, `structural_pairs=18`, `sample_count=18`, `first_four_distinct_moves=1`, `default_shadow_limit=2`, `max_shadow_limit=4`, `all_legal_composites_certified=false` | Bounded, order-dependent sampled alternatives; not an exhaustive comparison |
| Supported paired state | `current_ir_move_excluded=true`, candidate `SCOPED_PAIRED_MC_EVALUATED_NOT_CERTIFIED`, `coverage_complete=false`, `action_authority=NONE` | Conditional response only, no action certificate |
| Same-channel DST pair | `BLOCKED_UNSUPPORTED_JOINT_STATE`; reason `TWO_SAME_SPECIALIST_CHANNEL_ACQUISITIONS_UNSUPPORTED` | Not valued or certified |
| Waiver dependence | Marginals `p_first=0.5`, `p_second=0.5`; `p_both_lower=0.0`, `p_both_upper=0.5`, `joint_behavior_exact=false` | Unknown joint claim dependence/order; no independence assumption |
| Position headroom | `BLOCKED_UNSUPPORTED_JOINT_STATE`; reason `JOINT_POSITION_HEADROOM_INSUFFICIENT` | Fail-closed in this synthetic case |
| Direct shadow entrypoint | `in_ir_move_candidate_set=false`, `ir_state_status=BLOCKED`, `open_ir_slots=0`, but `shadow_candidate_status=SCOPED_PAIRED_MC_EVALUATED_NOT_CERTIFIED`; `coverage_complete=false`, `action_authority=NONE` | **Input provenance/capacity validation defect in direct shadow API**; no production reachability claim |
| Certification | `joint_status=SCOPED_JOINT_SHADOW_ONLY`, `joint_authority=NONE`, `overall_coverage_complete=false` | No section-5A or ESPN authority |

## Source classification and next narrow hypothesis

`src/ir_replacement.py` normally constructs the structural frontier after checking IR state/move candidates. `src/ir_joint_response.py` checks direct mover ownership, injury status, and lineup lock but does not independently enforce `ir_state.status=PASS`, current open IR-slot capacity, or exact membership in the supplied `ir_move_candidates` list. The synthetic probe bypasses the adapter by providing an invalid frontier directly; no evidence here establishes that such a frontier is emitted through the regular adapter. The shadow is opt-in, disabled by default and non-authoritative.

**Narrow proposed structural correction, not yet authorized or applied:** make `evaluate_bounded_joint_shadow` reject blocked state, absent IR vacancy, or mover not in the supplied decision-time eligible set before expensive MC evaluation, then test valid and invalid direct inputs and preserve the same fail-closed output authority. Any football/application logic change needs explicit user authorization. This does not solve non-exhaustive frontier sampling, same-channel specialist response, joint waiver queue/claim behavior, full legality, future IR timing or section-5A certification.

Protect the frozen November 3/4 Week 9 supervised captures. Thursday November 5's prospective gate and Saturday's independent opportunity outrank any optional patch/commissioning activity. No retrospective prediction can be relabeled as prospective.

`durable_memory_updated: true`
