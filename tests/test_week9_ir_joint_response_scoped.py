"""Public synthetic, source-bound tests: never touch ESPN or native MC receipts."""
from __future__ import annotations

from types import SimpleNamespace
import numpy as np
import pytest

from src import ir_joint_response as joint


class _Ctx:
    week = 9
    seed = 17
    cfg = {"paired_mean_interval_resamples": 40}
    team_id = 1
    predictive_scenarios = 64
    opponent_predictive = np.full((64, 17), 10.5)

    def __init__(self):
        self.roster = [
            {"espn_id": 11, "position": "QB", "injury_status": "OUT", "lineup_locked": False},
            {"espn_id": 100, "position": "QB", "injury_status": "ACTIVE"},
        ]
        self.actionable_available = [
            {"espn_id": 201, "position": "RB", "fantasy_status": "FREEAGENT"},
            {"espn_id": 202, "position": "WR", "fantasy_status": "WAIVERS"},
            {"espn_id": 203, "position": "K", "fantasy_status": "FREEAGENT"},
            {"espn_id": 204, "position": "DST", "fantasy_status": "FREEAGENT"},
            {"espn_id": 205, "position": "DST", "fantasy_status": "FREEAGENT"},
        ]

    def ensure_predictive_opponent_reference(self):
        return None


def _frontier(*, first=201, second=203):
    return {
        "sample_joint_states": [
            {"move_to_ir_espn_id": 11, "add_espn_ids": [first, second]},
        ]
    }


def _rows():
    return [
        {"add_espn_id": 201, "p_acquire": 1.0, "fantasy_status": "FREEAGENT"},
        {"add_espn_id": 202, "p_acquire": 0.6, "fantasy_status": "WAIVERS"},
        {"add_espn_id": 203, "p_acquire": 1.0, "fantasy_status": "FREEAGENT"},
        {"add_espn_id": 204, "p_acquire": 1.0, "fantasy_status": "FREEAGENT"},
        {"add_espn_id": 205, "p_acquire": 1.0, "fantasy_status": "FREEAGENT"},
    ]


def _ir_state():
    return {
        "status": "PASS", "ir_capacity": 1, "current_ir_occupancy": 0,
        "open_ir_slots": 1, "blockers": [], "invalid_current_ir_occupants": [],
        "new_acquisitions_blocked_by_ir_state": False,
        "direct_open_slot_add_capacity": 1, "ir_move_plus_add_capacity": 1,
        "potential_add_capacity": 2,
        "ir_move_candidate_count": 1,
        "ir_move_candidates": [
            {"espn_id": 11, "position": "QB", "injury_status": "OUT",
             "lineup_locked": False, "lineup_slot": "BE"},
        ],
        "position_headroom_total_roster": {p: 2 for p in ("QB", "RB", "WR", "TE", "DST", "K")},
    }


def _mock_native(monkeypatch):
    ctx = _Ctx()
    seen_rosters = []
    monkeypatch.setattr(joint, "_build_context", lambda *a, **k: ctx)
    monkeypatch.setattr(joint, "_static_team_weekly", lambda *a, **k: {})
    monkeypatch.setattr(joint, "simulate_specialist_market_policy", lambda ctx, *, position, user_mode, **k:
                        SimpleNamespace(delta=(2.0 if k.get("pre_acquire_espn_id") else 0.0)))
    def roster_mc(roster, ctx, **k):
        seen_rosters.append([p["espn_id"] for p in roster])
        ids = {p["espn_id"] for p in roster}
        baseline = 10.0 + (0.2 if 11 in ids else 0.0)
        adds = len(ids.intersection({201, 202}))
        baseline += (1.5 if adds == 2 else float(adds))
        arr = np.full((64, 17), baseline)
        return None, None, arr
    monkeypatch.setattr(joint, "evaluate_roster_predictive", roster_mc)
    monkeypatch.setattr(joint, "_compose_state", lambda weekly, opponent, ctx, *, d_policy, k_policy, **k:
                        (weekly + d_policy.delta + k_policy.delta, opponent, np.zeros(64)))
    # Keep native paired-statistics call shape but avoid slow bootstraps in fixtures.
    monkeypatch.setattr(joint, "_paired_stats", lambda delta, ctx, seed:
                        {"mean": float(np.mean(delta)), "classification": "FIXTURE_ONLY", "seed_salt": seed})
    return ctx, seen_rosters


