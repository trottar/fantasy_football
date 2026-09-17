from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .data_sources.nflverse import sync_weekly_player_stats
from .league import load_league
from .scoring import score_offense
from .transaction_manager import UtilityContext
from .weekly_manager import availability_status, find_week_opponent, resolve_team


CLOSURE_SCHEMA_VERSION = 1
PREDICTION_MODEL_VERSION = "0.29"
COUNT_COMPONENTS = {"attempts", "rushing_attempts", "carries", "targets"}
SUPPORTED_COMPONENTS: dict[str, tuple[str, ...]] = {
    "QB": ("attempts", "passing_yards_per_attempt", "rushing_attempts", "rushing_yards_per_attempt"),
    "RB": ("carries", "rushing_yards_per_attempt", "targets", "catch_rate", "receiving_yards_per_target"),
    "WR": ("targets", "catch_rate", "receiving_yards_per_target"),
    "TE": ("targets", "catch_rate", "receiving_yards_per_target"),
}


def _finite(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _iso(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _gsis_id(player: dict[str, Any]) -> str | None:
    for key in ("nflverse_gsis_id", "gsis_id", "player_id"):
        value = str(player.get(key) or "").strip()
        if value:
            return value
    return None


def _base_and_corrected_components(state: Any, *, expected_workload_factor: float = 1.0) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    components = getattr(state, "interaction_components", {}) or {}
    for name, raw in components.items():
        row = dict(raw or {})
        base = _finite(row.get("baseline_value"))
        corrected = _finite(row.get("corrected_value"))
        if base is None:
            continue
        if corrected is None:
            corrected = base
        closure_base = float(base * expected_workload_factor) if str(name) in COUNT_COMPONENTS else float(base)
        closure_corrected = float(corrected * expected_workload_factor) if str(name) in COUNT_COMPONENTS else float(corrected)
        out[str(name)] = {
            "base": float(base),
            "corrected": float(corrected),
            "closure_base": closure_base,
            "closure_corrected": closure_corrected,
            "correction": float(_finite(row.get("correction")) or 1.0),
            "correction_sd": float(_finite(row.get("correction_sd")) or 0.0),
            "support": float(_finite(row.get("support")) or 0.0),
            "defense_feature": row.get("defense_feature"),
            "defense_z": _finite(row.get("defense_z")),
            "commissioned": bool(row.get("commissioned", False)),
        }
    return out


def _player_prediction_record(player: dict[str, Any], ctx: UtilityContext, *, side: str) -> dict[str, Any]:
    week = int(ctx.week)
    state = ctx.yield_state(player, week)
    availability = ctx.availability_state(player, week)
    timing = ctx.lock_timing(player, week)
    status, status_source = availability_status(player)
    interaction_delta = float(state.interaction_delta_ppg or 0.0)
    corrected = float(state.operational_mean_ppg)
    base_mc = corrected - interaction_delta
    workload_factor = float(availability.p_full + availability.p_limited * availability.limited_workload_fraction)
    second_workload_factor = float(
        availability.p_full
        + availability.p_limited * availability.limited_workload_fraction * availability.limited_workload_fraction
    )

    def marginal_moments(mu: float, sigma: float) -> tuple[float, float]:
        mean = workload_factor * float(mu)
        second = second_workload_factor * (float(sigma) * float(sigma) + float(mu) * float(mu))
        variance = max(second - mean * mean, 0.0)
        return float(mean), float(math.sqrt(variance))

    corrected_marginal_mean, corrected_marginal_sd = marginal_moments(corrected, float(state.predictive_sd_ppg))
    base_conditional_sd = math.sqrt(
        float(state.game_sd_ppg) ** 2
        + float(state.model_sd_ppg) ** 2
        + float(state.kinematic_sd_ppg) ** 2
    )
    base_marginal_mean, base_marginal_sd = marginal_moments(base_mc, base_conditional_sd)
    return {
        "side": str(side),
        "espn_id": _int(player.get("espn_id")),
        "gsis_id": _gsis_id(player),
        "name": str(player.get("name") or "?"),
        "position": str(player.get("position") or "").upper(),
        "nfl_team": player.get("nfl_team"),
        "matchup_opponent": state.matchup_opponent,
        "model_mean_ppg": state.model_mean_ppg,
        "pre_matchup_mean_ppg": state.pre_matchup_operational_mean_ppg,
        "matchup_model_mean_ppg": state.matchup_model_mean_ppg,
        "espn_anchor_ppg": state.espn_anchor_ppg,
        "espn_anchor_kind": state.espn_anchor_kind,
        "base_mc_mean_ppg": float(base_mc),
        "interaction_corrected_mean_ppg": corrected,
        "operational_mean_ppg": corrected,
        "predictive_sd_ppg": float(state.predictive_sd_ppg),
        "availability_marginal_base_mc_mean_ppg": base_marginal_mean,
        "availability_marginal_base_mc_sd_ppg": base_marginal_sd,
        "availability_marginal_corrected_mean_ppg": corrected_marginal_mean,
        "availability_marginal_corrected_sd_ppg": corrected_marginal_sd,
        "expected_workload_factor": workload_factor,
        "game_sd_ppg": float(state.game_sd_ppg),
        "model_sd_ppg": float(state.model_sd_ppg),
        "kinematic_sd_ppg": float(state.kinematic_sd_ppg),
        "interaction_sd_ppg": float(state.interaction_sd_ppg),
        "kinematic_factor": float(state.kinematic_factor_mean),
        "interaction_factor": float(state.interaction_factor_mean),
        "interaction_delta_ppg": interaction_delta,
        "interaction_artifact_id": state.interaction_artifact_id,
        "component_predictions": _base_and_corrected_components(state, expected_workload_factor=workload_factor),
        "availability_status": status,
        "availability_status_source": status_source,
        "p_active": float(availability.p_active),
        "p_full_given_active": float(availability.p_full_given_active),
        "p_full": float(availability.p_full),
        "p_limited": float(availability.p_limited),
        "p_out": float(availability.p_out),
        "limited_workload_fraction": float(availability.limited_workload_fraction),
        "availability_evidence_level": availability.evidence_level,
        "availability_posterior_method": availability.posterior_method,
        "availability_calibration_status": availability.calibration_status,
        "practice_source": availability.practice_source,
        "practice_sequence": list(availability.practice_sequence),
        **timing.to_dict(),
    }


def build_pregame_capture_from_context(
    snapshot: dict[str, Any],
    model: dict[str, Any],
    ctx: UtilityContext,
    team: dict[str, Any],
    *,
    captured_utc: str | None = None,
) -> dict[str, Any]:
    opponent_id = find_week_opponent(snapshot, int(team.get("team_id")))
    opponent_roster = ctx.all_team_rosters.get(int(opponent_id), []) if opponent_id is not None else []
    captured = captured_utc or datetime.now(timezone.utc).isoformat()
    players = [
        *[_player_prediction_record(p, ctx, side="US") for p in ctx.roster],
        *[_player_prediction_record(p, ctx, side="OPP") for p in opponent_roster],
    ]
    return {
        "schema_version": CLOSURE_SCHEMA_VERSION,
        "model_version": PREDICTION_MODEL_VERSION,
        "captured_utc": captured,
        "snapshot_utc": snapshot.get("snapshot_utc"),
        "season": int((snapshot.get("espn", snapshot).get("season") or 2026)),
        "week": int((snapshot.get("espn", snapshot).get("week") or 1)),
        "team_id": _int(team.get("team_id")),
        "team_name": team.get("name"),
        "opponent_team_id": opponent_id,
        "mc_scenarios": int(ctx.predictive_scenarios),
        "interaction_artifact_id": (model.get("interaction_grid") or {}).get("artifact_id"),
        "players": players,
        "notes": [
            "Immutable pregame closure capture. Component predictions are football observables; fantasy scoring is retained separately as downstream yield.",
            "Base MC means are operational means before the v0.28 interaction point correction; corrected MC means include commissioned interaction grids.",
            "Availability probabilities are captured exactly as available at decision time and are not retroactively rewritten after games.",
        ],
    }


def build_pregame_capture(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    *,
    values_path: str | Path,
    team_name: str | None = None,
    team_id: int | None = None,
    captured_utc: str | None = None,
) -> dict[str, Any]:
    team = resolve_team(snapshot, team_name=team_name or league.get("user_team_name"), team_id=team_id)
    ctx = UtilityContext(snapshot, league, model, values_path, team)
    return build_pregame_capture_from_context(
        snapshot, model, ctx, team, captured_utc=captured_utc
    )


def save_pregame_capture(capture: dict[str, Any], out_dir: str | Path = "data/season_predictions/closure") -> Path:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    season = int(capture.get("season") or 0)
    week = int(capture.get("week") or 0)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / f"pregame_{season}_w{week:02d}_{stamp}.json"
    suffix = 1
    while path.exists():
        path = root / f"pregame_{season}_w{week:02d}_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(capture, indent=2, sort_keys=True), encoding="utf-8")
    return path


def capture_pregame_predictions(
    *,
    snapshot_path: str | Path = "data/season_snapshots/latest.json",
    league_path: str | Path = "config/league.json",
    model_path: str | Path = "config/model.json",
    values_path: str | Path = "data/processed/player_values_2026.csv",
    team_name: str | None = None,
    team_id: int | None = None,
    out_dir: str | Path = "data/season_predictions/closure",
) -> tuple[dict[str, Any], Path]:
    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    league = load_league(league_path)
    model = json.loads(Path(model_path).read_text(encoding="utf-8"))
    capture = build_pregame_capture(
        snapshot,
        league,
        model,
        values_path=values_path,
        team_name=team_name,
        team_id=team_id,
    )
    return capture, save_pregame_capture(capture, out_dir)


def _weekly_stats_frame(path: str | Path, season: int) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    if "season_type" in df.columns:
        df = df[df["season_type"].astype(str).str.upper().eq("REG")]
    if "season" in df.columns:
        df = df[pd.to_numeric(df["season"], errors="coerce").eq(int(season))]
    if "week" not in df.columns or "player_id" not in df.columns:
        raise ValueError("nflverse weekly stats require week and player_id columns")
    df = df.copy()
    df["week"] = pd.to_numeric(df["week"], errors="coerce")
    df = df.dropna(subset=["week", "player_id"])
    df["week"] = df["week"].astype(int)
    df["player_id"] = df["player_id"].astype(str)
    return df


def _num(row: pd.Series | dict[str, Any], key: str) -> float:
    value = _finite(row.get(key))
    return float(value or 0.0)


def observed_components(row: pd.Series | dict[str, Any], position: str) -> dict[str, float | None]:
    pos = str(position).upper()
    attempts = _num(row, "attempts")
    pass_yards = _num(row, "passing_yards")
    carries = _num(row, "carries")
    rush_yards = _num(row, "rushing_yards")
    targets = _num(row, "targets")
    receptions = _num(row, "receptions")
    rec_yards = _num(row, "receiving_yards")
    values = {
        "attempts": attempts,
        "passing_yards_per_attempt": pass_yards / attempts if attempts > 0 else None,
        "carries": carries,
        "rushing_attempts": carries,
        "rushing_yards_per_attempt": rush_yards / carries if carries > 0 else None,
        "targets": targets,
        "catch_rate": receptions / targets if targets > 0 else None,
        "receiving_yards_per_target": rec_yards / targets if targets > 0 else None,
    }
    return {name: values.get(name) for name in SUPPORTED_COMPONENTS.get(pos, ())}


def observed_fantasy_points(row: pd.Series | dict[str, Any], position: str) -> float | None:
    if str(position).upper() not in {"QB", "RB", "WR", "TE"}:
        return None
    lost = _num(row, "sack_fumbles_lost") + _num(row, "rushing_fumbles_lost") + _num(row, "receiving_fumbles_lost")
    stats = {
        "pass_yds": _num(row, "passing_yards"),
        "pass_td": _num(row, "passing_tds"),
        "pass_int": _num(row, "passing_interceptions"),
        "pass_2pt": _num(row, "passing_2pt_conversions"),
        "rush_yds": _num(row, "rushing_yards"),
        "rush_td": _num(row, "rushing_tds"),
        "rush_2pt": _num(row, "rushing_2pt_conversions"),
        "rec": _num(row, "receptions"),
        "rec_yds": _num(row, "receiving_yards"),
        "rec_td": _num(row, "receiving_tds"),
        "rec_2pt": _num(row, "receiving_2pt_conversions"),
        "fumbles_lost": lost,
        "kickoff_return_td": _num(row, "kickoff_return_tds"),
        "punt_return_td": _num(row, "punt_return_tds"),
        "fumble_recovery_td": _num(row, "special_teams_tds"),
    }
    return float(score_offense(stats))


def _capture_files(root: str | Path) -> list[Path]:
    return sorted(Path(root).glob("pregame_*.json"))


def _load_capture_records(root: str | Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in _capture_files(root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        captured = payload.get("captured_utc")
        season = _int(payload.get("season"))
        week = _int(payload.get("week"))
        if season is None or week is None:
            continue
        for player in payload.get("players") or []:
            row = dict(player)
            row["capture_path"] = str(path)
            row["captured_utc"] = captured
            row["season"] = season
            row["week"] = week
            out.append(row)
    return out


def _latest_valid_pregame_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[tuple[int, int, str, str], tuple[datetime, dict[str, Any]]] = {}
    for row in records:
        season = _int(row.get("season"))
        week = _int(row.get("week"))
        gsis = str(row.get("gsis_id") or "").strip()
        side = str(row.get("side") or "?")
        captured = _iso(row.get("captured_utc"))
        if season is None or week is None or not gsis or captured is None:
            continue
        kickoff = _iso(row.get("kickoff_utc") or row.get("kickoff"))
        if kickoff is not None and captured >= kickoff:
            # Decision-time integrity: a post-lock capture is never substituted for
            # the pregame state when building prospective closure.
            continue
        key = (season, week, gsis, side)
        prior = selected.get(key)
        if prior is None or captured > prior[0]:
            selected[key] = (captured, row)
    return [item[1] for item in selected.values()]


def build_closure_ledger(
    *,
    prediction_dir: str | Path,
    stats_by_season: dict[int, str | Path],
) -> pd.DataFrame:
    records = _latest_valid_pregame_records(_load_capture_records(prediction_dir))
    stats_frames = {int(season): _weekly_stats_frame(path, int(season)) for season, path in stats_by_season.items()}
    stats_index: dict[tuple[int, int, str], dict[str, Any]] = {}
    for season, frame in stats_frames.items():
        for rec in frame.to_dict("records"):
            stats_index[(int(season), int(rec["week"]), str(rec["player_id"]))] = rec

    ledger: list[dict[str, Any]] = []
    for pred in records:
        season = int(pred["season"])
        week = int(pred["week"])
        gsis = str(pred.get("gsis_id") or "")
        obs = stats_index.get((season, week, gsis))
        position = str(pred.get("position") or "").upper()
        observed = observed_components(obs, position) if obs is not None else {}
        observed_points = observed_fantasy_points(obs, position) if obs is not None else None
        component_predictions = pred.get("component_predictions") or {}
        component_names = sorted(set(SUPPORTED_COMPONENTS.get(position, ())) | set(component_predictions))
        base_points = _finite(pred.get("availability_marginal_base_mc_mean_ppg"))
        if base_points is None:
            base_points = _finite(pred.get("base_mc_mean_ppg"))
        corrected_points = _finite(pred.get("availability_marginal_corrected_mean_ppg"))
        if corrected_points is None:
            corrected_points = _finite(pred.get("interaction_corrected_mean_ppg"))
        sd_points = _finite(pred.get("availability_marginal_corrected_sd_ppg"))
        if sd_points is None:
            sd_points = _finite(pred.get("predictive_sd_ppg"))
        ledger.append({
            "row_type": "FANTASY_YIELD",
            "season": season,
            "week": week,
            "side": pred.get("side"),
            "espn_id": pred.get("espn_id"),
            "gsis_id": gsis,
            "name": pred.get("name"),
            "position": position,
            "nfl_team": pred.get("nfl_team"),
            "matchup_opponent": pred.get("matchup_opponent"),
            "component": "fantasy_points",
            "base_mc": base_points,
            "corrected_mc": corrected_points,
            "observed": observed_points,
            "predictive_sd": sd_points,
            "residual": (observed_points - corrected_points) if observed_points is not None and corrected_points is not None else None,
            "pull": ((observed_points - corrected_points) / sd_points) if observed_points is not None and corrected_points is not None and sd_points and sd_points > 0 else None,
            "data_over_mc": (observed_points / corrected_points) if observed_points is not None and corrected_points not in (None, 0.0) else None,
            "data_over_base_mc": (observed_points / base_points) if observed_points is not None and base_points not in (None, 0.0) else None,
            "p_active": pred.get("p_active"),
            "p_full_given_active": pred.get("p_full_given_active"),
            "observed_active": obs.get("active") if obs is not None and "active" in obs else None,
            "observed_stat_row": obs is not None,
            "captured_utc": pred.get("captured_utc"),
            "capture_path": pred.get("capture_path"),
        })
        for component in component_names:
            cp = dict(component_predictions.get(component) or {})
            base = _finite(cp.get("closure_base"))
            if base is None:
                base = _finite(cp.get("base"))
            corrected = _finite(cp.get("closure_corrected"))
            if corrected is None:
                corrected = _finite(cp.get("corrected"))
            value = _finite(observed.get(component))
            ledger.append({
                "row_type": "COMPONENT",
                "season": season,
                "week": week,
                "side": pred.get("side"),
                "espn_id": pred.get("espn_id"),
                "gsis_id": gsis,
                "name": pred.get("name"),
                "position": position,
                "nfl_team": pred.get("nfl_team"),
                "matchup_opponent": pred.get("matchup_opponent"),
                "component": component,
                "base_mc": base,
                "corrected_mc": corrected,
                "observed": value,
                "predictive_sd": None,
                "residual": (value - corrected) if value is not None and corrected is not None else None,
                "pull": None,
                "data_over_mc": (value / corrected) if value is not None and corrected not in (None, 0.0) else None,
                "data_over_base_mc": (value / base) if value is not None and base not in (None, 0.0) else None,
                "commissioned_interaction": cp.get("commissioned"),
                "interaction_correction": cp.get("correction"),
                "interaction_support": cp.get("support"),
                "p_active": pred.get("p_active"),
                "p_full_given_active": pred.get("p_full_given_active"),
                "observed_active": obs.get("active") if obs is not None and "active" in obs else None,
                "observed_stat_row": obs is not None,
                "captured_utc": pred.get("captured_utc"),
                "capture_path": pred.get("capture_path"),
            })
    return pd.DataFrame(ledger)


def _metric_summary(rows: pd.DataFrame) -> dict[str, Any]:
    valid = rows.dropna(subset=["observed", "corrected_mc"]).copy()
    if valid.empty:
        return {"n": 0, "bias": None, "mae": None, "rmse": None, "mean_data_over_mc": None}
    data = valid["observed"].astype(float).to_numpy()
    corr = valid["corrected_mc"].astype(float).to_numpy()
    out: dict[str, Any] = {
        "n": int(len(valid)),
        "bias": float(np.mean(data - corr)),
        "mae": float(np.mean(np.abs(data - corr))),
        "rmse": float(np.sqrt(np.mean((data - corr) ** 2))),
    }
    ratio = valid["data_over_mc"].dropna().astype(float)
    out["mean_data_over_mc"] = float(ratio.mean()) if len(ratio) else None
    base = valid.dropna(subset=["base_mc"])
    if len(base):
        bd = base["observed"].astype(float).to_numpy()
        bm = base["base_mc"].astype(float).to_numpy()
        base_rmse = float(np.sqrt(np.mean((bd - bm) ** 2)))
        out["base_rmse"] = base_rmse
        out["interaction_rmse_improvement"] = float(base_rmse - out["rmse"])
    else:
        out["base_rmse"] = None
        out["interaction_rmse_improvement"] = None
    return out


def _active_truth(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().upper()
    if text in {"1", "TRUE", "T", "YES", "Y", "ACTIVE"}:
        return 1.0
    if text in {"0", "FALSE", "F", "NO", "N", "INACTIVE"}:
        return 0.0
    parsed = _finite(value)
    if parsed is not None and parsed in {0.0, 1.0}:
        return float(parsed)
    return None


def summarize_closure_ledger(ledger: pd.DataFrame) -> dict[str, Any]:
    if ledger is None or ledger.empty:
        return {
            "schema_version": CLOSURE_SCHEMA_VERSION,
            "fantasy": _metric_summary(pd.DataFrame(columns=["observed", "corrected_mc", "base_mc", "data_over_mc"])),
            "components": {},
            "pull": {"n": 0, "mean": None, "sd": None},
            "availability": {"n": 0, "brier": None},
        }
    fantasy = ledger[ledger["row_type"].eq("FANTASY_YIELD")]
    components = ledger[ledger["row_type"].eq("COMPONENT")]
    component_summary: dict[str, Any] = {}
    for (position, component), group in components.groupby(["position", "component"], dropna=False):
        component_summary[f"{position}:{component}"] = _metric_summary(group)
    pulls = fantasy["pull"].dropna().astype(float)
    active = fantasy.dropna(subset=["observed_active", "p_active"]).copy()
    if len(active):
        active["_truth"] = active["observed_active"].map(_active_truth)
        active = active.dropna(subset=["_truth"])
    if len(active):
        y = active["_truth"].astype(float).to_numpy()
        p = active["p_active"].astype(float).to_numpy()
        brier = float(np.mean((p - y) ** 2))
    else:
        brier = None
    return {
        "schema_version": CLOSURE_SCHEMA_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "rows": int(len(ledger)),
        "fantasy": _metric_summary(fantasy),
        "components": component_summary,
        "pull": {
            "n": int(len(pulls)),
            "mean": float(pulls.mean()) if len(pulls) else None,
            "sd": float(pulls.std(ddof=1)) if len(pulls) > 1 else (0.0 if len(pulls) == 1 else None),
        },
        "availability": {"n": int(len(active)), "brier": brier},
        "weeks": sorted({f"{int(s)}-W{int(w):02d}" for s, w in zip(ledger["season"], ledger["week"])}),
    }


def save_closure_outputs(
    ledger: pd.DataFrame,
    summary: dict[str, Any],
    *,
    out_dir: str | Path = "data/season_closure",
) -> dict[str, Path]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    snapshots = root / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snap_path = snapshots / f"closure_{stamp}.json"
    suffix = 1
    while snap_path.exists():
        snap_path = snapshots / f"closure_{stamp}_{suffix:02d}.json"
        suffix += 1
    records = json.loads(ledger.to_json(orient="records")) if len(ledger) else []
    snap_payload = {"summary": summary, "records": records}
    snap_path.write_text(json.dumps(snap_payload, indent=2, sort_keys=True), encoding="utf-8")
    ledger_path = root / "ledger.csv"
    summary_path = root / "summary.json"
    ledger.to_csv(ledger_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return {"snapshot": snap_path, "ledger": ledger_path, "summary": summary_path}


def update_closure(
    *,
    prediction_dir: str | Path = "data/season_predictions/closure",
    raw_dir: str | Path = "data/raw/nflverse/closure",
    out_dir: str | Path = "data/season_closure",
    seasons: Iterable[int] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    records = _load_capture_records(prediction_dir)
    available_seasons = sorted({_int(row.get("season")) for row in records if _int(row.get("season")) is not None})
    selected = sorted({int(s) for s in (seasons or available_seasons)})
    if not selected:
        raise ValueError("closure-update found no pregame captures; run `python fantasy.py closure-capture` before games")
    stats_by_season = {
        season: sync_weekly_player_stats(raw_dir, season=season, force=force)
        for season in selected
    }
    ledger = build_closure_ledger(prediction_dir=prediction_dir, stats_by_season=stats_by_season)
    summary = summarize_closure_ledger(ledger)
    paths = save_closure_outputs(ledger, summary, out_dir=out_dir)
    return {"ledger": ledger, "summary": summary, "paths": paths, "stats": stats_by_season}


def load_closure_ledger(path: str | Path = "data/season_closure/ledger.csv") -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def load_closure_summary(path: str | Path = "data/season_closure/summary.json") -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return summarize_closure_ledger(pd.DataFrame())
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return summarize_closure_ledger(pd.DataFrame())

# v0.34 extends the immutable v0.29 player prediction capture at the observation
# boundary. The postgame v0.29 ledger intentionally continues to read only the
# `players` block until Data-informed 1.X commissioning begins.
_build_pregame_capture_from_context_pre_v034 = build_pregame_capture_from_context


def build_pregame_capture_from_context(
    snapshot: dict[str, Any],
    model: dict[str, Any],
    ctx: UtilityContext,
    team: dict[str, Any],
    *,
    captured_utc: str | None = None,
) -> dict[str, Any]:
    base = _build_pregame_capture_from_context_pre_v034(
        snapshot, model, ctx, team, captured_utc=captured_utc
    )
    team_names = {
        int(tid): row.get("name")
        for row in (ctx.espn.get("teams") or [])
        if (tid := _int(row.get("team_id"))) is not None
    }
    league_players = []
    for fantasy_team_id, roster in sorted(ctx.all_team_rosters.items()):
        for player in roster or []:
            if str(player.get("position") or "").upper() not in {"QB", "RB", "WR", "TE"}:
                continue
            record = _player_prediction_record(player, ctx, side="LEAGUE")
            record["fantasy_team_id"] = int(fantasy_team_id)
            record["fantasy_team_name"] = team_names.get(int(fantasy_team_id))
            league_players.append(record)
    base["league_player_predictions"] = {
        "scope": "ALL_ROSTERED_QB_RB_WR_TE_V034",
        "records": league_players,
        "count": len(league_players),
        "postgame_ledger_enabled": False,
        "note": "Frozen for future 1.X prospective closure; the inherited v0.29 ledger continues to consume only the players block.",
    }
    from .prospective_measurement_v034 import enrich_pregame_capture
    return enrich_pregame_capture(base, snapshot, model, ctx, team)

