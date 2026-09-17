from __future__ import annotations

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
from .weekly_manager import find_week_opponent

PLAYER_POSITIONS = {"QB", "RB", "WR", "TE"}
TEMPORAL_INFORMATION_MODEL = "SIMULATED_WEEK_BOUNDARY_ACTIVE_INACTIVE_REVEAL_PROXY_UNCALIBRATED_V033"
PLAYER_MEMBERSHIP_MODEL = "LATEST_SYNCED_PLAYER_MEMBERSHIP_PROPAGATED_TO_ACTIVATION_V033"
CLAIM_RESPONSE_MODEL = "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V031_TEMPORAL_ACTIVATION_WRAPPER_V033"
FUTURE_OPPONENT_MODEL = "CURRENT_MATCHUP_IF_ACTIVATION_NOW_ELSE_FIELD_REFERENCE_V033"
EPS = 1e-12


def _pid(player: dict[str, Any] | None) -> int | None:
    return _finite_int((player or {}).get("espn_id"))


def _ordinary_roster(roster: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(p) for p in roster if str(p.get("position") or "").upper() in PLAYER_POSITIONS]


def _week_weights_from(ctx, start_week: int) -> tuple[np.ndarray, np.ndarray, float]:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float).copy()
    weights[weeks < int(start_week)] = 0.0
    if float(weights.sum()) <= 0.0:
        weights[weeks >= int(start_week)] = 1.0
    norm = max(float(weights.sum()), EPS)
    return np.asarray(weeks, dtype=int), weights, norm


def _active_conditional_mean(player: dict[str, Any], ctx, week: int) -> tuple[float, float]:
    state = ctx.yield_state(player, int(week))
    probability = min(max(float(state.availability_probability), 0.0), 1.0)
    # fixed5 _player_points is the pregame operational yield *conditional on being
    # active*. Availability is a separate Bernoulli coordinate in the predictive MC.
    # Do not divide this conditional yield by p_active a second time.
    conditional = max(float(_player_points(player, ctx, int(week))), 0.0)
    return float(conditional), probability


def _expected_lineup_points(
    roster: list[dict[str, Any]],
    ctx,
    week: int,
    *,
    revealed_active: dict[int, bool] | None = None,
) -> float:
    players = _ordinary_roster(roster)
    scores: dict[int, float] = {}
    active: dict[int, bool] = {}
    for player in players:
        pid = _pid(player)
        if pid is None:
            continue
        conditional, probability = _active_conditional_mean(player, ctx, int(week))
        if revealed_active is not None:
            is_active = bool(revealed_active.get(pid, False)) and conditional > 0.0
            scores[pid] = conditional if is_active else 0.0
            active[pid] = is_active
        else:
            # Before the week-boundary active/inactive coordinate is revealed,
            # decisions use the expectation available at that information boundary.
            expected = conditional * probability
            scores[pid] = expected
            active[pid] = expected > 0.0
    value, _ = _best_lineup_points(players, active, scores, ctx.league, ctx.replacement_season)
    return float(value)


