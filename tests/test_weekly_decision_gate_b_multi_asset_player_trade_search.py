from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.market_manager import screen_player_trade_packages, search_trades
from src.weekly_decision_cycle import (
    CONTRACT,
    TRADE_1X1,
    TRADE_MULTI,
    TRADE_SPECIALIST,
    _gate_b_receipts,
    _trade_receipts,
)


def league_cfg():
    return {
        "teams": 3,
        "roster": {
            "QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1,
            "K": 1, "DST": 1, "BENCH": 3,
        },
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "fantasy_season": {
            "regular_season_weeks": list(range(1, 14)),
            "playoff_week_participation_prior": {
                "14": .5, "15": .33, "16": .17, "17": .17
            },
        },
        "bye_weeks_2026": {},
    }


def model_cfg():
    return {
        "weekly_manager": {
            "status_active_probability": {
                "ACTIVE": .995, "NORMAL": .995, "QUESTIONABLE": .75, "OUT": 0.0
            },
            "status_full_given_active": {
                "ACTIVE": .97, "NORMAL": .97, "QUESTIONABLE": .65
            },
            "limited_workload_fraction": {
                "DEFAULT": .65, "QB": .8, "RB": .65, "WR": .65,
                "TE": .65, "K": .9, "DST": .9,
            },
        },
        "season_utility": {
            "active_probability_nonbye": {
                "QB": .97, "RB": .92, "WR": .94, "TE": .94,
                "K": .995, "DST": 1.0,
            },
            "regular_week_weight": 1.0,
            "use_playoff_participation_prior": True,
        },
        "transaction_manager": {
            "availability_scenarios": 4,
            "predictive_mc_scenarios": 32,
            "random_seed": 19,
            "replacement_available_rank": {
                "QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DST": 2
            },
            "h2h_matchup_scale_points": 18.0,
            "paired_mean_interval_resamples": 100,
            "mc_progress_batch_size": 32,
        },
        "market_manager": {
            "trade_max_players_per_side": 2,
            "trade_search_mc_scenarios": 32,
            "trade_search_screen_limit": 8,
            "trade_search_give_candidates": 8,
            "trade_search_target_candidates": 8,
            "trade_search_min_user_screen_gain": -100.0,
            "trade_actionable_accept_probability": .40,
        },
        "matchup_model": {"enabled": False},
        "interaction_grid": {"enabled": False},
    }


def p(pid, name, pos, pts):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": "X",
        "pro_team_id": 1,
        "weekly_projection": pts,
        "season_projection": pts * 17,
        "season_ppg": pts,
        "injury_status": "ACTIVE",
        "fantasy_status": "ROSTERED",
        "droppable": True,
        "lineup_locked": False,
        "percent_owned": 50.0,
    }


def user_roster():
    return [
        p(1, "U QB", "QB", 20),
        p(2, "U RB1", "RB", 18), p(3, "U RB2", "RB", 16),
        p(4, "U RB3", "RB", 12), p(5, "U WR1", "WR", 17),
        p(6, "U WR2", "WR", 15), p(7, "U WR3", "WR", 6),
        p(8, "U TE1", "TE", 6), p(9, "U TE2", "TE", 4),
        p(10, "U K", "K", 8), p(11, "U DST", "DST", 7),
    ]


def partner_roster():
    return [
        p(101, "P QB", "QB", 19),
        p(102, "P RB1", "RB", 13), p(103, "P RB2", "RB", 8),
        p(104, "P RB3", "RB", 5), p(105, "P WR1", "WR", 18),
        p(106, "P WR2", "WR", 16), p(107, "P WR3", "WR", 7),
        p(108, "P TE Star", "TE", 14), p(109, "P TE2", "TE", 12),
        p(110, "P K", "K", 8), p(111, "P DST", "DST", 7),
    ]


def other_roster():
    return [
        dict(row, espn_id=row["espn_id"] + 200, name="O " + row["name"])
        for row in user_roster()
    ]


def snapshot():
    return {
        "snapshot_utc": "2026-10-01T12:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 4,
            "teams": [
                {"team_id": 1, "name": "Us", "roster": user_roster()},
                {"team_id": 2, "name": "Partner", "roster": partner_roster()},
                {"team_id": 3, "name": "Other", "roster": other_roster()},
            ],
            "available_players": [],
        },
    }


def values_file(tmp_path: Path):
    rows = []
    for player in user_roster() + partner_roster() + other_roster():
        rows.append({
            "espn_id": player["espn_id"],
            "latent_mean_ppg": player["weekly_projection"],
            "latent_mean_sd_ppg": 1.0,
            "predictive_weekly_sd_ppg": 4.0,
        })
    path = tmp_path / "values.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _screen_row(family, give_ids, receive_ids):
    return {
        "partner_team_id": 2,
        "partner_name": "Partner",
        "package_family": family,
        "give_ids": list(give_ids),
        "give_names": [f"G{x}" for x in give_ids],
        "give_positions": ["RB"] * len(give_ids),
        "receive_ids": list(receive_ids),
        "receive_names": [f"R{x}" for x in receive_ids],
        "receive_positions": ["WR"] * len(receive_ids),
        "give_id": give_ids[0] if len(give_ids) == 1 else None,
        "give_name": " + ".join(f"G{x}" for x in give_ids),
        "give_position": " + ".join(["RB"] * len(give_ids)),
        "receive_id": receive_ids[0] if len(receive_ids) == 1 else None,
        "receive_name": " + ".join(f"R{x}" for x in receive_ids),
        "receive_position": " + ".join(["WR"] * len(receive_ids)),
        "user_screen_gain_ppg": 1.0,
        "partner_screen_gain_ppg": 0.1,
        "screen_score": 1.0,
    }


