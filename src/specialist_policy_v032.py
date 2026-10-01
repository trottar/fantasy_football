from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .observability.dst_shadow import shadow_dst_call
from .observability.k_shadow import shadow_k_call

from .season_utility import week_weights
from .specialist_channels import (
    _best_player_slot_release,
    _is_current_week_locked,
    _specialist_week_samples,
    evaluate_defense_channel as _evaluate_defense_static,
    evaluate_kicker_channel as _evaluate_kicker_static,
    save_channel_report,
)
from .transaction_manager import (
    UtilityContext,
    _classify_paired_delta,
    _finite_int,
    _legal_drop,
    _paired_mean_interval,
    _scenario_h2h_utility_against,
    evaluate_roster_predictive,
    released_player_league_state_response,
    waiver_acquisition_probability,
    waiver_blocker_diagnostics,
)
from .weekly_manager import find_week_opponent, resolve_team
from .specialist_temporal_v033 import (
    CLAIM_RESPONSE_MODEL,
    PLAYER_MEMBERSHIP_MODEL,
    TEMPORAL_INFORMATION_MODEL,
    compose_temporal_release_shift,
    compose_temporal_release_weekly,
    release_plan_summary,
    temporal_release_plan,
    temporal_released_player_response,
)
from .player_temporal_state_v035 import (
    EXTERNAL_PLAYER_MARKET_MODEL,
    PLAYER_INFORMATION_POLICY,
    PLAYER_STATE_MODEL,
    PLAYER_TRANSACTION_MODEL,
    STATE_COMPOSITION_ORDER,
    build_temporal_player_states,
    state_for_week,
    summarize_temporal_player_states,
)

POLICY_MODEL = "DETERMINISTIC_SAME_CHANNEL_BEST_RESPONSE_V032"
ORDER_MODEL = "FROZEN_CURRENT_ESPN_WAIVER_PRIORITY_PROXY_UNCALIBRATED_V032"
POOL_MODEL = "CURRENT_FREEAGENTS_PLUS_NEXT_WEEK_RELEASES_V032"
EPS = 1e-12


@dataclass
class SpecialistPolicyResult:
    position: str
    mode: str
    user_capacity: int
    team_weekly: dict[int, np.ndarray]
    user_plan: list[dict[str, Any]]
    transactions: list[dict[str, Any]]
    guaranteed_free_agents_initial: int
    excluded_current_waivers: int
    pre_acquired_espn_id: int | None = None
    activation_week: int | None = None
    market_states: list[dict[str, Any]] = field(default_factory=list)

    @property
    def user_weekly(self) -> np.ndarray:
        if not self.team_weekly:
            return np.zeros((0, 17), dtype=float)
        first = next(iter(self.team_weekly.values()))
        return np.asarray(self.team_weekly.get(-1, np.zeros_like(first)), dtype=float)


def _pid(player: dict[str, Any] | None) -> int | None:
    return _finite_int((player or {}).get("espn_id"))


def _team_id(team: dict[str, Any]) -> int | None:
    return _finite_int(team.get("team_id"))


def _position_rows(rows, position: str) -> list[dict[str, Any]]:
    return [dict(p) for p in rows if str(p.get("position") or "").upper() == position]


def _is_bench(player: dict[str, Any]) -> bool:
    slot = str(player.get("lineup_slot") or "").strip().upper()
    return slot in {"", "BENCH", "BE", "IR", "RESERVE"}


def _guaranteed_free_pool(ctx: UtilityContext, position: str) -> tuple[dict[int, dict[str, Any]], int]:
    free: dict[int, dict[str, Any]] = {}
    waivers = 0
    for player in ctx.actionable_available:
        if str(player.get("position") or "").upper() != position:
            continue
        raw = str(player.get("fantasy_status") or "").upper()
        pid = _pid(player)
        if pid is None:
            continue
        if raw == "FREEAGENT":
            free[pid] = dict(player)
        elif raw in {"WAIVER", "WAIVERS"}:
            waivers += 1
    return free, waivers


def _manager_order(ctx: UtilityContext) -> list[int]:
    rows = []
    for team in ctx.espn.get("teams") or []:
        tid = _team_id(team)
        if tid is None or tid not in ctx.all_team_rosters:
            continue
        try:
            waiver = int(team.get("waiver_rank"))
        except (TypeError, ValueError):
            waiver = 10**6
        rows.append((waiver, tid))
    rows.sort(key=lambda x: (x[0], x[1]))
    return [tid for _, tid in rows]


def _cache_week(player: dict[str, Any], ctx: UtilityContext, week: int, cache: dict) -> tuple[np.ndarray, float, dict[str, Any]]:
    key = (_pid(player), int(week), int(ctx.predictive_scenarios))
    if key not in cache:
        cache[key] = _specialist_week_samples(player, ctx, int(week))
    samples, mean, detail = cache[key]
    return np.asarray(samples, dtype=float), float(mean), dict(detail)


def _locked_starter(portfolio: list[dict[str, Any]], ctx: UtilityContext, week: int, cache: dict):
    if int(week) != int(ctx.week):
        return None
    for player in portfolio:
        if not _is_bench(player) and _is_current_week_locked(player, ctx):
            samples, mean, detail = _cache_week(player, ctx, week, cache)
            return player, samples, mean, detail
    return None


def _best_choice(portfolio: list[dict[str, Any]], ctx: UtilityContext, week: int, cache: dict):
    locked = _locked_starter(portfolio, ctx, week, cache)
    if locked is not None:
        return locked
    choices = []
    for player in portfolio:
        samples, mean, detail = _cache_week(player, ctx, week, cache)
        choices.append((player, samples, mean, detail))
    if not choices:
        n = int(ctx.predictive_scenarios)
        return None, np.zeros(n, dtype=float), 0.0, {"opponent": None, "source": "EMPTY_SPECIALIST_SLOT"}
    return max(choices, key=lambda row: float(row[2]))


def _best_free(free: dict[int, dict[str, Any]], ctx: UtilityContext, week: int, cache: dict):
    choices = []
    for player in free.values():
        if int(week) == int(ctx.week) and _is_current_week_locked(player, ctx):
            continue
        samples, mean, detail = _cache_week(player, ctx, week, cache)
        choices.append((player, samples, mean, detail))
    return max(choices, key=lambda row: float(row[2])) if choices else None


def _worst_owned(portfolio: list[dict[str, Any]], ctx: UtilityContext, week: int, cache: dict):
    unlocked = []
    for player in portfolio:
        if int(week) == int(ctx.week) and (_is_current_week_locked(player, ctx) or not _legal_drop(player)):
            continue
        samples, mean, detail = _cache_week(player, ctx, week, cache)
        unlocked.append((player, samples, mean, detail))
    return min(unlocked, key=lambda row: float(row[2])) if unlocked else None


