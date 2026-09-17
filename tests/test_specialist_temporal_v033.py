from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

from src.specialist_temporal_v033 import (
    PLAYER_POSITIONS,
    TEMPORAL_INFORMATION_MODEL,
    compose_temporal_release_shift,
    compose_temporal_release_weekly,
    release_plan_summary,
)


def test_temporal_release_weekly_starts_only_at_activation_and_can_vary_by_scenario():
    base = np.zeros((4, 17), dtype=float)
    a = np.ones((4, 17), dtype=float) * 10.0
    b = np.ones((4, 17), dtype=float) * 20.0
    selected = np.array([1, 2, 1, 2])
    out = compose_temporal_release_weekly(base, {1: a, 2: b}, selected, 7)
    assert np.all(out[:, :6] == 0.0)
    assert np.all(out[[0, 2], 6:] == 10.0)
    assert np.all(out[[1, 3], 6:] == 20.0)


def test_temporal_release_shift_starts_only_at_activation_and_tracks_selected_release():
    selected = np.array([1, 2, 1, 2])
    responses = {
        1: {"opponent_reference_shift_ppg_by_week": [1.0] * 17},
        2: {"opponent_reference_shift_ppg_by_week": [2.0] * 17},
    }
    out = compose_temporal_release_shift(selected, responses, 5, 4)
    assert out.shape == (4, 17)
    assert np.all(out[:, :4] == 0.0)
    assert np.all(out[[0, 2], 4:] == 1.0)
    assert np.all(out[[1, 3], 4:] == 2.0)


def test_release_summary_is_distribution_not_frozen_named_player():
    plan = {
        "activation_week": 7,
        "information_model": TEMPORAL_INFORMATION_MODEL,
        "membership_model": "X",
        "distribution": [
            {"espn_id": 2, "name": "B", "position": "WR", "selection_probability": 0.6},
            {"espn_id": 1, "name": "A", "position": "RB", "selection_probability": 0.4},
        ],
    }
    summary = release_plan_summary(plan, {1: {"name": "A", "position": "RB"}, 2: {"name": "B", "position": "WR"}})
    assert summary["espn_id"] == 2
    assert summary["selection_probability"] == 0.6
    assert len(summary["selection_distribution"]) == 2
    assert summary["information_model"] == TEMPORAL_INFORMATION_MODEL


def test_future_release_information_boundary_does_not_double_apply_availability(monkeypatch):
    import src.specialist_temporal_v033 as temporal

    player = {"espn_id": 1, "name": "P", "position": "RB"}
    ctx = SimpleNamespace(
        league={},
        replacement_season={},
        yield_state=lambda _player, _week: SimpleNamespace(availability_probability=0.5),
    )
    monkeypatch.setattr(temporal, "_player_points", lambda _player, _ctx, _week: 10.0)
    monkeypatch.setattr(
        temporal,
        "_best_lineup_points",
        lambda _roster, _active, scores, _league, _replacement: (sum(scores.values()), set()),
    )

    # Before reveal: E[Y] = P(active) * E[Y|active] = 0.5 * 10.
    assert temporal._expected_lineup_points([player], ctx, 7) == 5.0
    # At the decision boundary after the active coordinate is revealed, use the
    # conditional yield directly; never divide it by p_active again.
    assert temporal._expected_lineup_points([player], ctx, 7, revealed_active={1: True}) == 10.0
    assert temporal._expected_lineup_points([player], ctx, 7, revealed_active={1: False}) == 0.0


def test_temporal_layer_player_universe_remains_player_channel_only():
    assert PLAYER_POSITIONS == {"QB", "RB", "WR", "TE"}


