from __future__ import annotations

import copy
import itertools
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .market_manager import (
    _paired_mean_interval,
    perceived_market_value,
    roster_is_legal,
    trade_response_probabilities,
)
from .season_utility import week_weights
from .specialist_policy_v032 import (
    SpecialistPolicyResult,
    _compose_state,
    _scenario_h2h_utility_against,
    _static_team_weekly,
)
from .transaction_manager import (
    PLAYER_POSITIONS,
    POSITIONS,
    McProgressCallback,
    UtilityContext,
    _finite_int,
    _legal_drop,
    evaluate_roster_predictive,
    evaluate_roster_utility,
)
from .weekly_manager import resolve_team
from .trade_timing import (
    require_trade_settings,
    resolve_trade_timing,
    season_ppg_from_weekly,
    splice_effective_week,
)


SPECIALIST_POSITIONS = ("DST", "K")
SUPPORTED_FAMILIES = ("1x1", "1x2", "2x1", "2x2")


def _pid(player: dict[str, Any] | None) -> int | None:
    return _finite_int((player or {}).get("espn_id"))


def _position(player: dict[str, Any] | None) -> str:
    return str((player or {}).get("position") or "").upper()


def _team_id(team: dict[str, Any]) -> int | None:
    return _finite_int(team.get("team_id"))


