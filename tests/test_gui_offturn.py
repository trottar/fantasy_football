import json
from pathlib import Path

import pandas as pd

from src.draft_state import DraftState
from src.gui.controller import DraftController


def test_controller_reports_waiting_forecast_target(tmp_path: Path):
    board = tmp_path / "board.csv"
    pd.DataFrame([
        {
            "espn_id": 1, "name": "A", "position": "RB", "nfl_team": "DET",
            "draft_eligible": True, "latent_mean_ppg": 10,
            "market_pick_mean": 10, "market_pick_sigma": 4,
        }
    ]).to_csv(board, index=False)

    league = tmp_path / "league.json"
    league.write_text(json.dumps({
        "teams": 12,
        "draft": {"rounds": 4, "user_draft_slot": 2},
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
    }))
    model = tmp_path / "model.json"
    model.write_text(json.dumps({
        "draft_value": {
            "expected_rostered_counts":{"QB":18,"RB":60,"WR":60,"TE":18},
            "scarcity_lookahead_players":5,
        },
        "live_draft":{"scarcity_weight":0.25},
    }))

    state_path = tmp_path / "state.json"
    state = DraftState(12, 4, 2)
    state.record_pick("9001", "P1", "RB", "X", espn_id=9001)
    state.record_pick("9002", "P2", "WR", "X", espn_id=9002)
    state.save(state_path)

    c = DraftController(board, state_path, league, model)
    info = c.turn_info()
    assert not info.user_on_clock
    assert info.next_user_pick == 23
    assert info.opponent_picks_until_user == 20
