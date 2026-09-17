import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fantasy import build_parser
from src.interaction_fit import fit_grid
from src.interaction_grid import evaluate_interaction_correction, interpolate_grid
from src.weekly_yield import WeeklyYieldState, sample_conditional_points


def _write_wr_artifact(root: Path) -> None:
    (root / "WR").mkdir(parents=True)
    (root / "manifest.json").write_text(json.dumps({
        "artifact_id": "test_grid_v001",
        "model_version": "0.28",
        "fantasy_points_used_in_fit": False,
    }))
    (root / "player_baselines.json").write_text(json.dumps({"players": {
        "00-TEST": {
            "position": "WR",
            "games": 8,
            "targets": 10.0,
            "catch_rate": 0.60,
            "receiving_yards_per_target": 8.0,
        }
    }}))
    (root / "position_baselines.json").write_text(json.dumps({"positions": {
        "WR": {"targets": 7.0, "catch_rate": 0.60, "receiving_yards_per_target": 7.0}
    }}))
    shape = (2, 2)
    np.savez_compressed(
        root / "WR" / "targets.npz",
        baseline_centers=np.asarray([5.0, 15.0]),
        defense_z_centers=np.asarray([-1.0, 1.0]),
        raw_correction=np.full(shape, 1.10),
        correction=np.full(shape, 1.10),
        uncertainty=np.full(shape, 0.02),
        support=np.full(shape, 100.0),
    )
    (root / "WR" / "targets.json").write_text(json.dumps({
        "position": "WR",
        "component": "targets",
        "defense_feature": "target_share_wr",
        "commissioned": True,
    }))


def test_grid_interpolation_tracks_defensive_interaction():
    rows = pd.DataFrame({
        "baseline": [8.0] * 120 + [12.0] * 120,
        "observed": [7.2] * 60 + [8.8] * 60 + [10.8] * 60 + [13.2] * 60,
        "defense": [-1.0] * 60 + [1.0] * 60 + [-1.0] * 60 + [1.0] * 60,
    })
    grid = fit_grid(
        rows,
        baseline_col="baseline",
        observed_col="observed",
        defense_col="defense",
        baseline_bins=2,
        defense_centers=np.asarray([-1.0, 1.0]),
        shrink_n=1.0,
        ratio_min=0.5,
        ratio_max=1.5,
        uncertainty_floor=0.01,
    )
    low, _, support_low = interpolate_grid(grid, 10.0, -1.0)
    high, _, support_high = interpolate_grid(grid, 10.0, 1.0)
    assert low < 1.0 < high
    assert high - low > 0.10
    assert support_low > 0 and support_high > 0


def test_runtime_grid_is_higher_order_correction_to_base_yield(tmp_path: Path):
    root = tmp_path / "grid"
    _write_wr_artifact(root)
    model = {
        "interaction_grid": {
            "enabled": True,
            "artifact_path": str(root),
            "commissioned_only": True,
            "correction_min": 0.75,
            "correction_max": 1.25,
            "yield_factor_min": 0.90,
            "yield_factor_max": 1.10,
            "max_absolute_delta_ppg": 4.0,
        }
    }
    player = {
        "position": "WR",
        "nfl_team": "LAR",
        "nflverse_gsis_id": "00-TEST",
    }
    context = {
        "team_week": {"LAR": {"1": {"opponent": "SF"}}},
        "defense_zscores": {"SF": {"target_share_wr": 0.5}},
    }
    league = {"scoring": {"receiving": {"yards": 0.1, "reception": 1.0}}}
    corr = evaluate_interaction_correction(
        player,
        week=1,
        matchup_context=context,
        model=model,
        league=league,
        reference_points=20.0,
    )
    # Baseline receiving response = 10*.60 receptions + 10*8*.1 yards = 14.
    # A +10% target correction adds 1.4 downstream points.
    assert np.isclose(corr.delta_points, 1.4)
    assert np.isclose(corr.factor, 1.07)
    assert corr.source == "DATA_MC_INTERACTION_GRID_V028"
    assert corr.baseline_source == "PLAYER_HISTORY"
    assert corr.components["targets"].commissioned is True
    assert corr.support == 100.0
    assert corr.uncertainty_ppg > 0.0


