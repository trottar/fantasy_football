"""Bounded, opt-in mixed IR two-add paired-MC *shadow* evaluation.

This is not transaction certification. It compares complete-roster, current-week
head-to-head scenario arrays under a single common-random-number context. A
current IR move cannot imply any future return date or capacity credit.
"""
from __future__ import annotations

from typing import Any, Mapping
import numpy as np

from .transaction_manager import PLAYER_POSITIONS, evaluate_roster_predictive
from .specialist_policy_v032 import (
    _build_context, _compose_state, _paired_stats,
    _static_team_weekly, simulate_specialist_market_policy,
)


class UnsupportedJointState(ValueError):
    """A joint action lacks a validated current-week state representation."""


def _finite_int(value: Any) -> int | None:
    try:
        if isinstance(value, bool):
            return None
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def joint_probability_bounds(p_first: float, p_second: float) -> dict[str, float | str]:
    """Sharp Frechet bounds, not an invented independent-claims estimate."""
    a, b = float(p_first), float(p_second)
    if not (np.isfinite(a) and np.isfinite(b) and 0 <= a <= 1 and 0 <= b <= 1):
        raise UnsupportedJointState("INVALID_ACQUISITION_PROBABILITY")
    lo, hi = max(0.0, a + b - 1.0), min(a, b)
    return {"p_both_lower": lo, "p_both_upper": hi,
            "coupling": "UNIDENTIFIED_UNLESS_BOUNDS_COLLAPSE",
            "independence_assumed": False}


