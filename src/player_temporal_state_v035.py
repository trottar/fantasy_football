from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .season_utility import week_weights
from .specialist_temporal_v033 import _active_conditional_mean, _temporal_roster_score
from .transaction_manager import (
    _classify_paired_delta,
    _finite_int,
    _legal_drop,
    _paired_mean_interval,
    _simulate_predictive_weekly_points,
)

PLAYER_POSITIONS = {"QB", "RB", "WR", "TE"}
PLAYER_STATE_MODEL = "CAUSAL_SELF_PLAYER_MEMBERSHIP_STATE_V035_FIXED1"
PLAYER_TRANSACTION_MODEL = "SCREENED_PAIRED_PREDICTIVE_CRN_BEST_RESPONSE_V035_FIXED1"
PLAYER_SCREEN_MODEL = "EXPECTED_LINEUP_PARETO_SCREEN_ONLY_V035_FIXED1"
PLAYER_CONFIRMATION_MODEL = "DIRECT_PLAYER_CHANNEL_PAIRED_H2H_CRN_V035_FIXED1"
EXTERNAL_PLAYER_MARKET_MODEL = "FROZEN_CURRENT_GUARANTEED_FREEAGENT_POOL_NO_EXTERNAL_CLAIMS_V035"
PLAYER_INFORMATION_POLICY = "EXPECTED_PREGAME_PLAYER_RESPONSE_NO_REALIZED_SCORE_V035_FIXED1"
STATE_COMPOSITION_ORDER = "PLAYER_POLICY_THEN_SPECIALIST_PERTURBATION_V035_FIXED1"
EPS = 1e-12


@dataclass
class TemporalPlayerState:
    week: int
    roster: list[dict[str, Any]]
    free_pool: dict[int, dict[str, Any]]
    transaction: dict[str, Any] | None
    expected_remaining_ppg: float
    expected_week_points: float
    guaranteed_free_agents: int
    excluded_current_waivers: int

    def roster_ids(self) -> tuple[int, ...]:
        ids = []
        for player in self.roster:
            pid = _finite_int(player.get("espn_id"))
            if pid is not None:
                ids.append(int(pid))
        return tuple(sorted(ids))

    def ordinary_roster_ids(self) -> tuple[int, ...]:
        ids = []
        for player in self.roster:
            if str(player.get("position") or "").upper() not in PLAYER_POSITIONS:
                continue
            pid = _finite_int(player.get("espn_id"))
            if pid is not None:
                ids.append(int(pid))
        return tuple(sorted(ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "week": int(self.week),
            "ordinary_roster_ids": list(self.ordinary_roster_ids()),
            "ordinary_roster": [
                {
                    "espn_id": _finite_int(p.get("espn_id")),
                    "name": p.get("name"),
                    "position": p.get("position"),
                    "nfl_team": p.get("nfl_team"),
                }
                for p in self.roster
                if str(p.get("position") or "").upper() in PLAYER_POSITIONS
            ],
            "transaction": dict(self.transaction) if self.transaction else None,
            "expected_remaining_ppg": float(self.expected_remaining_ppg),
            "expected_week_points": float(self.expected_week_points),
            "guaranteed_free_agents": int(self.guaranteed_free_agents),
            "excluded_current_waivers": int(self.excluded_current_waivers),
            "player_state_model": PLAYER_STATE_MODEL,
            "transaction_model": PLAYER_TRANSACTION_MODEL,
            "screen_model": PLAYER_SCREEN_MODEL,
            "confirmation_model": PLAYER_CONFIRMATION_MODEL,
            "external_market_model": EXTERNAL_PLAYER_MARKET_MODEL,
            "information_policy": PLAYER_INFORMATION_POLICY,
            "composition_order": STATE_COMPOSITION_ORDER,
        }


def _pid(player: dict[str, Any] | None) -> int | None:
    return _finite_int((player or {}).get("espn_id"))


def _ordinary_rows(roster: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(p) for p in roster if str(p.get("position") or "").upper() in PLAYER_POSITIONS]


def _guaranteed_free_pool(ctx) -> tuple[dict[int, dict[str, Any]], int]:
    free: dict[int, dict[str, Any]] = {}
    waivers = 0
    for player in getattr(ctx, "actionable_available", []) or []:
        if str(player.get("position") or "").upper() not in PLAYER_POSITIONS:
            continue
        pid = _pid(player)
        if pid is None:
            continue
        status = str(player.get("fantasy_status") or "").upper()
        if status == "FREEAGENT":
            free[int(pid)] = dict(player)
        elif status in {"WAIVER", "WAIVERS"}:
            waivers += 1
    return free, waivers


def _legal_player_swap(roster: list[dict[str, Any]], add: dict[str, Any], drop: dict[str, Any], league: dict[str, Any]) -> bool:
    apos = str(add.get("position") or "").upper()
    dpos = str(drop.get("position") or "").upper()
    if apos not in PLAYER_POSITIONS or dpos not in PLAYER_POSITIONS:
        return False
    counts = {pos: 0 for pos in PLAYER_POSITIONS}
    for player in roster:
        pos = str(player.get("position") or "").upper()
        if pos in counts:
            counts[pos] += 1
    counts[dpos] -= 1
    counts[apos] += 1
    maxima = league.get("position_maximums") or {}
    for pos in PLAYER_POSITIONS:
        if pos in maxima and counts[pos] > int(maxima[pos]):
            return False
    required = league.get("roster") or {}
    for pos in PLAYER_POSITIONS:
        if counts[pos] < int(required.get(pos, 0)):
            return False
    return True


def _candidate_expected_yield(player: dict[str, Any], ctx, start_week: int) -> float:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float).copy()
    weights[np.asarray(weeks, dtype=int) < int(start_week)] = 0.0
    norm = max(float(weights.sum()), EPS)
    total = 0.0
    for week in range(int(start_week), 18):
        w = float(weights[week - 1])
        if w <= 0.0:
            continue
        conditional, p_active = _active_conditional_mean(player, ctx, week)
        total += w * conditional * p_active
    return float(total / norm)