def test_missing_grid_is_exactly_neutral(tmp_path: Path):
    model = {"interaction_grid": {"enabled": True, "artifact_path": str(tmp_path / "missing")}}
    corr = evaluate_interaction_correction(
        {"position": "QB", "nfl_team": "BAL"},
        week=1,
        matchup_context={},
        model=model,
        league={},
        reference_points=20.0,
    )
    assert corr.factor == 1.0
    assert corr.delta_points == 0.0
    assert corr.uncertainty_ppg == 0.0
    assert corr.source == "INTERACTION_GRID_MISSING"


def test_shadow_grid_is_neutral_in_mean_and_operational_variance(tmp_path: Path):
    root = tmp_path / "grid"
    _write_wr_artifact(root)
    meta_path = root / "WR" / "targets.json"
    meta = json.loads(meta_path.read_text())
    meta["commissioned"] = False
    meta_path.write_text(json.dumps(meta))

    model = {
        "interaction_grid": {
            "enabled": True,
            "artifact_path": str(root),
            "commissioned_only": True,
            "correction_min": 0.75,
            "correction_max": 1.25,
            "yield_factor_min": 0.90,
            "yield_factor_max": 1.10,
            "max_absolute_delta_ppg": 4.0,
            "uncommissioned_uncertainty_floor": 0.50,
        }
    }
    player = {
        "position": "WR",
        "nfl_team": "LAR",
        "nflverse_gsis_id": "00-TEST",
    }
    context = {
        "team_week": {"LAR": {"1": {"opponent": "SF"}}},
        "defense_zscores": {"SF": {"target_share_wr": 0.5}},
    }
    league = {"scoring": {"receiving": {"yards": 0.1, "reception": 1.0}}}

    corr = evaluate_interaction_correction(
        player,
        week=1,
        matchup_context=context,
        model=model,
        league=league,
        reference_points=20.0,
    )

    assert corr.factor == 1.0
    assert corr.delta_points == 0.0
    assert corr.uncertainty_ppg == 0.0
    assert corr.components["targets"].commissioned is False
    assert corr.components["targets"].correction == 1.0
    assert corr.components["targets"].correction_sd == 0.0


def test_uncommissioned_grid_can_retain_uncertainty_only_in_explicit_exploratory_mode(tmp_path: Path):
    root = tmp_path / "grid"
    _write_wr_artifact(root)
    meta_path = root / "WR" / "targets.json"
    meta = json.loads(meta_path.read_text())
    meta["commissioned"] = False
    meta_path.write_text(json.dumps(meta))

    model = {
        "interaction_grid": {
            "enabled": True,
            "artifact_path": str(root),
            "commissioned_only": False,
            "correction_min": 0.75,
            "correction_max": 1.25,
            "yield_factor_min": 0.90,
            "yield_factor_max": 1.10,
            "max_absolute_delta_ppg": 4.0,
            "uncommissioned_uncertainty_floor": 0.05,
        }
    }
    player = {"position": "WR", "nfl_team": "LAR", "nflverse_gsis_id": "00-TEST"}
    context = {
        "team_week": {"LAR": {"1": {"opponent": "SF"}}},
        "defense_zscores": {"SF": {"target_share_wr": 0.5}},
    }
    league = {"scoring": {"receiving": {"yards": 0.1, "reception": 1.0}}}

    corr = evaluate_interaction_correction(
        player, week=1, matchup_context=context, model=model, league=league, reference_points=20.0
    )
    assert corr.factor > 1.0
    assert corr.delta_points > 0.0
    assert corr.uncertainty_ppg > 0.0
    assert corr.components["targets"].commissioned is False


