from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from src.prospective_measurement_v034 import (
    BEHAVIOR_STATE_MODEL,
    KICKER_COMPONENT_STATUS,
    MEASUREMENT_CONTRACT,
    PLAYER_CAPTURE_MODEL,
    build_behavioral_observation_state,
    canonical_sha256,
    capture_summary,
    enrich_pregame_capture,
    verify_capture_integrity,
)


def test_v034_capture_integrity_detects_mutation():
    base = {"players": [], "notes": [], "season": 2026, "week": 1}
    snapshot = {"snapshot_utc": "2026-09-03T20:00:00Z", "espn": {"teams": [], "available_players": []}}
    ctx = SimpleNamespace(
        league={}, week=1, espn=snapshot["espn"], all_team_rosters={}, actionable_available=[],
    )
    payload = enrich_pregame_capture(base, snapshot, {}, ctx, {})
    assert verify_capture_integrity(payload)
    changed = copy.deepcopy(payload)
    changed["week"] = 2
    assert not verify_capture_integrity(changed)


def test_v034_canonical_hash_is_order_independent():
    assert canonical_sha256({"a": 1, "b": [2, 3]}) == canonical_sha256({"b": [2, 3], "a": 1})


def test_v034_canonical_hash_handles_nonfinite_snapshot_scalars_deterministically():
    assert canonical_sha256({"x": float("nan")}) == canonical_sha256({"x": float("nan")})
    assert canonical_sha256({"x": float("inf")}) != canonical_sha256({"x": float("-inf")})


def test_v034_behavior_state_freezes_waiver_and_market_covariates():
    snapshot = {
        "snapshot_utc": "2026-09-03T20:00:00Z",
        "espn": {
            "teams": [{"team_id": 1, "name": "Us", "waiver_rank": 11, "roster": [{"espn_id": 10, "position": "RB"}]}],
            "available_players": [{
                "espn_id": 20, "name": "FA", "position": "WR", "fantasy_status": "FREEAGENT",
                "percent_owned": 12.3, "sleeper_trending_add_24h": 7,
            }],
        },
    }
    model = {"transaction_manager": {"waiver_need_logit_bonus": 0.6}, "market_manager": {"trade_accept_intercept": -0.35}}
    ctx = SimpleNamespace(actionable_available=[])
    state = build_behavioral_observation_state(snapshot, model, {"teams": 12}, ctx)
    assert state["model"] == BEHAVIOR_STATE_MODEL
    assert state["teams"][0]["waiver_rank"] == 11
    assert state["market_players"][0]["percent_owned"] == 12.3
    assert state["behavior_config"]["calibration_status"] == "UNCALIBRATED_PRE_DATA_PRIORS"
    assert state["behavior_config"]["full_transaction_manager_config"]["waiver_need_logit_bonus"] == 0.6
    assert state["behavior_config"]["full_market_manager_config"]["trade_accept_intercept"] == -0.35
    assert state["behavior_config"]["behavior_not_football_value"] is True


def test_v034_capture_is_explicitly_pre_data_and_non_calibrating():
    base = {"players": [{"espn_id": 1}], "notes": [], "season": 2026, "week": 1}
    snapshot = {"snapshot_utc": "2026-09-03T20:00:00Z", "espn": {"teams": [], "available_players": []}}
    ctx = SimpleNamespace(league={}, week=1, espn=snapshot["espn"], all_team_rosters={}, actionable_available=[])
    payload = enrich_pregame_capture(base, snapshot, {}, ctx, {})
    assert payload["measurement_contract"] == MEASUREMENT_CONTRACT
    assert payload["player_measurement_model"] == PLAYER_CAPTURE_MODEL
    assert payload["pre_data_firewall"]["2026_game_outcomes_used_for_tuning"] is False
    assert payload["pre_data_firewall"]["automatic_calibration"] is False
    assert payload["pre_data_firewall"]["next_data_informed_major_version"] == "1.X"


def test_v034_capture_summary_reports_all_measurement_sectors():
    payload = {
        "measurement_contract": MEASUREMENT_CONTRACT,
        "players": [{}, {}],
        "league_player_predictions": {"count": 17, "records": [{}] * 17},
        "specialist_predictions": {"counts": {"total": 3, "DST": 1, "K": 2}},
        "behavioral_observation_state": {"teams": [{}, {}], "market_players": [{}, {}, {}]},
    }
    payload["integrity"] = {"canonical_payload_sha256": canonical_sha256(payload)}
    summary = capture_summary(payload)
    assert summary["players"] == 2
    assert summary["league_players"] == 17
    assert summary["specialists"] == 3
    assert summary["dst"] == 1
    assert summary["kickers"] == 2
    assert summary["behavior_teams"] == 2
    assert summary["market_players"] == 3


def test_v034_kicker_contract_does_not_fabricate_components():
    source = Path("src/prospective_measurement_v034.py").read_text(encoding="utf-8")
    assert KICKER_COMPONENT_STATUS in source
    assert '"component_predictions": {}' in source
    assert "FG/XP opportunity and distance components are not yet modeled and are not fabricated" in source


def test_v034_dst_capture_uses_existing_component_physics():
    source = Path("src/prospective_measurement_v034.py").read_text(encoding="utf-8")
    assert "dst_component_expectation" in source
    assert "NFLVERSE_DST_COMPONENTS_V023_EXACT_ESPN_RESPONSE" in source
    assert "_specialist_week_samples" in source


def test_v034_closure_wrapper_preserves_player_ledger_and_adds_measurements():
    source = Path("src/closure.py").read_text(encoding="utf-8")
    assert "_build_pregame_capture_from_context_pre_v034" in source
    assert "enrich_pregame_capture" in source
    assert "league_player_predictions" in source
    assert "ALL_ROSTERED_QB_RB_WR_TE_V034" in source
    assert "build_closure_ledger" in source
    assert 'payload.get("players")' in source or "payload.get('players')" in source


def test_v034_existing_player_closure_gui_assertion_advanced():
    source = Path("tests/test_closure_v029.py").read_text(encoding="utf-8")
    assert 'payload["model_version"] == "0.35-fixed1"' in source
    assert 'payload["measurement_contract"] == "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034"' in source


def test_v034_cli_capture_reports_measurement_contract_and_is_cp1252_safe():
    source = Path("fantasy.py").read_text(encoding="utf-8")
    start = source.index("def cmd_closure_capture")
    end = source.index("\ndef cmd_closure_update", start)
    block = source[start:end]
    assert "Measurement contract:" in block
    assert "All-league player predictions:" in block
    assert "Specialist predictions:" in block
    assert "Behavior state:" in block
    assert "Capture integrity:" in block
    block.encode("cp1252")


def test_v034_gui_capture_returns_measurement_counts():
    source = Path("src/gui/season_service.py").read_text(encoding="utf-8")
    assert '"league_players": measurement.get("league_players")' in source
    assert '"specialists": measurement.get("specialists")' in source
    assert '"market_players": measurement.get("market_players")' in source
    assert '"measurement_contract": measurement.get("measurement_contract")' in source


def test_v034_release_metadata_and_a_priori_firewall():
    root = Path(__file__).parents[1]
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.35-fixed1"
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Fantasy Football Season Manager v0.35-fixed1")
    data_sources = (root / "DATA_SOURCES.md").read_text(encoding="utf-8")
    assert data_sources.startswith("# Data-source contract — v0.35-fixed1")
    assert "No 2026 game outcome is consumed by v0.34" in data_sources
    assert "Record now. Calibrate in 1.X." in data_sources
