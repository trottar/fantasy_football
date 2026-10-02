from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from .ir_roster_state import evaluate_ir_roster_state
from .specialist_channels import _is_current_week_locked
from .specialist_policy_v032 import (
    _build_context as _build_specialist_context,
    _compose_state,
    _is_current_week_locked,
    _paired_stats,
    _pid,
    _position_rows,
    _static_team_weekly,
    simulate_specialist_market_policy,
)
from .transaction_manager import (
    PLAYER_POSITIONS,
    UtilityContext,
    evaluate_roster_predictive,
    preselect_candidates,
    waiver_acquisition_probability,
    waiver_blocker_diagnostics,
)
from .weekly_manager import resolve_team


AUTHORITY = "IR_MOVE_PLUS_ADD_VALUE_ADAPTER_V001"
INFORMATION_POLICY = "CURRENT_WEEK_SINGLE_B2A_IR_OPENED_SLOT_ONLY_NO_FUTURE_CAPACITY_CREDIT"
SUPPORTED_CAPACITY = 1


def _finite_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _fantasy_status(player: Mapping[str, Any]) -> str:
    raw = str(player.get("fantasy_status") or "").strip().upper()
    return "WAIVERS" if raw in {"WAIVER", "WAIVERS"} else "FREEAGENT"


def _position(player: Mapping[str, Any]) -> str:
    return str(player.get("position") or "").strip().upper()


def _current_h2h(weekly: np.ndarray, opponent: np.ndarray, week: int) -> np.ndarray:
    ours = np.asarray(weekly, dtype=float)[:, int(week) - 1]
    theirs = np.asarray(opponent, dtype=float)[:, int(week) - 1]
    if ours.shape != theirs.shape:
        raise ValueError("current-week roster/opponent scenario shapes differ")
    out = (ours > theirs).astype(float)
    out[ours == theirs] = 0.5
    return out


def _resolve_current_capacity(ir_state: Mapping[str, Any]) -> dict[str, Any]:
    if str(ir_state.get("status") or "").upper() != "PASS":
        return {
            "coverage_complete": False,
            "reason": "IR_ROSTER_STATE_BLOCKED",
            "move_to_ir": None,
        }

    direct = int(ir_state.get("direct_open_slot_add_capacity") or 0)
    move_capacity = int(ir_state.get("ir_move_plus_add_capacity") or 0)
    total = int(ir_state.get("potential_add_capacity") or 0)
    candidates = [
        dict(row)
        for row in (ir_state.get("ir_move_candidates") or [])
        if isinstance(row, Mapping)
    ]

    if total <= 0:
        return {
            "coverage_complete": True,
            "reason": "NO_CURRENT_IR_OPENED_SLOT_CAPACITY",
            "move_to_ir": None,
        }

    if direct > 0:
        return {
            "coverage_complete": False,
            "reason": "DIRECT_OPEN_ACTIVE_SLOT_OUT_OF_SCOPE",
            "move_to_ir": None,
        }

    if total > SUPPORTED_CAPACITY:
        return {
            "coverage_complete": False,
            "reason": "MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED",
            "move_to_ir": None,
        }

    if move_capacity != 1 or len(candidates) != 1:
        return {
            "coverage_complete": False,
            "reason": "AMBIGUOUS_IR_MOVE_CANDIDATE_WITHOUT_B2B_HORIZON",
            "move_to_ir": None,
        }

    return {
        "coverage_complete": True,
        "reason": "IR_MOVE_OPENS_ONE_ACTIVE_SLOT",
        "move_to_ir": candidates[0],
    }


