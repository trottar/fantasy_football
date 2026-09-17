from __future__ import annotations

from pathlib import Path

import numpy as np

import src.specialist_policy_v032 as v32


def player(pid, name, mean1=5.0, mean2=None, *, status=None, locked=False, slot="DST"):
    return {
        "espn_id": pid,
        "name": name,
        "position": "DST",
        "nfl_team": name[:3].upper(),
        "fantasy_status": status,
        "lineup_slot": slot,
        "locked": locked,
        "means": {1: float(mean1), 2: float(mean1 if mean2 is None else mean2)},
    }


class FakeCtx:
    def __init__(self, user, opponent, available):
        self.predictive_scenarios = 4
        self.team_id = 1
        self.week = 1
        self.roster = list(user)
        self.all_team_rosters = {1: list(user), 2: list(opponent)}
        self.actionable_available = list(available)
        self.espn = {
            "teams": [
                {"team_id": 1, "waiver_rank": 2},
                {"team_id": 2, "waiver_rank": 1},
            ]
        }
        self.snapshot = {}


def install_fake_physics(monkeypatch, samples=None):
    samples = samples or {}
    def fake_week(p, ctx, week):
        mean = float((p.get("means") or {}).get(int(week), (p.get("means") or {}).get(1, 0.0)))
        arr = np.asarray(samples.get((int(p["espn_id"]), int(week)), [mean] * ctx.predictive_scenarios), dtype=float)
        return arr, mean, {"opponent": f"OPP{week}", "source": "TEST_PRELOCK_MEAN"}
    monkeypatch.setattr(v32, "_specialist_week_samples", fake_week)
    monkeypatch.setattr(v32, "_is_current_week_locked", lambda p, ctx: bool(p.get("locked")))
    monkeypatch.setattr(v32, "_legal_drop", lambda p: bool(p.get("droppable", True)))


def test_v032_one_slot_streams_only_for_strict_pregame_improvement(monkeypatch):
    install_fake_physics(monkeypatch)
    a = player(1, "Owned", 5, 9)
    b = player(2, "Free", 8, 8, status="FREEAGENT", slot="BENCH")
    c = player(3, "Opp", 4, 4)
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    tx = [t for t in result.transactions if t["team_id"] == 1 and t["week"] == 1]
    assert tx and tx[0]["add_espn_id"] == 2 and tx[0]["drop_espn_id"] == 1
    assert result.user_plan[0]["starter_espn_id"] == 2


def test_v032_no_hindsight_uses_mean_not_realized_score(monkeypatch):
    a = player(1, "Owned", 8)
    b = player(2, "Free", 7, status="FREEAGENT", slot="BENCH")
    c = player(3, "Opp", 1)
    install_fake_physics(monkeypatch, {(1, 1): [0, 0, 0, 0], (2, 1): [100, 100, 100, 100]})
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    assert result.user_plan[0]["starter_espn_id"] == 1
    np.testing.assert_array_equal(result.team_weekly[1][:, 0], np.zeros(4))


def test_v032_released_specialist_cannot_be_claimed_until_next_week(monkeypatch):
    install_fake_physics(monkeypatch)
    a = player(1, "Owned", 5, 7)
    b = player(2, "Free", 9, 9, status="FREEAGENT", slot="BENCH")
    c = player(3, "Opp", 1, 1)
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    opp_w1 = [t for t in result.transactions if t["team_id"] == 2 and t["week"] == 1]
    opp_w2 = [t for t in result.transactions if t["team_id"] == 2 and t["week"] == 2]
    assert not opp_w1
    assert opp_w2 and opp_w2[0]["add_espn_id"] == 1


def test_v032_current_waivers_are_not_fabricated_as_guaranteed_freeagents(monkeypatch):
    install_fake_physics(monkeypatch)
    a = player(1, "Owned", 5)
    b = player(2, "WaiverStar", 20, status="WAIVERS", slot="BENCH")
    c = player(3, "Opp", 1)
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    assert result.guaranteed_free_agents_initial == 0
    assert result.excluded_current_waivers == 1
    assert result.user_plan[0]["starter_espn_id"] == 1


