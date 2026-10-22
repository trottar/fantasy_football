# Weekly Decision Operations Procedure — v2 Implementation Contract

**Contract status:** approved for incremental engineering work; NOT runtime commissioned or ESPN action authority. Source gates remain explicit.

**Project:** `L:\Projects\fantasy_football\`
**Baseline:** commissioned `fantasy_season_v0_36_repack1` (`VERSION=0.36`)
**Status:** IMPLEMENTATION CONTRACT; SPECIFICATION ONLY — not installed, source-published, tested against live ESPN, commissioned, or authorized for ESPN writes.
**Evidence trigger:** Week 7, October 20–21, 2026: multiple narrow probes exposed missing end-to-end orchestration, and the Wednesday nine-channel MC labeled six offers actionable at its frozen state. Live ESPN state subsequently changed. A focused audit found four trade proposals structurally intact, but one illustrative 1×2 package would automatically drop a second quarterback and leave only a questionable QB. Those risks were discovered in chat rather than certified by the procedure. This v2 draft makes downstream roster risk, alternative counterfactuals, execution timing, and actionable classification explicit prerequisites.

## 1. Operating objective and accountability

One local, repository-owned operator entrypoint must produce a complete, state-bound weekly *decision report*, not a sequence of ad hoc ChatGPT-directed diagnostics. The operator can run it on the prescribed cadence and inspect one actionable queue. ChatGPT remains a development, calibration, and exceptional-failure resource, **not** the runtime state machine. **The controller owns football decision triage and post-transaction risk assessment; the user owns transaction approval and genuinely preference-sensitive close calls.**

**Proposed interface, NOT CURRENTLY IMPLEMENTED:**

```powershell
cd L:\Projects\fantasy_football
python .\fantasy.py operate-week --week 7 --mode review
```

The eventual command may be implemented by a separate `tools/operations/weekly_operator.py` instead of changing `fantasy.py`; confirm exact existing CLI and deployed source before selecting the integration point. No new public entrypoint is to be claimed live until local tests, staging, publication, and commissioning have passed.

The default mode is **read-only ESPN** (two or more bounded GETs as needed), with private local immutable evidence writes only. All lineup changes, add/drop, waiver claims, and trade submissions require a separate, explicit human transaction approval; an MC `PASS / ACTION` is **not** ESPN execution authority.

## 2. Scientific and permission invariants

- Preserve `N_fantasy ~ L × sigma × A × epsilon`, stochastic uncertainty, common random numbers in paired comparisons, `P ⊕ D ⊕ K`, and complete-roster utility `ΔU = U(S + δS) − U(S)`.
- All player waivers are searched across **QB/RB/WR/TE × every legal player drop**, never only user-supplied targets or "three-QB" examples. DST and K use their own commissioned specialist policies. Trade search includes legal player-only 1×1/1×2/2×1/2×2 and DST/K-inclusive families with partner, manager response, and legal roster fills/drops.
- Include lineup, availability, lock constraints, IR/open-slot/injury-replacement, provenance, and operational-health channels. Do not hard-code an IR failure or success based on historical B2b state: use the current commissioned receipt. Wednesday 2026-10-21 returned `PASS / HOLD:IR_REPLACEMENT` at its frozen state; any newly missing required transition must still report `INCOMPLETE_COVERAGE`.
- `screen != authority`; screening may prune only as the existing commissioned model permits. Behavior/acquisition probability is separate from intrinsic football value. An individual waiver candidate's `p_acquire` is not a joint probability that an ordered queue succeeds.
- Never backfill prospective captures, change immutable observations, or use outcomes to tune v0.X. Capture must occur before outcomes and consequential evaluations.
- Secrets, ESPN cookies, raw authenticated responses, user/league identifiers, runtime caches and diagnostic logs remain local. Git contains only sanitized public-safe source/tests/docs and manifests.
- Control-root apply, staged clone, committed remote, runtime synced, and workflow commissioned are distinct statuses; no direct GitHub connector writes.

## 3. Cadence and calendar guard

1. **Monday:** Prior-week closure intake; identify league week, verified future locks and all configured waiver/trade effective dates. Preserve frozen evidence.
2. **Tuesday pre-waiver:** Mandatory pre-claim candidate review for **all** acquisitions, not merely the kicker. Run all required independent player, K, DST, and trade evaluations if capture is valid and sufficient action lead remains. Build contingencies for mandatory lineup holes. Do not wait until Wednesday if a claim deadline occurs first.
3. **Wednesday protected primary:** Fresh six-provider snapshot and immutable prospective capture, then full nine-channel MC, live legality and human decision report, early enough to act before any relevant Thursday-or-earlier lock.
4. **Thursday/Friday:** Cheap live drift/lock checks; rerun only channels invalidated by a material event and with sufficient time. Never force a new long MC just because time passed or a player is mentioned.
5. **Saturday protected second:** Full fresh snapshot/capture/nine-channel MC and live recheck before player-specific locks; repeat actions only if there is new legal evidence and a meaningful opportunity.
6. **Sunday:** Optional fast ESPN check. No mandatory morning 40–50-minute MC. All deadlines derived from verified player/game, waiver and trade data, not a hard-coded Sunday clock.

The existing 80-minute planning budget (MC 40 + live verification 15 + approval/action 15 + safety 10) is a **minimum protected lead**, not an observed runtime guarantee. Track actual duration and choose conservative bounds. If a claim deadline is sooner than MC completion + implementation budget, **do not launch a run expecting to authorize that claim**; surface a time-critical blocker and the latest valid scoped evidence for a human decision.

## 4. State machine and deterministic event handling

Each weekly invocation has a private local manifest keyed by `(season, week, approved source/runtime/config identities, snapshot SHA256, capture SHA256, event epoch)`:

```text
DISCOVER_CALENDAR
   -> FETCH_AND_FREEZE  [six providers, time/health, immutable snapshot]
   -> PROSPECTIVE_CAPTURE [bound immutable capture; PRE vs LOCKED vs UNKNOWN]
   -> EVALUATE_CHANNELS [independent idempotent checkpoint receipts]
   -> LIVE_RECONCILE [exact roster, market, status, transactions, locks, rules]
        |-- unchanged -> REPORT_ACTION_QUEUE [scoped recommendations, deadlines]
        |-- benign/display-only -> REPORT with proved nonimpacting fields
        |-- material and recovery budget available -> NEW_EPOCH_CAPTURE -> rerun affected channels
        `-- material and too late/retry cap -> BLOCK_AFFECTED_ACTIONS + REPORT_ALL_UNAFFECTED
   -> AWAIT_HUMAN_APPROVAL -> VERIFY_ESPn_ACTION_SCREEN / effective date
   -> POST_ACTION_ESPN_VERIFY -> NEW_EVENT_EPOCH; schedule follow-up review
```

