from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.prospective_measurement_v034 import canonical_sha256
from src.weekly_decision_cycle import (
    DST,
    IR,
    KICKER,
    LINEUP,
    PLAYER,
    PROVENANCE,
    REQUIRED_CHANNELS,
    STATE_ACTION,
    STATE_BLOCKED_HEALTH,
    STATE_CAPTURE_REQUIRED,
    STATE_INCOMPLETE,
    STATE_NO_ACTION,
    STATUS_ACTION,
    TRADE_1X1,
    TRADE_MULTI,
    TRADE_SPECIALIST,
    ChannelReceipt,
    WeeklyAuthorities,
    classify_weekly_decision,
    run_weekly_decision_cycle,
)
from src.weekly_operational_health import (
    HealthItem,
    OperationalHealthReceipt,
    build_operational_health_receipt,
)


def _capture() -> dict:
    payload = {
        "schema_version": 2,
        "pre_data_firewall": {
            "2026_game_outcomes_used_for_tuning": False,
            "automatic_refit": False,
            "automatic_calibration": False,
            "postgame_specialist_ledger_enabled": False,
            "postgame_behavior_calibration_enabled": False,
        },
    }
    payload["integrity"] = {"canonical_payload_sha256": canonical_sha256(payload)}
    return payload


def _snapshot() -> dict:
    return {
        "snapshot_utc": "2026-09-30T20:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 4,
            "teams": [{"team_id": 1, "name": "Us", "roster": []}],
        },
        "source_status": {
            "espn": {"ok": True},
            "sleeper": {"ok": True},
            "nflverse_rosters": {"ok": True},
            "nflverse_matchups": {"ok": True},
            "nfl_official_rosters": {"complete": True},
            "nfl_official": {"ok": True},
        },
    }


def _write_dependency_files(tmp_path: Path) -> tuple[Path, Path, Path, Path, dict[str, str]]:
    league = tmp_path / "league.json"
    model = tmp_path / "model.json"
    values = tmp_path / "values.csv"
    version = tmp_path / "VERSION"
    league.write_text("{}\n", encoding="utf-8")
    model.write_text("{}\n", encoding="utf-8")
    values.write_text("espn_id\n", encoding="utf-8")
    version.write_text("0.36\n", encoding="utf-8")
    deps = {
        "league_config": hashlib.sha256(league.read_bytes()).hexdigest(),
        "model_config": hashlib.sha256(model.read_bytes()).hexdigest(),
        "player_values": hashlib.sha256(values.read_bytes()).hexdigest(),
    }
    return league, model, values, version, deps


def _healthy_health() -> OperationalHealthReceipt:
    return OperationalHealthReceipt(
        schema_version=1,
        generated_utc="2026-09-30T20:00:00+00:00",
        status="PASS",
        items=(HealthItem("x", "PASS", {}),),
        blockers=(),
    )


def _complete_channels(action: bool = False) -> list[ChannelReceipt]:
    out = []
    for ix, key in enumerate(REQUIRED_CHANNELS):
        out.append(ChannelReceipt(
            key=key,
            label=key,
            status=STATUS_ACTION if action and ix == 0 else f"PASS / HOLD:{key.upper()}",
            authority="test",
        ))
    return out


def test_classifier_is_fail_closed_and_complete_only_with_full_matrix():
    health = _healthy_health()
    complete = _complete_channels()
    assert classify_weekly_decision(complete, health, capture_required=False)[0] == STATE_NO_ACTION
    assert classify_weekly_decision(_complete_channels(action=True), health, capture_required=False)[0] == STATE_ACTION

    missing = [row for row in complete if row.key != PLAYER]
    assert classify_weekly_decision(missing, health, capture_required=False)[0] == STATE_INCOMPLETE

    incomplete = list(complete)
    incomplete[0] = ChannelReceipt(LINEUP, "lineup", "INCOMPLETE_COVERAGE:test", "test")
    assert classify_weekly_decision(incomplete, health, capture_required=False)[0] == STATE_INCOMPLETE

    blocked = OperationalHealthReceipt(1, health.generated_utc, "BLOCKED_HEALTH", (), ("x",))
    assert classify_weekly_decision(complete, blocked, capture_required=False)[0] == STATE_BLOCKED_HEALTH
    assert classify_weekly_decision(complete, health, capture_required=True)[0] == STATE_CAPTURE_REQUIRED