def _initial_portfolios(ctx: UtilityContext, position: str) -> dict[int, list[dict[str, Any]]]:
    return {
        int(tid): _position_rows(roster, position)
        for tid, roster in ctx.all_team_rosters.items()
    }


def _record_plan(player, mean: float, detail: dict[str, Any], week: int, transaction: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "week": int(week),
        "starter_espn_id": _pid(player),
        "starter_name": (player or {}).get("name"),
        "starter_team": (player or {}).get("nfl_team"),
        "expected_points": float(mean),
        "opponent": detail.get("opponent"),
        "source": detail.get("source"),
        "transaction": transaction,
    }


def simulate_specialist_market_policy(
    ctx: UtilityContext,
    *,
    position: str,
    user_mode: str,
    pre_acquire_espn_id: int | None = None,
    pre_drop_espn_id: int | None = None,
    pre_acquire_from_waivers: bool = False,
    activation_week: int | None = None,
) -> SpecialistPolicyResult:
    """Propagate a specialist-only league state with deterministic pre-lock best responses.

    No realized MC outcome affects a transaction or starter choice.  Today's guaranteed
    FREEAGENT pool is the initial market.  A dropped specialist becomes eligible only
    in the following modeled week.  The current ESPN waiver order is frozen solely as
    an ordering proxy for future simultaneous demand; this behavioral assumption is
    explicit and uncalibrated.
    """
    position = str(position).upper()
    if position not in {"DST", "K"}:
        raise ValueError("position must be DST or K")
    user_mode = str(user_mode).upper()
    if user_mode not in {"HOLD", "ONE_SLOT", "CARRY2"}:
        raise ValueError("user_mode must be HOLD, ONE_SLOT, or CARRY2")
    if position == "K" and user_mode == "CARRY2":
        raise ValueError("two-kicker policy is disabled")

    n = int(ctx.predictive_scenarios)
    portfolios = _initial_portfolios(ctx, position)
    portfolios.setdefault(int(ctx.team_id), _position_rows(ctx.roster, position))
    free, excluded_waivers = _guaranteed_free_pool(ctx, position)
    initial_free = len(free)
    cache: dict = {}
    order = _manager_order(ctx)
    user_id = int(ctx.team_id)
    capacity = 2 if user_mode == "CARRY2" else 1
    if user_mode == "CARRY2":
        activation_week = int(ctx.week if activation_week is None else activation_week)
        if activation_week < int(ctx.week) or activation_week > 17:
            raise ValueError("activation_week must be between the current week and week 17")
    else:
        activation_week = None

    pre_transaction: dict[str, Any] | None = None
    pre_released: dict[int, dict[str, Any]] = {}
    if pre_acquire_espn_id is not None:
        if user_mode == "HOLD":
            raise ValueError("pre-acquisition is incompatible with HOLD")
        if user_mode == "CARRY2" and int(activation_week) != int(ctx.week):
            raise ValueError("pre-acquisition is only valid for current-week CARRY2")
        pre_id = int(pre_acquire_espn_id)
        candidate = free.pop(pre_id, None)
        acquisition_state = "FREEAGENT"
        if candidate is None and pre_acquire_from_waivers:
            candidate = next((
                dict(player) for player in ctx.actionable_available
                if _pid(player) == pre_id
                and str(player.get("position") or "").upper() == position
                and str(player.get("fantasy_status") or "").upper() in {"WAIVER", "WAIVERS"}
            ), None)
            acquisition_state = "WAIVERS"
        if candidate is None:
            expected = "current WAIVERS candidate" if pre_acquire_from_waivers else "unlocked current FREEAGENT"
            raise ValueError(f"pre-acquired specialist must be an {expected}")
        if _is_current_week_locked(candidate, ctx):
            raise ValueError("pre-acquired specialist is already locked")

        portfolio = list(portfolios.get(user_id) or [])
        drop_player = None
        if pre_drop_espn_id is not None:
            drop_id = int(pre_drop_espn_id)
            drop_player = next((player for player in portfolio if _pid(player) == drop_id), None)
            if drop_player is None:
                raise ValueError("pre-acquisition drop specialist is not on the user roster")
            if _is_current_week_locked(drop_player, ctx) or not _legal_drop(drop_player):
                raise ValueError("pre-acquisition drop specialist is locked or not droppable")
            portfolio = [player for player in portfolio if _pid(player) != drop_id]
            pre_released[drop_id] = drop_player

        if user_mode == "ONE_SLOT" and pre_drop_espn_id is None and portfolio:
            raise ValueError("ONE_SLOT pre-acquisition requires an explicit legal specialist drop")
        if user_mode == "CARRY2" and len(portfolio) >= 2:
            raise ValueError("CARRY2 pre-acquisition exceeds specialist capacity")
        portfolio.append(candidate)
        portfolios[user_id] = portfolio
        pre_transaction = {
            "week": int(ctx.week),
            "team_id": int(user_id),
            "action": "ADD" if drop_player is None else "SWAP",
            "add": candidate.get("name"),
            "add_espn_id": pre_id,
            "drop": (drop_player or {}).get("name"),
            "drop_espn_id": _pid(drop_player),
            "expected_gain": None,
            "acquisition_state": acquisition_state,
            "conditional_acquisition": True,
        }

    team_weekly = {tid: np.zeros((n, 17), dtype=float) for tid in portfolios}
    # Convenience alias used by callers/tests without needing user id metadata.
    team_weekly[-1] = np.zeros((n, 17), dtype=float)
    user_plan: list[dict[str, Any]] = []
    transactions: list[dict[str, Any]] = [pre_transaction] if pre_transaction is not None else []
    market_states: list[dict[str, Any]] = []

    for week in range(max(1, int(ctx.week)), 18):
        dropped_next: dict[int, dict[str, Any]] = {}
        if week == int(ctx.week) and pre_released:
            dropped_next.update(pre_released)
        free_before = sorted(int(pid) for pid in free)
        ownership_before = {
            str(tid): sorted(int(pid) for p in roster if (pid := _pid(p)) is not None)
            for tid, roster in portfolios.items()
        }
        if week == int(ctx.week):
            week_order = [user_id] + [tid for tid in order if tid != user_id]
        else:
            week_order = list(order)
            if user_id not in week_order:
                week_order.append(user_id)

        for tid in week_order:
            portfolio = list(portfolios.get(tid) or [])
            is_user = tid == user_id
            manager_capacity = (
                2 if is_user and user_mode == "CARRY2" and int(week) >= int(activation_week)
                else 1
            )
            transaction = None

            # The pre-acquisition is itself the current user decision.  Do not allow a
            # second same-week user acquisition on top of that state perturbation.
            can_manage = not (is_user and user_mode == "HOLD")
            if is_user and week == int(ctx.week) and pre_acquire_espn_id is not None:
                can_manage = False
            if _locked_starter(portfolio, ctx, week, cache) is not None:
                can_manage = False

            if can_manage:
                best_free = _best_free(free, ctx, week, cache)
                if best_free is not None:
                    add_player, _add_samples, add_mean, _add_detail = best_free
                    add_id = _pid(add_player)
                    if len(portfolio) < manager_capacity:
                        if add_mean > EPS and add_id is not None:
                            portfolio.append(free.pop(add_id))
                            transaction = {
                                "action": "ADD", "add": add_player.get("name"),
                                "add_espn_id": add_id, "drop": None, "drop_espn_id": None,
                                "expected_gain": float(add_mean),
                            }
                    else:
                        worst = _worst_owned(portfolio, ctx, week, cache)
                        if worst is not None:
                            drop_player, _drop_samples, drop_mean, _drop_detail = worst
                            drop_id = _pid(drop_player)
                            if add_mean > float(drop_mean) + EPS and add_id is not None and drop_id is not None:
                                portfolio = [p for p in portfolio if _pid(p) != drop_id]
                                portfolio.append(free.pop(add_id))
                                dropped_next[drop_id] = drop_player
                                transaction = {
                                    "action": "SWAP",
                                    "add": add_player.get("name"),
                                    "add_espn_id": add_id,
                                    "drop": drop_player.get("name"),
                                    "drop_espn_id": drop_id,
                                    "expected_gain": float(add_mean - drop_mean),
                                }

            portfolios[tid] = portfolio
            if transaction is not None:
                transactions.append({"week": int(week), "team_id": int(tid), **transaction})

        # After every manager has acted, choose starters from pregame means and only
        # then attach realized MC samples.  This is the no-hindsight boundary.
        for tid, portfolio in portfolios.items():
            player, samples, mean, detail = _best_choice(portfolio, ctx, week, cache)
            team_weekly.setdefault(tid, np.zeros((n, 17), dtype=float))[:, week - 1] = samples
            if tid == user_id:
                tx = next((t for t in transactions if t["week"] == week and t["team_id"] == user_id), None)
                user_plan.append(_record_plan(player, mean, detail, week, tx))
                team_weekly[-1][:, week - 1] = samples

        # Releases are not available to a second manager in the same modeled week.
        free.update(dropped_next)
        market_states.append({
            "week": int(week),
            "free_agent_ids_before": free_before,
            "ownership_before": ownership_before,
            "released_after_week": sorted(int(pid) for pid in dropped_next),
            "free_agent_ids_after": sorted(int(pid) for pid in free),
            "ownership_after": {
                str(tid): sorted(int(pid) for p in roster if (pid := _pid(p)) is not None)
                for tid, roster in portfolios.items()
            },
        })

    return SpecialistPolicyResult(
        position=position,
        mode=user_mode,
        user_capacity=capacity,
        team_weekly=team_weekly,
        user_plan=user_plan,
        transactions=transactions,
        guaranteed_free_agents_initial=initial_free,
        excluded_current_waivers=excluded_waivers,
        pre_acquired_espn_id=int(pre_acquire_espn_id) if pre_acquire_espn_id is not None else None,
        activation_week=int(activation_week) if activation_week is not None else None,
        market_states=market_states,
    )