**Do not** mutate an existing prospective snapshot or receipt to make a recheck pass. A materially changed state means a new immutable *decision-time* epoch. For stable derived evaluation in a new epoch, prove all input dependencies identical before reusing an earlier channel receipt. A "changed injury" or "851 market changes" count alone is insufficient; compare precise identities and fields and classify their dependencies.

### Drift dependency model (initial conservative map)

| Observed change | Affected operation(s) | Default action |
| --- | --- | --- |
| Owned player injury/availability, NFL role, start/bench/IR, any lock | Lineup, player waivers, trades, IR; maybe complete-state specialist policies | Invalidate dependent receipts; new capture before action |
| Available-player acquisition state FREEAGENT ↔ WAIVERS or membership | Relevant P/D/K acquisition channel and trade fallback fills; claim legality | Re-evaluate affected channel; never call WAIVERS guaranteed |
| Any league transaction, ownership change, transaction setting | Roster/market state; all potentially coupled complete-roster results | Reconcile exact transaction and state; invalidate impacted channels |
| K/DST projection or opponent change | K/DST specialist response and combined complete-roster comparisons | Re-evaluate affected channel(s) |
| Clearly display-only text/stat change with proven unused field | None *if* a tested field-dependency contract proves no effect | Record benign status; do not fake capture authority |
| Unknown or unparseable state, missing ESPN rules, unknown kickoff | All possibly affected action authority | Fail closed, with specific reason and next operator step |

