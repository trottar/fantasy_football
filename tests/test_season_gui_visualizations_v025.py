import json

from src.gui.season_visualizations import (
    action_week_overlay_options,
    closure_residual_options,
    lineup_lab_distribution_options,
    matchup_slot_delta_options,
    model_espn_scatter_options,
    uncertainty_breakdown_options,
)


def test_v025_visualizations_are_json_serializable():
    hist = [{"x": 100.0, "count": 2.0}, {"x": 110.0, "count": 3.0}]
    diag = {"game_sd": 6.0, "model_sd": 2.0, "kinematic_sd": 1.0}
    slots = [{"slot": "QB", "us_name": "A", "opponent_name": "B", "delta": 2.4}]
    ledger = [
        {"name": "A", "model": 12.0, "espn": 10.0, "model_minus_espn": 2.0, "observed": None, "operational": 11.2},
        {"name": "B", "model": 8.0, "espn": 9.0, "model_minus_espn": -1.0, "observed": None, "operational": 8.4},
    ]
    options_list = [
        lineup_lab_distribution_options(hist, hist, hist),
        matchup_slot_delta_options(slots),
        uncertainty_breakdown_options(diag),
        action_week_overlay_options(hist, hist),
        model_espn_scatter_options(ledger),
        closure_residual_options(ledger),
    ]
    for options in options_list:
        json.dumps(options)
        assert "series" in options


def test_closure_residual_switches_to_observed_minus_mc_when_data_exist():
    rows = [{"name": "A", "observed": 15.0, "operational": 12.0, "model_minus_espn": 1.0}]
    options = closure_residual_options(rows)
    assert "Observed" in options["title"]["text"]
    assert options["series"][0]["data"] == [3.0]
