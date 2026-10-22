"""Read-only Week 8 B2b1: paired conditional partner + user trade response.

Freeze inputs before evaluation; no ESPN calls, trade submission or recommendation
certification. The audited native v0.36 Monte Carlo functions remain unchanged.
All after states assume *no* future free-agent fills; if illegal, fail closed.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

from action_predictive_b2 import (
    CONTRACT as B2A_CONTRACT, MAX_SCENARIOS, MAX_OPTIONS,
    _safe_option, canonical_sha256, paired_summary, probe_options,
    require, selection, verify_runtime, CertificationBlocked,
)

CONTRACT = "WEEK8_PARTNER_PAIRED_TRADE_DIAGNOSTIC_B2B1_V1"


def partner_drop_proof(snapshot: dict[str, Any], offer: dict[str, Any]) -> list[str]:
    """A *frozen* permitted drop is still not future ESPN action permission."""
    espn = snapshot.get("espn") or {}
    partners = [t for t in espn.get("teams") or []
                if type(t.get("team_id")) is int and t["team_id"] == offer["partner_team_id"]]
    require(len(partners) == 1, "PARTNER_TEAM_PROVENANCE_NOT_UNIQUE")
    roster = partners[0].get("roster") or []
    ids = [p.get("espn_id") for p in roster]
    require(len(ids) == len(set(ids)) and all(type(i) is int for i in ids),
            "PARTNER_ROSTER_IDENTITIES_INVALID")
    owned = {p["espn_id"]: p for p in roster}
    reasons = []
    outgoing = set(offer["receive_ids"])
    for pid in offer["modeled_partner_auto_drop_ids"]:
        if pid in outgoing:
            reasons.append("PARTNER_MODELED_DROP_ALREADY_OUTGOING")
        if pid not in owned:
            reasons.append("PARTNER_MODELED_DROP_NOT_FROZEN_OWNED")
        elif owned[pid].get("droppable") is not True or owned[pid].get("lineup_locked") is not False:
            reasons.append("PARTNER_MODELED_DROP_PERMISSION_OR_LOCK_UNPROVEN")
    return sorted(set(reasons))


def _native_joint(snapshot: dict[str, Any], league: dict[str, Any], model: dict[str, Any],
                  values_path: Path, offer: dict[str, Any], option: dict[str, Any],
                  user_team_id: int, scenarios: int, runtime: Path,
                  baselines: dict[int, tuple[Any, Any, Any, Any]] | None):
    """One native MC universe per manager, reused across all conditional options.

    Distinct managers have separate common-random-number spaces; their scenario
    indices are not a calibrated joint acceptance or cross-manager probability.
    """
    import numpy as np
    settings = (snapshot.get("espn") or {}).get("transaction_settings") or {}
    hours = settings.get("trade_review_hours")
    require(type(hours) is int and hours > 0,
            "TRADE_EFFECTIVE_WEEK_NOT_SOURCE_RESOLVED_FOR_ZERO_REVIEW")
    week = (snapshot.get("espn") or {}).get("week")
    require(type(week) is int and 1 <= week <= 17, "TRADE_WEEK_INVALID")
    effect_week = min(18, week + 1)
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from src import specialist_trade as st
    from src.market_manager import roster_is_legal
    from src.trade_timing import splice_effective_week
    teams = {int(t["team_id"]): t for t in snapshot["espn"]["teams"]}
    partner_id = int(offer["partner_team_id"])
    require(user_team_id != partner_id and user_team_id in teams and partner_id in teams,
            "FROZEN_TRADE_TEAMS_UNAVAILABLE")
    orig = {tid: list(teams[tid]["roster"]) for tid in (user_team_id, partner_id)}
    outgoing = {user_team_id: set(offer["give_ids"]), partner_id: set(offer["receive_ids"])}
    incoming = {user_team_id: set(offer["receive_ids"]), partner_id: set(offer["give_ids"])}
    dropped = {user_team_id: set(option["drop_ids"]),
               partner_id: set(offer["modeled_partner_auto_drop_ids"])}
    raw_after = {}
    for tid, other in ((user_team_id, partner_id), (partner_id, user_team_id)):
        rows = [copy.deepcopy(p) for p in orig[tid]
                if int(p["espn_id"]) not in (outgoing[tid] | dropped[tid])]
        rows += [copy.deepcopy(p) for p in orig[other]
                 if int(p["espn_id"]) in incoming[tid]]
        require(roster_is_legal(rows, league, target_size=len(orig[tid])),
                ("USER" if tid == user_team_id else "PARTNER") +
                "_NO_FUTURE_FILL_ROSTER_ILLEGAL")
        st._assert_supported_trade_specialist_state(rows,
            side="user" if tid == user_team_id else "partner")
        raw_after[tid] = st._normalize_incoming_assignments(
            orig[tid], rows, team_id=tid,
            incoming_ids=incoming[tid], outgoing_ids=outgoing[tid])
    final = st._snapshot_with_rosters(snapshot, raw_after)
    hybrid = st._hybrid_player_snapshot(snapshot, final, (user_team_id, partner_id))
    cache = dict(baselines or {})
    response = {}
    for tid in (user_team_id, partner_id):
        if tid not in cache:
            cache[tid] = st._baseline_state(snapshot, league, model, values_path, tid,
                scenarios, progress_label="B2b1 frozen baseline")
        base_ctx, base_u, base_w, base_opp = cache[tid]
        ctx, _, after_w, after_opp = st._composed_after_state(
            hybrid, final, league, model, values_path, tid, scenarios,
            progress_label="B2b1 no-future-fill alternative")
        delayed_w = splice_effective_week(np.asarray(base_w), np.asarray(after_w), effect_week)
        delayed_opp = splice_effective_week(np.asarray(base_opp), np.asarray(after_opp), effect_week)
        after_u = st._scenario_h2h_utility_against(delayed_w, delayed_opp, ctx)
        response[tid] = (np.asarray(base_u, dtype=float), np.asarray(after_u, dtype=float))
    return response, cache


def evaluate(snapshot: dict[str, Any], capture: dict[str, Any], receipt: dict[str, Any],
             league: dict[str, Any], model: dict[str, Any], values_path: Path, runtime: Path,
             offer_id: str, *, scenarios: int = 128, max_options: int = MAX_OPTIONS,
             kernel=None) -> dict[str, Any]:
    require(type(scenarios) is int and 16 <= scenarios <= MAX_SCENARIOS, "SCENARIO_BUDGET_INVALID")
    _, offer = selection(snapshot, capture, receipt, offer_id)
    original = tuple(canonical_sha256(x) for x in (snapshot, capture, receipt, league, model))
    chosen, remaining = probe_options(offer, max_options)
    blocked_partner = partner_drop_proof(snapshot, offer)
    user_team_id = int(receipt["team_id"])
    partner_team_id = int(offer["partner_team_id"])
    native = kernel if kernel is not None else _native_joint
    cached = None
    evaluated = {}
    rows = []
    for opt in chosen:
        can_run, local_reasons = _safe_option(offer, opt)
        reasons = local_reasons + blocked_partner
        row = {"drop_ids": list(opt["drop_ids"]),
               "native_selected": opt["native_selected_normalization"],
               "state": "BLOCKED", "blockers": sorted(set(reasons))}
        if can_run and not blocked_partner:
            try:
                responses, cached = native(snapshot, league, model, values_path, offer,
                    opt, user_team_id, scenarios, runtime, cached)
                require(isinstance(responses, dict) and set(responses) == {user_team_id, partner_team_id},
                        "BOTH_MANAGER_PAIRED_MC_REQUIRED")
                row["user"] = paired_summary(*responses[user_team_id])
                row["partner"] = paired_summary(*responses[partner_team_id])
                row["state"] = "CONDITIONAL_TWO_MANAGER_MC_NOT_CERTIFIED"
                evaluated[tuple(opt["drop_ids"])] = responses
            except (CertificationBlocked, ValueError, TypeError, KeyError, RuntimeError) as exc:
                row["blockers"].append(str(exc) if isinstance(exc, CertificationBlocked)
                                       else "NATIVE_MC_ERROR:" + type(exc).__name__)
        rows.append(row)
    # Conditional relative comparison is valid only within the same manager's
    # paired scenario universe, never by subtracting independent manager scores.
    reference = next((tuple(r["drop_ids"]) for r in rows
                      if r["native_selected"] and tuple(r["drop_ids"]) in evaluated), None)
    for row in rows:
        key = tuple(row["drop_ids"])
        if reference is not None and key in evaluated and key != reference:
            row["versus_native_drop_choice"] = {
                side: paired_summary(evaluated[reference][tid][1], evaluated[key][tid][1])
                for side, tid in (("user", user_team_id), ("partner", partner_team_id))}
    require(tuple(canonical_sha256(x) for x in (snapshot, capture, receipt, league, model)) == original,
            "FROZEN_INPUT_OR_CONFIG_MUTATED_DURING_TWO_MANAGER_MC")
    return {"contract": CONTRACT, "b2a_reference": B2A_CONTRACT,
            "offer_id": offer_id, "snapshot_sha256": original[0],
            "capture_sha256": original[1], "receipt_sha256": original[2],
            "scenarios_requested": scenarios, "conditional_no_future_fill": True,
            "structural_options_total": len(offer["structural_options"]),
            "structural_options_not_selected_for_bounded_probe": remaining,
            "options": rows, "two_manager_options_evaluated": len(evaluated),
            "native_drop_choice_comparison_reference": list(reference) if reference is not None else None,
            "unresolved": ["DISTINCT_MANAGER_SCENARIO_UNIVERSES_NOT_JOINT_ACCEPTANCE_PROBABILITY",
                           "PARTNER_ACCEPTANCE_AND_MANAGER_BEHAVIOR_NOT_CERTIFIED",
                           "FUTURE_FILL_AVAILABILITY_AND_WAIVER_QUEUE_NOT_CERTIFIED",
                           "ALTERNATIVE_TRADE_EFFECTIVE_TIMING_NOT_VERIFIED",
                           "MULTI_ACTION_PORTFOLIO_AND_INJURY_CONTINGENCIES_NOT_CERTIFIED",
                           "LIVE_ESPN_APP_LEGALITY_AND_POST_MC_DRIFT_NOT_CERTIFIED"] +
                          (["UNEVALUATED_DROP_OPTIONS"] if remaining else []),
            "state": "BLOCKED_B2B1_CONDITIONAL_TWO_MANAGER_MC_ONLY",
            "espn_action_authority": "NONE"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for arg in ("snapshot", "capture", "receipt", "league", "model", "values"):
        ap.add_argument("--" + arg, required=True, type=Path)
    ap.add_argument("--runtime", required=True, type=Path)
    ap.add_argument("--offer-id", required=True)
    ap.add_argument("--scenarios", type=int, default=128)
    ap.add_argument("--execute-native", action="store_true")
    ap.add_argument("--out", type=Path, help="Private local result, inside runtime/data")
    args = ap.parse_args(argv)
    print("WEEK8 B2B1 TWO MANAGER PAIRED TRADE DIAGNOSTIC", flush=True)
    try:
        docs = [json.loads(p.read_text(encoding="utf-8-sig"))
                for p in (args.snapshot, args.capture, args.receipt)]
        selection(*docs, args.offer_id)
        if not args.execute_native:
            print("MODE=CHECK_ONLY;NATIVE_MC_NOT_STARTED=TRUE;ESPN_ACTION_AUTHORITY=NONE")
            return 0
        runtime = args.runtime.resolve()
        verify_runtime(runtime)
        league = json.loads(args.league.read_text(encoding="utf-8-sig"))
        model = json.loads(args.model.read_text(encoding="utf-8-sig"))
        result = evaluate(*docs, league, model, args.values.resolve(), runtime,
                          args.offer_id, scenarios=args.scenarios)
        if args.out is not None:
            out = args.out.resolve()
            require(out.is_relative_to(runtime / "data") and not out.exists(),
                    "PRIVATE_OUTPUT_MUST_BE_NEW_RUNTIME_DATA_FILE")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("TWO_MANAGER_OPTIONS_EVALUATED=" + str(result["two_manager_options_evaluated"]) +
              ";CERTIFIED_ACTIONS=0;ESPN_WRITES=NONE")
        for row in result["options"]:
            print("B2B1_OPTION=" + json.dumps(row, sort_keys=True))
        print("STATE=BLOCKED_B2B1_CONDITIONAL_TWO_MANAGER_MC_ONLY;ACTION_AUTHORITY=NONE")
        return 0
    except (CertificationBlocked, OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print("B2B1_BLOCKED=" + (str(exc) if isinstance(exc, CertificationBlocked)
                              else type(exc).__name__) + ";ACTION_AUTHORITY=NONE")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
