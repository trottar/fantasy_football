import pandas as pd

from src.draft_state import DraftState
from src.live_draft import evaluate_candidates


def test_recommendation_smoke():
    rows = []
    positions = ["RB", "WR", "TE", "QB"]
    espn_id = 1
    for pos in positions:
        for i in range(8):
            rows.append({
                "espn_id": espn_id,
                "name": f"{pos}{i}",
                "position": pos,
                "nfl_team": "PIT",
                "draft_eligible": True,
                "latent_mean_ppg": 20.0 - i * 0.5,
                "latent_mean_sd_ppg": 1.5,
                "espn_adp": 2.0 + espn_id,
                "espn_rank": 2.0 + espn_id,
                "market_pick_mean": 2.0 + espn_id,
                "market_pick_sigma": 4.0,
                "tier": 1,
            })
            espn_id += 1
    board = pd.DataFrame(rows)

    # Pick 1 is already gone, so pick 2 is the user's turn.
    state = DraftState(12, 4, 2)
    state.record_pick("999", "Taken", "RB", "DET", espn_id=999)

    league = {
        "teams": 12,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3},
    }
    model = {
        "draft_value": {
            "expected_rostered_counts": {"QB":18,"RB":20,"WR":20,"TE":12},
            "scarcity_lookahead_players": 3,
        },
        "live_draft": {
            "simulations": 10,
            "random_seed": 7,
            "candidate_limit": 4,
            "opponent_need_strength": 0.35,
            "market_hazard_floor": 1e-8,
            "replacement_weight": 1.0,
            "scarcity_weight": 0.25,
            "survival_option_weight": 0.35,
            "risk_penalty": 0.10,
        },
    }

    out = evaluate_candidates(
        board, state, league, model,
        simulations=10, seed=7, candidate_limit=4,
    )

    assert len(out) == 4
    assert out["mc_objective"].notna().all()
    assert out["immediate_draft_value"].notna().all()
    assert (out["simulations"] == 10).all()
