from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any

import numpy as np

from .scoring import score_dst
from .data_sources.nflverse_matchups import normalize_team


DEFAULT_POSITION_WEIGHTS = {
    "QB": {
        "plays_per_game": 0.018,
        "pass_rate": 0.012,
        "pass_epa_per_play": 0.038,
        "sack_rate": -0.030,
        "explosive_pass_rate": 0.022,
        "redzone_td_rate": 0.015,
    },
    "RB": {
        "plays_per_game": 0.018,
        "rush_rate": 0.014,
        "rush_epa_per_play": 0.040,
        "explosive_rush_rate": 0.022,
        "redzone_td_rate": 0.015,
        "target_share_rb": 0.012,
    },
    "WR": {
        "plays_per_game": 0.014,
        "pass_rate": 0.010,
        "pass_epa_per_play": 0.030,
        "sack_rate": -0.018,
        "explosive_pass_rate": 0.028,
        "redzone_td_rate": 0.012,
        "target_share_wr": 0.020,
    },
    "TE": {
        "plays_per_game": 0.012,
        "pass_epa_per_play": 0.022,
        "sack_rate": -0.012,
        "redzone_td_rate": 0.012,
        "target_share_te": 0.032,
    },
}


@dataclass(frozen=True)
class MatchupAdjustment:
    factor: float
    source: str
    opponent: str | None
    home: bool | None
    team_implied_points: float | None
    defense_current_weight: float
    component_log_adjustments: dict[str, float]
    component_zscores: dict[str, float]
    dst_components: dict[str, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finite(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _week_context(context: dict[str, Any], team: str | None, week: int) -> dict[str, Any] | None:
    team = normalize_team(team)
    if not team:
        return None
    return (context.get("team_week") or {}).get(team, {}).get(str(int(week)))


def _weights(model: dict[str, Any], pos: str) -> dict[str, float]:
    cfg = model.get("matchup_model", {})
    custom = (cfg.get("position_log_weights") or {}).get(pos)
    base = dict(DEFAULT_POSITION_WEIGHTS.get(pos, {}))
    if isinstance(custom, dict):
        for key, value in custom.items():
            try:
                base[str(key)] = float(value)
            except (TypeError, ValueError):
                pass
    return base


def build_offensive_matchup_adjustment(
    player: dict[str, Any],
    *,
    week: int,
    matchup_context: dict[str, Any] | None,
    model: dict[str, Any],
) -> MatchupAdjustment:
    pos = str(player.get("position") or "").upper()
    team = normalize_team(player.get("nfl_team"))
    if pos not in {"QB", "RB", "WR", "TE"} or not matchup_context or not team:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_MATCHUP_DATA", None, None, None, 0.0, {}, {})
    game = _week_context(matchup_context, team, week)
    if not game:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_SCHEDULE", None, None, None, 0.0, {}, {})
    opponent = normalize_team(game.get("opponent"))
    if not opponent:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_OPPONENT", None, None, None, 0.0, {}, {})
    z = (matchup_context.get("defense_zscores") or {}).get(opponent, {})
    profile = (matchup_context.get("defense_profiles") or {}).get(opponent, {})
    if not z:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_DEFENSE_PROFILE", opponent, game.get("home"), _finite(game.get("team_implied_points")), 0.0, {}, {})

    log_parts: dict[str, float] = {}
    for key, weight in _weights(model, pos).items():
        zv = _finite(z.get(key))
        if zv is not None:
            log_parts[key] = float(weight * max(min(zv, 2.5), -2.5))

    cfg = model.get("matchup_model", {})
    if bool(game.get("home")):
        log_parts["home"] = float(cfg.get("home_log_bonus", 0.010))
    implied = _finite(game.get("team_implied_points"))
    if implied is not None:
        baseline = float(cfg.get("league_implied_points_baseline", 22.5))
        per_point = float(cfg.get("implied_points_log_weight", 0.006))
        log_parts["implied_points"] = per_point * max(min(implied - baseline, 10.0), -10.0)

    raw = math.exp(sum(log_parts.values()))
    lower = float(cfg.get("offense_factor_min", 0.88))
    upper = float(cfg.get("offense_factor_max", 1.12))
    factor = min(max(raw, lower), upper)
    return MatchupAdjustment(
        factor=float(factor),
        source="NFLVERSE_SHRUNK_DEFENSE_V023",
        opponent=opponent,
        home=bool(game.get("home")) if game.get("home") is not None else None,
        team_implied_points=implied,
        defense_current_weight=float(profile.get("current_weight") or 0.0),
        component_log_adjustments=log_parts,
        component_zscores={k: float(v) for k, v in z.items() if _finite(v) is not None},
    )


def _normal_bucket_expectation(mean: float, sd: float, buckets: list[tuple[float, float, float]]) -> float:
    if sd <= 1e-9:
        for lo, hi, value in buckets:
            if lo <= mean < hi:
                return value
        return buckets[-1][2]
    nd = NormalDist(mu=mean, sigma=sd)
    total = 0.0
    for lo, hi, value in buckets:
        p_lo = 0.0 if math.isinf(lo) and lo < 0 else nd.cdf(lo)
        p_hi = 1.0 if math.isinf(hi) and hi > 0 else nd.cdf(hi)
        total += max(p_hi - p_lo, 0.0) * value
    return total


def build_dst_component_expectation(
    player: dict[str, Any],
    *,
    week: int,
    matchup_context: dict[str, Any] | None,
    model: dict[str, Any],
) -> MatchupAdjustment:
    team = normalize_team(player.get("nfl_team"))
    if not matchup_context or not team:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_MATCHUP_DATA", None, None, None, 0.0, {}, {}, None)
    game = _week_context(matchup_context, team, week)
    if not game:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_SCHEDULE", None, None, None, 0.0, {}, {}, None)
    opponent = normalize_team(game.get("opponent"))
    defense = (matchup_context.get("defense_profiles") or {}).get(team, {})
    offense = (matchup_context.get("offense_profiles") or {}).get(opponent, {}) if opponent else {}
    if not defense or not offense:
        return MatchupAdjustment(1.0, "NEUTRAL_NO_DST_PROFILE", opponent, game.get("home"), None, float(defense.get("current_weight") or 0.0), {}, {}, None)

    cfg = model.get("matchup_model", {}).get("dst", {})
    plays = np.mean([float(defense.get("plays_per_game") or 64.0), float(offense.get("plays_per_game") or 64.0)])
    pass_rate = np.mean([float(defense.get("pass_rate") or 0.58), float(offense.get("pass_rate") or 0.58)])
    dropbacks = max(float(plays * pass_rate), 1.0)
    sack_rate = np.mean([float(defense.get("sack_rate") or 0.065), float(offense.get("sack_rate") or 0.065)])
    turnover_rate = np.mean([float(defense.get("turnover_rate") or 0.020), float(offense.get("turnover_rate") or 0.020)])
    yards_per_play = np.mean([float(defense.get("yards_per_play") or 5.4), float(offense.get("yards_per_play") or 5.4)])
    sacks = max(dropbacks * sack_rate, 0.0)
    turnovers = max(plays * turnover_rate, 0.0)
    yards = max(plays * yards_per_play, 0.0)

    implied_opp = None
    # team_week stores implied points for the team whose key is used. Get opponent's row.
    opp_game = _week_context(matchup_context, opponent, week) if opponent else None
    if opp_game:
        implied_opp = _finite(opp_game.get("team_implied_points"))
    league_ref = matchup_context.get("league_reference") or {}
    def_epa = float(defense.get("epa_per_play") or 0.0)
    off_epa = float(offense.get("epa_per_play") or 0.0)
    if implied_opp is None:
        baseline = float(cfg.get("points_allowed_baseline", 22.5))
        points = baseline + float(cfg.get("epa_points_scale", 28.0)) * (off_epa + def_epa) / 2.0
    else:
        points = implied_opp
    points = max(float(points), 0.0)

    points_sd = float(cfg.get("points_allowed_sd", 9.5))
    yards_sd = float(cfg.get("yards_allowed_sd", 75.0))
    def_td = max(turnovers * float(cfg.get("return_td_per_turnover", 0.10)), 0.0)
    blocked = float(cfg.get("blocked_kicks_mean", 0.08))
    safety = float(cfg.get("safeties_mean", 0.05))

    pa_buckets = [
        (-math.inf, 0.5, 5.0), (0.5, 6.5, 4.0), (6.5, 13.5, 3.0), (13.5, 17.5, 1.0),
        (17.5, 27.5, 0.0), (27.5, 34.5, -1.0), (34.5, 45.5, -3.0), (45.5, math.inf, -5.0),
    ]
    ya_buckets = [
        (-math.inf, 100.0, 5.0), (100.0, 200.0, 3.0), (200.0, 300.0, 2.0), (300.0, 350.0, 0.0),
        (350.0, 400.0, -1.0), (400.0, 450.0, -3.0), (450.0, 500.0, -5.0), (500.0, 550.0, -6.0), (550.0, math.inf, -7.0),
    ]
    bucket_expectation = _normal_bucket_expectation(points, points_sd, pa_buckets) + _normal_bucket_expectation(yards, yards_sd, ya_buckets)
    expected_fantasy = sacks + 2.0 * turnovers + 6.0 * def_td + 2.0 * blocked + 2.0 * safety + bucket_expectation
    components = {
        "plays": float(plays),
        "dropbacks": float(dropbacks),
        "sacks_mean": float(sacks),
        "turnovers_mean": float(turnovers),
        "defensive_tds_mean": float(def_td),
        "blocked_kicks_mean": float(blocked),
        "safeties_mean": float(safety),
        "points_allowed_mean": float(points),
        "points_allowed_sd": points_sd,
        "yards_allowed_mean": float(yards),
        "yards_allowed_sd": yards_sd,
        "component_expected_fantasy": float(expected_fantasy),
    }
    return MatchupAdjustment(
        factor=1.0,
        source="NFLVERSE_DST_COMPONENTS_V023",
        opponent=opponent,
        home=bool(game.get("home")) if game.get("home") is not None else None,
        team_implied_points=_finite(game.get("team_implied_points")),
        defense_current_weight=float(defense.get("current_weight") or 0.0),
        component_log_adjustments={},
        component_zscores={},
        dst_components=components,
    )


def build_matchup_adjustment(
    player: dict[str, Any],
    *,
    week: int,
    matchup_context: dict[str, Any] | None,
    model: dict[str, Any],
) -> MatchupAdjustment:
    pos = str(player.get("position") or "").upper()
    if pos == "DST":
        return build_dst_component_expectation(player, week=week, matchup_context=matchup_context, model=model)
    if pos in {"QB", "RB", "WR", "TE"}:
        return build_offensive_matchup_adjustment(player, week=week, matchup_context=matchup_context, model=model)
    return MatchupAdjustment(1.0, "NEUTRAL_POSITION_V023", None, None, None, 0.0, {}, {})


def simulate_dst_component_points(
    components: dict[str, float],
    *,
    scenarios: int,
    seed: int,
    target_mean: float,
) -> np.ndarray:
    """Simulate DST scoring components and apply exact ESPN PA/YA bucket response.

    The component model controls matchup-dependent shape. A constant closure offset
    recenters the raw component MC on the operational DST mean so the new response
    model does not silently discard the existing player/ESPN anchor calibration.
    """
    # ESPN uses negative IDs for team defenses.  Derived deterministic seeds can
    # therefore be negative even though NumPy SeedSequence requires non-negative
    # entropy.  Map the signed integer onto a stable uint64 stream instead of
    # rejecting legitimate DST IDs.
    normalized_seed = int(seed) & 0xFFFFFFFFFFFFFFFF
    rng = np.random.default_rng(normalized_seed)
    n = max(int(scenarios), 1)
    sacks = rng.poisson(max(float(components.get("sacks_mean", 0.0)), 0.0), n)
    turnovers = rng.poisson(max(float(components.get("turnovers_mean", 0.0)), 0.0), n)
    interceptions = rng.binomial(turnovers, 0.5)
    fumbles = turnovers - interceptions
    def_tds = rng.poisson(max(float(components.get("defensive_tds_mean", 0.0)), 0.0), n)
    blocked = rng.poisson(max(float(components.get("blocked_kicks_mean", 0.0)), 0.0), n)
    safeties = rng.poisson(max(float(components.get("safeties_mean", 0.0)), 0.0), n)
    pa = np.maximum(rng.normal(float(components.get("points_allowed_mean", 22.5)), float(components.get("points_allowed_sd", 9.5)), n), 0.0)
    ya = np.maximum(rng.normal(float(components.get("yards_allowed_mean", 340.0)), float(components.get("yards_allowed_sd", 75.0)), n), 0.0)
    raw = np.asarray([
        score_dst({
            "sacks": float(sacks[i]),
            "interceptions": float(interceptions[i]),
            "fumble_recoveries": float(fumbles[i]),
            "interception_return_td": float(def_tds[i]),
            "blocked_kicks": float(blocked[i]),
            "safeties": float(safeties[i]),
            "points_allowed": float(pa[i]),
            "yards_allowed": float(ya[i]),
        })
        for i in range(n)
    ], dtype=float)
    return raw + (float(target_mean) - float(np.mean(raw)))
