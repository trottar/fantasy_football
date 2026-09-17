import numpy as np
from types import SimpleNamespace

from src.season_utility import deterministic_bye_profile, season_roster_utility


def _league():
    return {
        "roster":{"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1,"K":1,"DST":1},
        "fantasy_season":{
            "regular_season_weeks":list(range(1,14)),
            "playoff_week_participation_prior":{"14":0.5,"15":1/3,"16":1/6,"17":1/6},
        },
    }


def _model():
    return {
        "season_utility":{
            "availability_scenarios":2,
            "active_probability_nonbye":{"QB":1,"RB":1,"WR":1,"TE":1,"K":1,"DST":1},
        },
        "full_rollout":{"starter_risk_penalty":0.0},
    }


def _prep(positions, vorp, byes):
    n=len(positions)
    return SimpleNamespace(
        ids=np.arange(1,n+1),
        positions=np.array(positions),
        vorp=np.array(vorp,dtype=float),
        bye_weeks=np.array(byes,dtype=int),
        sd=np.zeros(n),
    )


def test_h2h_cohesion_distinguishes_clustered_from_spread_byes():
    # Linear PPG loss is identical here, but H2H utility is not: the model is
    # allowed to prefer sacrificing one week over weakening two weeks.
    same = _prep(
        ["QB","RB","RB","WR","WR","TE","RB","WR","K","DST"],
        [8,8,7,9,8,5,10,7,1,1],
        [5,6,8,7,7,10,11,9,13,14],
    )
    spread = _prep(
        ["QB","RB","RB","WR","WR","TE","RB","WR","K","DST"],
        [8,8,7,9,8,5,10,7,1,1],
        [5,6,8,7,8,10,11,9,13,14],
    )
    roster=list(range(10))
    a=deterministic_bye_profile(same,roster,_league())
    b=deterministic_bye_profile(spread,roster,_league())
    assert abs(a["bye_loss_ppg"] - b["bye_loss_ppg"]) < 1e-9

    model=_model()
    model["season_utility"]["opponent_reference_vorp"] = 57.0
    model["season_utility"]["generic_opponent_matchup_scale_ppg"] = 6.0
    u=np.zeros((2,17,10))
    ua=season_roster_utility(same,roster,_league(),model,u)
    ub=season_roster_utility(spread,roster,_league(),model,u)
    assert ua["expected_h2h_win_probability"] != ub["expected_h2h_win_probability"]


def test_bench_insurance_is_usage_based_not_generic_depth_credit():
    prep = _prep(
        ["QB","RB","RB","WR","WR","TE","RB","WR","K","DST"],
        [8,8,7,9,8,5,6,7,1,1],
        [5,6,8,7,8,10,11,9,13,14],
    )
    roster=list(range(10))
    u=np.zeros((2,17,10)) # everyone active under p=1
    out=season_roster_utility(prep,roster,_league(),_model(),u)
    assert out["bench_insurance_value"] > 0
    assert out["bye_loss_ppg"] > 0


def test_playoff_bye_starter_is_reported():
    prep = _prep(
        ["QB","RB","RB","WR","WR","TE","RB","K","DST"],
        [8,8,7,9,8,5,6,1,1],
        [5,6,8,14,8,10,11,13,7],
    )
    p=deterministic_bye_profile(prep,list(range(9)),_league())
    assert p["playoff_bye_starters"] >= 1
