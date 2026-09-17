from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .season_utility import week_weights
from .transaction_manager import (
    _best_lineup_points,
    _finite_int,
    _legal_drop,
    _legal_roster_after_add_drop,
    _player_points,
    _release_claim_probability,
    _simulate_predictive_weekly_points,
)

PLAYER_POSITIONS = {"QB", "RB", "WR", "TE"}
CASCADE_MODEL = "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE"
CASCADE_ORDER1_CONTRACT = "COMMISSIONED_ORDER1_PRESERVED_EXACTLY_V036"
CASCADE_SCREEN_MODEL = "DETERMINISTIC_EXPECTED_LINEUP_CLAIMANT_FRONTIER_SCREEN_ONLY_V036"
CASCADE_ORDER_MODEL = "CURRENT_ESPN_WAIVER_PRIORITY_PROXY_UNCALIBRATED_V036"
CASCADE_TIMING_MODEL = "RECIPIENT_RELEASE_AVAILABLE_NEXT_MODELED_WEEK_V036"
CASCADE_CHANNEL_MODEL = "PLAYER_QB_RB_WR_TE_ONLY_V036"
EPS = 1e-12


@dataclass
class _Branch:
    probability: float
    released_player: dict[str, Any]
    release_week: int
    releaser_team_id: int
    rosters: dict[int, list[dict[str, Any]]]
    path_player_ids: tuple[int, ...]


def _pid(player: dict[str, Any] | None) -> int | None:
    return _finite_int((player or {}).get("espn_id"))


def _ordinary(player: dict[str, Any] | None) -> bool:
    return str((player or {}).get("position") or "").upper() in PLAYER_POSITIONS


def _clone_rosters(ctx) -> dict[int, list[dict[str, Any]]]:
    return {int(tid): [dict(p) for p in roster] for tid, roster in ctx.all_team_rosters.items()}


def _player_lookup(ctx, extra: dict[str, Any] | None = None) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    pools = []
    pools.extend(ctx.all_team_rosters.values())
    pools.append(list(ctx.espn.get("available_players") or []))
    if extra is not None:
        pools.append([extra])
    for pool in pools:
        for player in pool:
            pid = _pid(player)
            if pid is not None:
                out[int(pid)] = dict(player)
    return out


def _weights_from(ctx, start_week: int) -> tuple[np.ndarray, float]:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float).copy()
    weights[np.asarray(weeks, dtype=int) < int(start_week)] = 0.0
    if float(weights.sum()) <= 0.0:
        weights[np.asarray(weeks, dtype=int) >= int(start_week)] = 1.0
    return weights, max(float(weights.sum()), EPS)


def _expected_lineup_points(roster: list[dict[str, Any]], ctx, week: int) -> float:
    players = [dict(p) for p in roster if _ordinary(p)]
    scores: dict[int, float] = {}
    active: dict[int, bool] = {}
    for player in players:
        pid = _pid(player)
        if pid is None:
            continue
        state = ctx.yield_state(player, int(week))
        p_active = min(max(float(state.availability_probability), 0.0), 1.0)
        conditional = max(float(_player_points(player, ctx, int(week))), 0.0)
        expected = conditional * p_active
        scores[int(pid)] = expected
        active[int(pid)] = expected > 0.0
    value, _ = _best_lineup_points(players, active, scores, ctx.league, ctx.replacement_season)
    return float(value)


def _screen_roster_score(roster: list[dict[str, Any]], ctx, start_week: int) -> tuple[float, float]:
    weekly = np.zeros(17, dtype=float)
    for week in range(int(start_week), 18):
        weekly[week - 1] = _expected_lineup_points(roster, ctx, week)
    weights, norm = _weights_from(ctx, start_week)
    return float(np.sum(weekly * weights) / norm), float(weekly[int(start_week) - 1])


def _screen_interest(candidate: dict[str, Any], roster: list[dict[str, Any]], ctx, start_week: int) -> dict[str, Any]:
    if not _ordinary(candidate):
        return {"legal": False}
    baseline_season, baseline_week = _screen_roster_score(roster, ctx, start_week)
    best: tuple[dict[str, Any], list[dict[str, Any]], float, float] | None = None
    for drop in roster:
        if not _ordinary(drop) or not _legal_drop(drop):
            continue
        if not _legal_roster_after_add_drop(roster, candidate, drop, ctx.league):
            continue
        drop_id = _pid(drop)
        if drop_id is None:
            continue
        new_roster = [dict(p) for p in roster if _pid(p) != int(drop_id)] + [dict(candidate)]
        season_score, week_score = _screen_roster_score(new_roster, ctx, start_week)
        if best is None or season_score > best[2]:
            best = (dict(drop), new_roster, float(season_score), float(week_score))
    if best is None:
        return {"legal": False}
    drop, new_roster, season_score, week_score = best
    return {
        "legal": True,
        "drop_espn_id": _pid(drop),
        "drop_name": drop.get("name"),
        "new_roster": new_roster,
        "delta_season_ppg": float(season_score - baseline_season),
        "delta_current_week": float(week_score - baseline_week),
    }


