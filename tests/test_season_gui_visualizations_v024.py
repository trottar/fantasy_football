import json

from src.gui.season_visualizations import (
    action_delta_options,
    component_bar_options,
    distribution_overlay_options,
    margin_distribution_options,
    player_prediction_options,
)


def test_season_gui_visualizations_are_json_serializable():
    hist = [{"x": 100.0, "count": 2.0}, {"x": 110.0, "count": 3.0}]
    diag = {
        "model_mean": 12.0,
        "matchup_model_mean": 13.0,
        "espn_anchor": 12.5,
        "operational_mean": 12.8,
        "kinematic_components": {"pace": 0.02, "pressure": -0.01},
    }
    for options in (
        distribution_overlay_options(hist, hist),
        margin_distribution_options(hist),
        player_prediction_options(diag),
        component_bar_options(diag),
        action_delta_options(hist),
    ):
        json.dumps(options)
        assert "series" in options
