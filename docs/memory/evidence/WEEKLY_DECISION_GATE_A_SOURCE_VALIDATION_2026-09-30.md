# Weekly Decision Gate A Source Validation — 2026-09-30

---
evidence_type: production_source_preflight_and_local_checkpoint
status: SOURCE_VALIDATED_LOCAL_APPLIED_V2
production_source_change: gate_a_authorized
football_model_tuning: false
runtime_change: false
source_predecessor: 457e085a0acddc1ee9d6871a1bd85b10c8deb394
---

## Authorization / Objective

After the repository-memory semantic-integrity checkpoint was pushed and
remote-verified, the user explicitly authorized the next production-source step.
The authorized scope is Gate A from the accepted weekly-decision orchestrator
design: install the fail-closed weekly decision receipt/state machine and shared
operational-health interface over existing authorities before implementing any
additional action-family capability.

This is an operability/control-plane change. It does not tune football models and
does not use observed 2026 outcomes to change v0.X physics.

## Exact Source Predecessor

Repository `main` predecessor:

`457e085a0acddc1ee9d6871a1bd85b10c8deb394`

The read-only diagnostic rechecked remote `main` at that exact commit before
cloning and validation.

## Candidate Scope

Exactly five source/test paths:

1. `fantasy.py` — thin authoritative `weekly-cycle` CLI adapter;
2. `src/gui/season_service.py` — thin service adapter using the shared receipt;
3. `src/weekly_decision_cycle.py` — canonical fail-closed receipt/state machine;
4. `src/weekly_operational_health.py` — shared operational-health receipt builder;
5. `tests/test_weekly_decision_cycle_gate_a.py` — Gate A regressions.

The control-plane candidate reuses existing football authorities. It does not add
a second player optimizer or specialist model.

## Exact Candidate Identities

| Path | SHA-256 | Git blob |
| --- | --- | --- |
| `fantasy.py` | `92f22dff63a8c09bcf450c48cd2ce0ee173f34e75f8fdecfb330070a046f4e98` | `dd3a0a2b39ea1c6b424e71f6a11273f2503ccc64` |
| `src/gui/season_service.py` | `b8e6e324afadb341ed007ba1a6ae6c0ff67ec00f5cd9ffb59d97cfe47dbb34ef` | `561c16759fec24429e1517d2122bf3eafa142fd5` |
| `src/weekly_decision_cycle.py` | `adff80bc9558d6348ce45c6d5e8269c77def46112c4ac5d53bfb72a0b7eb4933` | `57110226dce55c60dbed05e97628ab3a04d04035` |
| `src/weekly_operational_health.py` | `efaf88a845eb53d874f7dcbcb2efbaf531b0dd81e2170b13222451e1cf3d6b41` | `e36e8a10ab0d768f6fb029d93c80c2fea5ecc204` |
| `tests/test_weekly_decision_cycle_gate_a.py` | `ffedce938a8ee532daeaa6d16bcc0b3120832c2d72c7d0b569b0d4598e233ce3` | `166a469ea87fd9a881e894dce7eba20a78525857` |

## Diagnostic Package / Operator Receipt

Diagnostic package:
`weekly_decision_gate_a_source_preflight_v1_20260930`

Archive SHA-256:
`e0320dafbd2f0296fd1173d262a7c6d04d025c635867c186eb4b35044fe8b160`

Operator-executed isolated-clone preflight reported:

- predecessor: exact `457e085a0acddc1ee9d6871a1bd85b10c8deb394`;
- remote movement guard: PASS / same commit;
- changed paths: exactly 5;
- targeted Gate A pytest: PASS;
- full repository pytest: PASS;
- compileall: PASS;
- strict memory health: PASS;
- `git diff --check`: PASS;
- all five exact result SHA-256/Git-blob identities: PASS;
- control root: untouched;
- commissioned runtime: untouched;
- staging/commit/push: not performed.

## Gate A Fail-Closed Contract

The candidate makes the completion state mechanically depend on explicit channel
and health receipts. In particular:

- missing/unsupported required action coverage -> `INCOMPLETE_COVERAGE`;
- missing/stale/failed required health -> `BLOCKED_HEALTH`;
- material decision-time state change -> `CAPTURE_REQUIRED`;
- narrow channel HOLDs cannot be upgraded independently to roster-wide HOLD;
- CLI and service use the same shared receipt/classifier surface.

## Explicit Gate B Blockers

Gate A intentionally leaves these capabilities unresolved and therefore blocking
where required:

- current specialist WAIVERS as uncertain acquisitions;
- IR/reserve/open-slot and IR-move-plus-add transitions;
- decision-time multiweek absence propagation;
- automated multi-asset/unequal player trade search;
- specialist-inclusive trade composition preserving `P ⊕ D ⊕ K`.

Their absence is a receipt result, not a negative football recommendation.

## Local Apply Lineage / Sparse-Control-Root Boundary

The control root is a sparse checkpoint/synchronization surface, not the complete
runnable application tree. Application/runtime pytest authority therefore remains
the isolated full clone used by the source preflight and, later, the commissioned
runtime.

Local-apply carrier `weekly_decision_gate_a_local_apply_v1_20260930` incorrectly
required root-level `fantasy.py` and `src/gui/season_service.py` to exist before
its exact predecessor/result guard ran. The operator receipt was:

- `MODIFICATION_STATE=FAILED BEFORE MODIFICATION`;
- error: project root did not match the assumed full source layout.

Classification: `PACKAGE_ROOT_LAYOUT_ASSUMPTION_DEFECT`. No source, memory, Git,
or runtime state changed, so the isolated-clone Gate A source validation remained
valid.

Corrected carrier `weekly_decision_gate_a_local_apply_v2_20260930` preserves the
exact five preflight-proven source/test result identities. Before any write it
rechecks remote `main` at the exact predecessor, creates a temporary read-only
clone, reconstructs the two modified existing source files from that exact source,
and verifies their expected result SHA-256/Git-blob identities. Absent application
paths are valid predecessor state on the sparse control root; any unexpected
existing content remains fail-closed.

The successful local checkpoint writes only the reviewed changed source/test paths
plus this durable state/evidence update to the sparse control-root synchronization
surface. It does not stage, commit, push, or modify the commissioned runtime.
Runtime synchronization and commissioning remain separate after source
publication.

`durable_memory_updated: true`