Because complete-roster utility couples player and specialist state at the root, "different position" is **not automatically** enough to call a change nonimpacting. Field dependencies must be source-derived and tested against actual model input access, including manager behavior and external league field effects.

### Restart and finite retry contract

- Every expensive phase writes a local **phase receipt** with exact input identities, output checksum, phase/version, duration, gate result, and a pointer to the private result file.
- On restart, skip a phase only when its source/config/capture/input fingerprints and outputs match exactly. Never rerun an already successful expensive phase merely because a later gate failed.
- On material drift, first display the raw normalized changed assets/statuses and the **specific invalidated channel list**. Only then choose a new capture/evaluation pass.
- **At most one automatic material-drift recovery epoch per invocation** initially; on a second material change, stop re-trying, print a full decision-state report, and schedule the next protected/checkpoint run. Do not silently loop or spend the entire waiver window fetching.
- Network or ESPN failure yields `BLOCKED_SOURCE` with retry-after recommendations, never a stale action certificate. Integrity/auth failure yields `BLOCKED_HEALTH` and stops.
- A missing unsupported channel remains `INCOMPLETE_COVERAGE` with a named capability issue; never convert it to HOLD. A partial diagnostic report is allowed, but must be labeled scoped.

## 5. Required decision report

Produce both sanitized `weekly_action_report.txt` for console and a private structured JSON receipt. Minimum contents:

1. **State**: week, source/runtime, snapshot/capture identity/timing, trusted kickoff and waiver/claim/trade deadlines, health.
2. **9-channel matrix** with statuses, missing coverage and exact supporting receipt IDs. No roster-wide COMPLETE until all required gates pass.
3. **Mandatory repairs first**: unfilled active roster or starting position, proven bye, legal IR transitions, acquisition certainty and deadline. Show fallback if first waiver fails; joint claim queue legal semantics must be modeled or explicitly unknown.
4. **Whole-player waiver frontier**: legal add/drop candidates, WAIVERS vs FREEAGENT, conditional predictive ΔU, uncertainty, behavioral `p_acquire`, current-week impact, identity of dropped player and their field response. Include negative/no-edge candidate counts.
5. **All roster concentration diagnostics** (including three QBs): each owned player's projected starter use, availability uncertainty, replacement/bench option value, bye coverage, drop legality, trade packages and why retained. Concentration is a prompt to evaluate, not a forced drop.
6. **Trade families** with explicit give/receive, partner, forecast deltas on both rosters, manager behavior, post-trade auto-fill/drop, review delay and earliest effective week. Flag trades that cannot affect the needed Week 7 slot before its lock.
7. **Certified ESPN action queue** ordered by verified effective deadline and mandatory feasibility, then paired complete-roster benefit. Only offers passing the end-to-end trade certificate in §5A may appear as `RECOMMEND_FOR_APPROVAL`; other states include `REJECT`, `CLOSE_CALL`, `BLOCKED`, `PENDING_WAIVER`, `PENDING_TRADE`, and `CONFIRMED`. A native `ACTIONABLE_OFFER` is just a candidate, not a certified executable recommendation.
8. **Human-facing exact next step**: a complete precomputed recommendation or a clearly scoped blocker. Never require an unscheduled ChatGPT discussion to uncover a known roster consequence; never recommend pressing Submit until ESPN action-screen legality and the required approval have been confirmed.

### Minimum console finish marker

