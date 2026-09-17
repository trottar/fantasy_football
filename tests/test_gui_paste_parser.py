import pandas as pd

from src.gui.paste_parser import (
    preview_is_committable,
    preview_pasted_picks,
    remove_already_recorded,
)


def _board():
    return pd.DataFrame([
        {"espn_id": 1, "name": "Jahmyr Gibbs", "position": "RB", "nfl_team": "DET"},
        {"espn_id": 2, "name": "Bijan Robinson", "position": "RB", "nfl_team": "ATL"},
        {"espn_id": 3, "name": "Puka Nacua", "position": "WR", "nfl_team": "LAR"},
    ])


def test_paste_parser_resolves_numbered_espn_like_rows():
    text = """
Round 1
1.01 Jahmyr Gibbs DET RB
1.02 Bijan Robinson ATL RB
1.03 Puka Nacua LAR WR
"""
    rows = preview_pasted_picks(text, _board(), 1, 12)
    assert [r.overall for r in rows] == [1, 2, 3]
    assert [r.espn_id for r in rows] == [1, 2, 3]
    assert preview_is_committable(rows)


def test_paste_parser_accepts_plain_names_sequentially():
    rows = preview_pasted_picks(
        "Jahmyr Gibbs\nBijan Robinson", _board(), 5, 12
    )
    assert [r.overall for r in rows] == [5, 6]
    assert preview_is_committable(rows)


def test_paste_parser_blocks_wrong_pick_and_duplicates():
    wrong = preview_pasted_picks(
        "1.03 Jahmyr Gibbs", _board(), 1, 12
    )
    assert wrong[0].status == "error"

    duplicate = preview_pasted_picks(
        "1 Jahmyr Gibbs\n2 Jahmyr Gibbs", _board(), 1, 12
    )
    assert duplicate[1].status == "error"
    assert not preview_is_committable(duplicate)


def test_paste_parser_marks_already_drafted_as_benign_overlap():
    rows = preview_pasted_picks(
        "1 Jahmyr Gibbs", _board(), 2, 12,
        drafted_espn_ids={1}, drafted_picks_by_espn_id={1: 1},
    )
    assert rows[0].status == "already_recorded"
    assert rows[0].overall == 1
    assert not preview_is_committable(rows)  # no genuinely new picks


def test_overlap_window_does_not_advance_expected_new_pick():
    rows = preview_pasted_picks(
        "1 Jahmyr Gibbs\n2 Bijan Robinson\n3 Puka Nacua",
        _board(), 3, 12,
        drafted_espn_ids={1, 2},
        drafted_picks_by_espn_id={1: 1, 2: 2},
    )
    assert [r.status for r in rows] == [
        "already_recorded", "already_recorded", "resolved"
    ]
    assert [r.overall for r in rows] == [1, 2, 3]
    assert preview_is_committable(rows)


def test_remove_already_recorded_helper():
    rows = preview_pasted_picks(
        "1 Jahmyr Gibbs\n2 Bijan Robinson\n3 Puka Nacua",
        _board(), 3, 12,
        drafted_espn_ids={1, 2},
        drafted_picks_by_espn_id={1: 1, 2: 2},
    )
    kept, removed = remove_already_recorded(rows)
    assert removed == 2
    assert len(kept) == 1
    assert kept[0].name == "Puka Nacua"
    assert kept[0].overall == 3


def test_conflicting_pick_number_for_recorded_player_is_error():
    rows = preview_pasted_picks(
        "2 Jahmyr Gibbs", _board(), 2, 12,
        drafted_espn_ids={1}, drafted_picks_by_espn_id={1: 1},
    )
    assert rows[0].status == "error"
    assert "Already recorded at pick 1" in rows[0].message
