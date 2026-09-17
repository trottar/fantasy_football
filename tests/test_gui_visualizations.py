import pandas as pd

from src.gui.visualizations import tier_heatmap_options, value_survival_options


def test_visualization_options_are_serializable_shapes():
    df = pd.DataFrame([
        {"name":"A","position":"RB","p_survive":0.2,"dynamic_draft_value":8.0,"espn_adp":10.0,"tier":1,"visual_rank":1},
        {"name":"B","position":"WR","p_survive":0.8,"dynamic_draft_value":6.0,"espn_adp":20.0,"tier":2,"visual_rank":1},
    ])
    scatter = value_survival_options(df, 23)
    assert scatter["xAxis"]["max"] == 100
    assert len(scatter["series"]) == 4

    heat = tier_heatmap_options(df)
    assert heat["series"][0]["type"] == "heatmap"
    assert len(heat["series"][0]["data"]) == 2