def _lookup(roster: Iterable[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for player in roster:
        pid = _pid(player)
        if pid is not None:
            out[int(pid)] = dict(player)
    return out


def _score_fast(roster: list[dict[str, Any]], ctx: UtilityContext) -> float:
    result = evaluate_roster_utility(roster, ctx)
    return float(result.season_expected_lineup_ppg) + 0.10 * float(result.bench_insurance_ppg)


def _minimum_deficits(roster: list[dict[str, Any]], league: dict[str, Any]) -> dict[str, int]:
    counts = {pos: 0 for pos in POSITIONS}
    for player in roster:
        pos = _position(player)
        if pos in counts:
            counts[pos] += 1
    minimums = league.get("roster") or {}
    return {
        pos: max(int(minimums.get(pos, 0)) - int(counts.get(pos, 0)), 0)
        for pos in ("QB", "RB", "WR", "TE", "K", "DST")
    }


def _best_mixed_auto_drops(
    roster: list[dict[str, Any]],
    *,
    original_size: int,
    incoming_ids: set[int],
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Normalize an overfull mixed roster at the complete-roster boundary.

    Candidate releases may come from P, D, or K.  They are never compared as
    individual cross-channel values; each legal release set is ranked only by
    complete-roster utility.
    """
    excess = max(0, len(roster) - int(original_size))
    if excess == 0:
        if not roster_is_legal(roster, league, target_size=original_size):
            raise ValueError("mixed trade leaves an illegal roster")
        return [dict(p) for p in roster], []
    if excess > 2:
        raise ValueError("mixed trade supports at most two automatic post-trade releases")

    candidates = [
        dict(player)
        for player in roster
        if _legal_drop(player)
        and _position(player) in POSITIONS
        and (_pid(player) not in incoming_ids)
    ]
    if len(candidates) < excess:
        raise ValueError("not enough legal mixed post-trade release candidates")

    by_id = {_pid(player): player for player in candidates if _pid(player) is not None}
    best_roster: list[dict[str, Any]] | None = None
    best_drops: list[dict[str, Any]] | None = None
    best_score = -float("inf")
    for combo in itertools.combinations(sorted(int(pid) for pid in by_id), excess):
        drop_ids = set(combo)
        trial = [dict(p) for p in roster if _pid(p) not in drop_ids]
        if not roster_is_legal(trial, league, target_size=original_size):
            continue
        score = _score_fast(trial, ctx)
        if score > best_score:
            best_score = score
            best_roster = trial
            best_drops = [dict(by_id[pid]) for pid in combo]
    if best_roster is None or best_drops is None:
        raise ValueError("no legal mixed post-trade release set preserves roster constraints")
    return best_roster, best_drops


def _fill_pool(
    roster: list[dict[str, Any]],
    *,
    league: dict[str, Any],
    ctx: UtilityContext,
) -> list[dict[str, Any]]:
    """Return guaranteed fills without inventing a new specialist-carry policy.

    Player FREEAGENTs retain the existing Gate B3 fill semantics.  DST/K
    FREEAGENTs become eligible only when the post-trade roster is below the
    league minimum for that same specialist channel.
    """
    deficits = _minimum_deficits(roster, league)
    required_specialists = {
        pos for pos in SPECIALIST_POSITIONS if int(deficits.get(pos, 0)) > 0
    }
    existing = {_pid(player) for player in roster}
    out: list[dict[str, Any]] = []
    for candidate in ctx.actionable_available:
        pid = _pid(candidate)
        pos = _position(candidate)
        if pid is None or pid in existing:
            continue
        if str(candidate.get("fantasy_status") or "").upper() != "FREEAGENT":
            continue
        if pos in PLAYER_POSITIONS or pos in required_specialists:
            out.append(dict(candidate))
    return out


def _best_mixed_auto_fills(
    roster: list[dict[str, Any]],
    *,
    original_size: int,
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Model guaranteed post-trade fills, never waiver success."""
    current = [dict(player) for player in roster]
    open_slots = max(0, int(original_size) - len(current))
    if open_slots == 0:
        if not roster_is_legal(current, league, target_size=original_size):
            raise ValueError("mixed trade leaves an illegal roster")
        return current, []

    pool = _fill_pool(current, league=league, ctx=ctx)
    best_roster: list[dict[str, Any]] | None = None
    best_fills: list[dict[str, Any]] = []
    best_score = -float("inf")

    # Prefer filling all available open slots, but permit a smaller legal roster
    # when no guaranteed FREEAGENT exists for every open slot.
    max_fill = min(open_slots, len(pool))
    sizes = list(range(max_fill, 0, -1)) + [0]
    for size in sizes:
        for combo in itertools.combinations(pool, size):
            trial = current + [dict(player) for player in combo]
            if not roster_is_legal(trial, league, target_size=original_size):
                continue
            score = _score_fast(trial, ctx)
            if score > best_score:
                best_score = score
                best_roster = trial
                best_fills = [dict(player) for player in combo]
        if best_roster is not None:
            break
    if best_roster is None:
        raise ValueError("no legal guaranteed FREEAGENT fill state preserves roster constraints")
    return best_roster, best_fills



def _best_mixed_normalization(
    roster: list[dict[str, Any]],
    *,
    original_size: int,
    incoming_ids: set[int],
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Find the minimum-churn legal post-trade roster state.

    Size imbalance is not the only capacity problem: an equal-count package can
    violate a position minimum or maximum.  We therefore try the minimum number
    of legal releases needed to make a valid state, and only then rank alternatives
    by complete-roster utility.  Guaranteed FREEAGENT fills are explicit and waiver
    success is never assumed.
    """
    raw = [dict(player) for player in roster]
    excess = max(0, len(raw) - int(original_size))
    if excess > 2:
        raise ValueError("mixed trade supports at most two automatic post-trade releases")

    candidates = [
        dict(player)
        for player in raw
        if _legal_drop(player)
        and _position(player) in POSITIONS
        and (_pid(player) not in incoming_ids)
    ]
    by_id = {_pid(player): player for player in candidates if _pid(player) is not None}

    minimum_drop_count = excess
    maximum_drop_count = min(2, len(by_id))
    for drop_count in range(minimum_drop_count, maximum_drop_count + 1):
        legal_states: list[
            tuple[float, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]
        ] = []
        combos = itertools.combinations(sorted(int(pid) for pid in by_id), drop_count)
        for drop_combo in combos:
            drop_ids = set(drop_combo)
            after_drop = [dict(player) for player in raw if _pid(player) not in drop_ids]
            if len(after_drop) > int(original_size):
                continue
            open_slots = max(0, int(original_size) - len(after_drop))
            fill_pool = _fill_pool(after_drop, league=league, ctx=ctx)
            max_fill = min(open_slots, len(fill_pool))
            # Prefer using the real open capacity when guaranteed FREEAGENTs exist,
            # while still permitting a smaller legal roster if no fill is available.
            for fill_count in range(max_fill, -1, -1):
                for fill_combo in itertools.combinations(fill_pool, fill_count):
                    final = after_drop + [dict(player) for player in fill_combo]
                    if not roster_is_legal(final, league, target_size=original_size):
                        continue
                    score = _score_fast(final, ctx)
                    legal_states.append((
                        score,
                        final,
                        [dict(by_id[pid]) for pid in drop_combo],
                        [dict(player) for player in fill_combo],
                    ))
                if legal_states:
                    break
        if legal_states:
            legal_states.sort(key=lambda item: item[0], reverse=True)
            _, final, drops, fills = legal_states[0]
            return final, drops, fills

    raise ValueError("no legal mixed post-trade capacity/drop/fill state exists")

def apply_specialist_trade_package(
    roster: list[dict[str, Any]],
    outgoing_ids: Iterable[int],
    incoming: Iterable[dict[str, Any]],
    *,
    league: dict[str, Any],
    ctx: UtilityContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    outgoing = {int(value) for value in outgoing_ids}
    lookup = _lookup(roster)
    missing = sorted(outgoing - set(lookup))
    if missing:
        raise ValueError(f"outgoing asset(s) not on roster: {missing}")

    incoming_rows = [dict(player) for player in incoming]
    incoming_ids = {_pid(player) for player in incoming_rows}
    incoming_ids = {int(pid) for pid in incoming_ids if pid is not None}
    if outgoing & incoming_ids:
        raise ValueError("the same asset cannot be both incoming and outgoing")

    original_size = len(roster)
    after = [dict(player) for player in roster if _pid(player) not in outgoing]
    after.extend(incoming_rows)
    return _best_mixed_normalization(
        after,
        original_size=original_size,
        incoming_ids=incoming_ids,
        league=league,
        ctx=ctx,
    )


def _rehome_player(
    player: dict[str, Any],
    *,
    team_id: int,
    outgoing: list[dict[str, Any]],
) -> dict[str, Any]:
    out = copy.deepcopy(player)
    same_position = [row for row in outgoing if _position(row) == _position(player)]
    if same_position:
        template = same_position[0]
        for key in ("lineup_slot_id", "lineup_slot", "lineup_locked"):
            if key in template:
                out[key] = copy.deepcopy(template.get(key))
    else:
        out["lineup_slot"] = "BENCH"
        out["lineup_locked"] = False
    out["fantasy_status"] = "ROSTERED"
    out["on_team_id"] = int(team_id)
    return out


def _normalize_incoming_assignments(
    original: list[dict[str, Any]],
    final: list[dict[str, Any]],
    *,
    team_id: int,
    incoming_ids: set[int],
    outgoing_ids: set[int],
) -> list[dict[str, Any]]:
    outgoing = [dict(row) for row in original if _pid(row) in outgoing_ids]
    original_ids = {_pid(row) for row in original}
    rows: list[dict[str, Any]] = []
    for player in final:
        pid = _pid(player)
        if pid in incoming_ids:
            row = _rehome_player(player, team_id=team_id, outgoing=outgoing)
        else:
            row = copy.deepcopy(player)
            if pid not in original_ids:
                row["lineup_slot"] = "BENCH"
                row["lineup_locked"] = False
        row["fantasy_status"] = "ROSTERED"
        row["on_team_id"] = int(team_id)
        rows.append(row)
    return rows


def _snapshot_with_rosters(
    snapshot: dict[str, Any],
    rosters: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    out = copy.deepcopy(snapshot)
    espn = out.get("espn", out)
    for team in espn.get("teams") or []:
        tid = _team_id(team)
        if tid is not None and int(tid) in rosters:
            team["roster"] = copy.deepcopy(rosters[int(tid)])
    return out


def _hybrid_player_snapshot(
    original_snapshot: dict[str, Any],
    final_snapshot: dict[str, Any],
    team_ids: Iterable[int],
) -> dict[str, Any]:
    """Apply final P ownership while keeping original D/K ownership.

    This is the production form of the read-only v3 audit decomposition.  The
    result is an intermediate state, not a league transaction state.
    """
    original = original_snapshot.get("espn", original_snapshot)
    final = final_snapshot.get("espn", final_snapshot)
    original_by_team = {
        int(tid): list(team.get("roster") or [])
        for team in original.get("teams") or []
        if (tid := _team_id(team)) is not None
    }
    final_by_team = {
        int(tid): list(team.get("roster") or [])
        for team in final.get("teams") or []
        if (tid := _team_id(team)) is not None
    }
    hybrid: dict[int, list[dict[str, Any]]] = {}
    for tid in team_ids:
        original_roster = original_by_team[int(tid)]
        final_roster = final_by_team[int(tid)]
        players = [copy.deepcopy(row) for row in final_roster if _position(row) in PLAYER_POSITIONS]
        specialists = [copy.deepcopy(row) for row in original_roster if _position(row) in SPECIALIST_POSITIONS]
        hybrid[int(tid)] = players + specialists
    return _snapshot_with_rosters(original_snapshot, hybrid)


def _fixed_ownership_policy(
    position: str,
    static: dict[int, np.ndarray],
    ctx: UtilityContext,
) -> SpecialistPolicyResult:
    weekly = {int(key): np.asarray(value, dtype=float) for key, value in static.items()}
    if int(ctx.team_id) not in weekly:
        raise ValueError(f"missing {position} team state for team {ctx.team_id}")
    weekly[-1] = np.asarray(weekly[int(ctx.team_id)], dtype=float)
    capacity = sum(1 for player in ctx.roster if _position(player) == position)
    return SpecialistPolicyResult(
        position=position,
        mode="TRADE_FIXED_OWNERSHIP_V001",
        user_capacity=int(capacity),
        team_weekly=weekly,
        user_plan=[],
        transactions=[],
        guaranteed_free_agents_initial=0,
        excluded_current_waivers=0,
    )


def _scenario_season_ppg(weekly: np.ndarray, ctx: UtilityContext) -> np.ndarray:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    return np.sum(np.asarray(weekly, dtype=float) * weights[None, :], axis=1) / norm


def _delta_summary(delta: np.ndarray) -> dict[str, float]:
    arr = np.asarray(delta, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "sd": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "p10": float(np.quantile(arr, 0.10)),
        "p50": float(np.quantile(arr, 0.50)),
        "p90": float(np.quantile(arr, 0.90)),
        "p_better": float(np.mean(arr > 0.0)),
        "p_worse": float(np.mean(arr < 0.0)),
        "mc_scenarios": int(len(arr)),
    }


def _context(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    values_path: str | Path,
    team_id: int,
    scenarios: int,
) -> UtilityContext:
    team = resolve_team(snapshot, team_id=int(team_id))
    ctx = UtilityContext(snapshot, league, model, values_path, team)
    ctx.set_predictive_scenarios(int(scenarios))
    return ctx


def _baseline_state(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    values_path: str | Path,
    team_id: int,
    scenarios: int,
    *,
    progress_callback: McProgressCallback | None = None,
    progress_label: str,
) -> tuple[UtilityContext, np.ndarray, np.ndarray, np.ndarray]:
    ctx = _context(snapshot, league, model, values_path, team_id, scenarios)
    ctx.ensure_predictive_opponent_reference()
    _, utility, weekly = evaluate_roster_predictive(
        ctx.roster,
        ctx,
        include_diagnostics=False,
        progress_callback=progress_callback,
        progress_label=progress_label,
    )
    opponent = np.asarray(ctx.opponent_predictive, dtype=float)
    return (
        ctx,
        np.asarray(utility, dtype=float),
        np.asarray(weekly, dtype=float),
        opponent,
    )


def _composed_after_state(
    hybrid_snapshot: dict[str, Any],
    final_snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    values_path: str | Path,
    team_id: int,
    scenarios: int,
    *,
    progress_callback: McProgressCallback | None = None,
    progress_label: str,
) -> tuple[UtilityContext, np.ndarray, np.ndarray, np.ndarray]:
    hybrid_ctx = _context(hybrid_snapshot, league, model, values_path, team_id, scenarios)
    final_ctx = _context(final_snapshot, league, model, values_path, team_id, scenarios)
    hybrid_ctx.ensure_predictive_opponent_reference()
    _, _, player_weekly = evaluate_roster_predictive(
        hybrid_ctx.roster,
        hybrid_ctx,
        include_diagnostics=False,
        progress_callback=progress_callback,
        progress_label=progress_label,
    )
    base_opponent = np.asarray(hybrid_ctx.opponent_predictive, dtype=float)

    d_static = _static_team_weekly(hybrid_ctx, "DST")
    k_static = _static_team_weekly(hybrid_ctx, "K")
    d_final = _static_team_weekly(final_ctx, "DST")
    k_final = _static_team_weekly(final_ctx, "K")
    d_policy = _fixed_ownership_policy("DST", d_final, final_ctx)
    k_policy = _fixed_ownership_policy("K", k_final, final_ctx)
    final_weekly, final_opponent, final_utility = _compose_state(
        np.asarray(player_weekly, dtype=float),
        base_opponent,
        hybrid_ctx,
        d_policy=d_policy,
        k_policy=k_policy,
        d_static=d_static,
        k_static=k_static,
    )
    return (
        hybrid_ctx,
        np.asarray(final_utility, dtype=float),
        np.asarray(final_weekly, dtype=float),
        np.asarray(final_opponent, dtype=float),
    )


def _package_family(give_ids: Iterable[int], receive_ids: Iterable[int]) -> str:
    return f"{len(tuple(give_ids))}x{len(tuple(receive_ids))}"


def _contains_specialist(rows: Iterable[dict[str, Any]]) -> bool:
    return any(_position(row) in SPECIALIST_POSITIONS for row in rows)


def _assert_supported_trade_specialist_state(
    roster: Iterable[dict[str, Any]],
    *,
    side: str,
) -> None:
    kickers = [player for player in roster if _position(player) == "K"]
    if len(kickers) > 1:
        raise ValueError(
            f"{side} specialist-trade state requires unsupported multi-K ownership; "
            "general two-kicker policy is disabled"
        )


def evaluate_specialist_trade(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    user_team: dict[str, Any],
    partner_team_id: int,
    give_ids: list[int],
    receive_ids: list[int],
    mc_scenarios: int | None = None,
    progress_callback: McProgressCallback | None = None,
) -> dict[str, Any]:
    """Evaluate a DST/K-inclusive package without changing player-trade authority."""
    if not give_ids or not receive_ids:
        raise ValueError("specialist trade requires at least one asset from each team")

    local_model = copy.deepcopy(model)
    cfg = local_model.get("market_manager") or {}
    max_side = min(2, max(1, int(cfg.get("trade_max_players_per_side", 2))))
    if len(give_ids) > max_side or len(receive_ids) > max_side:
        raise ValueError(f"specialist trade supports at most {max_side} assets per side")
    family = _package_family(give_ids, receive_ids)
    if family not in SUPPORTED_FAMILIES:
        raise ValueError(f"unsupported specialist trade package family: {family}")

    scenarios = int(
        mc_scenarios
        or cfg.get("trade_search_mc_scenarios")
        or (local_model.get("transaction_manager") or {}).get("predictive_mc_scenarios", 4096)
    )
    if scenarios < 2:
        raise ValueError("specialist trade predictive MC requires at least two scenarios")

    user_tid = _team_id(user_team)
    if user_tid is None:
        raise ValueError("user team id is missing")
    partner = resolve_team(snapshot, team_id=int(partner_team_id))
    partner_tid = _team_id(partner)
    if partner_tid is None or int(partner_tid) == int(user_tid):
        raise ValueError("invalid specialist trade partner")

    user_ctx = _context(snapshot, league, local_model, values_path, int(user_tid), scenarios)
    partner_ctx = _context(snapshot, league, local_model, values_path, int(partner_tid), scenarios)
    user_lookup = _lookup(user_ctx.roster)
    partner_lookup = _lookup(partner_ctx.roster)
    missing_give = sorted(set(int(x) for x in give_ids) - set(user_lookup))
    missing_receive = sorted(set(int(x) for x in receive_ids) - set(partner_lookup))
    if missing_give:
        raise ValueError(f"give asset(s) not on user roster: {missing_give}")
    if missing_receive:
        raise ValueError(f"receive asset(s) not on partner roster: {missing_receive}")

    give = [dict(user_lookup[int(pid)]) for pid in give_ids]
    receive = [dict(partner_lookup[int(pid)]) for pid in receive_ids]
    if not (_contains_specialist(give) or _contains_specialist(receive)):
        raise ValueError(
            "specialist trade authority requires at least one DST/K asset; "
            "player-only packages remain under market_manager.evaluate_trade"
        )

    require_trade_settings(snapshot)

    user_after, user_drops, user_adds = apply_specialist_trade_package(
        user_ctx.roster, give_ids, receive, league=league, ctx=user_ctx,
    )
    partner_after, partner_drops, partner_adds = apply_specialist_trade_package(
        partner_ctx.roster, receive_ids, give, league=league, ctx=partner_ctx,
    )

    user_after = _normalize_incoming_assignments(
        user_ctx.roster,
        user_after,
        team_id=int(user_tid),
        incoming_ids=set(int(x) for x in receive_ids),
        outgoing_ids=set(int(x) for x in give_ids),
    )
    partner_after = _normalize_incoming_assignments(
        partner_ctx.roster,
        partner_after,
        team_id=int(partner_tid),
        incoming_ids=set(int(x) for x in give_ids),
        outgoing_ids=set(int(x) for x in receive_ids),
    )
    if not roster_is_legal(user_after, league, target_size=len(user_ctx.roster)):
        raise ValueError("normalized user specialist-trade roster is illegal")
    if not roster_is_legal(partner_after, league, target_size=len(partner_ctx.roster)):
        raise ValueError("normalized partner specialist-trade roster is illegal")

    _assert_supported_trade_specialist_state(user_after, side="user")
    _assert_supported_trade_specialist_state(partner_after, side="partner")

    timing = resolve_trade_timing(
        snapshot,
        user_ctx.week,
        [
            *[("user_give", p, user_ctx) for p in give],
            *[("partner_receive", p, partner_ctx) for p in receive],
            *[("user_auto_drop", p, user_ctx) for p in user_drops],
            *[("partner_auto_drop", p, partner_ctx) for p in partner_drops],
            *[("user_auto_add", p, user_ctx) for p in user_adds],
            *[("partner_auto_add", p, partner_ctx) for p in partner_adds],
        ],
    )

    final_snapshot = _snapshot_with_rosters(
        snapshot, {int(user_tid): user_after, int(partner_tid): partner_after},
    )
    hybrid_snapshot = _hybrid_player_snapshot(
        snapshot, final_snapshot, (int(user_tid), int(partner_tid)),
    )

    ub_ctx, user_base_u, user_base_w, user_base_o = _baseline_state(
        snapshot, league, local_model, values_path, int(user_tid), scenarios,
        progress_callback=progress_callback,
        progress_label="specialist trade user baseline",
    )
    pb_ctx, partner_base_u, partner_base_w, partner_base_o = _baseline_state(
        snapshot, league, local_model, values_path, int(partner_tid), scenarios,
        progress_callback=progress_callback,
        progress_label="specialist trade partner baseline",
    )
    ua_ctx, _user_after_u_immediate, user_after_w_immediate, user_after_o_immediate = _composed_after_state(
        hybrid_snapshot, final_snapshot, league, local_model, values_path,
        int(user_tid), scenarios,
        progress_callback=progress_callback,
        progress_label="specialist trade user after",
    )
    pa_ctx, _partner_after_u_immediate, partner_after_w_immediate, partner_after_o_immediate = _composed_after_state(
        hybrid_snapshot, final_snapshot, league, local_model, values_path,
        int(partner_tid), scenarios,
        progress_callback=progress_callback,
        progress_label="specialist trade partner after",
    )

    user_after_w = splice_effective_week(
        user_base_w, user_after_w_immediate, timing.effective_week
    )
    partner_after_w = splice_effective_week(
        partner_base_w, partner_after_w_immediate, timing.effective_week
    )
    user_after_o = splice_effective_week(
        user_base_o, user_after_o_immediate, timing.effective_week
    )
    partner_after_o = splice_effective_week(
        partner_base_o, partner_after_o_immediate, timing.effective_week
    )
    user_after_u = _scenario_h2h_utility_against(user_after_w, user_after_o, ua_ctx)
    partner_after_u = _scenario_h2h_utility_against(
        partner_after_w, partner_after_o, pa_ctx
    )

    user_base_s = season_ppg_from_weekly(user_base_w, ub_ctx.league, ub_ctx.week)
    partner_base_s = season_ppg_from_weekly(
        partner_base_w, pb_ctx.league, pb_ctx.week
    )
    user_after_s = season_ppg_from_weekly(user_after_w, ua_ctx.league, ua_ctx.week)
    partner_after_s = season_ppg_from_weekly(
        partner_after_w, pa_ctx.league, pa_ctx.week
    )

    user_delta = user_after_s - user_base_s
    partner_delta = partner_after_s - partner_base_s
    user_utility_delta = user_after_u - user_base_u
    partner_utility_delta = partner_after_u - partner_base_u
    user_week_delta = user_after_w[:, ub_ctx.week - 1] - user_base_w[:, ub_ctx.week - 1]
    partner_week_delta = (
        partner_after_w[:, pb_ctx.week - 1] - partner_base_w[:, pb_ctx.week - 1]
    )

    partner_market_receive = sum(perceived_market_value(player, partner_ctx) for player in give)
    partner_market_give = sum(perceived_market_value(player, partner_ctx) for player in receive)
    partner_market_drop = sum(perceived_market_value(player, partner_ctx) for player in partner_drops)
    partner_market_fill = sum(perceived_market_value(player, partner_ctx) for player in partner_adds)
    partner_market_delta = float(
        partner_market_receive - partner_market_give - partner_market_drop + partner_market_fill
    )
    response = trade_response_probabilities(
        partner_delta_season_ppg=float(np.mean(partner_delta)),
        partner_p_better=float(np.mean(partner_delta > 0.0)),
        partner_market_delta=partner_market_delta,
        package_size=len(give_ids) + len(receive_ids),
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

    user_p16, user_p84 = _paired_mean_interval(
        user_delta,
        seed=ub_ctx.seed + 7919 * int(partner_tid) + sum(give_ids) + 3 * sum(receive_ids),
        draws=int((local_model.get("transaction_manager") or {}).get("paired_mean_interval_resamples", 1000)),
    )
    partner_p16, partner_p84 = _paired_mean_interval(
        partner_delta,
        seed=pb_ctx.seed + 104729 * int(partner_tid) + sum(receive_ids) + 5 * sum(give_ids),
        draws=int((local_model.get("transaction_manager") or {}).get("paired_mean_interval_resamples", 1000)),
    )

    return {
        "schema_version": 1,
        "model_version": "0.36-specialist-trade-timing-v001",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_utc": snapshot.get("snapshot_utc"),
        "season": int((snapshot.get("espn", snapshot).get("season") or 2026)),
        "week": int((snapshot.get("espn", snapshot).get("week") or 1)),
        "trade_timing": timing.as_dict(),
        "package_family": family,
        "specialist_inclusive": True,
        "user_team": {"team_id": int(user_tid), "name": user_team.get("name")},
        "partner_team": {"team_id": int(partner_tid), "name": partner.get("name")},
        "give": [dict(player) for player in give],
        "receive": [dict(player) for player in receive],
        "user_auto_drops": [dict(player) for player in user_drops],
        "partner_auto_drops": [dict(player) for player in partner_drops],
        "user_auto_adds": [dict(player) for player in user_adds],
        "partner_auto_adds": [dict(player) for player in partner_adds],
        "user": {
            "delta_season_ppg": _delta_summary(user_delta),
            "delta_current_week": _delta_summary(user_week_delta),
            "delta_complete_state_utility": _delta_summary(user_utility_delta),
            "delta_mean_interval_p16": user_p16,
            "delta_mean_interval_p84": user_p84,
        },
        "partner": {
            "delta_season_ppg": _delta_summary(partner_delta),
            "delta_current_week": _delta_summary(partner_week_delta),
            "delta_complete_state_utility": _delta_summary(partner_utility_delta),
            "delta_mean_interval_p16": partner_p16,
            "delta_mean_interval_p84": partner_p84,
            "market_delta": partner_market_delta,
        },
        "response": asdict(response),
        "expected_offer_value": expected_offer_value,
        "classification": classification,
        "mc_scenarios": scenarios,
        "screen_authority": False,
        "player_trade_authority_unchanged": "market_manager.evaluate_trade",
        "specialist_composition": "P_PLUS_D_PLUS_K_AT_COMPLETE_ROSTER_BOUNDARY",
        "notes": [
            "Player-only Gate B3 authority is unchanged; this evaluator is specialist-inclusive only.",
            "Trade ownership, automatic releases, and guaranteed fills are applied only from the causally legal effective week; commissioner early processing is never assumed.",
            "Player ownership is propagated first; DST/K ownership is valued through specialist response machinery and composed only at the complete-roster boundary.",
            "Automatic mixed-package releases are ranked by complete-roster utility, never individual cross-channel asset comparison.",
            "Guaranteed FREEAGENT fills may include DST/K only when required to restore that same specialist channel's roster minimum; waiver success is never assumed.",
            "Manager accept/counter/reject probability remains a separate behavior layer and does not alter intrinsic football response.",
        ],
    }


def _candidate_packages(
    players: list[dict[str, Any]],
    *,
    max_players_per_side: int,
) -> list[tuple[dict[str, Any], ...]]:
    packages = [(player,) for player in players]
    if int(max_players_per_side) >= 2:
        packages.extend(tuple(combo) for combo in itertools.combinations(players, 2))
    return packages


def _candidate_assets(
    roster: list[dict[str, Any]],
    *,
    player_limit: int,
    giving: bool,
) -> list[dict[str, Any]]:
    player_rows = [
        dict(player)
        for player in roster
        if _position(player) in PLAYER_POSITIONS and (not giving or _legal_drop(player))
    ]
    player_rows.sort(
        key=lambda player: float(player.get("season_ppg") or 0.0),
        reverse=not giving,
    )
    specialists = [
        dict(player)
        for player in roster
        if _position(player) in SPECIALIST_POSITIONS and (not giving or _legal_drop(player))
    ]
    rows = player_rows[: max(2, int(player_limit))] + specialists
    seen: set[int] = set()
    out: list[dict[str, Any]] = []
    for player in rows:
        pid = _pid(player)
        if pid is None or int(pid) in seen:
            continue
        seen.add(int(pid))
        out.append(player)
    return out


def _raw_package_after(
    roster: list[dict[str, Any]],
    outgoing_ids: Iterable[int],
    incoming: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    outgoing = {int(pid) for pid in outgoing_ids}
    return [dict(player) for player in roster if _pid(player) not in outgoing] + [
        dict(player) for player in incoming
    ]


def _specialist_signature(
    give: Iterable[dict[str, Any]],
    receive: Iterable[dict[str, Any]],
) -> str:
    positions = {_position(player) for player in itertools.chain(give, receive)}
    channels = [position for position in SPECIALIST_POSITIONS if position in positions]
    return "+".join(channels)


def _balanced_frontier(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    cap = max(1, int(limit))
    ordered = sorted(rows, key=lambda row: float(row.get("screen_score") or 0.0), reverse=True)
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in ordered:
        key = (str(row.get("package_family") or ""), str(row.get("specialist_channels") or ""))
        buckets.setdefault(key, []).append(row)
    selected: list[dict[str, Any]] = []
    used: set[tuple[int, tuple[int, ...], tuple[int, ...]]] = set()

    def marker(row: dict[str, Any]) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
        return (
            int(row["partner_team_id"]),
            tuple(int(x) for x in row.get("give_ids") or []),
            tuple(int(x) for x in row.get("receive_ids") or []),
        )

    active = [key for key in buckets if buckets[key]]
    index = 0
    while active and len(selected) < cap:
        key = active[index % len(active)]
        bucket = buckets[key]
        while bucket:
            row = bucket.pop(0)
            mk = marker(row)
            if mk not in used:
                used.add(mk)
                selected.append(row)
                break
        active = [item for item in active if buckets[item]]
        index += 1
    return selected


def screen_specialist_trade_packages(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    user_team: dict[str, Any],
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Cheap complete-roster screen for packages containing at least one DST/K."""
    user_ctx = UtilityContext(snapshot, league, model, values_path, user_team)
    cfg = model.get("market_manager") or {}
    max_package = min(2, max(1, int(cfg.get("trade_max_players_per_side", 2))))
    give_limit = max(2, int(cfg.get("trade_search_give_candidates", 8)))
    target_limit = max(2, int(cfg.get("trade_search_target_candidates", 10)))
    user_assets = _candidate_assets(user_ctx.roster, player_limit=give_limit, giving=True)
    user_packages = _candidate_packages(user_assets, max_players_per_side=max_package)
    base_user_fast = _score_fast(user_ctx.roster, user_ctx)

    rows: list[dict[str, Any]] = []
    espn = snapshot.get("espn", snapshot)
    for team in espn.get("teams") or []:
        tid = _team_id(team)
        if tid is None or int(tid) == int(user_ctx.team_id):
            continue
        partner_team = resolve_team(snapshot, team_id=int(tid))
        partner_ctx = UtilityContext(snapshot, league, model, values_path, partner_team)
        partner_roster = list(partner_ctx.roster)
        partner_assets = _candidate_assets(
            partner_roster, player_limit=target_limit, giving=False
        )
        partner_packages = _candidate_packages(
            partner_assets, max_players_per_side=max_package
        )
        base_partner_fast = _score_fast(partner_roster, partner_ctx)

        for give in user_packages:
            for receive in partner_packages:
                if not (_contains_specialist(give) or _contains_specialist(receive)):
                    continue
                family = f"{len(give)}x{len(receive)}"
                if family not in SUPPORTED_FAMILIES:
                    continue
                give_ids = [_pid(player) for player in give]
                receive_ids = [_pid(player) for player in receive]
                if any(pid is None for pid in give_ids + receive_ids):
                    continue

                raw_user = _raw_package_after(
                    user_ctx.roster,
                    [int(pid) for pid in give_ids if pid is not None],
                    receive,
                )
                raw_partner = _raw_package_after(
                    partner_roster,
                    [int(pid) for pid in receive_ids if pid is not None],
                    give,
                )
                user_gain = _score_fast(raw_user, user_ctx) - base_user_fast
                partner_gain = _score_fast(raw_partner, partner_ctx) - base_partner_fast
                minimum = float(cfg.get("trade_search_min_user_screen_gain", 0.15))
                if user_gain <= minimum:
                    continue
                score = user_gain + 0.75 * partner_gain - 0.25 * abs(user_gain - partner_gain)
                rows.append({
                    "partner_team_id": int(tid),
                    "partner_name": team.get("name"),
                    "package_family": family,
                    "specialist_channels": _specialist_signature(give, receive),
                    "give_ids": [int(pid) for pid in give_ids if pid is not None],
                    "give_names": [str(player.get("name") or _pid(player)) for player in give],
                    "give_positions": [_position(player) for player in give],
                    "receive_ids": [int(pid) for pid in receive_ids if pid is not None],
                    "receive_names": [str(player.get("name") or _pid(player)) for player in receive],
                    "receive_positions": [_position(player) for player in receive],
                    "user_screen_gain_complete_roster": float(user_gain),
                    "partner_screen_gain_complete_roster": float(partner_gain),
                    "screen_score": float(score),
                    "screen_authority": False,
                })
    return _balanced_frontier(rows, limit=max(int(limit), 1))


def search_specialist_trades(
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
    require_trade_settings(snapshot)
    cfg = model.get("market_manager") or {}
    screen_limit = max(
        int(limit),
        int(cfg.get("trade_search_screen_limit", 18)),
        len(SUPPORTED_FAMILIES),
    )
    screened = screen_specialist_trade_packages(
        snapshot,
        league,
        model,
        values_path=values_path,
        user_team=user_team,
        limit=screen_limit,
    )
    scenarios = int(mc_scenarios or cfg.get("trade_search_mc_scenarios", 4096))
    results: list[dict[str, Any]] = []
    for row in screened:
        try:
            result = evaluate_specialist_trade(
                snapshot,
                league,
                model,
                values_path=values_path,
                user_team=user_team,
                partner_team_id=int(row["partner_team_id"]),
                give_ids=[int(x) for x in row.get("give_ids") or []],
                receive_ids=[int(x) for x in row.get("receive_ids") or []],
                mc_scenarios=scenarios,
                progress_callback=None,
            )
        except (ValueError, RuntimeError):
            continue
        results.append({
            **row,
            "classification": result["classification"],
            "our_delta_season_ppg": result["user"]["delta_season_ppg"]["mean"],
            "our_p_better": result["user"]["delta_season_ppg"]["p_better"],
            "our_delta_complete_state_utility": result["user"]["delta_complete_state_utility"]["mean"],
            "partner_delta_season_ppg": result["partner"]["delta_season_ppg"]["mean"],
            "partner_p_better": result["partner"]["delta_season_ppg"]["p_better"],
            "partner_delta_complete_state_utility": result["partner"]["delta_complete_state_utility"]["mean"],
            "p_accept": result["response"]["p_accept"],
            "p_counter": result["response"]["p_counter"],
            "p_reject": result["response"]["p_reject"],
            "expected_offer_value": result["expected_offer_value"],
            "user_auto_drop_ids": [_pid(player) for player in result.get("user_auto_drops") or []],
            "partner_auto_drop_ids": [_pid(player) for player in result.get("partner_auto_drops") or []],
            "user_auto_add_ids": [_pid(player) for player in result.get("user_auto_adds") or []],
            "partner_auto_add_ids": [_pid(player) for player in result.get("partner_auto_adds") or []],
            "mc_scenarios": result["mc_scenarios"],
            "specialist_composition": result["specialist_composition"],
        })
    results.sort(
        key=lambda row: (
            row.get("classification") == "ACTIONABLE_OFFER",
            float(row.get("expected_offer_value") or -999.0),
            float(row.get("our_delta_complete_state_utility") or -999.0),
        ),
        reverse=True,
    )
    return results[: max(1, int(limit))]
