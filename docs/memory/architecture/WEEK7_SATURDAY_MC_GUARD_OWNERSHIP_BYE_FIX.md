# Week 7 Saturday — MC guard ownership and verified-bye source correction

**Candidate:** `week7_mc_guard_owned_player_verified_bye_20261024_v3`.
**Predecessor:** remote `ab3db6b46c285d737210b31c41af87da08ef7715`, tree `16c0764b7fd8b583d6fbd90340ef2226d6adcd98`.
**Status:** v1 rolled back after a legacy fixture lacked `week` (1 failed, 55 passed); v2 passed 57 targeted tests but rolled back when strict memory health rejected a merged `CURRENT.md` heading; v3 corrects the generated heading structure and enforces the exact heading contract before any project write. No corrected package has yet been locally applied, staged, published, commissioned, or MC-launched.

## One narrow, directly observed defect

The exact Saturday Week 7 capture `a1ba36bd6b2008a2ea432c116aed1b8f56d0b356d381de8fde927ddafd41424a` was prospectively frozen against six-provider snapshot `f7ba8ac8ba8511a9f26dc8e579a36ecc3a227a6850be0df64aaeade62ec759e7`. The previously accepted MC preflight source used `side='US'` to identify owned records within `league_player_predictions`; the published capture schema instead writes `side='LEAGUE'` and `fantasy_team_id` for *all* rostered QB/RB/WR/TE players. A real read-only diagnostic saw 14 owned players, zero recognized owned players, two correctly recognized owned specialists and an incorrect `native_guard_lock_status=PASS`. No native MC or ESPN transaction ran.

Of the 14 owned player records, 13 have a future kickoff and one has no kickoff. An independent read-only follow-up verified the missing kickoff against **all three** sources: NFL 2026 official bye table, configured league bye week, and exact frozen nflverse schedule absence. There are zero unproven owned missing-kickoff records. One specialist already played and one remains future. Unowned missing kicks are not owned-lock authority.

## Source correction scope

Change *only* the control-root `tools/operations/guarded_weekly_cycle.py` lock-scope check. Real league player ownership uses `fantasy_team_id` rather than `side='US'`; specialists continue to use `owner_team_id`. Real `side='LEAGUE'` player rows lacking a numeric owner field block. An owned missing kickoff remains blocked unless (a) the exact capture season/week is 2026/that week, (b) the official published 2026 bye map lists that NFL team in the week, (c) the configured bye map agrees, and (d) the immutable snapshot team-week schedule has no game. The official table is extracted *read-only* from the published, exact source-identity-checked calendar module, not fetched online or fabricated. No live source is contacted by this change.

Preserve existing snapshot/capture integrity, commissioned source/dependency identity, protected deadline budget, recent commissioned identity and strict memory-health receipts, duplicate MC no-repeat marker, no auto-MC, no ESPN transaction writes and `P ⊕ D ⊕ K` physics. This fix cannot create missing health receipts, extend the two-hour capture freshness gate, recreate the capture, or authorize MC.

## v1 failure and v2 correction

The first local apply failed targeted pytest because a pre-existing compact pure-helper test omits `week`. Installer rollback restored all four predecessor paths, so v2 retains the exact same source predecessor and does not layer on an uncertain partial patch. The v2 fix checks capture `week` whenever the production caller supplies the immutable `snapshot`; only direct isolated helper tests with no `snapshot` may omit `week`, and those calls cannot authorize MC. A targeted regression explicitly checks both paths. No captured-state field is invented.

## Acceptance and deferred boundary

Add targeted synthetic tests for actual `LEAGUE`/`fantasy_team_id` schema, 14-player/two-specialist count, the confirmed owned bye, failure for unknown non-bye kicks and missing/inconsistent calendar, explicit team identity, remaining future locks, and no change to specialist semantics. Preserve existing native guard/controller tests. Exact local apply, targeted tests, compileall, strict memory health, isolated full pytest, schema-2 staged manifest, separate publication and read-only remote verification are independent checkpoints. No synthetic result may be presented as live MC commissioning or fresh receipt verification.

The Saturday 2026-10-24 prospective capture occurred at ~15:51:38 UTC; M1a's two-hour MC launch gate ends ~17:51:38 UTC (13:51:38 EDT). If a correct guard and genuinely fresh health receipts are not validated before expiry, the captured predictions remain valid prospective Data/MC closure evidence, but new native MC for that epoch must be **deferred**, never backdated or repeated. Exact waiver/trade cutoff certification and the whole-roster M2 decision matrix remain separate unfinished work.

`durable_memory_updated: true`

## v2 rendering failure and v3 pre-write regression gate

The strict memory-health checker requires both `## Calendar / Evidence Gates` and `## Scientific / Architectural Boundaries` as independent sections in `CURRENT.md`. The v2 candidate combined them into one `## Calendar / Scientific Boundaries` heading; the installer restored predecessor bytes upon rejection. Offline installer tests had replaced the real validation function with a stub, so they failed to exercise the exact heading contract. The v3 package checks the actual rendered payload against the seven exact canonical headings, each once and in order, before any files are written; post-write strict memory health remains mandatory.