def _static_team_weekly(ctx: UtilityContext, position: str) -> dict[int, np.ndarray]:
    n = int(ctx.predictive_scenarios)
    cache: dict = {}
    out: dict[int, np.ndarray] = {}
    for tid, roster in ctx.all_team_rosters.items():
        portfolio = _position_rows(roster, position)
        arr = np.zeros((n, 17), dtype=float)
        for week in range(max(1, int(ctx.week)), 18):
            _player, samples, _mean, _detail = _best_choice(portfolio, ctx, week, cache)
            arr[:, week - 1] = samples
        out[int(tid)] = arr
    if int(ctx.team_id) not in out:
        portfolio = _position_rows(ctx.roster, position)
        arr = np.zeros((n, 17), dtype=float)
        for week in range(max(1, int(ctx.week)), 18):
            _player, samples, _mean, _detail = _best_choice(portfolio, ctx, week, cache)
            arr[:, week - 1] = samples
        out[int(ctx.team_id)] = arr
    return out


def _field_delta(policy: SpecialistPolicyResult, static: dict[int, np.ndarray], ctx: UtilityContext) -> np.ndarray:
    n = int(ctx.predictive_scenarios)
    deltas = []
    actual_id = find_week_opponent(ctx.snapshot, int(ctx.team_id))
    actual_current = None
    for tid, base in static.items():
        if int(tid) == int(ctx.team_id):
            continue
        after = policy.team_weekly.get(int(tid))
        if after is None:
            continue
        delta = np.asarray(after, dtype=float) - np.asarray(base, dtype=float)
        deltas.append(delta)
        if actual_id is not None and int(tid) == int(actual_id):
            actual_current = np.asarray(delta[:, int(ctx.week) - 1], dtype=float).copy()
    field = np.mean(np.stack(deltas, axis=0), axis=0) if deltas else np.zeros((n, 17), dtype=float)
    if actual_current is not None:
        field[:, int(ctx.week) - 1] = actual_current
    return field


def _weighted_summary(samples: np.ndarray, ctx: UtilityContext) -> dict[str, float]:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < int(ctx.week)] = 0.0
    if float(weights.sum()) <= 0.0:
        weights[weeks >= int(ctx.week)] = 1.0
    norm = max(float(weights.sum()), EPS)
    season = np.sum(np.asarray(samples, dtype=float) * weights[None, :], axis=1) / norm
    current = np.asarray(samples, dtype=float)[:, int(ctx.week) - 1]
    return {
        "weighted_mean_ppg": float(np.mean(season)),
        "weighted_sd_ppg": float(np.std(season, ddof=1)) if len(season) > 1 else 0.0,
        "current_week_mean": float(np.mean(current)),
        "current_week_sd": float(np.std(current, ddof=1)) if len(current) > 1 else 0.0,
    }


def _paired_stats(delta: np.ndarray, ctx: UtilityContext, seed_salt: int) -> dict[str, Any]:
    arr = np.asarray(delta, dtype=float)
    p16, p84 = _paired_mean_interval(
        arr,
        seed=int(ctx.seed) + int(seed_salt),
        draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)),
    )
    eps = 1e-12
    return {
        "mean": float(np.mean(arr)) if len(arr) else 0.0,
        "mean_p16": float(p16),
        "mean_p84": float(p84),
        "p_better": float(np.mean(arr > eps)) if len(arr) else 0.0,
        "p_tie": float(np.mean(np.abs(arr) <= eps)) if len(arr) else 1.0,
        "p_worse": float(np.mean(arr < -eps)) if len(arr) else 0.0,
        "classification": _classify_paired_delta(arr, ctx.cfg, mean_p16=p16),
    }


