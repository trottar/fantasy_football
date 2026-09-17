import json
from pathlib import Path

import pandas as pd

from src.draft_state import DraftState
from src.gui.controller import DraftController


def _write_fixture(tmp_path: Path):
    board = tmp_path / "board.csv"
    rows = []
    espn_id = 1
    for pos in ["RB", "WR", "TE", "QB"]:
        for i in range(20):
            rows.append({
                "espn_id": espn_id,
                "name": f"{pos} Player {i+1}",
                "position": pos,
                "nfl_team": "PIT",
                "draft_eligible": True,
                "latent_mean_ppg": 25 - i * 0.5,
                "latent_mean_sd_ppg": 1.5,
                "espn_adp": float(espn_id),
                "espn_rank": float(espn_id),
                "market_pick_mean": float(espn_id),
                "market_pick_sigma": 4.0,
                "tier": 1 if i < 3 else 2,
                "espn_proj_points": 250.0,
                "model_status": "history+projection",
            })
            espn_id += 1
    pd.DataFrame(rows).to_csv(board, index=False)

    league = tmp_path / "league.json"
    league.write_text(json.dumps({
        "teams": 12,
        "draft": {"rounds": 16, "user_draft_slot": 2},
        "roster": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1},
        "position_maximums": {"QB":4,"RB":8,"WR":8,"TE":3},
    }))

    model = tmp_path / "model.json"
    model.write_text(json.dumps({
        "draft_value": {
            "expected_rostered_counts": {"QB":18,"RB":60,"WR":60,"TE":18},
            "scarcity_lookahead_players": 5,
        },
        "live_draft": {
            "scarcity_weight": 0.25,
            "simulations": 10,
            "random_seed": 1,
            "candidate_limit": 4,
            "opponent_need_strength": 0.35,
            "market_hazard_floor": 1e-8,
            "replacement_weight": 1.0,
            "survival_option_weight": 0.35,
            "risk_penalty": 0.10,
        },
    }))

    state_path = tmp_path / "state.json"
    DraftState(12, 16, 2).save(state_path)
    return board, state_path, league, model


def test_controller_record_undo_and_turn_modes(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)

    info = c.turn_info()
    assert info.next_overall == 1
    assert not info.user_on_clock
    assert info.next_user_pick == 2

    c.record_player("RB Player 1")
    info = c.turn_info()
    assert info.next_overall == 2
    assert info.user_on_clock
    assert info.mode == "LONG TURN"

    undone = c.undo_last_pick()
    assert undone["player_name"] == "RB Player 1"
    assert c.state().next_overall == 1


def test_controller_batch_commit_and_visual_frames(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)

    rows = c.preview_paste("1 RB Player 1\n2 WR Player 1")
    assert len(rows) == 2
    committed = c.commit_preview()
    assert [p["overall"] for p in committed] == [1, 2]
    assert c.state().next_overall == 3

    frame, target = c.survival_frame(20)
    assert target == 23
    assert "p_survive" in frame.columns
    assert len(frame) <= 20

    tiers = c.tier_frame(5)
    assert set(tiers["position"]) == {"RB", "WR", "TE", "QB"}
    assert tiers.groupby("position").size().max() <= 5



def test_controller_overlap_paste_commits_only_new_picks(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)

    first = c.record_player("RB Player 1")
    assert first["overall"] == 1

    rows = c.preview_paste("1 RB Player 1\n2 WR Player 1\n3 TE Player 1")
    assert [r.status for r in rows] == [
        "already_recorded", "resolved", "resolved"
    ]

    committed = c.commit_preview()
    assert [p["overall"] for p in committed] == [2, 3]
    assert c.state().next_overall == 4
    assert [p["player_name"] for p in c.state().picks] == [
        "RB Player 1", "WR Player 1", "TE Player 1"
    ]


def test_controller_can_remove_already_picked_from_preview(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)
    c.record_player("RB Player 1")

    c.preview_paste("1 RB Player 1\n2 WR Player 1")
    rows, removed = c.remove_already_picked_from_preview()
    assert removed == 1
    assert len(rows) == 1
    assert rows[0].name == "WR Player 1"
    assert rows[0].overall == 2



def test_controller_recommendation_rows_must_be_currently_available(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)
    initial_sig = c.state_signature()

    # Initially the candidate is legal.
    ok, stale = c.recommendation_rows_match_current_state([
        {"espn_id": 1, "name": "RB Player 1"}
    ])
    assert ok
    assert stale == []

    c.record_player("RB Player 1")
    assert c.state_signature() != initial_sig

    # A result produced before that state change must not be displayable now.
    ok, stale = c.recommendation_rows_match_current_state([
        {"espn_id": 1, "name": "RB Player 1"}
    ])
    assert not ok
    assert stale == ["RB Player 1"]



def test_controller_reset_draft_clears_state_and_particle_bank_only(tmp_path: Path):
    board, state_path, league, model = _write_fixture(tmp_path)
    c = DraftController(board, state_path, league, model)

    c.record_player("RB Player 1")
    c.record_player("WR Player 1")
    assert c.state().next_overall == 3

    # The reset must remove the stale state-conditioned bank. Its contents do
    # not matter for this controller-level test.
    c.bank_path.write_bytes(b"stale deep bank")
    preserved = tmp_path / "preserved_calibration.csv"
    preserved.write_text("keep me")

    result = c.reset_draft()

    fresh = c.state()
    assert result["previous_picks"] == 2
    assert result["bank_removed"] is True
    assert fresh.next_overall == 1
    assert fresh.picks == []
    assert fresh.num_teams == 12
    assert fresh.rounds == 16
    assert fresh.user_draft_slot == 2
    assert not c.bank_path.exists()
    assert preserved.read_text() == "keep me"
