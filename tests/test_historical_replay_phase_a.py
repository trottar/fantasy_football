from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.counterfactual_replay import DependencyProvenance, freeze_phase_a_receipt
from src.historical_replay_phase_a import (
    ACTION_FAMILY_ORDER,
    DST,
    IR,
    KICKER,
    LINEUP,
    PLAYER,
    TRADE_1X1,
    TRADE_MULTI,
    TRADE_SPECIALIST,
    WEEK3_PHASE_A_EVALUATOR_CONTRACT,
    Week3PhaseAEvaluation,
    _bind_frozen_transaction_settings,
    _captured_base_mean,
    _coverage,
    _freeze_candidates_and_selection,
    _frozen_availability_state,
    _frozen_yield_state,
    _ir_candidates,
    _lineup_candidates,
    _normalized_transaction_settings,
    _overlay_enriched_row,
    _player_candidates,
    _specialist_trade_candidates,
    _trade_candidates,
    frozen_week3_authority_overlay,
)


def _player_record(pid: int = 1) -> dict:
    return {
        "espn_id": pid,
        "name": "Player",
        "position": "WR",
        "nfl_team": "PIT",
        "operational_mean_ppg": 12.0,
        "pre_matchup_mean_ppg": 11.5,
        "model_mean_ppg": 11.0,
        "matchup_model_mean_ppg": 11.8,
        "espn_anchor_ppg": 12.2,
        "espn_anchor_kind": "ESPN_WEEKLY",
        "predictive_sd_ppg": 7.0,
        "game_sd_ppg": 6.0,
        "model_sd_ppg": 2.0,
        "kinematic_sd_ppg": 1.0,
        "interaction_sd_ppg": 2.0,
        "kinematic_factor": 1.02,
        "kinematic_source": "TEST",
        "interaction_factor": 1.01,
        "interaction_delta_ppg": 0.2,
        "interaction_artifact_id": "artifact",
        "matchup_opponent": "BAL",
        "p_active": 0.8,
        "p_full_given_active": 0.75,
        "p_out": 0.2,
        "p_limited": 0.2,
        "p_full": 0.6,
        "limited_workload_fraction": 0.5,
        "expected_workload_factor": 0.7,
        "availability_status": "QUESTIONABLE",
        "availability_status_source": "ESPN",
        "availability_evidence_level": "TEST",
        "availability_posterior_method": "TEST",
        "availability_calibration_status": "UNCALIBRATED",
        "practice_source": "TEST",
        "practice_sequence": ["LIMITED", "FULL"],
        "kickoff_utc": "2026-09-27T17:00:00+00:00",
        "reveal_utc": "2026-09-27T15:30:00+00:00",
        "lock_group": "INDIVIDUAL_GAME",
        "source": "FROZEN",
    }


def _specialist_record(pid: int = -16008, pos: str = "DST") -> dict:
    return {
        "espn_id": pid,
        "name": "Specialist",
        "position": pos,
        "nfl_team": "PIT",
        "operational_mean_ppg": 8.0,
        "pre_matchup_operational_mean_ppg": 7.5,
        "model_mean_ppg": 7.0,
        "matchup_model_mean_ppg": 8.1,
        "espn_anchor_ppg": 7.8,
        "espn_anchor_kind": "ESPN_WEEKLY",
        "predictive_sd_ppg": 5.0,
        "game_sd_ppg": 4.0,
        "model_sd_ppg": 1.5,
        "kinematic_sd_ppg": 1.0,
        "kinematic_factor": 1.03,
        "kinematic_source": "TEST",
        "matchup_opponent": "BAL",
        "matchup_home": True,
        "team_implied_points": 21.0,
        "component_predictions": {"sacks": 2.0} if pos == "DST" else {},
        "kickoff_utc": "2026-09-27T17:00:00+00:00",
        "inactive_reveal_utc": "2026-09-27T15:30:00+00:00",
        "lock_group": "INDIVIDUAL_GAME",
        "lock_source": "FROZEN",
    }


def test_normalized_transaction_settings_from_raw_espn_msettings():
    raw = {
        "settings": {
            "tradeSettings": {
                "revisionHours": 48,
                "vetoVotesRequired": 4,
                "deadlineDate": 1796371200000,
                "max": -1,
            },
            "rosterSettings": {
                "lineupLocktimeType": "INDIVIDUAL_GAME",
                "rosterLocktimeType": "INDIVIDUAL_GAME",
            },
            "acquisitionSettings": {"transactionLockingEnabled": False},
        }
    }
    out = _normalized_transaction_settings(raw)
    assert out["trade_review_hours"] == 48
    assert out["lineup_locktime_type"] == "INDIVIDUAL_GAME"
    assert out["roster_locktime_type"] == "INDIVIDUAL_GAME"


