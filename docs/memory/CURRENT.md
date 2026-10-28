# Current Project State

---
state_updated: 2026-10-28
authoritative_release: v0.36-repack1
internal_version: "0.36"
active_phase: week8_standalone_operator_and_action_certification
active_workstream: week8_native_evaluated_alternatives_retention_source_candidate
memory_refinement_step: none
nfl_week: 8
fantasy_stage: regular_season
maintenance_status: healthy
---

## Active Objective

**Deliver and commission the Windows 10/11 portable, GUI-driven recurring weekly decision procedure**, without ChatGPT making roster decisions. The application must produce one ranked, uncertainty-aware full-roster decision report for lineup, players, DST, kicker, IR, and trade families, separately certify legal/current actions, obtain explicit user approval, and preserve the no-automatic-ESPN-write boundary. Tuesday is primary; Wednesday/Saturday/pre-lock are follow-ups. Preserve the commissioned v0.36 physics and P/D/K separation. Acceptance contracts: `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md` and `architecture/WEEKLY_DECISION_COMPLETION.md`.

## Current Work Item

**Source-only evaluated-candidate retention and GUI presentation candidate; NOT runtime commissioned.** After the October 27 supervised Tuesday native nine-channel MC, the read-only receipt verified `COMPLETE / ACTION_REQUIRED`, operational health PASS, zero incomplete native channels. The GUI operator correctly remained `INCOMPLETE_COVERAGE`, with no ESPN transaction authority, because full action certification is uncommissioned. The native MC presented four lineup changes (start Mark Andrews and Jakobi Meyers; bench George Kittle and J.K. Dobbins), but live reconciliation blocked lock/kickoff confirmation and reported market/partner drift. Player acquisition preselected 80 players; 2 one-for-one, 4 multi-player and 2 specialist trade packages were evaluated; no actionable waiver/trade offers survived. The existing receipt retained actionable offers, not the rejected or borderline alternatives, so the GUI could not explain the HOLD classifications quantitatively. **Do not infer that 80 players received paired MC or that the full legal joint transaction state was certified.**

The corrected portable v2 passed strict-memory repair and Tuesday source trial, and its independent `Weekly decisions` GUI tab was operator-verified on the local machine. That portable panel is **not** yet a source-published Windows 10/11 portable release. Current candidate adds bounded presentation-only evaluated alternatives to future native receipts without changing ranking, physics, classifications, or ESPN authority; presents retained rows through the source GUI. The existing October 27 receipt cannot be retroactively enriched. Local package v1 stopped before writes because the control root lacks `src/gui/season_app.py`; v2 recovered exact GUI predecessor bytes and passed targeted tests and strict memory health, but its unconditional full pytest command failed collection with exit 2. The October 28 read-only inventory established that the control root has 39 source Python files versus 90 in the commissioned runtime; missing Python modules caused full-suite collection to abort. v2 rolled back and left no source backup. v3 was applied locally with targeted tests and strict memory health PASS. The first owned eight-path isolated stage passed exact file and schema-2 manifest checks but failed `git diff --cached --check`: the new test fixture had extra blank lines at EOF. This targeted correction removes only that formatting defect, refreshes the staged manifest and completes full QA in the existing clone before publication. No runtime or MC changes.

## Verified State

- **Remote/source predecessor:** `154a16422bd788914519a69901c40b0cca45a357` on `trottar/fantasy_football/main` as inspected October 28. Exact local control source must be verified before applying candidate. Local source is applied; this checkpoint validates its recovered isolated staging tree. Commit, push, runtime sync, and commissioning are separate.
- **Tuesday evidence:** protected supervised trial performed six-provider sync, a new immutable prospective capture, one native MC launch and completion, and read-only review. Valid receipt SHA-256 `26fdac83015bca71cfdc341919e0d395645fb16193b9d05a79fecb129f25c285`; no MC repeat is authorized. Preserve both original Tuesday frozen reference and subsequent prospective trial capture.
- **Local portable GUI:** `week8_portable_gui_weekly_decision_panel_20261027_v1` was locally applied and displayed successfully; source/control repository and original commissioned runtime were not modified by that local package. No transaction submission authority.
- **Source candidate:** evaluated alternative evidence is purely observational, bounded per category, sourced from actual native-evaluated rows and tagged with reported MC stage; it cannot become an actionable recommendation. Full native decision and action-certification gaps remain open. Until staging/publishing and explicit runtime synchronization, this is not the weekly production GUI.

## Calendar / Evidence Gates

Wednesday October 28 and Saturday October 31 are prospective follow-up windows; Thursday October 29 starts Week 8 NFL games. Honor actual individualized kickoff and unknown waiver claim cutoff. Never backfill missed decision-time captures, duplicate uncertain MC, issue stale action certificates, infer free-agent future availability or auto-write ESPN. Preserve already-captured Tuesday prospective evidence. Weather/time or date alone do not authorize calibration.

## Scientific / Architectural Boundaries

`N_fantasy ~ L × sigma × A × epsilon`; `P ⊕ D ⊕ K`; `ΔU = U(S + δS) − U(S)`; `MC -> Data -> closure -> diagnosis -> calibration`. v0.X remains a-priori; player, defense and kicker channels remain distinct internally. Behavioral acquisition probabilities do not alter football utility. Screens generate candidate frontiers, never action authority. Native HOLD is limited to its evaluated scope. Missing source or rules are BLOCKED, not assumed pass.

## Exact Next Action

**After the existing isolated staging passes full pytest, compileall, and Git/manifest validation:** separately publish the exact staged tree under remote/allowlist guards, then verify the remote read-only. If the full QA fails, preserve the prior validated local checkpoint, without publication. Then perform a separately guarded candidate runtime sync and portable Win10/11 packaging test; revalidate identity guards and run a *future prospective* weekly evaluation only when timing permits. Never rerun or rewrite Tuesday's frozen MC. Subsequently implement the approved §5A legal/complete-roster/joint-portfolio action certification, live drift recovery, real waiver processing evidence and GUI recurrence; keep `RECOMMEND_FOR_APPROVAL` and automatic scheduling blocked until explicit test/commissioning gates pass.

## Relevant References

- `architecture/WEEKLY_DECISION_OPERATOR_V2_SPEC.md`; `architecture/WEEKLY_DECISION_COMPLETION.md`; `architecture/WEEK8_WEEKLY_OPERATOR_V2_INTEGRATION_GATE.md`; `patches/PATCH_PROTOCOL.md`; `USER.md`
- `evidence/WEEK8_EVALUATED_ALTERNATIVES_RETENTION_2026-10-28.md`
- `../../src/weekly_decision_cycle.py`; `../../src/weekly_decision_alternatives.py`; `../../src/gui/season_app.py`; `../../src/gui/weekly_decision_view.py`; `../../tests/test_weekly_decision_alternatives.py`
