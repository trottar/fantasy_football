import json
from pathlib import Path

import pandas as pd

from src.draft_state import DraftState
from src.roster_utility import add_roster_marginal_values, diversified_candidate_pool
from src.specialists import build_specialist_rows, ensure_specialists_in_live_board


def _model(tmp_path: Path):
    model = {
        "latent_value": {"season_games": 17},
        "draft_market": {"adp_sentinel_floor": 169.5, "general_max_rank": 400},
        "roster_utility": {
            "bench_option_weight": 0.25,
            "bench_depth_decay": 0.60,
            "candidate_floor_per_position": 2,
        },
        "specialists": {
            "positions": ["K", "DST"],
            "required_per_roster": {"K": 1, "DST": 1},
            "backup_default": False,
            "activation_extra_picks": 2,
            "replacement_rank": {"K": 13, "DST": 13},
            "epistemic_sigma_ppg": {"K": 1.5, "DST": 2.0},
            "market_sigma_pick": 20.0,
        },
    }
    path = tmp_path / "model.json"
    path.write_text(json.dumps(model))
    return path, model


def _league():
    return {
        "teams": 12,
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1,"DST":1,"K":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3,"DST":3,"K":3},
    }


def test_build_specialist_rows(tmp_path: Path):
    rows = []
    for pos in ["K", "DST"]:
        for i in range(15):
            rows.append({
                "espn_id": 1000 + len(rows),
                "name": f"{pos}{i}",
                "position": pos,
                "nfl_team": "PIT",
                "espn_adp": 145 + i,
                "espn_rank": 145 + i,
                "espn_proj_points": 150 - i,
            })
    source = tmp_path / "player_master.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    model_path, _ = _model(tmp_path)
    out = build_specialist_rows(source, model_path)
    assert set(out["position"]) == {"K", "DST"}
    assert out["draft_eligible"].all()
    assert out["dynamic_vorp_ppg"].notna().all()
    assert out["market_pick_mean"].notna().all()


def test_append_specialists_to_existing_live_board(tmp_path: Path):
    live = tmp_path / "live.csv"
    pd.DataFrame([{
        "espn_id": 1, "name": "RB1", "position": "RB",
        "nfl_team": "PIT", "draft_eligible": True,
    }]).to_csv(live, index=False)
    rows = []
    for pos in ["K", "DST"]:
        for i in range(13):
            rows.append({
                "espn_id": 100 + len(rows), "name": f"{pos}{i}",
                "position": pos, "nfl_team": "PIT",
                "espn_adp": 150+i, "espn_rank": 150+i,
                "espn_proj_points": 140-i,
            })
    source = tmp_path / "player_master.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    model_path, _ = _model(tmp_path)
    assert ensure_specialists_in_live_board(live, source, model_path) == 26
    out = pd.read_csv(live)
    assert {"RB", "K", "DST"} <= set(out["position"])


def _state_at_170():
    state = DraftState(12, 16, 2)
    user_pos = ["QB","RB","RB","WR","WR","TE","RB","WR","RB","WR","RB","WR","RB","WR"]
    for overall in range(1, 170):
        _, _, slot = state.expected_slot_for_pick(overall)
        if slot == 2:
            idx = len(state.roster_for_slot(2))
            pos = user_pos[min(idx, len(user_pos)-1)]
        else:
            pos = "RB"
        state.record_pick(str(5000+overall), f"P{overall}", pos, "X", espn_id=5000+overall)
    assert state.next_overall == 170
    return state


def _late_candidates():
    return pd.DataFrame([
        {"espn_id":1,"name":"RBX","position":"RB","latent_mean_ppg":15.0,"dynamic_replacement_ppg":8.0,"dynamic_vorp_ppg":7.0,"dynamic_draft_value":7.0,"espn_adp":160.0},
        {"espn_id":2,"name":"WRX","position":"WR","latent_mean_ppg":15.0,"dynamic_replacement_ppg":9.0,"dynamic_vorp_ppg":6.0,"dynamic_draft_value":6.0,"espn_adp":160.0},
        {"espn_id":3,"name":"QBX","position":"QB","latent_mean_ppg":18.0,"dynamic_replacement_ppg":14.0,"dynamic_vorp_ppg":4.0,"dynamic_draft_value":4.0,"espn_adp":160.0},
        {"espn_id":4,"name":"TEX","position":"TE","latent_mean_ppg":12.0,"dynamic_replacement_ppg":8.0,"dynamic_vorp_ppg":4.0,"dynamic_draft_value":4.0,"espn_adp":160.0},
        {"espn_id":10,"name":"KX","position":"K","latent_mean_ppg":9.0,"dynamic_replacement_ppg":8.0,"dynamic_vorp_ppg":1.0,"dynamic_draft_value":1.0,"espn_adp":160.0},
        {"espn_id":11,"name":"DSTX","position":"DST","latent_mean_ppg":9.0,"dynamic_replacement_ppg":8.0,"dynamic_vorp_ppg":1.0,"dynamic_draft_value":1.0,"espn_adp":160.0},
    ])


def test_last_two_user_picks_force_k_dst(tmp_path: Path):
    _, model = _model(tmp_path)
    board = _late_candidates()
    state = _state_at_170()
    valued = add_roster_marginal_values(board.copy(), board.copy(), state, _league(), model)
    legal = valued[valued["roster_candidate_legal"].astype(bool)]
    assert set(legal["position"]) == {"K", "DST"}
    pool = diversified_candidate_pool(valued, 8, model)
    assert set(pool["position"]) == {"K", "DST"}


def test_after_dst_only_k_is_legal_on_final_pick(tmp_path: Path):
    _, model = _model(tmp_path)
    board = _late_candidates()
    state = _state_at_170()
    state.record_pick("11", "DSTX", "DST", "X", espn_id=11)  # 170 user
    while state.next_overall < 191:
        n = state.next_overall
        state.record_pick(str(90000+n), f"O{n}", "RB", "X", espn_id=90000+n)
    assert state.next_overall == 191
    avail = board[board["espn_id"] != 11].copy()
    valued = add_roster_marginal_values(avail, board, state, _league(), model)
    legal = valued[valued["roster_candidate_legal"].astype(bool)]
    assert set(legal["position"]) == {"K"}
