from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter
from typing import Any

import numpy as np

MEASUREMENT_SCHEMA_VERSION = 2
MEASUREMENT_MODEL_VERSION = "0.35-fixed1"
MEASUREMENT_CONTRACT = "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034"
SPECIALIST_CAPTURE_SCOPE = "OWNED_PLUS_ACTIONABLE_MARKET_SPECIALISTS_V034"
BEHAVIOR_STATE_MODEL = "SNAPSHOT_ANCHORED_UNCALIBRATED_BEHAVIOR_STATE_V034"
PLAYER_CAPTURE_MODEL = "INHERITED_V029_PROSPECTIVE_PLAYER_CLOSURE_STATE"
DST_COMPONENT_MODEL = "NFLVERSE_DST_COMPONENTS_V023_EXACT_ESPN_RESPONSE"
KICKER_COMPONENT_STATUS = "AGGREGATE_YIELD_PLUS_TEAM_ENVIRONMENT_ONLY_V034"
KICKER_OBSERVATION_TARGETS = [
    "field_goal_attempts",
    "field_goal_makes",
    "field_goal_distance",
    "extra_point_attempts",
    "extra_point_makes",
]
SPECIALIST_POSITIONS = {"DST", "K"}


def _finite(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _canonical_jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return _canonical_jsonable(value.item())
    if isinstance(value, float):
        if math.isnan(value):
            return {"__nonfinite_float__": "NaN"}
        if math.isinf(value):
            return {"__nonfinite_float__": "+Inf" if value > 0 else "-Inf"}
        return value
    if isinstance(value, dict):
        return {str(k): _canonical_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_jsonable(v) for v in value]
    return value


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        _canonical_jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _payload_without_integrity(payload: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(dict(payload))
    out.pop("integrity", None)
    return out


def verify_capture_integrity(payload: dict[str, Any]) -> bool:
    expected = str((payload.get("integrity") or {}).get("canonical_payload_sha256") or "")
    if not expected:
        return False
    return canonical_sha256(_payload_without_integrity(payload)) == expected


def _distribution_summary(samples: np.ndarray) -> dict[str, Any]:
    arr = np.asarray(samples, dtype=float).reshape(-1)
    if arr.size == 0:
        return {"n": 0, "mean": 0.0, "sd": 0.0, "p05": 0.0, "p16": 0.0, "p50": 0.0, "p84": 0.0, "p95": 0.0, "p_zero": 1.0}
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)),
        "sd": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "p05": float(np.quantile(arr, 0.05)),
        "p16": float(np.quantile(arr, 0.16)),
        "p50": float(np.quantile(arr, 0.50)),
        "p84": float(np.quantile(arr, 0.84)),
        "p95": float(np.quantile(arr, 0.95)),
        "p_zero": float(np.mean(np.abs(arr) <= 1e-12)),
    }


def _owner_index(ctx: Any) -> tuple[dict[int, int], dict[int, str | None]]:
    owners: dict[int, int] = {}
    names: dict[int, str | None] = {}
    team_meta = {
        int(tid): row
        for row in (getattr(ctx, "espn", {}).get("teams") or [])
        if (tid := _int(row.get("team_id"))) is not None
    }
    for tid, roster in getattr(ctx, "all_team_rosters", {}).items():
        names[int(tid)] = (team_meta.get(int(tid)) or {}).get("name")
        for player in roster or []:
            pid = _int(player.get("espn_id"))
            if pid is not None:
                owners[int(pid)] = int(tid)
    return owners, names


def _specialist_universe(ctx: Any) -> list[dict[str, Any]]:
    owners, _names = _owner_index(ctx)
    by_id: dict[int, dict[str, Any]] = {}
    for roster in getattr(ctx, "all_team_rosters", {}).values():
        for player in roster or []:
            pid = _int(player.get("espn_id"))
            if pid is None or str(player.get("position") or "").upper() not in SPECIALIST_POSITIONS:
                continue
            by_id[int(pid)] = dict(player)
    for player in getattr(ctx, "actionable_available", []) or []:
        pid = _int(player.get("espn_id"))
        if pid is None or str(player.get("position") or "").upper() not in SPECIALIST_POSITIONS:
            continue
        # Roster ownership is authoritative if the same ID appears in more than one
        # normalized pool; otherwise preserve the current actionable market record.
        if int(pid) not in owners:
            by_id[int(pid)] = dict(player)
    return [by_id[pid] for pid in sorted(by_id)]


