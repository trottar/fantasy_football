from pathlib import Path
import json

import pandas as pd

from src.draft_state import DraftState
from src.roster_utility import (
    _active_roster_capacity,
    _core_roster_capacity,
    add_roster_marginal_values,
)


def league():
    return {
        "teams": 12,
        "roster": {
            "QB":1, "RB":2, "WR":2, "TE":1, "FLEX":1,
            "DST":1, "K":1, "BENCH":7, "IR":1,
        },
        "position_maximums": {
            "QB":4,"RB":8,"WR":8,"TE":3,"DST":3,"K":3
        },
    }


def model():
    return {
        "roster_utility": {
            "bench_option_weight":0.25,
            "bench_depth_decay":0.60,
            "candidate_floor_per_position":2,
        },
        "specialists": {
            "required_per_roster":{"K":1,"DST":1},
            "draft_only_when_core_filled":True,
            "activation_extra_picks":0,
        },
    }


def board():
    rows = []
    pid=1
    for pos in ["QB","RB","WR","TE"]:
        for i in range(20):
            rows.append({
                "espn_id":pid, "name":f"{pos}{i}", "position":pos,
                "latent_mean_ppg":20-i*0.2,
                "dynamic_replacement_ppg":10,
                "dynamic_vorp_ppg":max(10-i*0.2,0),
                "dynamic_draft_value":max(10-i*0.2,0),
                "espn_adp":50+pid, "market_pick_mean":50+pid,
                "market_pick_sigma":10, "draft_eligible":True,
            })
            pid += 1
    for pos in ["K","DST"]:
        for i in range(15):
            rows.append({
                "espn_id":pid, "name":f"{pos}{i}", "position":pos,
                "latent_mean_ppg":9-i*0.05,
                "dynamic_replacement_ppg":8,
                "dynamic_vorp_ppg":max(1-i*0.05,0),
                "dynamic_draft_value":max(1-i*0.05,0),
                "espn_adp":145+i, "market_pick_mean":145+i,
                "market_pick_sigma":20, "draft_eligible":True,
            })
            pid += 1
    return pd.DataFrame(rows)


def make_user_state(core_count: int, target_user_selection: int):
    """Create a valid 12-team slot-2 state on the requested user selection."""
    s = DraftState(12,16,2)
    user_picks = [2,23,26,47,50,71,74,95,98,119,122,143,146,167,170,191]
    target_overall = user_picks[target_user_selection-1]
    user_core_added=0
    for overall in range(1, target_overall):
        _,_,slot=s.expected_slot_for_pick(overall)
        if slot == 2 and user_core_added < core_count:
            # Rotate core positions; use IDs present in board.
            pos_cycle = ["QB","RB","RB","WR","WR","TE","RB","WR","RB","WR","RB","WR","RB","WR"]
            pos=pos_cycle[user_core_added % len(pos_cycle)]
            # Board IDs: QB 1-20, RB21-40, WR41-60, TE61-80
            bases={"QB":1,"RB":21,"WR":41,"TE":61}
            eid=bases[pos] + sum(1 for p in s.roster_for_slot(2) if p.get("position")==pos)
            s.record_pick(str(eid), f"{pos}{eid}", pos, "X", espn_id=eid)
            user_core_added+=1
        else:
            s.record_pick(str(100000+overall), f"O{overall}", "RB", "X", espn_id=100000+overall)
    assert s.next_overall == target_overall
    return s


def test_capacity_uses_bench_and_excludes_ir():
    assert _active_roster_capacity(league()) == 16
    assert _core_roster_capacity(league(), {"K":1,"DST":1}) == 14


def test_round_8_and_9_specialists_are_suppressed():
    b=board()
    for selection in (8,9):
        # Before selection 8 there are 7 user picks/core players; before 9 there are 8.
        s=make_user_state(selection-1, selection)
        valued=add_roster_marginal_values(b,b,s,league(),model())
        spec=valued[valued["position"].isin(["K","DST"])]
        assert not spec["roster_candidate_legal"].any()
        assert (spec["core_roster_slots_open"] > 0).all()


def test_selection_14_still_fills_last_core_bench_slot():
    b=board()
    s=make_user_state(13,14)
    valued=add_roster_marginal_values(b,b,s,league(),model())
    assert (valued["core_roster_slots_open"] == 1).all()
    spec=valued[valued["position"].isin(["K","DST"])]
    assert not spec["roster_candidate_legal"].any()
    core=valued[valued["position"].isin(["QB","RB","WR","TE"])]
    assert core["roster_candidate_legal"].any()


def test_selection_15_forces_specialists_after_14_core_slots():
    b=board()
    s=make_user_state(14,15)
    valued=add_roster_marginal_values(b,b,s,league(),model())
    assert (valued["core_roster_slots_open"] == 0).all()
    legal=valued[valued["roster_candidate_legal"].astype(bool)]
    assert set(legal["position"]) == {"K","DST"}


def test_after_k_selection_16_only_dst_is_legal():
    b=board()
    # State on selection 15 with 14 core.
    s=make_user_state(14,15)
    # Pick K at 170.
    krow=b[b["position"].eq("K")].iloc[0]
    s.record_pick(str(int(krow["espn_id"])), krow["name"], "K", "X", espn_id=int(krow["espn_id"]))
    # Opponent picks 171..190 until user's 191.
    while s.next_overall < 191:
        s.record_pick(str(200000+s.next_overall), f"O{s.next_overall}", "RB", "X", espn_id=200000+s.next_overall)
    assert s.next_overall == 191
    valued=add_roster_marginal_values(b,b,s,league(),model())
    legal=valued[valued["roster_candidate_legal"].astype(bool)]
    assert set(legal["position"]) == {"DST"}
