import json
from pathlib import Path

import pandas as pd
import pytest

from src.gui.season_service import CANONICAL_SLOTS, SeasonGuiError, SeasonGuiService
from src.transaction_manager import evaluate_roster_predictive


def _player(pid, name, pos, team, proj, *, status="ACTIVE", fantasy_status=None, slot="BENCH"):
    row = {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": team,
        "pro_team_id": 1,
        "weekly_projection": proj,
        "season_projection": proj * 17,
        "injury_status": status,
        "lineup_slot": slot,
        "droppable": True,
        "lineup_locked": False,
        "official_roster_status": "ACT",
        "official_roster_team": team,
    }
    if fantasy_status:
        row["fantasy_status"] = fantasy_status
    return row


def _build_runtime(tmp_path: Path) -> SeasonGuiService:
    cfg = tmp_path / "config"
    data = tmp_path / "data"
    processed = data / "processed"
    snapshots = data / "season_snapshots"
    cfg.mkdir(parents=True)
    processed.mkdir(parents=True)
    snapshots.mkdir(parents=True)

    league = {
        "teams": 2,
        "user_team_name": "Us",
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1, "BENCH": 3, "IR": 1},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "bye_weeks_2026": {},
        "fantasy_season": {"regular_season_weeks": list(range(1, 14)), "playoff_week_participation_prior": {"14": .5, "15": .5, "16": .3, "17": .3}},
    }
    model = {
        "weekly_manager": {"status_active_probability": {"ACTIVE": .995, "QUESTIONABLE": .75, "OUT": 0.0}},
        "weekly_yield": {
            "espn_week_anchor_weight": .35,
            "espn_season_anchor_weight": .15,
            "minimum_game_sd_ppg": 1.0,
            "minimum_model_sd_ppg": .25,
        },
        "matchup_model": {"kinematic_fractional_sd": .035, "early_season_extra_fractional_sd": .02, "dst": {"component_anchor_weight": .55}},
        "transaction_manager": {
            "availability_scenarios": 4,
            "predictive_mc_scenarios": 16,
            "random_seed": 12345,
            "h2h_matchup_scale_points": 18.0,
            "paired_mean_interval_resamples": 100,
            "candidate_limit": 20,
            "candidate_floor_per_position": 2,
            "actionable_probability_threshold": .9,
            "possible_probability_threshold": .65,
            "waiver_p_acquire_default": .35,
            "waiver_p_acquire_floor": .02,
        },
    }
    (cfg / "league.json").write_text(json.dumps(league))
    (cfg / "model.json").write_text(json.dumps(model))

    positions = ["QB", "RB", "RB", "RB", "WR", "WR", "WR", "TE", "TE", "K", "DST"]
    user = []
    opp = []
    vals = []
    for idx, pos in enumerate(positions, 1):
        proj = 20 - 0.8 * idx if pos not in {"K", "DST"} else 8 - 0.2 * idx
        status = "QUESTIONABLE" if idx == 2 else "ACTIVE"
        user.append(_player(idx, f"User {idx}", pos, "AAA", proj, status=status))
        opp.append(_player(100 + idx, f"Opp {idx}", pos, "BBB", proj - 1.0))
        vals.append({"espn_id": idx, "latent_mean_ppg": proj + .5, "latent_mean_sd_ppg": 1.2, "predictive_weekly_sd_ppg": 6.0})
        vals.append({"espn_id": 100 + idx, "latent_mean_ppg": proj - .5, "latent_mean_sd_ppg": 1.2, "predictive_weekly_sd_ppg": 6.0})

    add = _player(201, "Available WR", "WR", "CCC", 12.0, fantasy_status="FREEAGENT")
    vals.append({"espn_id": 201, "latent_mean_ppg": 12.5, "latent_mean_sd_ppg": 1.4, "predictive_weekly_sd_ppg": 6.5})
    pd.DataFrame(vals).to_csv(processed / "player_values_2026.csv", index=False)

    snapshot = {
        "snapshot_utc": "2026-08-31T12:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 1,
            "league_name": "Test",
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": 2, "roster": user},
                {"team_id": 2, "name": "Them", "waiver_rank": 1, "roster": opp},
            ],
            "available_players": [add],
            "matchups": [{"home_team_id": 1, "away_team_id": 2}],
        },
        "matchup_context": {},
        "source_status": {"sleeper": {"ok": True}, "nflverse_rosters": {"ok": True}, "nflverse_matchups": {"ok": True}},
    }
    (snapshots / "latest.json").write_text(json.dumps(snapshot))

    return SeasonGuiService(
        snapshot_path=snapshots / "latest.json",
        league_path=cfg / "league.json",
        model_path=cfg / "model.json",
        values_path=processed / "player_values_2026.csv",
        snapshots_dir=snapshots,
    )


def test_dashboard_uses_same_predictive_baseline_as_core(tmp_path: Path):
    service = _build_runtime(tmp_path)
    dashboard = service.dashboard_state()
    assert len(dashboard["planning_lineup"]) == 9
    assert 0 <= dashboard["weekly_win_probability"] <= 1
    baseline, _, _ = evaluate_roster_predictive(service.ctx.roster, service.ctx)
    assert dashboard["baseline"]["expected_h2h_win_probability"] == pytest.approx(baseline.expected_h2h_win_probability)