def _authoritative_claimants(
    candidate: dict[str, Any],
    rosters: dict[int, list[dict[str, Any]]],
    ctx,
    *,
    start_week: int,
    scenarios: int,
    exclude_team_ids: set[int],
    frontier: int,
) -> tuple[list[dict[str, Any]], float]:
    """Return paired-MC claimant rows plus screen-pruned winner probability mass.

    The deterministic screen chooses a legal release and limits the claimant frontier.
    It never supplies the football-response magnitude propagated into the cascade.
    """
    team_meta = {
        int(t.get("team_id")): t
        for t in (ctx.espn.get("teams") or [])
        if _finite_int(t.get("team_id")) is not None
    }
    screened: list[dict[str, Any]] = []
    for tid, roster in rosters.items():
        if int(tid) in exclude_team_ids:
            continue
        interest = _screen_interest(candidate, roster, ctx, start_week)
        if not bool(interest.get("legal")):
            continue
        p_screen = _release_claim_probability(candidate, roster, interest, ctx)
        if p_screen <= 0.0:
            continue
        meta = team_meta.get(int(tid)) or {}
        screened.append({
            "team_id": int(tid),
            "team_name": str(meta.get("name") or meta.get("team_name") or f"team {tid}"),
            "waiver_rank": _finite_int(meta.get("waiver_rank")) or 10**6,
            "screen_claim_probability": float(p_screen),
            "drop_espn_id": _finite_int(interest.get("drop_espn_id")),
            "drop_name": interest.get("drop_name"),
            "new_roster": list(interest.get("new_roster") or []),
        })
    screened.sort(key=lambda r: (int(r["waiver_rank"]), int(r["team_id"])))

    survival = 1.0
    for row in screened:
        p = min(max(float(row["screen_claim_probability"]), 0.0), 1.0)
        row["screen_winner_probability"] = float(survival * p)
        survival *= 1.0 - p
    retained = screened[: max(1, int(frontier))]
    pruned_mass = float(sum(float(r.get("screen_winner_probability") or 0.0) for r in screened[len(retained):]))

    old_n = int(ctx.predictive_scenarios)
    rows: list[dict[str, Any]] = []
    ctx.set_predictive_scenarios(max(16, int(scenarios)))
    try:
        weights, norm = _weights_from(ctx, start_week)
        for row in retained:
            tid = int(row["team_id"])
            roster = rosters[tid]
            new_roster = [dict(p) for p in row["new_roster"]]
            before = _simulate_predictive_weekly_points(
                roster, ctx, ctx.replacement_current, ctx.replacement_season,
                current_week_policy="realistic", progress_label="v0.36 cascade recipient before",
            )
            after = _simulate_predictive_weekly_points(
                new_roster, ctx, ctx.replacement_current, ctx.replacement_season,
                current_week_policy="realistic", progress_label="v0.36 cascade recipient after",
            )
            delta = np.asarray(after, dtype=float) - np.asarray(before, dtype=float)
            delta[:, : int(start_week) - 1] = 0.0
            delta_mean = np.mean(delta, axis=0)
            delta_season = np.sum(delta * weights[None, :], axis=1) / norm
            interest = {
                "legal": True,
                "delta_season_ppg": float(np.mean(delta_season)),
                "delta_current_week": float(delta_mean[int(start_week) - 1]),
            }
            p_claim = _release_claim_probability(candidate, roster, interest, ctx)
            rows.append({
                **row,
                "claim_probability": float(p_claim),
                "delta_season_ppg": float(interest["delta_season_ppg"]),
                "delta_release_week": float(interest["delta_current_week"]),
                "delta_weekly_mean": np.asarray(delta_mean, dtype=float),
            })
    finally:
        if int(ctx.predictive_scenarios) != old_n:
            ctx.set_predictive_scenarios(old_n)

    rows.sort(key=lambda r: (int(r["waiver_rank"]), int(r["team_id"])))
    survival = 1.0
    for row in rows:
        p = min(max(float(row["claim_probability"]), 0.0), 1.0)
        row["winner_probability"] = float(survival * p)
        survival *= 1.0 - p
    return rows, pruned_mass


def _season_mean_from_vector(vector: np.ndarray, ctx, start_week: int) -> float:
    weights, norm = _weights_from(ctx, start_week)
    return float(np.sum(np.asarray(vector, dtype=float) * weights) / norm)


