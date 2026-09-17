from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from fantasy import build_parser
from src.closure import (
    build_closure_ledger,
    observed_components,
    observed_fantasy_points,
    summarize_closure_ledger,
)
from src.data_sources import nflverse


def _write_capture(root: Path, *, stamp: str, captured: str, base: float, corrected: float) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "model_version": "0.29",
        "captured_utc": captured,
        "snapshot_utc": "2026-09-01T00:00:00+00:00",
        "season": 2026,
        "week": 1,
        "players": [
            {
                "side": "US",
                "espn_id": 1,
                "gsis_id": "00-TEST",
                "name": "Example Receiver",
                "position": "WR",
                "nfl_team": "AAA",
                "matchup_opponent": "BBB",
                "kickoff_utc": "2026-09-10T20:00:00+00:00",
                "base_mc_mean_ppg": base,
                "interaction_corrected_mean_ppg": corrected,
                "predictive_sd_ppg": 4.0,
                "p_active": 0.9,
                "p_full_given_active": 0.8,
                "component_predictions": {
                    "targets": {"base": 8.0, "corrected": 8.0, "correction": 1.0, "commissioned": False},
                    "catch_rate": {"base": 0.60, "corrected": 0.66, "correction": 1.10, "commissioned": True},
                    "receiving_yards_per_target": {"base": 8.0, "corrected": 8.0, "correction": 1.0, "commissioned": False},
                },
            }
        ],
    }
    path = root / f"pregame_2026_w01_{stamp}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_stats(path: Path, *, active=None) -> Path:
    row = {
        "season": 2026,
        "week": 1,
        "season_type": "REG",
        "player_id": "00-TEST",
        "position": "WR",
        "targets": 10,
        "receptions": 7,
        "receiving_yards": 90,
        "receiving_tds": 1,
        "carries": 0,
        "rushing_yards": 0,
        "rushing_tds": 0,
        "attempts": 0,
        "passing_yards": 0,
        "passing_tds": 0,
        "passing_interceptions": 0,
    }
    if active is not None:
        row["active"] = active
    pd.DataFrame([row]).to_csv(path, index=False)
    return path


def test_observed_component_and_fantasy_mapping_is_stat_based_only():
    row = {
        "targets": 10,
        "receptions": 7,
        "receiving_yards": 90,
        "receiving_tds": 1,
    }
    comp = observed_components(row, "WR")
    assert comp == {
        "targets": 10.0,
        "catch_rate": pytest.approx(0.7),
        "receiving_yards_per_target": pytest.approx(9.0),
    }
    # 7 receptions + 9 receiving-yard points + 6 TD points.
    assert observed_fantasy_points(row, "WR") == pytest.approx(22.0)


def test_closure_uses_latest_capture_before_player_kickoff_and_rejects_postlock(tmp_path: Path):
    pred = tmp_path / "pred"
    _write_capture(pred, stamp="a", captured="2026-09-10T15:00:00+00:00", base=9.0, corrected=10.0)
    _write_capture(pred, stamp="b", captured="2026-09-10T19:00:00+00:00", base=10.0, corrected=11.0)
    _write_capture(pred, stamp="c", captured="2026-09-10T21:00:00+00:00", base=99.0, corrected=99.0)
    stats = _write_stats(tmp_path / "stats.csv")

    ledger = build_closure_ledger(prediction_dir=pred, stats_by_season={2026: stats})
    fantasy = ledger[ledger["row_type"].eq("FANTASY_YIELD")].iloc[0]
    assert fantasy["base_mc"] == pytest.approx(10.0)
    assert fantasy["corrected_mc"] == pytest.approx(11.0)
    assert fantasy["observed"] == pytest.approx(22.0)
    assert fantasy["pull"] == pytest.approx((22.0 - 11.0) / 4.0)
    catch = ledger[(ledger["row_type"].eq("COMPONENT")) & (ledger["component"].eq("catch_rate"))].iloc[0]
    assert catch["base_mc"] == pytest.approx(0.60)
    assert catch["corrected_mc"] == pytest.approx(0.66)
    assert catch["observed"] == pytest.approx(0.70)


def test_missing_stats_row_is_not_silently_treated_as_inactive(tmp_path: Path):
    pred = tmp_path / "pred"
    _write_capture(pred, stamp="a", captured="2026-09-10T15:00:00+00:00", base=9.0, corrected=10.0)
    stats = tmp_path / "stats.csv"
    pd.DataFrame([{
        "season": 2026, "week": 1, "season_type": "REG", "player_id": "OTHER", "position": "WR"
    }]).to_csv(stats, index=False)
    ledger = build_closure_ledger(prediction_dir=pred, stats_by_season={2026: stats})
    fantasy = ledger[ledger["row_type"].eq("FANTASY_YIELD")].iloc[0]
    assert bool(fantasy["observed_stat_row"]) is False
    assert pd.isna(fantasy["observed_active"])
    summary = summarize_closure_ledger(ledger)
    assert summary["availability"]["n"] == 0
    assert summary["availability"]["brier"] is None


