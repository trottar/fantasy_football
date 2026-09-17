from __future__ import annotations

import math

import numpy as np

from src.weekly_yield import build_weekly_yield_state, sample_conditional_points


def test_espn_week_projection_is_explicit_weak_anchor():
    player = {
        "espn_id": 1,
        "name": "Anchor Player",
        "position": "WR",
        "nfl_team": "PIT",
        "latent_mean_ppg": 20.0,
        "latent_mean_sd_ppg": 2.0,
        "predictive_weekly_sd_ppg": 5.0,
        "espn_weekly_projection_raw": 10.0,
        "season_projection": 255.0,
        "projection_source": "ESPN_WEEKLY",
    }
    model = {"weekly_yield": {"espn_week_anchor_weight": 0.35}}
    state = build_weekly_yield_state(
        player, week=1, current_week=1, model=model, availability_probability=0.75
    )
    assert state.model_mean_ppg == 20.0
    assert state.espn_anchor_ppg == 10.0
    assert state.espn_anchor_kind == "ESPN_WEEKLY"
    assert state.espn_anchor_weight == 0.35
    assert state.operational_mean_ppg == 16.5
    assert state.delta_model_minus_espn == 10.0
    assert state.availability_probability == 0.75
    assert state.kinematic_factor_mean == 1.0
    assert state.kinematic_factor_source == "NEUTRAL_V022"
    assert math.isclose(state.game_sd_ppg, math.sqrt(21.0), rel_tol=1e-9)
    assert math.isclose(state.predictive_sd_ppg, 5.0, rel_tol=1e-9)


def test_future_week_uses_weaker_espn_season_anchor():
    player = {
        "espn_id": 2,
        "name": "Season Anchor",
        "position": "RB",
        "latent_mean_ppg": 15.0,
        "season_projection": 170.0,
    }
    model = {"weekly_yield": {"espn_season_anchor_weight": 0.15}}
    state = build_weekly_yield_state(
        player, week=4, current_week=1, model=model, availability_probability=0.92
    )
    assert state.espn_anchor_kind == "ESPN_SEASON_DIV17"
    assert state.espn_anchor_ppg == 10.0
    assert state.operational_mean_ppg == 14.25


def test_conditional_yield_sampler_separates_model_and_game_draws():
    player = {
        "espn_id": 3,
        "name": "Sampler",
        "position": "TE",
        "latent_mean_ppg": 10.0,
        "latent_mean_sd_ppg": 2.0,
        "predictive_weekly_sd_ppg": math.sqrt(13.0),
    }
    state = build_weekly_yield_state(
        player, week=1, current_week=1, model={}, availability_probability=1.0
    )
    samples = sample_conditional_points(
        state,
        np.array([1.0, -1.0]),
        np.array([1.0, -1.0]),
    )
    assert np.allclose(samples, np.array([15.0, 5.0]))
