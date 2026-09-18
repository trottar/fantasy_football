# v1.0A GUI Lifecycle Shadow-Pilot Build Failures

<!-- FANTASY_EVIDENCE_V10A_GUI_LIFECYCLE_SHADOW_BUILD_FAILURES_20260917:BEGIN -->
## Build / QA failure record

1. The first assistant-side v1 package-construction transformer used conflicting
   nested Python triple-quoted strings and raised `IndentationError` before it
   created the installer. No project or package output was modified.

2. A later assistant-side transformer intended to replace the installer
   `self_test()` and `main()` functions again embedded a triple-quoted fixture
   inside a generated Python literal and raised `SyntaxError` before the
   replacement executed. The already-created installer remained unchanged.

3. The first accumulated observability run passed 98 tests and failed one new
   structural assertion because the test expected the cosmetic literal
   `page_shadow = gui_shadow.open_page()`. The intended implementation opens into
   `shadow_page`, registers connect/disconnect/delete hooks, and only then
   assigns `page_shadow = shadow_page`.

4. The next accumulated run again passed 98 tests and failed one source-shape
   assertion that expected a direct `page_shadow.observe_background_task(...)`
   call. The implementation intentionally routes both task sites through the
   local fail-open `observe_task(...)` helper while preserving the original
   NiceGUI/asyncio task-creation primitives.

5. The first exact-ZIP accumulated-tree harness used a shortened one-line
   synthetic `SeasonGuiService(...)` constructor. The installer production
   source guard correctly rejected that fixture because the actual predecessor
   seam is multiline. No package logic ran past that guard. The harness fixture
   was restored to the exact predecessor formatting before exact-artifact QA was
   rerun.

6. The delivered v1 package passed machine-state preflight and both paired
   runtime probes, then failed the authoritative Windows full repository suite
   after 450 tests passed because two established GUI source-contract tests
   require the exact scheduling expressions
   `background_tasks.create(apply_mc_size(new_n))` and
   `asyncio.create_task(progress_pump())`. v1 had wrapped the awaitables at the
   scheduler call sites, preserving runtime intent but violating those frozen
   source-level scheduling contracts. The installer stopped before durable-memory
   rendering, commit, push, or local control/runtime synchronization. GitHub
   remained at `eb7fc236a61f50459397cf3e2f58cd1cdbb1091b`.

7. During v2 construction, the first all-in-one assistant-side transformer
   embedded a malformed multiline replacement literal and raised `SyntaxError`
   before writing any v2 installer changes. The copied package tree remained the
   unchanged v1 input and was discarded/recreated before the successful smaller
   transformations. No user project or repository state was involved.

8. The first v2 synthetic end-to-end apply passed staged probes and all 16
   GUI source-contract/lifecycle tests, then staged `compileall` exposed an
   indentation defect in the new coroutine-body transformer. The transformer
   matched the `progress_pump` signature four spaces into the line, so the
   generated inner coroutine landed at the same indentation as the outer
   function. This occurred assistant-side in a synthetic repository; no user
   project or GitHub state was involved. The signature was corrected to the
   exact nested indentation, transformed-source compilation was added to
   installer self-test, and full staged `compileall` was promoted into
   non-modifying preflight before probes/tests.

9. The next v2 synthetic end-to-end apply reached durable-memory rendering
   after staged compileall, both paired probes, and all 16 GUI contract/lifecycle
   tests passed, then the synthetic fixture failed because it omitted the
   `docs/memory/handoffs/` directory that exists in the real repository. The
   direct handoff write therefore raised `FileNotFoundError`. This was a
   synthetic QA fixture defect, not a package/source defect; the fixture was
   repaired to mirror the real durable-memory directory structure before the
   end-to-end apply was rerun.

10. The repaired v2 synthetic end-to-end apply then reached the temporary
    staging commit and stopped because the isolated container clone had no Git
    author/committer identity configured. The real Windows checkpoint workflow
    had already committed successfully in the predecessor slice, so this was a
    synthetic QA environment deficiency. Author/committer identity was supplied
    only to the synthetic QA process before rerunning the end-to-end path.

11. The first exact-artifact combined preflight+apply QA command passed exact
    ZIP extraction, staged compileall, both paired probes, and all 16 GUI
    contract/lifecycle tests, but the assistant container command wrapper timed
    out before the apply process returned a final status. No real repository was
    involved. The exact-artifact apply was therefore rerun separately in a
    persistent interactive QA process so completion could be observed rather
    than inferred.

Items 1-2 classification:
`FAILED DURING ARTIFACT CONSTRUCTION / BEFORE DELIVERY / NO PROJECT MODIFICATION`.

Items 3-5 classification:
`PRE-DELIVERY QA ASSERTION/FIXTURE DEFECT / NO PROJECT MODIFICATION`.

Item 6 classification:
`FULL-SUITE REGRESSION / FAILED BEFORE COMMIT-PUSH-LOCAL-SYNC / NO PROJECT MODIFICATION`.

Items 7-8 classification:
`FAILED DURING ARTIFACT CONSTRUCTION/PRE-DELIVERY QA / NO PROJECT MODIFICATION`.

Items 9-10 classification:
`PRE-DELIVERY QA FIXTURE/ENVIRONMENT DEFECT / NO PROJECT MODIFICATION`.

Item 11 classification:
`PRE-DELIVERY QA HARNESS TIMEOUT / NO REAL PROJECT MODIFICATION`.

Corrective action: construct function bodies as standalone syntax-checked files,
splice only after each fragment compiles, preserve established scheduling
expressions exactly, move observation inside the scheduled coroutine bodies,
run full staged compileall plus the frozen GUI source-contract tests during
non-modifying preflight, and reuse the same exact predecessor fixture for
source-guard QA at every artifact layer.
<!-- FANTASY_EVIDENCE_V10A_GUI_LIFECYCLE_SHADOW_BUILD_FAILURES_20260917:END -->
