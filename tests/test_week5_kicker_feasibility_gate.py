"""Feasibility-first kicker repair; no empirical calibration or ESPN actions."""
from datetime import datetime, timezone
from types import SimpleNamespace
import numpy as np
import pytest

from src import specialist_policy_v032 as p
from src.weekly_decision_cycle import KICKER, _specialist_receipt


class FakeContext:
    week = 5
    team_id = 1
    seed = 7
    cfg = {}
    league = {"bye_weeks_2026": {"KC": 5, "MIN": 6, "BUF": 7}}
    snapshot = {"snapshot_utc": "2026-10-08T16:00:00+00:00"}

    def __init__(self, owned=True):
        self.roster = ([{"espn_id": 10, "name": "Bye K", "position": "K", "nfl_team": "KC",
                         "lineup_slot": "K", "droppable": True}] if owned else [])
        self.actionable_available = [
            {"espn_id": 21, "name": "K 1", "position": "K", "nfl_team": "MIN", "fantasy_status": "FREEAGENT"},
            {"espn_id": 22, "name": "K 2", "position": "K", "nfl_team": "BUF", "fantasy_status": "FREEAGENT"},
        ]

    def lock_timing(self, player, week):
        if player.get("nfl_team") == "KC":
            return SimpleNamespace(kickoff=None, source="NO_SCHEDULE")
        return SimpleNamespace(kickoff=datetime(2026, 10, 11, 17, tzinfo=timezone.utc),
                               source="NFLVERSE_SCHEDULE")


def _evaluate(monkeypatch, ctx):
    def cache(player, _ctx, _week, _cache):
        mean = {21: 6.5, 22: 7.1}[player["espn_id"]]
        return np.full(8, mean), mean, {}

    def simulation(_ctx, **kw):
        assert kw["position"] == "K"
        assert kw["pre_acquire_espn_id"] in {21, 22}
        assert kw["pre_drop_espn_id"] == 10
        return SimpleNamespace(candidate_id=kw["pre_acquire_espn_id"], transactions=[{
            "week": 5, "team_id": 1, "action": "SWAP", "add_espn_id": kw["pre_acquire_espn_id"], "drop_espn_id": 10
        }])

    def compose(*args, **kwargs):
        utility = (np.array([0.1, 0.2, 0.3]) if kwargs["k_policy"] == "hold"
                   else np.array([0.15, 0.25, 0.35]) if kwargs["k_policy"].candidate_id == 22
                   else np.array([0.22, 0.32, 0.42]))
        return None, None, utility

    monkeypatch.setattr(p, "_cache_week", cache)
    monkeypatch.setattr(p, "simulate_specialist_market_policy", simulation)
    monkeypatch.setattr(p, "_compose_state", compose)
    monkeypatch.setattr(p, "_paired_stats", lambda *a, **k: {
        "mean": float(np.mean(a[0])), "p_better": 1., "p_tie": 0., "p_worse": 0., "classification": "NO_RESOLVED_EDGE"
    })
    return p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy="dst", hold_policy="hold", dst_static={}, kicker_static={}
    )


def test_known_bye_gap_has_legal_paired_mc_repair_even_without_significance(monkeypatch):
    result = _evaluate(monkeypatch, FakeContext())
    assert result["required"] is True
    assert result["status"] == "FEASIBILITY_REPAIR_ACTION"
    assert result["candidate_id"] == 21, "MC must override the initial expected-K screen order"
    assert result["drop_id"] == 10
    assert result["eligible_feasible_frontier"] == 2
    assert result["mc_candidate_count"] == 2
    assert result["frontier_complete"] is True
    assert result["paired_complete_state_delta"]["classification"] == "NO_RESOLVED_EDGE"
    assert result["screen_is_authority"] is False