def _shortlist_free_agents(free_pool: dict[int, dict[str, Any]], ctx, start_week: int) -> list[dict[str, Any]]:
    scored = []
    for player in free_pool.values():
        if str(player.get("position") or "").upper() not in PLAYER_POSITIONS:
            continue
        row = dict(player)
        row["_v035_expected_yield"] = _candidate_expected_yield(row, ctx, int(start_week))
        scored.append(row)
    scored.sort(key=lambda p: (-float(p.get("_v035_expected_yield") or 0.0), int(_pid(p) or 10**12)))

    total_limit = max(1, int(getattr(ctx, "cfg", {}).get("candidate_limit", 80)))
    floor = max(1, int(getattr(ctx, "cfg", {}).get("candidate_floor_per_position", 8)))
    selected: dict[int, dict[str, Any]] = {}
    for pos in sorted(PLAYER_POSITIONS):
        rows = [p for p in scored if str(p.get("position") or "").upper() == pos]
        for player in rows[:floor]:
            pid = _pid(player)
            if pid is not None:
                selected[int(pid)] = player
    for player in scored:
        if len(selected) >= total_limit:
            break
        pid = _pid(player)
        if pid is not None:
            selected[int(pid)] = player
    return sorted(
        selected.values(),
        key=lambda p: (-float(p.get("_v035_expected_yield") or 0.0), int(_pid(p) or 10**12)),
    )


def _roster_score_cached(roster: list[dict[str, Any]], ctx, start_week: int, cache: dict) -> tuple[float, float]:
    key = (
        int(start_week),
        tuple(sorted(int(pid) for p in roster if (pid := _pid(p)) is not None)),
    )
    if key not in cache:
        cache[key] = _temporal_roster_score(roster, ctx, int(start_week))
    season, week = cache[key]
    return float(season), float(week)



