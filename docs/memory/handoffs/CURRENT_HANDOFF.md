# Current Handoff

`CURRENT.md` is the sole authoritative resumable state. This file records only exceptional transfer state and cannot override `CURRENT.md`.

## Transfer State

- Work continues on the **existing October 27 Windows 10/11 portable v2** at `L:\Projects\fantasy_football_portable_win10_11_20261027_v2\fantasy_football`, launched using `L:\Projects\fantasy_football_portable_win10_11_20261027_v2\Start_Fantasy_Football.cmd`. Do not rebuild it to hide a source, import, or preflight defect.
- The guard-pin source repair is now committed on GitHub `main` at inspected predecessor `722ead079dba9aa4251a0beef55738c9bb918450`; its **portable-runtime sync remains unverified** in the current recovery evidence. Never assume that GitHub publication updated the installed portable.
- The first Week 9 direct-open-slot source carrier rolled back on pytest collection error. The follow-up read-only diagnostic confirmed a missing `src.weekly_manager` import in the isolated test context; committed source does contain that module. An initial v2 successor was blocked before writing by an incorrect assumption that the sparse control root contained `src/weekly_manager.py`. The read-only layout probe confirmed two complete isolated stage trees with all five relevant exact source identities, plus missing control-root import dependencies. The corrected successor must use a stage-backed temporary complete tree to run targeted tests before and after any source-only apply, without writing to stages or portable runtime. Its successful local application is **not** staging, publication, runtime sync or operational commissioning.
- Protect prospective Week 9 captures, keep the portable and commissioned kernels unchanged during source-only apply, and do not run a live trial or repeat uncertain MC as a packaging test.

## Resume

Follow `../CURRENT.md` for the exact next action. Return concise success summary or full failure output. Source-only `.ffpkg` steps stop before staging, commit, push, portable sync, ESPN or live MC.

`durable_memory_updated: true`