def _checked_win_vector(values: Any, label: str, n: int | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or len(arr) < 8 or not np.all(np.isfinite(arr)):
        raise UnsupportedJointState("INVALID_PAIRED_VECTOR:" + label)
    if n is not None and len(arr) != n:
        raise UnsupportedJointState("MC_SCENARIO_ALIGNMENT_MISMATCH:" + label)
    if np.any(arr < 0) or np.any(arr > 1):
        raise UnsupportedJointState("INVALID_H2H_RESPONSE_RANGE:" + label)
    return arr


def paired_branch_comparison(
    responses: Mapping[str, Any], p_first: float, p_second: float,
    *, ctx: Any, seed_salt: int = 51000,
) -> dict[str, Any]:
    """Compare five *jointly simulated* outcomes, never sum individual deltas.

    The outcomes are NO_ACTION, MOVE_ONLY, FIRST_ONLY, SECOND_ONLY, BOTH.
    FIRST_ONLY and SECOND_ONLY are conditional on the IR move being made; they
    are not an unconditional substitute for the original single-add policy.
    """
    keys = ("NO_ACTION", "MOVE_ONLY", "FIRST_ONLY", "SECOND_ONLY", "BOTH")
    if not isinstance(responses, Mapping) or set(responses) != set(keys):
        raise UnsupportedJointState("REQUIRED_ACQUISITION_OUTCOME_BRANCHES_MISSING")
    base = _checked_win_vector(responses["NO_ACTION"], "NO_ACTION")
    n = len(base)
    arrays = {key: _checked_win_vector(responses[key], key, n) for key in keys}
    probs = joint_probability_bounds(p_first, p_second)
    summaries = {}
    for i, key in enumerate(keys[1:]):
        # The same scenario index is the same physics draw in each branch.
        summaries[key] = _paired_stats(arrays[key] - base, ctx, seed_salt + i)
    return {
        "scenario_count": n,
        "comparison_baseline": "NO_ACTION_SAME_DRAW",
        "conditional_h2h_paired_response": summaries,
        "acquisition_behavior": probs,
        "joint_outcome_probability": (
            "UNIDENTIFIED" if probs["p_both_lower"] != probs["p_both_upper"]
            else float(probs["p_both_lower"])
        ),
        "conditional_response_computed_from_joint_state": True,
        "joint_expected_utility_certified": False,
        "future_capacity_credit": False,
        "action_authority": "NONE",
    }


def _require_current_move(ctx: Any, move_id: int) -> dict[str, Any]:
    moved = [dict(p) for p in ctx.roster if _finite_int(p.get("espn_id")) == move_id]
    if len(moved) != 1:
        raise UnsupportedJointState("MOVE_ASSET_NOT_OWNED_EXACTLY_ONCE")
    move = moved[0]
    if str(move.get("position") or "").upper() not in PLAYER_POSITIONS:
        raise UnsupportedJointState("SPECIALIST_IR_MOVE_NOT_YET_MODELED")
    if bool(move.get("lineup_locked")):
        raise UnsupportedJointState("IR_MOVE_ASSET_ALREADY_LOCKED")
    status = str(move.get("injury_status") or "").upper()
    if status not in {"OUT", "IR", "INJURY_RESERVE", "INJURED_RESERVE", "INJURED_RESERVE_IR"}:
        raise UnsupportedJointState("IR_MOVE_INJURY_STATUS_UNSUPPORTED")
    return move


def evaluate_bounded_joint_shadow(
    snapshot: Mapping[str, Any], league: Mapping[str, Any], model: Mapping[str, Any],
    ir_state: Mapping[str, Any], frontier: Mapping[str, Any], single_rows: list[dict[str, Any]],
    *, values_path: Any, team_name: Any, team_id: Any,
    mc_scenarios: int | None = None,
) -> dict[str, Any]:
    """Evaluate at most a bounded subset of frozen structural alternatives.

    Explicitly opt-in only; otherwise the existing live path is not burdened
    with extra MC. A skipped/failed pair can never authorize whole IR coverage.
    All five branches for each pair use the exact same UtilityContext and draws.
    """
    config = dict((model.get("ir_joint_response") or {}))
    if config.get("shadow_enabled") is not True:
        return {"status": "DISABLED", "coverage_complete": False,
                "action_authority": "NONE", "joint_predictive_mc": "NOT_EVALUATED"}
    limit = _finite_int(config.get("max_shadow_pairs", 2))
    if limit is None or not 1 <= limit <= 4:
        raise UnsupportedJointState("SHADOW_PAIR_BUDGET_INVALID")
    trials = _finite_int(mc_scenarios or config.get("shadow_scenarios", 64))
    if trials is None or not 64 <= trials <= 512:
        raise UnsupportedJointState("SHADOW_SCENARIO_BUDGET_INVALID")
    states = frontier.get("sample_joint_states") or []
    if not isinstance(states, list):
        raise UnsupportedJointState("JOINT_FRONTIER_NOT_A_LIST")
    rowmap = {_finite_int(row.get("add_espn_id")): dict(row) for row in single_rows
              if isinstance(row, Mapping) and _finite_int(row.get("add_espn_id")) is not None}
    ctx = _build_context(dict(snapshot), dict(league), dict(model), values_path,
                         team_name, team_id, trials)
    ctx.ensure_predictive_opponent_reference()
    d_static, k_static = _static_team_weekly(ctx, "DST"), _static_team_weekly(ctx, "K")
    d0 = simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    k0 = simulate_specialist_market_policy(ctx, position="K", user_mode="ONE_SLOT")
    base_player_weekly = evaluate_roster_predictive(
        list(ctx.roster), ctx, include_diagnostics=False,
        progress_label="IR joint shadow baseline",
    )[2]
    base_weekly, base_opp, _ = _compose_state(
        base_player_weekly, np.asarray(ctx.opponent_predictive, dtype=float), ctx,
        d_policy=d0, k_policy=k0, d_static=d_static, k_static=k_static,
    )
    week = int(ctx.week)
    base_win = _current_win(base_weekly, base_opp, week)
    available = {_finite_int(row.get("espn_id")): dict(row)
                 for row in ctx.actionable_available
                 if _finite_int(row.get("espn_id")) is not None}
    candidate_results = []
    for state in states[:limit]:
        if not isinstance(state, Mapping):
            candidate_results.append({"status": "BLOCKED_INVALID_FRONTIER_STATE"})
            continue
        move_id = _finite_int(state.get("move_to_ir_espn_id"))
        add_ids = state.get("add_espn_ids")
        if move_id is None or not isinstance(add_ids, list) or len(add_ids) != 2 or \
                any(_finite_int(pid) is None for pid in add_ids):
            candidate_results.append({"status": "BLOCKED_INVALID_FRONTIER_IDENTITY"})
            continue
        ids = [int(pid) for pid in add_ids]
        if len(set(ids + [move_id])) != 3:
            candidate_results.append({"status": "BLOCKED_DUPLICATE_ASSET"})
            continue
        try:
            _require_current_move(ctx, move_id)
            first, second = available.get(ids[0]), available.get(ids[1])
            if first is None or second is None:
                raise UnsupportedJointState("ACQUISITION_ASSET_NOT_IN_CURRENT_MARKET")
            rows = [rowmap.get(pid) for pid in ids]
            if any(row is None for row in rows):
                raise UnsupportedJointState("ACQUISITION_NOT_IN_SCOPED_FRONTIER")
            if any(str(row.get("fantasy_status") or "").upper() not in {"FREEAGENT", "WAIVERS"}
                   for row in rows):
                raise UnsupportedJointState("ACQUISITION_STATUS_UNSUPPORTED")
            positions = [str(row.get("position") or "").upper() for row in (first, second)]
            if any(pos not in set(PLAYER_POSITIONS) | {"DST", "K"} for pos in positions):
                raise UnsupportedJointState("CANDIDATE_POSITION_UNSUPPORTED")
            if (positions.count("DST") > 1 or positions.count("K") > 1):
                raise UnsupportedJointState("TWO_SAME_SPECIALIST_CHANNEL_ACQUISITIONS_UNSUPPORTED")
            headroom = ir_state.get("position_headroom_total_roster") or {}
            for pos in set(positions):
                if _finite_int(headroom.get(pos)) is None or \
                        int(headroom[pos]) < positions.count(pos):
                    raise UnsupportedJointState("JOINT_POSITION_HEADROOM_INSUFFICIENT")
            try:
                marginals = [float(row["p_acquire"]) for row in rows]
            except (KeyError, ValueError, TypeError, OverflowError) as exc:
                raise UnsupportedJointState("ACQUISITION_BEHAVIOR_MISSING") from exc
            if any(not np.isfinite(p) or not 0 <= p <= 1 for p in marginals):
                raise UnsupportedJointState("ACQUISITION_BEHAVIOR_INVALID")
            outcomes = {"NO_ACTION": base_win}
            for label, selected in (
                ("MOVE_ONLY", []), ("FIRST_ONLY", [first]),
                ("SECOND_ONLY", [second]), ("BOTH", [first, second]),
            ):
                p_adds = [dict(p) for p in selected
                          if str(p.get("position") or "").upper() in PLAYER_POSITIONS]
                current_roster = list(ctx.roster) + p_adds
                # The moved injured player remains owned, but is excluded from
                # this *current-week* lineup response after entering IR.
                without_move = [p for p in current_roster
                                if _finite_int(p.get("espn_id")) != move_id]
                # Only the current-week column is consumed: no claim is made
                # about return dates, future IR occupancy, or capacity credit.
                merged = evaluate_roster_predictive(
                    without_move, ctx, include_diagnostics=False,
                    progress_label="IR joint shadow current-only state",
                )[2]
                d_policy, k_policy = d0, k0
                for p in selected:
                    pos = str(p.get("position") or "").upper()
                    if pos in {"DST", "K"}:
                        forced = simulate_specialist_market_policy(
                            ctx, position=pos, user_mode="OPEN_SLOT_PLUS_ONE_CURRENT_ONLY",
                            pre_acquire_espn_id=int(p["espn_id"]),
                            pre_acquire_from_waivers=(
                                str(p.get("fantasy_status") or "").upper() in {"WAIVER", "WAIVERS"}
                            ),
                        )
                        if pos == "DST":
                            d_policy = forced
                        else:
                            k_policy = forced
                complete, opp, _ = _compose_state(
                    merged, np.asarray(ctx.opponent_predictive, dtype=float), ctx,
                    d_policy=d_policy, k_policy=k_policy,
                    d_static=d_static, k_static=k_static,
                )
                outcomes[label] = _current_win(complete, opp, week)
            paired = paired_branch_comparison(
                outcomes, marginals[0], marginals[1],
                ctx=ctx, seed_salt=51000 + ids[0] + ids[1] + move_id,
            )
            candidate_results.append({
                "status": "SCOPED_PAIRED_MC_EVALUATED_NOT_CERTIFIED",
                "move_to_ir_espn_id": move_id, "add_espn_ids": ids,
                "paired": paired,
            })
        except UnsupportedJointState as exc:
            candidate_results.append({"status": "BLOCKED_UNSUPPORTED_JOINT_STATE",
                                      "reason": str(exc)})
    return {"status": "SCOPED_JOINT_SHADOW_ONLY", "sample_total": len(states),
            "sample_evaluated": len(candidate_results),
            "all_structural_states_evaluated": False,
            "paired_candidates": candidate_results,
            "joint_behavior_exact": False,
            "joint_predictive_mc": "BOUNDED_SHADOW",
            "coverage_complete": False, "action_authority": "NONE",
            "future_capacity_credit": False}


def _current_win(weekly: Any, opponent: Any, week: int) -> np.ndarray:
    w = np.asarray(weekly, dtype=float)[:, week - 1]
    o = np.asarray(opponent, dtype=float)[:, week - 1]
    if w.shape != o.shape or w.ndim != 1 or not np.all(np.isfinite(w)) or not np.all(np.isfinite(o)):
        raise UnsupportedJointState("INCOMPARABLE_SCENARIO_SHAPES")
    result = (w > o).astype(float)
    result[w == o] = 0.5
    return result