def test_interaction_uncertainty_has_separate_mc_coordinate():
    state = WeeklyYieldState(
        espn_id=1,
        name="Test",
        position="WR",
        nfl_team="X",
        week=1,
        operational_mean_ppg=10.0,
        pre_matchup_operational_mean_ppg=10.0,
        model_mean_ppg=10.0,
        matchup_model_mean_ppg=10.0,
        espn_anchor_ppg=None,
        espn_anchor_kind=None,
        espn_anchor_weight=0.0,
        espn_anchor_acceptance_specific=False,
        delta_model_minus_espn=None,
        ratio_model_to_espn=None,
        anchor_pull_ppg=0.0,
        game_sd_ppg=0.0,
        model_sd_ppg=0.0,
        kinematic_sd_ppg=0.0,
        interaction_sd_ppg=2.0,
        predictive_sd_ppg=2.0,
        espn_anchor_sigma_ppg=None,
        espn_anchor_z=None,
        availability_probability=1.0,
        kinematic_factor_mean=1.0,
        kinematic_factor_source="neutral",
        interaction_factor_mean=1.0,
        interaction_factor_source="test",
        interaction_delta_ppg=0.0,
        interaction_artifact_id="test",
        interaction_baseline_source="test",
        interaction_support=100.0,
        interaction_components={},
        matchup_opponent=None,
        matchup_home=None,
        matchup_team_implied_points=None,
        matchup_defense_current_weight=0.0,
        kinematic_components={},
        kinematic_zscores={},
        dst_component_expectation=None,
        projection_source="test",
    )
    z = np.asarray([-1.0, 0.0, 1.0])
    out = sample_conditional_points(state, np.zeros(3), np.zeros(3), np.zeros(3), z)
    assert np.allclose(out, [8.0, 10.0, 12.0])


def test_interaction_cli_commands_are_available():
    fit = build_parser().parse_args(["interaction-fit"])
    status = build_parser().parse_args(["interaction-status"])
    assert Path(fit.out).parts[-2:] == ("interaction_grids", "v001")
    assert Path(status.artifact).parts[-2:] == ("interaction_grids", "v001")


def test_interaction_fit_writes_versioned_artifact_without_fantasy_targets(tmp_path: Path):
    from src.interaction_fit import fit_interaction_grids

    cache = tmp_path / "cache"
    cache.mkdir()
    pd.DataFrame({"gsis_id": ["WR1", "WR2"], "position": ["WR", "WR"]}).to_csv(cache / "players.csv", index=False)

    def pbp_for(season: int) -> pd.DataFrame:
        rows = []
        for week in range(1, 5):
            for team, opp, receiver, yards in (("AAA", "BBB", "WR1", 7), ("BBB", "AAA", "WR2", 11)):
                for play in range(12):
                    rows.append({
                        "season": season,
                        "season_type": "REG",
                        "week": week,
                        "game_id": f"{season}_{week}_{team}",
                        "posteam": team,
                        "defteam": opp,
                        "pass_attempt": 1,
                        "rush_attempt": 0,
                        "sack": 0,
                        "interception": 0,
                        "fumble_lost": 0,
                        "epa": (yards - 8) / 10.0,
                        "yards_gained": yards,
                        "yardline_100": 50,
                        "touchdown": 0,
                        "receiver_player_id": receiver,
                    })
        return pd.DataFrame(rows)

    for season in (2021, 2022, 2023):
        pbp_for(season).to_csv(cache / f"play_by_play_{season}.csv.gz", index=False, compression="gzip")

    stats_rows = []
    for season in (2022, 2023):
        for week in range(1, 5):
            stats_rows += [
                {"season": season, "season_type": "REG", "week": week, "player_id": "WR1", "position": "WR", "opponent_team": "BBB", "targets": 8 + week, "receptions": 5 + week, "receiving_yards": (8 + week) * 7},
                {"season": season, "season_type": "REG", "week": week, "player_id": "WR2", "position": "WR", "opponent_team": "AAA", "targets": 7 + week, "receptions": 4 + week, "receiving_yards": (7 + week) * 10},
            ]
    stats = tmp_path / "player_stats.csv.gz"
    pd.DataFrame(stats_rows).to_csv(stats, index=False, compression="gzip")
    model = {"interaction_grid": {"artifact_id": "fixture", "fit": {
        "seasons": [2022, 2023], "minimum_prior_games": 1, "baseline_shrink_games": 2,
        "baseline_bins": 2, "defense_z_centers": [-1, 0, 1], "cell_shrink_n": 2,
        "ratio_min": 0.5, "ratio_max": 1.5, "uncertainty_floor": 0.02,
        "current_baseline_games": 4,
    }}}
    out = tmp_path / "artifact"
    result = fit_interaction_grids(stats_path=stats, model=model, cache_dir=cache, out_dir=out)
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["model_version"] == "0.28"
    assert manifest["fantasy_points_used_in_fit"] is False
    assert manifest["training_seasons"] == [2022, 2023]
    assert result.grids >= 1
    assert (out / "WR" / "targets.npz").exists()
    assert (out / "player_baselines.json").exists()
    assert (out / "validation.json").exists()


