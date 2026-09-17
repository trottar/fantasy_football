from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .matchup_model import build_matchup_adjustment
from .interaction_grid import evaluate_interaction_correction


DEFAULT_GAME_SD = {"QB": 6.0, "RB": 6.5, "WR": 7.0, "TE": 5.5, "K": 3.5, "DST": 5.0}
DEFAULT_MODEL_SD = {"QB": 1.8, "RB": 2.4, "WR": 2.5, "TE": 2.2, "K": 1.2, "DST": 1.8}
DEFAULT_ESPN_ANCHOR_SD = {"QB": 4.0, "RB": 4.5, "WR": 4.5, "TE": 4.0, "K": 3.0, "DST": 4.0}


@dataclass(frozen=True)
class WeeklyYieldState:
    espn_id: int | None
    name: str
    position: str
    nfl_team: str | None
    week: int
    operational_mean_ppg: float
    pre_matchup_operational_mean_ppg: float
    model_mean_ppg: float | None
    matchup_model_mean_ppg: float | None
    espn_anchor_ppg: float | None
    espn_anchor_kind: str | None
    espn_anchor_weight: float
    espn_anchor_acceptance_specific: bool
    delta_model_minus_espn: float | None
    ratio_model_to_espn: float | None
    anchor_pull_ppg: float
    game_sd_ppg: float
    model_sd_ppg: float
    kinematic_sd_ppg: float
    interaction_sd_ppg: float
    predictive_sd_ppg: float
    espn_anchor_sigma_ppg: float | None
    espn_anchor_z: float | None
    availability_probability: float
    kinematic_factor_mean: float
    kinematic_factor_source: str
    interaction_factor_mean: float
    interaction_factor_source: str
    interaction_delta_ppg: float
    interaction_artifact_id: str | None
    interaction_baseline_source: str
    interaction_support: float
    interaction_components: dict[str, Any]
    matchup_opponent: str | None
    matchup_home: bool | None
    matchup_team_implied_points: float | None
    matchup_defense_current_weight: float
    kinematic_components: dict[str, float]
    kinematic_zscores: dict[str, float]
    dst_component_expectation: dict[str, float] | None
    projection_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finite(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _mapping_value(mapping: Any, key: str, default: float) -> float:
    if isinstance(mapping, dict):
        try:
            return float(mapping.get(key, default))
        except (TypeError, ValueError):
            return float(default)
    try:
        return float(mapping)
    except (TypeError, ValueError):
        return float(default)


def build_weekly_yield_state(
    player: dict[str, Any],
    *,
    week: int,
    current_week: int,
    model: dict[str, Any],
    availability_probability: float,
    matchup_context: dict[str, Any] | None = None,
    league: dict[str, Any] | None = None,
) -> WeeklyYieldState:
    """Build a transparent player-week predictive-yield state.

    v0.23 keeps ESPN as an external predicted-yield anchor while adding an
    independently auditable matchup/acceptance coordinate. For a current-week ESPN
    projection, ESPN is treated as already evaluated at its own implicit matchup
    point: our K factor is applied to the internal model branch *before* anchoring.
    A season/17 ESPN anchor is treated as neutral and receives the same K correction.
    """
    cfg = model.get("weekly_yield", {})
    mcfg = model.get("matchup_model", {})
    pos = str(player.get("position") or "").upper()

    try:
        pid = int(float(player.get("espn_id")))
    except (TypeError, ValueError):
        pid = None

    latent = _finite(player.get("latent_mean_ppg"))
    season_ppg = _finite(player.get("season_ppg"))
    projection = _finite(player.get("projection_points"))
    raw_espn_week = _finite(player.get("espn_weekly_projection_raw"))
    raw_espn_season = _finite(player.get("season_projection"))

    model_mean = latent if latent is not None and latent > 0 else None
    if model_mean is None and season_ppg is not None and season_ppg > 0:
        model_mean = season_ppg
    if model_mean is None and projection is not None and projection > 0:
        model_mean = projection

    espn_anchor = None
    anchor_kind = None
    anchor_weight = 0.0
    acceptance_specific = False
    if int(week) == int(current_week) and raw_espn_week is not None and raw_espn_week > 0:
        espn_anchor = raw_espn_week
        anchor_kind = "ESPN_WEEKLY"
        anchor_weight = float(cfg.get("espn_week_anchor_weight", 0.35))
        acceptance_specific = True
    elif raw_espn_season is not None and raw_espn_season > 0:
        espn_anchor = raw_espn_season / 17.0
        anchor_kind = "ESPN_SEASON_DIV17"
        anchor_weight = float(cfg.get("espn_season_anchor_weight", 0.15))

    anchor_weight = min(max(anchor_weight, 0.0), 1.0)
    adjustment = build_matchup_adjustment(
        player, week=int(week), matchup_context=matchup_context, model=model
    ) if matchup_context is not None else None
    factor = float(adjustment.factor) if adjustment is not None else 1.0
    factor_source = adjustment.source if adjustment is not None else "NEUTRAL_V022"

    matchup_model_mean = model_mean * factor if model_mean is not None else None

    # Neutral/base operational mean before our K acceptance correction. This remains
    # useful for closure diagnostics and makes the ESPN treatment explicit.
    if model_mean is not None and espn_anchor is not None:
        pre_matchup = (1.0 - anchor_weight) * model_mean + anchor_weight * espn_anchor
    elif model_mean is not None:
        pre_matchup = model_mean
        anchor_weight = 0.0
    elif espn_anchor is not None:
        pre_matchup = espn_anchor
        anchor_weight = 1.0
    else:
        pre_matchup = max(projection or 0.0, 0.0)
        anchor_weight = 0.0

    if pos == "DST" and adjustment is not None and adjustment.dst_components:
        component_mean = float(adjustment.dst_components.get("component_expected_fantasy") or pre_matchup)
        dst_weight = min(max(float(mcfg.get("dst", {}).get("component_anchor_weight", 0.55)), 0.0), 1.0)
        operational = (1.0 - dst_weight) * pre_matchup + dst_weight * component_mean
        factor = operational / pre_matchup if pre_matchup > 1e-9 else 1.0
        matchup_model_mean = component_mean
    elif acceptance_specific:
        # ESPN weekly already includes ESPN's implicit matchup acceptance. Avoid
        # multiplying that branch by our K a second time.
        if matchup_model_mean is not None and espn_anchor is not None:
            operational = (1.0 - anchor_weight) * matchup_model_mean + anchor_weight * espn_anchor
        elif matchup_model_mean is not None:
            operational = matchup_model_mean
        elif espn_anchor is not None:
            operational = espn_anchor
        else:
            operational = pre_matchup * factor
    else:
        # Season/17 anchor is a neutral reference; apply weekly acceptance afterward.
        operational = pre_matchup * factor

    # v0.28: apply the separately pre-fitted Data/MC interaction grid as a
    # higher-order correction to the commissioned base yield. The grid is trained
    # only on underlying football statistics. Fantasy scoring enters only here, as
    # the downstream response used to convert corrected component statistics into
    # a point-yield delta. Missing/uncommissioned grids are exactly neutral.
    interaction = evaluate_interaction_correction(
        player,
        week=int(week),
        matchup_context=matchup_context,
        model=model,
        league=league,
        reference_points=float(max(operational, 0.0)),
    )
    operational = max(float(operational) + float(interaction.delta_points), 0.0)

    comparable_model = matchup_model_mean if acceptance_specific else model_mean
    delta = None
    ratio = None
    anchor_sigma = None
    anchor_z = None
    if espn_anchor is not None and comparable_model is not None:
        delta = comparable_model - espn_anchor
        ratio = comparable_model / espn_anchor if abs(espn_anchor) > 1e-12 else None

    # Anchor pull is relative to the internally adjusted model when a comparable
    # matchup-specific model exists; otherwise relative to the neutral model.
    reference_for_pull = matchup_model_mean if matchup_model_mean is not None else model_mean
    pull = operational - reference_for_pull if reference_for_pull is not None else 0.0

    model_sd = _finite(player.get("latent_mean_sd_ppg"))
    if model_sd is None or model_sd <= 0:
        model_sd = _mapping_value(cfg.get("default_model_sd_ppg", {}), pos, DEFAULT_MODEL_SD.get(pos, 2.0))

    predictive_total = _finite(player.get("predictive_weekly_sd_ppg"))
    if predictive_total is not None and predictive_total > model_sd:
        game_sd = math.sqrt(max(predictive_total * predictive_total - model_sd * model_sd, 0.0))
    else:
        game_sd = _mapping_value(cfg.get("default_game_sd_ppg", {}), pos, DEFAULT_GAME_SD.get(pos, 6.0))
    game_sd = max(float(game_sd), float(cfg.get("minimum_game_sd_ppg", 1.0)))
    model_sd = max(float(model_sd), float(cfg.get("minimum_model_sd_ppg", 0.25)))

    if adjustment is not None and pos in {"QB", "RB", "WR", "TE", "DST"}:
        base_frac = float(mcfg.get("kinematic_fractional_sd", 0.035))
        early_extra = float(mcfg.get("early_season_extra_fractional_sd", 0.020))
        current_weight = float(adjustment.defense_current_weight or 0.0)
        frac = max(base_frac + early_extra * (1.0 - current_weight), 0.0)
        kinematic_sd = abs(float(operational)) * frac
    else:
        kinematic_sd = 0.0
    interaction_sd = max(float(interaction.uncertainty_ppg), 0.0)
    predictive_sd = math.sqrt(
        game_sd * game_sd
        + model_sd * model_sd
        + kinematic_sd * kinematic_sd
        + interaction_sd * interaction_sd
    )

    if espn_anchor is not None and comparable_model is not None:
        anchor_sigma = _mapping_value(cfg.get("espn_anchor_sigma_ppg", {}), pos, DEFAULT_ESPN_ANCHOR_SD.get(pos, 4.0))
        denom = math.sqrt(model_sd * model_sd + kinematic_sd * kinematic_sd + anchor_sigma * anchor_sigma)
        anchor_z = delta / denom if denom > 0 and delta is not None else None

    return WeeklyYieldState(
        espn_id=pid,
        name=str(player.get("name") or pid or "?"),
        position=pos,
        nfl_team=player.get("nfl_team"),
        week=int(week),
        operational_mean_ppg=float(max(operational, 0.0)),
        pre_matchup_operational_mean_ppg=float(max(pre_matchup, 0.0)),
        model_mean_ppg=float(model_mean) if model_mean is not None else None,
        matchup_model_mean_ppg=float(matchup_model_mean) if matchup_model_mean is not None else None,
        espn_anchor_ppg=float(espn_anchor) if espn_anchor is not None else None,
        espn_anchor_kind=anchor_kind,
        espn_anchor_weight=float(anchor_weight),
        espn_anchor_acceptance_specific=bool(acceptance_specific),
        delta_model_minus_espn=float(delta) if delta is not None else None,
        ratio_model_to_espn=float(ratio) if ratio is not None else None,
        anchor_pull_ppg=float(pull),
        game_sd_ppg=float(game_sd),
        model_sd_ppg=float(model_sd),
        kinematic_sd_ppg=float(kinematic_sd),
        interaction_sd_ppg=float(interaction_sd),
        predictive_sd_ppg=float(predictive_sd),
        espn_anchor_sigma_ppg=float(anchor_sigma) if anchor_sigma is not None else None,
        espn_anchor_z=float(anchor_z) if anchor_z is not None else None,
        availability_probability=float(min(max(availability_probability, 0.0), 1.0)),
        kinematic_factor_mean=float(factor),
        kinematic_factor_source=factor_source,
        interaction_factor_mean=float(interaction.factor),
        interaction_factor_source=str(interaction.source),
        interaction_delta_ppg=float(interaction.delta_points),
        interaction_artifact_id=interaction.artifact_id,
        interaction_baseline_source=str(interaction.baseline_source),
        interaction_support=float(interaction.support),
        interaction_components={k: v.to_dict() for k, v in interaction.components.items()},
        matchup_opponent=adjustment.opponent if adjustment is not None else None,
        matchup_home=adjustment.home if adjustment is not None else None,
        matchup_team_implied_points=adjustment.team_implied_points if adjustment is not None else None,
        matchup_defense_current_weight=float(adjustment.defense_current_weight) if adjustment is not None else 0.0,
        kinematic_components=dict(adjustment.component_log_adjustments) if adjustment is not None else {},
        kinematic_zscores=dict(adjustment.component_zscores) if adjustment is not None else {},
        dst_component_expectation=dict(adjustment.dst_components) if adjustment is not None and adjustment.dst_components else None,
        projection_source=str(player.get("projection_source") or "UNKNOWN"),
    )


def sample_conditional_points(
    state: WeeklyYieldState,
    epistemic_standard_normal: np.ndarray,
    game_standard_normal: np.ndarray,
    kinematic_standard_normal: np.ndarray | None = None,
    interaction_standard_normal: np.ndarray | None = None,
) -> np.ndarray:
    """Sample conditional-on-playing fantasy yield around the operational mean."""
    if kinematic_standard_normal is None:
        kinematic_standard_normal = np.zeros_like(np.asarray(game_standard_normal, dtype=float))
    if interaction_standard_normal is None:
        interaction_standard_normal = np.zeros_like(np.asarray(game_standard_normal, dtype=float))
    values = (
        state.operational_mean_ppg
        + state.model_sd_ppg * np.asarray(epistemic_standard_normal, dtype=float)
        + state.game_sd_ppg * np.asarray(game_standard_normal, dtype=float)
        + state.kinematic_sd_ppg * np.asarray(kinematic_standard_normal, dtype=float)
        + state.interaction_sd_ppg * np.asarray(interaction_standard_normal, dtype=float)
    )
    return values
