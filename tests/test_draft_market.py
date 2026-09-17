import json
from pathlib import Path

import pandas as pd

from src.draft_market import (
    build_market_values,
    conditional_survival_probability,
    next_user_pick,
)


def test_conditional_survival_is_monotonic():
    p23 = conditional_survival_probability(25.0, 6.0, 2, 23)
    p26 = conditional_survival_probability(25.0, 6.0, 2, 26)
    assert 0.0 <= p26 <= p23 <= 1.0

    # Conditioning on survival to pick 23 increases the chance of also
    # surviving to 26 relative to an unconditional start-of-draft view.
    cond = conditional_survival_probability(25.0, 6.0, 23, 26)
    assert cond >= p26


def test_next_user_pick_slot_2():
    assert next_user_pick(2, 12, 16, 2) == 23
    assert next_user_pick(23, 12, 16, 2) == 26
    assert next_user_pick(26, 12, 16, 2) == 47


def test_market_eligibility_excludes_stale_history_only(tmp_path: Path):
    rows = [
        {
            "name": "Current Star", "position": "RB", "nfl_team": "DET",
            "espn_adp": 10.0, "espn_rank": 8.0,
            "espn_proj_points": 300.0,
            "model_status": "history+projection",
            "draft_value_score": 10.0,
        },
        {
            "name": "Stale Veteran", "position": "RB", "nfl_team": "ARI",
            "espn_adp": 169.95, "espn_rank": 1800.0,
            "espn_proj_points": None,
            "model_status": "history_only",
            "draft_value_score": 9.0,
        },
        {
            "name": "Free Agent", "position": "WR", "nfl_team": "FA",
            "espn_adp": 50.0, "espn_rank": 50.0,
            "espn_proj_points": 200.0,
            "model_status": "history+projection",
            "draft_value_score": 8.0,
        },
        {
            "name": "Current Sleeper", "position": "WR", "nfl_team": "PIT",
            "espn_adp": 60.0, "espn_rank": 55.0,
            "espn_proj_points": 180.0,
            "model_status": "projection_only",
            "draft_value_score": 7.0,
        },
    ]
    path = tmp_path / "draft.csv"
    pd.DataFrame(rows).to_csv(path, index=False)

    league = tmp_path / "league.json"
    league.write_text(json.dumps({"teams": 12}))
    model = tmp_path / "model.json"
    model.write_text(json.dumps({
        "draft_market": {
            "adp_sentinel_floor": 169.5,
            "history_only_max_rank": 250,
            "general_max_rank": 400,
            "market_pick_sigma_floor": 4.0,
            "market_pick_sigma_fraction": 0.10,
            "market_pick_sigma_cap": 24.0,
            "adp_bins": [0, 24, 48, 72, 96, 120, 144, 169.5],
        }
    }))

    out, diag = build_market_values(
        path, league, model,
        tmp_path / "market.csv",
        tmp_path / "diag.json",
    )

    status = out.set_index("name")["draft_eligible"].to_dict()
    assert bool(status["Current Star"])
    assert bool(status["Current Sleeper"])
    assert not bool(status["Stale Veteran"])
    assert not bool(status["Free Agent"])
    assert diag["eligible_players"] == 2
