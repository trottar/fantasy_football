# Week 8 M2 — B2b4a Ordered Joint Trade State/Field Audit

**Checkpoint candidate:** `week8_b2b4a_ordered_joint_structural_source_20261025_v1`.
**Predecessor:** remote-verified `d1720be7a394204dba0be84ef233766c67501236` (B2b3 source published; not runtime commissioned).
**State:** source-only, read-only, uncommissioned; no native MC, provider access, probability calibration, actionable trade recommendation or ESPN writes.

## Narrow question

The B2b2 pair graph can report overlapping offers but does not advance a single common league state. B2b3's paired football response is conditional on **one** trade and one future-fill outcome. A pair of separately attractive trades may be mutually incompatible after the first transfer/drop, or may release an asset that becomes part of the league's field. Can the system represent and classify that sequential state *without* assuming trade acceptance, independent future acquisition success, a guaranteed available release, or summable football utility?

## Deterministic B2b4a candidate

`tools/operations/action_joint_state_b2b4a.py` consumes frozen snapshot, prospective capture, native nine-channel receipt, and explicit league rules; reuses B1's provenance-bound frontier and the complete B2b2 structural branch lattice. The caller selects exactly two distinct offer IDs and the complete explicit drop identity set for each. Missing, duplicate, truncated or inconsistent frontiers and unknown frozen drop permissions/locks fail closed.

- Rebuild all teams' initial asset ownership and exact frozen free-agent pool, rejecting league-wide duplicate ownership and market collisions.
- Enumerate both offer orders and every combination of their **unweighted** B2b2 conditional fill branches. Limit to four combined modeled fill variables (at most 16 cases per order); reject overlapping future fill identities between the two offers as an unmodeled coupled acquisition process rather than multiplying independent flags.
- For each conditional ordered case, require current owner to hold the outgoing asset at that step; require the exact proposed user/partner drops to be currently owned, affirmatively droppable and unlocked in frozen evidence. Apply transfers, compulsory drops and hypothetical frozen-FREEAGENT fills to a deep-copied league state. Never acquire a `WAIVERS` asset as a guaranteed fill or substitute a released player as immediately available.
- Validate each step's user/partner frozen static position minima/maxima and roster capacity **before committing that step to the copied state**. Report whose action cannot proceed, all surviving owner identities, and player IDs released back into a separate market-status-unknown field ledger. Market, owner and source inputs remain unchanged.
- Do not infer ESPN transaction processing, future lock legality, trade acceptance/order, future market availability, shared acquisition probabilities, player field-value response, or injury downside. A static path `PASS` means a **hypothetical** structurally consistent ordering under explicit conditions, not an action certificate.

Private full results may be written only as a new JSON file directly under the installed runtime's `data` directory. The console prints only aggregate counts/states. The CLI is entirely read-only and offers no `--execute-native` or transaction path. `BLOCKED_B2B4A_ORDERED_STRUCTURAL_ONLY`, `certified_actions=0`, and `espn_action_authority=NONE` are unconditional; B2b1–B2b3 and commissioned football physics remain untouched.

## Evidence and next gate

Synthetic tests must prove two valid orders, different conditional fill states, immutable input and source data, released-player field identities, direct shared-outgoing conflict, frozen permission block, shared-fill dependency block, missing/WAIVER fill block, boolean/identity contract, and bounded branch count. The package installer must validate runner `--package-id`, target predecessor hashes, protected create-only paths, rollback, exact generated memory, focused tests, compilation and strict memory health. Isolated staging, full checkout QA and guarded publication are separate evidence gates.

**Next B2b4b:** jointly simulated complete-roster football utility for each valid *ordered* branch, including player release/opponent field response and matched manager-specific random streams, without summing standalone trade results. Separately discover genuine decision-time market/manager acquisition evidence for correlated probabilities. Without such evidence, conditional branch weights remain UNKNOWN. Live ESPN candidate cutoffs, processing, legal action screens, bounded event-epoch reconciliation, injury contingencies and user approval remain independent blockers.

Week 7 immutable captures and MC are preserved; user closed Week 7 operations. Week 8 prospective calendar gates outrank nonessential development. No 2026-outcome tuning of v0.X.

`durable_memory_updated: true`