def test_package_screen_covers_all_four_bounded_player_families(tmp_path):
    snap = snapshot()
    rows = screen_player_trade_packages(
        snap, league_cfg(), model_cfg(),
        values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0],
        limit=8,
    )
    families = {row["package_family"] for row in rows}
    assert families == {"1x1", "1x2", "2x1", "2x2"}
    for row in rows:
        give_n, receive_n = [int(x) for x in row["package_family"].split("x")]
        assert len(row["give_ids"]) == give_n
        assert len(row["receive_ids"]) == receive_n
        assert give_n <= 2 and receive_n <= 2


def test_search_routes_each_package_family_to_existing_predictive_authority(monkeypatch, tmp_path):
    import src.market_manager as mm

    screened = [
        _screen_row("1x1", [4], [108]),
        _screen_row("1x2", [4], [108, 107]),
        _screen_row("2x1", [4, 7], [108]),
        _screen_row("2x2", [4, 7], [108, 107]),
    ]
    seen = []

    monkeypatch.setattr(mm, "screen_player_trade_packages", lambda *a, **k: list(screened))

    def fake_eval(*args, **kwargs):
        give_ids = tuple(kwargs["give_ids"])
        receive_ids = tuple(kwargs["receive_ids"])
        seen.append((give_ids, receive_ids))
        return {
            "classification": "NO_RESOLVED_EDGE",
            "give": [{"espn_id": x, "name": f"G{x}"} for x in give_ids],
            "receive": [{"espn_id": x, "name": f"R{x}"} for x in receive_ids],
            "user_auto_drops": [{"espn_id": 900, "name": "Drop"}] if len(receive_ids) > len(give_ids) else [],
            "partner_auto_drops": [],
            "user_auto_adds": [{"espn_id": 901, "name": "Fill"}] if len(give_ids) > len(receive_ids) else [],
            "partner_auto_adds": [],
            "user": {"delta_season_ppg": {"mean": 0.0, "p_better": 0.5}},
            "partner": {"delta_season_ppg": {"mean": 0.0, "p_better": 0.5}},
            "response": {"p_accept": 0.1, "p_counter": 0.2, "p_reject": 0.7},
            "expected_offer_value": 0.0,
        }

    monkeypatch.setattr(mm, "evaluate_trade", fake_eval)
    snap = snapshot()
    rows = search_trades(
        snap, league_cfg(), model_cfg(),
        values_path=values_file(tmp_path),
        user_team=snap["espn"]["teams"][0],
        limit=4,
        mc_scenarios=16,
    )
    assert set(seen) == {
        ((4,), (108,)),
        ((4,), (108, 107)),
        ((4, 7), (108,)),
        ((4, 7), (108, 107)),
    }
    assert {row["package_family"] for row in rows} == {"1x1", "1x2", "2x1", "2x2"}
    by_family = {row["package_family"]: row for row in rows}
    assert by_family["1x2"]["user_auto_drop_names"] == ["Drop"]
    assert by_family["2x1"]["user_auto_add_names"] == ["Fill"]


def test_weekly_trade_receipts_close_multi_asset_gap_but_not_specialist_gap():
    rows = [
        {"package_family": "1x1", "classification": "NO_RESOLVED_EDGE"},
        {"package_family": "1x2", "classification": "NO_RESOLVED_EDGE"},
        {"package_family": "2x1", "classification": "ACTIONABLE_OFFER"},
        {"package_family": "2x2", "classification": "NO_RESOLVED_EDGE"},
    ]
    receipts = _trade_receipts(rows)
    assert [row.key for row in receipts] == [TRADE_1X1, TRADE_MULTI]
    assert receipts[0].status.startswith("PASS")
    assert receipts[1].status == "PASS / ACTION"
    assert receipts[1].action["kind"] == "MULTI_ASSET_PLAYER_TRADE"
    assert receipts[1].evidence["supported_package_families"] == ["1x2", "2x1", "2x2"]

    remaining = _gate_b_receipts()
    assert [row.key for row in remaining] == [TRADE_SPECIALIST]
    assert remaining[0].status.startswith("INCOMPLETE_COVERAGE")


def test_weekly_contract_identifies_multi_asset_player_trade_search_gate():
    assert CONTRACT == "WEEKLY_DECISION_COMPLETION_GATE_B3_MULTI_ASSET_PLAYER_TRADE_SEARCH_V001"
