from src.draft_state import DraftState


def test_undo_last_pick():
    state = DraftState(12, 16, 2)
    assert state.undo_last_pick() is None
    state.record_pick("1", "A", "RB", "DET", espn_id=1)
    state.record_pick("2", "B", "WR", "PIT", espn_id=2)
    last = state.undo_last_pick()
    assert last["player_name"] == "B"
    assert state.next_overall == 2
    assert len(state.picks) == 1
