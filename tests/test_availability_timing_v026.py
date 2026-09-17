from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.availability_timing import availability_state_model, player_lock_timing
from src.transaction_manager import UtilityContext, evaluate_roster_predictive


def _player(pid: int, name: str, team: str, points: float, status: str = "ACTIVE") -> dict:
    return {
        "espn_id": pid,
        "name": name,
        "position": "WR",
        "nfl_team": team,
        "weekly_projection": points,
        "season_projection": points * 17,
        "injury_status": status,
        "droppable": True,
        "lineup_locked": False,
        "official_roster_status": "ACT",
        "official_roster_team": team,
    }


def _league() -> dict:
    return {
        "teams": 2,
        "roster": {"QB": 0, "RB": 0, "WR": 1, "TE": 0, "FLEX": 0, "K": 0, "DST": 0},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "bye_weeks_2026": {},
        "fantasy_season": {"regular_season_weeks": list(range(1, 14))},
    }


def _model() -> dict:
    return {
        "weekly_manager": {
            "status_active_probability": {"ACTIVE": 1.0, "QUESTIONABLE": 0.50, "OUT": 0.0},
            "status_full_given_active": {"ACTIVE": 1.0, "QUESTIONABLE": 1.0},
            "limited_workload_fraction": {"WR": 0.60, "DEFAULT": 0.60},
            "inactive_reveal_lead_minutes": 90,
        },
        "season_utility": {"active_probability_nonbye": {"WR": 1.0}},
        "weekly_yield": {
            "espn_week_anchor_weight": 0.35,
            "espn_season_anchor_weight": 0.15,
            "minimum_game_sd_ppg": 1.0,
            "minimum_model_sd_ppg": 0.25,
        },
        "matchup_model": {
            "kinematic_fractional_sd": 0.0,
            "early_season_extra_fractional_sd": 0.0,
            "dst": {"component_anchor_weight": 0.55},
        },
        "transaction_manager": {
            "availability_scenarios": 4,
            "predictive_mc_scenarios": 256,
            "random_seed": 260026,
            "replacement_available_rank": {"WR": 1},
            "h2h_matchup_scale_points": 18.0,
        },
    }


def _matchup_context(late_time: str = "16:25") -> dict:
    def game(time: str, opp: str) -> dict:
        return {
            "game_id": f"g-{time}-{opp}",
            "gameday": "2026-09-13",
            "gametime": time,
            "opponent": opp,
            "home": True,
            "team_implied_points": 22.5,
        }

    return {
        "team_week": {
            "EAR": {"1": game("13:00", "X")},
            "LAT": {"1": game(late_time, "Y")},
            "OPP": {"1": game("13:00", "Z")},
        },
        "defense_profiles": {},
        "offense_profiles": {},
        "defense_zscores": {},
        "league_reference": {},
    }


def _context(tmp_path: Path, *, late_time: str = "16:25") -> UtilityContext:
    early = _player(1, "Early", "EAR", 10.0, "ACTIVE")
    late = _player(2, "Late Q", "LAT", 20.0, "QUESTIONABLE")
    opp = _player(101, "Opponent", "OPP", 12.0, "ACTIVE")
    values = tmp_path / "values.csv"
    pd.DataFrame(
        [
            {"espn_id": 1, "latent_mean_ppg": 10.0, "latent_mean_sd_ppg": 0.25, "predictive_weekly_sd_ppg": 1.0},
            {"espn_id": 2, "latent_mean_ppg": 20.0, "latent_mean_sd_ppg": 0.25, "predictive_weekly_sd_ppg": 1.0},
            {"espn_id": 101, "latent_mean_ppg": 12.0, "latent_mean_sd_ppg": 0.25, "predictive_weekly_sd_ppg": 1.0},
        ]
    ).to_csv(values, index=False)
    snap = {
        "snapshot_utc": "2026-08-31T12:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 1,
            "teams": [
                {"team_id": 1, "name": "Us", "roster": [early, late]},
                {"team_id": 2, "name": "Them", "roster": [opp]},
            ],
            "available_players": [],
            "matchups": [{"week": 1, "home_team_id": 1, "away_team_id": 2}],
        },
        "matchup_context": _matchup_context(late_time),
    }
    return UtilityContext(snap, _league(), _model(), values, snap["espn"]["teams"][0])


