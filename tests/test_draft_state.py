from src.draft_state import DraftState
from src.league import user_overall_picks


def test_user_pick_sequence():
    assert user_overall_picks(12, 16, 2) == [
        2, 23, 26, 47, 50, 71, 74, 95,
        98, 119, 122, 143, 146, 167, 170, 191
    ]


def test_snake_slots():
    state = DraftState(12, 16, 2)
    for i in range(1, 24):
        state.record_pick(f"p{i}", f"Player {i}")
    assert state.picks[1]["fantasy_team_slot"] == 2   # overall pick 2
    assert state.picks[22]["fantasy_team_slot"] == 2 # overall pick 23
