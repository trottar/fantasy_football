from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .matchup_model import simulate_dst_component_points
from .data_sources.nflverse_matchups import normalize_team
from .season_utility import week_weights
from .transaction_manager import (
    UtilityContext,
    _finite_float,
    _finite_int,
    _legal_drop,
    evaluate_roster_utility,
)
from .weekly_manager import resolve_team
from .weekly_yield import sample_conditional_points

PLAYER_POSITIONS = {"QB", "RB", "WR", "TE"}
SPECIALIST_POSITIONS = {"DST", "K"}


@dataclass(frozen=True)
class SpecialistConfigurationSummary:
    weighted_mean_ppg: float
    weighted_sd_ppg: float
    current_week_mean: float
    current_week_sd: float
    current_week_choice: str | None
    mc_scenarios: int


def _snapshot_time(ctx: UtilityContext):
    text = ctx.snapshot.get("snapshot_utc") or ctx.espn.get("snapshot_utc")
    if not text:
        return None
    try:
        value = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _is_current_week_locked(player: dict[str, Any], ctx: UtilityContext) -> bool:
    if player.get("lineup_locked") is True:
        return True
    timing = ctx.lock_timing(player, ctx.week)
    snap = _snapshot_time(ctx)
    return bool(timing.kickoff is not None and snap is not None and timing.kickoff <= snap)


def _specialist_week_samples(player: dict[str, Any], ctx: UtilityContext, week: int) -> tuple[np.ndarray, float, dict[str, Any]]:
    """Return one specialist's weekly MC response in the specialist channel.

    This deliberately does not compare the specialist to QB/RB/WR/TE assets.  It
    exposes the existing position-specific predictive response as a weekly channel
    coordinate that can be combined with same-channel alternatives.
    """
    n = int(ctx.predictive_scenarios)
    pid = _finite_int(player.get("espn_id"))
    if pid is None:
        return np.zeros(n, dtype=float), 0.0, {}
    pos = str(player.get("position") or "").upper()
    team = normalize_team(player.get("nfl_team")) or ""
    bye = ctx.league.get("bye_weeks_2026", {}).get(team)
    try:
        on_bye = bye is not None and int(bye) == int(week)
    except (TypeError, ValueError):
        on_bye = False
    if on_bye:
        return np.zeros(n, dtype=float), 0.0, {"bye": True}

    state = ctx.yield_state(player, int(week))
    mean = float(state.operational_mean_ppg)
    if pos == "DST" and state.dst_component_expectation:
        samples = simulate_dst_component_points(
            state.dst_component_expectation,
            scenarios=n,
            seed=ctx.seed + 1000003 * int(pid) + 97 * int(week),
            target_mean=mean,
        )
        samples = (
            samples
            + state.model_sd_ppg * ctx.epistemic_normals(pid)
            + state.kinematic_sd_ppg * ctx.kinematic_normals(pid)[:, int(week) - 1]
        )
    else:
        samples = sample_conditional_points(
            state,
            ctx.epistemic_normals(pid),
            ctx.game_normals(pid)[:, int(week) - 1],
            ctx.kinematic_normals(pid)[:, int(week) - 1],
            ctx.interaction_normals(pid)[:, int(week) - 1],
        )

    # Kicker's v0.30 predictive state has no matchup coordinate.  v0.31 gives the
    # kicker channel a deliberately simple team-environment response using the same
    # schedule/game-total data already present in the matchup context.  This is a
    # channel-level prior, explicitly uncalibrated until prospective K closure exists.
    detail: dict[str, Any] = {
        "bye": False,
        "opponent": state.matchup_opponent,
        "source": state.kinematic_factor_source,
        "base_mean": mean,
    }
    if pos == "K":
        cfg = (ctx.model.get("specialist_channels") or {}).get("kicker", {})
        game = ((ctx.matchup_context.get("team_week") or {}).get(team, {}) or {}).get(str(int(week)))
        implied = _finite_float((game or {}).get("team_implied_points"))
        baseline = float(cfg.get("implied_points_baseline", 22.5))
        elasticity = float(cfg.get("implied_points_elasticity", 0.65))
        lower = float(cfg.get("matchup_factor_min", 0.82))
        upper = float(cfg.get("matchup_factor_max", 1.18))
        factor = 1.0
        if implied is not None and baseline > 1e-9:
            factor = float(np.clip((max(implied, 1.0) / baseline) ** elasticity, lower, upper))
        samples = np.asarray(samples, dtype=float) * factor
        mean *= factor
        detail.update({
            "opponent": (game or {}).get("opponent"),
            "team_implied_points": implied,
            "matchup_factor": factor,
            "source": "TEAM_IMPLIED_POINTS_KICKER_CHANNEL_V031" if implied is not None else "NEUTRAL_NO_TOTAL_KICKER_CHANNEL_V031",
        })
    elif pos == "DST":
        detail.update({
            "opponent": state.matchup_opponent,
            "team_implied_points": state.matchup_team_implied_points,
            "matchup_factor": state.kinematic_factor_mean,
            "source": state.kinematic_factor_source,
            "components": state.dst_component_expectation,
        })
    return np.asarray(samples, dtype=float), float(mean), detail