def test_specialist_policy_exposes_temporal_market_and_information_state():
    source = Path("src/specialist_policy_v032.py").read_text(encoding="utf-8")
    assert "market_states" in source
    assert "TEMPORAL_INFORMATION_MODEL" in source
    assert "RECOMPUTED_AT_ACTIVATION_STATE_V033" in source
    assert "COMMISSIONED_CURRENT_STATE_RELEASE_RESPONSE_V031" in source
    assert "FROZEN_CURRENT_PLAYER_CLAIM_RESPONSE_APPLIED_FROM_ACTIVATION_WEEK_V032_FIXED4" not in source
    assert '"model_version": "0.35-fixed1"' in source
    assert '"policy_layer": "SPECIALIST_WITH_CAUSAL_PLAYER_STATE_V035"' in source


def test_specialist_market_state_records_pre_and_post_free_pool():
    source = Path("src/specialist_policy_v032.py").read_text(encoding="utf-8")
    assert '"free_agent_ids_before"' in source
    assert '"free_agent_ids_after"' in source
    assert '"released_after_week"' in source
    assert "free.update(dropped_next)" in source
    assert source.index("free.update(dropped_next)") < source.index('"free_agent_ids_after"')


def test_v033_preserves_no_hindsight_specialist_boundaries():
    source = Path("src/specialist_policy_v032.py").read_text(encoding="utf-8")
    assert "_best_choice(portfolio, ctx, week, cache)" in source
    assert "_best_free(free, ctx, week, cache)" in source
    assert "realized MC outcome affects a transaction or starter choice" in source
    temporal = Path("src/specialist_temporal_v033.py").read_text(encoding="utf-8")
    assert "No realized fantasy-point sample" in temporal
    assert "predictive_uniforms" in temporal


def test_v033_release_response_is_recomputed_at_activation_not_frozen_current():
    temporal = Path("src/specialist_temporal_v033.py").read_text(encoding="utf-8")
    assert "activation_week" in temporal
    assert "_temporal_manager_interest" in temporal
    assert "_release_claim_probability" in temporal
    assert "_simulate_predictive_weekly_points" in temporal
    assert "delta_weekly[:, : start_week - 1] = 0.0" in temporal


def test_v033_complete_state_supports_scenario_conditioned_externality_under_crn():
    source = Path("src/specialist_policy_v032.py").read_text(encoding="utf-8")
    assert "compose_temporal_release_weekly" in source
    assert "compose_temporal_release_shift" in source
    assert "shift.ndim == 2" in source
    assert "_scenario_h2h_utility_against" in source


def test_v033_release_metadata():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.35-fixed1")
    assert (root / "DATA_SOURCES.md").read_text(encoding="utf-8").startswith("# Data-source contract — v0.35-fixed1")


def test_v033_cli_remains_ascii_cp1252_contract():
    source = Path("fantasy.py").read_text(encoding="utf-8")
    block_start = source.index("def _print_specialist_channel")
    block_end = source.index("\ndef cmd_defense_channel", block_start)
    block = source[block_start:block_end]
    block.encode("cp1252")