def _screen_future_swaps(
    roster: list[dict[str, Any]],
    free_pool: dict[int, dict[str, Any]],
    ctx,
    week: int,
    cache: dict,
) -> list[dict[str, Any]]:
    """Generate a cheap expected-lineup frontier; this screen is never authoritative."""
    baseline_season, baseline_week = _roster_score_cached(roster, ctx, int(week), cache)
    candidates = _shortlist_free_agents(free_pool, ctx, int(week))
    drops = [
        dict(p)
        for p in roster
        if str(p.get("position") or "").upper() in PLAYER_POSITIONS and _pid(p) is not None and _legal_drop(p)
    ]
    rows: list[dict[str, Any]] = []
    for add in candidates:
        add_id = _pid(add)
        if add_id is None:
            continue
        for drop in drops:
            drop_id = _pid(drop)
            if drop_id is None or int(drop_id) == int(add_id):
                continue
            if not _legal_player_swap(roster, add, drop, ctx.league):
                continue
            trial = [p for p in roster if _pid(p) != int(drop_id)] + [dict(add)]
            season_score, week_score = _roster_score_cached(trial, ctx, int(week), cache)
            season_gain = float(season_score - baseline_season)
            week_gain = float(week_score - baseline_week)
            # This deterministic expectation is only a broad screen.  It may not
            # change P_w by itself.  Authority is reserved for paired predictive MC.
            if season_gain <= EPS or week_gain < -EPS:
                continue
            rows.append({
                "action": "SWAP",
                "week": int(week),
                "add_espn_id": int(add_id),
                "add": add.get("name"),
                "add_position": add.get("position"),
                "drop_espn_id": int(drop_id),
                "drop": drop.get("name"),
                "drop_position": drop.get("position"),
                "screen_expected_remaining_gain_ppg": season_gain,
                "screen_expected_week_gain_points": week_gain,
                "candidate_expected_yield_ppg": float(add.get("_v035_expected_yield") or 0.0),
                "screen_model": PLAYER_SCREEN_MODEL,
                "_new_roster": trial,
            })
    rows.sort(
        key=lambda row: (
            float(row["screen_expected_remaining_gain_ppg"]),
            float(row["screen_expected_week_gain_points"]),
            -int(row["add_espn_id"]),
            -int(row["drop_espn_id"]),
        ),
        reverse=True,
    )
    keep = max(1, int(getattr(ctx, "cfg", {}).get("temporal_player_state_screen_keep", 4)))
    return rows[:keep]


def _future_h2h_utility(
    weekly: np.ndarray,
    opponent: np.ndarray,
    ctx,
    start_week: int,
) -> np.ndarray:
    """Paired H2H utility from a future decision boundary onward."""
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float).copy()
    weights[np.asarray(weeks, dtype=int) < int(start_week)] = 0.0
    if float(weights.sum()) <= 0.0:
        weights[np.asarray(weeks, dtype=int) >= int(start_week)] = 1.0
    norm = max(float(weights.sum()), EPS)
    weekly = np.asarray(weekly, dtype=float)
    opponent = np.asarray(opponent, dtype=float)
    if weekly.shape != opponent.shape:
        raise ValueError(f"future player-state opponent shape {opponent.shape} != roster shape {weekly.shape}")
    wins = (weekly > opponent).astype(float)
    wins[weekly == opponent] = 0.5
    return np.sum(wins * weights[None, :], axis=1) / norm


def _predictive_weekly_cached(
    roster: list[dict[str, Any]],
    ctx,
    cache: dict,
) -> np.ndarray:
    key = ("weekly", tuple(sorted(int(pid) for p in roster if (pid := _pid(p)) is not None)))
    if key not in cache:
        cache[key] = _simulate_predictive_weekly_points(
            roster,
            ctx,
            ctx.replacement_current,
            ctx.replacement_season,
            current_week_policy="realistic",
        )
    return np.asarray(cache[key], dtype=float)


def _prepare_predictive_confirmation(ctx, cache: dict) -> None:
    if cache.get("_prepared"):
        return
    old_n = int(ctx.predictive_scenarios)
    target_n = max(64, int(ctx.cfg.get("temporal_player_state_scenarios", 256)))
    ctx.set_predictive_scenarios(target_n)
    opponent = np.asarray(ctx.ensure_predictive_opponent_reference(), dtype=float)
    cache["_prepared"] = True
    cache["_old_n"] = old_n
    cache["_scenarios"] = int(target_n)
    cache["_opponent"] = opponent


def _restore_predictive_confirmation(ctx, cache: dict) -> None:
    if not cache.get("_prepared"):
        return
    old_n = int(cache.get("_old_n") or ctx.predictive_scenarios)
    if int(ctx.predictive_scenarios) != old_n:
        ctx.set_predictive_scenarios(old_n)