def test_existing_nonbye_kicker_preserves_optional_significance_gate():
    ctx = FakeContext()
    ctx.roster[0]["nfl_team"] = "MIN"
    result = p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy=None, hold_policy=None, dst_static={}, kicker_static={}
    )
    assert result == {"required": False, "status": "NOT_REQUIRED_K_PRESENT"}


def test_no_automatic_add_assumption_for_empty_roster():
    ctx = FakeContext(owned=False)
    result = p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy=None, hold_policy=None, dst_static={}, kicker_static={}
    )
    assert result["status"].startswith("INCOMPLETE_COVERAGE")
    assert result["reason"] == "K_ROSTER_CAPACITY_OR_DROP_STATE_UNRESOLVED"


def test_nondroppable_bye_kicker_fails_closed():
    ctx = FakeContext()
    ctx.roster[0]["droppable"] = False
    result = p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy=None, hold_policy=None, dst_static={}, kicker_static={}
    )
    assert result["reason"] == "OWNED_K_NOT_LEGALLY_DROPPABLE"


def test_unresolved_kickoff_is_not_actionable(monkeypatch):
    ctx = FakeContext()
    ctx.actionable_available = ctx.actionable_available[:1]
    ctx.lock_timing = lambda player, week: SimpleNamespace(kickoff=None, source="NO_SCHEDULE")
    result = p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy=None, hold_policy=None, dst_static={}, kicker_static={}
    )
    assert result["status"].startswith("INCOMPLETE_COVERAGE")
    assert result["excluded_unresolved_timing"] == 1


def test_waiver_only_does_not_invent_immediate_acquisition():
    ctx = FakeContext()
    for row in ctx.actionable_available:
        row["fantasy_status"] = "WAIVERS"
    result = p._required_kicker_feasibility_repair(
        ctx, base_weekly=np.zeros((3, 17)), base_opponent=np.zeros((3, 17)),
        dst_policy=None, hold_policy=None, dst_static={}, kicker_static={}
    )
    assert result["current_waiver_candidates"] == 2
    assert result["status"].startswith("INCOMPLETE_COVERAGE")


def test_weekly_receipt_requires_mandatory_repair_even_when_optional_hold():
    repair = {"required": True, "status": "FEASIBILITY_REPAIR_ACTION", "candidate_id": 22,
              "drop_id": 10, "transaction": {"action": "SWAP", "add_espn_id": 22, "drop_espn_id": 10},
              "paired_complete_state_delta": {"classification": "NO_RESOLVED_EDGE"}}
    report = {"one_slot_policy": {"recommended_current_action": {"action": "HOLD"},
                "authoritative_current_action": False}, "kicker_feasibility": repair}
    receipt = _specialist_receipt(KICKER, "K", report, "source")
    assert receipt.status == "PASS / ACTION"
    assert receipt.action["kind"] == "KICKER_FEASIBILITY_REPAIR"
    assert receipt.evidence["feasibility"]["candidate_id"] == 22


def test_weekly_receipt_fails_closed_when_required_repair_unresolved():
    report = {"one_slot_policy": {}, "kicker_feasibility": {
        "required": True, "status": "INCOMPLETE_COVERAGE:KICKER_FEASIBILITY_REPAIR",
        "reason": "OWNED_K_NOT_LEGALLY_DROPPABLE"}}
    receipt = _specialist_receipt(KICKER, "K", report, "source")
    assert receipt.status.startswith("INCOMPLETE_COVERAGE")
    assert receipt.action is None


def test_unaffected_optional_k_hold_and_dst_keep_original_classifier():
    for key in (KICKER, "dst_waiver_free_agent"):
        report = {"one_slot_policy": {"recommended_current_action": {"action": "HOLD"},
                                     "authoritative_current_action": False},
                  "kicker_feasibility": {"required": False, "status": "NOT_REQUIRED_K_PRESENT"}}
        receipt = _specialist_receipt(key, "specialist", report, "source")
        assert receipt.status.startswith("PASS / HOLD")
