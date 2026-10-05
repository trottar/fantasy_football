from __future__ import annotations

import copy
from types import SimpleNamespace

import numpy as np
import pytest

from src import specialist_trade as st


def p(pid, pos, *, status="ROSTERED", points=10.0, droppable=True):
    return {
        "espn_id": pid,
        "name": f"{pos}-{pid}",
        "position": pos,
        "fantasy_status": status,
        "season_ppg": points,
        "season_projection": points * 17,
        "weekly_projection": points,
        "droppable": droppable,
        "lineup_locked": False,
    }


def league():
    return {
        "roster": {"QB": 1, "RB": 1, "WR": 1, "TE": 1, "K": 1, "DST": 1, "BENCH": 2},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
    }


def base_roster(offset=0):
    return [
        p(offset + 1, "QB", points=20),
        p(offset + 2, "RB", points=15),
        p(offset + 3, "WR", points=14),
        p(offset + 4, "TE", points=10),
        p(offset + 5, "K", points=8),
        p(offset + 6, "DST", points=7),
        p(offset + 7, "RB", points=8),
        p(offset + 8, "WR", points=7),
    ]


class FakeCtx:
    def __init__(self, available=()):
        self.actionable_available = list(available)


def test_mixed_capacity_can_drop_specialist_only_at_complete_roster_boundary(monkeypatch):
    roster = base_roster()
    incoming = [p(101, "RB", points=18), p(102, "WR", points=17)]
    # One outgoing, two incoming => one automatic release.  Force complete-roster
    # utility to prefer dropping the existing K while keeping the roster legal by
    # using a second K on the original roster.
    roster.append(p(9, "K", points=1))
    ctx = FakeCtx()
    monkeypatch.setattr(
        st,
        "evaluate_roster_utility",
        lambda rows, _ctx: SimpleNamespace(
            season_expected_lineup_ppg=sum(x["season_ppg"] for x in rows),
            bench_insurance_ppg=0.0,
        ),
    )
    after, drops, fills = st.apply_specialist_trade_package(
        roster, [7], incoming, league=league(), ctx=ctx
    )
    assert len(after) == len(roster)
    assert len(drops) == 1
    assert st._position(drops[0]) in {"K", "RB", "WR", "QB", "TE", "DST"}
    assert fills == []
    assert st.roster_is_legal(after, league(), target_size=len(roster))


def test_open_slot_requires_same_channel_specialist_freeagent_fill(monkeypatch):
    roster = base_roster()
    # Trade away K + RB for one WR, creating an open slot and a K minimum deficit.
    incoming = [p(201, "WR", points=16)]
    free_k = p(900, "K", status="FREEAGENT", points=9)
    waiver_k = p(901, "K", status="WAIVERS", points=20)
    free_rb = p(902, "RB", status="FREEAGENT", points=30)
    ctx = FakeCtx([free_k, waiver_k, free_rb])
    monkeypatch.setattr(
        st,
        "evaluate_roster_utility",
        lambda rows, _ctx: SimpleNamespace(
            season_expected_lineup_ppg=sum(x["season_ppg"] for x in rows),
            bench_insurance_ppg=0.0,
        ),
    )
    after, drops, fills = st.apply_specialist_trade_package(
        roster, [2, 5], incoming, league=league(), ctx=ctx
    )
    assert drops == []
    assert any(x["espn_id"] == 900 for x in fills)
    assert all(x["espn_id"] != 901 for x in fills)
    assert st.roster_is_legal(after, league(), target_size=len(roster))


def test_fixed_policy_keeps_same_channel_team_weekly():
    ctx = SimpleNamespace(
        team_id=1,
        roster=[p(5, "K")],
    )
    static = {
        1: np.ones((4, 17)),
        2: np.full((4, 17), 2.0),
    }
    policy = st._fixed_ownership_policy("K", static, ctx)
    assert policy.mode == "TRADE_FIXED_OWNERSHIP_V001"
    assert policy.user_capacity == 1
    assert np.array_equal(policy.user_weekly, static[1])
    assert np.array_equal(policy.team_weekly[2], static[2])