def _position_headroom(ir_state: Mapping[str, Any], position: str) -> bool:
    headroom = ir_state.get("position_headroom_total_roster")
    if not isinstance(headroom, Mapping):
        return False
    value = headroom.get(str(position).upper())
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def _candidate_common(
    candidate: Mapping[str, Any],
    ctx: UtilityContext,
    stats: Mapping[str, Any],
    *,
    channel: str,
) -> dict[str, Any]:
    status = _fantasy_status(candidate)
    blockers: list[dict[str, Any]] = []
    p_acquire = 1.0
    if status == "WAIVERS":
        blockers = waiver_blocker_diagnostics(dict(candidate), ctx)
        p_acquire = float(
            waiver_acquisition_probability(dict(candidate), ctx, blockers=blockers)
        )
    mean = float(stats.get("mean") or 0.0)
    return {
        "channel": str(channel),
        "add_espn_id": _finite_int(candidate.get("espn_id")),
        "add_name": candidate.get("name"),
        "add_position": _position(candidate),
        "add_team": candidate.get("nfl_team"),
        "fantasy_status": status,
        "drop_espn_id": None,
        "drop_name": None,
        "p_acquire": float(p_acquire),
        "waiver_blockers": blockers,
        "conditional_complete_state_delta": dict(stats),
        "expected_complete_state_delta_mean": float(p_acquire * mean),
        "classification": str(stats.get("classification") or "NO_RESOLVED_EDGE"),
        "future_capacity_credit": False,
        "information_policy": INFORMATION_POLICY,
    }


def _player_candidates(
    snapshot: Mapping[str, Any],
    league: Mapping[str, Any],
    model: Mapping[str, Any],
    ir_state: Mapping[str, Any],
    *,
    values_path,
    team_name,
    team_id,
    mc_scenarios,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    team = resolve_team(dict(snapshot), team_name=team_name, team_id=team_id)
    ctx = UtilityContext(dict(snapshot), dict(league), dict(model), values_path, team)
    if mc_scenarios is not None:
        ctx.set_predictive_scenarios(int(mc_scenarios))

    screened = [
        dict(player)
        for player in preselect_candidates(ctx.actionable_available, ctx.cfg, position=None)
        if _position(player) in PLAYER_POSITIONS
        and _finite_int(player.get("espn_id")) is not None
        and not _is_current_week_locked(dict(player), ctx)
        and _position_headroom(ir_state, _position(player))
        and _fantasy_status(player) in {"FREEAGENT", "WAIVERS"}
    ]

    if not screened:
        return [], {
            "preselected": 0,
            "predictive_frontier": 0,
            "mc_scenarios": int(ctx.predictive_scenarios),
            "screen_authority": False,
        }

    ctx.ensure_predictive_opponent_reference()
    _base_result, _base_utility, base_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, include_diagnostics=False, progress_label="IR open-slot HOLD"
    )
    d_static = _static_team_weekly(ctx, "DST")
    k_static = _static_team_weekly(ctx, "K")
    d1 = simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    k1 = simulate_specialist_market_policy(ctx, position="K", user_mode="ONE_SLOT")
    base_weekly_complete, base_opponent, _base_complete_utility = _compose_state(
        base_weekly,
        np.asarray(ctx.opponent_predictive, dtype=float),
        ctx,
        d_policy=d1,
        k_policy=k1,
        d_static=d_static,
        k_static=k_static,
    )
    base_current = _current_h2h(base_weekly_complete, base_opponent, int(ctx.week))

    rows: list[dict[str, Any]] = []
    for candidate in screened:
        new_roster = list(ctx.roster) + [dict(candidate)]
        _result, _utility, weekly = evaluate_roster_predictive(
            new_roster,
            ctx,
            include_diagnostics=False,
            progress_label=f"IR open-slot add {candidate.get('name') or candidate.get('espn_id')}",
        )
        weekly_complete, opponent, _complete_utility = _compose_state(
            weekly,
            np.asarray(ctx.opponent_predictive, dtype=float),
            ctx,
            d_policy=d1,
            k_policy=k1,
            d_static=d_static,
            k_static=k_static,
        )
        current = _current_h2h(weekly_complete, opponent, int(ctx.week))
        delta = np.asarray(current) - np.asarray(base_current)
        stats = _paired_stats(
            delta,
            ctx,
            41000 + int(_finite_int(candidate.get("espn_id")) or 0),
        )
        rows.append(_candidate_common(candidate, ctx, stats, channel="PLAYER"))

    return rows, {
        "preselected": len(screened),
        "predictive_frontier": len(screened),
        "mc_scenarios": int(ctx.predictive_scenarios),
        "screen_authority": False,
    }


