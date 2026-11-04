from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np
import pytest

from src.ir_replacement import AUTHORITY, INFORMATION_POLICY, _resolve_current_capacity, evaluate_ir_replacement
from src.specialist_policy_v032 import simulate_specialist_market_policy
from src.weekly_decision_cycle import _ir_receipt


def _ir_state(**updates):
    base = {
        "status": "PASS",
        "direct_open_slot_add_capacity": 0,
        "ir_move_plus_add_capacity": 1,
        "potential_add_capacity": 1,
        "ir_move_candidates": [{"espn_id": 11, "name": "Out QB", "position": "QB", "injury_status": "OUT", "lineup_locked": False}],
        "position_headroom_total_roster": {"QB": 1, "RB": 1, "WR": 1, "TE": 1, "DST": 2, "K": 2},
        "blockers": [],
    }
    base.update(updates)
    return base


def test_capacity_accepts_only_one_current_opened_slot():
    result = _resolve_current_capacity(_ir_state())
    assert result["coverage_complete"] is True
    assert result["reason"] == "IR_MOVE_OPENS_ONE_ACTIVE_SLOT"

    direct = _resolve_current_capacity(_ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=0,
        potential_add_capacity=1, ir_move_candidates=[],
    ))
    assert direct["coverage_complete"] is True
    assert direct["reason"] == "DIRECT_OPEN_ACTIVE_SLOT_CURRENT_ONLY"
    assert direct["move_to_ir"] is None

    multiple = _resolve_current_capacity(_ir_state(
        ir_move_plus_add_capacity=2, potential_add_capacity=2,
        ir_move_candidates=[{"espn_id": 11}, {"espn_id": 12}],
    ))
    assert multiple["coverage_complete"] is False
    assert multiple["reason"] == "MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED"


class _FakeCtx:
    predictive_scenarios = 4
    team_id = 1
    week = 4

    def __init__(self, candidate_locked=False):
        self.snapshot = {"snapshot_utc": "2026-10-02T12:00:00+00:00"}
        self.espn = {"teams": [{"team_id": 1, "waiver_rank": 1}]}
        self.roster = [{
            "espn_id": 100, "name": "Owned K", "position": "K",
            "fantasy_status": "ROSTERED", "lineup_slot": "K", "lineup_locked": False,
        }]
        self.all_team_rosters = {1: list(self.roster)}
        self.actionable_available = [{
            "espn_id": 200, "name": "Candidate K", "position": "K",
            "fantasy_status": "FREEAGENT", "lineup_slot": "",
            "lineup_locked": bool(candidate_locked),
        }]

    def lock_timing(self, player, week):
        return SimpleNamespace(kickoff=datetime(2026, 10, 3, 20, 0, tzinfo=timezone.utc))


def test_specialist_current_only_open_slot_supports_second_k_without_enabling_carry2(monkeypatch):
    import src.specialist_policy_v032 as module

    def fake_samples(player, ctx, week):
        mean = 8.0 if int(player["espn_id"]) == 200 else 5.0
        return np.full(int(ctx.predictive_scenarios), mean), mean, {"source": "TEST"}

    monkeypatch.setattr(module, "_specialist_week_samples", fake_samples)
    ctx = _FakeCtx()

    result = simulate_specialist_market_policy(
        ctx, position="K", user_mode="OPEN_SLOT_PLUS_ONE_CURRENT_ONLY",
        pre_acquire_espn_id=200,
    )
    assert result.user_capacity == 2
    assert result.mode == "OPEN_SLOT_PLUS_ONE_CURRENT_ONLY"
    assert result.user_plan[0]["starter_espn_id"] == 200
    assert np.all(result.team_weekly[-1][:, 3] == 8.0)
    assert np.all(result.team_weekly[-1][:, 4:] == 0.0)

    with pytest.raises(ValueError, match="two-kicker policy is disabled"):
        simulate_specialist_market_policy(ctx, position="K", user_mode="CARRY2")


