# Weekly Decision Gate B2a IR Roster-State Source Validation — 2026-10-01

---
evidence_type: production_source_preflight_and_local_checkpoint
status: SOURCE_VALIDATED_LOCAL_APPLIED_V1
production_source_change: gate_b2a_authorized
football_model_tuning: false
runtime_change: false
source_predecessor: f6900878c97ef4dd9148b924fa41167337086a2c
---

## Authorization / Objective

Gate B production-source work was previously explicitly authorized by the user.
B2a is the narrow current IR/open-slot representation slice produced by the B2
audit. It represents league-legal current roster capacity and move-to-IR state
without inferring a multiweek recovery horizon or changing intrinsic football
value.

B2a does not close B2b multiweek absence propagation, automated broader trade
search, or specialist-inclusive trade composition.

## Classification / Evidence Boundary

The sanitized B2 audit established:

- one configured IR slot, no current IR occupant, and one current ESPN `OUT`
  roster player;
- normalized `injury_status` matches raw ESPN `player.injuryStatus` on all 16
  roster rows;
- all 16 roster players expose IR in generic `eligibleSlots`, including active
  players, so slot compatibility is not current IR-eligibility authority;
- neither normalized nor raw ESPN state contains an explicit return week,
  absence-through week, or equivalent multiweek horizon.

The accepted B2 classification is therefore
`B2_IR_MOVE_PLUS_ADD_PATCHABLE_ABSENCE_HORIZON_STILL_MISSING`.

B2a may represent current ESPN-status-qualified IR/open-slot transitions. It may
not treat the resulting open active-roster capacity as permanently available for
season valuation. B2b remains fail-closed.

Canonical audit evidence:
`WEEKLY_DECISION_GATE_B2_IR_ABSENCE_AUDIT_2026-10-01.md`.

## Failed v1 Preflight Lineage

B2a source-preflight v1 failed **before modification** because strict memory
health classified the prior Windows-worktree `CURRENT.md` as `SOFT`. Control root
and commissioned runtime were untouched. The candidate was not rejected on
football/source behavior.

The active-memory compaction checkpoint was then published at predecessor role
`f6900878c97ef4dd9148b924fa41167337086a2c`, restoring strict memory health. The unchanged B2a candidate was
regenerated as source-preflight v2 against that successor predecessor.

## Exact Source Predecessor

Repository `main` predecessor:

`f6900878c97ef4dd9148b924fa41167337086a2c`

Published predecessor tree:

`eaf8b2efc40b9efbfc9b08b318975394a09dc358`

The operator preflight rechecked remote `main` at that exact commit before
validation.

## Candidate Scope

Exactly three source/test paths:

1. `src/ir_roster_state.py` — new pure current IR/active-roster state authority;
2. `src/weekly_decision_cycle.py` — adapts the B2a representation into the weekly
   IR receipt while preserving fail-closed replacement/temporal coverage;
3. `tests/test_weekly_decision_gate_b2a_ir_roster_state.py` — focused B2a
   regressions.

Commissioned B1 specialist policy and `transaction_manager.py` are unchanged.

## Exact Candidate Identities

| Path | SHA-256 | Git blob |
| --- | --- | --- |
| `src/ir_roster_state.py` | `ee60b036801f2cc29a15f41a7fd65cd57b0e784591730590ec2feb5cdd35e0f1` | `d767baa7e25a8e630d99c358d5e039322a2f2cb4` |
| `src/weekly_decision_cycle.py` | `270f0925afdcad5767a55a20204e1a24c01319c64653640ba1f6beee72a020c2` | `e3513f54a9decbc108a23a14ba06a3a68442aed8` |
| `tests/test_weekly_decision_gate_b2a_ir_roster_state.py` | `e2309cc88f4da7f90c02bf4031f371276c7dea52d79bb4311933822bb409f92f` | `75c9a6edc32cce6b87a60f0b4aa9c99c72f364fb` |

## Diagnostic Package / Operator Receipt

Diagnostic package:
`weekly_decision_gate_b2a_ir_roster_state_source_preflight_v2_20261001`

Archive SHA-256:
`9a2481d0adee2e1d8f36d6aeeb90a8160bf1f3872890762d948af2f1d6ff6114`

Operator-executed isolated-clone preflight reported:

- predecessor and remote: exact `f6900878c97ef4dd9148b924fa41167337086a2c`;
- source audit prerequisite:
  `weekly_decision_gate_b2_ir_eligibility_rule_audit_v2_20261001`;
- source-audit archive SHA-256:
  `fbf060de15efeb6d1551d752a7590f170d70d9721dfebd6c1f210b90598584ea`;
- changed paths: exactly 3;
- targeted B2a/Gate A/B1 pytest: PASS;
- full repository pytest: PASS;
- `compileall`: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS;
- all three exact result SHA-256/Git-blob identities: PASS;
- control root and commissioned runtime: untouched;
- staging/commit/push: not performed;
- runner exit code: 0.

The operator receipt is authoritative source validation for these exact result
identities.

## Local Apply Boundary

This local checkpoint applies the exact three source/test result identities plus
five durable-memory paths recording B2a source validation. The apply guard
re-establishes remote `f6900878c97ef4dd9148b924fa41167337086a2c`, exact existing predecessor blobs, package
payload identities, and new-path absence before any write.

The local apply does not stage, commit, push, or modify the commissioned
`v0.36-repack1` runtime. `docs/memory/manifest.json` remains unchanged until the
separate isolated-staging step regenerates schema-2 manifest state from staged
Git blobs.

B2a is not operational until source publication plus separate runtime preflight
and runtime commissioning succeed.

## Remaining Gate B Blockers

After B2a source validation, roster-wide completion remains blocked by:

- B2a publication and runtime commissioning;
- B2b explicit decision-time multiweek absence/return horizon and temporal
  roster-capacity propagation;
- broader automated multi-asset/unequal player trade search;
- specialist-inclusive trade composition preserving `P ⊕ D ⊕ K`.

No observed 2026 result is used to tune v0.X.

`durable_memory_updated: true`