def test_interaction_random_stream_is_deterministic_and_releasable(tmp_path: Path):
    from test_season_gui_service_v024 import _build_runtime
    service = _build_runtime(tmp_path)
    ctx = service.ctx
    assert ctx is not None
    pid = int(ctx.roster[0]["espn_id"])
    first = ctx.interaction_normals(pid).copy()
    ctx.release_predictive_streams([pid])
    second = ctx.interaction_normals(pid).copy()
    assert np.array_equal(first, second)
    old_n = ctx.predictive_scenarios
    ctx.set_predictive_scenarios(old_n + 8)
    assert pid not in ctx._interaction_normals
    assert ctx.interaction_normals(pid).shape == (old_n + 8, 17)


def test_weekly_stats_can_recover_opponent_from_game_id_when_field_is_missing():
    from src.interaction_fit import _prepare_weekly_player_stats

    raw = pd.DataFrame([
        {
            "season": 2025,
            "season_type": "REG",
            "week": 1,
            "game_id": "2025_01_ARI_NO",
            "team": "ARI",
            "player_id": "WR1",
            "position": "WR",
            "targets": 8,
            "receptions": 5,
            "receiving_yards": 70,
        }
    ])
    prepared = _prepare_weekly_player_stats(raw)
    assert prepared.iloc[0]["opponent"] == "NO"


def test_population_shrinkage_baseline_is_strictly_pregame():
    from src.interaction_fit import _prepare_weekly_player_stats, _rolling_baselines

    base_rows = [
        {"season": 2024, "season_type": "REG", "week": 1, "player_id": "WR1", "position": "WR", "opponent_team": "AAA", "targets": 4},
        {"season": 2024, "season_type": "REG", "week": 1, "player_id": "WR2", "position": "WR", "opponent_team": "BBB", "targets": 8},
        {"season": 2024, "season_type": "REG", "week": 2, "player_id": "WR1", "position": "WR", "opponent_team": "CCC", "targets": 6},
        {"season": 2024, "season_type": "REG", "week": 2, "player_id": "WR2", "position": "WR", "opponent_team": "DDD", "targets": 10},
    ]
    first = _rolling_baselines(_prepare_weekly_player_stats(pd.DataFrame(base_rows)), min_games=1, shrink_games=2.0)
    future_rows = base_rows + [
        {"season": 2024, "season_type": "REG", "week": 3, "player_id": "WR3", "position": "WR", "opponent_team": "EEE", "targets": 1000},
    ]
    second = _rolling_baselines(_prepare_weekly_player_stats(pd.DataFrame(future_rows)), min_games=1, shrink_games=2.0)
    b1 = float(first[(first.player_id == "WR1") & (first.week == 2)].iloc[0]["baseline_targets"])
    b2 = float(second[(second.player_id == "WR1") & (second.week == 2)].iloc[0]["baseline_targets"])
    assert b1 == pytest.approx(b2)
    # Prior player mean=4, prior position-week population mean=(4+8)/2=6,
    # lambda=1/(1+2), hence 4/3 + 4 = 5.333...
    assert b1 == pytest.approx((1.0 / 3.0) * 4.0 + (2.0 / 3.0) * 6.0)


