from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import src.specialist_policy_v032 as v32
from src.weekly_decision_cycle import DST, KICKER, STATUS_ACTION, _specialist_receipt


def _player(pid, name, *, position="K", mean=5.0, status=None, slot=None):
    return {
        "espn_id": pid,
        "name": name,
        "position": position,
        "nfl_team": name[:3].upper(),
        "fantasy_status": status,
        "lineup_slot": slot or position,
        "droppable": True,
        "locked": False,
        "means": {1: float(mean), 2: float(mean)},
    }


class FakeCtx:
    def __init__(self, *, position="K", waiver_mean=10.0):
        self.predictive_scenarios = 4
        self.team_id = 1
        self.week = 1
        self.seed = 17
        self.cfg = {"paired_mean_interval_resamples": 8}
        self.model = {"specialist_channels": {"mc_scenarios": 4}}
        self.league = {}
        owned = _player(1, "Owned", position=position, mean=5.0)
        opponent = _player(2, "Opp", position=position, mean=4.0)
        waiver = _player(3, "Waiver", position=position, mean=waiver_mean, status="WAIVERS", slot="BENCH")
        self.roster = [owned]
        self.all_team_rosters = {1: [owned], 2: [opponent]}
        self.actionable_available = [waiver]
        self.espn = {
            "teams": [
                {"team_id": 1, "waiver_rank": 2},
                {"team_id": 2, "waiver_rank": 1},
            ]
        }
        self.snapshot = {}
        self.opponent_predictive = np.zeros((4, 17), dtype=float)

    def ensure_predictive_opponent_reference(self):
        return None


def _install_fake_physics(monkeypatch):
    def fake_week(player, ctx, week):
        mean = float((player.get("means") or {}).get(int(week), 0.0))
        return np.full(ctx.predictive_scenarios, mean, dtype=float), mean, {
            "opponent": f"OPP{week}",
            "source": "TEST",
        }

    monkeypatch.setattr(v32, "_specialist_week_samples", fake_week)
    monkeypatch.setattr(v32, "_is_current_week_locked", lambda player, ctx: bool(player.get("locked")))
    monkeypatch.setattr(v32, "_legal_drop", lambda player: bool(player.get("droppable", True)))


def test_conditional_one_slot_waiver_claim_is_not_free_agent(monkeypatch):
    _install_fake_physics(monkeypatch)
    ctx = FakeCtx(position="K")

    result = v32.simulate_specialist_market_policy(
        ctx,
        position="K",
        user_mode="ONE_SLOT",
        pre_acquire_espn_id=3,
        pre_drop_espn_id=1,
        pre_acquire_from_waivers=True,
    )

    current = next(tx for tx in result.transactions if tx["team_id"] == 1 and tx["week"] == 1)
    assert current["action"] == "SWAP"
    assert current["add_espn_id"] == 3
    assert current["drop_espn_id"] == 1
    assert current["acquisition_state"] == "WAIVERS"
    assert current["conditional_acquisition"] is True

    # The claimed waiver player is never inserted into the guaranteed current FA
    # pool, while the dropped incumbent is released only after the current week.
    market = result.market_states[0]
    assert 3 not in market["free_agent_ids_before"]
    assert 1 not in market["free_agent_ids_before"]
    assert 1 in market["released_after_week"]
    assert 1 in market["free_agent_ids_after"]
    assert result.user_plan[0]["starter_espn_id"] == 3


def test_conditional_carry2_waiver_claim_is_supported(monkeypatch):
    _install_fake_physics(monkeypatch)
    ctx = FakeCtx(position="DST")

    result = v32.simulate_specialist_market_policy(
        ctx,
        position="DST",
        user_mode="CARRY2",
        pre_acquire_espn_id=3,
        pre_acquire_from_waivers=True,
        activation_week=1,
    )

    current = next(tx for tx in result.transactions if tx["team_id"] == 1 and tx["week"] == 1)
    assert current["action"] == "ADD"
    assert current["add_espn_id"] == 3
    assert current["drop_espn_id"] is None
    assert current["acquisition_state"] == "WAIVERS"
    assert set(result.market_states[0]["ownership_after"]["1"]) == {1, 3}