def test_player_only_package_is_rejected_by_specialist_authority(monkeypatch):
    snap = {
        "espn": {
            "teams": [
                {"team_id": 1, "name": "Us", "roster": base_roster()},
                {"team_id": 2, "name": "Them", "roster": base_roster(100)},
            ]
        }
    }
    monkeypatch.setattr(
        st,
        "_context",
        lambda snapshot, league, model, values_path, team_id, scenarios:
            SimpleNamespace(
                team_id=team_id,
                roster=copy.deepcopy(base_roster(0 if team_id == 1 else 100)),
                actionable_available=[],
            ),
    )
    with pytest.raises(ValueError, match="specialist trade authority"):
        st.evaluate_specialist_trade(
            snap,
            league(),
            {"market_manager": {"trade_max_players_per_side": 2}},
            values_path="unused.csv",
            user_team={"team_id": 1, "name": "Us"},
            partner_team_id=2,
            give_ids=[2],
            receive_ids=[102],
            mc_scenarios=4,
        )


def test_balanced_screen_frontier_preserves_dst_and_k_when_available():
    rows = [
        {"partner_team_id": 2, "give_ids": [1], "receive_ids": [2], "package_family": "1x1", "specialist_channels": "DST", "screen_score": 10},
        {"partner_team_id": 2, "give_ids": [3], "receive_ids": [4], "package_family": "1x1", "specialist_channels": "K", "screen_score": 9},
        {"partner_team_id": 3, "give_ids": [5], "receive_ids": [6, 7], "package_family": "1x2", "specialist_channels": "DST", "screen_score": 8},
        {"partner_team_id": 3, "give_ids": [8, 9], "receive_ids": [10], "package_family": "2x1", "specialist_channels": "K", "screen_score": 7},
    ]
    frontier = st._balanced_frontier(rows, limit=4)
    assert {row["specialist_channels"] for row in frontier} == {"DST", "K"}
    assert {row["package_family"] for row in frontier} >= {"1x1", "1x2", "2x1"}



def test_equal_count_mixed_trade_can_release_and_replace_to_restore_specialist_minimum(monkeypatch):
    roster = base_roster()
    incoming = [p(301, "WR", points=16)]
    free_k = p(903, "K", status="FREEAGENT", points=9)
    ctx = FakeCtx([free_k])
    monkeypatch.setattr(
        st,
        "evaluate_roster_utility",
        lambda rows, _ctx: SimpleNamespace(
            season_expected_lineup_ppg=sum(x["season_ppg"] for x in rows),
            bench_insurance_ppg=0.0,
        ),
    )
    # K-for-WR is equal count but removes the only K. The legal state must make
    # one additional release and fill K from guaranteed free agency.
    after, drops, fills = st.apply_specialist_trade_package(
        roster, [5], incoming, league=league(), ctx=ctx
    )
    assert len(after) == len(roster)
    assert len(drops) == 1
    assert [x["espn_id"] for x in fills] == [903]
    assert st.roster_is_legal(after, league(), target_size=len(roster))


def test_specialist_weekly_receipt_is_separate_from_player_trade_receipts():
    from src.weekly_decision_cycle import TRADE_SPECIALIST, _specialist_trade_receipt

    receipt = _specialist_trade_receipt([
        {
            "package_family": "1x2",
            "specialist_channels": "DST",
            "classification": "ACTIONABLE_OFFER",
            "screen_authority": False,
        },
        {
            "package_family": "2x1",
            "specialist_channels": "K",
            "classification": "NO_RESOLVED_EDGE",
            "screen_authority": False,
        },
    ])
    assert receipt.key == TRADE_SPECIALIST
    assert receipt.status == "PASS / ACTION"
    assert receipt.authority == "specialist_trade.search_specialist_trades"
    assert receipt.evidence["evaluated_by_family"]["1x2"] == 1
    assert set(receipt.evidence["specialist_channels"]) == {"DST", "K"}
    assert receipt.evidence["screen_authority"] is False

def test_specialist_trade_policy_guard_rejects_user_multi_k_state():
    roster = base_roster() + [p(9, "K", points=9)]
    with pytest.raises(
        ValueError,
        match="user specialist-trade state requires unsupported multi-K ownership",
    ):
        st._assert_supported_trade_specialist_state(roster, side="user")


def test_specialist_trade_policy_guard_rejects_partner_multi_k_state():
    roster = base_roster(100) + [p(109, "K", points=9)]
    with pytest.raises(
        ValueError,
        match="partner specialist-trade state requires unsupported multi-K ownership",
    ):
        st._assert_supported_trade_specialist_state(roster, side="partner")


