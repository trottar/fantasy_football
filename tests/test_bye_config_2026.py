import json
from pathlib import Path


def test_all_32_teams_have_exactly_one_2026_bye():
    league=json.loads((Path(__file__).parents[1]/"config"/"league.json").read_text())
    byes=league["bye_weeks_2026"]
    assert len(byes)==32
    assert set(byes.values()) <= {5,6,7,8,9,10,11,13,14}
    assert byes["ARI"]==14
    assert byes["DAL"]==14
    assert byes["BUF"]==7
    assert byes["KC"]==5
