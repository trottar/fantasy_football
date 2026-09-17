from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

import src.player_temporal_state_v035 as v35
import src.specialist_policy_v032 as policy
import src.specialist_temporal_v033 as temporal


def _player(pid, name, pos="RB", *, status=None, score=1.0, droppable=True):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": "TST",
        "fantasy_status": status,
        "score": float(score),
        "droppable": droppable,
        "lineup_slot": "BENCH",
    }


def _ctx(roster, available, *, week=1):
    return SimpleNamespace(
        week=int(week),
        roster=list(roster),
        actionable_available=list(available),
        cfg={"candidate_limit": 20, "candidate_floor_per_position": 2},
        league={
            "roster": {"QB": 0, "RB": 0, "WR": 0, "TE": 0},
            "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3},
        },
    )


def _install_simple_score(monkeypatch):
    def score(roster, _ctx, _start_week):
        total = sum(float(p.get("score") or 0.0) for p in roster if str(p.get("position") or "") in v35.PLAYER_POSITIONS)
        return total, total
    monkeypatch.setattr(v35, "_temporal_roster_score", score)
    monkeypatch.setattr(v35, "_candidate_expected_yield", lambda player, _ctx, _week: float(player.get("score") or 0.0))
    monkeypatch.setattr(v35, "_legal_drop", lambda p: bool(p.get("droppable", True)))

    def confirm(_roster, screens, _ctx, _week, _cache):
        if not screens:
            return None
        row = dict(screens[0])
        row.update({
            "predictive_direct_h2h_delta_mean": 1.0,
            "predictive_mean_p16": 0.5,
            "predictive_mean_p84": 1.5,
            "predictive_p_better": 1.0,
            "predictive_p_tie": 0.0,
            "predictive_p_worse": 0.0,
            "predictive_week_gain_points": 1.0,
            "predictive_classification": "ACTIONABLE_EDGE",
            "predictive_scenarios": 64,
            "transaction_model": v35.PLAYER_TRANSACTION_MODEL,
            "confirmation_model": v35.PLAYER_CONFIRMATION_MODEL,
        })
        return row
    monkeypatch.setattr(v35, "_confirm_screened_future_swaps", confirm)


def test_v035_player_sector_is_qb_rb_wr_te_only():
    assert v35.PLAYER_POSITIONS == {"QB", "RB", "WR", "TE"}


def test_v035_current_week_membership_is_observed_and_immutable(monkeypatch):
    _install_simple_score(monkeypatch)
    roster = [_player(1, "Owned", score=1.0), _player(90, "DST", pos="DST", score=99.0)]
    free = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    states = v35.build_temporal_player_states(_ctx(roster, free))
    assert states[1].transaction is None
    assert set(states[1].roster_ids()) == {1, 90}


def test_v035_future_freeagent_swap_evolves_membership_and_preserves_specialists(monkeypatch):
    _install_simple_score(monkeypatch)
    roster = [_player(1, "Owned", score=1.0), _player(90, "DST", pos="DST", score=99.0), _player(91, "K", pos="K", score=99.0)]
    free = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    states = v35.build_temporal_player_states(_ctx(roster, free))
    assert states[2].transaction["add_espn_id"] == 2
    assert states[2].transaction["drop_espn_id"] == 1
    assert set(states[2].roster_ids()) == {2, 90, 91}


def test_v035_current_waivers_are_not_fabricated_as_guaranteed_acquisitions(monkeypatch):
    _install_simple_score(monkeypatch)
    states = v35.build_temporal_player_states(
        _ctx([_player(1, "Owned", score=1.0)], [_player(2, "Waiver", status="WAIVERS", score=20.0)])
    )
    assert states[1].excluded_current_waivers == 1
    assert states[2].transaction is None


def test_v035_drop_reenters_self_market_only_next_modeled_week(monkeypatch):
    _install_simple_score(monkeypatch)
    states = v35.build_temporal_player_states(
        _ctx([_player(1, "Owned", score=1.0)], [_player(2, "Free", status="FREEAGENT", score=10.0)])
    )
    assert 1 not in states[2].free_pool
    assert 1 in states[3].free_pool


