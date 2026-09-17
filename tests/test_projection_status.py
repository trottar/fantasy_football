from pathlib import Path
import pandas as pd

from src.diagnostics import projection_coverage


def test_projection_coverage(tmp_path: Path):
    p = tmp_path / "master.csv"
    pd.DataFrame([
        {"position": "WR", "espn_proj_points": 250.0},
        {"position": "WR", "espn_proj_points": None},
        {"position": "RB", "espn_proj_points": 220.0},
        {"position": "DST", "espn_proj_points": None},
    ]).to_csv(p, index=False)

    out = projection_coverage(p)
    wr = out[out["position"] == "WR"].iloc[0]
    rb = out[out["position"] == "RB"].iloc[0]
    assert wr["players"] == 2
    assert wr["projection_nonnull"] == 1
    assert abs(wr["coverage_fraction"] - 0.5) < 1e-12
    assert rb["projection_positive"] == 1