def _legal_release_candidates(ctx, roster: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = []
    source_roster = ctx.roster if roster is None else roster
    for player in _ordinary_roster(source_roster):
        if _pid(player) is None or not _legal_drop(player):
            continue
        rows.append(dict(player))
    rows.sort(key=lambda p: (str(p.get("position") or ""), int(_pid(p) or 10**12), str(p.get("name") or "")))
    return rows


def temporal_release_plan(
    ctx,
    activation_week: int,
    *,
    current_release_id: int | None = None,
    roster: list[dict[str, Any]] | None = None,
    membership_model: str | None = None,
) -> dict[str, Any]:
    """Choose the player-slot release from information available at the activation boundary.

    Current-week activation preserves the commissioned current-state release screen.  A
    future activation uses the existing player-keyed predictive availability uniform as
    an active/inactive state that becomes observable only at that modeled week boundary.
    No realized fantasy-point sample, workload realization, or future-game score is used
    by this selector.  Subsequent weeks enter only through expected player response and
    bye structure.
    """
    week = int(activation_week)
    if week < int(ctx.week) or week > 17:
        raise ValueError("activation_week must be between the current week and week 17")
    source_roster = [dict(p) for p in (ctx.roster if roster is None else roster)]
    membership = str(membership_model or PLAYER_MEMBERSHIP_MODEL)
    candidates = _legal_release_candidates(ctx, source_roster)
    n = int(ctx.predictive_scenarios)
    if not candidates:
        return {
            "activation_week": week,
            "selected_ids": np.full(n, -1, dtype=int),
            "distribution": [],
            "information_model": TEMPORAL_INFORMATION_MODEL,
            "membership_model": membership,
        }

    candidate_ids = [int(_pid(p)) for p in candidates if _pid(p) is not None]
    if week == int(ctx.week) and current_release_id is not None and int(current_release_id) in candidate_ids:
        selected = np.full(n, int(current_release_id), dtype=int)
        distribution = []
        for player in candidates:
            pid = int(_pid(player))
            distribution.append({
                "espn_id": pid,
                "name": player.get("name"),
                "position": player.get("position"),
                "selection_probability": 1.0 if pid == int(current_release_id) else 0.0,
            })
        return {
            "activation_week": week,
            "selected_ids": selected,
            "distribution": distribution,
            "information_model": "COMMISSIONED_CURRENT_STATE_RELEASE_SCREEN_V031",
            "membership_model": membership,
        }

    roster = _ordinary_roster(source_roster)
    # I_w: active/inactive is revealed at the modeled week boundary from the same
    # player-keyed CRN coordinate used by the predictive player MC.  This is an
    # explicitly uncalibrated information proxy, not a forecast of future news.
    active_matrix: dict[int, np.ndarray] = {}
    for player in roster:
        pid = _pid(player)
        if pid is None:
            continue
        conditional, probability = _active_conditional_mean(player, ctx, week)
        if conditional <= 0.0:
            active_matrix[pid] = np.zeros(n, dtype=bool)
        else:
            uniforms = np.asarray(ctx.predictive_uniforms(pid), dtype=float)
            active_matrix[pid] = uniforms[:n, week - 1] < probability

    _weeks, weights, norm = _week_weights_from(ctx, week)
    future_constant: dict[int, float] = {}
    baseline_future = 0.0
    for later in range(week + 1, 18):
        w = float(weights[later - 1])
        if w <= 0.0:
            continue
        base_value = _expected_lineup_points(roster, ctx, later)
        baseline_future += w * base_value
        for player in candidates:
            pid = int(_pid(player))
            if pid not in future_constant:
                future_constant[pid] = 0.0
            trial = [p for p in roster if _pid(p) != pid]
            future_constant[pid] += w * _expected_lineup_points(trial, ctx, later)

    costs = np.zeros((len(candidates), n), dtype=float)
    activation_weight = float(weights[week - 1])
    for scenario in range(n):
        reveal = {pid: bool(arr[scenario]) for pid, arr in active_matrix.items()}
        baseline = activation_weight * _expected_lineup_points(roster, ctx, week, revealed_active=reveal) + baseline_future
        for idx, player in enumerate(candidates):
            pid = int(_pid(player))
            trial = [p for p in roster if _pid(p) != pid]
            trial_value = activation_weight * _expected_lineup_points(trial, ctx, week, revealed_active=reveal)
            trial_value += future_constant.get(pid, 0.0)
            costs[idx, scenario] = (baseline - trial_value) / norm

    # Candidate ordering is deterministic, so argmin tie-breaking is reproducible.
    choice = np.argmin(costs, axis=0)
    selected = np.asarray([int(_pid(candidates[int(i)])) for i in choice], dtype=int)
    distribution = []
    for idx, player in enumerate(candidates):
        pid = int(_pid(player))
        distribution.append({
            "espn_id": pid,
            "name": player.get("name"),
            "position": player.get("position"),
            "selection_probability": float(np.mean(selected == pid)),
            "mean_expected_lineup_cost_ppg": float(np.mean(costs[idx])),
        })
    distribution.sort(key=lambda row: (-float(row["selection_probability"]), float(row.get("mean_expected_lineup_cost_ppg") or 0.0), int(row["espn_id"])))
    return {
        "activation_week": week,
        "selected_ids": selected,
        "distribution": distribution,
        "information_model": TEMPORAL_INFORMATION_MODEL,
        "membership_model": membership,
    }


def release_plan_summary(plan: dict[str, Any], player_lookup: dict[int, dict[str, Any]]) -> dict[str, Any] | None:
    distribution = [dict(row) for row in plan.get("distribution") or [] if float(row.get("selection_probability") or 0.0) > 0.0]
    if not distribution:
        return None
    dominant = distribution[0]
    pid = int(dominant["espn_id"])
    player = player_lookup.get(pid) or {}
    return {
        "espn_id": pid,
        "name": player.get("name") or dominant.get("name"),
        "position": player.get("position") or dominant.get("position"),
        "selection_probability": float(dominant.get("selection_probability") or 0.0),
        "selection_distribution": distribution,
        "activation_week": int(plan.get("activation_week") or 0),
        "method": "TEMPORAL_PLAYER_SLOT_RELEASE_V033",
        "information_model": plan.get("information_model"),
        "membership_model": plan.get("membership_model"),
    }


def compose_temporal_release_weekly(
    base_weekly: np.ndarray,
    release_weekly_by_id: dict[int, np.ndarray],
    selected_ids: np.ndarray,
    activation_week: int,
) -> np.ndarray:
    base = np.asarray(base_weekly, dtype=float)
    out = base.copy()
    selected = np.asarray(selected_ids, dtype=int)
    if len(selected) != base.shape[0]:
        raise ValueError("selected_ids must have one entry per predictive scenario")
    week = int(activation_week)
    for pid in np.unique(selected):
        if int(pid) < 0:
            continue
        release = release_weekly_by_id.get(int(pid))
        if release is None:
            raise KeyError(f"missing release weekly samples for ESPN id {int(pid)}")
        mask = selected == int(pid)
        out[mask, week - 1:] = np.asarray(release, dtype=float)[mask, week - 1:]
    return out


def compose_temporal_release_shift(
    selected_ids: np.ndarray,
    response_by_id: dict[int, dict[str, Any]],
    activation_week: int,
    scenarios: int,
) -> np.ndarray:
    selected = np.asarray(selected_ids, dtype=int)
    if len(selected) != int(scenarios):
        raise ValueError("selected_ids must have one entry per predictive scenario")
    out = np.zeros((int(scenarios), 17), dtype=float)
    week = int(activation_week)
    for pid in np.unique(selected):
        if int(pid) < 0:
            continue
        response = response_by_id.get(int(pid)) or {}
        shift = np.asarray(response.get("opponent_reference_shift_ppg_by_week") or np.zeros(17), dtype=float)
        shift[: week - 1] = 0.0
        out[selected == int(pid), :] = shift[None, :]
    return out


def _temporal_roster_score(roster: list[dict[str, Any]], ctx, start_week: int) -> tuple[float, float]:
    weekly = np.zeros(17, dtype=float)
    players = _ordinary_roster(roster)
    for week in range(int(start_week), 18):
        weekly[week - 1] = _expected_lineup_points(players, ctx, week)
    _weeks, weights, norm = _week_weights_from(ctx, int(start_week))
    return float(np.sum(weekly * weights) / norm), float(weekly[int(start_week) - 1])


def _temporal_manager_interest(candidate: dict[str, Any], roster: list[dict[str, Any]], ctx, start_week: int) -> dict[str, Any]:
    baseline_season, baseline_week = _temporal_roster_score(roster, ctx, start_week)
    best = None
    best_score = -float("inf")
    for drop in roster:
        if str(drop.get("position") or "").upper() not in PLAYER_POSITIONS:
            continue
        if not _legal_drop(drop):
            continue
        if not _legal_roster_after_add_drop(roster, candidate, drop, ctx.league):
            continue
        drop_id = _pid(drop)
        new_roster = [p for p in roster if _pid(p) != drop_id] + [dict(candidate)]
        season_score, week_score = _temporal_roster_score(new_roster, ctx, start_week)
        if season_score > best_score:
            best_score = season_score
            best = (drop, new_roster, season_score, week_score)
    if best is None:
        return {
            "legal": False,
            "drop_espn_id": None,
            "drop_name": None,
            "delta_season_ppg": -99.0,
            "delta_current_week": -99.0,
            "new_roster": None,
        }
    drop, new_roster, season_score, week_score = best
    return {
        "legal": True,
        "drop_espn_id": _pid(drop),
        "drop_name": drop.get("name"),
        "delta_season_ppg": float(season_score - baseline_season),
        # Behavioral kernel field name is retained, but this coordinate refers to
        # the activation week rather than the snapshot's current week.
        "delta_current_week": float(week_score - baseline_week),
        "new_roster": new_roster,
    }


def temporal_released_player_response(
    candidate: dict[str, Any],
    ctx,
    *,
    activation_week: int,
    scenarios: int | None = None,
) -> dict[str, Any]:
    """Recompute fixed6-style released-player response at a future activation state.

    The football response remains the commissioned predictive player generator under
    common random numbers.  Only the state at which recipient interest and before/after
    deltas are evaluated changes from the frozen current week to ``activation_week``.
    """
    start_week = int(activation_week)
    response_n = int(scenarios or ctx.cfg.get("league_state_response_scenarios", 256))
    old_n = int(ctx.predictive_scenarios)
    candidates = []
    try:
        ctx.set_predictive_scenarios(max(64, response_n))
        for team in ctx.espn.get("teams") or []:
            tid = _finite_int(team.get("team_id"))
            if tid is None or int(tid) == int(ctx.team_id):
                continue
            roster = list(ctx.all_team_rosters.get(int(tid)) or [])
            interest = _temporal_manager_interest(candidate, roster, ctx, start_week)
            if not bool(interest.get("legal")):
                continue
            new_roster = list(interest.pop("new_roster") or [])
            before = _simulate_predictive_weekly_points(
                roster, ctx, ctx.replacement_current, ctx.replacement_season,
                current_week_policy="realistic", progress_label="v0.33 release recipient before",
            )
            after = _simulate_predictive_weekly_points(
                new_roster, ctx, ctx.replacement_current, ctx.replacement_season,
                current_week_policy="realistic", progress_label="v0.33 release recipient after",
            )
            delta_weekly = np.asarray(after, dtype=float) - np.asarray(before, dtype=float)
            delta_weekly[:, : start_week - 1] = 0.0
            _weeks, weights, norm = _week_weights_from(ctx, start_week)
            delta_season = np.sum(delta_weekly * weights[None, :], axis=1) / norm
            authoritative_interest = dict(interest)
            authoritative_interest["delta_season_ppg"] = float(np.mean(delta_season))
            authoritative_interest["delta_current_week"] = float(np.mean(delta_weekly[:, start_week - 1]))
            p_claim = _release_claim_probability(candidate, roster, authoritative_interest, ctx)
            try:
                waiver = int(team.get("waiver_rank"))
            except (TypeError, ValueError):
                waiver = 10**6
            candidates.append({
                "team_id": int(tid),
                "team_name": team.get("team_name") or team.get("name"),
                "waiver_rank": waiver,
                "claim_probability": float(p_claim),
                "drop_espn_id": authoritative_interest.get("drop_espn_id"),
                "drop_name": authoritative_interest.get("drop_name"),
                "delta_season_ppg": float(authoritative_interest["delta_season_ppg"]),
                "delta_activation_week": float(authoritative_interest["delta_current_week"]),
                "delta_weekly_mean": np.mean(delta_weekly, axis=0),
            })
    finally:
        if int(ctx.predictive_scenarios) != old_n:
            ctx.set_predictive_scenarios(old_n)

    candidates.sort(key=lambda row: (int(row["waiver_rank"]), int(row["team_id"])))
    survival = 1.0
    destinations = []
    other_count = max(1, len([tid for tid in ctx.all_team_rosters if int(tid) != int(ctx.team_id)]))
    field_shift = np.zeros(17, dtype=float)
    expected_gain = 0.0
    for row in candidates:
        p_local = min(max(float(row["claim_probability"]), 0.0), 1.0)
        winner = survival * p_local
        survival *= 1.0 - p_local
        delta_weekly_mean = np.asarray(row.pop("delta_weekly_mean"), dtype=float)
        field_shift += (winner / other_count) * delta_weekly_mean
        expected_gain += winner * float(row["delta_season_ppg"])
        row["winner_probability"] = float(winner)
        destinations.append(row)
    p_claimed = float(1.0 - survival)
    field_shift[: start_week - 1] = 0.0
    reference_shift = field_shift.copy()
    current_opp_shift = 0.0
    opponent_model = FUTURE_OPPONENT_MODEL
    if start_week == int(ctx.week):
        actual = find_week_opponent(ctx.snapshot, int(ctx.team_id))
        if actual is not None:
            actual_row = next((row for row in destinations if int(row["team_id"]) == int(actual)), None)
            if actual_row is not None:
                current_opp_shift = float(actual_row["winner_probability"] * actual_row["delta_activation_week"])
                reference_shift[start_week - 1] = current_opp_shift
    _weeks, weights, norm = _week_weights_from(ctx, start_week)
    first_order = {
        "model": CLAIM_RESPONSE_MODEL,
        "activation_week": start_week,
        "information_model": TEMPORAL_INFORMATION_MODEL,
        "player_membership_model": PLAYER_MEMBERSHIP_MODEL,
        "opponent_reference_model": opponent_model,
        "waiver_order_model": "CURRENT_ESPN_WAIVER_PRIORITY_PROXY_UNCALIBRATED_V033",
        "scenarios": int(response_n),
        "p_claimed": p_claimed,
        "expected_recipient_gain_ppg": float(expected_gain),
        "field_shift_ppg": float(np.sum(field_shift * weights) / norm),
        "current_opponent_shift_ppg": float(current_opp_shift),
        "opponent_reference_shift_ppg_by_week": [float(x) for x in reference_shift],
        "destinations": destinations,
    }
    from .league_response_v036 import extend_release_response
    result = extend_release_response(candidate, ctx, first_order, start_week=start_week)
    result["activation_week"] = start_week
    result["information_model"] = TEMPORAL_INFORMATION_MODEL
    result["player_membership_model"] = PLAYER_MEMBERSHIP_MODEL
    result["opponent_reference_model"] = opponent_model
    result["waiver_order_model"] = "CURRENT_ESPN_WAIVER_PRIORITY_PROXY_UNCALIBRATED_V033"
    return result