def test_kicker_policy_models_all_current_waivers_with_behavior_separate(monkeypatch):
    _install_fake_physics(monkeypatch)
    ctx = FakeCtx(position="K", waiver_mean=10.0)

    monkeypatch.setattr(v32, "_build_context", lambda *a, **k: ctx)
    monkeypatch.setattr(v32, "_evaluate_kicker_static", lambda *a, **k: {"swap_actions": []})
    monkeypatch.setattr(v32, "_static_team_weekly", lambda c, position: {
        1: np.zeros((4, 17), dtype=float),
        2: np.zeros((4, 17), dtype=float),
    })
    monkeypatch.setattr(
        v32,
        "evaluate_roster_predictive",
        lambda *a, **k: (None, None, np.zeros((4, 17), dtype=float)),
    )

    def fake_compose(base_weekly, base_opponent, c, *, d_policy, k_policy, **kwargs):
        utility = np.asarray(k_policy.team_weekly[1], dtype=float).sum(axis=1)
        return np.asarray(base_weekly), np.asarray(base_opponent), utility

    monkeypatch.setattr(v32, "_compose_state", fake_compose)
    monkeypatch.setattr(
        v32,
        "_paired_stats",
        lambda delta, c, seed_salt: {
            "mean": float(np.mean(delta)),
            "mean_p16": float(np.mean(delta)),
            "mean_p84": float(np.mean(delta)),
            "p_better": float(np.mean(np.asarray(delta) > 0)),
            "p_tie": float(np.mean(np.asarray(delta) == 0)),
            "p_worse": float(np.mean(np.asarray(delta) < 0)),
            "classification": "ACTIONABLE_EDGE" if float(np.mean(delta)) > 0 else "NO_RESOLVED_EDGE",
        },
    )
    monkeypatch.setattr(v32, "waiver_blocker_diagnostics", lambda candidate, c: [{"model": "BEHAVIOR_ONLY"}])
    monkeypatch.setattr(v32, "waiver_acquisition_probability", lambda candidate, c, blockers=None: 0.4)

    report = v32._evaluate_policy_channel({}, {}, {}, position="K")
    block = report["one_slot_policy"]

    assert block["excluded_current_waivers"] == 1
    assert block["modeled_current_waivers"] == 1
    assert block["current_waiver_one_slot_coverage_complete"] is True
    assert block["current_waiver_carry2_coverage_complete"] is True
    assert block["current_waiver_coverage_complete"] is True
    row = block["current_waiver_actions"][0]
    assert row["fantasy_status"] == "WAIVERS"
    assert row["p_acquire"] == 0.4
    assert row["conditional_complete_state_delta"]["classification"] == "ACTIONABLE_EDGE"
    assert abs(row["expected_complete_state_delta_mean"] - 0.4 * row["conditional_complete_state_delta"]["mean"]) < 1e-12
    assert block["recommended_current_action"]["action"] == "SWAP_CLAIM"


def test_weekly_receipt_remains_fail_closed_for_legacy_unmodeled_waivers():
    report = {
        "one_slot_policy": {
            "excluded_current_waivers": 2,
            "recommended_current_action": {"action": "HOLD"},
            "authoritative_current_action": False,
        }
    }
    receipt = _specialist_receipt(DST, "DST", report, "test")
    assert receipt.status == "INCOMPLETE_COVERAGE:CURRENT_SPECIALIST_WAIVERS_UNSUPPORTED"


def test_weekly_receipt_accepts_modeled_waiver_and_surfaces_carry2_action():
    report = {
        "one_slot_policy": {
            "excluded_current_waivers": 1,
            "modeled_current_waivers": 1,
            "current_waiver_coverage_complete": True,
            "current_waiver_one_slot_coverage_complete": True,
            "current_waiver_carry2_coverage_complete": True,
            "recommended_current_action": {"action": "SWAP_CLAIM", "add_espn_id": 3},
            "authoritative_current_action": True,
            "current_waiver_actions": [{"add_espn_id": 3, "p_acquire": 0.4}],
            "complete_state_delta": {"classification": "ACTIONABLE_EDGE"},
        },
        "dynamic_carry_actions": [{
            "current_activation": True,
            "classification": "CARRY2_POSSIBLE_EDGE",
            "acquisition_state": "WAIVERS",
            "p_acquire": 0.4,
            "expected_complete_state_delta_mean": 0.1,
            "complete_state_delta": {"mean": 0.25},
            "add_espn_id": 4,
        }],
        "carry2_current_recommendation": "CLAIM_SECOND_DST_NOW",
    }
    receipt = _specialist_receipt(DST, "DST", report, "test")
    assert receipt.status == STATUS_ACTION
    assert receipt.evidence["current_waiver_coverage_complete"] is True
    policies = {row["policy"] for row in receipt.action["authorized_actions"]}
    assert policies == {"ONE_SLOT", "CARRY2"}


def test_kicker_receipt_does_not_require_carry2():
    report = {
        "one_slot_policy": {
            "excluded_current_waivers": 1,
            "modeled_current_waivers": 1,
            "current_waiver_coverage_complete": True,
            "current_waiver_one_slot_coverage_complete": True,
            "current_waiver_carry2_coverage_complete": True,
            "recommended_current_action": {"action": "HOLD"},
            "authoritative_current_action": False,
            "current_waiver_actions": [{"add_espn_id": 3, "classification": "NO_WAIVER_RESOLVED_EDGE"}],
        },
        "dynamic_carry_actions": [],
    }
    receipt = _specialist_receipt(KICKER, "Kicker", report, "test")
    assert receipt.status.startswith("PASS / HOLD:")
