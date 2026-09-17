import json
from pathlib import Path

import pandas as pd

from src.draft_state import DraftState
from src.live_draft import (
    resolve_player,
    available_board,
    dynamic_replacement_levels,
    next_user_pick_after,
    is_user_pick,
    draft_state_signature,
)


def _board():
    return pd.DataFrame([
        {
            "espn_id": 1, "name": "Alpha One", "position": "RB",
            "nfl_team": "DET", "draft_eligible": True,
            "latent_mean_ppg": 20.0, "espn_adp": 1.0,
            "market_pick_mean": 1.0, "market_pick_sigma": 4.0,
        },
        {
            "espn_id": 2, "name": "Beta Two Jr.", "position": "RB",
            "nfl_team": "ATL", "draft_eligible": True,
            "latent_mean_ppg": 18.0, "espn_adp": 5.0,
            "market_pick_mean": 5.0, "market_pick_sigma": 4.0,
        },
        {
            "espn_id": 3, "name": "Gamma", "position": "WR",
            "nfl_team": "PIT", "draft_eligible": False,
            "latent_mean_ppg": 17.0, "espn_adp": 10.0,
            "market_pick_mean": 10.0, "market_pick_sigma": 4.0,
        },
    ])


def test_resolve_and_remove_drafted():
    board = _board()
    row = resolve_player(board, "Beta Two")
    assert int(row["espn_id"]) == 2

    state = DraftState(12, 16, 2)
    state.record_pick("1", "Alpha One", "RB", "DET", espn_id=1)
    avail = available_board(board, state)
    assert set(avail["espn_id"].astype(int)) == {2}


def test_dynamic_replacement_uses_drafted_counts():
    board = pd.DataFrame([
        {
            "espn_id": i, "name": f"RB{i}", "position": "RB",
            "draft_eligible": True, "latent_mean_ppg": 30-i
        }
        for i in range(1, 8)
    ])
    state = DraftState(2, 4, 1)
    state.record_pick("1", "RB1", "RB", "X", espn_id=1)
    avail = available_board(board, state)
    repl = dynamic_replacement_levels(
        avail, state, {"QB": 1, "RB": 4, "WR": 1, "TE": 1}
    )
    # Four expected total RB rostered, one already drafted: first 3 available
    # are still rostered, so the 4th available is replacement.
    assert repl["RB"]["remaining_expected_rostered"] == 3
    assert repl["RB"]["replacement_player"] == "RB5"


def test_snake_turn_helpers():
    state = DraftState(12, 16, 2)
    assert not is_user_pick(state, 1)
    assert is_user_pick(state, 2)

    # Record pick 1 so next pick is user's 1.02.
    state.record_pick("x", "X", "RB", "DET")
    assert is_user_pick(state)
    assert next_user_pick_after(state) == 23



def test_available_board_legacy_numeric_player_id_fallback():
    board = _board()
    state = DraftState(12, 16, 2)
    # Simulate legacy row: espn_id key exists but is null; player_id is numeric.
    state.record_pick("1", "Alpha One", "RB", "DET", espn_id=None)
    avail = available_board(board, state)
    assert 1 not in set(avail["espn_id"].astype(int))


def test_available_board_legacy_name_position_fallback():
    board = _board()
    state = DraftState(12, 16, 2)
    state.record_pick("alpha_one", "Alpha One", "RB", "DET", espn_id=None)
    avail = available_board(board, state)
    assert 1 not in set(avail["espn_id"].astype(int))


def test_draft_state_signature_changes_with_pick():
    state = DraftState(12, 16, 2)
    before = draft_state_signature(state)
    state.record_pick("1", "Alpha One", "RB", "DET", espn_id=1)
    after = draft_state_signature(state)
    assert before != after
    assert after == draft_state_signature(state)
