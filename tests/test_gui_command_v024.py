from pathlib import Path

from fantasy import build_parser


def test_gui_command_is_season_control_room_and_draft_gui_remains_available():
    parser = build_parser()
    season = parser.parse_args(["gui"])
    snapshot = Path(season.snapshot)
    assert snapshot.name == "latest.json"
    assert snapshot.parent.name == "season_snapshots"
    assert hasattr(season, "values")
    draft = parser.parse_args(["draft-gui"])
    assert hasattr(draft, "board")
    assert draft.port == 8081