def test_specialist_current_only_open_slot_reuses_lock_boundary(monkeypatch):
    import src.specialist_policy_v032 as module
    monkeypatch.setattr(module, "_specialist_week_samples", lambda player, ctx, week: (
        np.ones(int(ctx.predictive_scenarios)), 1.0, {"source": "TEST"}
    ))
    ctx = _FakeCtx(candidate_locked=True)
    with pytest.raises(ValueError, match="already locked"):
        simulate_specialist_market_policy(
            ctx, position="K", user_mode="OPEN_SLOT_PLUS_ONE_CURRENT_ONLY",
            pre_acquire_espn_id=200,
        )


def test_ir_adapter_authorizes_no_drop_action_and_never_credits_future(monkeypatch):
    import src.ir_replacement as module

    monkeypatch.setattr(module, "evaluate_ir_roster_state", lambda *args, **kwargs: _ir_state())
    monkeypatch.setattr(module, "_player_candidates", lambda *args, **kwargs: ([
        {
            "channel": "PLAYER", "add_espn_id": 21, "add_name": "Candidate",
            "add_position": "RB", "fantasy_status": "FREEAGENT",
            "drop_espn_id": None, "drop_name": None, "p_acquire": 1.0,
            "conditional_complete_state_delta": {"mean": 0.08, "classification": "ACTIONABLE_EDGE"},
            "expected_complete_state_delta_mean": 0.08,
            "classification": "ACTIONABLE_EDGE",
            "future_capacity_credit": False, "information_policy": INFORMATION_POLICY,
        }
    ], {"preselected": 1, "predictive_frontier": 1, "mc_scenarios": 64, "screen_authority": False}))
    monkeypatch.setattr(module, "_specialist_candidates", lambda *args, **kwargs: ([], {
        "candidates_considered": 0, "mc_scenarios": 64,
        "open_slot_policy": "OPEN_SLOT_PLUS_ONE_CURRENT_ONLY",
        "general_two_kicker_carry_policy_unchanged": "DISABLED",
        "legal_kicker_open_slot_branch_skipped": False,
    }))

    report = evaluate_ir_replacement({}, {}, {})
    assert report["authority"] == AUTHORITY
    assert report["coverage_complete"] is True
    assert report["future_capacity_credit"] is False
    assert report["multiweek_absence_horizon_used"] is False
    assert report["recommended_action"]["drop_espn_id"] is None


def test_ir_adapter_fails_closed_when_position_headroom_is_incomplete(monkeypatch):
    import src.ir_replacement as module
    state = _ir_state()
    del state["position_headroom_total_roster"]["K"]
    monkeypatch.setattr(module, "evaluate_ir_roster_state", lambda *args, **kwargs: state)
    report = evaluate_ir_replacement({}, {}, {})
    assert report["coverage_complete"] is False
    assert report["coverage_reason"] == "POSITION_MAXIMUM_HEADROOM_INCOMPLETE"


def test_ir_receipt_accepts_enriched_hold_and_action():
    hold_report = {
        "authority": AUTHORITY, "status": "PASS", "coverage_complete": True,
        "coverage_reason": "NO_CURRENT_IR_OPENED_SLOT_CAPACITY",
        "future_capacity_credit": False, "multiweek_absence_horizon_used": False,
        "candidate_rows": [], "recommended_action": None,
    }
    hold = _ir_receipt(hold_report)
    assert hold.status == "PASS / HOLD:IR_REPLACEMENT"

    action_report = dict(hold_report)
    action_report["coverage_reason"] = "IR_MOVE_OPENS_ONE_ACTIVE_SLOT"
    action_report["recommended_action"] = {
        "kind": "IR_MOVE_PLUS_ADD", "move_to_ir": {"espn_id": 11},
        "add": {"add_espn_id": 21, "classification": "ACTIONABLE_EDGE", "drop_espn_id": None},
        "drop_espn_id": None,
    }
    action = _ir_receipt(action_report)
    assert action.status == "PASS / ACTION"


