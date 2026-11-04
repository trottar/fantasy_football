# Week 9 — mixed direct slot plus eligible IR move, scoped structural continuation

`durable_memory_updated: true`

## Frozen evidence and source boundary

The November 4, 2026 supervised Week 9 native MC completed with a valid SYNC/CAPTURE/MC phase chain. Independent read-only audit of its immutable receipt and source-bound B2a IR state established: active roster capacity 16, occupancy 15, direct open capacity 1; IR capacity 1, occupancy 0; three ESPN-status-qualified unlocked move alternatives (two OUT, one INJURY_RESERVE); one move-created potential opening; arithmetic total 2; position maximum headroom for QB/RB/WR/TE/DST/K; all reported raw invariants PASS. The published predecessor `src/ir_replacement.py` Git blob `75c9f575ce1943b012c64d47a8d34ba6a62b53fd` returns `MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED` before calling either current-week single-add evaluator.

The three move candidates are choices for ONE IR slot, not three IR capacities. The two openings are distinct current roster transitions: one already vacant active slot, one conditional on moving an eligible owned player to IR. Wednesday's frozen receipt is immutable evidence, not new source-version predictive authorization.

## Narrow source candidate

Permit recognition only of the **exact 1 direct + 1 IR-created** two-opening state with validated distinct current eligible unlocked IR-move alternatives. Preserve single-opening behavior and fail-closed handling for unknown/multiple direct openings, more than two total openings, invalid/ambiguous moves, incomplete position headroom, and unmodeled future injury/return horizon.

In the mixed state, evaluate the already-legal direct-add P/D/K **single-perturbation** MC as scoped evidence, and enumerate bounded legal *structural* two-add/one-move alternatives with total-roster position maxima, unique adds, and mutually exclusive IR move choices. Enumeration is a screen; it does not establish that two acquisitions jointly succeed or that two separately valued marginal gains add linearly. It does not call a joint predictive MC or joint behavior kernel.

Therefore preserve `coverage_complete=False`, `recommended_action=None`, `joint_complete_roster_response_evaluated=False`, `joint_predictive_mc=NOT_EVALUATED`, `joint_acquisition_behavior=NOT_EVALUATED` and the existing `INCOMPLETE_COVERAGE` weekly gate. No ESPN action certificate. This is a bounded structural continuation, **not yet the full two-opening coupled response**. Its remaining required component is a paired P/D/K joint scenario engine with acquisition contingencies and validated native receipt interpretation.

## Evidence/validation status

The proposed package is source-only and must establish actual local prewrite/postwrite tests, strict memory health and exact applied identities before any stage/publication. It does not edit the installed portable v2, frozen native MC receipts, snapshots/captures, ESPN, Git index, or commits. Full suite, schema-2 staging, guarded push, portable sync and operational commissioning require separate receipts.
