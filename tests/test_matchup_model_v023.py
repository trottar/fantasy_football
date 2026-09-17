from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.data_sources.nflverse_matchups import aggregate_team_profiles, build_matchup_context
from src.matchup_model import build_matchup_adjustment, simulate_dst_component_points
from src.weekly_yield import build_weekly_yield_state


def _context():
    return {
        "defense_profiles": {
            "BAL": {"current_weight": 0.0},
            "CLE": {"current_weight": 0.0},
        },
        "offense_profiles": {
            "PIT": {"plays_per_game": 64, "pass_rate": .58, "sack_rate": .07, "turnover_rate": .02, "yards_per_play": 5.4, "epa_per_play": 0.0},
            "CLE": {"plays_per_game": 63, "pass_rate": .60, "sack_rate": .10, "turnover_rate": .03, "yards_per_play": 5.0, "epa_per_play": -0.05},
        },
        "defense_zscores": {
            "BAL": {"pass_epa_per_play": 1.0, "sack_rate": -1.0, "plays_per_game": .5, "pass_rate": .2, "explosive_pass_rate": .5, "redzone_td_rate": .2, "target_share_wr": .3},
            "CLE": {},
        },
        "team_week": {
            "PIT": {"1": {"opponent": "BAL", "home": True, "team_implied_points": 25.0}},
            "BAL": {"1": {"opponent": "PIT", "home": False, "team_implied_points": 21.0}},
            "CLE": {"1": {"opponent": "PIT", "home": False, "team_implied_points": 19.0}},
        },
    }


def test_offensive_matchup_factor_uses_defense_coordinates():
    player = {"position": "WR", "nfl_team": "PIT"}
    adj = build_matchup_adjustment(player, week=1, matchup_context=_context(), model={})
    assert adj.opponent == "BAL"
    assert adj.home is True
    assert adj.factor > 1.0
    assert adj.source == "NFLVERSE_SHRUNK_DEFENSE_V023"
    assert "pass_epa_per_play" in adj.component_log_adjustments


def test_weekly_espn_anchor_is_not_double_multiplied_by_k():
    player = {
        "espn_id": 1,
        "name": "WR",
        "position": "WR",
        "nfl_team": "PIT",
        "latent_mean_ppg": 20.0,
        "espn_weekly_projection_raw": 10.0,
    }
    model = {"weekly_yield": {"espn_week_anchor_weight": 0.35}}
    state = build_weekly_yield_state(
        player,
        week=1,
        current_week=1,
        model=model,
        availability_probability=1.0,
        matchup_context=_context(),
    )
    expected = 0.65 * (20.0 * state.kinematic_factor_mean) + 0.35 * 10.0
    assert math.isclose(state.operational_mean_ppg, expected, rel_tol=1e-10)
    assert state.espn_anchor_acceptance_specific is True
    assert not math.isclose(state.operational_mean_ppg, state.pre_matchup_operational_mean_ppg * state.kinematic_factor_mean)


def test_current_season_profiles_are_aggressively_shrunk():
    schedules = pd.DataFrame([{"season": 2026, "game_type": "REG", "week": 1, "home_team": "BAL", "away_team": "PIT", "spread_line": 3.0, "total_line": 44.0}])
    prior = {
        "defense": {"BAL": {"plays": 1000, "plays_per_game": 60.0, "pass_epa_per_play": -0.1}, "PIT": {"plays": 1000, "plays_per_game": 65.0, "pass_epa_per_play": 0.1}},
        "offense": {"BAL": {"plays": 1000, "plays_per_game": 60.0}, "PIT": {"plays": 1000, "plays_per_game": 65.0}},
    }
    current = {
        "defense": {"BAL": {"plays": 100, "plays_per_game": 80.0, "pass_epa_per_play": 0.5}, "PIT": {"plays": 100, "plays_per_game": 50.0, "pass_epa_per_play": -0.5}},
        "offense": {"BAL": {"plays": 100, "plays_per_game": 80.0}, "PIT": {"plays": 100, "plays_per_game": 50.0}},
    }
    ctx = build_matchup_context(schedules, season=2026, current_week=3, prior_profiles=prior, current_profiles=current, shrinkage_plays=400)
    assert math.isclose(ctx["defense_profiles"]["BAL"]["current_weight"], 0.2)
    assert math.isclose(ctx["defense_profiles"]["BAL"]["plays_per_game"], 64.0)
    assert ctx["team_week"]["BAL"]["1"]["team_implied_points"] == 23.5
    assert ctx["team_week"]["PIT"]["1"]["team_implied_points"] == 20.5