def _channel_configuration(
    specialists: Iterable[dict[str, Any]],
    ctx: UtilityContext,
    *,
    position: str,
) -> tuple[SpecialistConfigurationSummary, np.ndarray, list[dict[str, Any]]]:
    specialists = [dict(p) for p in specialists if str(p.get("position") or "").upper() == position]
    n = int(ctx.predictive_scenarios)
    weekly = np.zeros((n, 17), dtype=float)
    details: list[dict[str, Any]] = []
    current_choice = None
    for week in range(max(1, ctx.week), 18):
        choices: list[tuple[dict[str, Any], np.ndarray, float, dict[str, Any]]] = []
        for player in specialists:
            samples, mean, detail = _specialist_week_samples(player, ctx, week)
            choices.append((player, samples, mean, detail))
        if not choices:
            continue
        # Current-week ESPN locks are immutable.  If a specialist is already locked
        # into its scoring slot, preserve that starter before considering modeled
        # weekly expectations.  Otherwise lineup selection uses the pregame modeled
        # expectation. Realized samples score the already-selected specialist; there
        # is no hindsight max.
        locked_starters = []
        if week == ctx.week:
            for choice in choices:
                owned_player = choice[0]
                slot = str(owned_player.get("lineup_slot") or "").strip().upper()
                on_bench = slot in {"", "BENCH", "BE", "IR", "RESERVE"}
                if not on_bench and _is_current_week_locked(owned_player, ctx):
                    locked_starters.append(choice)
        if locked_starters:
            player, samples, mean, detail = locked_starters[0]
        else:
            player, samples, mean, detail = max(choices, key=lambda x: float(x[2]))
        weekly[:, week - 1] = samples
        if week == ctx.week:
            current_choice = str(player.get("name") or player.get("espn_id"))
        details.append({
            "week": int(week),
            "starter_espn_id": _finite_int(player.get("espn_id")),
            "starter_name": player.get("name"),
            "starter_team": player.get("nfl_team"),
            "expected_points": float(mean),
            **detail,
        })

    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0.0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    season = np.sum(weekly * weights[None, :], axis=1) / norm
    current = weekly[:, ctx.week - 1]
    return SpecialistConfigurationSummary(
        weighted_mean_ppg=float(np.mean(season)),
        weighted_sd_ppg=float(np.std(season, ddof=1)) if n > 1 else 0.0,
        current_week_mean=float(np.mean(current)),
        current_week_sd=float(np.std(current, ddof=1)) if n > 1 else 0.0,
        current_week_choice=current_choice,
        mc_scenarios=n,
    ), season, details


def _roster_active_capacity(league: dict[str, Any]) -> int:
    roster = league.get("roster") or {}
    # IR is a reserve state rather than an active roster/bench slot.
    return int(sum(int(v) for k, v in roster.items() if str(k).upper() != "IR"))


