# Week 8 evaluated-alternatives retention and weekly GUI source candidate — 2026-10-28

Source predecessor: `154a16422bd788914519a69901c40b0cca45a357`. Source candidate only; future native receipt schema additive presentation evidence. `durable_memory_updated: true`.

## Direct evidence and narrow hypothesis

The October 27 operator-completed native receipt SHA-256 `26fdac83015bca71cfdc341919e0d395645fb16193b9d05a79fecb129f25c285` returned `COMPLETE / ACTION_REQUIRED` and nine valid native channels. Acquisition preselection counted 80 player assets, but its weekly channel receipt retained only `ACTIONABLE_EDGE` candidates. Native trade search reported 2 one-for-one, 4 multi-player and 2 specialist-inclusive evaluated packages, but retained only `ACTIONABLE_OFFER` offers. Tuesday's GUI correctly displayed no waiver/trade proposals because the native actionable lists were empty, not because the analyses never ran. It could not show rejected/possible alternatives because those rows were not persisted in the weekly receipt.

## Narrow structural change

`src/weekly_decision_alternatives.py` projects an upper-bounded, display-only subset of rows **already returned** by player and trade searches: classification, expected delta/offer value, uncertainty and behavior probabilities where available, original MC stage, sample count and futility-stop information. The add/drop report distinguishes 80 preselected candidate assets from screened combinations and actual paired MC evaluated action rows; these quantities are not interchangeable. `src/weekly_decision_cycle.py` stores the projection only as channel `evidence.evaluated_alternatives`, without changing `action`, `status`, the overall decision gate, search, Monte Carlo samples, or random streams. It does not promote borderline or negative assets to actionable. `src/gui/weekly_decision_view.py` reads and displays that evidence when present; prior receipts show an explicit historical not-retained notice. `src/gui/season_app.py` adds the view tab in the source tree. The bye display accepts either a missing or explicit-null frozen schedule-week entry only when the official, league and owned-player state corroborate a bye. This changes presentation, not native lock authority.

## Boundaries and acceptance

No data provider calls, MC rerun, new ESPN writes, calibration, threshold changes, scheduler, autonomous transactions or runtime commissioning. The historical Tuesday receipt cannot be enriched retrospectively. No action is certified merely because the diagnostic evidence is present. Existing v0.36 runtime identity hashes prevent silent in-place model replacement; source publication, guarded runtime sync and separate Win10/11 portable tests are future gates. §5A legal post-action comparison, manager response, uncertain future fills, joint strategies and live app-side approval remain separate, uncommissioned work. `screen != authority`; `P ⊕ D ⊕ K` preserved.

## Validation required

Targeted pure-projection and GUI tests; exact source-blob predecessor guard and normalized anchor checks; source compileall; full repository pytest; strict durable memory health; artifact extraction SHA validation and controlled failure; later isolated Git index/manifest, guarded publication, and read-only remote verification. Record only checks actually performed. Do not claim runtime commissioning from source tests.

## Local control-root predecessor recovery (2026-10-28)

The first carrier `week8_evaluated_alternatives_source_gui_20261028_v1` stopped with `PREDECESSOR_FILE_MISSING:src/gui/season_app.py` at a read-only predecessor gate (`exit 3`, no source/Git/ESPN/MC writes). Exact `src/weekly_decision_cycle.py` passed its preceding identity gate. The control-root `src/gui/season_app.py` cannot be assumed present just because the Git checkpoint tracks it and the commissioned runtime contains it. V2 rehydrates that **public source file in the control root only**, exclusively when the installed v0.36 runtime's GUI source or local Git blob matches the committed exact SHA-1 `4bf46e20feca615dd65db998dde5a52edd0b0cd0`. A mismatch blocks before writes. The installed runtime is never modified. Tests cover rehydration, wrong-byte fail-close, idempotence, and rollback to a missing worktree source on failed validation. No prospective data, native MC or action authority changes.

## October 28 sparse-root full-pytest collection diagnosis (v3 gate correction)

The first source carrier was correctly blocked before writes for a missing control-root
`src/gui/season_app.py`. The v2 successor recovered the GUI from an exact
committed-blob identity and reached targeted tests and strict memory health,
then stopped at unconditional `pytest -q` with collection exit 2; rollback
left `src/gui/season_app.py` and all new source paths absent and removed its backup.
A separate read-only `.ffpkg` probe recorded 39 control-root source Python files,
61 control-root test Python files, 90 commissioned-runtime source Python files,
and 16 named missing import modules across GUI, market and utility tests.
The underlying problem is incomplete full-suite collection authority in the
control root, **not** an observed native football-model test regression.

The v3 installer validates named missing modules against the read-only
commissioned source tree, runs targeted new tests and strict memory health in
the control root, and reports `FULL_PYTEST=DEFERRED_SPARSE_CONTROL_ROOT`.
If the modules are present, it runs full pytest normally. If missing modules
are not demonstrably present in the runtime, it blocks. **Full pytest, compileall,
manifest/index checks and exact source validation in the complete isolated
staging clone are mandatory before commit/push or runtime synchronization.**
No original runtime bytes, ESPN credentials, frozen prospective evidence,
transaction authorization, football physics, or MC behavior are changed.

`durable_memory_updated: true`

## October 28 staged-index whitespace recovery

The successful v3 control-root apply left seven reviewed paths. The first isolated stage
was owned, at exact remote predecessor `154a16422bd788914519a69901c40b0cca45a357`,
with exactly eight staged paths, seven reviewed files, and schema-2 index manifest
validation PASS (221 entries). Unstaged tracked changes: none. The only measured
failing gate was `git diff --cached --check`. Direct inspection of the exact v3
carrier's `repo_test.py` proved three ending newline bytes (two blank EOF lines);
Git reproduced `new blank line at EOF`. A guarded correction requires that exact
staged error and byte-for-byte v3 source/index identities before touching the
control-root and stage copies of the test. It preserves the validated football
source, GUI, and model semantics, reindexes the one corrected test, regenerates
the memory manifest, reruns strict memory, full-suite pytest, compileall, and
Git representation/whitespace checks on the existing complete stage. This
is not a fresh prospective capture, MC run, runtime sync, commit, or push.
