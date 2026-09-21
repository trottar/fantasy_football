# Current Handoff

`CURRENT.md` is authoritative. This file is a compact resume/operational-warning
surface and cannot override it.

## Last Remote-Verified Checkpoint

`24a7e57794b0325510349ae163cd36b2f6c19070`

Commit: **Add v1.0A data-source season-sync shadow pilot**.

## Active Technical Checkpoint

**Phase 1A data-source season-sync shadow pilot — RUNTIME COMMISSIONED**

Current classification:

`SOURCE PUSHED / REMOTE VERIFIED / RUNTIME SYNCHRONIZED / TARGETED TEST PASS / PAIRED PROBE PASS / FULL PYTEST PASS / COMPILEALL PASS / FINAL IDENTITY PASS / PERSISTENCE DISABLED`

The commissioned runtime remains `v0.36-repack1`, internal `VERSION = 0.36`.
Only `src/observability/shadow_pilot.py` and `src/season_snapshot.py` were
synchronized for this runtime step. Their final identities match repository
commit `24a7e57794b0325510349ae163cd36b2f6c19070`.

The runtime paired probe measured 2,028,200 ns baseline median, 2,201,600 ns
observed median, 173,400 ns incremental overhead, and 0.08549452716694605
relative overhead. Behavior/state/privacy gates passed; no arguments, returned
values, exception messages, or persistent sink were captured.

## Resume Instruction

1. Read the complete bootstrap set.
2. Treat Phase 1A runtime commissioning as complete.
3. Finish the memory-only commissioning-closure checkpoint through staged
   schema-2 manifest, commit, push, and remote verification.
4. Do not rerun Phase 1A tests without new evidence.
5. After closure is remote-verified, begin Phase 1B closure instrumentation only.
6. Preserve the Week 3 prospective-capture deadline.

## Critical Boundaries

- control root != staging clone != commissioned runtime;
- no provider-level instrumentation;
- no arguments, returned payloads/paths, authenticated data, or exception
  messages in observability events;
- persistent sink remains disabled;
- no football/model semantic change;
- no direct GitHub connector writes for checkpoints;
- successful operator steps may return concise summary blocks; request full logs
  only for failures or missing evidence.