def test_defense_state_generation_covers_player_stat_weeks_beyond_cached_pbp_max(tmp_path: Path):
    from src.interaction_fit import build_training_rows

    cache = tmp_path / "cache"
    cache.mkdir()
    pd.DataFrame([{"gsis_id": "WR1", "position": "WR"}]).to_csv(cache / "players.csv", index=False)

    def make_pbp(season: int, weeks: list[int]):
        rows = []
        for week in weeks:
            for play in range(10):
                rows.append({
                    "season": season,
                    "season_type": "REG",
                    "week": week,
                    "game_id": f"{season}_{week:02d}_AAA_BBB",
                    "posteam": "AAA",
                    "defteam": "BBB",
                    "pass_attempt": 1,
                    "rush_attempt": 0,
                    "sack": 0,
                    "interception": 0,
                    "fumble_lost": 0,
                    "epa": 0.1,
                    "yards_gained": 8,
                    "yardline_100": 50,
                    "touchdown": 0,
                    "receiver_player_id": "WR1",
                })
                rows.append({
                    "season": season,
                    "season_type": "REG",
                    "week": week,
                    "game_id": f"{season}_{week:02d}_AAA_BBB",
                    "posteam": "BBB",
                    "defteam": "AAA",
                    "pass_attempt": 1,
                    "rush_attempt": 0,
                    "sack": 0,
                    "interception": 0,
                    "fumble_lost": 0,
                    "epa": -0.1,
                    "yards_gained": 6,
                    "yardline_100": 50,
                    "touchdown": 0,
                    "receiver_player_id": "WR1",
                })
        return pd.DataFrame(rows)

    make_pbp(2023, [1, 2]).to_csv(cache / "play_by_play_2023.csv.gz", index=False, compression="gzip")
    make_pbp(2024, [1, 2]).to_csv(cache / "play_by_play_2024.csv.gz", index=False, compression="gzip")
    # Current cached PBP ends at week 2, but player stats contain week 3.  The
    # pregame state for week 3 must still be generated from data through week 2.
    make_pbp(2025, [1, 2]).to_csv(cache / "play_by_play_2025.csv.gz", index=False, compression="gzip")

    stats_rows = []
    for season in (2024, 2025):
        for week in (1, 2, 3):
            stats_rows.append({
                "season": season,
                "season_type": "REG",
                "week": week,
                "game_id": f"{season}_{week:02d}_AAA_BBB",
                "team": "AAA",
                "player_id": "WR1",
                "position": "WR",
                "opponent_team": "BBB",
                "targets": 5 + week,
                "receptions": 4,
                "receiving_yards": 50,
            })
    stats = tmp_path / "stats.csv.gz"
    pd.DataFrame(stats_rows).to_csv(stats, index=False, compression="gzip")
    rows, _ = build_training_rows(
        stats,
        seasons=[2024, 2025],
        cache_dir=cache,
        min_prior_games=1,
        baseline_shrink_games=2.0,
    )
    week3 = rows[(rows.season == 2025) & (rows.week == 3)]
    assert len(week3) == 1
    assert week3.filter(regex=r"^def_").notna().any(axis=1).all()


def test_sync_nflverse_builds_explicit_season_weekly_stats(monkeypatch, tmp_path: Path):
    from src.data_sources import nflverse as nflverse_source

    def fake_download(url, path, force=False):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.name == "players.csv":
            pd.DataFrame({"gsis_id": ["P1"], "position": ["WR"]}).to_csv(path, index=False)
            return path
        season = int(path.stem.rsplit("_", 1)[-1])
        pd.DataFrame({
            "player_id": [f"P{season}"],
            "position": ["WR"],
            "recent_team": ["AAA"],
            "season": [season],
            "week": [1],
            "season_type": ["REG"],
            "targets": [7],
        }).to_csv(path, index=False)
        return path

    monkeypatch.setattr(nflverse_source, "_download", fake_download)
    result = nflverse_source.sync_nflverse(tmp_path, force=True, seasons=[2024, 2025])
    combined = pd.read_csv(result["player_stats"], compression="gzip")
    assert sorted(combined["season"].unique().tolist()) == [2024, 2025]
    assert (tmp_path / "player_stats_seasons" / "stats_player_week_2025.csv").exists()