def test_raw_b2a_receipt_remains_fail_closed_for_backward_compatibility():
    receipt = _ir_receipt(_ir_state())
    assert receipt.status == "INCOMPLETE_COVERAGE:GATE_B_IR_REPLACEMENT_VALUE_AND_ABSENCE_HORIZON"


def test_direct_open_active_slot_is_current_only_and_no_ir_move(monkeypatch):
    import src.ir_replacement as module

    state = _ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=0,
        potential_add_capacity=1, ir_move_candidates=[],
    )
    monkeypatch.setattr(module, "evaluate_ir_roster_state", lambda *args, **kwargs: state)
    monkeypatch.setattr(module, "_player_candidates", lambda *args, **kwargs: ([{
        "channel": "PLAYER", "add_espn_id": 21, "add_name": "Current candidate",
        "add_position": "RB", "fantasy_status": "FREEAGENT",
        "drop_espn_id": None, "drop_name": None, "p_acquire": 1.0,
        "conditional_complete_state_delta": {
            "mean": 0.08, "classification": "ACTIONABLE_EDGE",
        },
        "expected_complete_state_delta_mean": 0.08,
        "classification": "ACTIONABLE_EDGE", "future_capacity_credit": False,
        "information_policy": INFORMATION_POLICY,
    }], {"preselected": 1, "predictive_frontier": 1, "screen_authority": False}))
    monkeypatch.setattr(module, "_specialist_candidates", lambda *args, **kwargs: (
        [], {"candidates_considered": 0, "open_slot_policy": "OPEN_SLOT_PLUS_ONE_CURRENT_ONLY"}
    ))

    report = evaluate_ir_replacement({}, {}, {})
    assert report["authority"] == AUTHORITY
    assert report["coverage_complete"] is True
    assert report["coverage_reason"] == "DIRECT_OPEN_ACTIVE_SLOT_CURRENT_ONLY"
    assert report["move_to_ir"] is None
    assert report["future_capacity_credit"] is False
    assert report["multiweek_absence_horizon_used"] is False
    action = report["recommended_action"]
    assert action["kind"] == "DIRECT_OPEN_SLOT_ADD"
    assert action["move_to_ir"] is None
    assert action["drop_espn_id"] is None
    assert action["future_capacity_credit"] is False
    assert action["add"]["add_espn_id"] == 21
    assert _ir_receipt(report).status == "PASS / ACTION"


def test_current_open_slot_never_implicitly_authorizes_two_slots():
    more_than_one = _resolve_current_capacity(_ir_state(
        direct_open_slot_add_capacity=2, ir_move_plus_add_capacity=0,
        potential_add_capacity=2, ir_move_candidates=[],
    ))
    assert more_than_one["coverage_complete"] is False
    assert more_than_one["reason"] == "MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED"

    mixed = _resolve_current_capacity(_ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=1,
        potential_add_capacity=2,
    ))
    assert mixed["coverage_complete"] is False
    assert mixed["reason"] == "MIXED_DIRECT_PLUS_IR_MOVE_JOINT_RESPONSE_UNMODELED"


def test_direct_open_slot_still_requires_full_position_headroom(monkeypatch):
    import src.ir_replacement as module
    state = _ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=0,
        potential_add_capacity=1, ir_move_candidates=[],
    )
    del state["position_headroom_total_roster"]["K"]
    monkeypatch.setattr(module, "evaluate_ir_roster_state", lambda *args, **kwargs: state)
    report = evaluate_ir_replacement({}, {}, {})
    assert report["coverage_complete"] is False
    assert report["coverage_reason"] == "POSITION_MAXIMUM_HEADROOM_INCOMPLETE"
    assert report["recommended_action"] is None


def test_mixed_one_direct_plus_ir_move_is_recognized_without_joint_authority():
    state = _ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=1,
        potential_add_capacity=2,
    )
    found = _resolve_current_capacity(state)
    assert found["coverage_complete"] is False
    assert found["reason"] == "MIXED_DIRECT_PLUS_IR_MOVE_JOINT_RESPONSE_UNMODELED"
    assert found["direct_only_supported"] is True
    assert found["potential_current_additions"] == 2
    assert len(found["ir_move_alternatives"]) == 1