# No realized score or workload outcome is revealed to the policy. Predictive MC
# samples are integrated only as an ensemble response for paired expected-utility
# confirmation; starter selection inside that MC remains pregame/no-hindsight.
def _confirm_screened_future_swaps(
    roster: list[dict[str, Any]],
    screens: list[dict[str, Any]],
    ctx,
    week: int,
    predictive_cache: dict,
) -> dict[str, Any] | None:
    """Authorize P_w changes only with the commissioned paired predictive player MC."""
    if not screens:
        return None
    _prepare_predictive_confirmation(ctx, predictive_cache)
    opponent = np.asarray(predictive_cache["_opponent"], dtype=float)
    baseline_weekly = _predictive_weekly_cached(roster, ctx, predictive_cache)
    baseline_utility = _future_h2h_utility(baseline_weekly, opponent, ctx, int(week))
    accepted: list[dict[str, Any]] = []
    for row in screens:
        trial = list(row["_new_roster"])
        trial_weekly = _predictive_weekly_cached(trial, ctx, predictive_cache)
        trial_utility = _future_h2h_utility(trial_weekly, opponent, ctx, int(week))
        delta = np.asarray(trial_utility - baseline_utility, dtype=float)
        p16, p84 = _paired_mean_interval(
            delta,
            seed=int(ctx.seed) + 350000 + 101 * int(week) + int(row["add_espn_id"]) - int(row["drop_espn_id"]),
            draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)),
        )
        classification = _classify_paired_delta(delta, ctx.cfg, mean_p16=p16)
        week_delta = np.asarray(
            trial_weekly[:, int(week) - 1] - baseline_weekly[:, int(week) - 1],
            dtype=float,
        )
        week_gain = float(np.mean(week_delta))
        mean_delta = float(np.mean(delta))
        p_better = float(np.mean(delta > EPS))
        p_tie = float(np.mean(np.abs(delta) <= EPS))
        p_worse = float(np.mean(delta < -EPS))
        # Preserve the mature player-channel rule: a deterministic screen cannot
        # authorize a transaction.  The paired predictive response must itself be
        # resolved, and the decision week may not be sacrificed.
        if classification not in {"ACTIONABLE_EDGE", "POSSIBLE_EDGE"} or week_gain < -EPS:
            continue
        out = {k: v for k, v in row.items() if not k.startswith("_")}
        out.update({
            "predictive_direct_h2h_delta_mean": mean_delta,
            "predictive_mean_p16": float(p16),
            "predictive_mean_p84": float(p84),
            "predictive_p_better": p_better,
            "predictive_p_tie": p_tie,
            "predictive_p_worse": p_worse,
            "predictive_week_gain_points": week_gain,
            "predictive_classification": classification,
            "predictive_scenarios": int(predictive_cache["_scenarios"]),
            "transaction_model": PLAYER_TRANSACTION_MODEL,
            "confirmation_model": PLAYER_CONFIRMATION_MODEL,
            "_new_roster": trial,
        })
        accepted.append(out)
    if not accepted:
        return None
    accepted.sort(
        key=lambda row: (
            2 if row["predictive_classification"] == "ACTIONABLE_EDGE" else 1,
            float(row["predictive_direct_h2h_delta_mean"]),
            float(row["predictive_p_better"]),
            float(row["predictive_week_gain_points"]),
            -int(row["add_espn_id"]),
            -int(row["drop_espn_id"]),
        ),
        reverse=True,
    )
    return accepted[0]


def _best_future_swap(
    roster: list[dict[str, Any]],
    free_pool: dict[int, dict[str, Any]],
    ctx,
    week: int,
    screen_cache: dict,
    predictive_cache: dict,
) -> dict[str, Any] | None:
    screens = _screen_future_swaps(roster, free_pool, ctx, int(week), screen_cache)
    return _confirm_screened_future_swaps(roster, screens, ctx, int(week), predictive_cache)


