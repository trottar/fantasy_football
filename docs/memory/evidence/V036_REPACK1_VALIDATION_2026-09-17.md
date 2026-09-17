# v0.36-repack1 Validation Evidence

<!-- FANTASY_EVIDENCE_V036_REPACK1_20260917:BEGIN -->
## Validation summary

Timestamp: `2026-09-17T11:01:47.459865-04:00`

Artifact label: `v0.36-repack1` (packaging revision only; internal `VERSION` remains `0.36`).

Original invalid v0.36 ZIP SHA-256:
`598c518ad30e2f1c65c452bafca111808f5456eeb818bf04c43994ceb269987c`

Repaired release ZIP:
`fantasy_season_v0_36_repack1.zip`

Repaired release SHA-256:
`01dc3ddce16d828ba91f97058e15ce4102592418a2648049135c24d146826380`

Packaging delta relative to exact v0.36:
- changed: `0`
- removed: `0`
- added: exactly the four previously identified mock-calibration fixtures.

Source import:
- imported the 26 previously measured/validated v0.36 changed-or-added files;
- no newly designed football/model/GUI logic was introduced in this checkpoint;
- the v0.36 source delta itself includes its already-validated `config/model.json` and source changes;
- the packaging repair adds fixtures only.

Validation:
- fixture-targeted pytest: PASS;
- candidate compileall: PASS;
- candidate full pytest: PASS;
- automated GUI gate: PASS (`17` GUI-focused test files);
- GUI lifecycle invariants: PASS;
- GUI safe-module import smoke: PASS;
- `gui` and `draft-gui` CLI/parser smoke: PASS;
- exact repaired ZIP compileall/full pytest/GUI gate: PASS;
- installed-tree byte manifest matches the validated exact ZIP: PASS.

Live browser GUI commissioning is still `PENDING`; v1.0A implementation remains blocked until that live check passes.
<!-- FANTASY_EVIDENCE_V036_REPACK1_20260917:END -->
