# Week 9 Joint Shadow — Portable Offline Synthetic Acceptance

Date: 2026-11-04
Checkpoint evidence type: sanitized operator receipt (read-only diagnostic)
Package: `week9_ir_joint_shadow_portable_offline_source_acceptance_20261104_v1`

## Provenance and local execution

- The generic `.ffpkg` runner accepted the diagnostic carrier and reported archive bytes `4065`, archive SHA-256 `2496fd7b030abeb58eba92af07a7f44bb2b2d7ff1cfcb621831952feab2687d9` and exit code `0`.
- `PUBLISHED_STAGE_COMMIT=PASS;TREE=PASS;PUBLISHED_TEST_BLOBS=PASS` against published joint-shadow commit `60bc7f5c520ae491462afc831f8a12c76fdaa753` and committed tree `2905499aaac479f4425bb430d2ec2f3a13e58aaa`.
- `PORTABLE_SOURCE_BLOBS=PASS;GUARD=PASS;VERSION=0.36` against `src/ir_replacement.py` Git blob `25ce88da16e86c7bc44a2c6f92f834d634d6a4a3`, `src/ir_joint_response.py` blob `15c681c99a307db1ea0b3dab5e590007fea26eb7`, and the unchanged guarded weekly source blob `801a87ae3787aa9e159f52964d880d8ff1d1e2ac`.
- `IMPORT_ORIGINS=PASS;SHADOW_DEFAULT_DISABLED=PASS;ACTION_AUTHORITY=NONE`.
- `PORTABLE_PUBLISHED_SYNTHETIC_PYTEST=PASS:21 passed;NO_REAL_DATA_MC=TRUE`.
- `POSTTEST_PORTABLE_SOURCE_IDENTITIES=PASS`.
- `STATUS=OFFLINE_SYNTHETIC_RUNTIME_ACCEPTANCE_PASS;READ_ONLY=TRUE;NETWORK=NONE;ESPN=NONE;CAPTURE=NONE;NATIVE_MC=NONE;GIT_WRITES=NONE;PORTABLE_SOURCE_WRITES=NONE;ACTION_AUTHORITY=NONE`.

## Classification

**Accepted: source-level synthetic runtime integration, only.** The receipt establishes that the published joint-response and IR adapter modules and the existing regression suites run from the portable installation without source drift. It does not establish that the bounded joint shadow was enabled, exercised against fresh real decision-time data, or commissioned for production action authority.

**Unresolved:** Same-channel DST/DST or K/K acquisitions, additional legal IR-move alternatives and position limits, conditional joint WAIVER claim queue and timing/dependence behavior, exhaustive complete-roster legal composite states, and independent weekly section-5A certification. No individual marginal acquisition probabilities may be multiplied to claim joint success. No invented future capacity or ESPN execution authority.

Preserve the frozen November 3/4 native MC receipts. Thursday November 5 and subsequent prospective capture gates take priority over experimental runs. Further work should proceed with one source-bound read-only synthetic diagnostic before any production-logic change or new shadow commissioning.

`durable_memory_updated: true`