def test_bind_frozen_transaction_settings_injects_snapshot_and_dependency(tmp_path):
    snap_dir = tmp_path / "snapshot"
    raw_dir = snap_dir / "espn"
    raw_dir.mkdir(parents=True)
    raw_path = raw_dir / "espn_league_raw.json"
    raw_path.write_text(
        """{"settings":{"tradeSettings":{"revisionHours":48},"rosterSettings":{"lineupLocktimeType":"INDIVIDUAL_GAME","rosterLocktimeType":"INDIVIDUAL_GAME"},"acquisitionSettings":{"transactionLockingEnabled":false}}}""",
        encoding="utf-8",
    )
    snapshot_path = snap_dir / "snapshot.json"
    snapshot_path.write_text("{}", encoding="utf-8")
    snapshot = {"espn": {}}
    dep = _bind_frozen_transaction_settings(
        snapshot, snapshot_path, "2026-09-22T14:10:51+00:00"
    )
    assert snapshot["espn"]["transaction_settings"]["trade_review_hours"] == 48
    assert dep.status == "FROZEN"
    assert dep.channel == "transaction_timing"
    assert dep.sha256


def test_overlay_enriched_row_uses_frozen_capture_values():
    row = {"espn_id": 1, "projection_points": 999.0}
    _overlay_enriched_row(row, _player_record())
    assert row["latent_mean_ppg"] == 11.0
    assert row["season_ppg"] == 11.0
    assert row["projection_points"] == 12.0
    assert row["latent_mean_sd_ppg"] == 2.0
    assert row["predictive_weekly_sd_ppg"] == 7.0
    assert row["active_probability"] == 0.8
    assert row["expected_workload_given_active"] == 0.7


def test_zero_valued_frozen_prediction_is_valid_and_not_reconstructed():
    record = _player_record(4259619)
    record["model_mean_ppg"] = None
    record["pre_matchup_mean_ppg"] = 0.0
    record["operational_mean_ppg"] = 0.0
    record["predictive_sd_ppg"] = 0.0
    record["game_sd_ppg"] = 0.0
    record["model_sd_ppg"] = 0.0
    record["kinematic_sd_ppg"] = 0.0
    record["interaction_sd_ppg"] = 0.0

    assert _captured_base_mean(record) == 0.0

    row = {
        "espn_id": 4259619,
        "projection_points": 99.0,
        "latent_mean_ppg": 88.0,
        "season_ppg": 77.0,
    }
    _overlay_enriched_row(row, record)
    assert row["latent_mean_ppg"] == 0.0
    assert row["season_ppg"] == 0.0
    assert row["projection_points"] == 0.0
    assert row["predictive_weekly_sd_ppg"] == 0.0

    state = _frozen_yield_state(row, record, 3)
    assert state.operational_mean_ppg == 0.0
    assert state.predictive_sd_ppg == 0.0
    assert state.projection_source == "FROZEN_WEEK3_CAPTURE"


def test_frozen_yield_state_preserves_captured_current_week_coordinates():
    state = _frozen_yield_state(
        {"espn_id": 1, "position": "WR"},
        _player_record(),
        3,
    )
    assert state.week == 3
    assert state.operational_mean_ppg == 12.0
    assert state.model_mean_ppg == 11.0
    assert state.predictive_sd_ppg == 7.0
    assert state.interaction_delta_ppg == 0.2
    assert state.projection_source == "FROZEN_WEEK3_CAPTURE"


def test_frozen_availability_state_preserves_capture_probabilities():
    state = _frozen_availability_state(_player_record())
    assert state is not None
    assert state.p_active == 0.8
    assert state.p_full == 0.6
    assert state.p_limited == 0.2
    assert state.p_out == 0.2
    assert state.practice_sequence == ("LIMITED", "FULL")


def test_overlay_context_restores_transaction_manager_hooks():
    from src import transaction_manager as tm

    original_enrich = tm.enrich_season_values
    original_yield = tm.UtilityContext.yield_state
    fake_state = SimpleNamespace(
        rostered_player_predictions={1: _player_record()},
        owned_specialist_predictions={-16008: _specialist_record()},
        actionable_specialist_predictions={},
        metadata={"player_value_source_contract": "TEST"},
    )
    with frozen_week3_authority_overlay(fake_state) as meta:
        assert tm.enrich_season_values is not original_enrich
        assert tm.UtilityContext.yield_state is not original_yield
        assert meta["frozen_rostered_player_count"] == 1
        assert meta["frozen_specialist_count"] == 1
    assert tm.enrich_season_values is original_enrich
    assert tm.UtilityContext.yield_state is original_yield