def test_operational_health_requires_all_explicit_evidence(tmp_path: Path):
    league, model, values, version, deps = _write_dependency_files(tmp_path)
    identity = {
        "commissioned": True,
        "source_checkpoint": "abc123",
        "runtime_version": "0.36",
        "dependencies": deps,
    }
    memory = {"status": "PASS", "source_checkpoint": "abc123"}
    health = build_operational_health_receipt(
        snapshot=_snapshot(),
        capture=_capture(),
        commissioning_identity=identity,
        observed_dependencies=deps,
        observed_runtime_version=version.read_text().strip(),
        memory_health=memory,
        persistence_state=SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
        unresolved_diagnostics=(),
        receipt_inventory=REQUIRED_CHANNELS,
        required_receipts=REQUIRED_CHANNELS,
    )
    assert health.status == "PASS"
    assert not health.blockers

    bad_snapshot = _snapshot()
    del bad_snapshot["source_status"]["nfl_official"]
    bad = build_operational_health_receipt(
        snapshot=bad_snapshot,
        capture=_capture(),
        commissioning_identity=identity,
        observed_dependencies=deps,
        observed_runtime_version="0.36",
        memory_health=memory,
        persistence_state=SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
        unresolved_diagnostics=(),
        receipt_inventory=REQUIRED_CHANNELS,
        required_receipts=REQUIRED_CHANNELS,
    )
    assert bad.status == "BLOCKED_HEALTH"
    assert any("provider:nfl_official" in item for item in bad.blockers)


def test_gate_a_orchestrates_existing_authorities_but_remains_incomplete(tmp_path: Path):
    league_path, model_path, values_path, version_path, deps = _write_dependency_files(tmp_path)
    calls = {"player_position": "unset"}

    def lineup(*args, **kwargs):
        return {
            "missing_slots": [],
            "selected_espn_ids": [1],
            "current_starter_espn_ids": [1],
            "locked_espn_ids": [],
            "action_required": False,
        }

    def player(*args, **kwargs):
        calls["player_position"] = kwargs.get("position")
        return {
            "candidate_pool_evaluated": 20,
            "legal_drop_players": 5,
            "free_agent_actions": [{"combined_action_classification": "ACTIONABLE_EDGE", "add_espn_id": 9}],
            "waiver_actions": [],
            "market_channel": "PLAYER_QB_RB_WR_TE_V031",
        }

    def specialist(*args, **kwargs):
        return {
            "one_slot_policy": {
                "excluded_current_waivers": 0,
                "guaranteed_free_agents_initial": 4,
                "recommended_current_action": {"action": "HOLD"},
                "authoritative_current_action": False,
                "complete_state_delta": {"classification": "NO_RESOLVED_EDGE"},
            }
        }

    def trades(*args, **kwargs):
        return [{"classification": "NO_RESOLVED_EDGE"}]

    authorities = WeeklyAuthorities(
        lineup=lineup,
        player_actions=player,
        defense=specialist,
        kicker=specialist,
        trade_search=trades,
        persistence_state=lambda: SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
    )
    receipt = run_weekly_decision_cycle(
        _snapshot(), {}, {},
        values_path=values_path,
        league_path=league_path,
        model_path=model_path,
        version_path=version_path,
        team_id=1,
        capture=_capture(),
        commissioning_identity={
            "commissioned": True,
            "source_checkpoint": "abc123",
            "runtime_version": "0.36",
            "dependencies": deps,
        },
        memory_health={"status": "PASS", "source_checkpoint": "abc123"},
        authorities=authorities,
    )
    assert calls["player_position"] is None, "user examples/position filters must not narrow broad player search"
    assert receipt.overall_state == STATE_INCOMPLETE
    by_key = {row.key: row for row in receipt.channels}
    assert by_key[PLAYER].status == STATUS_ACTION
    assert by_key[IR].status.startswith("INCOMPLETE_COVERAGE:GATE_B")
    assert by_key[TRADE_MULTI].status.startswith("INCOMPLETE_COVERAGE:GATE_B")
    assert by_key[TRADE_SPECIALIST].status.startswith("INCOMPLETE_COVERAGE:GATE_B")
    assert {LINEUP, PLAYER, DST, KICKER, IR, TRADE_1X1, TRADE_MULTI, TRADE_SPECIALIST, PROVENANCE} == set(by_key)


def test_current_specialist_waiver_is_never_silently_dropped(tmp_path: Path):
    league_path, model_path, values_path, version_path, deps = _write_dependency_files(tmp_path)

    def specialist(*args, **kwargs):
        return {
            "one_slot_policy": {
                "excluded_current_waivers": 2,
                "guaranteed_free_agents_initial": 4,
                "recommended_current_action": {"action": "ADD", "add_espn_id": 7},
                "authoritative_current_action": True,
                "complete_state_delta": {"classification": "ACTIONABLE_EDGE"},
            }
        }

    authorities = WeeklyAuthorities(
        lineup=lambda *a, **k: {"missing_slots": [], "selected_espn_ids": [], "current_starter_espn_ids": [], "action_required": False},
        player_actions=lambda *a, **k: {"free_agent_actions": [], "waiver_actions": []},
        defense=specialist,
        kicker=specialist,
        trade_search=lambda *a, **k: [],
        persistence_state=lambda: SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
    )
    receipt = run_weekly_decision_cycle(
        _snapshot(), {}, {}, values_path=values_path, league_path=league_path,
        model_path=model_path, version_path=version_path, team_id=1,
        capture=_capture(),
        commissioning_identity={"commissioned": True, "source_checkpoint": "abc123", "runtime_version": "0.36", "dependencies": deps},
        memory_health={"status": "PASS", "source_checkpoint": "abc123"},
        authorities=authorities,
    )
    by_key = {row.key: row for row in receipt.channels}
    assert by_key[DST].status == "INCOMPLETE_COVERAGE:CURRENT_SPECIALIST_WAIVERS_UNSUPPORTED"
    assert by_key[KICKER].status == "INCOMPLETE_COVERAGE:CURRENT_SPECIALIST_WAIVERS_UNSUPPORTED"
    assert by_key[DST].evidence["excluded_current_waivers"] == 2


