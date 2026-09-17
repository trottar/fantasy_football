from __future__ import annotations

from pathlib import Path

import pytest

import src.specialist_channels as specialist_channels
from fantasy import _print_specialist_channel
from src.specialist_channels import evaluate_defense_channel
from src.transaction_manager import UtilityContext
from test_specialist_channels_v031 import league_cfg, model_cfg, p, snapshot, values_file


def test_fixed2_kicker_normalizes_was_to_wsh_schedule_key(tmp_path):
    candidate = p(9901, "Alias K", "K", 8.0, team="WAS", fantasy_status="FREEAGENT")
    snap = snapshot([candidate])
    snap.setdefault("matchup_context", {}).setdefault("team_week", {})["WSH"] = {
        "1": {"opponent": "DAL", "team_implied_points": 30.0}
    }
    values = values_file(tmp_path, [(9901, 8.0)])
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    candidate = next(x for x in ctx.available if int(x["espn_id"]) == 9901)
    _, _, detail = specialist_channels._specialist_week_samples(candidate, ctx, 1)
    assert detail["opponent"] == "DAL"
    assert detail["team_implied_points"] == pytest.approx(30.0)
    assert detail["source"] == "TEAM_IMPLIED_POINTS_KICKER_CHANNEL_V031"


def test_fixed2_carry_is_screen_not_authoritative(tmp_path):
    candidate = p(9902, "Complement DST", "DST", 11.0, team="KC", fantasy_status="FREEAGENT")
    report = evaluate_defense_channel(
        snapshot([candidate]), league_cfg(), model_cfg(),
        values_path=values_file(tmp_path, [(9902, 11.0)]),
        team_name="Us", mc_scenarios=128,
    )
    assert report["model_version"] == "0.31-fixed3"
    assert report["carry_policy_status"] == "DIAGNOSTIC_STATIC_ONE_SPECIALIST_BASELINE_V031_FIXED2"
    assert report["carry_actions"]
    for row in report["carry_actions"]:
        assert row["authoritative"] is False
        assert row["complete_state_confirmed"] is False
        assert row["carry_baseline_kind"] == "BEST_STATIC_ONE_SPECIALIST_V031_FIXED2"
        assert row["classification"] in {"CARRY_SYNERGY_SCREEN", "HOLD_CHANNEL"}
        assert row["classification"] != "CARRY_SYNERGY_EDGE"


def test_fixed2_carry_exposes_player_slot_cost_provenance(tmp_path):
    candidate = p(9903, "Second DST", "DST", 10.0, team="KC", fantasy_status="FREEAGENT")
    report = evaluate_defense_channel(
        snapshot([candidate]), league_cfg(), model_cfg(),
        values_path=values_file(tmp_path, [(9903, 10.0)]),
        team_name="Us", mc_scenarios=128,
    )
    row = report["carry_actions"][0]
    expected = (
        float(row["player_slot_lineup_cost_ppg"])
        + float(row["player_slot_insurance_weight"])
        * float(row["player_slot_insurance_cost_ppg"])
    )
    assert row["player_slot_cost_ppg"] == pytest.approx(expected)
    assert row["net_screen_ppg"] == pytest.approx(row["net_complete_state_ppg"])
    assert row["player_slot_cost_method"] == "PLAYER_CHANNEL_SEASON_LINEUP_PLUS_WEIGHTED_INSURANCE_V031_FIXED2"


def test_fixed2_specialist_cli_labels_static_swaps_and_preserves_headers(capsys):
    report = {
        "week": 1, "channel": "KICKER", "team_name": "Us", "position": "K",
        "owned": [{"name": "Owned K", "team": "KC"}], "mc_scenarios": 32,
        "baseline": {
            "weighted_mean_ppg": 8.0, "current_week_mean": 8.0,
            "current_week_sd": 3.0, "current_week_choice": "Owned K",
        },
        "swap_actions": [
            {
                "action": "SWAP", "add_name": "A", "add_team": "A", "drop_name": "Owned K",
                "fantasy_status": "FREEAGENT", "delta_channel_ppg": -0.1,
                "p_channel_better": 0.45, "current_week_delta": 0.2,
                "classification": "HOLD_CHANNEL", "weekly_plan": [],
            },
            {
                "action": "SWAP", "add_name": "B", "add_team": "B", "drop_name": "Owned K",
                "fantasy_status": "FREEAGENT", "delta_channel_ppg": -0.2,
                "p_channel_better": 0.40, "current_week_delta": -0.1,
                "classification": "HOLD_CHANNEL", "weekly_plan": [],
            },
        ],
        "carry_actions": [],
    }
    _print_specialist_channel(report, limit=8)
    out = capsys.readouterr().out
    assert "=== SAME-CHANNEL STATIC SWAPS ===" in out
    assert " 1. SWAP A" in out
    assert " 2. SWAP B" in out


def test_fixed2_version_metadata():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.35-fixed1")
    assert (root / "DATA_SOURCES.md").read_text(encoding="utf-8").startswith("# Data-source contract — v0.35-fixed1")
