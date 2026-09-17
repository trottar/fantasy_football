import pandas as pd

from src.draft_state import DraftState
from src.fast_recommend import evaluate_candidates_fast


def test_fast_evaluates_multiple_positions_after_rb_saturation():
    rows = []
    pid = 1
    for pos, repl, base in [("RB",8,18),("WR",9,16),("QB",15,20),("TE",8,12)]:
        for i in range(12):
            rows.append({
                "espn_id":pid,"name":f"{pos}{i+1}","position":pos,"nfl_team":"X",
                "draft_eligible":True,"latent_mean_ppg":base-i*0.3,
                "latent_mean_sd_ppg":1.5,"espn_adp":float(pid),"espn_rank":float(pid),
                "market_pick_mean":float(pid),"market_pick_sigma":4.0,
                "dynamic_replacement_ppg":repl,"tier":1,
            })
            pid += 1
    board = pd.DataFrame(rows)

    # 2-team snake, user slot 1; construct a legal user turn after user already
    # holds RB1/RB2/RB3. Opponent filler IDs are outside the board.
    state = DraftState(2, 8, 1)
    # overall 1 user RB1, 2 opp, 3 opp, 4 user RB2, 5 user RB3, 6 opp -> next 7 opp not user.
    # Add through overall 8 so next 9 is user in round 5 for slot 1.
    sequence = [
        (1,"RB1","RB",1),(2,"O1","WR",9001),(2,"O2","WR",9002),
        (1,"RB2","RB",2),(1,"RB3","RB",3),(2,"O3","RB",9003),
        (2,"O4","TE",9004),(1,"QBfill","QB",25),
    ]
    # At pick 9 in 2-team snake, slot1 is user.
    for slot, name, pos, eid in sequence:
        rnd, pir, expected_slot = state.expected_slot_for_pick(state.next_overall)
        assert expected_slot == slot
        state.record_pick(str(eid), name, pos, "X", espn_id=eid)

    league = {
        "teams":2,"roster":{"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
        "position_maximums":{"QB":4,"RB":8,"WR":8,"TE":3},
    }
    model = {
        "draft_value":{"expected_rostered_counts":{"QB":4,"RB":12,"WR":12,"TE":4},"scarcity_lookahead_players":3},
        "live_draft":{"scarcity_weight":0.25,"random_seed":1,"replacement_weight":1.0,
            "survival_option_weight":0.35,"risk_penalty":0.1,"opponent_need_strength":0.35,"market_hazard_floor":1e-8},
        "fast_engine":{"candidate_limit":8,"long_simulations":20},
        "roster_utility":{"bench_option_weight":0.25,"bench_depth_decay":0.60,"candidate_floor_per_position":2},
    }

    out = evaluate_candidates_fast(board, state, league, model, simulations=20, candidate_limit=8, seed=1)
    assert len(set(out["position"])) >= 3
    # Missing WR starters should now be meaningfully represented.
    assert "WR" in set(out.head(5)["position"])
