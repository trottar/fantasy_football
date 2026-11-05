# Week 9 IR Joint Shadow — Fail-Closed Direct-Entrypoint Provenance Guard

Date: 2026-11-04
Checkpoint candidate: `week9_ir_joint_shadow_entrypoint_provenance_guard_20261104_v2` (supersedes failed v1 local-apply attempt)
Classification: authorized narrow structural correction; **not** representative football MC commissioning

## Authorization and predecessor

- November 4 user authorization: proceed with the narrowly scoped source correction and synthetic regressions.
- Published remote predecessor: `afc82e98e5654adb4b1f1a5f398042a95ead00a7`; this is the predecessor, not the future commit of this candidate.
- Changed source: `src/ir_joint_response.py`, from exact published Git blob `15c681c99a307db1ea0b3dab5e590007fea26eb7`.
- Changed regression tests: `tests/test_week9_ir_joint_response_scoped.py`, from Git blob `ef9eb922d8c0095b83ded1d670866e5014d9c5d4`.
- Memory updates: `docs/memory/CURRENT.md` and `docs/memory/handoffs/CURRENT_HANDOFF.md`; this record is new. Schema-2 `docs/memory/manifest.json` is regenerated from the later isolated staged Git blobs, **not** the local-apply raw bytes.

## Exact scope and response

The source-bound November 4 gap audit found that a synthetically supplied invalid frontier could pass direct shadow evaluation even with `ir_state.status=BLOCKED`, no IR vacancy, and no mover membership. The normal `ir_replacement.py` adapter was not shown to generate such a frontier and is unchanged.

The corrected direct shadow API now checks:

1. IR-state PASS, no incumbent acquisition blockers, and consistent IR occupancy/vacancy.
2. Exactly the current supported direct-plus-IR two-opening capacity, without future capacity credit.
3. The mover's unique decision-time IR candidate-set identity, player-channel eligibility, injury status, and unlocked/non-IR lineup slot.
4. Current-context ownership exactly once, position/status agreement and lock/slot checks before predictive baseline MC.
5. Candidate-specific blocked reasons with stable original sampled order; all-invalid inputs avoid baseline MC and remain non-authoritative.

The supported valid player/specialist case still evaluates five branches using paired common draws. Same-channel DST/K pairs, unmodeled waiver dependence/ordering, exhaustive alternative movers, full roster effects and independent section-5A certification remain unresolved. `shadow_enabled` remains opt-in and false by default. No recommendation, ESPN write or complete IR decision is authorized.

## Verification boundaries

- Published predecessor source/test Git blob identities reconstructed exactly for offline construction.
- Candidate source and tests parsed successfully in the assistant's isolated construction environment.
- Synthetic suite using independent stubbed dependencies: **26 passed, 1 original production-adapter integration test deselected**. This is *not* a full project test or a portable/runtime acceptance.
- Initial `..._v1` local-apply attempt failed during targeted pytest import collection: `src.transaction_manager` could not import `src.season_utility` from the synchronized control root. The runner returned exit code 3 with `ROLLBACK_VALIDATION=PASS`, no Git or portable writes. Published GitHub tracks `src/season_utility.py`; the receipt does not prove the runtime source is defective.
- The `..._v2` successor changes **only the package validation environment** relative to the reviewed source/test payloads: before control-root writes, it locates a unique exact-blob installed portable source, copies only Python modules into an isolated temporary root, overlays the candidate guard/test artifacts, and runs all 27 synthetic regressions there. On missing/inconsistent installed source or test failure it stops before modification. After successful source apply it checks exact post images and strict memory health, rolling back on failure.
- This is isolated *source-copy* synthetic test coverage, not real-data MC, portable mutation, staged full-repository QA, or action certification. The user-returned receipt determines whether local application passed.
- Full project pytest, clean-filter/index manifest, isolated stage, commit, remote publication, portable sync and native MC commissioning remain separate uncompleted gates until their receipts exist.

**Calendar:** Week 9 November 3/4 prospective captures and native MC are immutable. Thursday November 5 and Saturday separate calendar gates outrank optional source checkpoint activity.

`durable_memory_updated: true`
