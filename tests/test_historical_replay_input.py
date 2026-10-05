from __future__ import annotations

import csv
import hashlib
import json

import pytest

import src.historical_replay_input as replay_input
from src.counterfactual_replay import RECONSTRUCTED_RETROSPECTIVE_REPLAY
from src.historical_replay_input import ReplayInputError, build_week3_replay_input


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _write_values(path, player_ids):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "espn_id",
        "latent_mean_ppg",
        "latent_mean_sd_ppg",
        "predictive_weekly_sd_ppg",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for pid in player_ids:
            writer.writerow(
                {
                    "espn_id": pid,
                    "latent_mean_ppg": 10.0,
                    "latent_mean_sd_ppg": 1.0,
                    "predictive_weekly_sd_ppg": 3.0,
                }
            )


def _fixture(tmp_path):
    league = {"roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1}}
    model = {"transaction_manager": {"random_seed": 7}}

    player_roster = [
        {
            "espn_id": pid,
            "name": f"P{pid}",
            "position": ("QB", "RB", "WR", "TE")[(pid - 1) % 4],
            "nfl_team": "BUF",
            "pro_team_id": 2,
            "lineup_slot": "BENCH",
        }
        for pid in range(1, 175)
    ]
    owned_specialists = [
        {
            "espn_id": 1000 + i,
            "name": f"S{i}",
            "position": "DST" if i % 2 else "K",
            "nfl_team": "BUF",
            "pro_team_id": 2,
            "lineup_slot": "BENCH",
        }
        for i in range(1, 25)
    ]
    teams = []
    assets = player_roster + owned_specialists
    for team_id in range(1, 13):
        teams.append(
            {
                "team_id": team_id,
                "name": f"T{team_id}",
                "roster": [
                    dict(row)
                    for index, row in enumerate(assets)
                    if index % 12 == team_id - 1
                ],
            }
        )

    available_players = [
        {
            "espn_id": 20000 + i,
            "name": f"A{i}",
            "position": ("QB", "RB", "WR", "TE")[i % 4],
            "nfl_team": "BUF",
            "pro_team_id": 2,
            "fantasy_status": "FREEAGENT",
        }
        for i in range(780)
    ]
    available_specialists = []
    for i in range(66):
        eligible = i < 40
        available_specialists.append(
            {
                "espn_id": 30000 + i,
                "name": f"AS{i}",
                "position": "DST" if i % 2 else "K",
                "nfl_team": "BUF" if eligible else "FA",
                "pro_team_id": 2 if eligible else 0,
                "fantasy_status": "WAIVERS" if i % 3 == 0 else "FREEAGENT",
            }
        )

    snapshot = {
        "snapshot_utc": "2026-09-24T15:51:01+00:00",
        "espn": {
            "season": 2026,
            "week": 3,
            "snapshot_utc": "2026-09-24T15:51:01+00:00",
            "teams": teams,
            "available_players": available_players + available_specialists,
            "transactions": [],
        },
    }

    player_predictions = [
        {
            "espn_id": row["espn_id"],
            "position": row["position"],
            "operational_mean_ppg": 10.0,
            "predictive_sd_ppg": 3.0,
        }
        for row in player_roster
    ]
    owned_predictions = [
        {
            "espn_id": row["espn_id"],
            "position": row["position"],
            "owner_team_id": next(
                team["team_id"]
                for team in teams
                if row["espn_id"] in {
                    x["espn_id"] for x in team["roster"]
                }
            ),
            "market_state": "OWNED",
            "operational_mean_ppg": 8.0,
            "predictive_sd_ppg": 2.0,
        }
        for row in owned_specialists
    ]
    market_predictions = [
        {
            "espn_id": row["espn_id"],
            "position": row["position"],
            "owner_team_id": None,
            "market_state": row["fantasy_status"],
            "operational_mean_ppg": 7.0,
            "predictive_sd_ppg": 2.0,
        }
        for row in available_specialists[:40]
    ]
    compact_market = [
        {
            "espn_id": row["espn_id"],
            "name": row["name"],
            "position": row["position"],
            "nfl_team": row["nfl_team"],
            "fantasy_status": row["fantasy_status"],
        }
        for row in available_players + available_specialists
    ]

    capture = {
        "season": 2026,
        "week": 3,
        "captured_utc": "2026-09-24T15:51:02+00:00",
        "snapshot_utc": snapshot["snapshot_utc"],
        "measurement_contract": "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034",
        "league_player_predictions": {
            "count": 174,
            "records": player_predictions,
        },
        "specialist_predictions": {
            "records": owned_predictions + market_predictions,
        },
        "behavioral_observation_state": {
            "snapshot_sha256": replay_input.canonical_json_sha256(snapshot),
            "captured_from_snapshot_utc": snapshot["snapshot_utc"],
            "league_config_sha256": replay_input.canonical_json_sha256(league),
            "model_config_sha256": replay_input.canonical_json_sha256(model),
            "market_players": compact_market,
            "teams": [],
        },
        "pre_data_firewall": {
            "2026_game_outcomes_used_for_tuning": False,
            "automatic_refit": False,
            "automatic_calibration": False,
        },
    }
    capture["integrity"] = {
        "canonical_payload_sha256": replay_input.canonical_json_sha256(capture)
    }

    snapshot_path = tmp_path / "snapshot.json"
    capture_path = tmp_path / "pregame_2026_w03.json"
    league_path = tmp_path / "league.json"
    model_path = tmp_path / "model.json"
    values_path = tmp_path / "player_values_2026.csv"
    _write_json(snapshot_path, snapshot)
    _write_json(capture_path, capture)
    _write_json(league_path, league)
    _write_json(model_path, model)
    _write_values(values_path, [row["espn_id"] for row in available_players])

    values_sha = hashlib.sha256(values_path.read_bytes()).hexdigest()
    return {
        "snapshot": snapshot,
        "capture": capture,
        "league": league,
        "model": model,
        "snapshot_path": snapshot_path,
        "capture_path": capture_path,
        "league_path": league_path,
        "model_path": model_path,
        "values_path": values_path,
        "values_sha": values_sha,
    }


def _build(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(
        replay_input,
        "WEEK3_RECONSTRUCTED_VALUES_SHA256",
        fx["values_sha"],
    )
    state = build_week3_replay_input(
        snapshot_path=fx["snapshot_path"],
        capture_path=fx["capture_path"],
        league_path=fx["league_path"],
        model_path=fx["model_path"],
        values_path=fx["values_path"],
    )
    return fx, state


def test_week3_adapter_builds_exact_mixed_provenance_state(tmp_path, monkeypatch):
    _fx, state = _build(tmp_path, monkeypatch)
    summary = state.summary()
    assert state.replay_mode == RECONSTRUCTED_RETROSPECTIVE_REPLAY
    assert summary["reconstructed_dependencies"] == [
        "player_waiver_free_agent:player_values_for_available_market"
    ]
    assert summary["missing_dependencies"] == []
    assert summary["counts"]["rostered_player_predictions"] == 174
    assert summary["counts"]["owned_specialist_predictions"] == 24
    assert summary["counts"]["actionable_specialist_predictions"] == 40
    assert summary["counts"]["actionable_player_ids"] == 780
    assert state.metadata["outcomes_available_to_adapter"] is False


def test_week3_adapter_allows_commissioned_snapshot_projection_fallback_for_missing_values(
    tmp_path, monkeypatch
):
    fx = _fixture(tmp_path)
    fallback_ids = list(range(20000, 20012))
    covered_ids = list(range(20012, 20780))
    _write_values(fx["values_path"], covered_ids)
    sha = hashlib.sha256(fx["values_path"].read_bytes()).hexdigest()
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", sha)

    state = build_week3_replay_input(
        snapshot_path=fx["snapshot_path"],
        capture_path=fx["capture_path"],
        league_path=fx["league_path"],
        model_path=fx["model_path"],
        values_path=fx["values_path"],
    )

    assert state.metadata[
        "snapshot_projection_fallback_actionable_player_ids"
    ] == tuple(fallback_ids)
    assert state.metadata[
        "snapshot_projection_fallback_actionable_player_count"
    ] == len(fallback_ids)
    assert state.metadata["reconstructed_latent_actionable_player_count"] == len(
        covered_ids
    )
    assert state.summary()["counts"][
        "snapshot_projection_fallback_actionable_players"
    ] == len(fallback_ids)


def test_week3_adapter_rejects_capture_integrity_failure(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    payload = json.loads(fx["capture_path"].read_text(encoding="utf-8"))
    payload["integrity"]["canonical_payload_sha256"] = "0" * 64
    _write_json(fx["capture_path"], payload)
    with pytest.raises(ReplayInputError, match="integrity"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_snapshot_link_mismatch(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    snapshot = json.loads(fx["snapshot_path"].read_text(encoding="utf-8"))
    snapshot["espn"]["transactions"].append({"id": 1})
    _write_json(fx["snapshot_path"], snapshot)
    with pytest.raises(ReplayInputError, match="snapshot identity"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_wrong_week(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    snapshot = json.loads(fx["snapshot_path"].read_text(encoding="utf-8"))
    snapshot["espn"]["week"] = 4
    _write_json(fx["snapshot_path"], snapshot)
    with pytest.raises(ReplayInputError, match="not 2026 Week 3"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_missing_rostered_prediction(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    capture = json.loads(fx["capture_path"].read_text(encoding="utf-8"))
    capture["league_player_predictions"]["records"].pop()
    capture["integrity"]["canonical_payload_sha256"] = replay_input.canonical_json_sha256(
        {k: v for k, v in capture.items() if k != "integrity"}
    )
    _write_json(fx["capture_path"], capture)
    with pytest.raises(ReplayInputError, match="coverage mismatch"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_specialist_frontier_mismatch(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    capture = json.loads(fx["capture_path"].read_text(encoding="utf-8"))
    capture["specialist_predictions"]["records"][-1]["espn_id"] = 39999
    capture["integrity"]["canonical_payload_sha256"] = replay_input.canonical_json_sha256(
        {k: v for k, v in capture.items() if k != "integrity"}
    )
    _write_json(fx["capture_path"], capture)
    with pytest.raises(ReplayInputError, match="frontier mismatch"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_values_identity_mismatch(tmp_path):
    fx = _fixture(tmp_path)
    with pytest.raises(ReplayInputError, match="values identity mismatch"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_missing_values_columns(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    with fx["values_path"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["espn_id", "latent_mean_ppg"])
        writer.writeheader()
        for pid in range(20000, 20780):
            writer.writerow({"espn_id": pid, "latent_mean_ppg": 10.0})
    sha = hashlib.sha256(fx["values_path"].read_bytes()).hexdigest()
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", sha)
    with pytest.raises(ReplayInputError, match="missing required fields"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_config_identity_mismatch(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    model = json.loads(fx["model_path"].read_text(encoding="utf-8"))
    model["transaction_manager"]["random_seed"] = 99
    _write_json(fx["model_path"], model)
    with pytest.raises(ReplayInputError, match="model config"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=fx["capture_path"],
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )


def test_week3_adapter_rejects_phase_b_named_capture_path(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    monkeypatch.setattr(replay_input, "WEEK3_RECONSTRUCTED_VALUES_SHA256", fx["values_sha"])
    unsafe = tmp_path / "postgame" / "pregame_2026_w03.json"
    unsafe.parent.mkdir()
    unsafe.write_bytes(fx["capture_path"].read_bytes())
    with pytest.raises(ReplayInputError, match="not Phase-A-safe"):
        build_week3_replay_input(
            snapshot_path=fx["snapshot_path"],
            capture_path=unsafe,
            league_path=fx["league_path"],
            model_path=fx["model_path"],
            values_path=fx["values_path"],
        )