def test_joint_probability_bounds_do_not_assume_independent_waivers():
    bounds = joint.joint_probability_bounds(0.4, 0.8)
    assert bounds["p_both_lower"] == pytest.approx(0.2)
    assert bounds["p_both_upper"] == pytest.approx(0.4)
    assert bounds["independence_assumed"] is False
    assert joint.joint_probability_bounds(1, 0.6)["p_both_upper"] == 0.6
    with pytest.raises(joint.UnsupportedJointState):
        joint.joint_probability_bounds(1.2, 0.8)


def test_paired_branch_summary_requires_five_aligned_outcomes():
    b = np.full(64, 0.5)
    with pytest.raises(joint.UnsupportedJointState, match="REQUIRED_ACQUISITION"):
        joint.paired_branch_comparison({"NO_ACTION": b}, 1, 1, ctx=_Ctx())
    vals = {key: b.copy() for key in ("NO_ACTION", "MOVE_ONLY", "FIRST_ONLY", "SECOND_ONLY", "BOTH")}
    vals["BOTH"] = np.zeros(63)
    with pytest.raises(joint.UnsupportedJointState, match="SCENARIO_ALIGNMENT"):
        joint.paired_branch_comparison(vals, 1, 1, ctx=_Ctx())
    vals["BOTH"] = np.full(64, 2.0)
    with pytest.raises(joint.UnsupportedJointState, match="H2H_RESPONSE_RANGE"):
        joint.paired_branch_comparison(vals, 1, 1, ctx=_Ctx())