def test_mixed_frontier_counts_distinct_moves_and_joint_position_headroom():
    import src.ir_replacement as module
    state = _ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=1,
        potential_add_capacity=2,
        ir_move_candidates=[
            {"espn_id": 11, "position": "QB", "injury_status": "OUT", "lineup_locked": False},
            {"espn_id": 12, "position": "RB", "injury_status": "INJURY_RESERVE", "lineup_locked": False},
            {"espn_id": 13, "position": "WR", "injury_status": "OUT", "lineup_locked": False},
        ],
        position_headroom_total_roster={"QB": 1, "RB": 1, "WR": 1, "TE": 1, "DST": 1, "K": 1},
    )
    capacity = _resolve_current_capacity(state)
    rows = [
        {"add_espn_id": 201, "add_position": "RB"},
        {"add_espn_id": 202, "add_position": "DST"},
        {"add_espn_id": 203, "add_position": "K"},
        {"add_espn_id": 204, "add_position": "RB"},
    ]
    report = module._mixed_two_opening_frontier(state, capacity, rows)
    # Six unique pairs; the RB+RB pair violates the total-roster maximum.
    assert report["move_alternatives"] == 3
    assert report["screened_structural_joint_states"] == 15
    assert report["joint_predictive_mc"] == "NOT_EVALUATED"
    assert report["joint_acquisition_behavior"] == "NOT_EVALUATED"
    assert report["all_legal_composites_certified"] is False
    assert report["action_authority"] == "NONE"
    assert all(len(x["add_espn_ids"]) == 2 for x in report["sample_joint_states"])


def test_mixed_capacity_values_scoped_direct_add_but_never_recommends(monkeypatch):
    import src.ir_replacement as module
    state = _ir_state(direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=1,
                      potential_add_capacity=2)
    monkeypatch.setattr(module, "evaluate_ir_roster_state", lambda *args, **kwargs: state)
    monkeypatch.setattr(module, "_player_candidates", lambda *args, **kwargs: ([{
        "channel": "PLAYER", "add_espn_id": 21, "add_position": "RB",
        "classification": "ACTIONABLE_EDGE", "expected_complete_state_delta_mean": 0.3,
    }], {"preselected": 1}))
    monkeypatch.setattr(module, "_specialist_candidates", lambda *args, **kwargs: ([{
        "channel": "DST", "add_espn_id": 22, "add_position": "DST",
        "classification": "ACTIONABLE_EDGE", "expected_complete_state_delta_mean": 0.2,
    }], {"candidates_considered": 1}))
    report = evaluate_ir_replacement({}, {}, {})
    assert report["status"] == "PASS"
    assert report["coverage_complete"] is False
    assert report["direct_open_slot_scoped_evaluated"] is True
    assert len(report["direct_only_scoped_candidate_rows"]) == 2
    assert report["joint_state_frontier"]["screened_structural_joint_states"] == 1
    assert report["joint_complete_roster_response_evaluated"] is False
    assert report["recommended_action"] is None
    receipt = _ir_receipt(report)
    assert receipt.status.startswith("INCOMPLETE_COVERAGE")
    assert receipt.action is None


def test_mixed_invalid_move_and_more_than_two_stay_blocked():
    invalid = _resolve_current_capacity(_ir_state(
        direct_open_slot_add_capacity=1, ir_move_plus_add_capacity=1,
        potential_add_capacity=2,
        ir_move_candidates=[{"espn_id": 11, "injury_status": "QUESTIONABLE", "lineup_locked": False}],
    ))
    assert invalid["reason"] == "MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED"
    three = _resolve_current_capacity(_ir_state(
        direct_open_slot_add_capacity=2, ir_move_plus_add_capacity=1,
        potential_add_capacity=3,
    ))
    assert three["reason"] == "MULTIPLE_CURRENT_OPEN_SLOTS_UNSUPPORTED"
