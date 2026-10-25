# Week 8 M2 — B2b4b Conditional Joint Predictive Response

**Source candidate:** `week8_b2b4b_ordered_joint_predictive_source_20261025_v1`.
**Predecessor:** `e79735927552c4d889bdd5e37961a68ccb34a3c4` (B2b4a exact tree `a0c445da6d25b016c4f2b3a6037704ceefd21504`).
**State:** read-only source-only diagnostic, opt-in native MC, uncommissioned. No ESPN transaction or recommendation authority, no football-physics changes.

## Narrow question and state

B2b4a establishes two sequential trade orders and up to 16 conditional free-agent fill states per order under an identical frozen league snapshot. No B2b3 standalone utility may be summed to infer joint value. For each B2b4a structurally passing case, reconstruct **one complete final league roster state** plus a distinct market ledger. Ensure unique league-wide player identities and conservation of all frozen assets. A dropped/released player remains `RELEASED_PROCESSING_UNKNOWN` in the B2b4a ledger and is **not** an immediately acquirable FREEAGENT in the simulated provider pool. A frozen FREEAGENT consumed by an assumed successful fill is removed from the copied pool; other frozen market statuses persist.

`tools/operations/action_joint_predictive_b2b4b.py` invokes B2b4a's complete frozen frontier and respects every BLOCKED case without invoking MC. It fails closed on forged/lost identities, duplicate ownership, non-conserved release ledger, malformed scenario responses and input mutation. It does not re-enumerate or thin B2b4a cases. Maximum 32 cases and 16–128 per-manager native samples; opt-in only. CHECK_ONLY performs B2b4a source/structure checks without native MC. Optional complete JSON output is a new private file directly inside the commissioned runtime `data` directory.

## Native physics response

For a passing conditional case, use the unchanged commissioned `specialist_trade` machinery: normalize final roster ownership for every team, build a P-only hybrid over original specialist ownership, then compose final P/D/K results at complete-roster utility boundaries. Use `st._baseline_state` and `st._composed_after_state` per affected manager with cached baseline scenarios, and source-equivalent `splice_effective_week` assuming positive trade-review hours imply **modeled** next-week effect. This is not proof of actual ESPN completion or timing. The native runtime source/version guard from B2a applies. No new likelihood parameters or tuned predictions are introduced.

Within each affected manager, calculate paired `U(joint) - U(HOLD)` and separately paired changes in the native opponent reference (averaged over remaining season with native weights). This opponent-reference response reflects the entire joint conditional roster change, **not** a proven downstream pickup or scoring impact of a released asset. Preserve the released IDs as an uncertainty ledger. When both ordered cases share an identical conditional fill state, compare their modeled within-manager utilities, without treating separate managers' scenario indices as correlated joint outcomes. Results are not summed or probabilistically averaged across managers/cases.

## Explicit limitations and gates

- B2b4a static PASS is hypothetical and may not be ESPN-executable; league config and effective-order locks are not app certified.
- Future manager trade acceptance, correlated acquisitions/waiver success and release-reacquisition probabilities remain `UNKNOWN`. No released asset becomes available through an assumed claim.
- The common modeled next-week effective date cannot distinguish asynchronous processing between orders; equal final rosters may produce equal modeled responses. A separate event-time evidence gate is required.
- The native opponent-reference shift is measurable in this conditional model; full third-party player acquisition/field response is **not** estimated without a source-bound behavior and timing model.
- Player injury contingencies, broader weekly action coverage, current ESPN drift and user approval remain independent blockers.

All output is `BLOCKED_B2B4B_CONDITIONAL_JOINT_MC_ONLY`, `certified_actions=0`, `espn_action_authority=NONE`. Guarded installation is local-apply only, followed by assistant verification, exact isolated staging, full QA and separate publication. No native simulation, six-provider sync, capture, ESPN GET/POST, runtime edit, Git staging or push is performed by the installation carrier.

**Next:** model decision-time event ordering, conditional third-party release uptake/manager behavior and independently evidenced acquisition correlations without forced probabilities; then M1/M2 end-to-end deadlines/legal action-screen certification and one-command report. Protect all Week 8 prospective capture gates. No 2026-observation tuning of v0.X.

`durable_memory_updated: true`