def _specialist_candidates(
    snapshot: Mapping[str, Any],
    league: Mapping[str, Any],
    model: Mapping[str, Any],
    ir_state: Mapping[str, Any],
    *,
    values_path,
    team_name,
    team_id,
    mc_scenarios,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ctx = _build_specialist_context(
        dict(snapshot),
        dict(league),
        dict(model),
        values_path,
        team_name,
        team_id,
        mc_scenarios,
    )
    ctx.ensure_predictive_opponent_reference()

    d_static = _static_team_weekly(ctx, "DST")
    k_static = _static_team_weekly(ctx, "K")
    d1 = simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    k1 = simulate_specialist_market_policy(ctx, position="K", user_mode="ONE_SLOT")
    _base_result, _base_utility, base_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, include_diagnostics=False, progress_label="IR specialist base roster"
    )
    base_weekly_complete, base_opponent, _base_complete_utility = _compose_state(
        base_weekly,
        np.asarray(ctx.opponent_predictive, dtype=float),
        ctx,
        d_policy=d1,
        k_policy=k1,
        d_static=d_static,
        k_static=k_static,
    )
    base_current = _current_h2h(base_weekly_complete, base_opponent, int(ctx.week))

    rows: list[dict[str, Any]] = []
    considered = 0

    for position in ("DST", "K"):
        if not _position_headroom(ir_state, position):
            continue
        owned = _position_rows(ctx.roster, position)
        mode = "OPEN_SLOT_PLUS_ONE_CURRENT_ONLY"
        candidates = [
            dict(player)
            for player in ctx.actionable_available
            if _position(player) == position
            and _finite_int(player.get("espn_id")) is not None
            and not _is_current_week_locked(player, ctx)
            and _fantasy_status(player) in {"FREEAGENT", "WAIVERS"}
        ]
        candidates.sort(
            key=lambda p: (
                -float(p.get("weekly_projection") or 0.0),
                int(_finite_int(p.get("espn_id")) or 10**12),
            )
        )
        limit = max(
            1,
            int(
                (dict(model).get("specialist_channels") or {}).get(
                    "candidate_limit", 16
                )
            ),
        )
        candidates = candidates[:limit]
        considered += len(candidates)

        for candidate in candidates:
            candidate_id = int(_finite_int(candidate.get("espn_id")) or 0)
            status = _fantasy_status(candidate)
            forced = simulate_specialist_market_policy(
                ctx,
                position=position,
                user_mode=mode,
                pre_acquire_espn_id=candidate_id,
                pre_acquire_from_waivers=(status == "WAIVERS"),
            )
            if position == "DST":
                weekly_complete, opponent, _utility = _compose_state(
                    base_weekly,
                    np.asarray(ctx.opponent_predictive, dtype=float),
                    ctx,
                    d_policy=forced,
                    k_policy=k1,
                    d_static=d_static,
                    k_static=k_static,
                )
            else:
                weekly_complete, opponent, _utility = _compose_state(
                    base_weekly,
                    np.asarray(ctx.opponent_predictive, dtype=float),
                    ctx,
                    d_policy=d1,
                    k_policy=forced,
                    d_static=d_static,
                    k_static=k_static,
                )
            current = _current_h2h(weekly_complete, opponent, int(ctx.week))
            delta = np.asarray(current) - np.asarray(base_current)
            stats = _paired_stats(delta, ctx, 42000 + candidate_id)
            rows.append(_candidate_common(candidate, ctx, stats, channel=position))

    return rows, {
        "candidates_considered": int(considered),
        "mc_scenarios": int(ctx.predictive_scenarios),
        "open_slot_policy": "OPEN_SLOT_PLUS_ONE_CURRENT_ONLY",
        "general_two_kicker_carry_policy_unchanged": "DISABLED",
        "legal_kicker_open_slot_branch_skipped": False,
    }


