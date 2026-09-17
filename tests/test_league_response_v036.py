from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

import src.league_response_v036 as v36


def _p(pid: int, name: str, pos: str = "RB"):
    return {"espn_id": pid, "name": name, "position": pos}


def _ctx(**overrides):
    cfg = {
        "league_response_cascade_max_depth": 3,
        "league_response_cascade_branch_probability_floor": 0.01,
        "league_response_cascade_field_shift_floor_ppg": 0.0,
        "league_response_cascade_seed_branches": 3,
        "league_response_cascade_claimant_frontier": 4,
        "league_response_cascade_max_branches_per_order": 8,
        "league_response_cascade_scenarios": 64,
    }
    cfg.update(overrides.pop("cfg", {}))
    rosters = {
        1: [_p(10, "User")],
        2: [_p(2, "B")],
        3: [_p(3, "C")],
        4: [_p(4, "D")],
    }
    ctx = SimpleNamespace(
        cfg=cfg,
        team_id=1,
        week=1,
        all_team_rosters=rosters,
        espn={
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": 4},
                {"team_id": 2, "name": "T2", "waiver_rank": 1},
                {"team_id": 3, "name": "T3", "waiver_rank": 2},
                {"team_id": 4, "name": "T4", "waiver_rank": 3},
            ],
            "available_players": [],
        },
        league={"week_weights": [1.0] * 17},
        replacement_current={"QB": 0, "RB": 0, "WR": 0, "TE": 0},
        replacement_season={"QB": 0, "RB": 0, "WR": 0, "TE": 0},
    )
    ctx.__dict__.update(overrides)
    return ctx


def _first(candidate_shift=0.03, winner=0.5):
    shift = [candidate_shift] * 17
    return {
        "model": "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V031_FIRST_ORDER",
        "scenarios": 256,
        "p_claimed": winner,
        "p_unclaimed": 1.0 - winner,
        "field_shift_ppg": candidate_shift,
        "current_opponent_shift_ppg": 0.01,
        "opponent_reference_shift_ppg_by_week": shift,
        "destinations": [
            {"team_id": 2, "winner_probability": winner, "best_drop_espn_id": 2, "best_drop_name": "B"}
        ],
    }


def _fake_claimants(candidate, rosters, ctx, *, start_week, scenarios, exclude_team_ids, frontier):
    pid = candidate["espn_id"]
    if pid == 2:
        row = {
            "team_id": 3, "team_name": "T3", "waiver_rank": 2,
            "winner_probability": 0.5, "claim_probability": 0.5,
            "drop_espn_id": 3, "drop_name": "C", "delta_season_ppg": 1.0,
            "delta_weekly_mean": np.array([0.0] * (start_week - 1) + [0.12] * (18 - start_week)),
        }
        return [row], 0.0
    if pid == 3:
        row = {
            "team_id": 4, "team_name": "T4", "waiver_rank": 3,
            "winner_probability": 0.5, "claim_probability": 0.5,
            "drop_espn_id": 4, "drop_name": "D", "delta_season_ppg": 0.5,
            "delta_weekly_mean": np.array([0.0] * (start_week - 1) + [0.06] * (18 - start_week)),
        }
        return [row], 0.0
    return [], 0.0


