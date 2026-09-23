# Phase 1C Player Shadow Source Validation — 2026-09-22

## Authority

Repository/source predecessor:

- commit: `8b8181830590e4ca0ec8d8456d52f5240c078eab`;
- tree: `203120a630382384f80cd09958112be50f2802fc`.

Validated player-only production boundaries:

- CLI: `src/transaction_manager.py::evaluate_actions` at
  `subsystem.player.evaluate_actions`;
- GUI: `src/gui/season_service.py::SeasonGuiService.evaluate_single_add_drop` at
  `subsystem.player.evaluate_single_add_drop`.

The complete-roster evaluator `evaluate_roster_predictive` remains explicitly
uninstrumented because it contains mixed P/D/K response machinery.

## Diagnostic Provenance

Diagnostic package:
`phase1c-player-shadow-preflight-v1-20260922`

Diagnostic archive SHA-256:
`3d88d32b5cf60aacfe84ca837ff7be829af562a8e91538930e128fba58c83844`

The diagnostic ran against exact remote `main` `8b8181830590e4ca0ec8d8456d52f5240c078eab` in an isolated
temporary clone and removed that clone after validation. It changed neither the
control-root checkpoint surface nor the commissioned runtime.

## Technical Scope

Exactly five technical paths:

1. `src/transaction_manager.py`
2. `src/gui/season_service.py`
3. `src/observability/player_shadow.py`
4. `tests/test_observability_player_shadow_v10a.py`
5. `tools/probe_observability_player_shadow_v10a.py`

The candidate adds only bounded in-memory observability wrappers at the two
accepted player perturbation surfaces. It does not add or change football,
waiver, trade, lineup, scoring, or recommendation logic. It does not invent a
shared player-production wrapper.

## Validation

Operator-executed preflight results:

- targeted pytest: **6 passed in 1.67 s**;
- full pytest: **509 passed in 53.49 s**;
- strict memory health: **HEALTHY**;
- CLI paired gate: baseline `5250 ns`, observed `78500 ns`, incremental
  `73250 ns`, PASS;
- GUI paired gate: baseline `5200 ns`, observed `74900 ns`, incremental
  `69700 ns`, PASS;
- privacy: PASS;
- persistent sink: disabled;
- complete-roster evaluator: uninstrumented;
- diagnostic modification state: temporary clone removed, control root unchanged,
  runtime unchanged.

Both baseline timings are below the established `1,000,000 ns` relative floor,
so the relative percentage is non-authoritative. Both incremental timings are
well below the authoritative `1,000,000 ns` absolute overhead limit.

## Exact Locally Applied Source Identity

The local-apply package reconstructed the candidate from the same exact remote
predecessor and deterministic transform/payload identity used by the validated
preflight. SHA-256 identities:

- `src/transaction_manager.py`: `1da1f007bcc50d1f65dbcdd8fbb50431485487e436bc09047755791f4220de45`
- `src/gui/season_service.py`: `d393cbebff7e9b05ede9c46f58d77ffb7ded2fc64e51c2012a7ead17a869f4e7`
- `src/observability/player_shadow.py`: `75b19efda45a1f35192fa9d514e06e6912f6e5a20ff0be72d1254e23c5d288ef`
- `tests/test_observability_player_shadow_v10a.py`: `f99545526a04a926ab24e68a855f361239851332b5306d665ce63e5b7d322f83`
- `tools/probe_observability_player_shadow_v10a.py`: `449ce94a20509cc105bd76f02edecef40ab071827f0cd11057e36045561a4bf3`

## Scientific / Privacy Classification

The player observer is restricted to QB/RB/WR/TE perturbation boundaries and
preserves `P ⊕ D ⊕ K`. DST and K remain separately observed at their commissioned
specialist boundaries. Cross-channel coupling remains only at complete-roster
utility/state boundaries.

Arguments, returned values, authenticated/private payloads, and exception
messages are not retained by the observer. Persistent evidence remains disabled.
No observed 2026 game outcome was used to tune a v0.X football model.

## Result

`PHASE1C_PLAYER_CANDIDATE_FULLY_SOURCE_VALIDATED`

Package `phase1c-player-shadow-local-apply-v1-20260922` applies these exact validated bytes to the local
control-root checkpoint surface together with this durable evidence. This is
**not** repository publication and **not** runtime commissioning.

Repository staging/publication and commissioned-runtime synchronization remain
separate later gates.