def test_v035_transaction_requires_pareto_nonworsening_week(monkeypatch):
    roster = [_player(1, "Owned", score=1.0)]
    free = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    ctx = _ctx(roster, free)
    monkeypatch.setattr(v35, "_candidate_expected_yield", lambda player, _ctx, _week: float(player.get("score") or 0.0))
    monkeypatch.setattr(v35, "_legal_drop", lambda p: True)

    def score(rows, _ctx, _week):
        ids = {p["espn_id"] for p in rows if p.get("position") in v35.PLAYER_POSITIONS}
        return (20.0, 0.0) if 2 in ids else (10.0, 5.0)

    monkeypatch.setattr(v35, "_temporal_roster_score", score)
    states = v35.build_temporal_player_states(ctx)
    assert states[2].transaction is None


def test_v035_future_candidate_screen_uses_model_yield_not_market_popularity():
    source = Path(v35.__file__).read_text(encoding="utf-8")
    assert "_candidate_expected_yield" in source
    assert "percent_owned" not in source
    assert "trending_add" not in source
    assert "trending_drop" not in source


def test_v035_no_realized_score_or_workload_selects_player_transaction():
    source = Path(v35.__file__).read_text(encoding="utf-8")
    assert "No realized score" in source or "No realized" in source
    assert "_temporal_roster_score" in source
    assert "predictive_uniforms" not in source


def test_v035_release_plan_can_use_supplied_evolved_roster_and_membership_model(monkeypatch):
    supplied = [_player(2, "Future", score=1.0)]
    ctx = SimpleNamespace(
        week=1,
        roster=[_player(1, "Current", score=1.0)],
        predictive_scenarios=2,
        league={},
        replacement_season={},
        yield_state=lambda _p, _w: SimpleNamespace(availability_probability=1.0),
        predictive_uniforms=lambda _pid: np.zeros((2, 17), dtype=float),
    )
    monkeypatch.setattr(temporal, "_legal_drop", lambda p: True)
    monkeypatch.setattr(temporal, "_active_conditional_mean", lambda p, _ctx, _w: (1.0, 1.0))
    monkeypatch.setattr(temporal, "_expected_lineup_points", lambda roster, _ctx, _w, revealed_active=None: float(len(roster)))
    monkeypatch.setattr(temporal, "_week_weights_from", lambda _ctx, _w: (np.arange(1, 18), np.ones(17), 17.0))
    plan = temporal.temporal_release_plan(
        ctx, 2, roster=supplied, membership_model=v35.PLAYER_STATE_MODEL
    )
    assert set(plan["selected_ids"]) == {2}
    assert plan["membership_model"] == v35.PLAYER_STATE_MODEL


def test_v035_local_baseline_evolves_before_activation_then_freezes_activation_state():
    def state(week, pid):
        return v35.TemporalPlayerState(
            week=week,
            roster=[_player(pid, f"P{pid}")],
            free_pool={},
            transaction=None,
            expected_remaining_ppg=0.0,
            expected_week_points=0.0,
            guaranteed_free_agents=0,
            excluded_current_waivers=0,
        )
    states = {1: state(1, 1), 2: state(2, 2), 3: state(3, 3)}
    base = np.zeros((2, 17), dtype=float)
    cache = {
        (1,): np.ones((2, 17), dtype=float),
        (2,): np.ones((2, 17), dtype=float) * 2.0,
        (3,): np.ones((2, 17), dtype=float) * 3.0,
    }
    ctx = SimpleNamespace(week=1)
    out, path = policy._temporal_player_baseline_to_activation(base, states, 3, ctx, cache)
    assert np.all(out[:, 0] == 1.0)
    assert np.all(out[:, 1] == 2.0)
    assert np.all(out[:, 2:] == 3.0)
    assert [row["week"] for row in path] == [1, 2, 3]


def test_v035_specialist_complete_state_expands_about_local_player_state():
    source = Path(policy.__file__).read_text(encoding="utf-8")
    assert "u_local_base" in source
    assert "delta = np.asarray(ub) - np.asarray(u_local_base)" in source
    assert "STATE_COMPOSITION_ORDER" in source
    assert '"policy_layer": "SPECIALIST_WITH_CAUSAL_PLAYER_STATE_V035"' in source


def test_v035_external_player_market_is_explicitly_first_order():
    assert v35.EXTERNAL_PLAYER_MARKET_MODEL == "FROZEN_CURRENT_GUARANTEED_FREEAGENT_POOL_NO_EXTERNAL_CLAIMS_V035"
    source = Path(policy.__file__).read_text(encoding="utf-8")
    assert "bounded order-2+ external player-channel release cascade" in source