def _best_player_slot_release(ctx: UtilityContext) -> dict[str, Any] | None:
    """Ask the player sector for the least costly legal bench-slot release.

    This is intentionally a *player-sector* response.  No specialist is compared to a
    player directly.  The returned cost is used only after the specialist channel has
    calculated its own rotation/synergy gain.
    """
    baseline = evaluate_roster_utility(ctx.roster, ctx)
    best = None
    for player in ctx.roster:
        if str(player.get("position") or "").upper() not in PLAYER_POSITIONS or not _legal_drop(player):
            continue
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        trial = [p for p in ctx.roster if _finite_int(p.get("espn_id")) != pid]
        util = evaluate_roster_utility(trial, ctx)
        loss = max(float(baseline.season_expected_lineup_ppg - util.season_expected_lineup_ppg), 0.0)
        row = {
            "espn_id": pid,
            "name": player.get("name"),
            "position": player.get("position"),
            "season_lineup_cost_ppg": loss,
            "bench_insurance_cost_ppg": max(float(baseline.bench_insurance_ppg - util.bench_insurance_ppg), 0.0),
            "method": "PLAYER_CHANNEL_FAST_ROSTER_RESPONSE_V031",
        }
        if best is None or (row["season_lineup_cost_ppg"], row["bench_insurance_cost_ppg"]) < (
            best["season_lineup_cost_ppg"], best["bench_insurance_cost_ppg"]
        ):
            best = row
    return best


def _action_status(player: dict[str, Any]) -> str:
    raw = str(player.get("fantasy_status") or "").upper()
    return "WAIVERS" if raw in {"WAIVER", "WAIVERS"} else "FREEAGENT"


def _candidate_pool(ctx: UtilityContext, position: str) -> list[dict[str, Any]]:
    rows = [
        dict(p) for p in ctx.actionable_available
        if str(p.get("position") or "").upper() == position
        and str(p.get("fantasy_status") or "").upper() in {"FREEAGENT", "WAIVER", "WAIVERS"}
        and not _is_current_week_locked(p, ctx)
    ]
    # Same-channel preselection only; no cross-position market score.
    rows.sort(
        key=lambda p: (
            float(p.get("projection_points") or 0.0),
            float(p.get("season_ppg") or 0.0),
            float(p.get("percent_owned") or 0.0),
        ),
        reverse=True,
    )
    limit = int((ctx.model.get("specialist_channels") or {}).get("candidate_limit", 16))
    return rows[: max(1, limit)]