def test_v026_availability_separates_active_from_full_workload():
    player = _player(9, "Q", "EAR", 10.0, "QUESTIONABLE")
    model = _model()
    model["weekly_manager"]["status_active_probability"]["QUESTIONABLE"] = 0.75
    model["weekly_manager"]["status_full_given_active"]["QUESTIONABLE"] = 0.60
    state = availability_state_model(player, model)
    assert state.p_active == pytest.approx(0.75)
    assert state.p_full_given_active == pytest.approx(0.60)
    assert state.p_full == pytest.approx(0.45)
    assert state.p_limited == pytest.approx(0.30)
    assert state.p_out == pytest.approx(0.25)
    assert state.expected_workload_given_active == pytest.approx(0.60 + 0.40 * 0.60)


def test_v026_kickoff_and_reveal_group_come_from_nflverse_schedule():
    player = _player(1, "Early", "EAR", 10.0)
    timing = player_lock_timing(player, week=1, matchup_context=_matchup_context(), model=_model())
    assert timing.lock_group == "SUN_EARLY"
    assert timing.kickoff is not None and timing.reveal_time is not None
    assert (timing.kickoff - timing.reveal_time).total_seconds() == pytest.approx(90 * 60)


def test_v026_lock_aware_policy_cannot_use_late_inactive_before_early_lock(tmp_path: Path):
    ctx = _context(tmp_path, late_time="16:25")
    realistic, _, realistic_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, current_week_policy="realistic"
    )
    idealized, _, idealized_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, current_week_policy="idealized"
    )
    r = np.asarray(realistic_weekly[:, 0])
    i = np.asarray(idealized_weekly[:, 0])
    # When the high-upside late player is inactive, idealized policy can retroactively
    # choose the early player; the realistic policy had to decide before that status
    # was available. This is exactly the information-timing inflation v0.26 targets.
    assert float(np.mean(i)) > float(np.mean(r))
    assert idealized.current_week_expected_points > realistic.current_week_expected_points


def test_v026_same_lock_window_removes_inactive_timing_advantage(tmp_path: Path):
    ctx = _context(tmp_path, late_time="13:00")
    _, _, realistic_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, current_week_policy="realistic"
    )
    _, _, idealized_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, current_week_policy="idealized"
    )
    assert np.asarray(realistic_weekly[:, 0]) == pytest.approx(np.asarray(idealized_weekly[:, 0]))


def test_v026_snapshot_locked_lineup_state_is_immutable(tmp_path: Path):
    from src.transaction_manager import _snapshot_locked_state

    ctx = _context(tmp_path, late_time="16:25")
    early = next(p for p in ctx.roster if p["espn_id"] == 1)
    timing_by_id = {int(p["espn_id"]): ctx.lock_timing(p, 1) for p in ctx.roster}

    # ESPN says the early player is already locked on the bench: he is expired
    # and cannot be retroactively inserted by the policy.
    early["lineup_locked"] = True
    early["lineup_slot"] = "BENCH"
    fixed, expired = _snapshot_locked_state(ctx.roster, ctx, 1, timing_by_id)
    assert 1 in expired
    assert 1 not in fixed.values()

    # If ESPN instead says he is locked into the WR starter slot, preserve it.
    early["lineup_slot"] = "WR"
    fixed, expired = _snapshot_locked_state(ctx.roster, ctx, 1, timing_by_id)
    assert 1 in expired
    assert fixed["WR"] == 1


def test_v026_score_ties_keep_flex_open_for_later_players():
    from src.transaction_manager import _optimal_lineup_assignment

    league = {
        "roster": {"QB": 0, "RB": 1, "WR": 1, "TE": 0, "FLEX": 1, "K": 0, "DST": 0}
    }
    roster = [
        {"espn_id": 1, "position": "RB", "name": "Early RB"},
        {"espn_id": 2, "position": "RB", "name": "Late RB"},
        {"espn_id": 3, "position": "WR", "name": "Late WR"},
    ]
    assignment = _optimal_lineup_assignment(
        roster,
        {1, 2, 3},
        {1: 10.0, 2: 20.0, 3: 19.0},
        league,
        avoid_flex_ids={1},
    )
    assert assignment["RB"] == 1
    assert assignment["FLEX"] == 2
    assert assignment["WR"] == 3
