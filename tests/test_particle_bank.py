import numpy as np
import pandas as pd

from src.draft_state import DraftState
from src.particle_bank import condition_bank, load_bank, save_bank


def _board():
    return pd.DataFrame([
        {"espn_id": i, "name": f"P{i}", "position": "WR", "draft_eligible": True}
        for i in range(1, 7)
    ])


def _league():
    return {
        "teams": 4,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
    }


def _model():
    return {
        "live_draft": {"opponent_need_strength": 0.35},
        "full_rollout": {"deep_market_queue_lookahead": 4, "deep_queue_temperature": 2.0},
        "specialists": {"backup_default": False},
        "particle_bank": {
            "conditioning_likelihood_floor": 0.001,
            "conditioning_temperature": 1.0,
            "degraded_ess_fraction": 0.25,
        },
    }


def test_observed_opponent_pick_reweights_particles(tmp_path):
    state = DraftState(4, 4, 1)
    state.record_pick("1", "P1", "WR", "X", espn_id=1)
    bank = tmp_path / "bank.npz"
    orders = np.asarray([
        [2, 3, 4, 5, 6, 1],
        [3, 2, 4, 5, 6, 1],
        [4, 3, 2, 5, 6, 1],
    ], dtype=np.int64)
    save_bank(bank, orders, state, source="DEEP-FULL")

    # Pick 2 belongs to opponent slot 2. Seeing P2 should favor particles
    # where P2 was nearer the front of the latent market queue.
    state.record_pick("2", "P2", "WR", "X", espn_id=2)
    loaded, status = condition_bank(bank, _board(), state, _league(), _model())
    w = loaded["weights"]
    assert status.valid
    assert status.observed_opponent_picks == 1
    assert status.conditioned_through == 2
    assert w[0] > w[1] > w[2]
    assert status.ess < 3.0


def test_user_choice_selects_anchor_branch_without_penalizing_particles(tmp_path):
    state = DraftState(4, 4, 1)
    bank = tmp_path / "bank.npz"
    orders = np.asarray([
        [1, 2, 3, 4, 5, 6],
        [2, 1, 3, 4, 5, 6],
    ], dtype=np.int64)
    save_bank(
        bank, orders, state, source="DEEP-FULL",
        summary_rows=[{"espn_id": 1, "name": "P1"}, {"espn_id": 2, "name": "P2"}],
    )
    state.record_pick("1", "P1", "WR", "X", espn_id=1)
    loaded, status = condition_bank(bank, _board(), state, _league(), _model())
    assert status.valid
    assert status.selected_branch_id == 1
    assert status.selected_branch_name == "P1"
    assert status.observed_opponent_picks == 0
    assert np.allclose(loaded["weights"], [0.5, 0.5])


def test_bank_invalid_if_history_before_anchor_changes(tmp_path):
    state = DraftState(4, 4, 1)
    state.record_pick("1", "P1", "WR", "X", espn_id=1)
    bank = tmp_path / "bank.npz"
    orders = np.asarray([[2, 3, 4, 5, 6, 1]], dtype=np.int64)
    save_bank(bank, orders, state, source="DEEP-FULL")
    state.undo_last_pick()
    _, status = condition_bank(bank, _board(), state, _league(), _model())
    assert status.exists
    assert not status.valid
    assert "history changed" in status.message.lower()


def test_conditioning_persists_weights(tmp_path):
    state = DraftState(4, 4, 1)
    state.record_pick("1", "P1", "WR", "X", espn_id=1)
    bank = tmp_path / "bank.npz"
    orders = np.asarray([
        [2, 3, 4, 5, 6, 1],
        [3, 2, 4, 5, 6, 1],
    ], dtype=np.int64)
    save_bank(bank, orders, state, source="DEEP-FULL")
    state.record_pick("2", "P2", "WR", "X", espn_id=2)
    loaded, status = condition_bank(bank, _board(), state, _league(), _model(), persist=True)
    reread = load_bank(bank)
    assert status.valid
    assert np.allclose(loaded["weights"], reread["weights"])
    assert int(reread["meta"]["conditioned_through"]) == 2
