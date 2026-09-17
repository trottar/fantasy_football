from __future__ import annotations

import math

import numpy as np

from src.transaction_manager import _best_lineup_realized_points, _paired_mean_interval
from src.weekly_yield import build_weekly_yield_state, sample_conditional_points


def test_lineup_is_selected_from_pregame_mean_not_realized_score():
    league = {"roster": {"QB": 0, "RB": 0, "WR": 1, "TE": 0, "FLEX": 0, "K": 0, "DST": 0}}
    roster = [
        {"espn_id": 1, "position": "WR"},
        {"espn_id": 2, "position": "WR"},
    ]
    active = {1: True, 2: True}
    # Player 1 is the correct pregame start, even though player 2 realizes a huge score.
    decision = {1: 10.0, 2: 9.0}
    realized = {1: 0.0, 2: 100.0}
    total, selected = _best_lineup_realized_points(
        roster, active, decision, realized, league, {"WR": 0.0}
    )
    assert selected == {1}
    assert total == 0.0


def test_aggregate_sampler_does_not_shift_mean_with_zero_truncation():
    player = {
        "espn_id": 3,
        "name": "Low Mean",
        "position": "WR",
        "nfl_team": "PIT",
        "latent_mean_ppg": 1.0,
        "latent_mean_sd_ppg": 1.0,
        "predictive_weekly_sd_ppg": math.sqrt(2.0),
    }
    state = build_weekly_yield_state(
        player, week=1, current_week=1, model={}, availability_probability=1.0
    )
    sample = sample_conditional_points(state, np.array([-3.0]), np.array([0.0]))
    assert sample[0] < 0.0


def test_paired_interval_targets_mean_not_raw_discrete_quantiles():
    # Raw 16/84 percentiles are exactly 0 and 1/14 here; the resampled mean interval
    # must instead lie around the mean effect and be much narrower than that step.
    delta = np.array([0.0] * 96 + [1.0 / 14.0] * 32)
    lo, hi = _paired_mean_interval(delta, seed=11, draws=2000)
    mean = float(np.mean(delta))
    assert 0.0 < lo < mean < hi < (1.0 / 14.0)


def test_paired_mean_interval_accepts_negative_dst_derived_seed():
    from src.transaction_manager import _paired_mean_interval

    delta = np.asarray([0.0, 0.01, -0.01, 0.0, 0.02, 0.0], dtype=float)
    first = _paired_mean_interval(delta, seed=-4812345, draws=250)
    second = _paired_mean_interval(delta, seed=-4812345, draws=250)
    assert first == second
    assert first[0] <= first[1]