def evaluate_ir_replacement(
    snapshot: Mapping[str, Any],
    league: Mapping[str, Any],
    model: Mapping[str, Any],
    *,
    values_path="data/processed/player_values_2026.csv",
    team_name=None,
    team_id=None,
    player_mc_scenarios=None,
    specialist_mc_scenarios=None,
) -> dict[str, Any]:
    ir_state = evaluate_ir_roster_state(
        snapshot, league, team_name=team_name, team_id=team_id
    )
    capacity = _resolve_current_capacity(ir_state)

    headroom = ir_state.get("position_headroom_total_roster")
    required_positions = ("QB", "RB", "WR", "TE", "DST", "K")
    headroom_complete = isinstance(headroom, Mapping) and all(
        _finite_int(headroom.get(position)) is not None
        for position in required_positions
    )
    if not headroom_complete and bool(capacity.get("coverage_complete")):
        capacity = {
            "coverage_complete": False,
            "reason": "POSITION_MAXIMUM_HEADROOM_INCOMPLETE",
            "move_to_ir": capacity.get("move_to_ir"),
        }

    base = {
        "schema_version": 1,
        "authority": AUTHORITY,
        "status": str(ir_state.get("status") or "UNKNOWN"),
        "coverage_complete": bool(capacity.get("coverage_complete")),
        "coverage_reason": capacity.get("reason"),
        "ir_state": dict(ir_state),
        "move_to_ir": capacity.get("move_to_ir"),
        "future_capacity_credit": False,
        "multiweek_absence_horizon_used": False,
        "information_policy": INFORMATION_POLICY,
        "supported_current_open_slots": SUPPORTED_CAPACITY,
        "candidate_rows": [],
        "recommended_action": None,
    }

    if not bool(capacity.get("coverage_complete")):
        return base
    if str(capacity.get("reason")) == "NO_CURRENT_IR_OPENED_SLOT_CAPACITY":
        return base

    player_rows, player_meta = _player_candidates(
        snapshot,
        league,
        model,
        ir_state,
        values_path=values_path,
        team_name=team_name,
        team_id=team_id,
        mc_scenarios=player_mc_scenarios,
    )
    specialist_rows, specialist_meta = _specialist_candidates(
        snapshot,
        league,
        model,
        ir_state,
        values_path=values_path,
        team_name=team_name,
        team_id=team_id,
        mc_scenarios=specialist_mc_scenarios,
    )
    rows = player_rows + specialist_rows
    rows.sort(
        key=lambda row: (
            float(row.get("expected_complete_state_delta_mean") or -999.0),
            float(
                (
                    (row.get("conditional_complete_state_delta") or {}).get("mean")
                    or -999.0
                )
            ),
            -int(row.get("add_espn_id") or -1),
        ),
        reverse=True,
    )
    actionable = [
        dict(row)
        for row in rows
        if str(row.get("classification") or "") == "ACTIONABLE_EDGE"
        and float(row.get("expected_complete_state_delta_mean") or 0.0) > 0.0
    ]

    base["candidate_rows"] = rows
    base["player_search"] = player_meta
    base["specialist_search"] = specialist_meta
    if actionable:
        best = dict(actionable[0])
        base["recommended_action"] = {
            "kind": "IR_MOVE_PLUS_ADD",
            "move_to_ir": capacity.get("move_to_ir"),
            "add": best,
            "drop_espn_id": None,
            "drop_name": None,
            "future_capacity_credit": False,
            "information_policy": INFORMATION_POLICY,
        }
    return base
