import json
from pathlib import Path
import pandas as pd

from src.pipeline import build_live_board


def test_live_board_recomputes_replacement_on_eligible_universe(tmp_path: Path):
    rows = []
    # 25 QBs so the QB replacement boundary exists.
    for i in range(25):
        rows.append({
            "espn_id": 1000+i, "name": f"QB{i}", "position": "QB",
            "nfl_team": "PIT", "latent_mean_ppg": 25-i*0.3,
            "latent_mean_sd_ppg": 2.0, "espn_adp": 20+i,
            "espn_rank": 20+i, "espn_proj_points": 250,
            "model_status": "history+projection",
        })
    # Stale high-PPG player must be excluded and not define boundary.
    rows.append({
        "espn_id": 9999, "name": "Stale QB", "position": "QB",
        "nfl_team": "FA", "latent_mean_ppg": 40.0,
        "latent_mean_sd_ppg": 2.0, "espn_adp": 169.9,
        "espn_rank": 1900, "espn_proj_points": None,
        "model_status": "history_only",
    })
    # Fill other positions enough for starter/replacement code.
    for pos in ["RB", "WR", "TE"]:
        n = 70 if pos in ["RB", "WR"] else 25
        for i in range(n):
            rows.append({
                "espn_id": hash((pos, i)) % 10000000 + 20000,
                "name": f"{pos}{i}", "position": pos,
                "nfl_team": "DET", "latent_mean_ppg": 20-i*0.2,
                "latent_mean_sd_ppg": 2.0, "espn_adp": 30+i,
                "espn_rank": 30+i, "espn_proj_points": 200,
                "model_status": "history+projection",
            })

    values = tmp_path / "values.csv"
    pd.DataFrame(rows).to_csv(values, index=False)

    league = tmp_path / "league.json"
    league.write_text(json.dumps({
        "teams": 12,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
    }))
    model = tmp_path / "model.json"
    model.write_text(json.dumps({
        "draft_market": {
            "adp_sentinel_floor": 169.5,
            "history_only_max_rank": 250,
            "general_max_rank": 400,
            "market_pick_sigma_floor": 4.0,
            "market_pick_sigma_fraction": 0.10,
            "market_pick_sigma_cap": 24.0,
            "adp_bins": [0,24,48,72,96,120,144,169.5],
        },
        "draft_value": {
            "expected_rostered_counts": {"QB":18,"RB":60,"WR":60,"TE":18},
            "tier_gap_sigma":0.35,
            "tier_min_absolute_gap_ppg":0.75,
            "scarcity_lookahead_players":5,
            "starter_allocation":{
                "QB_per_team":1,"RB_per_team":2,"WR_per_team":2,
                "TE_per_team":1,"FLEX_per_team":1,
                "flex_eligible":["RB","WR","TE"],
            },
        },
    }))

    out, diag = build_live_board(
        values, league, model,
        tmp_path/"market.csv", tmp_path/"draft.csv", tmp_path/"live.csv",
        tmp_path/"market_diag.json", tmp_path/"draft_diag.json",
    )

    stale = out[out["name"] == "Stale QB"].iloc[0]
    assert not bool(stale["draft_eligible"])
    assert diag["replacement"]["QB"]["replacement_player"] != "Stale QB"