def _compose_state(
    base_weekly: np.ndarray,
    base_opponent: np.ndarray,
    ctx: UtilityContext,
    *,
    d_policy: SpecialistPolicyResult,
    k_policy: SpecialistPolicyResult,
    d_static: dict[int, np.ndarray],
    k_static: dict[int, np.ndarray],
    extra_opponent_shift_by_week: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    uid = int(ctx.team_id)
    weekly = np.asarray(base_weekly, dtype=float).copy()
    weekly += np.asarray(d_policy.team_weekly[uid] - d_static[uid], dtype=float)
    weekly += np.asarray(k_policy.team_weekly[uid] - k_static[uid], dtype=float)
    opponent = np.asarray(base_opponent, dtype=float).copy()
    opponent += _field_delta(d_policy, d_static, ctx)
    opponent += _field_delta(k_policy, k_static, ctx)
    if extra_opponent_shift_by_week is not None:
        shift = np.asarray(extra_opponent_shift_by_week, dtype=float)
        if shift.ndim == 1:
            if shift.shape[0] != 17:
                raise ValueError("opponent shift must contain 17 weeks")
            shift = shift.reshape(1, 17)
        elif shift.ndim == 2:
            if shift.shape[1] != 17 or shift.shape[0] not in {1, opponent.shape[0]}:
                raise ValueError("scenario-conditioned opponent shift must be Nx17")
        else:
            raise ValueError("opponent shift must be a 17-vector or Nx17 matrix")
        opponent += shift
    utility = _scenario_h2h_utility_against(weekly, opponent, ctx)
    return weekly, opponent, utility


def _build_context(snapshot, league, model, values_path, team_name, team_id, mc_scenarios):
    team = resolve_team(snapshot, team_name=team_name, team_id=team_id)
    local_model = json.loads(json.dumps(model))
    ctx = UtilityContext(snapshot, league, local_model, values_path, team)
    cfg = local_model.get("specialist_channels") or {}
    n = int(mc_scenarios or cfg.get("mc_scenarios", 2048))
    ctx.set_predictive_scenarios(max(64, n))
    return ctx


def _policy_block(policy: SpecialistPolicyResult, ctx: UtilityContext, static: dict[int, np.ndarray]) -> dict[str, Any]:
    uid = int(ctx.team_id)
    summary = _weighted_summary(policy.team_weekly[uid], ctx)
    base_summary = _weighted_summary(static[uid], ctx)
    current_tx = next((t for t in policy.transactions if t["team_id"] == uid and t["week"] == int(ctx.week)), None)
    return {
        **summary,
        "delta_vs_static_ppg": float(summary["weighted_mean_ppg"] - base_summary["weighted_mean_ppg"]),
        "current_action": current_tx or {"action": "HOLD"},
        "weekly_plan": policy.user_plan,
        "market_model": POLICY_MODEL,
        "transaction_order_model": ORDER_MODEL,
        "pool_model": POOL_MODEL,
        "guaranteed_free_agents_initial": policy.guaranteed_free_agents_initial,
        "excluded_current_waivers": policy.excluded_current_waivers,
        "market_states": policy.market_states,
    }


def _timed_release_state(
    base_weekly: np.ndarray,
    release_weekly: np.ndarray,
    release_shift: np.ndarray,
    activation_week: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply the player-slot release only from the second-DST activation week onward."""
    week = int(activation_week)
    weekly = np.asarray(base_weekly, dtype=float).copy()
    weekly[:, week - 1:] = np.asarray(release_weekly, dtype=float)[:, week - 1:]
    shift = np.asarray(release_shift, dtype=float).copy()
    shift[: week - 1] = 0.0
    return weekly, shift


def _user_transaction_for_week(policy: SpecialistPolicyResult, team_id: int, week: int) -> dict[str, Any] | None:
    return next(
        (t for t in policy.transactions if int(t.get("team_id") or -1) == int(team_id) and int(t.get("week") or -1) == int(week)),
        None,
    )


def _player_roster_key(roster: list[dict[str, Any]]) -> tuple[int, ...]:
    return tuple(sorted(
        int(pid)
        for player in roster
        if (pid := _pid(player)) is not None
    ))


def _predictive_player_roster_cached(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    cache: dict[tuple[int, ...], np.ndarray],
    *,
    label: str,
) -> np.ndarray:
    key = _player_roster_key(roster)
    if key not in cache:
        _result, _utility, weekly = evaluate_roster_predictive(
            roster, ctx, include_diagnostics=False, progress_label=label
        )
        cache[key] = np.asarray(weekly, dtype=float)
    return np.asarray(cache[key], dtype=float)


def _temporal_player_baseline_to_activation(
    base_weekly: np.ndarray,
    player_states: dict[int, Any],
    activation_week: int,
    ctx: UtilityContext,
    roster_weekly_cache: dict[tuple[int, ...], np.ndarray],
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Evolve P_w causally to activation, then freeze it for the local perturbation.

    This is the v0.35 first-order expansion point.  Ordinary-player policy transitions
    before activation are retained; after activation the local player state is frozen
    so the second-DST response is not contaminated by higher-order post-perturbation
    player-market reactions reserved for v0.36.
    """
    week0 = max(1, int(ctx.week))
    activation = int(activation_week)
    out = np.asarray(base_weekly, dtype=float).copy()
    path: list[dict[str, Any]] = []
    for week in range(week0, activation):
        state = state_for_week(player_states, week)
        path.append(state.to_dict())
        matrix = _predictive_player_roster_cached(
            state.roster, ctx, roster_weekly_cache,
            label=f"v0.35 player state W{week}",
        )
        out[:, week - 1] = matrix[:, week - 1]
    state = state_for_week(player_states, activation)
    path.append(state.to_dict())
    matrix = _predictive_player_roster_cached(
        state.roster, ctx, roster_weekly_cache,
        label=f"v0.35 activation player state W{activation}",
    )
    out[:, activation - 1:] = matrix[:, activation - 1:]
    return out, path


def _evaluate_policy_channel(
    snapshot: dict[str, Any], league: dict[str, Any], model: dict[str, Any], *,
    position: str, values_path="data/processed/player_values_2026.csv", team_name=None,
    team_id=None, mc_scenarios=None,
) -> dict[str, Any]:
    static_report = (_evaluate_defense_static if position == "DST" else _evaluate_kicker_static)(
        snapshot, league, model, values_path=values_path, team_name=team_name,
        team_id=team_id, mc_scenarios=mc_scenarios,
    )
    ctx = _build_context(snapshot, league, model, values_path, team_name, team_id, mc_scenarios)
    n = int(ctx.predictive_scenarios)

    d_static = _static_team_weekly(ctx, "DST")
    k_static = _static_team_weekly(ctx, "K")
    d1 = simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    k1 = simulate_specialist_market_policy(ctx, position="K", user_mode="ONE_SLOT")
    d_hold = simulate_specialist_market_policy(ctx, position="DST", user_mode="HOLD")
    k_hold = simulate_specialist_market_policy(ctx, position="K", user_mode="HOLD")

    # Build the commissioned full-team player baseline once.  Policy state changes are
    # applied as same-channel deltas on top, preserving the mature player propagator.
    ctx.ensure_predictive_opponent_reference()
    _base_result, _base_utility, base_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, include_diagnostics=False, progress_label="v0.32 base roster"
    )
    base_opponent = np.asarray(ctx.opponent_predictive, dtype=float)

    if position == "DST":
        _w0, _o0, u_hold = _compose_state(base_weekly, base_opponent, ctx, d_policy=d_hold, k_policy=k1, d_static=d_static, k_static=k_static)
        _w1, _o1, u_policy = _compose_state(base_weekly, base_opponent, ctx, d_policy=d1, k_policy=k1, d_static=d_static, k_static=k_static)
        policy = d1
        static = d_static
    else:
        _w0, _o0, u_hold = _compose_state(base_weekly, base_opponent, ctx, d_policy=d1, k_policy=k_hold, d_static=d_static, k_static=k_static)
        _w1, _o1, u_policy = _compose_state(base_weekly, base_opponent, ctx, d_policy=d1, k_policy=k1, d_static=d_static, k_static=k_static)
        policy = k1
        static = k_static

    block = _policy_block(policy, ctx, static)
    block["complete_state_delta"] = _paired_stats(np.asarray(u_policy) - np.asarray(u_hold), ctx, 32001 if position == "DST" else 32002)
    block["baseline_policy"] = "HOLD_CURRENT_SPECIALIST_WITH_DYNAMIC_OPPONENT_MARKET_V032"
    block["proposal_current_action"] = dict(block.get("current_action") or {"action": "HOLD"})
    resolved = str((block.get("complete_state_delta") or {}).get("classification") or "NO_RESOLVED_EDGE") in {"ACTIONABLE_EDGE", "POSSIBLE_EDGE"}
    block["recommended_current_action"] = dict(block["proposal_current_action"]) if resolved else {"action": "HOLD"}
    block["authoritative_current_action"] = bool(resolved)

    # Current WAIVERS remain distinct from the guaranteed FREEAGENT market.  Each
    # claim is evaluated conditionally on acquisition with the same specialist
    # complete-state response, while acquisition probability stays in the separate
    # uncalibrated manager-behavior kernel.
    waiver_candidates = [
        dict(player) for player in ctx.actionable_available
        if str(player.get("position") or "").upper() == position
        and str(player.get("fantasy_status") or "").upper() in {"WAIVER", "WAIVERS"}
        and _pid(player) is not None
        and not _is_current_week_locked(player, ctx)
    ]
    waiver_candidates.sort(key=lambda player: int(_pid(player) or 10**12))
    owned_specialists = _position_rows(ctx.roster, position)
    current_waiver_actions: list[dict[str, Any]] = []
    for candidate in waiver_candidates:
        candidate_id = int(_pid(candidate))
        blockers = waiver_blocker_diagnostics(candidate, ctx)
        p_acquire = float(waiver_acquisition_probability(candidate, ctx, blockers=blockers))
        drop_options: list[dict[str, Any] | None]
        if owned_specialists:
            drop_options = [
                owned for owned in owned_specialists
                if _legal_drop(owned) and not _is_current_week_locked(owned, ctx)
            ]
        else:
            drop_options = [None]

        candidate_rows: list[dict[str, Any]] = []
        if not drop_options:
            candidate_rows.append({
                "action": "CLAIM",
                "position": position,
                "add_espn_id": candidate_id,
                "add_name": candidate.get("name"),
                "add_team": candidate.get("nfl_team"),
                "drop_espn_id": None,
                "drop_name": None,
                "fantasy_status": "WAIVERS",
                "p_acquire": p_acquire,
                "waiver_blockers": blockers,
                "legal": False,
                "reason": "NO_LEGAL_UNLOCKED_SAME_CHANNEL_DROP",
                "conditional_complete_state_delta": None,
                "expected_complete_state_delta_mean": 0.0,
                "classification": "NO_LEGAL_CLAIM_STATE",
            })
        else:
            for drop_player in drop_options:
                drop_id = _pid(drop_player)
                conditional = simulate_specialist_market_policy(
                    ctx,
                    position=position,
                    user_mode="ONE_SLOT",
                    pre_acquire_espn_id=candidate_id,
                    pre_drop_espn_id=drop_id,
                    pre_acquire_from_waivers=True,
                )
                if position == "DST":
                    _ww, _oo, u_claim = _compose_state(
                        base_weekly, base_opponent, ctx,
                        d_policy=conditional, k_policy=k1,
                        d_static=d_static, k_static=k_static,
                    )
                else:
                    _ww, _oo, u_claim = _compose_state(
                        base_weekly, base_opponent, ctx,
                        d_policy=d1, k_policy=conditional,
                        d_static=d_static, k_static=k_static,
                    )
                stats = _paired_stats(
                    np.asarray(u_claim) - np.asarray(u_hold),
                    ctx,
                    32500 + candidate_id + int(drop_id or 0),
                )
                base_class = str(stats.get("classification") or "NO_RESOLVED_EDGE")
                classification = (
                    "WAIVER_ACTIONABLE_EDGE" if base_class == "ACTIONABLE_EDGE"
                    else "WAIVER_POSSIBLE_EDGE" if base_class == "POSSIBLE_EDGE"
                    else "NO_WAIVER_RESOLVED_EDGE"
                )
                candidate_rows.append({
                    "action": "CLAIM" if drop_player is None else "SWAP_CLAIM",
                    "position": position,
                    "add_espn_id": candidate_id,
                    "add_name": candidate.get("name"),
                    "add_team": candidate.get("nfl_team"),
                    "drop_espn_id": drop_id,
                    "drop_name": (drop_player or {}).get("name"),
                    "fantasy_status": "WAIVERS",
                    "p_acquire": p_acquire,
                    "waiver_blockers": blockers,
                    "legal": True,
                    "conditional_complete_state_delta": stats,
                    "expected_complete_state_delta_mean": float(p_acquire * float(stats.get("mean") or 0.0)),
                    "classification": classification,
                    "conditional_policy_market_states": conditional.market_states,
                })
        candidate_rows.sort(
            key=lambda row: (
                float(row.get("expected_complete_state_delta_mean") or -999.0),
                float(((row.get("conditional_complete_state_delta") or {}).get("mean") or -999.0)),
                -int(row.get("drop_espn_id") or -1),
            ),
            reverse=True,
        )
        current_waiver_actions.append(candidate_rows[0])

    current_waiver_actions.sort(
        key=lambda row: (
            float(row.get("expected_complete_state_delta_mean") or -999.0),
            float(((row.get("conditional_complete_state_delta") or {}).get("mean") or -999.0)),
            -int(row.get("add_espn_id") or -1),
        ),
        reverse=True,
    )
    block["current_waiver_candidates_total"] = len(waiver_candidates)
    block["modeled_current_waivers"] = len(current_waiver_actions)
    block["current_waiver_one_slot_coverage_complete"] = len(current_waiver_actions) == len(waiver_candidates)
    block["current_waiver_actions"] = current_waiver_actions

    free_action = dict(block.get("recommended_current_action") or {"action": "HOLD"})
    free_expected = (
        float((block.get("complete_state_delta") or {}).get("mean") or 0.0)
        if block.get("authoritative_current_action") and str(free_action.get("action") or "HOLD").upper() != "HOLD"
        else 0.0
    )
    authorized_current_actions: list[dict[str, Any]] = []
    if free_expected > 0.0:
        authorized_current_actions.append({
            "acquisition_state": "FREEAGENT",
            "expected_complete_state_delta_mean": free_expected,
            "action": free_action,
        })
    for row in current_waiver_actions:
        if str(row.get("classification") or "") not in {"WAIVER_ACTIONABLE_EDGE", "WAIVER_POSSIBLE_EDGE"}:
            continue
        authorized_current_actions.append({
            "acquisition_state": "WAIVERS",
            "expected_complete_state_delta_mean": float(row.get("expected_complete_state_delta_mean") or 0.0),
            "action": row,
        })
    authorized_current_actions.sort(
        key=lambda item: float(item.get("expected_complete_state_delta_mean") or 0.0),
        reverse=True,
    )
    block["authorized_current_actions"] = authorized_current_actions
    if authorized_current_actions:
        best = authorized_current_actions[0]
        block["recommended_current_action"] = dict(best["action"])
        block["authoritative_current_action"] = True

    dynamic_carry: list[dict[str, Any]] = []
    temporal_player_state_report = None
    if position == "DST":
        current_release_screen = _best_player_slot_release(ctx)
        current_release_id = _pid(current_release_screen) if current_release_screen else None

        # v0.35 first evolves our ordinary-player membership P_w under a causal
        # expected player-channel policy. Current-week membership is observed and
        # immutable here; future current FREEAGENTs are the guaranteed pool. Other
        # Broader endogenous manager transaction policy remains outside this local
        # v0.36 response cascade; only response branches causally seeded by our perturbation
        # are propagated.
        player_states = build_temporal_player_states(ctx)
        temporal_player_state_report = summarize_temporal_player_states(player_states)
        player_lookup: dict[int, dict[str, Any]] = {}
        for player in list(ctx.roster) + list(ctx.actionable_available) + [q for r in ctx.all_team_rosters.values() for q in r]:
            pid = _pid(player)
            if pid is not None:
                player_lookup[int(pid)] = player
        for state in player_states.values():
            for player in state.roster:
                pid = _pid(player)
                if pid is not None:
                    player_lookup[int(pid)] = player
            for pid, player in state.free_pool.items():
                player_lookup[int(pid)] = player

        # Build I_w and the slot-release policy on the evolved player membership at
        # each decision boundary. Realized fantasy scores remain invisible.
        release_plans = {
            activation_week: temporal_release_plan(
                ctx, activation_week, current_release_id=current_release_id,
                roster=state_for_week(player_states, activation_week).roster,
                membership_model=PLAYER_STATE_MODEL,
            )
            for activation_week in range(max(1, int(ctx.week)), 18)
        }
        roster_weekly_cache: dict[tuple[int, ...], np.ndarray] = {
            _player_roster_key(ctx.roster): np.asarray(base_weekly, dtype=float)
        }
        release_weekly_cache: dict[tuple[tuple[int, ...], int], np.ndarray] = {}

        response_n = int(ctx.cfg.get("league_state_response_scenarios", 256))
        response_cache: dict[tuple[int, int], dict[str, Any]] = {}
        d1_sum = _weighted_summary(d1.team_weekly[int(ctx.team_id)], ctx)
        activation_rows: list[dict[str, Any]] = []

        def _carry2_row(
            d2: SpecialistPolicyResult,
            requested_activation_week: int,
            *,
            acquisition_state: str = "FREEAGENT",
            p_acquire: float = 1.0,
            waiver_blockers: list[dict[str, Any]] | None = None,
        ) -> dict[str, Any]:
            d2_sum = _weighted_summary(d2.team_weekly[int(ctx.team_id)], ctx)

            # The slot is physically consumed when the user actually makes the ADD that
            # grows the defense portfolio.  Normally this is the requested activation
            # week; if no guaranteed defense is obtainable then, defer the player-sector
            # release until the first later ADD rather than charging a phantom slot cost.
            add_tx = next((
                t for t in d2.transactions
                if int(t.get("team_id") or -1) == int(ctx.team_id)
                and int(t.get("week") or -1) >= int(requested_activation_week)
                and str(t.get("action") or "").upper() == "ADD"
                and t.get("drop_espn_id") is None
            ), None)
            effective_activation_week = int(add_tx.get("week")) if add_tx is not None else None

            if effective_activation_week is None:
                local_base_weekly = np.asarray(base_weekly, dtype=float).copy()
                timed_weekly = np.asarray(base_weekly, dtype=float).copy()
                player_state_path = [state_for_week(player_states, int(ctx.week)).to_dict()]
                scenario_shift = np.zeros((n, 17), dtype=float)
                release_summary = None
                response_summary = {
                    "p_claimed": 0.0,
                    "field_shift_ppg": 0.0,
                    "current_opponent_shift_ppg": 0.0,
                    "model": CLAIM_RESPONSE_MODEL,
                    "timing_proxy": "NO_PLAYER_RELEASE_UNTIL_SECOND_DST_IS_ACQUIRED_V033",
                    "information_model": TEMPORAL_INFORMATION_MODEL,
                    "player_membership_model": PLAYER_STATE_MODEL,
                }
                release_plan = None
            else:
                release_plan = release_plans[int(effective_activation_week)]
                activation_state = state_for_week(player_states, int(effective_activation_week))
                local_base_weekly, player_state_path = _temporal_player_baseline_to_activation(
                    base_weekly, player_states, int(effective_activation_week), ctx, roster_weekly_cache
                )
                selected_ids = np.asarray(release_plan.get("selected_ids"), dtype=int)
                release_weekly_by_id: dict[int, np.ndarray] = {}
                state_key = _player_roster_key(activation_state.roster)
                for rid in [int(pid) for pid in np.unique(selected_ids) if int(pid) >= 0]:
                    cache_key = (state_key, int(rid))
                    if cache_key not in release_weekly_cache:
                        release_roster = [p for p in activation_state.roster if _pid(p) != int(rid)]
                        release_weekly_cache[cache_key] = _predictive_player_roster_cached(
                            release_roster, ctx, {}, label=f"v0.35 W{effective_activation_week} release roster {rid}"
                        )
                    release_weekly_by_id[int(rid)] = release_weekly_cache[cache_key]
                timed_weekly = compose_temporal_release_weekly(
                    local_base_weekly, release_weekly_by_id, selected_ids, effective_activation_week
                )
                active_release_ids = [int(pid) for pid in np.unique(selected_ids) if int(pid) >= 0]
                response_by_id: dict[int, dict[str, Any]] = {}
                for rid in active_release_ids:
                    key = (int(effective_activation_week), int(rid))
                    if key not in response_cache:
                        release_player = player_lookup.get(int(rid))
                        if release_player is None:
                            continue
                        if int(effective_activation_week) == int(ctx.week):
                            # Preserve the commissioned fixed6 current-state response exactly.
                            # v0.33 changes only the future-state approximation.
                            response_cache[key] = released_player_league_state_response(
                                release_player, ctx, scenarios=response_n
                            )
                        else:
                            response_cache[key] = temporal_released_player_response(
                                release_player, ctx,
                                activation_week=effective_activation_week,
                                scenarios=response_n,
                            )
                    response_by_id[int(rid)] = response_cache[key]
                scenario_shift = compose_temporal_release_shift(
                    selected_ids, response_by_id, effective_activation_week, n
                )
                release_summary = release_plan_summary(release_plan, player_lookup)
                distribution = (release_summary or {}).get("selection_distribution") or []
                p_claimed = 0.0
                field_shift_ppg = 0.0
                first_order_field_shift_ppg = 0.0
                higher_order_field_shift_ppg = 0.0
                current_opponent_shift_ppg = 0.0
                cascade_pruned_probability_mass = 0.0
                cascade_stop_reasons = set()
                for item in distribution:
                    rid = int(item.get("espn_id"))
                    weight = float(item.get("selection_probability") or 0.0)
                    response = response_by_id.get(rid) or {}
                    p_claimed += weight * float(response.get("p_claimed") or 0.0)
                    field_shift_ppg += weight * float(response.get("field_shift_ppg") or 0.0)
                    first_order_field_shift_ppg += weight * float(response.get("first_order_field_shift_ppg") or response.get("field_shift_ppg") or 0.0)
                    higher_order_field_shift_ppg += weight * float(response.get("higher_order_field_shift_ppg") or 0.0)
                    current_opponent_shift_ppg += weight * float(response.get("current_opponent_shift_ppg") or 0.0)
                    cascade_pruned_probability_mass += weight * float(response.get("cascade_pruned_probability_mass") or 0.0)
                    cascade_stop_reasons.update(response.get("cascade_stop_reasons") or [])
                response_models = sorted({
                    str(response.get("model"))
                    for response in response_by_id.values()
                    if response.get("model")
                })
                dominant_release_id = None
                if distribution:
                    dominant_release_id = int(max(distribution, key=lambda item: float(item.get("selection_probability") or 0.0)).get("espn_id"))
                dominant_response = response_by_id.get(dominant_release_id) or {}
                response_summary = {
                    "p_claimed": float(p_claimed),
                    "field_shift_ppg": float(field_shift_ppg),
                    "first_order_field_shift_ppg": float(first_order_field_shift_ppg),
                    "higher_order_field_shift_ppg": float(higher_order_field_shift_ppg),
                    "current_opponent_shift_ppg": float(current_opponent_shift_ppg),
                    "model": response_models[0] if len(response_models) == 1 else "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE",
                    "first_order_model": dominant_response.get("first_order_model"),
                    "higher_order_scenarios": int(dominant_response.get("higher_order_scenarios") or 0),
                    "cascade_orders": list(dominant_response.get("cascade_orders") or []),
                    "cascade_summary_basis": "DOMINANT_RELEASE_STATE_V036",
                    "cascade_pruned_probability_mass": float(cascade_pruned_probability_mass),
                    "cascade_stop_reasons": sorted(cascade_stop_reasons),
                    "timing_proxy": (
                        "COMMISSIONED_CURRENT_STATE_RELEASE_RESPONSE_V031"
                        if int(effective_activation_week) == int(ctx.week)
                        else "RECOMPUTED_AT_ACTIVATION_STATE_V033"
                    ),
                    "information_model": release_plan.get("information_model"),
                    "player_membership_model": release_plan.get("membership_model"),
                    "release_distribution": distribution,
                }

            _wbase, _obase, u_local_base = _compose_state(
                local_base_weekly, base_opponent, ctx, d_policy=d1, k_policy=k1,
                d_static=d_static, k_static=k_static,
            )
            _wb, _ob, ub = _compose_state(
                timed_weekly, base_opponent, ctx, d_policy=d2, k_policy=k1,
                d_static=d_static, k_static=k_static,
                extra_opponent_shift_by_week=scenario_shift,
            )
            delta = np.asarray(ub) - np.asarray(u_local_base)
            stats = _paired_stats(delta, ctx, 34000 + int(requested_activation_week))
            tx = add_tx or _user_transaction_for_week(d2, int(ctx.team_id), requested_activation_week) or {}
            add_id = _finite_int(tx.get("add_espn_id"))
            add_player = player_lookup.get(int(add_id)) if add_id is not None else None
            current = int(requested_activation_week) == int(ctx.week)
            base_class = str(stats.get("classification") or "NO_RESOLVED_EDGE")
            if base_class == "ACTIONABLE_EDGE":
                classification = "CARRY2_ACTIONABLE_EDGE" if current else "FUTURE_CARRY2_ACTIONABLE_EDGE"
            elif base_class == "POSSIBLE_EDGE":
                classification = "CARRY2_POSSIBLE_EDGE" if current else "FUTURE_CARRY2_POSSIBLE_EDGE"
            else:
                classification = "NO_CARRY2_RESOLVED_EDGE"
            row = {
                "activation_week": int(requested_activation_week),
                "effective_player_release_week": effective_activation_week,
                "current_activation": bool(current),
                "add_espn_id": add_id,
                "add_name": tx.get("add"),
                "add_team": (add_player or {}).get("nfl_team"),
                "dynamic_channel_delta_ppg": float(d2_sum["weighted_mean_ppg"] - d1_sum["weighted_mean_ppg"]),
                "one_slot_policy_ppg": d1_sum["weighted_mean_ppg"],
                "two_slot_policy_ppg": d2_sum["weighted_mean_ppg"],
                "player_slot_release": release_summary,
                "weekly_plan": d2.user_plan,
                "market_model": POLICY_MODEL,
                "market_states": d2.market_states,
                "information_model": TEMPORAL_INFORMATION_MODEL,
                "player_membership_model": PLAYER_STATE_MODEL,
                "player_transaction_model": PLAYER_TRANSACTION_MODEL,
                "external_player_market_model": EXTERNAL_PLAYER_MARKET_MODEL,
                "player_information_policy": PLAYER_INFORMATION_POLICY,
                "state_composition_order": STATE_COMPOSITION_ORDER,
                "player_state_at_release": (
                    state_for_week(player_states, int(effective_activation_week)).to_dict()
                    if effective_activation_week is not None else None
                ),
                "player_state_path": player_state_path,
                "complete_state_confirmed": True,
                "complete_state_delta": stats,
                "classification": classification,
                "release_response": response_summary,
                "acquisition_state": acquisition_state,
                "p_acquire": float(p_acquire),
                "waiver_blockers": list(waiver_blockers or []),
                "expected_complete_state_delta_mean": float(p_acquire * float(stats.get("mean") or 0.0)),
            }
            return row
        for requested_activation_week in range(max(1, int(ctx.week)), 18):
            d2 = simulate_specialist_market_policy(
                ctx, position="DST", user_mode="CARRY2", activation_week=requested_activation_week
            )
            activation_rows.append(
                _carry2_row(d2, requested_activation_week, acquisition_state="FREEAGENT")
            )

        for candidate in waiver_candidates:
            candidate_id = int(_pid(candidate))
            blockers = waiver_blocker_diagnostics(candidate, ctx)
            p_acquire = float(waiver_acquisition_probability(candidate, ctx, blockers=blockers))
            try:
                d2 = simulate_specialist_market_policy(
                    ctx,
                    position="DST",
                    user_mode="CARRY2",
                    pre_acquire_espn_id=candidate_id,
                    pre_acquire_from_waivers=True,
                    activation_week=int(ctx.week),
                )
            except ValueError:
                continue
            activation_rows.append(
                _carry2_row(
                    d2,
                    int(ctx.week),
                    acquisition_state="WAIVERS",
                    p_acquire=p_acquire,
                    waiver_blockers=blockers,
                )
            )

        activation_rows.sort(
            key=lambda r: (
                float(r.get("expected_complete_state_delta_mean") or -999.0),
                float(((r.get("complete_state_delta") or {}).get("mean") or -999.0)),
                -int(r.get("activation_week") or 99),
            ), reverse=True,
        )
        dynamic_carry = activation_rows

    waiver_carry2_rows = [
        row for row in dynamic_carry
        if bool(row.get("current_activation"))
        and str(row.get("acquisition_state") or "").upper() == "WAIVERS"
    ]
    carry2_required = position == "DST" and len(owned_specialists) < 2
    carry2_complete = (not carry2_required) or len(waiver_carry2_rows) == len(waiver_candidates)
    block["modeled_current_waiver_carry2"] = len(waiver_carry2_rows)
    block["current_waiver_carry2_coverage_complete"] = bool(carry2_complete)
    block["current_waiver_coverage_complete"] = bool(
        block.get("current_waiver_one_slot_coverage_complete") and carry2_complete
    )

    current_carry = next((r for r in dynamic_carry if r.get("current_activation")), None)
    current_carry_class = str((current_carry or {}).get("classification") or "NO_CARRY2_RESOLVED_EDGE")
    carry2_current_recommendation = (
        ("CLAIM_SECOND_DST_NOW" if str((current_carry or {}).get("acquisition_state") or "").upper() == "WAIVERS" else "ADD_SECOND_DST_NOW")
        if current_carry_class in {"CARRY2_ACTIONABLE_EDGE", "CARRY2_POSSIBLE_EDGE"}
        else "HOLD_ONE_DST_NOW"
    )

    report = dict(static_report)
    report.update({
        "schema_version": 3,
        "model_version": "0.36",
        "policy_layer": "SPECIALIST_WITH_CAUSAL_PLAYER_STATE_V035",
        "one_slot_policy": block,
        "dynamic_carry_actions": dynamic_carry,
        "carry2_current_recommendation": carry2_current_recommendation,
        "best_carry2_activation": dynamic_carry[0] if dynamic_carry else None,
        "temporal_player_state": temporal_player_state_report,
        "policy_notes": [
            "L1 static same-channel comparisons are preserved as diagnostics.",
            "L2 one-slot policy propagates the specialist market week by week from the current guaranteed FREEAGENT pool.",
            "Manager transactions and starters use pregame expected specialist response only; realized MC never selects an action or starter.",
            "Dropped specialists enter the modeled market in the following week, not the same week.",
            "Future simultaneous demand uses current ESPN waiver priority only as an explicit uncalibrated transaction-order proxy.",
            "L3 two-DST policy endogenizes the activation week and lets the evolving same-channel market choose the acquired second defense; candidate names are outputs of the state transition, not independent placeholder actions.",
            "v0.35-fixed1 evolves our ordinary-player membership causally before each future specialist decision using expected player-channel best responses; current Week-1 membership remains the observed commissioned state.",
            "v0.36 preserves the v0.35-fixed1 causal self-player state and adds a bounded order-2+ external player-channel release cascade around specialist perturbations; broader endogenous league transaction policy remains outside this response expansion.",
            "L4 carry2 confirmation expands around the evolved activation-week player state, freezes that local P_w after the perturbation, recomputes released-player claimant/recipient response, and compares complete H2H states under common random numbers.",
            "Future active/inactive information uses an explicitly uncalibrated week-boundary reveal proxy; no future realized fantasy score or workload realization selects an action.",
            "Post-activation response is expanded through the bounded v0.36 order-2+ player-channel cascade; unrelated league transactions remain outside the local perturbation.",
        ],
    })
    return report


@shadow_dst_call("subsystem.dst.channel")
def evaluate_defense_channel(*args, **kwargs) -> dict[str, Any]:
    return _evaluate_policy_channel(*args, position="DST", **kwargs)


@shadow_k_call("subsystem.k.channel")
def evaluate_kicker_channel(*args, **kwargs) -> dict[str, Any]:
    return _evaluate_policy_channel(*args, position="K", **kwargs)