def test_missing_capture_and_stale_state_preempt_action_search_completion(tmp_path: Path):
    league_path, model_path, values_path, version_path, deps = _write_dependency_files(tmp_path)
    authorities = WeeklyAuthorities(
        lineup=lambda *a, **k: {"missing_slots": [], "selected_espn_ids": [], "current_starter_espn_ids": [], "action_required": False},
        player_actions=lambda *a, **k: {"free_agent_actions": [], "waiver_actions": []},
        defense=lambda *a, **k: {"one_slot_policy": {"excluded_current_waivers": 0, "recommended_current_action": {"action": "HOLD"}, "authoritative_current_action": False}},
        kicker=lambda *a, **k: {"one_slot_policy": {"excluded_current_waivers": 0, "recommended_current_action": {"action": "HOLD"}, "authoritative_current_action": False}},
        trade_search=lambda *a, **k: [],
        persistence_state=lambda: SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
    )
    common = dict(
        values_path=values_path, league_path=league_path, model_path=model_path,
        version_path=version_path, team_id=1,
        commissioning_identity={"commissioned": True, "source_checkpoint": "abc123", "runtime_version": "0.36", "dependencies": deps},
        memory_health={"status": "PASS", "source_checkpoint": "abc123"}, authorities=authorities,
    )
    assert run_weekly_decision_cycle(_snapshot(), {}, {}, capture=None, **common).overall_state == STATE_CAPTURE_REQUIRED
    assert run_weekly_decision_cycle(_snapshot(), {}, {}, capture=_capture(), material_state_change=True, **common).overall_state == STATE_CAPTURE_REQUIRED


def test_health_blocker_precedes_known_gate_b_coverage_gaps(tmp_path: Path):
    league_path, model_path, values_path, version_path, deps = _write_dependency_files(tmp_path)
    authorities = WeeklyAuthorities(
        lineup=lambda *a, **k: {"missing_slots": [], "selected_espn_ids": [], "current_starter_espn_ids": [], "action_required": False},
        player_actions=lambda *a, **k: {"free_agent_actions": [], "waiver_actions": []},
        defense=lambda *a, **k: {"one_slot_policy": {"excluded_current_waivers": 0, "recommended_current_action": {"action": "HOLD"}, "authoritative_current_action": False}},
        kicker=lambda *a, **k: {"one_slot_policy": {"excluded_current_waivers": 0, "recommended_current_action": {"action": "HOLD"}, "authoritative_current_action": False}},
        trade_search=lambda *a, **k: [],
        persistence_state=lambda: SimpleNamespace(enabled=False, failed=False, failures=0, disabled_reason="disabled"),
    )
    receipt = run_weekly_decision_cycle(
        _snapshot(), {}, {}, values_path=values_path, league_path=league_path, model_path=model_path,
        version_path=version_path, team_id=1, capture=_capture(),
        commissioning_identity={"commissioned": True, "source_checkpoint": "abc123", "runtime_version": "0.36", "dependencies": deps},
        memory_health={"status": "FAIL", "source_checkpoint": "abc123"}, authorities=authorities,
    )
    assert receipt.overall_state == STATE_BLOCKED_HEALTH
    assert any("memory_health" in item for item in receipt.stale_or_missing_health)


def test_cli_gui_and_chat_surfaces_do_not_define_a_second_completion_classifier():
    fantasy_source = Path("fantasy.py").read_text(encoding="utf-8")
    service_source = Path("src/gui/season_service.py").read_text(encoding="utf-8")
    chat_source = Path("src/gui/chat_report.py").read_text(encoding="utf-8")

    assert "def cmd_weekly_cycle(args):" in fantasy_source
    assert "run_weekly_decision_cycle(" in fantasy_source
    assert "def weekly_decision_cycle(" in service_source
    assert "from ..weekly_decision_cycle import run_weekly_decision_cycle" in service_source
    # Chat diagnosis remains descriptive; it cannot independently issue one of the
    # roster-wide completion states owned by weekly_decision_cycle.py.
    for state in (
        "COMPLETE / ACTION_REQUIRED",
        "COMPLETE / NO_ACTION",
        "INCOMPLETE_COVERAGE",
        "BLOCKED_HEALTH",
        "CAPTURE_REQUIRED",
    ):
        assert state not in chat_source