def _specialist_prediction_record(player: dict[str, Any], ctx: Any, owners: dict[int, int], owner_names: dict[int, str | None]) -> dict[str, Any]:
    from .specialist_channels import _specialist_week_samples

    week = int(getattr(ctx, "week", 1))
    pid = _int(player.get("espn_id"))
    pos = str(player.get("position") or "").upper()
    state = ctx.yield_state(player, week)
    samples, mean, detail = _specialist_week_samples(player, ctx, week)
    timing = ctx.lock_timing(player, week)
    owner_id = owners.get(int(pid)) if pid is not None else None
    raw_components = dict(getattr(state, "dst_component_expectation", {}) or {})
    base = {
        "espn_id": pid,
        "name": player.get("name"),
        "position": pos,
        "nfl_team": player.get("nfl_team"),
        "fantasy_status": player.get("fantasy_status"),
        "owner_team_id": owner_id,
        "owner_team_name": owner_names.get(owner_id) if owner_id is not None else None,
        "market_state": "OWNED" if owner_id is not None else str(player.get("fantasy_status") or "AVAILABLE").upper(),
        "lineup_slot": player.get("lineup_slot"),
        "droppable": player.get("droppable"),
        "lineup_locked": player.get("lineup_locked"),
        "week": week,
        "operational_mean_ppg": _finite(getattr(state, "operational_mean_ppg", None)),
        "pre_matchup_operational_mean_ppg": _finite(getattr(state, "pre_matchup_operational_mean_ppg", None)),
        "model_mean_ppg": _finite(getattr(state, "model_mean_ppg", None)),
        "matchup_model_mean_ppg": _finite(getattr(state, "matchup_model_mean_ppg", None)),
        "espn_anchor_ppg": _finite(getattr(state, "espn_anchor_ppg", None)),
        "espn_anchor_kind": getattr(state, "espn_anchor_kind", None),
        "predictive_sd_ppg": _finite(getattr(state, "predictive_sd_ppg", None)),
        "game_sd_ppg": _finite(getattr(state, "game_sd_ppg", None)),
        "model_sd_ppg": _finite(getattr(state, "model_sd_ppg", None)),
        "kinematic_sd_ppg": _finite(getattr(state, "kinematic_sd_ppg", None)),
        "kinematic_factor": _finite(getattr(state, "kinematic_factor_mean", None)),
        "kinematic_source": getattr(state, "kinematic_factor_source", None),
        "matchup_opponent": detail.get("opponent") or getattr(state, "matchup_opponent", None),
        "matchup_home": getattr(state, "matchup_home", None),
        "team_implied_points": _finite(detail.get("team_implied_points") if isinstance(detail, dict) else None),
        "channel_expected_points": float(mean),
        "channel_source": detail.get("source") if isinstance(detail, dict) else None,
        "channel_matchup_factor": _finite(detail.get("matchup_factor") if isinstance(detail, dict) else None),
        "channel_distribution": _distribution_summary(np.asarray(samples, dtype=float)),
        "kickoff_utc": timing.to_dict().get("kickoff_utc"),
        "inactive_reveal_utc": timing.to_dict().get("inactive_reveal_utc"),
        "lock_group": timing.to_dict().get("lock_group"),
        "lock_source": timing.to_dict().get("lock_source"),
    }
    if pos == "DST":
        base.update({
            "component_model_status": "COMPONENT_LEVEL_MC_AVAILABLE",
            "component_model": DST_COMPONENT_MODEL,
            "component_predictions": raw_components or dict(detail.get("components") or {}),
            "fantasy_response": "EXACT_CONFIGURED_ESPN_DST_BUCKET_SCORING",
        })
    elif pos == "K":
        base.update({
            "component_model_status": KICKER_COMPONENT_STATUS,
            "component_model": None,
            "component_predictions": {},
            "future_component_observation_targets": list(KICKER_OBSERVATION_TARGETS),
            "fantasy_response": "AGGREGATE_SPECIALIST_YIELD_WITH_TEAM_IMPLIED_POINTS_RESPONSE",
            "measurement_limitation": "v0.34 freezes the commissioned aggregate kicker prediction; FG/XP opportunity and distance components are not yet modeled and are not fabricated.",
        })
    return base


