from __future__ import annotations

from src.ir_roster_state import build_ir_roster_state
from src.weekly_decision_cycle import _ir_receipt


def _league(*, active=2, ir=1):
    return {
        "roster": {"QB": 1, "BENCH": active - 1, "IR": ir},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "DST": 3, "K": 3},
    }


def _player(pid, name, *, status="ACTIVE", slot="BENCH", locked=False, position="RB"):
    return {
        "espn_id": pid,
        "name": name,
        "position": position,
        "injury_status": status,
        "lineup_slot": slot,
        "lineup_locked": locked,
        # Deliberately include IR for every player. The authority must not use this
        # compatibility list as current IR eligibility.
        "eligible_slots": ["BENCH", "IR"],
    }


def test_ir_move_eligibility_uses_espn_injury_status_not_slot_compatibility():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Out", status="OUT", slot="BENCH", position="RB"),
        ]
    }
    state = build_ir_roster_state(team, _league())

    assert state["status"] == "PASS"
    assert state["active_roster_capacity"] == 2
    assert state["active_roster_occupancy"] == 2
    assert state["open_active_roster_slots"] == 0
    assert state["ir_capacity"] == 1
    assert state["open_ir_slots"] == 1
    assert state["ir_compatible_roster_players"] == 2
    assert state["eligible_slots_used_for_ir_eligibility"] is False
    assert state["ir_move_candidate_count"] == 1
    assert state["ir_move_candidates"][0]["espn_id"] == 2
    assert state["ir_move_candidates"][0]["injury_status"] == "OUT"
    assert state["ir_move_plus_add_capacity"] == 1
    assert state["potential_add_capacity"] == 1


def test_questionable_current_ir_incumbent_may_remain_and_does_not_block_adds():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Bench", status="ACTIVE", slot="BENCH"),
            _player(3, "IR Q", status="QUESTIONABLE", slot="IR"),
        ]
    }
    state = build_ir_roster_state(team, _league())

    assert state["status"] == "PASS"
    assert state["current_ir_occupancy"] == 1
    assert state["open_ir_slots"] == 0
    assert state["invalid_current_ir_occupants"] == []
    assert state["new_acquisitions_blocked_by_ir_state"] is False


def test_healthy_current_ir_incumbent_blocks_new_acquisitions_fail_closed():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Bench", status="ACTIVE", slot="BENCH"),
            _player(3, "Healthy IR", status="ACTIVE", slot="IR"),
        ]
    }
    state = build_ir_roster_state(team, _league())

    assert state["status"] == "BLOCKED"
    assert state["new_acquisitions_blocked_by_ir_state"] is True
    assert state["potential_add_capacity"] == 0
    assert "INELIGIBLE_CURRENT_IR_OCCUPANT_BLOCKS_ACQUISITIONS" in state["blockers"]


def test_locked_out_player_is_not_a_move_to_ir_candidate():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Locked Out", status="OUT", slot="BENCH", locked=True),
        ]
    }
    state = build_ir_roster_state(team, _league())
    assert state["ir_move_candidate_count"] == 0
    assert state["ir_move_plus_add_capacity"] == 0


def test_position_limits_count_the_full_owned_roster_not_only_active_slots():
    league = _league()
    league["position_maximums"]["RB"] = 1
    team = {
        "roster": [
            _player(1, "QB", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Out RB", status="OUT", slot="BENCH", position="RB"),
        ]
    }
    state = build_ir_roster_state(team, league)
    assert state["position_counts_total_roster"]["RB"] == 1
    assert state["position_headroom_total_roster"]["RB"] == 0


def test_weekly_ir_receipt_records_transition_state_but_remains_fail_closed_for_value_and_horizon():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Out", status="OUT", slot="BENCH", position="RB"),
        ]
    }
    state = build_ir_roster_state(team, _league())
    receipt = _ir_receipt(state)

    assert receipt.status == "INCOMPLETE_COVERAGE:GATE_B_IR_REPLACEMENT_VALUE_AND_ABSENCE_HORIZON"
    assert receipt.authority == "ir_roster_state.evaluate_ir_roster_state"
    assert receipt.evidence["ir_move_plus_add_available"] is True
    assert receipt.evidence["multiweek_absence_horizon_supported"] is False
    assert receipt.action is None
    assert "authoritative replacement value" in str(receipt.gap)


def test_weekly_ir_receipt_preserves_blocked_ir_state():
    team = {
        "roster": [
            _player(1, "Healthy", status="ACTIVE", slot="QB", position="QB"),
            _player(2, "Bench", status="ACTIVE", slot="BENCH"),
            _player(3, "Healthy IR", status="ACTIVE", slot="IR"),
        ]
    }
    receipt = _ir_receipt(build_ir_roster_state(team, _league()))
    assert receipt.status == "INCOMPLETE_COVERAGE:GATE_B_IR_ROSTER_STATE_BLOCKED"
    assert "INELIGIBLE_CURRENT_IR_OCCUPANT_BLOCKS_ACQUISITIONS" in str(receipt.gap)