def test_hypothetical_lineup_and_availability_modes(tmp_path: Path):
    service = _build_runtime(tmp_path)
    selection = service.default_lineup_selection()
    assert set(selection) == set(CANONICAL_SLOTS)
    result_model = service.evaluate_hypothetical_lineup(selection)
    qid = 2
    result_full = service.evaluate_hypothetical_lineup(selection, availability_modes={qid: "FULL"})
    assert 0 <= result_model["win_probability"] <= 1
    assert result_full["team"]["mean"] >= result_model["team"]["mean"]
    with pytest.raises(SeasonGuiError):
        broken = dict(selection)
        broken["RB2"] = broken["RB1"]
        service.evaluate_hypothetical_lineup(broken)


def test_player_diagnostic_and_single_action_are_model_backed(tmp_path: Path):
    service = _build_runtime(tmp_path)
    diag = service.player_diagnostic(1)
    assert diag["operational_mean"] > 0
    assert "kinematic_components" in diag
    drops = service.legal_drop_players()
    drop = next(r for r in drops if r["position"] == "WR")
    result = service.evaluate_single_add_drop(201, int(drop["espn_id"]))
    assert result["p_acquire"] == pytest.approx(1.0)
    assert result["mc_scenarios"] == 16
    assert result["classification"] in {"ACTIONABLE_EDGE", "POSSIBLE_EDGE", "NO_RESOLVED_EDGE"}
    assert len(result["utility_delta_distribution"]["histogram"]) > 0


def test_v025_dashboard_exposes_fixed_lineup_and_slot_diagnostics(tmp_path: Path):
    service = _build_runtime(tmp_path)
    dashboard = service.dashboard_state()
    assert dashboard["fixed_planning_win_probability"] is not None
    assert len(dashboard["matchup_slot_deltas"]) == 9
    assert dashboard["contingency_policy_value"] == pytest.approx(
        dashboard["weekly_win_probability"] - dashboard["fixed_planning_win_probability"]
    )


def test_v025_lineup_lab_separates_fixed_and_contingent_baselines(tmp_path: Path):
    service = _build_runtime(tmp_path)
    selection = service.default_lineup_selection()
    result = service.evaluate_hypothetical_lineup(selection)
    assert result["delta_vs_fixed_win_probability"] == pytest.approx(0.0)
    assert result["win_probability"] == pytest.approx(result["fixed_baseline_win_probability"])
    assert result["contingency_policy_value"] == pytest.approx(
        result["policy_baseline_win_probability"] - result["fixed_baseline_win_probability"]
    )
    assert len(result["changes"]) == 9
    assert not any(row["changed"] for row in result["changes"])


def test_v025_lineup_lab_tracks_player_or_availability_changes(tmp_path: Path):
    service = _build_runtime(tmp_path)
    selection = service.default_lineup_selection()
    selected_id = int(selection["RB1"])
    result = service.evaluate_hypothetical_lineup(selection, availability_modes={selected_id: "OUT"})
    changed = [row for row in result["changes"] if row["changed"]]
    assert changed
    assert any(row["selected_espn_id"] == selected_id and row["mode"] == "OUT" for row in changed)
    assert result["delta_vs_fixed_win_probability"] <= 0


def test_v025_action_exposes_absolute_hold_and_action_distributions(tmp_path: Path):
    service = _build_runtime(tmp_path)
    drop = next(r for r in service.legal_drop_players() if r["position"] == "WR")
    result = service.evaluate_single_add_drop(201, int(drop["espn_id"]))
    assert "baseline_utility" in result
    assert "action_utility" in result
    assert len(result["baseline_week_distribution"]["histogram"]) > 0
    assert len(result["action_week_distribution"]["histogram"]) > 0
    assert result["action_week_distribution"]["mean"] - result["baseline_week_distribution"]["mean"] == pytest.approx(
        result["week_delta"]
    )


def test_v025_prediction_ledger_summary_reports_anchor_coverage(tmp_path: Path):
    service = _build_runtime(tmp_path)
    summary = service.prediction_ledger_summary()
    assert summary["players"] == len(service.roster_players())
    assert summary["anchor_coverage"] > 0
    assert summary["observed_coverage"] == 0
    assert summary["mean_abs_model_minus_espn"] is not None


def test_v026_dashboard_separates_status_timing_and_workload_information(tmp_path: Path):
    service = _build_runtime(tmp_path)
    dashboard = service.dashboard_state()
    assert "idealized_active_policy_win_probability" in dashboard
    assert dashboard["information_timing_inflation"] == pytest.approx(
        dashboard["status_timing_inflation"] + dashboard["workload_information_inflation"]
    )
    # This fixture intentionally has no kickoff schedule, so the realistic policy
    # uses the documented active/inactive-known fallback with workload still latent.
    assert dashboard["policy_timing_fallback"] is True
    assert dashboard["realistic_policy_win_probability"] == pytest.approx(
        dashboard["idealized_active_policy_win_probability"]
    )
