from __future__ import annotations

import itertools
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

from .season_utility import week_weights
from .transaction_manager import (
    POSITIONS,
    PLAYER_POSITIONS,
    McProgressCallback,
    RosterUtilityResult,
    UtilityContext,
    _classify_paired_delta,
    _finite_float,
    _finite_int,
    _legal_drop,
    _paired_mean_interval,
    _simulate_predictive_weekly_points,
    evaluate_roster_utility,
)
from .weekly_manager import resolve_team


@dataclass(frozen=True)
class SeasonScenarioSummary:
    mean_ppg: float
    sd_ppg: float
    current_week_mean: float
    current_week_sd: float
    p10_ppg: float
    p50_ppg: float
    p90_ppg: float
    mc_scenarios: int


@dataclass(frozen=True)
class TradeResponseProbabilities:
    p_accept: float
    p_counter: float
    p_reject: float
    model: str


TRADE_RESPONSE_MODEL = "UNCALIBRATED_TRADE_RESPONSE_V030"
WAIVER_RESPONSE_MODEL = "UNCALIBRATED_MANAGER_CLAIM_UTILITY_V030"


def _safe_softmax(values: list[float]) -> list[float]:
    arr = np.asarray(values, dtype=float)
    arr = arr - float(np.max(arr))
    exp = np.exp(np.clip(arr, -50.0, 50.0))
    total = float(np.sum(exp))
    if total <= 0.0 or not math.isfinite(total):
        return [1.0 / len(values)] * len(values)
    return [float(x / total) for x in exp]


def _quantile_summary(values: np.ndarray, current_week: np.ndarray) -> SeasonScenarioSummary:
    arr = np.asarray(values, dtype=float)
    week = np.asarray(current_week, dtype=float)
    return SeasonScenarioSummary(
        mean_ppg=float(np.mean(arr)) if len(arr) else 0.0,
        sd_ppg=float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        current_week_mean=float(np.mean(week)) if len(week) else 0.0,
        current_week_sd=float(np.std(week, ddof=1)) if len(week) > 1 else 0.0,
        p10_ppg=float(np.quantile(arr, 0.10)) if len(arr) else 0.0,
        p50_ppg=float(np.quantile(arr, 0.50)) if len(arr) else 0.0,
        p90_ppg=float(np.quantile(arr, 0.90)) if len(arr) else 0.0,
        mc_scenarios=int(len(arr)),
    )


def evaluate_roster_season_scenarios(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    *,
    progress_callback: McProgressCallback | None = None,
    progress_offset: int = 0,
    progress_total: int | None = None,
    progress_label: str = "roster season value",
) -> tuple[SeasonScenarioSummary, np.ndarray, np.ndarray]:
    """Evaluate full predictive roster scoring without constructing an opponent reference.

    Trade acceptance is a season-roster question.  We therefore keep the detailed
    player-level predictive MC and common-random-number structure, but compare roster
    lineup PPG directly rather than spending another whole-league MC pass to define a
    partner's current H2H opponent.  This is also the paired quantity used for partner
    trade-benefit probabilities.
    """
    weekly = _simulate_predictive_weekly_points(
        roster,
        ctx,
        ctx.replacement_current,
        ctx.replacement_season,
        current_week_policy="realistic",
        progress_callback=progress_callback,
        progress_offset=progress_offset,
        progress_total=progress_total,
        progress_label=progress_label,
    )
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    season = np.sum(weekly * weights[None, :], axis=1) / norm
    current = weekly[:, ctx.week - 1]
    return _quantile_summary(season, current), season, weekly


