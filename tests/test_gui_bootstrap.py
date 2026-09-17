import json
from pathlib import Path

import pytest

from src.draft_state import DraftState
from src.gui.bootstrap import GuiStartupError, ensure_gui_runtime


def _write_config(tmp_path: Path):
    league = {
        "teams": 12,
        "draft": {
            "rounds": 16,
            "user_draft_slot": 2,
        },
    }
    league_path = tmp_path / "config" / "league.json"
    model_path = tmp_path / "config" / "model.json"
    league_path.parent.mkdir(parents=True)
    league_path.write_text(json.dumps(league))
    model_path.write_text(json.dumps({}))
    return league_path, model_path


def test_missing_data_gives_migration_message(tmp_path: Path):
    league, model = _write_config(tmp_path)
    board = tmp_path / "data" / "processed" / "live_board_2026.csv"
    state = tmp_path / "data" / "draft_state.json"

    with pytest.raises(GuiStartupError) as exc:
        ensure_gui_runtime(board, state, league, model)

    message = str(exc.value)
    assert "Copy the entire `data` directory" in message
    assert "v0.10" in message
    assert "pandas" not in message.lower()


def test_existing_board_initializes_state_only(tmp_path: Path):
    league, model = _write_config(tmp_path)
    board = tmp_path / "data" / "processed" / "live_board_2026.csv"
    board.parent.mkdir(parents=True)
    board.write_text("espn_id,name\\n1,Example\\n")
    state = tmp_path / "data" / "draft_state.json"

    result = ensure_gui_runtime(board, state, league, model)

    assert not result.board_built
    assert result.state_initialized
    loaded = DraftState.load(state)
    assert loaded.next_overall == 1
    assert loaded.user_draft_slot == 2


def test_existing_state_is_never_overwritten(tmp_path: Path):
    league, model = _write_config(tmp_path)
    board = tmp_path / "data" / "processed" / "live_board_2026.csv"
    board.parent.mkdir(parents=True)
    board.write_text("espn_id,name\\n1,Example\\n")
    state_path = tmp_path / "data" / "draft_state.json"

    state = DraftState(12, 16, 2)
    state.record_pick("123", "Already Drafted", "RB", "DET", espn_id=123)
    state.save(state_path)

    result = ensure_gui_runtime(board, state_path, league, model)

    assert not result.state_initialized
    loaded = DraftState.load(state_path)
    assert loaded.next_overall == 2
    assert loaded.picks[0]["player_name"] == "Already Drafted"