def build_specialist_prediction_block(ctx: Any) -> dict[str, Any]:
    owners, owner_names = _owner_index(ctx)
    rows = [_specialist_prediction_record(player, ctx, owners, owner_names) for player in _specialist_universe(ctx)]
    counts = Counter(str(row.get("position") or "?") for row in rows)
    return {
        "scope": SPECIALIST_CAPTURE_SCOPE,
        "week": int(getattr(ctx, "week", 1)),
        "records": rows,
        "counts": {"total": len(rows), "DST": int(counts.get("DST", 0)), "K": int(counts.get("K", 0))},
        "notes": [
            "Specialist records are immutable decision-time predictions, not postgame observations.",
            "D/ST stores the commissioned component-level response and final fantasy distribution.",
            "Kicker stores the commissioned aggregate yield/environment response and explicitly records the absence of an FG/XP component model.",
        ],
    }


_MARKET_FIELDS = (
    "espn_id", "name", "position", "nfl_team", "fantasy_status", "on_team_id",
    "lineup_slot", "droppable", "lineup_locked", "percent_owned", "percent_started",
    "sleeper_trending_add_24h", "sleeper_trending_drop_24h", "weekly_projection",
    "season_projection", "projection_points", "projection_source", "season_ppg",
    "season_ppg_source", "injury_status", "nfl_roster_status", "nfl_roster_status_source",
)


def _compact_market_row(player: dict[str, Any]) -> dict[str, Any]:
    out = {key: player.get(key) for key in _MARKET_FIELDS if key in player}
    if "espn_id" not in out:
        out["espn_id"] = _int(player.get("espn_id"))
    return out


def _behavior_config(model: dict[str, Any]) -> dict[str, Any]:
    tx = model.get("transaction_manager") or {}
    market = model.get("market_manager") or {}
    specialist = ((model.get("specialist_channels") or {}).get("dynamic_policy") or {})
    tx_keys = [
        "waiver_claim_logit_intercept", "waiver_improvement_logit_per_ppg",
        "waiver_owned_logit_per_pct", "waiver_trend_logit_weight", "waiver_need_logit_bonus",
        "waiver_claim_utility_logit_intercept", "waiver_claim_season_ppg_weight",
        "waiver_claim_current_week_weight", "league_response_claim_logit_intercept",
        "league_response_claim_season_ppg_weight", "league_response_claim_current_week_weight",
        "opponent_roster_target",
    ]
    market_keys = [
        "trade_accept_intercept", "trade_accept_season_ppg_weight", "trade_accept_pbetter_weight",
        "trade_accept_market_weight", "trade_counter_intercept", "trade_counter_abs_gain_weight",
        "trade_counter_abs_market_weight", "trade_counter_small_deficit_bonus",
        "trade_reject_intercept", "trade_reject_negative_gain_weight",
        "trade_reject_negative_market_weight", "trade_package_complexity_penalty",
        "trade_actionable_accept_probability",
        "market_base_ppg_weight", "market_surplus_weight",
        "market_owned_weight", "market_trend_weight",
    ]
    return {
        "waiver_and_release_claim": {k: tx.get(k) for k in tx_keys if k in tx},
        "trade_response": {k: market.get(k) for k in market_keys if k in market},
        "specialist_market": dict(specialist),
        "full_transaction_manager_config": copy.deepcopy(tx),
        "full_market_manager_config": copy.deepcopy(market),
        "calibration_status": "UNCALIBRATED_PRE_DATA_PRIORS",
        "behavior_not_football_value": True,
    }