def build_temporal_player_states(ctx) -> dict[int, TemporalPlayerState]:
    """Propagate our ordinary-player membership causally from the synchronized state.

    Current-week membership is observed and therefore immutable here; authoritative
    current actions remain the commissioned roster-actions problem. Beginning next
    modeled week, the deterministic expected-lineup layer may screen candidate FREEAGENT
    swaps, but P_w changes only when the paired predictive player MC resolves a direct
    player-channel edge without worsening that decision week. Current WAIVERS are not
    fabricated as guaranteed acquisitions. Other managers' player transactions are
    intentionally not simulated until v0.36.
    """
    start = max(1, int(ctx.week))
    roster = [dict(p) for p in (getattr(ctx, "roster", []) or [])]
    free_pool, excluded_waivers = _guaranteed_free_pool(ctx)
    if not roster:
        return {
            start: TemporalPlayerState(
                week=start, roster=[], free_pool={int(k): dict(v) for k, v in free_pool.items()},
                transaction=None, expected_remaining_ppg=0.0, expected_week_points=0.0,
                guaranteed_free_agents=len(free_pool), excluded_current_waivers=excluded_waivers,
            )
        }
    score_cache: dict = {}
    predictive_cache: dict = {}
    states: dict[int, TemporalPlayerState] = {}
    season_score, week_score = _roster_score_cached(roster, ctx, start, score_cache)
    states[start] = TemporalPlayerState(
        week=start,
        roster=[dict(p) for p in roster],
        free_pool={int(k): dict(v) for k, v in free_pool.items()},
        transaction=None,
        expected_remaining_ppg=season_score,
        expected_week_points=week_score,
        guaranteed_free_agents=len(free_pool),
        excluded_current_waivers=excluded_waivers,
    )

    dropped_next: dict[int, dict[str, Any]] = {}
    try:
        for week in range(start + 1, 18):
            if dropped_next:
                free_pool.update({int(k): dict(v) for k, v in dropped_next.items()})
                dropped_next = {}
            proposal = _best_future_swap(
                roster, free_pool, ctx, week, score_cache, predictive_cache
            )
            transaction = None
            if proposal is not None:
                add_id = int(proposal["add_espn_id"])
                drop_id = int(proposal["drop_espn_id"])
                add = free_pool.pop(add_id, None)
                drop = next((p for p in roster if _pid(p) == drop_id), None)
                if add is not None and drop is not None:
                    roster = [p for p in roster if _pid(p) != drop_id] + [dict(add)]
                    released = dict(drop)
                    released["fantasy_status"] = "FREEAGENT"
                    released["on_team_id"] = None
                    released["lineup_slot"] = "BENCH"
                    dropped_next[drop_id] = released
                    transaction = {k: v for k, v in proposal.items() if not k.startswith("_")}
            season_score, week_score = _roster_score_cached(roster, ctx, week, score_cache)
            states[week] = TemporalPlayerState(
                week=week,
                roster=[dict(p) for p in roster],
                free_pool={int(k): dict(v) for k, v in free_pool.items()},
                transaction=transaction,
                expected_remaining_ppg=season_score,
                expected_week_points=week_score,
                guaranteed_free_agents=len(free_pool),
                excluded_current_waivers=excluded_waivers,
            )
    finally:
        _restore_predictive_confirmation(ctx, predictive_cache)
    return states


def state_for_week(states: dict[int, TemporalPlayerState], week: int) -> TemporalPlayerState:
    if int(week) in states:
        return states[int(week)]
    eligible = [w for w in states if int(w) <= int(week)]
    if not eligible:
        raise KeyError(f"no temporal player state available for week {week}")
    return states[max(eligible)]


def summarize_temporal_player_states(states: dict[int, TemporalPlayerState]) -> dict[str, Any]:
    ordered = [states[w] for w in sorted(states)]
    transactions = [dict(state.transaction) for state in ordered if state.transaction]
    return {
        "player_state_model": PLAYER_STATE_MODEL,
        "transaction_model": PLAYER_TRANSACTION_MODEL,
        "screen_model": PLAYER_SCREEN_MODEL,
        "confirmation_model": PLAYER_CONFIRMATION_MODEL,
        "external_market_model": EXTERNAL_PLAYER_MARKET_MODEL,
        "information_policy": PLAYER_INFORMATION_POLICY,
        "composition_order": STATE_COMPOSITION_ORDER,
        "weeks": [state.to_dict() for state in ordered],
        "transactions": transactions,
        "transaction_count": len(transactions),
    }
