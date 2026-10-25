# Week 8 M2 — B2b4c Supplied Event-Time and Release-Uptake Evidence Boundary

**Checkpoint candidate:** `week8_b2b4c_supplied_event_timeline_source_20261025_v1`.
**Source predecessor:** B2b4b published at `792805a2d23ac9727b25ad9920f406bf2382189a`, staged/committed tree `786b7d875dd47fbe750194618b5a79f152a15776`; no B2b4b runtime commissioning.
**Status:** read-only, source-only diagnostic; no live provider access, native MC, action recommendation, source-authentication guarantee, or transaction authority.

## One narrow question

B2b4b computes a **conditional** final-joint-roster football response, but a positive ESPN review window is *not* the actual processing timestamp. B2b4a tracks dropped/released assets as market-status-unknown. Which event-order/market transitions could be reconciled against actual post-freeze observations, and what can be classified **without** promoting unverified caller-supplied evidence into a decision-time forecast or assuming that a released player instantly becomes a FREEAGENT?

## B2b4c observational design

`tools/operations/action_joint_event_evidence_b2b4c.py` calls B2b4a's complete two-order, unweighted conditional branch audit. No branch trimming, probability fit or native MC. A frozen, aware `snapshot_utc` is mandatory. With no optional evidence file the result is UNKNOWN for all future event times and release statuses. An explicitly supplied evidence envelope must bind the frozen canonical snapshot hash and an aware observation as-of timestamp. Every event must carry its own frozen hash, source-kind label, source fingerprint, event time and observation time, with **snapshot freeze < event time <= observation time <= as-of**. Only 64 claimed events are considered, and malformed/over-budget records block entirely.

Recognized supplied claims, each bound to an exact B2b4a conditional case:

- `TRADE_PROCESSED` for the exact ordered offer and step; duplicate steps or reversed/equal claimed processing times block that case. An observed single step remains partial, not a two-trade success.
- `RELEASE_STATUS` only for a player B2b4a explicitly released in a successfully applied step, and never before that step's processing claim. Preserve whether the supplied market status is `UNKNOWN`, `WAIVERS`, `FREEAGENT` or `ROSTERED`; don't convert current status into a future availability certificate.
- `THIRD_PARTY_ACQUIRED` only for an explicit released asset, by a frozen league team that is **not** the user or either trade partner, after its release-processing claim and a preceding supplied `FREEAGENT` transition. `WAIVERS` or an absent status claim cannot silently become a successful claim, and competing duplicate third-party acquisitions block.

These are **syntactic and causal consistency checks for an untrusted evidence envelope**. Neither a plausible `source_kind` string nor a 64-character digest authenticates ESPN, proves provider provenance, proves action-screen legality, or establishes that an event really happened. A later observed event is explicitly **post-freeze**, not usable as an earlier prospective prediction. Outputs contain only aggregate classification/structural case data; optional JSON is restricted to a new file directly under the private commissioned runtime `data` directory.

The state is unconditionally `BLOCKED_B2B4C_SUPPLIED_EVENT_PROVENANCE_ONLY`, `certified_actions=0`, `espn_action_authority=NONE`. Conditional fill probabilities, correlated acceptances, exact future trade processing, future waiver success, released-asset scoring/field response and third-party roster utility remain UNKNOWN or NOT COMPUTED. B2b4b native opponent-reference changes cannot be relabeled as release-uptake effects.

## Acceptance and subsequent gate

Synthetic tests prove empty-event UNKNOWN; two consistent post-freeze processing receipts; reversed processing rejected; release chronology; a FREEAGENT-after-WAIVERS sequence before supplied uptake; missing/WAIVERS-only prerequisites rejected; unrelated/duplicate assets, bound-hash/source/clock errors, participant-as-third-party claims, immutable frozen inputs, budget, blocked-case receipts, and no native/provider/action path. Installer must preserve exact B2b4b and CURRENT predecessor blobs, require create-only source/test/architecture paths, accept the generic runner's `--package-id`, prevalidate rendered memory, back up and roll back CURRENT, run targeted regressions, compilation and strict memory health. Isolated staging/full QA and publication are separate gates.

**Next evidence gate:** establish an independently attested, decision-time-safe ESPN event producer and transaction/action-screen cutoff evidence with exact epoch/asset binding. Only after that consider bounded downstream field response MC and manager-acquisition behavior using real causal observations; do not fit empirical v0.X manager/football parameters from hindsight. Implement M1/M2 comprehensive legal decision certification and one-command report before M3 scheduled operation. Week 8 prospective capture deadlines outrank all nonessential development.

`durable_memory_updated: true`
