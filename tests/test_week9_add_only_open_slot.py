"""Public synthetic regression for direct vacant-slot player acquisitions.

No ESPN API, private runtime data, or native MC capture is used here.
"""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from src import open_slot_actions as oa
from src import transaction_manager as tm
from src.weekly_decision_cycle import _player_receipt


def _league(*, active=2, ir=1, qb_max=3):
    return {
        "roster": {"QB": 1, "BENCH": active - 1, "IR": ir},
        "position_maximums": {"QB": qb_max, "RB": 5, "WR": 5, "TE": 5},
    }


def _ctx(*, roster=None):
    roster = roster if roster is not None else [
        {"espn_id": 11, "position": "QB", "lineup_slot": "QB", "injury_status": "ACTIVE"},
    ]
    return SimpleNamespace(
        team={"roster": roster}, roster=roster, seed=123,
        cfg={"action_mc_final_keep_per_status": 4,
             "action_mc_stages": [], "paired_mean_interval_resamples": 100,
             "actionable_p_better": .9, "lean_p_better": .67},
        predictive_scenarios=8,
    )


def _candidate(pid, pos, status="FREEAGENT"):
    return {"espn_id": pid, "name": "Candidate " + str(pid),
            "position": pos, "fantasy_status": status, "lineup_locked": False}


def test_open_slot_candidate_covers_all_player_positions_and_no_fake_drop():
    ctx = _ctx()
    state = {"status": "PASS", "direct_open_slot_add_capacity": 1}
    additions = [_candidate(30, "QB"), _candidate(31, "RB"), _candidate(32, "WR"),
                 _candidate(33, "TE"), _candidate(34, "DST"), _candidate(30, "QB")]
    actual = oa.legal_open_slot_candidates(ctx.roster, additions, state, _league())
    assert {row["position"] for row in actual} == {"QB", "RB", "WR", "TE"}
    assert len(actual) == 4
    assert all(row["espn_id"] not in {11} for row in actual)


def test_open_slot_capacity_and_position_limit_fail_closed():
    ctx = _ctx()
    candidates = [_candidate(30, "QB"), _candidate(31, "RB")]
    state = {"status": "PASS", "direct_open_slot_add_capacity": 1}
    assert [x["position"] for x in oa.legal_open_slot_candidates(
        ctx.roster, candidates, state, _league(qb_max=1))] == ["RB"]
    assert not oa.legal_open_slot_candidates(ctx.roster, candidates,
                                             {"status": "BLOCKED", "direct_open_slot_add_capacity": 1}, _league())
    assert not oa.legal_open_slot_candidates(ctx.roster, candidates,
                                             {"status": "PASS", "direct_open_slot_add_capacity": 0}, _league())


def test_paired_predictive_add_only_keeps_no_release(monkeypatch):
    ctx = _ctx()
    seen = []
    monkeypatch.setattr(tm, "evaluate_roster_utility", lambda roster, ignored:
                        SimpleNamespace(utility=float(len(roster))))
    monkeypatch.setattr(tm, "waiver_screen_acquisition_probability", lambda add, ignored: .4)

    def fake_mc(rows, ignored, *, mc_scenarios, stage_name, **kwargs):
        out = []
        for row in rows:
            seen.append((row["drop"], row["new_roster"], row["league_state_response"]))
            clone = dict(row)
            clone.update(stage_raw_delta=np.array([.1, .3, .4, .2]),
                         stage_adjusted_delta=np.array([.1, .3, .4, .2]),
                         stage_name=stage_name, stage_mc=mc_scenarios,
                         stage_expected_delta=.25 * row["p_acquire"],
                         stage_classification_plausible=True)
            out.append(clone)
        return None, None, None, out

    monkeypatch.setattr(tm, "_run_action_mc_stage", fake_mc)
    monkeypatch.setattr(tm, "released_player_league_state_response", lambda *a, **k:
                        pytest.fail("Add-only must never release a player"))
    report = oa.evaluate_open_slot_actions(ctx, [_candidate(21, "RB"),
                                                  _candidate(22, "WR", "WAIVERS")], _league())
    assert report["status"] == "PREDICTIVE_EVALUATED_UNCERTIFIED"
    assert report["predictive_actions_evaluated"] == 2
    assert all(r["drop_espn_id"] is None and r["release_response_applied"] is False
               and r["action_authority"] == "NONE" for r in report["actions"])
    assert all(drop["espn_id"] == 0 and release == {} and len(after) == 2
               and after[0]["espn_id"] == 11 for drop, after, release in seen)
    states = {r["fantasy_status"]: r["p_acquire"] for r in report["actions"]}
    assert states == {"FREEAGENT": 1.0, "WAIVERS": .4}


def test_direct_open_slot_absent_never_invokes_predictive_mc(monkeypatch):
    ctx = _ctx(roster=[{"espn_id": 11, "position": "QB", "lineup_slot": "QB"},
                              {"espn_id": 12, "position": "RB", "lineup_slot": "BENCH"}])
    monkeypatch.setattr(tm, "_run_action_mc_stage", lambda *a, **k:
                        pytest.fail("No open slot must avoid MC"))
    result = oa.evaluate_open_slot_actions(ctx, [_candidate(22, "WR")], _league())
    assert result["status"] == "NO_CURRENT_DIRECT_OPENING"
    assert not result["actions"]


def test_blocked_ir_incumbent_does_not_assume_free_open_slot(monkeypatch):
    roster = [{"espn_id": 11, "position": "QB", "lineup_slot": "QB"},
              {"espn_id": 12, "position": "RB", "lineup_slot": "IR", "injury_status": "ACTIVE"}]
    monkeypatch.setattr(tm, "_run_action_mc_stage", lambda *a, **k:
                        pytest.fail("Blocked IR acquisition must avoid MC"))
    report = oa.evaluate_open_slot_actions(_ctx(roster=roster), [_candidate(30, "WR")],
                                           _league())
    assert report["status"] == "BLOCKED_IR_STATE"


def test_player_receipt_open_slot_only_does_not_escalate_to_authorized_action():
    report = {"free_agent_actions": [], "waiver_actions": [],
              "open_slot_acquisitions": {"status": "PREDICTIVE_EVALUATED_UNCERTIFIED",
                  "open_active_roster_slots": 1,
                  "actions": [{"acquisition_structure": "ADD_ONLY", "add_name": "QB candidate",
                               "drop_espn_id": None, "mc_stage": "FINAL", "combined_action_classification": "ACTIONABLE_EDGE",
                               "action_authority": "NONE"}]}}
    receipt = _player_receipt(report)
    assert receipt.status == "INCOMPLETE_COVERAGE:OPEN_SLOT_ADD_ONLY_CERTIFICATION_REQUIRED"
    assert receipt.action is None
    assert receipt.evidence["open_slot_acquisitions"]["actions"][0]["drop_espn_id"] is None
