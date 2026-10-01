# Weekly Decision Gate B2 — IR / Absence State Audit Evidence

**Date:** 2026-10-01
**Source checkpoint predecessor:** `6363ded2a3c6b4fa09de6a8b7b274ebb076ebfea`
**Runtime:** `v0.36-repack1`, internal `VERSION = 0.36`
**Classification:** `B2_IR_MOVE_PLUS_ADD_PATCHABLE_ABSENCE_HORIZON_STILL_MISSING`
**Production modification during audits:** none

## Question

Can the commissioned Week 4 state represent league-legal IR/open-slot
transitions and decision-time multiweek absence state without inventing data or
changing football physics?

## Audit v1 — Capacity / Schema Probe

Package:
`weekly_decision_gate_b2_ir_absence_state_audit_v1_20261001`

Archive SHA-256:
`ed6973f22b5d92e20ead6c30c35f6c08c4192d097894b80d8e490427d16a9dd6`

Accepted sanitized receipt:

- roster rows: 16;
- active roster capacity / occupancy: 16 / 16;
- open active roster slots: 0;
- configured IR slots: 1;
- current IR occupancy: 0;
- open IR slots: 1;
- raw ESPN IR slots: 1;
- configured/raw IR count match: true;
- rows with `eligible_slots`: 16;
- rows advertising IR compatibility: 16;
- hard-unavailable rows advertising IR compatibility: 2;
- explicit normalized absence-horizon fields: none;
- explicit raw ESPN absence-horizon fields: none;
- raw authenticated content, player names/IDs, and fantasy-team identity exported:
  false.

The v1 classifier initially reported IR capacity/eligibility evidence as complete.
That interpretation is **superseded** because the raw measurement showed every
roster player advertising IR compatibility. Generic `eligible_slots` therefore
could not safely represent current IR eligibility.

## Audit v2 — ESPN IR Eligibility Rule Input

Package:
`weekly_decision_gate_b2_ir_eligibility_rule_audit_v2_20261001`

Archive SHA-256:
`fbf060de15efeb6d1551d752a7590f170d70d9721dfebd6c1f210b90598584ea`

Accepted sanitized receipt:

- roster/raw roster rows: 16 / 16;
- configured/open IR slots: 1 / 1;
- current IR occupancy: 0;
- platform rule source label:
  `ESPN_FAN_SUPPORT_UPDATED_2026-08-18`;
- platform rule represented by the probe:
  `OUT_OR_INJURY_RESERVE_ONLY`;
- normalized ESPN injury-status counts:
  `ACTIVE=12`, `DAY_TO_DAY=1`, `MISSING=1`, `OUT=1`, `QUESTIONABLE=1`;
- raw player injury-status counts: exact same distribution;
- normalized/raw player status matches: 16;
- mismatches: 0;
- missing joins: 0;
- raw IR-slot-compatible roster players: 16;
- raw IR-slot-compatible `ACTIVE` rows: 12;
- raw IR-slot-compatible `injured=false` rows: 15;
- explicit IR-eligibility player flag/settings: none;
- status-rule IR-eligible, not-currently-IR rows: 1 (`OUT`);
- IR move-plus-add capacity precondition: true;
- explicit normalized/raw absence-horizon fields: none;
- raw authenticated content, player names/IDs, and fantasy-team identity exported:
  false.

Raw evidence therefore establishes that ESPN `player.injuryStatus`, not generic
`eligibleSlots`, is the preserved platform-rule input for current IR legality in
this snapshot.

## B2 Split Classification

### B2a — Current IR/Open-Slot State

Patchable from direct captured facts:

- configured IR capacity;
- current IR occupancy;
- current active-roster occupancy/capacity;
- current ESPN `injury_status`;
- current lineup/IR placement state.

B2a may represent legal current transitions such as moving an ESPN-status-qualified
player into an open IR slot and the immediate active-roster slot opened by that
transition.

B2a must **not** use generic `eligible_slots` as current IR eligibility and must
not change intrinsic player/DST/K football value.

### B2b — Multiweek Absence / Return Horizon

Not represented by the captured state. There is no explicit normalized or raw
ESPN return week, absence-through week, or equivalent horizon field.

Therefore no v0.X production path may infer a recovery horizon from injury type,
injury start date, generic status priors, or retrospective outcomes. The season
model may not treat an IR-created 17-player state as permanently available until
an explicit decision-time temporal capacity state is represented.

## B2a Source Candidate / Failed Preflight v1

Prepared candidate package:
`weekly_decision_gate_b2a_ir_roster_state_source_preflight_v1_20261001`

Archive SHA-256:
`a6d7ef5006337d6ef4d7c16800649a84d77badd7176eea689336bd8d8074b47a`

Candidate scope is exactly three paths:

1. `src/ir_roster_state.py` — new pure IR roster-state authority;
2. `src/weekly_decision_cycle.py` — weekly receipt adapter;
3. `tests/test_weekly_decision_gate_b2a_ir_roster_state.py` — focused regressions.

Candidate result identities:

- `src/ir_roster_state.py`:
  SHA-256 `ee60b036801f2cc29a15f41a7fd65cd57b0e784591730590ec2feb5cdd35e0f1`,
  Git blob `d767baa7e25a8e630d99c358d5e039322a2f2cb4`;
- `src/weekly_decision_cycle.py`:
  SHA-256 `270f0925afdcad5767a55a20204e1a24c01319c64653640ba1f6beee72a020c2`,
  Git blob `e3513f54a9decbc108a23a14ba06a3a68442aed8`;
- `tests/test_weekly_decision_gate_b2a_ir_roster_state.py`:
  SHA-256 `e2309cc88f4da7f90c02bf4031f371276c7dea52d79bb4311933822bb409f92f`,
  Git blob `75c9a6edc32cce6b87a60f0b4aa9c99c72f364fb`.

Assistant-side reconstructed targeted regressions passed 20/20 before delivery.
The operator preflight then failed **before modification** at strict memory
health:

- `CURRENT.md`: 160 lines, 8,346 Windows-worktree bytes;
- threshold status: `SOFT`;
- strict status: `ATTENTION`;
- control root: untouched;
- commissioned runtime: untouched;
- staging/commit/push: not performed.

The canonical LF form of that `CURRENT.md` was 8,186 bytes; CRLF representation
exposed the 8 KiB soft threshold. Independent of line-ending representation, the
active file also contained completed B1 commissioning chronology and was due for
role-based compaction under `MAINTENANCE.md`.

The failure does not validate or invalidate the B2a source candidate. Operator
full source validation did not complete.

## Decision

Perform a memory-only active-state compaction checkpoint first. Preserve this
audit/failure lineage here, keep `CURRENT.md` focused on the B2 frontier, and do
not weaken strict memory health.

After that checkpoint is remote-durable, regenerate the unchanged B2a source
preflight against the new remote predecessor and run its full operator validation.
Do not rerun the passed B2 audit probes or Gate A/B1 source/runtime gates without
new contradictory evidence.

`durable_memory_updated: true`
