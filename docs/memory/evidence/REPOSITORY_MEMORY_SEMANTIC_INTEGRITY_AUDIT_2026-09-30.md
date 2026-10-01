# Repository Memory Semantic Integrity Audit — 2026-09-30

## Identity

- predecessor commit: `43c77e35f5fc2f6456e7374a6f06708c01a161d7`
- predecessor tree: `bbe7b6e53f1771373cc834543a04abe0827d61ce`
- audit class: read-only repository memory / tooling audit
- production source write: false
- football model tuning: false

## Classification

`ACTIVE_MEMORY_SEMANTIC_INTEGRITY_GAP = CONFIRMED`

The existing strict checker could pass while active repository memory remained
semantically stale in deterministic ways.

## Confirmed Defects

1. `CURRENT.md` still instructed publication of the source/design checkpoint even
   though that checkpoint was already the durable predecessor.
2. `roadmap/STATUS.md` still labeled that audit `MEMORY CHECKPOINT PENDING`.
3. the live handoff said no exceptional transfer state was active but retained
   routine stale phase/workflow prose forbidden by maintenance policy.
4. `roadmap/SEASON_2026.md` still labeled Week 3 as an active hard capture gate
   while `CURRENT.md` identified Week 4.
5. `docs/KNOWN_ISSUES.md` retained completed memory-refinement and obsolete Week 3
   active-gate items.
6. `DECISION_LOG.md` omitted multiple canonical D-010 through D-020 records and
   D-004 wording could be misread as transaction exclusion.
7. `templates/MEMORY_UPDATE.md` retained routine handoff-rewrite and ZIP-era
   delivery wording.
8. `templates/WEEKLY_RECAP.md` lacked a decision-completion / operational-health
   receipt section and no canonical weekly decision receipt template existed.
9. `patches/DIAGNOSTIC_TOOL_QA_PROTOCOL.md` retained ZIP-era exact-delivery steps.
10. `tools/check_memory_health.py` and its tests did not reject these deterministic
    contradictions.

## Failed Hardening Carrier Lineage

### v1

Package:
`repository_memory_semantic_integrity_hardening_20260930_v1.ffpkg`

Archive SHA-256:
`13a1c46b38e3b370a3a0322c4e74fa97def2c31bbb0769326041b589c3df019e`

Observed failure:

`ApplyError:patch predecessor marker mismatch: tools/check_memory_health.py count=2`

Classification:
`PACKAGE_PREDECESSOR_MARKER_CARDINALITY_DEFECT`

The selected textual predecessor block appeared twice. The deterministic
single-replacement guard correctly rejected it.

### v2

Package:
`repository_memory_semantic_integrity_hardening_20260930_v2.ffpkg`

Archive SHA-256:
`a056fb50c37b8a4790d839b78708e7487eccb274ceb631a03ad6e641ae307c7a`

Observed failure:

`ApplyError:prewrite patch cardinality mismatch: tools/check_memory_health.py op=1 count=0`

Classification:
`FAILED BEFORE MODIFICATION`

The v2 prewrite simulation correctly stopped before writes, but the expected
anchor itself had been fabricated. Exact source proved that
`REQUIRED_REPO_FILES` begins with `AGENTS.md`, `CURRENT.md`, and `MEMORY.md`
before `MAINTENANCE.md`; prepending the constant declaration to a later mid-block
marker therefore created text that did not exist.

Neither failed carrier produced a durable Git checkpoint. The durable remote
predecessor remained `43c77e35...` throughout the recovery audit.

## Root QA Failure

The assistant had validated properties of constructed markers without first
proving those exact markers against authoritative predecessor source. Putting a
new cardinality simulation inside v2 still made the operator the first executor
of that final package-level validation.

This violated existing rules to derive inspectable deterministic values from
source, validate rendered/extracted artifacts, and keep the operator out of the
first-validator role.

## Successor Design

The successor therefore:

- uses exact predecessor Git blob identities for every overwritten file;
- uses nonexistence guards for new paths;
- carries complete final-file payloads instead of chained predecessor text
  substitutions;
- validates candidate semantics in a disposable predecessor tree before carrier
  construction;
