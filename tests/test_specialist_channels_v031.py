from __future__ import annotations

import pandas as pd
import pytest

from src.market_manager import evaluate_trade, screen_one_for_one_trades
from src.specialist_channels import evaluate_defense_channel, evaluate_kicker_channel
from src.transaction_manager import evaluate_actions


def league_cfg():
    return {
        "teams": 3,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1, "BENCH": 2},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "fantasy_season": {"regular_season_weeks": list(range(1, 14))},
        "bye_weeks_2026": {},
    }


def model_cfg():
    return {
        "weekly_manager": {"status_active_probability": {"ACTIVE": 1.0}},
        "season_utility": {"active_probability_nonbye": {"QB": 1.0, "RB": 1.0, "WR": 1.0, "TE": 1.0, "K": 1.0, "DST": 1.0}},
        "weekly_yield": {
            "espn_week_anchor_weight": 0.35,
            "espn_season_anchor_weight": 0.15,
            "minimum_game_sd_ppg": 1.0,
            "minimum_model_sd_ppg": 0.25,
        },
        "transaction_manager": {
            "availability_scenarios": 2,
            "predictive_mc_scenarios": 64,
            "predictive_mc_screen_per_status": 12,
            "random_seed": 31,
            "candidate_limit": 20,
            "candidate_floor_per_position": 2,
            "replacement_available_rank": {"QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DST": 2},
            "waiver_p_acquire_default": 0.35,
            "waiver_p_acquire_floor": 0.02,
            "opponent_roster_target": {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1},
        },
        "specialist_channels": {
            "mc_scenarios": 128,
            "candidate_limit": 8,
            "player_slot_insurance_weight": 0.25,
            "defense": {"allow_second": True},
            "kicker": {
                "allow_second": False,
                "implied_points_baseline": 22.5,
                "implied_points_elasticity": 0.65,
                "matchup_factor_min": 0.82,
                "matchup_factor_max": 1.18,
            },
        },
        "market_manager": {"trade_max_players_per_side": 2, "trade_search_give_candidates": 8, "trade_search_target_candidates": 8},
    }


def p(pid, name, pos, pts, *, team="PIT", fantasy_status="ROSTERED"):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": team,
        "weekly_projection": pts,
        "season_projection": pts * 17,
        "injury_status": "ACTIVE",
        "fantasy_status": fantasy_status,
        "droppable": True,
        "lineup_locked": False,
        "percent_owned": 50.0,
    }


def roster(offset=0, *, dst_pts=7.0, k_pts=8.0):
    return [
        p(offset + 1, "QB", "QB", 20),
        p(offset + 2, "RB1", "RB", 17), p(offset + 3, "RB2", "RB", 15), p(offset + 4, "RB3", "RB", 7),
        p(offset + 5, "WR1", "WR", 16), p(offset + 6, "WR2", "WR", 14), p(offset + 7, "WR3", "WR", 6),
        p(offset + 8, "TE1", "TE", 10), p(offset + 9, "TE2", "TE", 5),
        p(offset + 10, "K", "K", k_pts, team="DET"),
        p(offset + 11, "DST", "DST", dst_pts, team="DET"),
    ]


def snapshot(available):
    return {
        "snapshot_utc": "2026-08-31T05:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 1,
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": 2, "roster": roster(0)},
                {"team_id": 2, "name": "Them", "waiver_rank": 1, "roster": roster(100)},
                {"team_id": 3, "name": "Other", "waiver_rank": 3, "roster": roster(200)},
            ],
            "matchups": [{"week": 1, "home_team_id": 1, "away_team_id": 2}],
            "available_players": available,
        },
        "matchup_context": {
            "team_week": {
                "DET": {
                    "1": {"opponent": "GB", "home": True, "team_implied_points": 18.0},
                    "2": {"opponent": "CHI", "home": False, "team_implied_points": 19.0},
                },
                "KC": {
                    "1": {"opponent": "LV", "home": True, "team_implied_points": 30.0},
                    "2": {"opponent": "DEN", "home": False, "team_implied_points": 27.0},
                },
            },
            "defense_profiles": {},
            "offense_profiles": {},
            "defense_zscores": {},
            "league_reference": {},
        },
    }