def build_behavioral_observation_state(snapshot: dict[str, Any], model: dict[str, Any], league: dict[str, Any], ctx: Any) -> dict[str, Any]:
    espn = snapshot.get("espn", snapshot)
    teams = []
    for team in espn.get("teams") or []:
        tid = _int(team.get("team_id"))
        roster = list(team.get("roster") or [])
        pos_counts = Counter(str(p.get("position") or "?").upper() for p in roster)
        teams.append({
            "team_id": tid,
            "name": team.get("name"),
            "waiver_rank": _int(team.get("waiver_rank")),
            "wins": _int(team.get("wins")),
            "losses": _int(team.get("losses")),
            "ties": _int(team.get("ties")),
            "points_for": _finite(team.get("points_for")),
            "roster_espn_ids": [pid for p in roster if (pid := _int(p.get("espn_id"))) is not None],
            "position_counts": dict(sorted(pos_counts.items())),
        })
    market_source = espn.get("available_players") or getattr(ctx, "actionable_available", []) or []
    market = [_compact_market_row(dict(p)) for p in market_source]
    status_counts = Counter(str(p.get("fantasy_status") or "UNKNOWN").upper() for p in market)
    position_counts = Counter(str(p.get("position") or "?").upper() for p in market)
    transaction_rows = espn.get("transactions") or espn.get("recent_transactions") or []
    if not isinstance(transaction_rows, list):
        transaction_rows = []
    return {
        "model": BEHAVIOR_STATE_MODEL,
        "captured_from_snapshot_utc": snapshot.get("snapshot_utc") or espn.get("snapshot_utc"),
        "snapshot_sha256": canonical_sha256(snapshot),
        "model_config_sha256": canonical_sha256(model),
        "league_config_sha256": canonical_sha256(league),
        "teams": teams,
        "market_players": market,
        "market_counts": {
            "total": len(market),
            "by_status": dict(sorted(status_counts.items())),
            "by_position": dict(sorted(position_counts.items())),
        },
        "transactions_observed_at_capture": copy.deepcopy(transaction_rows),
        "behavior_config": _behavior_config(model),
        "notes": [
            "This block freezes manager-facing covariates before outcomes so later 1.X releases can calibrate behavioral kernels prospectively.",
            "Behavior probabilities remain separate from football-value response and are not recalibrated in v0.34.",
        ],
    }


def enrich_pregame_capture(base_capture: dict[str, Any], snapshot: dict[str, Any], model: dict[str, Any], ctx: Any, team: dict[str, Any]) -> dict[str, Any]:
    capture = copy.deepcopy(base_capture)
    capture["schema_version"] = MEASUREMENT_SCHEMA_VERSION
    capture["model_version"] = MEASUREMENT_MODEL_VERSION
    capture["measurement_contract"] = MEASUREMENT_CONTRACT
    capture["player_measurement_model"] = PLAYER_CAPTURE_MODEL
    capture["specialist_predictions"] = build_specialist_prediction_block(ctx)
    capture["behavioral_observation_state"] = build_behavioral_observation_state(snapshot, model, getattr(ctx, "league", {}), ctx)
    from .player_temporal_state_v035 import build_temporal_player_states, summarize_temporal_player_states
    capture["temporal_player_state_prediction"] = summarize_temporal_player_states(
        build_temporal_player_states(ctx)
    )
    capture["pre_data_firewall"] = {
        "2026_game_outcomes_used_for_tuning": False,
        "automatic_refit": False,
        "automatic_calibration": False,
        "postgame_specialist_ledger_enabled": False,
        "postgame_behavior_calibration_enabled": False,
        "next_data_informed_major_version": "1.X",
    }
    notes = list(capture.get("notes") or [])
    notes.extend([
        "v0.34 established the a priori measurement contract; v0.35-fixed1 additionally freezes the causal temporal player-membership prediction before 2026 outcomes and still performs no outcome-informed tuning.",
        "The inherited v0.29 player closure ledger continues to consume only the players block; the all-league player, specialist, behavioral and temporal player-state blocks are frozen now for later 1.X Data/MC analysis.",
    ])
    capture["notes"] = notes
    capture["integrity"] = {
        "algorithm": "SHA256_CANONICAL_JSON_EXCLUDING_INTEGRITY",
        "canonical_payload_sha256": canonical_sha256(_payload_without_integrity(capture)),
    }
    return capture


def capture_summary(capture: dict[str, Any]) -> dict[str, Any]:
    specialists = capture.get("specialist_predictions") or {}
    behavior = capture.get("behavioral_observation_state") or {}
    counts = specialists.get("counts") or {}
    return {
        "measurement_contract": capture.get("measurement_contract"),
        "players": len(capture.get("players") or []),
        "league_players": int((capture.get("league_player_predictions") or {}).get("count") or 0),
        "specialists": int(counts.get("total") or 0),
        "dst": int(counts.get("DST") or 0),
        "kickers": int(counts.get("K") or 0),
        "behavior_teams": len(behavior.get("teams") or []),
        "market_players": len(behavior.get("market_players") or []),
        "temporal_player_transactions": int((capture.get("temporal_player_state_prediction") or {}).get("transaction_count") or 0),
        "snapshot_sha256": behavior.get("snapshot_sha256"),
        "integrity_ok": verify_capture_integrity(capture),
    }