def test_pbp_aggregation_produces_measured_defensive_observables():
    pbp = pd.DataFrame([
        {"season_type":"REG","week":1,"game_id":"g1","posteam":"PIT","defteam":"BAL","pass_attempt":1,"rush_attempt":0,"sack":0,"interception":0,"fumble_lost":0,"epa":0.4,"yards_gained":25,"yardline_100":50,"touchdown":0,"receiver_player_id":"wr1"},
        {"season_type":"REG","week":1,"game_id":"g1","posteam":"PIT","defteam":"BAL","pass_attempt":1,"rush_attempt":0,"sack":1,"interception":0,"fumble_lost":0,"epa":-1.0,"yards_gained":-7,"yardline_100":40,"touchdown":0,"receiver_player_id":None},
        {"season_type":"REG","week":1,"game_id":"g1","posteam":"PIT","defteam":"BAL","pass_attempt":0,"rush_attempt":1,"sack":0,"interception":0,"fumble_lost":0,"epa":0.2,"yards_gained":12,"yardline_100":15,"touchdown":1,"receiver_player_id":None},
    ])
    out = aggregate_team_profiles(pbp, receiver_positions={"wr1":"WR"})
    bal = out["defense"]["BAL"]
    assert bal["plays"] == 3
    assert math.isclose(bal["sack_rate"], 0.5)
    assert math.isclose(bal["explosive_pass_rate"], 0.5)
    assert math.isclose(bal["explosive_rush_rate"], 1.0)
    assert math.isclose(bal["target_share_wr"], 1.0)
    assert math.isclose(bal["redzone_td_rate"], 1.0)


def test_dst_component_mc_closes_on_operational_mean_and_uses_bucket_scoring():
    components = {
        "sacks_mean": 3.0,
        "turnovers_mean": 1.5,
        "defensive_tds_mean": 0.15,
        "blocked_kicks_mean": 0.08,
        "safeties_mean": 0.04,
        "points_allowed_mean": 20.0,
        "points_allowed_sd": 8.0,
        "yards_allowed_mean": 330.0,
        "yards_allowed_sd": 60.0,
    }
    draws = simulate_dst_component_points(components, scenarios=2000, seed=1234, target_mean=7.5)
    assert len(draws) == 2000
    assert math.isclose(float(np.mean(draws)), 7.5, abs_tol=1e-10)
    assert float(np.std(draws)) > 2.0


def test_dst_component_mc_accepts_negative_espn_dst_derived_seed():
    """ESPN team-defense IDs can make deterministic derived seeds negative."""
    components = {
        "sacks_mean": 2.5,
        "turnovers_mean": 1.2,
        "defensive_tds_mean": 0.1,
        "blocked_kicks_mean": 0.05,
        "safeties_mean": 0.03,
        "points_allowed_mean": 22.0,
        "points_allowed_sd": 8.0,
        "yards_allowed_mean": 335.0,
        "yards_allowed_sd": 65.0,
    }
    first = simulate_dst_component_points(components, scenarios=64, seed=-16001, target_mean=7.0)
    second = simulate_dst_component_points(components, scenarios=64, seed=-16001, target_mean=7.0)
    assert len(first) == 64
    assert np.array_equal(first, second)
    assert math.isclose(float(np.mean(first)), 7.0, abs_tol=1e-10)