def values_file(tmp_path, extra=()):
    ids = [x[0] for x in extra]
    rows = []
    for team_offset in (0, 100, 200):
        for player in roster(team_offset):
            rows.append({"espn_id": player["espn_id"], "latent_mean_ppg": player["weekly_projection"], "latent_mean_sd_ppg": 0.5, "predictive_weekly_sd_ppg": 3.0})
    for pid, mean in extra:
        rows.append({"espn_id": pid, "latent_mean_ppg": mean, "latent_mean_sd_ppg": 0.5, "predictive_weekly_sd_ppg": 3.0})
    path = tmp_path / "values.csv"
    pd.DataFrame(rows).drop_duplicates("espn_id").to_csv(path, index=False)
    return path


def test_v031_player_market_excludes_dst_and_k_candidates(tmp_path):
    available = [
        p(900, "DST Upgrade", "DST", 12, team="KC", fantasy_status="FREEAGENT"),
        p(901, "K Upgrade", "K", 11, team="KC", fantasy_status="FREEAGENT"),
        p(902, "WR Upgrade", "WR", 18, team="KC", fantasy_status="FREEAGENT"),
    ]
    report = evaluate_actions(snapshot(available), league_cfg(), model_cfg(), values_file(tmp_path, [(900, 12), (901, 11), (902, 18)]), team_name="Us")
    assert report["market_channel"] == "PLAYER_QB_RB_WR_TE_V031"
    assert report["candidate_pool_evaluated"] == 1
    assert all(r["add_position"] in {"QB", "RB", "WR", "TE"} for r in report["free_agent_actions"] + report["waiver_actions"])
    assert all(r["drop_position"] in {"QB", "RB", "WR", "TE"} for r in report["free_agent_actions"] + report["waiver_actions"])


def test_v031_defense_channel_compares_dst_to_dst_and_reports_rotation_slot_cost(tmp_path):
    candidate = p(900, "KC DST", "DST", 11, team="KC", fantasy_status="FREEAGENT")
    report = evaluate_defense_channel(
        snapshot([candidate]), league_cfg(), model_cfg(), values_path=values_file(tmp_path, [(900, 11)]), team_name="Us", mc_scenarios=128,
    )
    assert report["channel"] == "DEFENSE"
    assert report["swap_actions"]
    top = report["swap_actions"][0]
    assert top["add_name"] == "KC DST"
    assert top["drop_name"] == "DST"
    assert top["delta_channel_ppg"] > 0
    assert top["classification"] == "CHANNEL_UPGRADE"
    assert report["carry_actions"]
    carry = report["carry_actions"][0]
    assert carry["player_slot_release"]["position"] in {"QB", "RB", "WR", "TE"}
    assert "rotation_synergy_ppg" in carry
    assert "net_complete_state_ppg" in carry


def test_v031_kicker_channel_is_same_position_and_uses_weekly_team_environment(tmp_path):
    candidate = p(901, "KC K", "K", 8.5, team="KC", fantasy_status="FREEAGENT")
    report = evaluate_kicker_channel(
        snapshot([candidate]), league_cfg(), model_cfg(), values_path=values_file(tmp_path, [(901, 8.5)]), team_name="Us", mc_scenarios=128,
    )
    assert report["channel"] == "KICKER"
    assert report["carry_actions"] == []
    assert report["swap_actions"]
    top = report["swap_actions"][0]
    assert top["drop_name"] == "K"
    assert top["add_name"] == "KC K"
    assert top["weekly_plan"][0]["source"] == "TEAM_IMPLIED_POINTS_KICKER_CHANNEL_V031"
    assert top["weekly_plan"][0]["team_implied_points"] == 30.0


def test_v031_trade_channel_rejects_specialist_assets(tmp_path):
    snap = snapshot([])
    with pytest.raises(ValueError, match="player-only"):
        evaluate_trade(
            snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path),
            user_team=snap["espn"]["teams"][0], partner_team_id=2,
            give_ids=[10], receive_ids=[110], mc_scenarios=32,
        )


def test_v031_trade_search_screen_contains_only_player_positions(tmp_path):
    snap = snapshot([])
    rows = screen_one_for_one_trades(
        snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0], limit=50,
    )
    assert all(r["give_position"] in {"QB", "RB", "WR", "TE"} for r in rows)
    assert all(r["receive_position"] in {"QB", "RB", "WR", "TE"} for r in rows)