def test_current_stats_player_schema_recovers_opponent_from_pbp(tmp_path: Path):
    from src.interaction_fit import build_training_rows

    cache = tmp_path / "cache"
    cache.mkdir()
    pd.DataFrame({"gsis_id": ["WR1", "WR2"], "position": ["WR", "WR"]}).to_csv(cache / "players.csv", index=False)

    def pbp_for(season: int) -> pd.DataFrame:
        rows = []
        for week in range(1, 5):
            for team, opp, receiver, yards in (("AAA", "BBB", "WR1", 7), ("BBB", "AAA", "WR2", 11)):
                for play in range(8):
                    rows.append({
                        "season": season,
                        "season_type": "REG",
                        "week": week,
                        "game_id": f"{season}_{week:02d}_{team}_{opp}",
                        "posteam": team,
                        "defteam": opp,
                        "pass_attempt": 1,
                        "rush_attempt": 0,
                        "sack": 0,
                        "interception": 0,
                        "fumble_lost": 0,
                        "epa": (yards - 8) / 10.0,
                        "yards_gained": yards,
                        "yardline_100": 50,
                        "touchdown": 0,
                        "receiver_player_id": receiver,
                    })
        return pd.DataFrame(rows)

    for season in (2023, 2024, 2025):
        pbp_for(season).to_csv(cache / f"play_by_play_{season}.csv.gz", index=False, compression="gzip")

    stats_rows = []
    for season in (2024, 2025):
        for week in range(1, 5):
            stats_rows += [
                {"season": season, "season_type": "REG", "week": week, "player_id": "WR1", "position": "WR", "recent_team": "AAA", "targets": 8 + week, "receptions": 5 + week, "receiving_yards": (8 + week) * 7},
                {"season": season, "season_type": "REG", "week": week, "player_id": "WR2", "position": "WR", "recent_team": "BBB", "targets": 7 + week, "receptions": 4 + week, "receiving_yards": (7 + week) * 10},
            ]
    stats = tmp_path / "player_stats.csv.gz"
    pd.DataFrame(stats_rows).to_csv(stats, index=False, compression="gzip")

    rows, sources = build_training_rows(
        stats,
        seasons=[2024, 2025],
        cache_dir=cache,
        min_prior_games=1,
        baseline_shrink_games=2.0,
        defense_shrinkage_plays=400.0,
    )
    assert rows["opponent"].notna().all()
    assert set(rows.loc[rows["team"].eq("AAA"), "opponent"]) == {"BBB"}
    assert set(rows.loc[rows["team"].eq("BBB"), "opponent"]) == {"AAA"}
    assert sources["opponent_mapping"]["method"] == "STATS_EXPLICIT_THEN_PBP_POSTEAM_DEFTEAM"


def test_interaction_status_marks_previous_artifact_stale_after_failed_fit(tmp_path: Path, capsys):
    from types import SimpleNamespace
    from fantasy import cmd_interaction_status

    root = tmp_path / "artifact"
    root.mkdir()
    (root / "manifest.json").write_text(json.dumps({
        "artifact_id": "old",
        "model_version": "0.28",
        "training_seasons": [2022, 2023, 2024, 2025],
    }))
    (root / "validation.json").write_text(json.dumps({
        "validation_season": 2025,
        "components": {},
    }))
    failure = root / "fit_failure.json"
    failure.write_text(json.dumps({
        "reason": "validation season 2025 has zero player rows",
        "coverage_path": str(root / "coverage.json"),
    }))
    # Ensure the failure marker is at least as recent as the manifest on filesystems
    # with coarse timestamp resolution.
    failure.touch()

    cmd_interaction_status(SimpleNamespace(artifact=str(root)))
    out = capsys.readouterr().out
    assert "LATEST INTERACTION FIT: FAILED" in out
    assert "STALE" in out
