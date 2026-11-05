"""Prospective add-only player-channel response for a *current* open active slot.

This is a bounded candidate/evidence path, not ESPN legality or action authority.
It reuses commissioned player predictive streams and the original zero-release
league baseline.  It does not model IR-move-plus-add or DST/K acquisitions.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .ir_roster_state import build_ir_roster_state


POSITIONS = ("QB", "RB", "WR", "TE")
STATUSES = ("FREEAGENT", "WAIVERS")


def _bounded_positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if number > 0 else None


def _status(row: Mapping[str, Any]) -> str | None:
    value = str(row.get("fantasy_status") or "").upper()
    if value == "WAIVER":
        value = "WAIVERS"
    return value if value in STATUSES else None


def legal_open_slot_candidates(
    roster: list[dict[str, Any]], candidates: list[dict[str, Any]],
    state: Mapping[str, Any], league: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Preserve all legal player positions, without pretending to drop anyone."""
    if state.get("status") != "PASS" or int(state.get("direct_open_slot_add_capacity") or 0) < 1:
        return []
    maxima = league.get("position_maximums")
    if not isinstance(maxima, Mapping) or any(_bounded_positive_int(maxima.get(p)) is None for p in POSITIONS):
        return []
    ids = {_bounded_positive_int(p.get("espn_id")) for p in roster}
    counts = {p: sum(str(r.get("position") or "").upper() == p for r in roster) for p in POSITIONS}
    selected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        pid = _bounded_positive_int(candidate.get("espn_id"))
        pos = str(candidate.get("position") or "").upper()
        if (pid is None or pid in ids or pid in seen or pos not in POSITIONS or
                _status(candidate) is None or counts[pos] >= int(maxima[pos])):
            continue
        if candidate.get("lineup_locked") is True:
            continue
        selected.append(dict(candidate))
        seen.add(pid)
    return selected