def test_joint_shadow_is_opt_in_and_never_claims_full_coverage(monkeypatch):
    monkeypatch.setattr(joint, "_build_context", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not run")))
    r = joint.evaluate_bounded_joint_shadow({}, {}, {}, _ir_state(), _frontier(), _rows(),
                                             values_path="unused", team_name=None, team_id=1)
    assert r["status"] == "DISABLED" and r["coverage_complete"] is False


def test_mixed_player_specialist_joint_mc_uses_common_draws_not_sum(monkeypatch):
    ctx, rosters = _mock_native(monkeypatch)
    model = {"ir_joint_response": {"shadow_enabled": True, "max_shadow_pairs": 1, "shadow_scenarios": 64}}
    r = joint.evaluate_bounded_joint_shadow({}, {}, model, _ir_state(), _frontier(), _rows(),
                                             values_path="unused", team_name=None, team_id=1)
    assert r["status"] == "SCOPED_JOINT_SHADOW_ONLY"
    assert r["coverage_complete"] is False and r["action_authority"] == "NONE"
    candidate = r["paired_candidates"][0]
    assert candidate["status"] == "SCOPED_PAIRED_MC_EVALUATED_NOT_CERTIFIED"
    pair = candidate["paired"]
    assert pair["scenario_count"] == 64
    assert pair["conditional_response_computed_from_joint_state"] is True
    assert pair["joint_expected_utility_certified"] is False
    assert pair["conditional_h2h_paired_response"]["BOTH"]["mean"] == 1.0
    # The two independently successful additions are NOT added as utilities.
    assert (pair["conditional_h2h_paired_response"]["FIRST_ONLY"]["mean"] +
            pair["conditional_h2h_paired_response"]["SECOND_ONLY"]["mean"]) > \
        pair["conditional_h2h_paired_response"]["BOTH"]["mean"]
    assert 11 in rosters[0]  # no-action baseline
    assert all(11 not in ids for ids in rosters[1:])  # IR move excludes current-week starter
    assert r["future_capacity_credit"] is False


def test_two_same_specialist_channel_is_blocked_not_valued(monkeypatch):
    _mock_native(monkeypatch)
    model = {"ir_joint_response": {"shadow_enabled": True, "max_shadow_pairs": 1}}
    r = joint.evaluate_bounded_joint_shadow({}, {}, model, _ir_state(), _frontier(first=204, second=205), _rows(),
                                             values_path="unused", team_name=None, team_id=1)
    assert r["paired_candidates"][0]["status"] == "BLOCKED_UNSUPPORTED_JOINT_STATE"
    assert r["paired_candidates"][0]["reason"] == "TWO_SAME_SPECIALIST_CHANNEL_ACQUISITIONS_UNSUPPORTED"
    assert r["action_authority"] == "NONE"


def test_joint_headroom_and_budget_reject_unsupported_states(monkeypatch):
    _mock_native(monkeypatch)
    model = {"ir_joint_response": {"shadow_enabled": True, "max_shadow_pairs": 1}}
    state = _ir_state()
    state["position_headroom_total_roster"]["RB"] = 0
    r = joint.evaluate_bounded_joint_shadow({}, {}, model, state, _frontier(), _rows(),
                                             values_path="unused", team_name=None, team_id=1)
    assert r["paired_candidates"][0]["reason"] == "JOINT_POSITION_HEADROOM_INSUFFICIENT"
    with pytest.raises(joint.UnsupportedJointState, match="SHADOW_PAIR_BUDGET_INVALID"):
        joint.evaluate_bounded_joint_shadow({}, {}, {"ir_joint_response": {
            "shadow_enabled": True, "max_shadow_pairs": 500}}, _ir_state(), _frontier(), _rows(),
            values_path="unused", team_name=None, team_id=1)


def _mixed_native_state():
    return {
        "status": "PASS",
        "direct_open_slot_add_capacity": 1,
        "ir_move_plus_add_capacity": 1,
        "potential_add_capacity": 2,
        "ir_move_candidates": [
            {"espn_id": 11, "position": "QB", "injury_status": "OUT", "lineup_locked": False}
        ],
        "position_headroom_total_roster": {p: 2 for p in ("QB", "RB", "WR", "TE", "DST", "K")},
    }


def test_ir_adapter_shadow_hook_never_promotes_certification(monkeypatch):
    from src import ir_replacement as adapter
    monkeypatch.setattr(adapter, "evaluate_ir_roster_state", lambda *a, **k: _mixed_native_state())
    monkeypatch.setattr(adapter, "_player_candidates", lambda *a, **k:
                        ([{"add_espn_id": 201, "add_position": "RB"}], {"sample": 1}))
    monkeypatch.setattr(adapter, "_specialist_candidates", lambda *a, **k:
                        ([{"add_espn_id": 203, "add_position": "K"}], {"sample": 1}))
    calls = []
    def fake_shadow(*a, **k):
        calls.append((a, k))
        return {"status": "SCOPED_JOINT_SHADOW_ONLY", "action_authority": "NONE"}
    monkeypatch.setattr(joint, "evaluate_bounded_joint_shadow", fake_shadow)
    enabled = adapter.evaluate_ir_replacement({}, {}, {
        "ir_joint_response": {"shadow_enabled": True}
    })
    assert len(calls) == 1
    assert enabled["joint_mc_shadow"]["action_authority"] == "NONE"
    assert enabled["coverage_complete"] is False
    assert enabled["recommended_action"] is None
    assert enabled["joint_complete_roster_response_evaluated"] is False
    calls.clear()
    disabled = adapter.evaluate_ir_replacement({}, {}, {})
    assert not calls
    assert "joint_mc_shadow" not in disabled
    assert disabled["coverage_complete"] is False


@pytest.mark.parametrize("change,reason", [
    ({"status": "BLOCKED"}, "IR_ROSTER_STATE_NOT_PASS"),
    ({"open_ir_slots": 0}, "CURRENT_IR_CAPACITY_UNAVAILABLE_OR_INCONSISTENT"),
    ({"ir_capacity": 0}, "CURRENT_IR_CAPACITY_UNAVAILABLE_OR_INCONSISTENT"),
    ({"current_ir_occupancy": 1}, "CURRENT_IR_CAPACITY_UNAVAILABLE_OR_INCONSISTENT"),
    ({"direct_open_slot_add_capacity": 0}, "JOINT_TWO_OPENING_CAPACITY_UNPROVEN"),
    ({"new_acquisitions_blocked_by_ir_state": True}, "IR_ACQUISITIONS_BLOCKED_OR_UNPROVEN"),
    ({"invalid_current_ir_occupants": [{"espn_id": 99}]},
     "IR_OCCUPANCY_BLOCKERS_PRESENT_OR_UNPROVEN"),
    ({"blockers": ["INELIGIBLE_CURRENT_IR_OCCUPANT_BLOCKS_ACQUISITIONS"]},
     "IR_OCCUPANCY_BLOCKERS_PRESENT_OR_UNPROVEN"),
    ({"ir_move_candidates": [], "ir_move_candidate_count": 0},
     "IR_MOVE_NOT_IN_DECISION_TIME_CANDIDATES"),
    ({"ir_move_candidate_count": 2}, "IR_MOVE_CANDIDATE_SET_UNPROVEN"),
])
def test_direct_frontier_bad_ir_state_rejected_before_context(monkeypatch, change, reason):
    state = _ir_state()
    state.update(change)
    monkeypatch.setattr(joint, "_build_context", lambda *a, **k:
                        (_ for _ in ()).throw(AssertionError("no MC context permitted")))
    result = joint.evaluate_bounded_joint_shadow({}, {},
        {"ir_joint_response": {"shadow_enabled": True}}, state, _frontier(), _rows(),
        values_path="unused", team_name=None, team_id=1)
    assert result["paired_candidates"][0] == {
        "status": "BLOCKED_UNSUPPORTED_JOINT_STATE", "reason": reason}
    assert result["joint_predictive_mc"] == "NOT_EVALUATED"
    assert result["coverage_complete"] is False and result["action_authority"] == "NONE"


@pytest.mark.parametrize("field,value", [
    ("injury_status", "ACTIVE"), ("lineup_locked", True),
    ("lineup_slot", "IR"), ("position", "DST"),
])
def test_ineligible_candidate_row_blocked_before_context(monkeypatch, field, value):
    state = _ir_state()
    state["ir_move_candidates"][0][field] = value
    monkeypatch.setattr(joint, "_build_context", lambda *a, **k:
                        (_ for _ in ()).throw(AssertionError("no MC context permitted")))
    result = joint.evaluate_bounded_joint_shadow({}, {},
        {"ir_joint_response": {"shadow_enabled": True}}, state, _frontier(), _rows(),
        values_path="unused", team_name=None, team_id=1)
    assert result["paired_candidates"][0]["reason"] == "IR_MOVE_CANDIDATE_NOT_CURRENTLY_ELIGIBLE"
    assert result["action_authority"] == "NONE"


@pytest.mark.parametrize("change,reason", [
    ({"roster": []}, "MOVE_ASSET_NOT_OWNED_EXACTLY_ONCE"),
    ({"roster": [{"espn_id": 11, "position": "QB", "injury_status": "ACTIVE"}]},
     "IR_MOVE_INJURY_STATUS_UNSUPPORTED"),
    ({"roster": [{"espn_id": 11, "position": "QB", "injury_status": "OUT",
                  "lineup_locked": True}]}, "IR_MOVE_ASSET_ALREADY_LOCKED"),
    ({"roster": [{"espn_id": 11, "position": "RB", "injury_status": "OUT"}]},
     "IR_MOVE_CANDIDATE_ROSTER_STATE_MISMATCH"),
    ({"roster": [{"espn_id": 11, "position": "QB", "injury_status": "OUT",
                  "lineup_slot": "IR"}]}, "IR_MOVE_ASSET_ALREADY_IN_IR"),
])
def test_direct_frontier_mover_ownership_validation_precedes_baseline_mc(
        monkeypatch, change, reason):
    ctx, seen_rosters = _mock_native(monkeypatch)
    ctx.roster = change["roster"]
    result = joint.evaluate_bounded_joint_shadow({}, {},
        {"ir_joint_response": {"shadow_enabled": True}}, _ir_state(), _frontier(), _rows(),
        values_path="unused", team_name=None, team_id=1)
    assert result["paired_candidates"][0]["reason"] == reason
    assert result["joint_predictive_mc"] == "NOT_EVALUATED"
    assert not seen_rosters


def test_preflight_preserves_mixed_candidate_order_and_valid_response(monkeypatch):
    _, seen_rosters = _mock_native(monkeypatch)
    model = {"ir_joint_response": {"shadow_enabled": True, "max_shadow_pairs": 2}}
    frontier = {"sample_joint_states": [
        {"move_to_ir_espn_id": 99, "add_espn_ids": [201, 203]},
        {"move_to_ir_espn_id": 11, "add_espn_ids": [201, 203]},
    ]}
    result = joint.evaluate_bounded_joint_shadow({}, {}, model, _ir_state(), frontier, _rows(),
        values_path="unused", team_name=None, team_id=1)
    assert [c["status"] for c in result["paired_candidates"]] == [
        "BLOCKED_UNSUPPORTED_JOINT_STATE", "SCOPED_PAIRED_MC_EVALUATED_NOT_CERTIFIED"]
    assert result["paired_candidates"][0]["reason"] == "IR_MOVE_NOT_IN_DECISION_TIME_CANDIDATES"
    assert len(seen_rosters) == 5  # one baseline and four paired response branches
    assert result["action_authority"] == "NONE" and result["coverage_complete"] is False