def evaluate_specialist_channel(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    position: str,
    values_path: str | Path = "data/processed/player_values_2026.csv",
    team_name: str | None = None,
    team_id: int | None = None,
    mc_scenarios: int | None = None,
) -> dict[str, Any]:
    position = str(position).upper()
    if position not in SPECIALIST_POSITIONS:
        raise ValueError("specialist channel position must be DST or K")
    team = resolve_team(snapshot, team_name=team_name, team_id=team_id)
    local_model = json.loads(json.dumps(model))
    ctx = UtilityContext(snapshot, league, local_model, values_path, team)
    cfg = local_model.get("specialist_channels") or {}
    n = int(mc_scenarios or cfg.get("mc_scenarios", 2048))
    ctx.set_predictive_scenarios(max(64, n))

    owned = [dict(p) for p in ctx.roster if str(p.get("position") or "").upper() == position]
    candidates = _candidate_pool(ctx, position)
    baseline_summary, baseline_s, baseline_weeks = _channel_configuration(owned, ctx, position=position)

    swaps: list[dict[str, Any]] = []
    for candidate in candidates:
        if not owned:
            configurations = [(None, [candidate])]
        else:
            configurations = []
            for outgoing in owned:
                # Same-channel swaps still obey transaction/lock physics. A specialist
                # whose lineup is already locked (including past kickoff) cannot be
                # removed from the current roster state.
                if not _legal_drop(outgoing) or _is_current_week_locked(outgoing, ctx):
                    continue
                config = [p for p in owned if _finite_int(p.get("espn_id")) != _finite_int(outgoing.get("espn_id"))] + [candidate]
                configurations.append((outgoing, config))
        best = None
        for outgoing, config in configurations:
            summary, season_s, week_detail = _channel_configuration(config, ctx, position=position)
            delta = np.asarray(season_s) - np.asarray(baseline_s)
            row = {
                "action": "ADD" if outgoing is None else "SWAP",
                "position": position,
                "add_espn_id": _finite_int(candidate.get("espn_id")),
                "add_name": candidate.get("name"),
                "add_team": candidate.get("nfl_team"),
                "drop_espn_id": _finite_int((outgoing or {}).get("espn_id")),
                "drop_name": (outgoing or {}).get("name"),
                "fantasy_status": _action_status(candidate),
                "delta_channel_ppg": float(np.mean(delta)),
                "delta_channel_sd_ppg": float(np.std(delta, ddof=1)) if len(delta) > 1 else 0.0,
                "p_channel_better": float(np.mean(delta > 0.0)),
                "current_week_delta": float(summary.current_week_mean - baseline_summary.current_week_mean),
                "after": asdict(summary),
                "weekly_plan": week_detail,
                "classification": "CHANNEL_UPGRADE" if float(np.mean(delta)) > 0 and float(np.mean(delta > 0)) >= 0.67 else "HOLD_CHANNEL",
            }
            if best is None or row["delta_channel_ppg"] > best["delta_channel_ppg"]:
                best = row
        if best is not None:
            swaps.append(best)
    swaps.sort(key=lambda r: (float(r["delta_channel_ppg"]), float(r["p_channel_better"])), reverse=True)

    carry: list[dict[str, Any]] = []
    allow_carry = bool(cfg.get("defense", {}).get("allow_second", True)) if position == "DST" else bool(cfg.get("kicker", {}).get("allow_second", False))
    max_pos = int((league.get("position_maximums") or {}).get(position, 1))
    if allow_carry and len(owned) < max_pos:
        active_capacity = _roster_active_capacity(league)
        needs_slot = len(ctx.roster) >= active_capacity
        slot_release = _best_player_slot_release(ctx) if needs_slot else None
        slot_cost = float((slot_release or {}).get("season_lineup_cost_ppg") or 0.0)
        slot_insurance = float((slot_release or {}).get("bench_insurance_cost_ppg") or 0.0)
        slot_weight = float(cfg.get("player_slot_insurance_weight", 0.25))
        total_slot_cost = slot_cost + slot_weight * slot_insurance
        for candidate in candidates:
            config = owned + [candidate]
            summary, season_s, week_detail = _channel_configuration(config, ctx, position=position)

            # A second specialist is valuable only for *complementarity*.  If the new
            # specialist is simply better than the incumbent every week, the correct
            # same-channel action is SWAP, not CARRY.  Compare the multi-specialist
            # state to the better one-specialist state selected on pregame expectation.
            candidate_only_summary, candidate_only_s, _candidate_only_weeks = _channel_configuration(
                [candidate], ctx, position=position
            )
            if candidate_only_summary.weighted_mean_ppg > baseline_summary.weighted_mean_ppg:
                best_one_summary = candidate_only_summary
                best_one_s = candidate_only_s
                best_one_name = str(candidate.get("name") or candidate.get("espn_id"))
            else:
                best_one_summary = baseline_summary
                best_one_s = baseline_s
                best_one_name = baseline_summary.current_week_choice
            delta = np.asarray(season_s) - np.asarray(best_one_s)
            synergy = float(np.mean(delta))
            net = synergy - total_slot_cost
            carry.append({
                "action": "CARRY_SECOND",
                "position": position,
                "add_espn_id": _finite_int(candidate.get("espn_id")),
                "add_name": candidate.get("name"),
                "add_team": candidate.get("nfl_team"),
                "fantasy_status": _action_status(candidate),
                "rotation_synergy_ppg": synergy,
                "rotation_synergy_sd_ppg": float(np.std(delta, ddof=1)) if len(delta) > 1 else 0.0,
                "p_rotation_better": float(np.mean(delta > 0.0)),
                "current_week_rotation_delta": float(summary.current_week_mean - best_one_summary.current_week_mean),
                "best_one_defense_state": best_one_name,
                "best_one_defense_ppg": float(best_one_summary.weighted_mean_ppg),
                "carry_baseline_kind": "BEST_STATIC_ONE_SPECIALIST_V031_FIXED2",
                "player_slot_lineup_cost_ppg": slot_cost,
                "player_slot_insurance_cost_ppg": slot_insurance,
                "player_slot_insurance_weight": slot_weight,
                "player_slot_cost_ppg": total_slot_cost,
                "player_slot_cost_method": "PLAYER_CHANNEL_SEASON_LINEUP_PLUS_WEIGHTED_INSURANCE_V031_FIXED2",
                "player_slot_release": slot_release,
                "net_complete_state_ppg": net,
                "net_screen_ppg": net,
                "net_complete_state_interpretation": "DIAGNOSTIC_SCREEN_ONLY_STATIC_ONE_SPECIALIST_BASELINE",
                "authoritative": False,
                "complete_state_confirmed": False,
                "after": asdict(summary),
                "weekly_plan": week_detail,
                "classification": "CARRY_SYNERGY_SCREEN" if net > 0.0 else "HOLD_CHANNEL",
            })
        carry.sort(key=lambda r: (float(r["net_complete_state_ppg"]), float(r["rotation_synergy_ppg"])), reverse=True)

    channel_name = "DEFENSE" if position == "DST" else "KICKER"
    return {
        "schema_version": 1,
        "model_version": "0.31-fixed3",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "season": ctx.espn.get("season"),
        "week": ctx.week,
        "team_id": ctx.team_id,
        "team_name": ctx.team.get("name"),
        "channel": channel_name,
        "position": position,
        "carry_policy_status": (
            "DIAGNOSTIC_STATIC_ONE_SPECIALIST_BASELINE_V031_FIXED2"
            if position == "DST" else "NOT_APPLICABLE"
        ),
        "mc_scenarios": int(ctx.predictive_scenarios),
        "owned": [
            {
                "espn_id": _finite_int(p.get("espn_id")),
                "name": p.get("name"),
                "team": p.get("nfl_team"),
                "locked": _is_current_week_locked(p, ctx),
            }
            for p in owned
        ],
        "baseline": asdict(baseline_summary),
        "swap_actions": swaps,
        "carry_actions": carry,
        "candidate_count": len(candidates),
        "notes": [
            "v0.31 separates QB/RB/WR/TE player-market decisions from DST and K management channels.",
            "Specialists are compared only against same-channel alternatives; no DST/RB or K/WR value coordinate is constructed.",
            "Weekly specialist lineup choices use pregame modeled means and realized MC only to score the selected specialist, preventing hindsight selection.",
            "A second-defense roster-slot cost is requested from the player sector after defense rotation synergy is calculated; the channels are combined only at the complete-state level.",
            "Kicker matchup response uses existing schedule game totals as an uncalibrated v0.31 channel prior pending prospective kicker closure.",
        ],
    }


def evaluate_defense_channel(*args, **kwargs) -> dict[str, Any]:
    return evaluate_specialist_channel(*args, position="DST", **kwargs)


def evaluate_kicker_channel(*args, **kwargs) -> dict[str, Any]:
    return evaluate_specialist_channel(*args, position="K", **kwargs)


def save_channel_report(report: dict[str, Any], out_dir: str | Path = "data/season_decisions") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    channel = str(report.get("channel") or "specialist").lower()
    path = out / f"{channel}_channel_{stamp}.json"
    suffix = 1
    while path.exists():
        path = out / f"{channel}_channel_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