def evaluate_open_slot_actions(ctx: Any, candidates: list[dict[str, Any]],
                               league: Mapping[str, Any], *, final_mc: int | None = None) -> dict[str, Any]:
    """Value S -> S + player with paired predictive MC, without a release kernel.

    Reuse the existing hierarchical paired-MC stage and native classification.
    Cheap utility ranks a bounded predictive frontier; it cannot certify HOLD
    for unmodeled IR moves, claim ordering, or app-side transaction legality.
    """
    from . import transaction_manager as tm

    state = build_ir_roster_state(ctx.team, league)
    open_slots = int(state.get("open_active_roster_slots") or 0)
    result: dict[str, Any] = {
        "contract": "PLAYER_OPEN_ACTIVE_SLOT_PAIRED_RESPONSE_V1",
        "authority": "OBSERVATION_ONLY",
        "acquisition_structure": "ADD_ONLY",
        "open_active_roster_slots": open_slots,
        "ir_state": str(state.get("status") or "UNKNOWN"),
        "screened_actions": 0,
        "predictive_actions_evaluated": 0,
        "actions": [],
        "action_authority": "NONE",
    }
    if state.get("status") != "PASS":
        result["status"] = "BLOCKED_IR_STATE"
        result["blockers"] = list(state.get("blockers") or [])
        return result
    if int(state.get("direct_open_slot_add_capacity") or 0) < 1:
        result["status"] = "NO_CURRENT_DIRECT_OPENING"
        return result
    maxima = league.get("position_maximums")
    if not isinstance(maxima, Mapping) or any(_bounded_positive_int(maxima.get(p)) is None for p in POSITIONS):
        result["status"] = "BLOCKED_POSITION_LIMITS_UNKNOWN"
        return result

    actionable = legal_open_slot_candidates(ctx.roster, candidates, state, league)
    result["legal_candidate_count"] = len(actionable)
    if not actionable:
        result["status"] = "NO_LEGAL_CANDIDATE"
        return result

    # The complete-roster cheap response is a *screen*, never the final value.
    base = tm.evaluate_roster_utility(ctx.roster, ctx)
    budget = max(1, int(ctx.cfg.get("action_mc_final_keep_per_status", 4)))
    rows: list[dict[str, Any]] = []
    for add in actionable:
        status = _status(add)
        if status is None:
            continue
        after_roster = list(ctx.roster) + [dict(add)]
        quick = tm.evaluate_roster_utility(after_roster, ctx)
        p_acquire = (1.0 if status == "FREEAGENT"
                     else tm.waiver_screen_acquisition_probability(add, ctx))
        rows.append({
            "add": add,
            # An explicit bookkeeping sentinel for the existing MC progress API,
            # NEVER a player to release or an ESPN drop identifier.
            "drop": {"espn_id": 0, "name": "OPEN_SLOT", "position": "OPEN_SLOT"},
            "acquisition_structure": "ADD_ONLY",
            "new_roster": after_roster,
            "fantasy_status": status,
            "p_acquire": float(p_acquire),
            "screen_delta": float(quick.utility - base.utility),
            "screen_expected_delta": float(p_acquire * (quick.utility - base.utility)),
            "screen_utility": quick,
            "league_state_response": {},  # no release -> no field-response correction
        })
    result["screened_actions"] = len(rows)
    selected: list[dict[str, Any]] = []
    for status in STATUSES:
        group = [r for r in rows if r["fantasy_status"] == status]
        group.sort(key=lambda r: float(r["screen_expected_delta"]), reverse=True)
        selected.extend(group[:budget])
    if not selected:
        result["status"] = "NO_SELECTED_ACTION"
        return result

    final_n = int(final_mc if final_mc is not None else ctx.predictive_scenarios)
    stages = sorted({int(x) for x in ctx.cfg.get("action_mc_stages", [])
                     if str(x).isdigit() and 8 <= int(x) < final_n})
    stages.append(final_n)
    frontier = selected
    evaluated: list[dict[str, Any]] = []
    for ix, n in enumerate(stages):
        _, _, _, evaluated = tm._run_action_mc_stage(
            frontier, ctx, mc_scenarios=n,
            stage_name="FINAL" if ix == len(stages) - 1 else "SCREEN" + str(ix + 1),
            include_diagnostics=(ix == len(stages) - 1),
        )
        if ix < len(stages) - 1:
            next_frontier = tm._action_stage_prune(
                evaluated, per_status_limit=budget,
                require_classification_plausible=bool(ctx.cfg.get("action_mc_futility_enabled", True)),
            )
            if not next_frontier:
                result["predictive_screen_futility_stop"] = True
                break
            frontier = next_frontier
    result["predictive_actions_evaluated"] = len(evaluated)
    # Each row has paired per-universe deltas relative to the very same baseline.
    # With no dropped asset, the field remains unchanged (zero release response).
    out: list[dict[str, Any]] = []
    for row in evaluated:
        add = row["add"]
        raw = np.asarray(row["stage_raw_delta"], dtype=float)
        adjusted = np.asarray(row["stage_adjusted_delta"], dtype=float)
        if raw.shape != adjusted.shape or raw.ndim != 1 or not len(raw):
            raise ValueError("OPEN_SLOT_PAIRED_MC_SHAPE_INVALID")
        pid = int(add["espn_id"])
        seed = int(ctx.seed) + 31 * pid  # no fictitious release identifier
        interval_raw = tm._paired_mean_interval(
            raw, seed=seed, draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)))
        interval = tm._paired_mean_interval(
            adjusted, seed=seed, draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)))
        combined, _, _ = tm._classify_market_action(
            raw, adjusted, ctx.cfg, raw_p16=interval_raw[0], adjusted_p16=interval[0])
        value = float(np.mean(adjusted))
        out.append({
            "acquisition_structure": "ADD_ONLY",
            "add_espn_id": pid,
            "add_name": str(add.get("name") or pid),
            "add_position": str(add.get("position")),
            "fantasy_status": row["fantasy_status"],
            "drop_espn_id": None,
            "drop_name": None,
            "drop_position": None,
            "delta_utility": value,
            "expected_delta_utility": value * float(row["p_acquire"]),
            "p_acquire": float(row["p_acquire"]),
            "delta_total_utility_p16": float(interval[0]),
            "delta_total_utility_p84": float(interval[1]),
            "p_utility_better_if_acquired": float(np.mean(adjusted > 0)),
            "combined_action_classification": combined,
            "mc_stage": str(row["stage_name"]),
            "mc_scenarios": int(row["stage_mc"]),
            "release_response_applied": False,
            "action_authority": "NONE",
        })
    out.sort(key=lambda x: x["expected_delta_utility"], reverse=True)
    result["actions"] = out
    result["status"] = "PREDICTIVE_EVALUATED_UNCERTIFIED"
    return result
