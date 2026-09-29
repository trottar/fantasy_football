# Phase 1E Persistence Controller Source Validation — 2026-09-28

## Classification

`PHASE1E2_PERSISTENCE_CONTROLLER = SOURCE PREFLIGHT VALIDATED / LOCAL-APPLIED /
PERSISTENCE DISABLED`

This checkpoint advances the final Phase 1 measurement-apparatus gate without
activating persistent runtime evidence.

`durable_memory_updated: true`

## Authority

Remote/source predecessor:

`4833361b045cdc7c7bd97c6fd297560518de8e8b`

Commissioned runtime remains:

`L:\Projects\fantasy_football\fantasy_season_v0_36_repack1`

Previously commissioned Phase 1E safety primitive:

`src/observability/sinks.py::RedactingJsonlSink`

Production persistence was disabled before this checkpoint and remains disabled
after it.

## Read-Only Design / Roadmap Reconciliation

The Phase 1 roadmap defines persistent local evidence as the remaining Phase 1
acceptance item. Phase 2 prospective Data/MC collection is concurrent; Phase 1E
does not authorize retrospective reconstruction of missing telemetry.

Accepted controller design:

1. local-only root `logs/observability/`, resolved from the runtime/source tree
   rather than process CWD;
2. production persistence only through `RedactingJsonlSink`;
3. source default disabled; source import alone cannot activate persistence;
4. explicit activation via `configure_shadow_persistence(...)`;
5. shared recorder integration beneath `ShadowRecorder` and
   `GuiShadowRecorder`, not duplicated across P/D/K/behavior boundaries;
6. rotation on UTC event-day change or 16 MiB active-segment size;
7. 256 MiB total storage ceiling;
8. no automatic retention deletion during the season;
9. storage ceiling stops new persistence and preserves existing evidence;
10. disk/redaction/path failure disables later writes for that controller
    instance and cannot alter wrapped production result/exception behavior.

Run/action identifiers are not used as filenames. Generated segment names are
Windows-safe.

## Diagnostic Package v1 Failure

Package:

`phase1e2_persistence_controller_source_preflight_20260928_v1`

The first diagnostic package failed before technical validation completed.

Failure 1:

- `git status --porcelain` output was passed through `.strip()`;
- the meaningful leading status-column space on the first record was removed;
- fixed-column slicing then transformed
  `src/observability/__init__.py` into
  `rc/observability/__init__.py`.

Classification:

`DIAGNOSTIC PATH-PARSING DEFECT / CANDIDATE SOURCE NOT INVALIDATED`

Failure 2:

- temporary-clone removal encountered the known Windows read-only Git-object
  cleanup defect.

No control-root or commissioned-runtime source was modified.

## Corrected Diagnostic Package v2

Package:

`phase1e2_persistence_controller_source_preflight_20260928_v2`

Archive SHA-256:

`4075aab868f8c22a581c9678bfbb9dea152955e2b9ec6baf65c7d942159f759e`

Corrections:

- changed paths parsed from `git status --porcelain=v1 -z`;
- no trimming of status columns;
- rename/copy states explicitly rejected;
- regression self-test covers a leading-space first record;
- temporary tree carries a package ownership sentinel;
- read-only permission repair is allowed only inside the verified owned temp
  tree;
- cleanup helper is self-tested before repository cloning.

Operator receipt:

- exact base commit: PASS;
- changed paths: `5/EXACT`;
- helper self-test: PASS;
- import context: PASS;
- `py_compile`: PASS;
- targeted pytest: **34 passed in 6.74s**;
- observability pytest: **152 passed in 5.12s**;
- full pytest: **531 passed in 48.21s**;
- `compileall src`: PASS;
- strict memory health: HEALTHY;
- `git diff --check`: PASS;
- `git diff --cached --check`: PASS;
- `logs/observability/` Git exclusion: PASS;
- persistence active: false;
- project modified: false;
- runtime modified: false;
- football/model/business logic changed: false;
- retention deletion enabled: false;
- temporary-clone cleanup: PASS.

Temporary candidate staged tree:

`05ffff982cc8633d2fa3447e228d5c23168cc7e9`

This tree identifies only the isolated five-path technical candidate before
durable-memory/roadmap files are added. It is not the later repository checkpoint
tree.

## Exact Validated Technical Target Identities

`src/observability/__init__.py`

- raw SHA-256:
  `0c7aed205635f65967c95c8fdc86a5bcff00ac8636ee3bb561f6654b972841be`
- Git blob:
  `cd6c25fcd584543e4cb7ea9fab00d72b19c00c96`

`src/observability/gui_shadow.py`

- raw SHA-256:
  `630c2c0b44a8c7c2c940f730fe80bc663f254d30b83ceb55b5b4ccb59b919e4b`
- Git blob:
  `3b15e3c2825e61b30538ab6f87e1101319f1c0b6`

`src/observability/persistence.py`

- raw SHA-256:
  `420a40df9a9732235a880cb58396075100f089a80fbdc536da8450d79303b4ce`
- Git blob:
  `02a2a11c1cd320d713c934fc1f6a90ac00772420`

`src/observability/shadow_pilot.py`

- raw SHA-256:
  `6d5359de73fc9d4ac1b52a4f7f23ba0f92acaec454aad0a13becd39c59f4c414`
- Git blob:
  `3a49420f2d7e2b3341cba777a2da9cbfcb823ee7`

`tests/test_observability_persistence_controller_v10a.py`

- raw SHA-256:
  `048008160cc512a62b9dd6b24d52d8f1f7387b18d3e156b1c91a95a46091ee63`
- Git blob:
  `23e6e2e6df172017602c61774d3f0b6209440daa`

## Local Checkpoint Boundary

The local-apply carrier installs exactly the validated five-path technical
candidate plus:

- `docs/memory/CURRENT.md`;
- `docs/memory/roadmap/STATUS.md`;
- `docs/ROADMAP.md`;
- this evidence record.

The control root is the checkpoint surface. The commissioned runtime is used
only as exact read-only predecessor authority when a technical source file is
absent from the intentionally partial control root.

Local apply validates exact target identities, static compilation, strict memory
health, rendered whitespace, unchanged Git index, unchanged commissioned runtime,
and unchanged local observability-log evidence. It stops before staging, commit,
push, runtime synchronization, or persistence activation.

## Scientific / Privacy Classification

The candidate changes observability infrastructure only.

It does not change:

- player/DST/kicker football formulas;
- `P ⊕ D ⊕ K`;
- Monte Carlo draws or recommendation authority;
- trade/manager-response formulas;
- prospective capture rules;
- v0.X calibration state.

Persistence remains **DISABLED**.

## Next Gate

After the local-apply receipt is verified:

`LOCAL-APPLIED -> declarative isolated staging -> guarded source publication ->
read-only remote verification -> separate runtime commissioning with persistence
OFF`

Persistent activation remains a later, separately authorized commissioning gate.