def test_candidate_normalizers_keep_channel_local_authorization():
    lineup = _lineup_candidates({
        "action_required": True,
        "lineup_legality_complete": True,
        "lineup_legality_gaps": [],
        "selected_espn_ids": [1],
        "current_starter_espn_ids": [2],
    })
    assert lineup[0]["authorized"] is True

    player = _player_candidates({
        "free_agent_actions": [],
        "waiver_actions": [{
            "add_espn_id": 3,
            "drop_espn_id": 4,
            "combined_action_classification": "ACTIONABLE_EDGE",
            "p_utility_better_if_acquired": 0.7,
        }],
    })
    assert player[0]["authorized"] is True
    assert player[-1]["prediction"]["action"] == "HOLD"

    one, multi = _trade_candidates([
        {"package_family": "1x1", "classification": "ACTIONABLE_OFFER"},
        {"package_family": "1x2", "classification": "NO_RESOLVED_EDGE"},
    ])
    assert one[0]["authorized"] is True
    assert multi[0]["authorized"] is False


def test_ir_and_specialist_trade_frontiers_include_explicit_hold():
    ir = _ir_candidates({
        "coverage_complete": True,
        "candidate_rows": [{
            "add_espn_id": 10,
            "classification": "ACTIONABLE_EDGE",
            "expected_complete_state_delta_mean": 0.2,
        }],
        "recommended_action": {
            "add": {"add_espn_id": 10},
        },
    })
    assert ir[0]["authorized"] is True
    assert ir[-1]["prediction"]["action"] == "HOLD"

    specialist = _specialist_trade_candidates([])
    assert len(specialist) == 1
    assert specialist[0]["prediction"]["action"] == "HOLD"


def test_freeze_candidates_uses_per_channel_selection_not_global_ranking():
    candidates = {}
    for family in ACTION_FAMILY_ORDER:
        candidates[family] = [{
            "candidate_id": f"{family}:hold",
            "action_family": family,
            "prediction": {
                "channel_rank": 1,
                "rank_scope": "CHANNEL_LOCAL",
                "authorized_by_weekly_authority": False,
                "action": "HOLD",
            },
            "uncertainty": {},
            "authorized": False,
        }]
    candidates[PLAYER].insert(0, {
        "candidate_id": f"{PLAYER}:action",
        "action_family": PLAYER,
        "prediction": {
            "channel_rank": 1,
            "rank_scope": "CHANNEL_LOCAL",
            "authorized_by_weekly_authority": True,
            "action": "ADD_DROP",
        },
        "uncertainty": {},
        "authorized": True,
    })
    frozen, selections, model_action = _freeze_candidates_and_selection(candidates)
    assert [row.rank for row in frozen] == list(range(1, len(frozen) + 1))
    player_selection = next(
        row for row in selections if row["action_family"] == PLAYER
    )
    assert player_selection["status"] == "PASS / ACTION"
    assert player_selection["candidate_ids"] == [f"{PLAYER}:action"]
    assert "NO_CROSS_CHANNEL_ASSET_RANKING" in model_action["selection_semantics"]


def test_week3_phase_a_evaluation_verify_requires_complete_family_coverage():
    deps = [
        DependencyProvenance(
            key="snapshot",
            channel="state",
            status="FROZEN",
        ),
        DependencyProvenance(
            key="market",
            channel="player",
            status="RECONSTRUCTED",
        ),
    ]
    candidates = []
    rank = 1
    selections = []
    for family in ACTION_FAMILY_ORDER:
        cid = f"{family}:hold"
        candidates.append({
            "candidate_id": cid,
            "action_family": family,
            "rank": rank,
            "prediction": {
                "channel_rank": 1,
                "action": "HOLD",
            },
            "uncertainty": {},
        })
        selections.append({
            "action_family": family,
            "status": f"PASS / HOLD:{family}",
            "candidate_ids": [cid],
        })
        rank += 1
    receipt = freeze_phase_a_receipt(
        frozen_utc="2026-10-05T00:00:00+00:00",
        season=2026,
        week=3,
        dependencies=deps,
        engine_identities={"test": True},
        candidates=candidates,
        model_action={
            "selection_semantics": "PER_CHANNEL",
            "channel_selections": selections,
            "authorized_candidate_ids": [],
        },
        metadata={},
    )
    result = Week3PhaseAEvaluation(
        contract=WEEK3_PHASE_A_EVALUATOR_CONTRACT,
        receipt=receipt,
        coverage={
            "required_action_families": list(ACTION_FAMILY_ORDER),
            "coverage_complete": True,
        },
        channel_selections=tuple(selections),
        metadata={},
    )
    result.verify()
    assert result.receipt.replay_mode == "RECONSTRUCTED_RETROSPECTIVE_REPLAY"


def test_coverage_fails_closed_on_lineup_or_specialist_waiver_gap():
    reports = {
        LINEUP: {
            "lineup_legality_complete": False,
            "lineup_legality_gaps": ["x"],
        },
        PLAYER: {},
        DST: {"one_slot_policy": {"current_waiver_coverage_complete": True}},
        KICKER: {"one_slot_policy": {"current_waiver_coverage_complete": False}},
        IR: {"coverage_complete": True},
    }
    candidates = {family: [{"x": 1}] for family in ACTION_FAMILY_ORDER}
    coverage = _coverage(reports, candidates)
    assert coverage["coverage_complete"] is False
