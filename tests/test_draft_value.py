import json
from pathlib import Path

import pandas as pd

from src.draft_value import build_draft_values


def test_draft_value_replacement_and_flex(tmp_path: Path):
    rows = []
    specs = {
        "QB": 24,
        "RB": 70,
        "WR": 70,
        "TE": 30,
    }
    for pos, n in specs.items():
        for i in range(n):
            rows.append({
                "name": f"{pos}{i+1}",
                "position": pos,
                "nfl_team": "PIT",
                "latent_mean_ppg": 25.0 - 0.2 * i,
                "latent_mean_sd_ppg": 1.0,
                "predictive_weekly_sd_ppg": 5.0,
                "espn_adp": float(i + 1),
                "espn_rank": float(i + 1),
                "model_status": "history+projection",
            })

    values = tmp_path / "values.csv"
    pd.DataFrame(rows).to_csv(values, index=False)

    league = {
        "teams": 12,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}
    }
    league_path = tmp_path / "league.json"
    league_path.write_text(json.dumps(league))

    model = {
        "draft_value": {
            "expected_rostered_counts": {
                "QB": 18, "RB": 60, "WR": 60, "TE": 18
            },
            "tier_gap_sigma": 0.35,
            "tier_min_absolute_gap_ppg": 0.75,
            "scarcity_lookahead_players": 5,
            "starter_allocation": {
                "QB_per_team": 1,
                "RB_per_team": 2,
                "WR_per_team": 2,
                "TE_per_team": 1,
                "FLEX_per_team": 1,
                "flex_eligible": ["RB", "WR", "TE"],
            },
        }
    }
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(model))

    out_path = tmp_path / "draft.csv"
    diag_path = tmp_path / "diag.json"

    out, diag = build_draft_values(
        values, league_path, model_path, out_path, diag_path
    )

    # 12 QB + 24 RB + 24 WR + 12 TE mandatory = 72, plus 12 FLEX = 84.
    assert sum(diag["starter_counts"].values()) == 84

    # Replacement player is rank count+1.
    assert diag["replacement"]["QB"]["replacement_rank"] == 19
    assert diag["replacement"]["RB"]["replacement_rank"] == 61
    assert diag["replacement"]["WR"]["replacement_rank"] == 61
    assert diag["replacement"]["TE"]["replacement_rank"] == 19

    rb1 = out[out["name"] == "RB1"].iloc[0]
    rb61 = out[out["name"] == "RB61"].iloc[0]
    assert rb1["vorp_ppg"] > 0
    assert abs(rb61["vorp_ppg"]) < 1e-12
    assert out_path.exists()
    assert diag_path.exists()


def test_tiers_are_position_local(tmp_path: Path):
    # Reuse a tiny league to verify tier column is integer-like and populated.
    rows = [
        {"name": "WR1", "position": "WR", "latent_mean_ppg": 20.0, "latent_mean_sd_ppg": 1.0, "espn_adp": 1},
        {"name": "WR2", "position": "WR", "latent_mean_ppg": 19.8, "latent_mean_sd_ppg": 1.0, "espn_adp": 2},
        {"name": "WR3", "position": "WR", "latent_mean_ppg": 17.0, "latent_mean_sd_ppg": 1.0, "espn_adp": 3},
        {"name": "QB1", "position": "QB", "latent_mean_ppg": 25.0, "latent_mean_sd_ppg": 1.0, "espn_adp": 4},
    ]
    # Add enough filler rows for replacement indexing.
    for pos in ["QB", "RB", "WR", "TE"]:
        for i in range(1, 8):
            rows.append({
                "name": f"{pos}F{i}",
                "position": pos,
                "latent_mean_ppg": 10.0 - 0.1*i,
                "latent_mean_sd_ppg": 1.0,
                "espn_adp": 10 + i,
            })

    values = tmp_path / "values.csv"
    pd.DataFrame(rows).to_csv(values, index=False)

    league_path = tmp_path / "league.json"
    league_path.write_text(json.dumps({"teams": 2}))
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps({
        "draft_value": {
            "expected_rostered_counts": {"QB": 2, "RB": 2, "WR": 2, "TE": 2},
            "tier_gap_sigma": 0.35,
            "tier_min_absolute_gap_ppg": 0.75,
            "scarcity_lookahead_players": 2,
            "starter_allocation": {
                "QB_per_team": 1, "RB_per_team": 1, "WR_per_team": 1,
                "TE_per_team": 1, "FLEX_per_team": 1,
                "flex_eligible": ["RB", "WR", "TE"],
            },
        }
    }))

    out, _ = build_draft_values(
        values, league_path, model_path, tmp_path / "out.csv"
    )
    wr = out[out["name"].isin(["WR1", "WR2", "WR3"])].set_index("name")
    assert int(wr.loc["WR1", "tier"]) == int(wr.loc["WR2", "tier"])
    assert int(wr.loc["WR3", "tier"]) > int(wr.loc["WR2", "tier"])