def _roster_position_counts(roster: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {p: 0 for p in POSITIONS}
    for player in roster:
        pos = str(player.get("position") or "")
        if pos in counts:
            counts[pos] += 1
    return counts


def roster_is_legal(roster: list[dict[str, Any]], league: dict[str, Any], *, target_size: int | None = None) -> bool:
    if target_size is not None and len(roster) > int(target_size):
        return False
    counts = _roster_position_counts(roster)
    maxima = league.get("position_maximums") or {}
    for pos, maximum in maxima.items():
        if pos in counts and counts[pos] > int(maximum):
            return False
    minimums = league.get("roster") or {}
    for pos in ("QB", "RB", "WR", "TE", "K", "DST"):
        if counts.get(pos, 0) < int(minimums.get(pos, 0)):
            return False
    return True


def _player_lookup(roster: Iterable[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is not None:
            out[pid] = player
    return out


def _best_auto_drops(
    roster: list[dict[str, Any]],
    *,
    original_size: int,
    incoming_ids: set[int],
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Keep a trade roster at its pre-trade size by making the best modeled release(s)."""
    excess = max(0, len(roster) - int(original_size))
    if excess == 0:
        if not roster_is_legal(roster, league, target_size=original_size):
            raise ValueError("trade leaves an illegal roster")
        return roster, []
    if excess > 2:
        raise ValueError("v0.30 supports at most two automatic post-trade releases")

    candidates = [
        p for p in roster
        if _legal_drop(p)
        and str(p.get("position") or "").upper() in PLAYER_POSITIONS
        and (_finite_int(p.get("espn_id")) not in incoming_ids)
    ]
    if len(candidates) < excess:
        raise ValueError("not enough legal post-trade release candidates")

    best_roster: list[dict[str, Any]] | None = None
    best_drops: list[dict[str, Any]] | None = None
    best_value = -float("inf")
    candidate_ids = {_finite_int(p.get("espn_id")): p for p in candidates}
    for drop_combo in itertools.combinations([pid for pid in candidate_ids if pid is not None], excess):
        drop_set = set(int(x) for x in drop_combo)
        final = [p for p in roster if _finite_int(p.get("espn_id")) not in drop_set]
        if not roster_is_legal(final, league, target_size=original_size):
            continue
        fast = evaluate_roster_utility(final, ctx)
        score = float(fast.season_expected_lineup_ppg) + 0.10 * float(fast.bench_insurance_ppg)
        if score > best_value:
            best_value = score
            best_roster = final
            best_drops = [candidate_ids[x] for x in drop_combo]
    if best_roster is None or best_drops is None:
        raise ValueError("no legal post-trade release set preserves roster constraints")
    return best_roster, best_drops


def _best_auto_fills(
    roster: list[dict[str, Any]],
    *,
    original_size: int,
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fill net-open trade slots with the best currently guaranteed FREEAGENT.

    A 2-for-1 trade creates a real roster slot.  Treating that slot as worthless would
    systematically penalize consolidation trades.  v0.30 therefore models the best
    immediately available free-agent fill, but never assumes a waiver claim succeeds.
    The fill is surfaced explicitly in every trade report.
    """
    current = [dict(p) for p in roster]
    fills: list[dict[str, Any]] = []
    existing = {_finite_int(p.get("espn_id")) for p in current}
    while len(current) < int(original_size):
        best = None
        best_value = -float("inf")
        for candidate in ctx.actionable_available:
            if str(candidate.get("position") or "").upper() not in PLAYER_POSITIONS:
                continue
            pid = _finite_int(candidate.get("espn_id"))
            if pid is None or pid in existing:
                continue
            if str(candidate.get("fantasy_status") or "").upper() != "FREEAGENT":
                continue
            trial = current + [dict(candidate)]
            if not roster_is_legal(trial, league, target_size=original_size):
                continue
            utility = evaluate_roster_utility(trial, ctx)
            score = float(utility.season_expected_lineup_ppg) + 0.10 * float(utility.bench_insurance_ppg)
            if score > best_value:
                best_value = score
                best = dict(candidate)
        if best is None:
            break
        current.append(best)
        fills.append(best)
        existing.add(_finite_int(best.get("espn_id")))
    return current, fills


def apply_trade_package(
    roster: list[dict[str, Any]],
    outgoing_ids: Iterable[int],
    incoming: Iterable[dict[str, Any]],
    *,
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    outgoing = {int(x) for x in outgoing_ids}
    lookup = _player_lookup(roster)
    missing = sorted(outgoing - set(lookup))
    if missing:
        raise ValueError(f"outgoing player(s) not on roster: {missing}")
    incoming_rows = [dict(p) for p in incoming]
    incoming_ids = {_finite_int(p.get("espn_id")) for p in incoming_rows}
    incoming_ids = {int(x) for x in incoming_ids if x is not None}
    if outgoing & incoming_ids:
        raise ValueError("the same player cannot be both incoming and outgoing")
    original_size = len(roster)
    after = [dict(p) for p in roster if _finite_int(p.get("espn_id")) not in outgoing]
    after.extend(incoming_rows)
    after, drops = _best_auto_drops(
        after,
        original_size=original_size,
        incoming_ids=incoming_ids,
        league=league,
        ctx=ctx,
    )
    after, fills = _best_auto_fills(
        after, original_size=original_size, league=league, ctx=ctx
    )
    return after, drops, fills


def _espn_market_ppg(player: dict[str, Any]) -> float:
    season = _finite_float(player.get("season_projection"))
    if season is not None and season > 0:
        return season / 17.0
    weekly = _finite_float(player.get("projection_points"))
    if weekly is not None and weekly > 0:
        return weekly
    weekly = _finite_float(player.get("weekly_projection"))
    if weekly is not None and weekly > 0:
        return weekly
    return max(_finite_float(player.get("season_ppg")) or 0.0, 0.0)


def perceived_market_value(player: dict[str, Any], ctx: UtilityContext) -> float:
    """A deliberately separate manager-perception channel, not our roster utility.

    It uses ESPN projected production plus public ownership/trend observables.  It does
    not use our action delta and is therefore suitable as an independent acceptance
    feature rather than a generic external trade-value chart.
    """
    pos = str(player.get("position") or "")
    ppg = _espn_market_ppg(player)
    replacement = float(ctx.replacement_season.get(pos, 0.0))
    surplus = max(ppg - replacement, 0.0)
    owned = max(_finite_float(player.get("percent_owned")) or 0.0, 0.0)
    adds = max(_finite_int(player.get("sleeper_trending_add_24h")) or 0, 0)
    drops = max(_finite_int(player.get("sleeper_trending_drop_24h")) or 0, 0)
    trend = math.log1p(adds) - 0.5 * math.log1p(drops)
    cfg = ctx.model.get("market_manager") or {}
    return float(
        float(cfg.get("market_base_ppg_weight", 0.20)) * ppg
        + float(cfg.get("market_surplus_weight", 0.80)) * surplus
        + float(cfg.get("market_owned_weight", 0.012)) * owned
        + float(cfg.get("market_trend_weight", 0.05)) * trend
    )


def trade_response_probabilities(
    *,
    partner_delta_season_ppg: float,
    partner_p_better: float,
    partner_market_delta: float,
    package_size: int,
    cfg: dict[str, Any],
) -> TradeResponseProbabilities:
    """Provisional three-way manager response model, kept separate from valuation."""
    gain = float(partner_delta_season_ppg)
    pbetter = min(max(float(partner_p_better), 0.0), 1.0)
    market = float(partner_market_delta)
    package_penalty = max(int(package_size) - 2, 0)

    accept = (
        float(cfg.get("trade_accept_intercept", -0.35))
        + float(cfg.get("trade_accept_season_ppg_weight", 1.15)) * gain
        + float(cfg.get("trade_accept_pbetter_weight", 1.50)) * (pbetter - 0.5)
        + float(cfg.get("trade_accept_market_weight", 0.30)) * market
        - float(cfg.get("trade_package_complexity_penalty", 0.15)) * package_penalty
    )
    # Counteroffers are most likely near the acceptance boundary rather than when the
    # trade is either clearly favorable or clearly poor.
    counter = (
        float(cfg.get("trade_counter_intercept", -0.15))
        - float(cfg.get("trade_counter_abs_gain_weight", 0.60)) * abs(gain)
        - float(cfg.get("trade_counter_abs_market_weight", 0.15)) * abs(market)
        + float(cfg.get("trade_counter_small_deficit_bonus", 0.30)) * min(max(-gain, 0.0), 1.0)
    )
    reject = (
        float(cfg.get("trade_reject_intercept", 0.0))
        + float(cfg.get("trade_reject_negative_gain_weight", 1.10)) * max(-gain, 0.0)
        + float(cfg.get("trade_reject_negative_market_weight", 0.25)) * max(-market, 0.0)
    )
    p_accept, p_counter, p_reject = _safe_softmax([accept, counter, reject])
    return TradeResponseProbabilities(p_accept, p_counter, p_reject, TRADE_RESPONSE_MODEL)


def _partner_team(snapshot: dict[str, Any], team_id: int) -> dict[str, Any]:
    espn = snapshot.get("espn", snapshot)
    for team in espn.get("teams") or []:
        if _finite_int(team.get("team_id")) == int(team_id):
            return team
    raise ValueError(f"partner team id {team_id} not found")


def _scenario_delta_summary(delta: np.ndarray) -> dict[str, float]:
    arr = np.asarray(delta, dtype=float)
    return {
        "mean": float(np.mean(arr)) if len(arr) else 0.0,
        "sd": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "p10": float(np.quantile(arr, 0.10)) if len(arr) else 0.0,
        "p50": float(np.quantile(arr, 0.50)) if len(arr) else 0.0,
        "p90": float(np.quantile(arr, 0.90)) if len(arr) else 0.0,
        "p_better": float(np.mean(arr > 0.0)) if len(arr) else 0.0,
        "p_tie": float(np.mean(arr == 0.0)) if len(arr) else 0.0,
        "p_worse": float(np.mean(arr < 0.0)) if len(arr) else 0.0,
    }


def evaluate_trade(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    user_team: dict[str, Any],
    partner_team_id: int,
    give_ids: Iterable[int],
    receive_ids: Iterable[int],
    mc_scenarios: int | None = None,
    progress_callback: McProgressCallback | None = None,
) -> dict[str, Any]:
    """Evaluate a hypothetical trade for both managers with paired predictive MC."""
    give_ids = [int(x) for x in give_ids]
    receive_ids = [int(x) for x in receive_ids]
    if not give_ids or not receive_ids:
        raise ValueError("trade must contain at least one player on each side")
    max_package = int((model.get("market_manager") or {}).get("trade_max_players_per_side", 2))
    if len(give_ids) > max_package or len(receive_ids) > max_package:
        raise ValueError(f"v0.30 supports at most {max_package} players per side")

    partner = _partner_team(snapshot, int(partner_team_id))
    if _finite_int(partner.get("team_id")) == _finite_int(user_team.get("team_id")):
        raise ValueError("trade partner must be another team")

    # UtilityContext keeps mutable MC-size state inside the model dictionary.  Trade
    # searches often use a smaller candidate-generation N, so isolate that state from
    # the live GUI/service model before changing predictive_scenarios.
    local_model = json.loads(json.dumps(model))
    user_ctx = UtilityContext(snapshot, league, local_model, values_path, user_team)
    partner_ctx = UtilityContext(snapshot, league, local_model, values_path, partner)
    if mc_scenarios is not None:
        user_ctx.set_predictive_scenarios(int(mc_scenarios))
        partner_ctx.set_predictive_scenarios(int(mc_scenarios))

    user_lookup = _player_lookup(user_ctx.roster)
    partner_lookup = _player_lookup(partner_ctx.roster)
    missing_give = [pid for pid in give_ids if pid not in user_lookup]
    missing_receive = [pid for pid in receive_ids if pid not in partner_lookup]
    if missing_give:
        raise ValueError(f"give player(s) not on user roster: {missing_give}")
    if missing_receive:
        raise ValueError(f"receive player(s) not on partner roster: {missing_receive}")

    give = [user_lookup[pid] for pid in give_ids]
    receive = [partner_lookup[pid] for pid in receive_ids]
    specialist_names = [
        str(p.get("name") or p.get("espn_id"))
        for p in give + receive
        if str(p.get("position") or "").upper() not in PLAYER_POSITIONS
    ]
    if specialist_names:
        raise ValueError(
            "v0.31 trade channel is player-only (QB/RB/WR/TE); specialist assets belong to the DST/K management channels: "
            + ", ".join(specialist_names)
        )

    user_after, user_auto_drops, user_auto_adds = apply_trade_package(
        user_ctx.roster,
        give_ids,
        receive,
        league=league,
        ctx=user_ctx,
    )
    partner_after, partner_auto_drops, partner_auto_adds = apply_trade_package(
        partner_ctx.roster,
        receive_ids,
        give,
        league=league,
        ctx=partner_ctx,
    )

    # Four visible passes: user baseline/after and partner baseline/after.  Each pass
    # uses the same player-keyed random streams within that manager context.
    weeks = max(1, 18 - max(user_ctx.week, 1))
    per_pass = weeks * user_ctx.predictive_scenarios
    total_work = 4 * per_pass
    ub, user_base_s, user_base_w = evaluate_roster_season_scenarios(
        user_ctx.roster, user_ctx,
        progress_callback=progress_callback, progress_offset=0,
        progress_total=total_work, progress_label="trade user baseline",
    )
    ua, user_after_s, user_after_w = evaluate_roster_season_scenarios(
        user_after, user_ctx,
        progress_callback=progress_callback, progress_offset=per_pass,
        progress_total=total_work, progress_label="trade user after",
    )
    pb, partner_base_s, partner_base_w = evaluate_roster_season_scenarios(
        partner_ctx.roster, partner_ctx,
        progress_callback=progress_callback, progress_offset=2 * per_pass,
        progress_total=total_work, progress_label="trade partner baseline",
    )
    pa, partner_after_s, partner_after_w = evaluate_roster_season_scenarios(
        partner_after, partner_ctx,
        progress_callback=progress_callback, progress_offset=3 * per_pass,
        progress_total=total_work, progress_label="trade partner after",
    )

    user_delta = np.asarray(user_after_s) - np.asarray(user_base_s)
    partner_delta = np.asarray(partner_after_s) - np.asarray(partner_base_s)
    user_week_delta = np.asarray(user_after_w[:, user_ctx.week - 1]) - np.asarray(user_base_w[:, user_ctx.week - 1])
    partner_week_delta = np.asarray(partner_after_w[:, partner_ctx.week - 1]) - np.asarray(partner_base_w[:, partner_ctx.week - 1])

    cfg = local_model.get("market_manager") or {}
    partner_market_receive = sum(perceived_market_value(p, partner_ctx) for p in give)
    partner_market_give = sum(perceived_market_value(p, partner_ctx) for p in receive)
    partner_market_drop = sum(perceived_market_value(p, partner_ctx) for p in partner_auto_drops)
    partner_market_fill = sum(perceived_market_value(p, partner_ctx) for p in partner_auto_adds)
    partner_market_delta = float(partner_market_receive - partner_market_give - partner_market_drop + partner_market_fill)

    response = trade_response_probabilities(
        partner_delta_season_ppg=float(np.mean(partner_delta)),
        partner_p_better=float(np.mean(partner_delta > 0.0)),
        partner_market_delta=partner_market_delta,
        package_size=len(give) + len(receive),
        cfg=cfg,
    )
    expected_offer_value = float(response.p_accept * np.mean(user_delta))

    classification = "NO_RESOLVED_EDGE"
    if float(np.mean(user_delta)) > 0 and float(np.mean(partner_delta)) > 0:
        classification = "MUTUAL_MODEL_GAIN"
        if response.p_accept >= float(cfg.get("trade_actionable_accept_probability", 0.40)):
            classification = "ACTIONABLE_OFFER"
    elif float(np.mean(user_delta)) > 0:
        classification = "OUR_EDGE_PARTNER_LOSS"
    elif float(np.mean(partner_delta)) > 0:
        classification = "PARTNER_EDGE_OUR_LOSS"

    user_summary = _scenario_delta_summary(user_delta)
    partner_summary = _scenario_delta_summary(partner_delta)
    user_week_summary = _scenario_delta_summary(user_week_delta)
    partner_week_summary = _scenario_delta_summary(partner_week_delta)
    user_p16, user_p84 = _paired_mean_interval(
        user_delta,
        seed=user_ctx.seed + 7919 * int(partner_team_id) + sum(give_ids) + 3 * sum(receive_ids),
        draws=int((local_model.get("transaction_manager") or {}).get("paired_mean_interval_resamples", 1000)),
    )
    partner_p16, partner_p84 = _paired_mean_interval(
        partner_delta,
        seed=partner_ctx.seed + 104729 * int(partner_team_id) + sum(receive_ids) + 5 * sum(give_ids),
        draws=int((local_model.get("transaction_manager") or {}).get("paired_mean_interval_resamples", 1000)),
    )

    return {
        "schema_version": 1,
        "model_version": "0.30",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_utc": snapshot.get("snapshot_utc"),
        "season": int((snapshot.get("espn", snapshot).get("season") or 2026)),
        "week": int((snapshot.get("espn", snapshot).get("week") or 1)),
        "user_team": {"team_id": _finite_int(user_team.get("team_id")), "name": user_team.get("name")},
        "partner_team": {"team_id": _finite_int(partner.get("team_id")), "name": partner.get("name")},
        "give": [dict(p) for p in give],
        "receive": [dict(p) for p in receive],
        "user_auto_drops": [dict(p) for p in user_auto_drops],
        "partner_auto_drops": [dict(p) for p in partner_auto_drops],
        "user_auto_adds": [dict(p) for p in user_auto_adds],
        "partner_auto_adds": [dict(p) for p in partner_auto_adds],
        "user": {
            "baseline": asdict(ub),
            "after": asdict(ua),
            "delta_season_ppg": user_summary,
            "delta_mean_interval_p16": user_p16,
            "delta_mean_interval_p84": user_p84,
            "delta_current_week": user_week_summary,
        },
        "partner": {
            "baseline": asdict(pb),
            "after": asdict(pa),
            "delta_season_ppg": partner_summary,
            "delta_mean_interval_p16": partner_p16,
            "delta_mean_interval_p84": partner_p84,
            "delta_current_week": partner_week_summary,
            "market_delta": partner_market_delta,
        },
        "response": asdict(response),
        "expected_offer_value": expected_offer_value,
        "classification": classification,
        "mc_scenarios": user_ctx.predictive_scenarios,
        "notes": [
            "Trade value and partner response probability are separate layers.",
            "Both managers' roster deltas use the same commissioned player-yield, K, interaction, availability, bye, and lock-aware predictive machinery.",
            "Partner acceptance/counter/reject probabilities are explicitly uncalibrated v0.30 manager-behavior priors and do not alter our player valuation.",
            "No external trade-value chart is used; the independent market-perception feature is derived from ESPN projections plus public ownership/trend observables.",
            "Unequal package sizes may trigger a modeled best legal post-trade release and/or guaranteed free-agent slot fill; both are surfaced explicitly.",
        ],
    }


def _need_multiplier(roster: list[dict[str, Any]], player: dict[str, Any], league: dict[str, Any]) -> float:
    pos = str(player.get("position") or "")
    counts = _roster_position_counts(roster)
    starters = league.get("roster") or {}
    base_need = int(starters.get(pos, 0))
    if pos in {"RB", "WR", "TE"}:
        base_need += 1 if int(starters.get("FLEX", 0)) > 0 else 0
    deficit = max(base_need - counts.get(pos, 0), 0)
    return 1.0 + 0.20 * deficit


def _coarse_trade_score(
    user_roster: list[dict[str, Any]],
    partner_roster: list[dict[str, Any]],
    give: dict[str, Any],
    receive: dict[str, Any],
    league: dict[str, Any],
) -> tuple[float, float]:
    give_ppg = float(give.get("season_ppg") or 0.0)
    receive_ppg = float(receive.get("season_ppg") or 0.0)
    user_gain = receive_ppg * _need_multiplier(user_roster, receive, league) - give_ppg * _need_multiplier(user_roster, give, league)
    partner_gain = give_ppg * _need_multiplier(partner_roster, give, league) - receive_ppg * _need_multiplier(partner_roster, receive, league)
    return float(user_gain), float(partner_gain)


def screen_one_for_one_trades(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    user_team: dict[str, Any],
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Cheap league-wide screen used only to choose offers for full predictive MC."""
    user_ctx = UtilityContext(snapshot, league, model, values_path, user_team)
    user_candidates = [p for p in user_ctx.roster if _legal_drop(p) and str(p.get("position") or "").upper() in PLAYER_POSITIONS]
    cfg = model.get("market_manager") or {}
    give_limit = max(2, int(cfg.get("trade_search_give_candidates", 8)))
    target_limit = max(2, int(cfg.get("trade_search_target_candidates", 10)))
    user_candidates = sorted(user_candidates, key=lambda p: float(p.get("season_ppg") or 0.0))[:give_limit]
    rows: list[dict[str, Any]] = []
    espn = snapshot.get("espn", snapshot)
    for team in espn.get("teams") or []:
        tid = _finite_int(team.get("team_id"))
        if tid is None or tid == user_ctx.team_id:
            continue
        roster = user_ctx.all_team_rosters.get(tid, [])
        targets = sorted([p for p in roster if str(p.get("position") or "").upper() in PLAYER_POSITIONS], key=lambda p: float(p.get("season_ppg") or 0.0), reverse=True)[:target_limit]
        for give in user_candidates:
            for receive in targets:
                ug, pg = _coarse_trade_score(user_ctx.roster, roster, give, receive, league)
                # The screen is permissive on partner cost but prioritizes offers that could
                # plausibly benefit both sides after positional-context effects.
                if ug <= float(cfg.get("trade_search_min_user_screen_gain", 0.15)):
                    continue
                combined = ug + 0.75 * pg - 0.25 * abs(ug - pg)
                rows.append({
                    "partner_team_id": tid,
                    "partner_name": team.get("name"),
                    "give_id": _finite_int(give.get("espn_id")),
                    "give_name": give.get("name"),
                    "give_position": give.get("position"),
                    "receive_id": _finite_int(receive.get("espn_id")),
                    "receive_name": receive.get("name"),
                    "receive_position": receive.get("position"),
                    "user_screen_gain_ppg": ug,
                    "partner_screen_gain_ppg": pg,
                    "screen_score": combined,
                })
    rows.sort(key=lambda r: float(r["screen_score"]), reverse=True)
    return rows[: max(1, int(limit))]


def search_trades(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    user_team: dict[str, Any],
    limit: int = 6,
    mc_scenarios: int | None = None,
    progress_callback: McProgressCallback | None = None,
) -> list[dict[str, Any]]:
    cfg = model.get("market_manager") or {}
    screen_limit = max(int(limit), int(cfg.get("trade_search_screen_limit", 18)))
    screened = screen_one_for_one_trades(
        snapshot, league, model, values_path=values_path, user_team=user_team, limit=screen_limit
    )
    search_mc = int(mc_scenarios or cfg.get("trade_search_mc_scenarios", 4096))
    results: list[dict[str, Any]] = []
    for i, row in enumerate(screened):
        try:
            result = evaluate_trade(
                snapshot, league, model,
                values_path=values_path,
                user_team=user_team,
                partner_team_id=int(row["partner_team_id"]),
                give_ids=[int(row["give_id"])],
                receive_ids=[int(row["receive_id"])],
                mc_scenarios=search_mc,
                progress_callback=None,  # candidate-level callback below keeps the UI legible
            )
        except (ValueError, RuntimeError):
            continue
        summary = {
            **row,
            "classification": result["classification"],
            "our_delta_season_ppg": result["user"]["delta_season_ppg"]["mean"],
            "our_p_better": result["user"]["delta_season_ppg"]["p_better"],
            "partner_delta_season_ppg": result["partner"]["delta_season_ppg"]["mean"],
            "partner_p_better": result["partner"]["delta_season_ppg"]["p_better"],
            "p_accept": result["response"]["p_accept"],
            "p_counter": result["response"]["p_counter"],
            "p_reject": result["response"]["p_reject"],
            "expected_offer_value": result["expected_offer_value"],
            "mc_scenarios": search_mc,
        }
        results.append(summary)
        if progress_callback is not None:
            progress_callback(i + 1, max(1, len(screened)), f"trade search {i + 1}/{len(screened)}")
    results.sort(
        key=lambda r: (
            float(r.get("expected_offer_value") or 0.0),
            float(r.get("our_delta_season_ppg") or 0.0),
        ),
        reverse=True,
    )
    return results[: max(1, int(limit))]


def save_trade_report(report: dict[str, Any], out_dir: str | Path = "data/season_decisions") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out / f"trade_eval_{stamp}.json"
    suffix = 1
    while path.exists():
        path = out / f"trade_eval_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