def test_specialist_trade_policy_guard_preserves_multi_dst_state():
    roster = base_roster() + [p(9, "DST", points=9)]
    st._assert_supported_trade_specialist_state(roster, side="user")
    assert sum(1 for row in roster if st._position(row) == "DST") == 2
    assert sum(1 for row in roster if st._position(row) == "K") == 1


def test_specialist_trade_multi_k_guard_is_after_legal_normalization():
    source = open(st.__file__, encoding="utf-8").read()
    user_legal = (
        'if not roster_is_legal(user_after, league, target_size=len(user_ctx.roster)):'
    )
    partner_legal = (
        'if not roster_is_legal(partner_after, league, target_size=len(partner_ctx.roster)):'
    )
    user_guard = '_assert_supported_trade_specialist_state(user_after, side="user")'
    partner_guard = (
        '_assert_supported_trade_specialist_state(partner_after, side="partner")'
    )
    assert source.index(user_legal) < source.index(partner_legal)
    assert source.index(partner_legal) < source.index(user_guard)
    assert source.index(user_guard) < source.index(partner_guard)

def test_specialist_trade_review_window_defers_current_week_state(monkeypatch):
    snap = {
        "snapshot_utc": "2026-10-05T01:26:55.901034+00:00",
        "espn": {
            "season": 2026,
            "week": 4,
            "transaction_settings": {
                "trade_review_hours": 48,
                "trade_veto_votes_required": 4,
                "trade_deadline_date": 1796371200000,
                "trade_max": -1,
                "lineup_locktime_type": "INDIVIDUAL_GAME",
                "roster_locktime_type": "INDIVIDUAL_GAME",
                "transaction_locking_enabled": False,
            },
            "teams": [
                {"team_id": 1, "name": "Us", "roster": base_roster()},
                {"team_id": 2, "name": "Them", "roster": base_roster(100)},
            ],
        },
    }

    class Ctx:
        def __init__(self, team_id, roster):
            self.team_id = team_id
            self.roster = copy.deepcopy(roster)
            self.actionable_available = []
            self.week = 4
            self.seed = 19
            self.league = league()
            self.model = {"market_manager": {}}

    contexts = {
        1: Ctx(1, base_roster()),
        2: Ctx(2, base_roster(100)),
    }
    monkeypatch.setattr(
        st, "_context",
        lambda snapshot, league, model, values_path, team_id, scenarios:
            contexts[int(team_id)],
    )
    monkeypatch.setattr(
        st,
        "apply_specialist_trade_package",
        lambda roster, outgoing_ids, incoming, **kwargs: (
            [dict(p) for p in roster if st._pid(p) not in set(outgoing_ids)]
            + [dict(p) for p in incoming],
            [],
            [],
        ),
    )
    monkeypatch.setattr(st, "perceived_market_value", lambda *args, **kwargs: 0.0)

    baseline = np.ones((4, 17))
    immediate = np.full((4, 17), 2.0)
    base_utility = np.full(4, 1.0)
    immediate_utility = np.full(4, 2.0)
    opponent = np.ones((4, 17))

    def fake_baseline(snapshot, league, model, values_path, team_id, scenarios, **kwargs):
        return contexts[int(team_id)], base_utility.copy(), baseline.copy(), opponent.copy()

    def fake_after(hybrid_snapshot, final_snapshot, league, model, values_path, team_id, scenarios, **kwargs):
        return contexts[int(team_id)], immediate_utility.copy(), immediate.copy(), opponent.copy()

    monkeypatch.setattr(st, "_baseline_state", fake_baseline)
    monkeypatch.setattr(st, "_composed_after_state", fake_after)
    monkeypatch.setattr(
        st,
        "_scenario_h2h_utility_against",
        lambda weekly, opponent, ctx: np.mean(weekly, axis=1),
    )

    report = st.evaluate_specialist_trade(
        snap,
        league(),
        {"market_manager": {"trade_max_players_per_side": 2}},
        values_path="unused.csv",
        user_team={"team_id": 1, "name": "Us"},
        partner_team_id=2,
        give_ids=[6],
        receive_ids=[106],
        mc_scenarios=4,
    )
    assert report["trade_timing"]["effective_week"] == 5
    assert report["trade_timing"]["current_week_effective"] is False
    assert report["user"]["delta_current_week"]["mean"] == 0.0
    assert report["partner"]["delta_current_week"]["mean"] == 0.0
    assert report["user"]["delta_season_ppg"]["mean"] > 0.0