def test_v035_current_release_response_still_preserves_commissioned_fixed6_path():
    source = Path(policy.__file__).read_text(encoding="utf-8")
    assert "released_player_league_state_response" in source
    assert "COMMISSIONED_CURRENT_STATE_RELEASE_RESPONSE_V031" in source
    assert "if int(effective_activation_week) == int(ctx.week)" in source


def test_v035_capture_freezes_temporal_player_state_without_changing_v034_measurement_contract():
    source = Path("src/prospective_measurement_v034.py").read_text(encoding="utf-8")
    assert 'MEASUREMENT_MODEL_VERSION = "0.36"' in source
    assert 'MEASUREMENT_CONTRACT = "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034"' in source
    assert 'capture["temporal_player_state_prediction"]' in source
    assert '"2026_game_outcomes_used_for_tuning": False' in source


def test_v035_cli_exposes_player_state_provenance_and_remains_cp1252_safe(capsys):
    from fantasy import _print_specialist_channel
    report = {
        "week": 1, "channel": "DEFENSE", "team_name": "Us", "position": "DST", "mc_scenarios": 64,
        "owned": [{"name": "Owned D/ST", "team": "DET"}],
        "baseline": {"weighted_mean_ppg": 5.0, "current_week_mean": 5.0, "current_week_sd": 2.0, "current_week_choice": "Owned D/ST"},
        "swap_actions": [], "one_slot_policy": {}, "carry2_current_recommendation": "HOLD_ONE_DST_NOW",
        "dynamic_carry_actions": [{
            "activation_week": 7, "effective_player_release_week": 7, "current_activation": False,
            "add_name": "Future D/ST", "add_team": "TEN", "dynamic_channel_delta_ppg": 0.1,
            "classification": "NO_CARRY2_RESOLVED_EDGE", "one_slot_policy_ppg": 5.8, "two_slot_policy_ppg": 5.9,
            "player_slot_release": {"name": "P", "position": "RB", "selection_probability": 1.0, "selection_distribution": [{"name": "P", "selection_probability": 1.0}]},
            "player_membership_model": v35.PLAYER_STATE_MODEL,
            "external_player_market_model": v35.EXTERNAL_PLAYER_MARKET_MODEL,
            "player_state_at_release": {"week": 7},
            "player_state_path": [{"week": 1, "transaction": None}, {"week": 4, "transaction": {"week": 4, "add": "A", "drop": "B"}}],
            "complete_state_confirmed": True,
            "complete_state_delta": {"mean": 0.0, "mean_p16": 0.0, "mean_p84": 0.0, "p_better": 0.0, "p_tie": 1.0, "p_worse": 0.0},
            "release_response": {"p_claimed": 0.5, "field_shift_ppg": 0.0, "current_opponent_shift_ppg": 0.0, "timing_proxy": "RECOMPUTED_AT_ACTIVATION_STATE_V033"},
        }],
    }
    _print_specialist_channel(report)
    out = capsys.readouterr().out
    assert f"player state: {v35.PLAYER_STATE_MODEL}" in out
    assert "modeled prior swaps=1" in out
    assert "latest player-state move: W4 ADD A / DROP B" in out
    out.encode("cp1252")


def test_v035_release_metadata():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.36"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.36")
    assert (root / "DATA_SOURCES.md").read_text(encoding="utf-8").startswith("# Data-source contract — v0.36")


def test_v035_full_release_is_standalone_source_tree_without_bootstrap_dependency():
    root = Path(__file__).parents[1]
    assert (root / "src" / "player_temporal_state_v035.py").exists()
    assert not (root / "materialize_v034.py").exists()
    assert not (root / "_v034_core.py").exists()
    assert not (root / ".v034_materialized").exists()


def test_v035_fixed1_screen_alone_cannot_change_future_membership(monkeypatch):
    roster = [_player(1, "Owned", score=1.0)]
    free = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    ctx = _ctx(roster, free)
    monkeypatch.setattr(v35, "_candidate_expected_yield", lambda player, _ctx, _week: float(player.get("score") or 0.0))
    monkeypatch.setattr(v35, "_legal_drop", lambda p: True)
    monkeypatch.setattr(
        v35,
        "_temporal_roster_score",
        lambda rows, _ctx, _week: (
            sum(float(p.get("score") or 0.0) for p in rows if p.get("position") in v35.PLAYER_POSITIONS),
            sum(float(p.get("score") or 0.0) for p in rows if p.get("position") in v35.PLAYER_POSITIONS),
        ),
    )
    monkeypatch.setattr(v35, "_confirm_screened_future_swaps", lambda *_args, **_kwargs: None)
    states = v35.build_temporal_player_states(ctx)
    assert states[2].transaction is None
    assert states[2].ordinary_roster_ids() == (1,)