def test_closure_summary_reports_base_corrected_and_pull_calibration(tmp_path: Path):
    pred = tmp_path / "pred"
    _write_capture(pred, stamp="a", captured="2026-09-10T15:00:00+00:00", base=10.0, corrected=11.0)
    stats = _write_stats(tmp_path / "stats.csv", active=True)
    ledger = build_closure_ledger(prediction_dir=pred, stats_by_season={2026: stats})
    summary = summarize_closure_ledger(ledger)
    fantasy = summary["fantasy"]
    assert fantasy["n"] == 1
    assert fantasy["rmse"] == pytest.approx(11.0)
    assert fantasy["base_rmse"] == pytest.approx(12.0)
    assert fantasy["interaction_rmse_improvement"] == pytest.approx(1.0)
    assert summary["pull"]["mean"] == pytest.approx(2.75)
    assert summary["availability"]["n"] == 1
    assert summary["availability"]["brier"] == pytest.approx(0.01)


def test_weekly_stats_sync_does_not_rewrite_historical_aggregate(monkeypatch, tmp_path: Path):
    calls = []

    def fake_download(url, path, force=False):
        calls.append((url, Path(path), force))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("season,week,player_id\n2026,1,x\n", encoding="utf-8")
        return Path(path)

    monkeypatch.setattr(nflverse, "_download", fake_download)
    path = nflverse.sync_weekly_player_stats(tmp_path, season=2026, force=True)
    assert path.name == "stats_player_week_2026.csv"
    assert "stats_player_week_2026.csv" in calls[0][0]
    assert calls[0][2] is True


def test_closure_cli_commands_are_available_and_windows_safe():
    capture = build_parser().parse_args(["closure-capture"])
    update = build_parser().parse_args(["closure-update"])
    status = build_parser().parse_args(["closure-status"])
    assert Path(capture.out).parts[-2:] == ("season_predictions", "closure")
    assert Path(update.out).parts[-1:] == ("season_closure",)
    assert Path(status.ledger).parts[-2:] == ("season_closure", "ledger.csv")


def test_closure_prefers_availability_marginal_yield_and_count_predictions(tmp_path: Path):
    pred = tmp_path / "pred"
    path = _write_capture(pred, stamp="a", captured="2026-09-10T15:00:00+00:00", base=20.0, corrected=22.0)
    payload = json.loads(path.read_text(encoding="utf-8"))
    player = payload["players"][0]
    player["availability_marginal_base_mc_mean_ppg"] = 12.0
    player["availability_marginal_corrected_mean_ppg"] = 13.2
    player["availability_marginal_corrected_sd_ppg"] = 6.0
    player["component_predictions"]["targets"]["closure_base"] = 4.8
    player["component_predictions"]["targets"]["closure_corrected"] = 4.8
    path.write_text(json.dumps(payload), encoding="utf-8")
    stats = _write_stats(tmp_path / "stats.csv")
    ledger = build_closure_ledger(prediction_dir=pred, stats_by_season={2026: stats})
    fantasy = ledger[ledger["row_type"].eq("FANTASY_YIELD")].iloc[0]
    assert fantasy["base_mc"] == pytest.approx(12.0)
    assert fantasy["corrected_mc"] == pytest.approx(13.2)
    assert fantasy["pull"] == pytest.approx((22.0 - 13.2) / 6.0)
    targets = ledger[(ledger["row_type"].eq("COMPONENT")) & ledger["component"].eq("targets")].iloc[0]
    assert targets["base_mc"] == pytest.approx(4.8)
    assert targets["corrected_mc"] == pytest.approx(4.8)


def test_gui_service_capture_uses_exact_in_memory_state(tmp_path: Path):
    from test_season_gui_service_v024 import _build_runtime

    service = _build_runtime(tmp_path)
    out = tmp_path / "captures"
    result = service.capture_pregame_closure(out)
    path = Path(result["path"])
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["model_version"] == "0.36"
    assert payload["measurement_contract"] == "A_PRIORI_PRE_DATA_PROSPECTIVE_CAPTURE_V034"
    assert payload["pre_data_firewall"]["2026_game_outcomes_used_for_tuning"] is False
    assert payload["snapshot_utc"] == service.snapshot["snapshot_utc"]
    assert payload["mc_scenarios"] == service.mc_scenarios
    assert len(payload["players"]) == len(service.ctx.roster) + len(service.ctx.all_team_rosters[2])
    player = payload["players"][0]
    assert "availability_marginal_corrected_mean_ppg" in player
    assert "availability_marginal_corrected_sd_ppg" in player


def test_v029_gui_exposes_capture_and_component_closure_controls():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    assert "Capture Pregame State" in source
    assert "Prospective component closure" in source
    assert "component_closure_summary_rows" in source