def test_v032_locked_current_specialist_is_immutable(monkeypatch):
    install_fake_physics(monkeypatch)
    a = player(1, "Owned", 5, locked=True)
    b = player(2, "Free", 20, status="FREEAGENT", slot="BENCH")
    c = player(3, "Opp", 1)
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="ONE_SLOT")
    assert result.user_plan[0]["starter_espn_id"] == 1
    assert not [t for t in result.transactions if t["team_id"] == 1 and t["week"] == 1]


def test_v032_carry2_preacquisition_removes_candidate_from_market_and_uses_pregame_starter(monkeypatch):
    install_fake_physics(monkeypatch)
    a = player(1, "Owned", 5)
    b = player(2, "Carry", 9, status="FREEAGENT", slot="BENCH")
    c = player(3, "Opp", 1)
    ctx = FakeCtx([a], [c], [b])
    result = v32.simulate_specialist_market_policy(ctx, position="DST", user_mode="CARRY2", pre_acquire_espn_id=2)
    assert result.user_plan[0]["starter_espn_id"] == 2
    assert not [t for t in result.transactions if t["team_id"] == 2 and t.get("add_espn_id") == 2]


def test_v032_field_delta_uses_actual_opponent_current_week_then_field_mean(monkeypatch):
    ctx = FakeCtx([player(1, "U")], [player(2, "O")], [])
    ctx.all_team_rosters[3] = [player(3, "X")]
    static = {1: np.zeros((4, 17)), 2: np.zeros((4, 17)), 3: np.zeros((4, 17))}
    p2 = np.full((4, 17), 2.0)
    p3 = np.full((4, 17), 10.0)
    policy = v32.SpecialistPolicyResult(
        position="DST", mode="ONE_SLOT", user_capacity=1,
        team_weekly={1: np.zeros((4,17)), 2: p2, 3: p3, -1: np.zeros((4,17))},
        user_plan=[], transactions=[], guaranteed_free_agents_initial=0, excluded_current_waivers=0,
    )
    monkeypatch.setattr(v32, "find_week_opponent", lambda snapshot, team_id: 2)
    delta = v32._field_delta(policy, static, ctx)
    np.testing.assert_array_equal(delta[:, 0], np.full(4, 2.0))
    np.testing.assert_array_equal(delta[:, 1], np.full(4, 6.0))


def test_v032_release_metadata_and_gui_policy_wiring():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.36"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.36")
    app = (root / "src" / "gui" / "season_app.py").read_text(encoding="utf-8")
    service = (root / "src" / "gui" / "season_service.py").read_text(encoding="utf-8")
    assert "L2 dynamic one-slot policy" in app
    assert "L3/L4 dynamic second-DST activation + complete-state confirmation" in app
    assert "specialist_policy_v032" in service


def test_v032_specialist_cli_remains_cp1252_safe(capsys):
    from fantasy import _print_specialist_channel
    report = {
        "week": 1, "channel": "DEFENSE", "team_name": "Us", "position": "DST", "mc_scenarios": 64,
        "owned": [{"name": "Owned", "team": "DET"}],
        "baseline": {"weighted_mean_ppg": 5.0, "current_week_mean": 5.0, "current_week_sd": 2.0, "current_week_choice": "Owned"},
        "swap_actions": [{"action":"SWAP","add_name":"Free","add_team":"NO","drop_name":"Owned","fantasy_status":"FREEAGENT","delta_channel_ppg":0.1,"p_channel_better":0.6,"current_week_delta":0.2,"classification":"CHANNEL_UPGRADE"}],
        "one_slot_policy": {"weighted_mean_ppg":5.2,"delta_vs_static_ppg":0.2,"current_action":{"action":"SWAP","add":"Free","drop":"Owned"},"complete_state_delta":{"mean":0.001,"mean_p16":0.0,"mean_p84":0.002,"p_better":0.6,"p_tie":0.0,"p_worse":0.4,"classification":"POSSIBLE_EDGE"},"market_model":v32.POLICY_MODEL,"transaction_order_model":v32.ORDER_MODEL,"guaranteed_free_agents_initial":1,"excluded_current_waivers":0,"weekly_plan":[]},
        "dynamic_carry_actions": [],
    }
    _print_specialist_channel(report)
    out = capsys.readouterr().out
    out.encode("cp1252")
    assert all(ord(ch) < 128 for ch in out)
    assert "L2 DYNAMIC ONE-SLOT POLICY" in out
    assert "=== SAME-CHANNEL STATIC SWAPS ===" in out
