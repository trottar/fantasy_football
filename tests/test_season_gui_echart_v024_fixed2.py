from pathlib import Path

from src.gui.season_app import _set_echart_options


class ReadOnlyOptionsChart:
    def __init__(self):
        self._options = {"old": 1}
        self.update_calls = 0

    @property
    def options(self):
        return self._options

    def update(self):
        self.update_calls += 1


def test_echart_options_are_replaced_in_place_without_property_assignment():
    chart = ReadOnlyOptionsChart()
    original_mapping = chart.options
    _set_echart_options(chart, {"series": [{"type": "bar", "data": [1, 2]}]})
    assert chart.options is original_mapping
    assert chart.options == {"series": [{"type": "bar", "data": [1, 2]}]}
    assert chart.update_calls == 1


def test_season_gui_never_assigns_to_echart_options_property():
    source = Path("src/gui/season_app.py").read_text()
    assert ".options =" not in source