def test_v036_preserves_commissioned_order1_contract(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", lambda *a, **k: ([], 0.0))
    first = _first()
    out = v36.extend_release_response(_p(1, "A"), _ctx(), first, start_week=1)
    assert out["first_order_model"] == first["model"]
    assert out["first_order_field_shift_ppg"] == first["field_shift_ppg"]
    assert out["p_claimed"] == first["p_claimed"]
    assert out["current_opponent_shift_ppg"] == first["current_opponent_shift_ppg"]


def test_v036_order2_probability_is_parent_times_local_winner(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    out = v36.extend_release_response(_p(1, "A"), _ctx(), _first(winner=0.5), start_week=1)
    row = next(r for r in out["cascade_destinations"] if r["order"] == 2)
    assert abs(row["branch_probability"] - 0.25) < 1e-12


def test_v036_order3_starts_one_week_after_order2_release(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    out = v36.extend_release_response(_p(1, "A"), _ctx(), _first(), start_week=1)
    rows = out["cascade_destinations"]
    assert {r["order"]: r["release_week"] for r in rows} == {2: 2, 3: 3}


def test_v036_hard_max_depth_stops_order3(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    ctx = _ctx(cfg={"league_response_cascade_max_depth": 2})
    out = v36.extend_release_response(_p(1, "A"), ctx, _first(), start_week=1)
    assert {r["order"] for r in out["cascade_destinations"]} == {2}


def test_v036_branch_probability_floor_prunes_seed(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    ctx = _ctx(cfg={"league_response_cascade_branch_probability_floor": 0.6})
    out = v36.extend_release_response(_p(1, "A"), ctx, _first(winner=0.5), start_week=1)
    assert out["cascade_destinations"] == []
    assert out["cascade_pruned_probability_mass"] >= 0.5


def test_v036_incremental_field_floor_stops_next_order(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    ctx = _ctx(cfg={"league_response_cascade_field_shift_floor_ppg": 10.0})
    out = v36.extend_release_response(_p(1, "A"), ctx, _first(), start_week=1)
    assert {r["order"] for r in out["cascade_destinations"]} == {2}
    assert "INCREMENTAL_FIELD_SHIFT_FLOOR" in out["cascade_stop_reasons"]


def test_v036_cycle_guard_prevents_reintroducing_path_player(monkeypatch):
    def cyc(candidate, rosters, ctx, **kwargs):
        return [{
            "team_id": 3, "team_name": "T3", "waiver_rank": 2,
            "winner_probability": 0.5, "claim_probability": 0.5,
            "drop_espn_id": 1, "drop_name": "A", "delta_season_ppg": 1.0,
            "delta_weekly_mean": np.array([0.0] + [0.1] * 16),
        }], 0.0
    monkeypatch.setattr(v36, "_authoritative_claimants", cyc)
    ctx = _ctx()
    ctx.all_team_rosters[3].append(_p(1, "A"))
    out = v36.extend_release_response(_p(1, "A"), ctx, _first(), start_week=1)
    assert "CYCLE_GUARD" in out["cascade_stop_reasons"]


def test_v036_specialists_cannot_enter_player_cascade():
    out = v36.extend_release_response(_p(99, "DST", "DST"), _ctx(), _first(), start_week=1)
    assert out["cascade_destinations"] == []
    assert "NON_PLAYER_CHANNEL_OR_MISSING_ID" in out["cascade_stop_reasons"]


def test_v036_excludes_user_and_immediate_releaser_from_downstream_claimants(monkeypatch):
    seen = []
    def capture(candidate, rosters, ctx, **kwargs):
        seen.append(set(kwargs["exclude_team_ids"]))
        return [], 0.0
    monkeypatch.setattr(v36, "_authoritative_claimants", capture)
    v36.extend_release_response(_p(1, "A"), _ctx(), _first(), start_week=1)
    assert seen == [{1, 2}]


def test_v036_screen_pruned_mass_is_weighted_by_parent_branch(monkeypatch):
    def pruned(*args, **kwargs):
        return [], 0.2
    monkeypatch.setattr(v36, "_authoritative_claimants", pruned)
    out = v36.extend_release_response(_p(1, "A"), _ctx(), _first(winner=0.5), start_week=1)
    assert abs(out["cascade_pruned_probability_mass"] - 0.1) < 1e-12


def test_v036_total_reference_shift_is_order1_plus_higher(monkeypatch):
    monkeypatch.setattr(v36, "_authoritative_claimants", _fake_claimants)
    first = _first(candidate_shift=0.03)
    out = v36.extend_release_response(_p(1, "A"), _ctx(), first, start_week=1)
    total = np.asarray(out["opponent_reference_shift_ppg_by_week"])
    higher = np.asarray(out["higher_order_opponent_reference_shift_ppg_by_week"])
    assert np.allclose(total, np.asarray(first["opponent_reference_shift_ppg_by_week"]) + higher)
    assert out["higher_order_field_shift_ppg"] != 0.0


def test_v036_prospective_capture_freezes_cascade_architecture():
    source = (Path(__file__).parents[1] / "src" / "prospective_measurement_v034.py").read_text(encoding="utf-8")
    assert 'MEASUREMENT_MODEL_VERSION = "0.36"' in source
    assert '"league_response_cascade_v036"' in source
    assert '"2026_game_outcomes_used_for_tuning": False' in source


def test_v036_cli_exposes_order_decomposition_and_is_cp1252_safe(capsys):
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
            "player_membership_model": "CAUSAL_SELF_PLAYER_MEMBERSHIP_STATE_V035_FIXED1",
            "external_player_market_model": "FROZEN_CURRENT_GUARANTEED_FREEAGENT_POOL_NO_EXTERNAL_CLAIMS_V035",
            "player_state_at_release": {"week": 7}, "player_state_path": [],
            "complete_state_confirmed": True,
            "complete_state_delta": {"mean": 0.0, "mean_p16": 0.0, "mean_p84": 0.0, "p_better": 0.0, "p_tie": 1.0, "p_worse": 0.0},
            "release_response": {
                "p_claimed": 0.5, "field_shift_ppg": 0.02, "first_order_field_shift_ppg": 0.03,
                "higher_order_field_shift_ppg": -0.01, "current_opponent_shift_ppg": 0.0,
                "timing_proxy": "RECOMPUTED_AT_ACTIVATION_STATE_V033", "model": v36.CASCADE_MODEL,
                "higher_order_scenarios": 64, "cascade_orders": [{"order": 2}],
                "cascade_pruned_probability_mass": 0.02, "cascade_stop_reasons": ["MAX_DEPTH"],
            },
        }],
    }
    _print_specialist_channel(report)
    out = capsys.readouterr().out
    assert "order1=+0.030, order2+=-0.010" in out
    assert "N2+=64" in out
    assert "MAX_DEPTH" in out
    out.encode("cp1252")


def test_v036_release_metadata_and_standalone_tree():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.36"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.36")
    assert (root / "DATA_SOURCES.md").read_text(encoding="utf-8").startswith("# Data-source contract — v0.36")
    assert (root / "src" / "league_response_v036.py").exists()
    assert not (root / "materialize_v034.py").exists()
