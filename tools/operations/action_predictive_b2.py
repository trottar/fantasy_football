"""Week 8 B2a: opt-in read-only native paired-MC alternative-drop diagnostic.

Only frozen snapshot/capture/receipt inputs are accepted. No trade, ESPN access,
manager acceptance, or action permission is inferred from a paired utility result.
A partner no-future-fill state must be league-legal or the option is blocked.
No modification of the commissioned model or its stochastic kernels.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

from action_frontier import build_frontier, CertificationBlocked, canonical_sha256

CONTRACT = "WEEK8_NATIVE_PAIRED_TRADE_DIAGNOSTIC_B2A_V1"
MAX_OPTIONS = 3
MAX_SCENARIOS = 512
EXPECTED_RUNTIME = "fantasy_season_v0_36_repack1"
EXPECTED_SOURCE_BLOBS = {
    "src/specialist_trade.py": "79bc906337748025857e504e9a3fc739fa8284e4",
    "src/transaction_manager.py": "4f800454408851d179e35c5dd462fb8f5ecb675c",
    "src/market_manager.py": "3036bac8baad2c70e5f019e365c6796ca85a4447",
    "src/trade_timing.py": "b462bd4c3a622c4ee00b12a4543e2b8bbc801e84",
    "src/specialist_policy_v032.py": "44b80c3f4600f05c9ffa0bee1f0855f74aa7bf44",
    "src/season_utility.py": "7c9f5b6ec497c9ba5fe228458911ce1f25b9ab03",
}


def require(value: bool, reason: str) -> None:
    if not value:
        raise CertificationBlocked(reason)


def git_blob(raw: bytes) -> str:
    normalized = raw.removeprefix(b"\xef\xbb\xbf").replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha1(b"blob " + str(len(normalized)).encode() + b"\x00" + normalized).hexdigest()


def verify_runtime(runtime: Path) -> None:
    require(runtime.name.casefold() == EXPECTED_RUNTIME.casefold(), "UNEXPECTED_COMMISSIONED_RUNTIME_ROOT")
    version = runtime / "VERSION"
    require(version.is_file() and version.read_text(encoding="utf-8-sig").strip() == "0.36",
            "COMMISSIONED_RUNTIME_VERSION_MISMATCH")
    for name, expected in EXPECTED_SOURCE_BLOBS.items():
        file = runtime / name
        require(file.is_file() and git_blob(file.read_bytes()) == expected,
                "NATIVE_MC_SOURCE_IDENTITY_MISMATCH:" + name)


def selection(snapshot: dict[str, Any], capture: dict[str, Any], receipt: dict[str, Any],
              offer_id: str, *, max_options: int = MAX_OPTIONS) -> tuple[dict[str, Any], dict[str, Any]]:
    require(1 <= max_options <= MAX_OPTIONS, "INVALID_OPTION_BUDGET")
    frontier = build_frontier(snapshot, capture, receipt)  # immutable causal contract
    matches = [row for row in frontier["offers"] if row["offer_id"] == offer_id]
    require(len(matches) == 1, "OFFER_ID_NOT_UNIQUE_OR_MISSING")
    offer = matches[0]
    require(not offer["structural_options_truncated"], "UNCERTIFIED_TRUNCATED_DROP_FRONTIER")
    require(not any(x.startswith("NATIVE_NORMALIZATION_COUNT_INCONSISTENT") for x in offer["blocking_evidence"]),
            "NATIVE_NORMALIZATION_INCONSISTENT")
    return frontier, offer


def probe_options(offer: dict[str, Any], limit: int = MAX_OPTIONS) -> tuple[list[dict[str, Any]], int]:
    """Bound MC expense transparently; this is NOT a full-action frontier ranking."""
    require(1 <= limit <= MAX_OPTIONS, "INVALID_OPTION_BUDGET")
    rows = list(offer["structural_options"])
    # Native plus options with stronger QB depth first; this is only a diagnostic
    # prioritization, never a utility screen that can authorize a transaction.
    rows.sort(key=lambda r:(not r["native_selected_normalization"],
                            -(r["post_trade_static_state"]["channels"]["P"]["QB"]),
                            len(r["post_trade_static_state"]["unresolved_qb_availability"]),
                            tuple(r["drop_ids"])))
    return rows[:limit], max(0,len(rows)-limit)


def _safe_option(offer: dict[str, Any], row: dict[str, Any]) -> tuple[bool, list[str]]:
    errors = []
    # The B1 native option is included even if ESPN booleans are unknown; NEVER
    # run it as a conditionally legal alternative without affirmative evidence.
    if "FROZEN_ESPN_DROPPABLE_NOT_TRUE" in row["feasibility_evidence"]:
        errors.append("FROZEN_DROP_PERMISSION_UNPROVEN")
    if "FROZEN_LOCK_EVIDENCE_NOT_EXPLICITLY_UNLOCKED" in row["feasibility_evidence"]:
        errors.append("FROZEN_DROP_LOCK_UNPROVEN")
    if "ROSTER_COUNT_MISMATCH_OR_FUTURE_FILL_NEEDED" in row["feasibility_evidence"]:
        errors.append("FUTURE_USER_FILL_REQUIRED_NO_GUARANTEE")
    if not row["post_trade_owned_ids_without_future_fills"]:
        errors.append("EMPTY_AFTER_ROSTER")
    if offer["required_user_fills_by_count"]:
        errors.append("FUTURE_USER_FILL_ASSUMPTION")
    return not errors, errors


def paired_summary(baseline: Any, alternative: Any) -> dict[str, float | int]:
    import numpy as np
    a = np.asarray(baseline, dtype=float)
    b = np.asarray(alternative, dtype=float)
    require(a.ndim == 1 and a.shape == b.shape and a.size >= 16,
            "PAIRED_MC_ARRAY_SHAPE_OR_SAMPLE_COUNT_INVALID")
    require(bool(np.isfinite(a).all()) and bool(np.isfinite(b).all()),
            "NONFINITE_PAIRED_MC_RESPONSE")
    d = b - a
    return {"mc_scenarios": int(len(d)), "paired_delta_mean": float(np.mean(d)),
            "paired_delta_sd": float(np.std(d, ddof=1)),
            "paired_delta_p10": float(np.quantile(d, .1)),
            "paired_delta_p50": float(np.quantile(d, .5)),
            "paired_delta_p90": float(np.quantile(d, .9)),
            "paired_p_better": float(np.mean(d > 0)),
            "paired_p_worse": float(np.mean(d < 0))}


def _native_arrays(snapshot: dict[str, Any], league: dict[str, Any], model: dict[str, Any],
                   values_path: Path, offer: dict[str, Any], option: dict[str, Any],
                   user_team_id: int, scenarios: int, runtime: Path,
                   baseline: tuple[Any, Any, Any, Any] | None = None) -> tuple[Any, Any, tuple[Any, Any, Any, Any]]:
    import numpy as np
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from src import specialist_trade as st
    from src.market_manager import roster_is_legal
    from src.trade_timing import splice_effective_week, season_ppg_from_weekly

    espn = snapshot.get("espn", snapshot)
    teamrows = {int(t["team_id"]): t for t in espn["teams"]}
    partner_id = int(offer["partner_team_id"])
    require(user_team_id in teamrows and partner_id in teamrows and partner_id != user_team_id,
            "MISSING_OR_INVALID_FROZEN_TRADE_TEAMS")
    orig_user = list(teamrows[user_team_id]["roster"])
    orig_partner = list(teamrows[partner_id]["roster"])
    user_ids = set(int(v) for v in offer["give_ids"])
    receive_ids = set(int(v) for v in offer["receive_ids"])
    drop_ids = set(int(v) for v in option["drop_ids"])
    partner_drops = set(int(v) for v in offer["modeled_partner_auto_drop_ids"])
    us_after_raw = [copy.deepcopy(p) for p in orig_user if int(p["espn_id"]) not in (user_ids | drop_ids)]
    us_after_raw += [copy.deepcopy(p) for p in orig_partner if int(p["espn_id"]) in receive_ids]
    pa_after_raw = [copy.deepcopy(p) for p in orig_partner if int(p["espn_id"]) not in (receive_ids | partner_drops)]
    pa_after_raw += [copy.deepcopy(p) for p in orig_user if int(p["espn_id"]) in user_ids]
    # NO unverified future free-agent fill is silently appended to either roster.
    require(roster_is_legal(us_after_raw, league, target_size=len(orig_user)),
            "USER_NO_FUTURE_FILL_STATE_NOT_LEAGUE_LEGAL")
    require(roster_is_legal(pa_after_raw, league, target_size=len(orig_partner)),
            "PARTNER_NO_FUTURE_FILL_STATE_NOT_LEAGUE_LEGAL")
    st._assert_supported_trade_specialist_state(us_after_raw, side="user")
    st._assert_supported_trade_specialist_state(pa_after_raw, side="partner")
    us_final = st._normalize_incoming_assignments(orig_user, us_after_raw, team_id=user_team_id,
                                                 incoming_ids=receive_ids, outgoing_ids=user_ids)
    pa_final = st._normalize_incoming_assignments(orig_partner, pa_after_raw, team_id=partner_id,
                                                 incoming_ids=user_ids, outgoing_ids=receive_ids)
    final = st._snapshot_with_rosters(snapshot, {user_team_id: us_final, partner_id: pa_final})
    hybrid = st._hybrid_player_snapshot(snapshot, final, (user_team_id, partner_id))
    if baseline is None:
        baseline = st._baseline_state(snapshot, league, model, values_path,
                                      user_team_id, scenarios, progress_label="B2a frozen baseline")
    base_ctx, base_utility, base_weekly, base_opp = baseline
    ctx, _, after_weekly, after_opp = st._composed_after_state(
        hybrid, final, league, model, values_path, user_team_id, scenarios,
        progress_label="B2a no-future-fill alternative")
    review_hours = ((snapshot.get("espn") or {}).get("transaction_settings") or {}).get("trade_review_hours")
    require(type(review_hours) is int and review_hours > 0,
            "TRADE_EFFECTIVE_WEEK_NOT_SOURCE_RESOLVED_FOR_ZERO_REVIEW")
    effect_week = min(18, int(espn["week"]) + 1)
    delayed_w = splice_effective_week(np.asarray(base_weekly), np.asarray(after_weekly), effect_week)
    delayed_opp = splice_effective_week(np.asarray(base_opp), np.asarray(after_opp), effect_week)
    after_utility = st._scenario_h2h_utility_against(delayed_w, delayed_opp, ctx)
    return np.asarray(base_utility, dtype=float), np.asarray(after_utility, dtype=float), baseline


def evaluate(snapshot: dict[str, Any], capture: dict[str, Any], receipt: dict[str, Any],
             league: dict[str, Any], model: dict[str, Any], values_path: Path, runtime: Path,
             offer_id: str, *, scenarios: int = 128, max_options: int = MAX_OPTIONS,
             kernel=None) -> dict[str, Any]:
    require(type(scenarios) is int and 16 <= scenarios <= MAX_SCENARIOS, "SCENARIO_BUDGET_INVALID")
    frontier, offer = selection(snapshot, capture, receipt, offer_id, max_options=max_options)
    original_ids = (canonical_sha256(snapshot), canonical_sha256(capture), canonical_sha256(receipt))
    before_config = (canonical_sha256(league), canonical_sha256(model))
    chosen, not_evaluated = probe_options(offer, max_options)
    result_rows = []
    prior = None
    # Injected kernel is for self-contained test fixtures only; normal CLI uses
    # native st._baseline_state + st._composed_after_state. No cheap screen.
    native = kernel or _native_arrays
    for option in chosen:
        safe, violations = _safe_option(offer, option)
        item = {"drop_ids": list(option["drop_ids"]), "native_selected": option["native_selected_normalization"],
                "comparison_state": "BLOCKED", "blockers": list(violations)}
        if safe:
            try:
                base, after, prior = native(snapshot, league, model, values_path, offer, option,
                                             int(receipt["team_id"]), scenarios, runtime, prior)
                item["paired_complete_roster_utility"] = paired_summary(base, after)
                item["comparison_state"] = "NATIVE_MC_EVALUATED_NOT_TRANSACTION_CERTIFIED"
            except (CertificationBlocked, ValueError, TypeError, KeyError, RuntimeError) as exc:
                item["blockers"].append(str(exc) if isinstance(exc, CertificationBlocked) else "NATIVE_MC_ERROR:" + type(exc).__name__)
        result_rows.append(item)
    require((canonical_sha256(snapshot), canonical_sha256(capture), canonical_sha256(receipt)) == original_ids and
            (canonical_sha256(league), canonical_sha256(model)) == before_config,
            "FROZEN_INPUT_OR_CONFIG_MUTATED_DURING_MC")
    return {"contract": CONTRACT, "offer_id": offer_id, "source_checkpoint": "ad5df6d73e434443c1c7061e6d0b51e43de795ca",
            "snapshot_sha256": original_ids[0], "capture_sha256": original_ids[1], "receipt_sha256": original_ids[2],
            "scenarios_requested": scenarios, "conditional_no_future_fill": True,
            "structural_options_total": len(offer["structural_options"]),
            "structural_options_not_selected_for_bounded_probe": not_evaluated,
            "options": result_rows, "options_evaluated": sum(x["comparison_state"].startswith("NATIVE_MC_") for x in result_rows),
            "unresolved": ["PARTNER_PAIRED_UTILITY_AND_MANAGER_BEHAVIOR_NOT_EVALUATED",
                           "LIVE_ESPN_AND_ACTUAL_TRADE_LEGALITY_UNVERIFIED", "FUTURE_FILL_ACQUISITION_NOT_GUARANTEED",
                           "MULTI_ACTION_PORTFOLIO_AND_INJURY_CONTINGENCIES_NOT_CERTIFIED"] +
                           (["UNEVALUATED_ALTERNATIVE_DROP_OPTIONS"] if not_evaluated else []),
            "state": "BLOCKED_B2A_PARTIAL_NATIVE_MC_DIAGNOSTIC", "espn_action_authority": "NONE"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for arg in ("snapshot", "capture", "receipt", "league", "model", "values"):
        ap.add_argument("--" + arg, required=True, type=Path)
    ap.add_argument("--offer-id", required=True)
    ap.add_argument("--runtime", required=True, type=Path)
    ap.add_argument("--scenarios", type=int, default=128)
    ap.add_argument("--out", type=Path, help="private local report path; never commit")
    ap.add_argument("--execute-native", action="store_true", help="opt in to bounded native MC")
    args = ap.parse_args(argv)
    print("WEEK8 SLICE B2A PAIRED TRADE DIAGNOSTIC", flush=True)
    try:
        paths = [args.snapshot, args.capture, args.receipt]
        docs = [json.loads(p.read_text(encoding="utf-8-sig")) for p in paths]
        frontier, offer = selection(*docs, args.offer_id)
        print("FROZEN_PROVENANCE=PASS;SELECTED_OFFER=" + offer["offer_id"] + ";OPTIONS=" + str(len(offer["structural_options"])),flush=True)
        if not args.execute_native:
            print("MODE=CHECK_ONLY;NATIVE_MC_NOT_STARTED=TRUE;ESPN_ACTION_AUTHORITY=NONE", flush=True)
            return 0
        runtime = args.runtime.resolve()
        verify_runtime(runtime)
        league = json.loads(args.league.read_text(encoding="utf-8-sig"))
        model = json.loads(args.model.read_text(encoding="utf-8-sig"))
        result = evaluate(*docs, league, model, args.values.resolve(), runtime,
                          args.offer_id, scenarios=args.scenarios)
        if args.out:
            out = args.out.resolve()
            require(out.is_relative_to(runtime / "data") and not out.exists(), "PRIVATE_OUTPUT_MUST_BE_NEW_RUNTIME_DATA_FILE")
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        print("B2A_OPTIONS_EVALUATED=" + str(result["options_evaluated"]) + ";CERTIFIED_ACTIONS=0",flush=True)
        for row in result["options"]:
            print("B2A_OPTION=" + json.dumps(row,sort_keys=True),flush=True)
        print("STATE=BLOCKED_B2A_PARTIAL_NATIVE_MC_DIAGNOSTIC;ESPN_WRITES=NONE;ACTION_AUTHORITY=NONE",flush=True)
        return 0
    except (CertificationBlocked, OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print("B2A_BLOCKED=" + (str(exc) if isinstance(exc, CertificationBlocked) else type(exc).__name__) + ";ESPN_ACTION_AUTHORITY=NONE", flush=True)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