def extend_release_response(
    candidate: dict[str, Any],
    ctx,
    first_order: dict[str, Any],
    *,
    start_week: int,
) -> dict[str, Any]:
    """Add bounded order-2+ field response while preserving commissioned order 1.

    Order 1 is supplied by the existing commissioned kernel.  Only the player released
    by an order-n recipient can seed order n+1, and that released player becomes
    available no earlier than the following modeled week.
    """
    result = dict(first_order)
    first_shift = np.asarray(first_order.get("opponent_reference_shift_ppg_by_week") or np.zeros(17), dtype=float)
    if len(first_shift) != 17:
        first_shift = np.resize(first_shift, 17)
    result.update({
        "model": CASCADE_MODEL,
        "first_order_model": first_order.get("model"),
        "first_order_contract": CASCADE_ORDER1_CONTRACT,
        "cascade_screen_model": CASCADE_SCREEN_MODEL,
        "cascade_waiver_order_model": CASCADE_ORDER_MODEL,
        "cascade_timing_model": CASCADE_TIMING_MODEL,
        "cascade_channel_model": CASCADE_CHANNEL_MODEL,
        "first_order_field_shift_ppg": float(first_order.get("field_shift_ppg") or 0.0),
        "higher_order_field_shift_ppg": 0.0,
        "higher_order_opponent_reference_shift_ppg_by_week": [0.0] * 17,
        "higher_order_scenarios": int(ctx.cfg.get("league_response_cascade_scenarios", 64)),
        "cascade_orders": [],
        "cascade_destinations": [],
        "cascade_pruned_probability_mass": 0.0,
        "cascade_stop_reasons": [],
    })
    pid = _pid(candidate)
    if pid is None or not _ordinary(candidate):
        result["cascade_stop_reasons"].append("NON_PLAYER_CHANNEL_OR_MISSING_ID")
        return result

    max_depth = max(1, int(ctx.cfg.get("league_response_cascade_max_depth", 3)))
    if max_depth < 2:
        result["cascade_stop_reasons"].append("MAX_DEPTH_LT_2")
        return result
    branch_floor = max(0.0, float(ctx.cfg.get("league_response_cascade_branch_probability_floor", 0.02)))
    field_floor = max(0.0, float(ctx.cfg.get("league_response_cascade_field_shift_floor_ppg", 0.001)))
    seed_limit = max(1, int(ctx.cfg.get("league_response_cascade_seed_branches", 3)))
    frontier = max(1, int(ctx.cfg.get("league_response_cascade_claimant_frontier", 4)))
    max_branches = max(1, int(ctx.cfg.get("league_response_cascade_max_branches_per_order", 8)))
    higher_n = max(16, int(ctx.cfg.get("league_response_cascade_scenarios", 64)))
    other_count = max(1, sum(1 for tid in ctx.all_team_rosters if int(tid) != int(ctx.team_id)))
    lookup = _player_lookup(ctx, candidate)

    first_dest = list(first_order.get("destinations") or [])
    first_dest.sort(key=lambda r: float(r.get("winner_probability") or 0.0), reverse=True)
    queue: list[_Branch] = []
    seeded_mass = 0.0
    for row in first_dest[:seed_limit]:
        prob = float(row.get("winner_probability") or 0.0)
        if prob < branch_floor:
            continue
        tid = _finite_int(row.get("team_id"))
        drop_id = _finite_int(row.get("best_drop_espn_id"))
        if drop_id is None:
            drop_id = _finite_int(row.get("drop_espn_id"))
        if tid is None or drop_id is None:
            continue
        dropped = lookup.get(int(drop_id))
        if dropped is None or not _ordinary(dropped):
            continue
        rosters = _clone_rosters(ctx)
        base_roster = rosters.get(int(tid), [])
        rosters[int(tid)] = [dict(p) for p in base_roster if _pid(p) != int(drop_id)] + [dict(candidate)]
        queue.append(_Branch(
            probability=prob,
            released_player=dict(dropped),
            release_week=int(start_week) + 1,
            releaser_team_id=int(tid),
            rosters=rosters,
            path_player_ids=(int(pid), int(drop_id)),
        ))
        seeded_mass += prob

    higher_shift = np.zeros(17, dtype=float)
    cascade_rows: list[dict[str, Any]] = []
    pruned_mass = max(0.0, float(first_order.get("p_claimed") or 0.0) - float(seeded_mass))
    stop_reasons: list[str] = []
    if pruned_mass > 0.0:
        stop_reasons.append("ORDER1_SEED_FRONTIER_OR_BRANCH_FLOOR")
    current_order = 2

    while queue and current_order <= max_depth:
        order_shift = np.zeros(17, dtype=float)
        next_queue: list[_Branch] = []
        order_probability_mass = 0.0
        processed = 0
        for branch in sorted(queue, key=lambda b: b.probability, reverse=True)[:max_branches]:
            if branch.release_week > 17:
                stop_reasons.append("SEASON_BOUNDARY")
                continue
            if branch.probability < branch_floor:
                stop_reasons.append("BRANCH_PROBABILITY_FLOOR")
                continue
            claimant_rows, local_pruned = _authoritative_claimants(
                branch.released_player,
                branch.rosters,
                ctx,
                start_week=branch.release_week,
                scenarios=higher_n,
                exclude_team_ids={int(ctx.team_id), int(branch.releaser_team_id)},
                frontier=frontier,
            )
            pruned_mass += branch.probability * float(local_pruned)
            for row in claimant_rows:
                local_winner = float(row.get("winner_probability") or 0.0)
                absolute_p = branch.probability * local_winner
                if absolute_p <= 0.0:
                    continue
                delta_weekly = np.asarray(row.get("delta_weekly_mean"), dtype=float)
                contribution = (absolute_p / float(other_count)) * delta_weekly
                order_shift += contribution
                order_probability_mass += absolute_p
                processed += 1
                drop_id = _finite_int(row.get("drop_espn_id"))
                cascade_rows.append({
                    "order": int(current_order),
                    "release_week": int(branch.release_week),
                    "candidate_espn_id": _pid(branch.released_player),
                    "candidate_name": branch.released_player.get("name"),
                    "recipient_team_id": int(row["team_id"]),
                    "recipient_team_name": row.get("team_name"),
                    "waiver_rank": int(row.get("waiver_rank") or 10**6),
                    "branch_probability": float(absolute_p),
                    "local_winner_probability": float(local_winner),
                    "claim_probability": float(row.get("claim_probability") or 0.0),
                    "drop_espn_id": drop_id,
                    "drop_name": row.get("drop_name"),
                    "delta_season_ppg": float(row.get("delta_season_ppg") or 0.0),
                })
                if current_order >= max_depth or drop_id is None:
                    continue
                dropped = lookup.get(int(drop_id))
                if dropped is None or not _ordinary(dropped):
                    continue
                if int(drop_id) in branch.path_player_ids:
                    stop_reasons.append("CYCLE_GUARD")
                    continue
                new_rosters = {int(t): [dict(p) for p in rs] for t, rs in branch.rosters.items()}
                tid = int(row["team_id"])
                new_rosters[tid] = [dict(p) for p in new_rosters.get(tid, []) if _pid(p) != int(drop_id)] + [dict(branch.released_player)]
                child = _Branch(
                    probability=float(absolute_p),
                    released_player=dict(dropped),
                    release_week=int(branch.release_week) + 1,
                    releaser_team_id=tid,
                    rosters=new_rosters,
                    path_player_ids=branch.path_player_ids + (int(drop_id),),
                )
                next_queue.append(child)
        order_shift[: max(int(start_week), current_order + int(start_week) - 1) - 1] = 0.0
        higher_shift += order_shift
        order_field = _season_mean_from_vector(order_shift, ctx, max(int(start_week), current_order + int(start_week) - 1))
        result["cascade_orders"].append({
            "order": int(current_order),
            "branches_processed": int(processed),
            "winner_probability_mass": float(order_probability_mass),
            "field_shift_ppg": float(order_field),
        })
        if abs(float(order_field)) < field_floor:
            stop_reasons.append("INCREMENTAL_FIELD_SHIFT_FLOOR")
            break
        next_queue = sorted(next_queue, key=lambda b: b.probability, reverse=True)[:max_branches]
        queue = next_queue
        current_order += 1

    if current_order > max_depth and queue:
        stop_reasons.append("MAX_DEPTH")
    total_shift = first_shift + higher_shift
    total_shift[: int(start_week) - 1] = 0.0
    result["higher_order_opponent_reference_shift_ppg_by_week"] = [float(x) for x in higher_shift]
    result["opponent_reference_shift_ppg_by_week"] = [float(x) for x in total_shift]
    result["higher_order_field_shift_ppg"] = float(_season_mean_from_vector(higher_shift, ctx, int(start_week)))
    result["field_shift_ppg"] = float(_season_mean_from_vector(total_shift, ctx, int(start_week)))
    result["cascade_destinations"] = sorted(cascade_rows, key=lambda r: (int(r["order"]), -float(r["branch_probability"])))
    result["cascade_pruned_probability_mass"] = float(pruned_mass)
    result["cascade_stop_reasons"] = sorted(set(stop_reasons))
    return result