```text
WEEKLY_OPERATOR_RESULT=SCOPED_READY | COMPLETE_READY | BLOCKED_SOURCE | BLOCKED_HEALTH | CAPTURE_REQUIRED | INCOMPLETE_COVERAGE
SNAPSHOT_CAPTURE_BINDING=PASS | BLOCKED
CHANNELS=LINEUP,PLAYER_WAIVER,DST_WAIVER,K_WAIVER,IR,TRADE_1X1,TRADE_MULTI,TRADE_SPECIALIST,PROVENANCE
AFFECTED_CHANNEL_RESTARTS=<integer, with exact evidence>
OWNED_POSITION_CONCENTRATIONS=<relevant records with three-QB inventory>
MANDATORY_GAPS=<reported>
NEXT_PROVEN_ACTION=<exact ESPN step or NONE>
ESPN_ACTION_AUTHORITY=NONE
LOCAL_WRITE_SCOPE=PRIVATE_RUNTIME_EVIDENCE_ONLY
```

**These are prospective output-schema examples, not current receipt values.**

## 5A. Mandatory end-to-end action certification (v2 addition)

**Owner:** the permanent weekly controller, NOT ChatGPT or the end user. An optimizer's `PASS / ACTION` or an evaluator's `ACTIONABLE_OFFER` is a **candidate-discovery result only**. A separate **Action Certification Gate** must classify every surfaced transaction. Do not change the commissioned physics or manager-behavior kernels merely to get a cleaner classification. The gate compares fully evaluated, legally representable *strategy states* and may request narrow native paired-MC reevaluation where necessary.

### A. Resolve the full transaction, not just give/receive names

For every shortlisted trade, waiver, free-agent move, lineup assignment, and IR move:

1. Bind the decision to an immutable, pre-outcome snapshot/capture and the exact initiating roster, partner roster (for trades), configuration, lock state, acquisition state, and transaction settings.
2. Enumerate **all legal consequences**, including roster capacity, minimum/maximum position counts, lock and IR eligibility, every compulsory drop, empty roster slot, open lineup position, legal replacement, automatic-model fill, and the player's release into the *league* state.
3. Distinguish a **modeled optimal drop/fill** from an **ESPN-proven executable operation**. Do not claim the app will automatically drop a named player; verify whether ESPN requires a manual drop at acceptance, rejection or review, and what it will do if the roster becomes illegal.
4. Where there are multiple legal drop choices, evaluate the complete roster under the **actual feasible choices**, not only the optimizer's initial preferred normalization. Expose whether that chosen drop is dominated by another legal alternative. No hidden compulsory roster loss in the output.
5. For every guaranteed `FREEAGENT` fill, verify its current state and its **required future availability time**. A player available when the trade is proposed is not guaranteed to be available after a 48-hour review. Model a legal contingency without that fill, or block any gain requiring unsupported guaranteed future availability. All `WAIVERS` fills require their own uncertain acquisition state; never promote them to guaranteed.
6. Model trade review, effective week, starter lock, trade deadline, lineup/roster lock policy, commissioner processing uncertainty, and partner acceptance **separately**. With the commissioned positive-review rule, earliest modeled Week 7 trade effect is Week 8; this is not an ESPN execution guarantee.
7. Recheck the offer's exact participant ownership, partner-side prerequisites, pending transactions, live lineup legality, and app-specific submission/processing semantics immediately before human approval and after execution. Fail closed on unsupported or contradictory details; never execute ESPN writes automatically under this contract.

### B. Automatic roster resilience and concentration checks

The decision gate must test a complete post-action weekly state `S_w = (P_w, D_w, K_w, M_w, I_w)` across the affected horizon, **including the effects of losses after the trade becomes effective**:

- Starting slot coverage for every affected week; confirmed bye, known locks, IR and roster minimums; future flex/TE/QB depth rather than roster count alone.
- Injury/participation scenarios and workload uncertainty for all remaining starters, especially any only remaining viable QB; substitutes available *at decision time* versus uncertain future acquisitions.
- Correlated adversity (multiple questionable players, substitute unavailable, delayed trade) to the extent supported by the commissioned predictive uncertainty model; do not invent arbitrary injury rates.
- Bench insurance, worst-case/left-tail complete-roster utility, head-to-head and season utility, and changes in league-state field response when dropped/traded players become available to opponents.
- Exact alternative strategies: no transaction; keep Lamar; each supported legal auto-drop alternative; a comparable legal trade package; and, if relevant, legal short-term waiver coverage and IR-related transitions. Cross-channel coupling is allowed **only at the complete-roster state boundary**.
- Every evaluated path must show conditional predictive distribution, paired uncertainty interval, prospective evidence identity, effect date, manager-acquisition behavior separately, and the consequences if its required acquisition/trade step fails.