def test_v031_second_dst_synergy_is_incremental_over_best_single_dst(tmp_path, monkeypatch):
    import numpy as np
    import src.specialist_channels as sc

    candidate = p(903, "Always Better DST", "DST", 10, team="KC", fantasy_status="FREEAGENT")

    def fake_samples(player, ctx, week):
        mean = 10.0 if int(player.get("espn_id")) == 903 else 7.0
        return np.full(ctx.predictive_scenarios, mean, dtype=float), mean, {"opponent": "X", "source": "TEST"}

    monkeypatch.setattr(sc, "_specialist_week_samples", fake_samples)
    report = sc.evaluate_defense_channel(
        snapshot([candidate]), league_cfg(), model_cfg(), values_path=values_file(tmp_path, [(903, 10)]), team_name="Us", mc_scenarios=64,
    )
    carry = report["carry_actions"][0]
    # There is no rotation complementarity: the candidate alone is already the best
    # one-defense state in every week. Carrying both must not count the swap gain again.
    assert abs(carry["rotation_synergy_ppg"]) < 1e-12
    assert carry["best_one_defense_state"] == "Always Better DST"
    assert carry["classification"] == "HOLD_CHANNEL"


def test_v031_second_dst_synergy_rewards_weekly_complementarity_not_realized_hindsight(tmp_path, monkeypatch):
    import numpy as np
    import src.specialist_channels as sc

    candidate = p(904, "Complement DST", "DST", 8, team="KC", fantasy_status="FREEAGENT")

    def fake_samples(player, ctx, week):
        is_candidate = int(player.get("espn_id")) == 904
        # Candidate is strong in even weeks; incumbent is strong in odd weeks.
        mean = 11.0 if (is_candidate == (week % 2 == 0)) else 5.0
        # Realized samples deliberately contain a large opposite-tail event. If the
        # optimizer used hindsight max instead of pregame mean, this would inflate value.
        arr = np.full(ctx.predictive_scenarios, mean, dtype=float)
        if len(arr) > 0:
            arr[0] = 40.0 if mean == 5.0 else mean
        return arr, mean, {"opponent": "X", "source": "TEST"}

    monkeypatch.setattr(sc, "_specialist_week_samples", fake_samples)
    report = sc.evaluate_defense_channel(
        snapshot([candidate]), league_cfg(), model_cfg(), values_path=values_file(tmp_path, [(904, 8)]), team_name="Us", mc_scenarios=64,
    )
    carry = report["carry_actions"][0]
    assert carry["rotation_synergy_ppg"] > 0.0
    # Weekly plan alternates based on the pregame expected means.
    starters = {x["week"]: x["starter_name"] for x in carry["weekly_plan"][:4]}
    assert starters[1] == "DST"
    assert starters[2] == "Complement DST"
    assert starters[3] == "DST"
    assert starters[4] == "Complement DST"


def test_v031_specialist_channel_preserves_locked_current_week_starter(tmp_path, monkeypatch):
    import numpy as np
    import src.specialist_channels as sc

    candidate = p(905, "Better DST", "DST", 14, team="KC", fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    incumbent = next(x for x in snap["espn"]["teams"][0]["roster"] if x["position"] == "DST")
    incumbent["lineup_locked"] = True
    incumbent["lineup_slot"] = "DST"

    def fake_samples(player, ctx, week):
        mean = 14.0 if int(player.get("espn_id")) == 905 else 7.0
        return np.full(ctx.predictive_scenarios, mean, dtype=float), mean, {"opponent": "X", "source": "TEST"}

    monkeypatch.setattr(sc, "_specialist_week_samples", fake_samples)
    report = sc.evaluate_defense_channel(
        snap, league_cfg(), model_cfg(), values_path=values_file(tmp_path, [(905, 14)]), team_name="Us", mc_scenarios=64,
    )
    # A locked incumbent cannot be swapped out, and a carry configuration must keep
    # that incumbent as the current-week starter even when the candidate projects higher.
    assert report["swap_actions"] == []
    assert report["carry_actions"]
    assert report["carry_actions"][0]["weekly_plan"][0]["week"] == 1
    assert report["carry_actions"][0]["weekly_plan"][0]["starter_name"] == "DST"
