from pathlib import Path


def _source() -> str:
    return Path("src/gui/season_app.py").read_text(encoding="utf-8")


def test_trade_tab_is_local_read_only_and_exposes_three_way_response():
    source = _source()
    assert "ui.tab('Trades'" in source
    assert "Trade laboratory" in source
    assert "No ESPN trade is submitted" in source
    assert "P(accept)" in source
    assert "P(counter)" in source
    assert "P(reject)" in source
    assert "evaluate_trade_offer" in source


def test_trade_gui_supports_up_to_two_players_each_side():
    source = _source()
    assert "Give (up to 2)" in source
    assert "Receive (up to 2)" in source
    assert "len(give_ids) > 2" in source
    assert "len(receive_ids) > 2" in source


def test_waiver_gui_surfaces_higher_priority_manager_blockers():
    source = _source()
    assert "Higher-priority waiver blockers" in source
    assert "P(claim)" in source
    assert "best drop" in source


def test_fixed6_gui_labels_counterfactual_league_state_response():
    source = _source()
    assert "League-state EVΔ" in source
    assert "Release response: P(claimed)" in source
    assert "Contingent diagnostic only" in source
    assert "Combined EVΔ" not in source