**Week 7 counterexample — compulsory fixture:** For `Lamar Jackson → CeeDee Lamb + Ravens D/ST`, the model-selected over-capacity drop was `Jacoby Brissett`, leaving `Baker Mayfield` as the only remaining QB, with Baker `QUESTIONABLE` at the captured decision time. The gate must assess whether that particular resulting roster is robust; explicitly compare alternative legal drops and remaining QB acquisition/insurance. The naive `+2.99 season-lineup PPG` and `+0.0399 complete-roster ΔU` are inputs to, not substitutes for, this certification. If the subsequent QB contingency is unsupported, classify `BLOCKED` rather than `RECOMMEND`.

### C. Deterministic recommendation and escalation policy

At the end of **all** mandatory checks, issue one of:

| Final decision state | Required proof and system behavior |
| --- | --- |
| `RECOMMEND_FOR_APPROVAL` | All modeled and live-operational feasibility gates pass; no unsupported critical dependence; paired response beats the proper no-action and best feasible alternative under the commissioned decision rule. Output exact transaction, compulsory drops/fills, effective week, contingencies, and bounded uncertainty. User may approve/decline without ChatGPT. |
| `REJECT` | A required legal/roster or football utility gate fails, or another evaluated legal option dominates. Say precisely why; do not present as a recommended trade. |
| `CLOSE_CALL` | Multiple supported alternatives are statistically/economically too close under existing model thresholds or differ on a genuine user preference. Display the trade-off in one short comparison and ask **one** user decision. |
| `BLOCKED` | Exact app rules, requisite prospective evidence, state/provenance, or necessary conditional response is unknown or stale. Name the missing fact and an automated read-only remedy when possible. Do not ask the user to debug data or ask ChatGPT to guess. |

Do **not** invent ad hoc football gain thresholds or tune `v0.X` to observed 2026 scores. Reuse commissioned decision tolerances and paired-MC uncertainty; where no reliable criterion exists, report the gap and require an explicitly authorized future production policy change. Partner acceptance estimates remain uncalibrated and cannot by themselves qualify a trade as `RECOMMEND_FOR_APPROVAL`.

A recommendation certificate must include, at minimum:

```text
ACTION_ID=<stable private local ID>
CANDIDATE_FOOTBALL_CLASSIFICATION=<native result>
FINAL_DECISION=RECOMMEND_FOR_APPROVAL | REJECT | CLOSE_CALL | BLOCKED
FROZEN_EVIDENCE=<snapshot/capture/MC receipt identities>
GIVE=<exact assets>;RECEIVE=<exact assets>
ESPN_LEGALITY=<VERIFIED | UNVERIFIED>;TRADE_EFFECTIVE_WEEK=<grounded week>
MANDATORY_DROPS=<exact options and validated choice>;MANDATORY_FILLS=<state and timing>
POSITION_COVERAGE=<PASS | FAIL | UNCERTAIN>;INJURY_CONTINGENCIES=<supported scenario summary>
NO_ACTION_AND_BEST_ALTERNATIVE=<paired ΔU, uncertainty, legal assumptions>
EXTERNAL_DEPENDENCIES=<partner acceptance, app processing, waivers, future FAs>
CURRENT_ESPN_RECHECK=<PASS | MATERIAL_CHANGE | UNKNOWN>
HUMAN_PROMPT=<approve/decline exact action | choose between close legal alternatives | none>
```

### D. Joint strategy and transaction lifecycle, not isolated single actions