def test_v035_fixed1_predictive_confirmation_rejects_unresolved_screen(monkeypatch):
    roster = [_player(1, "Owned", score=1.0)]
    trial = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    screens = [{
        "action": "SWAP",
        "week": 2,
        "add_espn_id": 2,
        "add": "Free",
        "add_position": "RB",
        "drop_espn_id": 1,
        "drop": "Owned",
        "drop_position": "RB",
        "screen_expected_remaining_gain_ppg": 9.0,
        "screen_expected_week_gain_points": 9.0,
        "candidate_expected_yield_ppg": 10.0,
        "screen_model": v35.PLAYER_SCREEN_MODEL,
        "_new_roster": trial,
    }]
    ctx = SimpleNamespace(
        seed=7,
        cfg={"paired_mean_interval_resamples": 100, "actionable_p_better": 0.9, "lean_p_better": 0.67},
    )
    cache = {}
    monkeypatch.setattr(
        v35,
        "_prepare_predictive_confirmation",
        lambda _ctx, c: c.update({"_prepared": True, "_scenarios": 64, "_opponent": np.zeros((64, 17))}),
    )
    monkeypatch.setattr(v35, "_predictive_weekly_cached", lambda _rows, _ctx, _cache: np.ones((64, 17)))
    monkeypatch.setattr(v35, "_future_h2h_utility", lambda _weekly, _opponent, _ctx, _week: np.zeros(64))
    out = v35._confirm_screened_future_swaps(roster, screens, ctx, 2, cache)
    assert out is None


def test_v035_fixed1_predictive_confirmation_accepts_resolved_crn_edge(monkeypatch):
    roster = [_player(1, "Owned", score=1.0)]
    trial = [_player(2, "Free", status="FREEAGENT", score=10.0)]
    screens = [{
        "action": "SWAP",
        "week": 2,
        "add_espn_id": 2,
        "add": "Free",
        "add_position": "RB",
        "drop_espn_id": 1,
        "drop": "Owned",
        "drop_position": "RB",
        "screen_expected_remaining_gain_ppg": 9.0,
        "screen_expected_week_gain_points": 9.0,
        "candidate_expected_yield_ppg": 10.0,
        "screen_model": v35.PLAYER_SCREEN_MODEL,
        "_new_roster": trial,
    }]
    ctx = SimpleNamespace(
        seed=7,
        cfg={"paired_mean_interval_resamples": 100, "actionable_p_better": 0.9, "lean_p_better": 0.67},
    )
    cache = {}
    monkeypatch.setattr(
        v35,
        "_prepare_predictive_confirmation",
        lambda _ctx, c: c.update({"_prepared": True, "_scenarios": 64, "_opponent": np.zeros((64, 17))}),
    )

    def weekly(rows, _ctx, _cache):
        ids = {p["espn_id"] for p in rows}
        return np.full((64, 17), 2.0 if 2 in ids else 0.0)

    monkeypatch.setattr(v35, "_predictive_weekly_cached", weekly)
    monkeypatch.setattr(
        v35,
        "_future_h2h_utility",
        lambda weekly_arr, _opponent, _ctx, _week: np.ones(64) if float(np.mean(weekly_arr)) > 1.0 else np.zeros(64),
    )
    out = v35._confirm_screened_future_swaps(roster, screens, ctx, 2, cache)
    assert out is not None
    assert out["predictive_classification"] == "ACTIONABLE_EDGE"
    assert out["predictive_p_better"] == 1.0
    assert out["confirmation_model"] == v35.PLAYER_CONFIRMATION_MODEL


def test_v035_fixed1_transaction_provenance_separates_screen_and_authority():
    assert v35.PLAYER_SCREEN_MODEL == "EXPECTED_LINEUP_PARETO_SCREEN_ONLY_V035_FIXED1"
    assert v35.PLAYER_CONFIRMATION_MODEL == "DIRECT_PLAYER_CHANNEL_PAIRED_H2H_CRN_V035_FIXED1"
    assert v35.PLAYER_TRANSACTION_MODEL == "SCREENED_PAIRED_PREDICTIVE_CRN_BEST_RESPONSE_V035_FIXED1"
