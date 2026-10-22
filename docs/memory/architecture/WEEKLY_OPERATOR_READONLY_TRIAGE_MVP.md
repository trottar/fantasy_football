# Weekly Operator — Permanent Read-Only Decision Triage MVP

**State:** local-apply source candidate, not runtime commissioned or ESPN transaction authority. Parent checkpoint: remote-verified B2b2 commit `b45ba6abea843bed95ea1fabacc323bdb7b96399` (tree `f40f2c50f3a98b506ed62777e6f1202b4573995e`). `v0.36-repack1` remains commissioned and unchanged.

## Why this exists

The 2026-10-22 full native nine-channel receipt returned `COMPLETE / ACTION_REQUIRED`, with lineup and two trade families marked ACTION. A second live ESPN read disclosed one changed market record. A follow-up revealed a Lamar Jackson-for-Jacoby Brissett QB optimizer selection, but Lamar's injury/participation remained questionable and trades were uncertified. Repeated ChatGPT-generated one-off audits are **not** the controller that the approved weekly operator v2 contract requires. The system must identify and explain action, hold, unresolved evidence, state-dependent refresh, and next decision time itself.

## First permanent read-only slice

`tools/operations/weekly_operator_review.py` is the first stable control-root interface:

```powershell
cd L:\Projects\fantasy_football
python -B .\tools\operations\weekly_operator_review.py --project-root .
```

No explicit snapshot, capture, receipt or player names are entered. The tool identifies the commissioned `fantasy_season_v0_36_repack1` tree through the already-validated guarded source verifier, checks strict durable memory health, identifies `latest.json` against exactly one immutable snapshot copy, locates exactly one bound prospective capture and exactly one complete nine-channel native receipt for the same epoch, checks capture SHA/prospective firewall through the commissioned source, and compares the three required dependency hashes with the receipt's commissioned runtime identity. Ambiguous or missing pairing blocks rather than reusing an old state.

It performs exactly two live read-only ESPN queries through existing installed provider code. The private roster IDs never appear in its console output. It explicitly separates owned lineup/availability drift from available-market drift, partner roster drift, transaction changes and rules changes. It prints all nine channel statuses, a named proposed lineup START/BENCH queue, frozen kickoff times and actual live lock/injury flags, DST/K/player-acquisition/IR scopes, uncertified trade counts and blockers, the next injury recheck timestamp when supported by source kickoff evidence, and the identities of the immutable inputs. No one-off package or assistant interpretation is required to produce the **scoped** triage queue.

An optimizer's lineup-selected set does not establish the exact ESPN slot assignment; no `RECOMMEND_FOR_APPROVAL` is inferred. Questionable, doubtful, out, inactive, locked, missing kickoff, owned-roster drift, unproven transaction history, market change, and partner change have explicit fail-closed outcomes. All native trade offers remain blocked pending the complete B2 certificate; player and specialist model valuation is neither changed nor rerun. Dropped players and uncertain acquisitions retain their modeled league-state meanings. Intrinsic P/D/K physics and behavior kernels are never touched.

## Still missing (not silently claimed commissioned)

This slice reports from an **existing** fresh capture and MC receipt. It does not automatically create, commission or schedule the six-provider sync, prospective capture, affected-channel rerun, or scheduled injury alerts; it does not verify app-specific slot mapping/approval at ESPN; it does not model portfolio-level correlated MC or partner acceptance. A recorded next-check timestamp is a pending obligation, not a Windows scheduled task. It does not write a persistent report or perform transactions. The 2026-10-24 protected capture takes priority over further engineering.

## Validation and publication boundaries

Synthetic deterministic tests prove complete read-only report assembly, epoch coupling, dependency checks, unknown and locked timing, current-roster versus market drift differentiation, partner drift, transaction ambiguity, incomplete channel rejection, and absence of private file modifications. Full repository `pytest`, `compileall`, strict manifest/index checks, isolated staging, guarded publication and operator live run are **separate** gates. Tests using injected ESPN results do not establish live commissioning.

`durable_memory_updated: true`.