- Build one **ordered portfolio** of nonconflicting actions using the same complete-roster state; avoid offering simultaneous mutually exclusive trades, duplicate drops, or a waiver claim that invalidates a trade. Rank conditional alternatives and account for failed offers/claims.
- Before final approval, recalculate current legality and prerequisites once at the authoritative ESPN/app state. After each user-approved manual transaction, verify the ESPN recorded state, update the event epoch, and invalidate only affected downstream strategies.
- Use action-specific due dates for claim submissions, trade offer expiry, partner acceptance, review processing, earliest effective week, and lineup assignments. Never assume a pending trade is executed or a post-trade replacement remains available.
- Unknown ESPN mechanics remain `BLOCKED`, with a short operator check in the same local command; never translate uncertainty into unverified transaction authority.

### E. Required certification tests (promotion blockers)

These must pass **before** the controller can represent itself as a normal weekly production procedure:

1. **Lamar / Lamb / Ravens fixture:** primary native trade classifies `ACTIONABLE_OFFER`, but certification must expose the implicit Brissett release, Baker-only QB future, QUESTIONABLE injury state, and evaluate legal alternate drops / replacement scenarios; absent supportive evidence => `BLOCKED`, not `RECOMMEND`.
2. **Uncertain future free-agent fill:** 49ers D/ST is free now but acquired by another manager before trade review ends; test cannot retain the gain from an impossible future guarantee. Recompute scenario or block; never replace with a free win.
3. **Timing:** 48-hour positive trade-review means earliest modeled effective week is Week 8 for the Week 7 offer. Changed roster lock/offer processing rules require fresh evidence; never silently treat it as Week 7 gain.
4. **Mutually exclusive trade offers and waivers:** choose a coherent portfolio and reveal dependencies; reject conflicting claims against the same asset.
5. **Compare all legal over-capacity drop variants:** model's preferred candidate drop is not necessarily the ESPN user's executable choice. Show delta distributions for viable drop alternatives and a completed legal lineup.
6. **Dominance and close-call:** machine-select a clearly supported superior strategy; surface one preference question only when criteria genuinely cannot distinguish alternatives. No ChatGPT dependency in either ordinary case.
7. **Mid-run partner transaction / market injury drift:** only affected candidates invalidate; no stale approval, no unconditional full-MC rerun; bounded fresh epoch and preserved valid phase receipts.
8. **No transactions without approval:** all `RECOMMEND_FOR_APPROVAL` outcomes stop at approval with no ESPN POST, verify eventual recorded result independently, and never overstate certainty of acceptance.

**Product-acceptance test:** In a future Week 8 run, a user can read **one complete report** and either approve a fully evaluated action, reject it, or choose between a clearly presented close pair—without needing ChatGPT to ask what happens to the second QB or to discover a hidden automatic release.

## 6. Implementation plan and acceptance gates

**Slice A — repository-owned controller, read-only recovery, and action-certification scaffolding (first delivery):**
- Reuse existing `fantasy.py` subcommands, `src/weekly_decision_cycle.py`, `tools/operations/deadline_budget.py`, and source-bound `guarded_weekly_cycle.py`. Do not replace commissioned football physics.
- Build a single orchestrator handling exact pre-state, fresh capture, nine-channel evaluation, normalized live ESPN diff, checkpointed phases, bounded one-epoch recovery, and complete report. It must never turn `ACTIONABLE_OFFER` into an approval-ready action without §5A certification; unimplemented subgates explicitly yield `BLOCKED`.
- Enforce no ESPN transactions. Stage only source/tests/documentation/memory and public-safe synthetic fixtures. Update `CURRENT.md` in same checkpoint.

**Slice B — fully implemented action certification, operator workflow, and claim/trade semantics:**
- Add read-only claim queue/priority introspection only to the extent that ESPN supplies reliable current facts; do not invent processing cutoff or joint claim success.
- Implement §5A portfolio/counterfactual/drop/fill/depth/contingency gate with commissioned MC; add action queue presentation, exact app-side confirmation workflow, post-action reconciliation, per-family effective-week constraints; no autonomous ESPN writes without separate explicit user authorization and commissioned guard.