def test_v033_fixed2_cli_reports_temporal_release_provenance_and_distribution(capsys):
    from fantasy import _print_specialist_channel
    report = {
        "week": 1,
        "channel": "DEFENSE",
        "team_name": "Us",
        "position": "DST",
        "mc_scenarios": 64,
        "owned": [{"name": "Owned D/ST", "team": "DET"}],
        "baseline": {"weighted_mean_ppg": 5.0, "current_week_mean": 5.0, "current_week_sd": 3.0, "current_week_choice": "Owned D/ST"},
        "swap_actions": [],
        "one_slot_policy": {},
        "carry2_current_recommendation": "HOLD_ONE_DST_NOW",
        "dynamic_carry_actions": [{
            "activation_week": 7,
            "effective_player_release_week": 8,
            "current_activation": False,
            "add_name": "Future D/ST",
            "add_team": "TEN",
            "dynamic_channel_delta_ppg": 0.2,
            "classification": "NO_CARRY2_RESOLVED_EDGE",
            "one_slot_policy_ppg": 5.8,
            "two_slot_policy_ppg": 6.0,
            "player_slot_release": {
                "name": "Player A",
                "position": "RB",
                "selection_probability": 0.6,
                "selection_distribution": [
                    {"name": "Player A", "selection_probability": 0.6},
                    {"name": "Player B", "selection_probability": 0.4},
                ],
            },
            "complete_state_confirmed": True,
            "complete_state_delta": {"mean": 0.003, "mean_p16": 0.002, "mean_p84": 0.004, "p_better": 0.3, "p_tie": 0.5, "p_worse": 0.2},
            "release_response": {
                "p_claimed": 0.8,
                "field_shift_ppg": 0.04,
                "current_opponent_shift_ppg": 0.0,
                "timing_proxy": "RECOMPUTED_AT_ACTIVATION_STATE_V033",
            },
        }],
    }
    _print_specialist_channel(report)
    out = capsys.readouterr().out
    assert "player release begins W8: Player A (RB) [dominant=60.0%]" in out
    assert "release-state distribution: Player A 60.0%; Player B 40.0%" in out
    assert "released-player response:" in out
    assert "timing=RECOMPUTED_AT_ACTIVATION_STATE_V033" in out
    assert "released-player response proxy:" not in out
    out.encode("cp1252")


def test_v033_fixed2_cli_keeps_complete_current_row_and_eighth_swap_header(capsys):
    from fantasy import _print_specialist_channel
    swaps = []
    for idx in range(1, 9):
        swaps.append({
            "action": "SWAP", "add_name": "Jake Elliott" if idx == 8 else f"K{idx}",
            "add_team": "PHI" if idx == 8 else "X", "drop_name": "Owned K",
            "fantasy_status": "FREEAGENT", "delta_channel_ppg": -0.1 * idx,
            "p_channel_better": 0.4, "current_week_delta": 0.0, "classification": "HOLD_CHANNEL",
        })
    report = {
        "week": 1, "channel": "DEFENSE", "team_name": "Us", "position": "DST", "mc_scenarios": 64,
        "owned": [{"name": "Owned D/ST", "team": "DET"}],
        "baseline": {"weighted_mean_ppg": 5.0, "current_week_mean": 5.0, "current_week_sd": 3.0, "current_week_choice": "Owned D/ST"},
        "swap_actions": swaps,
        "one_slot_policy": {},
        "carry2_current_recommendation": "HOLD_ONE_DST_NOW",
        "dynamic_carry_actions": [{
            "activation_week": 1, "effective_player_release_week": 1, "current_activation": True,
            "add_name": "Packers D/ST", "add_team": "GB", "dynamic_channel_delta_ppg": 0.129,
            "classification": "NO_CARRY2_RESOLVED_EDGE", "one_slot_policy_ppg": 5.892, "two_slot_policy_ppg": 6.021,
            "player_slot_release": {"name": "Justice Hill", "position": "RB", "selection_probability": 1.0, "selection_distribution": [{"name": "Justice Hill", "selection_probability": 1.0}]},
            "complete_state_confirmed": True,
            "complete_state_delta": {"mean": 0.00246, "mean_p16": 0.00158, "mean_p84": 0.00322, "p_better": 0.206, "p_tie": 0.641, "p_worse": 0.153},
            "release_response": {"p_claimed": 0.549, "field_shift_ppg": 0.007, "current_opponent_shift_ppg": 0.012, "timing_proxy": "COMMISSIONED_CURRENT_STATE_RELEASE_RESPONSE_V031"},
        }],
    }
    _print_specialist_channel(report, limit=8)
    out = capsys.readouterr().out
    assert " 8. SWAP Jake Elliott (PHI) / DROP Owned K [FREEAGENT]" in out
    assert "one-slot=5.892 | two-slot=6.021 | player release begins W1: Justice Hill (RB) [dominant=100.0%]" in out
    assert "complete-state delta=+0.246 pp" in out
    assert "released-player response: P(claimed)=54.9%" in out
