from pathlib import Path
import numpy as np
from src import specialist_policy_v032 as v32
from tests.test_specialist_policy_v032 import FakeCtx, install_fake_physics, player


def test_fixed4_delayed_second_slot_has_no_early_user_add(monkeypatch):
    install_fake_physics(monkeypatch)
    owned = player(1, "Owned", 8, 4)
    free = player(2, "Free", 7, 9, status="FREEAGENT", slot="BENCH")
    opp = player(3, "Opp", 3, 3)
    ctx = FakeCtx([owned], [opp], [free])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="CARRY2", activation_week=2)
    assert not [t for t in result.transactions if t["team_id"] == 1 and t["week"] == 1]
    assert [t for t in result.transactions if t["team_id"] == 1 and t["week"] == 2 and t["action"] == "ADD"]
    assert result.activation_week == 2


def test_fixed4_release_state_begins_at_activation_week():
    base = np.ones((4, 17), dtype=float)
    released = np.full((4, 17), 2.0, dtype=float)
    shift = np.arange(17, dtype=float)
    weekly, timed_shift = v32._timed_release_state(base, released, shift, 3)
    np.testing.assert_array_equal(weekly[:, :2], base[:, :2])
    np.testing.assert_array_equal(weekly[:, 2:], released[:, 2:])
    np.testing.assert_array_equal(timed_shift[:2], np.zeros(2))
    np.testing.assert_array_equal(timed_shift[2:], shift[2:])


def test_fixed4_production_carry_is_activation_based_not_candidate_enumeration():
    source = Path(v32.__file__).read_text(encoding="utf-8")
    assert "for activation_week in range" in source
    assert "pre_acquire_espn_id=cid" not in source
    assert "TEMPORAL_INFORMATION_MODEL" in source
    assert "RECOMPUTED_AT_ACTIVATION_STATE_V033" in source
    assert "FROZEN_CURRENT_PLAYER_CLAIM_RESPONSE_APPLIED_FROM_ACTIVATION_WEEK_V032_FIXED4" not in source


def test_fixed4_cli_has_real_newlines_and_unresolved_proposal_holds(capsys):
    from fantasy import _print_specialist_channel
    report = {
        "week": 1, "channel": "KICKER", "team_name": "Us", "position": "K", "mc_scenarios": 64,
        "owned": [{"name": "Owned K", "team": "KC"}],
        "baseline": {"weighted_mean_ppg": 8.0, "current_week_mean": 8.0, "current_week_sd": 3.0, "current_week_choice": "Owned K"},
        "swap_actions": [],
        "one_slot_policy": {
            "weighted_mean_ppg": 8.4, "delta_vs_static_ppg": 0.4,
            "proposal_current_action": {"action": "SWAP", "add": "Free K", "drop": "Owned K"},
            "recommended_current_action": {"action": "HOLD"},
            "complete_state_delta": {"mean": 0.008, "mean_p16": 0.006, "mean_p84": 0.010, "p_better": 0.38, "p_tie": 0.32, "p_worse": 0.30, "classification": "NO_RESOLVED_EDGE"},
            "weekly_plan": [],
        },
        "dynamic_carry_actions": [],
    }
    _print_specialist_channel(report)
    out = capsys.readouterr().out
    assert "\\n" not in out
    assert "policy proposal=SWAP Free K / DROP Owned K | current recommendation=HOLD" in out
    out.encode("cp1252")


def test_fixed4_release_metadata():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.35-fixed1")
    assert (root / "DATA_SOURCES.md").read_text(encoding="utf-8").startswith("# Data-source contract — v0.35-fixed1")