**Slice C — scheduled operation (optional after successful commissioning):**
- A Windows Task Scheduler job may trigger the read-only wrapper on Tuesday before verified league-specific waiver cutoff, Wednesday primary and Saturday secondary, plus optional cheap checks. Scheduler must never wake up and execute ESPN writes. Alerts can point to local sanitized report.

**Validation matrix for Slice A (minimum):**
- Synthetic roster with three QBs: verify all three legal drops are considered and both player-only and specialist-inclusive trade scopes are searched; then run the eight mandatory §5A certification fixtures before any approval-ready recommendation is possible.
- 851 market WAIVERS rollover: invalidate relevant decisions and restart once; never coerce WAIVERS into FREEAGENT.
- Player injury `OUT → QUESTIONABLE`; trade history changed mid-run; market status changed between capture and MC; further mid-recovery drift: correct finite stop and actionable partial report.
- Kill process after player MC and resume: exact receipt reuse, no repeated six-provider pull or MC for unaffected phases; wrong hash rejects reuse.
- Known/unknown individual locks, near waiver deadline, unknown exact claim cutoff, 48-hour trade review: no backdated action, no automatic effective-week assumption.
- Missing IR B2b, incomplete mandatory kicker WAIVERS, incomplete lineup: overall stays INCOMPLETE_COVERAGE.
- Secrets/ESPN private IDs absent from console and staged files; private evidence confined locally.
- Source tests, full `pytest`, `compileall`, `git diff --check`, package extract/retest, schema-2 manifest, isolated staging, guarded publication, and live read-only commissioning receipt. Distinguish `PACKAGE-VALIDATED`, `LOCAL-APPLIED`, `STAGED`, `PUSHED/REMOTE-VERIFIED`, and `COMMISSIONED`.

## 7. October 21 state and Week 8 implementation boundary

**Latest operator evidence, Wednesday 2026-10-21:** The fresh Week 7 six-provider snapshot (`20261021T152438Z`) and immutable prospective capture (`20261021T152510Z`) passed; native nine-channel MC receipt `weekly_decision_receipt_20261021T161455Z.json` returned `COMPLETE / ACTION_REQUIRED` at its frozen state. Butker was acquired and verified active at the starting K slot; Bass was released. A post-MC ESPN audit found new transactions and market changes; a focused partner audit found four previously generated proposals without direct trade-participant or assumed-free-agent-fill drift, but none has new current action authority. **No trade or other ESPN action was submitted by the diagnostic system.**

The Week 7 case `Lamar Jackson → CeeDee Lamb + Ravens D/ST` highlighted why native positive utility cannot be treated as a fully certified trade: simulated post-trade normalization drops a second quarterback, which could leave one questionable QB. A chat-based manual discovery of that issue is **a failed procedure acceptance criterion**, irrespective of whether the trade eventually proves beneficial.

**Week 7 only:** Preserve the Wednesday full MC receipt as frozen evidence. Finish any required decision-time, app-side and injury checks with narrowly scoped ad hoc work; never rerun unaffected full MC phases, fabricate current trade authorization, or let implementation work consume the Thursday/Saturday capture windows. Trade review is configured at 48 hours and modeled conservatively as Week 8 effective; actual ESPN processing remains separately unverified.

**Starting Week 8 (Monday October 26) development target:** validate and commission the source-bound weekly controller, add the §5A certification state machine and eight acceptance fixtures, and demonstrate the one-command report without ChatGPT intervention. The permanent procedure is **not currently installed or commissioned**. Repository changes require exact control-root read-only audit, deterministic `.ffpkg` local apply, targeted/full tests, isolated staged review with manifest, separate authorized guarded publication, remote verification and explicit runtime commissioning. Never claim readiness before those gates pass.

**Out of scope for v2 specification:** changing intrinsic v0.36 football physics, using observed 2026 outcomes to tune v0.X, automatically sending ESPN transactions, and assuming another manager accepts a trade.