- validates the exact reconstructed carrier and controlled failure/idempotence
  paths before delivery;
- leaves `docs/memory/manifest.json` untouched during local apply because that
  registry belongs to the later isolated staged Git-blob representation.

## Successor Pre-Delivery QA Recovery

The first assistant-side v3 carrier dry run stopped **before modification** on a
contract-validation defect: canonical JSON serialization sorted the predecessor
identity map, while the package validator incorrectly required the separately
stored target list to preserve that map's insertion order. Target inventory is a
set contract, not an order contract.

Classification: `PRE-DELIVERY QA FAILURE / FAILED BEFORE MODIFICATION`.

The disposable predecessor remained unchanged. The validator was corrected to
require exact set equality plus uniqueness, consistent with the existing rule not
to impose order semantics on unordered allowlists. The exact carrier was then
rebuilt and the full package QA sequence restarted from a fresh predecessor.

## v3 Operator Validation-Scope Failure

Package:
`repository_memory_semantic_integrity_hardening_20260930_v3.ffpkg`

Observed operator failure:

- targeted memory-health tests and strict memory health had already passed;
- the package then invoked bare repository-root `pytest -q`;
- pytest recursively collected historical `archive/` trees and multiple retained
  `fantasy_season_v0_*` release trees into one process;
- those independent historical trees reuse the `src` package name and are not a
  valid single import environment, producing 878 collection errors;
- the package returned nonzero and its guarded failure path restored the
  predecessor targets before exit.

Classification:
`PACKAGE_VALIDATION_SCOPE_DEFECT / ROLLBACK REQUIRED`

The defect was in the validation command, not in the memory payload. The first
successor attempt, v4, narrowed collection to the root `tests/` tree. Operator
evidence then proved that this was still the wrong authority surface.

This incident also corrects the assistant-side v3 pre-delivery claim: the
disposable tree's bare pytest could not expose repository-root recursive
collection because that disposable tree intentionally omitted historical and
release copies. Exact package validation must establish whether a proposed test
command is applicable to the real target surface, not merely whether it passes in
a reduced dependency tree.

## v4 Operator Validation-Surface Failure

Package:
`repository_memory_semantic_integrity_hardening_20260930_v4.ffpkg`

Archive SHA-256:
`2a4e261b73a5398c8b35ceaabd3c7f9b469fdcf16f4a8b36ffc84942e3bb0b04`

Observed operator failure:

- the package correctly passed carrier preflight and reached post-write
  validation;
- `pytest -q tests -p no:cacheprovider` collected only the root tests, avoiding
  the v3 historical-tree collision;
- five observability tests then failed during collection because the synchronized
  control root lacks application/runtime modules including `src.season_utility`,
  `src.data_sources`, and top-level `fantasy`;
- the package reported `MODIFICATION_STATE=ROLLED BACK` and exited nonzero.

Classification:
`PACKAGE_VALIDATION_AUTHORITY_SURFACE_DEFECT / ROLLED BACK`

This is consistent with the established project architecture: the control root is
a synchronization/checkpoint surface, while the commissioned runnable release
tree is a distinct authority for application imports and runtime validation.
Presence of application-oriented test files in the control root does not make the
control root a complete runnable application tree.

The v5 correction therefore does **not** weaken a valid gate. It removes an
inapplicable application/runtime gate from this memory-only local apply and keeps
the complete applicable validation set:

- compile the changed memory-health tool/test;
- memory-health self-test;
- full `tests/test_memory_health.py` regression suite;
- strict memory health against the rendered control-root state;
- rendered-target whitespace validation;
- `git diff --check` on the exact target allowlist;
- exact predecessor/result identities, manifest non-modification, and
  extracted-carrier success/failure/rollback/idempotence QA.

Application/runtime pytest remains required when application source/runtime is the
surface being changed or commissioned, and must run in the validated complete
staging/runtime import context.

Neither v3 nor v4 produced a durable repository checkpoint.

## Scope Boundary

This audit/hardening does not modify football/model/application/runtime source,
does not authorize the designed weekly orchestrator, does not activate
persistence, and does not submit any roster transaction.
