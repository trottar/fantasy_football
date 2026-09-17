import pandas as pd

from src.draft_state import DraftState
from src.roster_utility import (
    add_roster_marginal_values,
    diversified_candidate_pool,
    lineup_value,
)


def _league():
    return {
        "teams": 12,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3},
    }


def _model():
    return {
        "roster_utility": {
            "bench_option_weight": 0.25,
            "bench_depth_decay": 0.60,
            "candidate_floor_per_position": 2,
        }
    }


def test_lineup_value_handles_flex():
    roster = pd.DataFrame([
        {"key":1,"name":"RB1","position":"RB","latent_mean_ppg":20},
        {"key":2,"name":"RB2","position":"RB","latent_mean_ppg":18},
        {"key":3,"name":"RB3","position":"RB","latent_mean_ppg":17},
        {"key":4,"name":"WR1","position":"WR","latent_mean_ppg":19},
        {"key":5,"name":"WR2","position":"WR","latent_mean_ppg":16},
        {"key":6,"name":"TE1","position":"TE","latent_mean_ppg":12},
        {"key":7,"name":"QB1","position":"QB","latent_mean_ppg":22},
    ])
    repl = {"QB":15,"RB":8,"WR":9,"TE":8}
    value, selected = lineup_value(roster, repl, _league())
    # All mandatory starters plus RB3 in FLEX.
    assert 3 in selected
    assert len(selected) == 7
    assert value > 0


def test_fourth_rb_has_diminished_value_vs_missing_wr():
    board = pd.DataFrame([
        {"espn_id":1,"name":"RB1","position":"RB","latent_mean_ppg":20},
        {"espn_id":2,"name":"RB2","position":"RB","latent_mean_ppg":18},
        {"espn_id":3,"name":"RB3","position":"RB","latent_mean_ppg":17},
        {"espn_id":4,"name":"RB4","position":"RB","latent_mean_ppg":16},
        {"espn_id":5,"name":"WR1","position":"WR","latent_mean_ppg":15},
    ])
    state = DraftState(12, 16, 2)
    # Put three RBs on the user's roster directly for utility testing.
    state.picks = [
        {"overall":2,"round":1,"pick_in_round":2,"fantasy_team_slot":2,
         "player_id":"1","player_name":"RB1","position":"RB","nfl_team":"X","espn_id":1},
        {"overall":23,"round":2,"pick_in_round":11,"fantasy_team_slot":2,
         "player_id":"2","player_name":"RB2","position":"RB","nfl_team":"X","espn_id":2},
        {"overall":26,"round":3,"pick_in_round":2,"fantasy_team_slot":2,
         "player_id":"3","player_name":"RB3","position":"RB","nfl_team":"X","espn_id":3},
    ]
    dyn = pd.DataFrame([
        {"espn_id":4,"name":"RB4","position":"RB","latent_mean_ppg":16,
         "dynamic_replacement_ppg":8,"dynamic_vorp_ppg":8,"espn_adp":40},
        {"espn_id":5,"name":"WR1","position":"WR","latent_mean_ppg":15,
         "dynamic_replacement_ppg":9,"dynamic_vorp_ppg":6,"espn_adp":45},
    ])
    valued = add_roster_marginal_values(dyn, board, state, _league(), _model())
    v = valued.set_index("name")
    assert v.loc["RB4", "roster_lineup_gain_ppg"] == 0
    assert v.loc["RB4", "roster_bench_option_value"] > 0
    assert v.loc["WR1", "roster_lineup_gain_ppg"] > 0
    assert v.loc["WR1", "roster_marginal_value"] > v.loc["RB4", "roster_marginal_value"]


def test_candidate_pool_preserves_cross_position_evaluation():
    rows = []
    for pos, base in [("RB",10),("WR",8),("QB",6),("TE",5)]:
        for i in range(4):
            rows.append({
                "espn_id":len(rows)+1,"name":f"{pos}{i}","position":pos,
                "roster_candidate_legal":True,
                "roster_marginal_value":base-i*0.1,
                "espn_adp":len(rows)+1,
            })
    valued = pd.DataFrame(rows)
    pool = diversified_candidate_pool(valued, 12, _model())
    assert set(pool["position"]) == {"RB","WR","QB","TE"}
    assert all((pool["position"] == p).sum() >= 2 for p in ["RB","WR","QB","TE"])
