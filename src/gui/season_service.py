from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Callable

import numpy as np

from ..league import load_league
from ..matchup_model import simulate_dst_component_points
from ..season_snapshot import sync_season_snapshot
from ..transaction_manager import (
    UtilityContext,
    PLAYER_POSITIONS,
    _classify_paired_delta,
    _classify_market_action,
    _legal_drop,
    _legal_roster_after_add_drop,
    _paired_mean_interval,
    _market_projection_support,
    _option_scarcity_utility_adjustment,
    roster_option_scarcity_value,
    released_player_league_state_response,
    _scenario_h2h_utility_against,
    evaluate_roster_predictive,
    waiver_acquisition_probability,
    waiver_blocker_diagnostics,
)

from ..specialist_policy_v032 import evaluate_defense_channel, evaluate_kicker_channel

from ..market_manager import (
    evaluate_trade,
    screen_one_for_one_trades,
    search_trades,
)
from ..weekly_manager import (
    active_probability,
    availability_status,
    find_week_opponent,
    optimize_lineup,
    resolve_team,
)
from ..weekly_yield import sample_conditional_points
from ..closure import build_pregame_capture_from_context, load_closure_ledger, load_closure_summary, save_pregame_capture
from .chat_report import format_chat_report


CANONICAL_SLOTS = ("QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "DST")
SLOT_POSITIONS = {
    "QB": {"QB"},
    "RB1": {"RB"},
    "RB2": {"RB"},
    "WR1": {"WR"},
    "WR2": {"WR"},
    "TE": {"TE"},
    "FLEX": {"RB", "WR", "TE"},
    "K": {"K"},
    "DST": {"DST"},
}
AVAILABILITY_MODES = {"MODEL", "FULL", "LIMITED", "OUT"}


class SeasonGuiError(RuntimeError):
    pass


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


def _quantiles(values: np.ndarray) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return {"mean": 0.0, "sd": 0.0, "p10": 0.0, "p50": 0.0, "p90": 0.0}
    return {
        "mean": float(np.mean(arr)),
        "sd": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "p10": float(np.quantile(arr, 0.10)),
        "p50": float(np.quantile(arr, 0.50)),
        "p90": float(np.quantile(arr, 0.90)),
    }


def _histogram(values: np.ndarray, bins: int = 24) -> list[dict[str, float]]:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return []
    lo = float(np.min(arr))
    hi = float(np.max(arr))
    if math.isclose(lo, hi):
        return [{"x": lo, "count": float(arr.size)}]
    counts, edges = np.histogram(arr, bins=max(6, int(bins)))
    centers = 0.5 * (edges[:-1] + edges[1:])
    return [{"x": float(x), "count": float(c)} for x, c in zip(centers, counts)]


class SeasonGuiService:
    """Thin, read-only GUI facade over the season model.

    The GUI is intentionally not a second optimizer. This class delegates player
    yield construction and roster utility to the same shared base/interaction model objects used
    by the CLI, while providing GUI-friendly summaries and local hypothetical states.
    No method writes to ESPN.
    """

    def __init__(
        self,
        *,
        snapshot_path: str | Path = "data/season_snapshots/latest.json",
        league_path: str | Path = "config/league.json",
        model_path: str | Path = "config/model.json",
        values_path: str | Path = "data/processed/player_values_2026.csv",
        secrets_path: str | Path | None = None,
        snapshots_dir: str | Path = "data/season_snapshots",
        team_name: str | None = None,
        team_id: int | None = None,
        mc_scenarios: int | None = None,
    ) -> None:
        self.snapshot_path = Path(snapshot_path)
        self.league_path = Path(league_path)
        self.model_path = Path(model_path)
        self.values_path = Path(values_path)
        self.secrets_path = str(secrets_path) if secrets_path is not None else None
        self.snapshots_dir = Path(snapshots_dir)
        self.explicit_team_name = team_name
        self.explicit_team_id = team_id
        self.mc_scenarios_override = self._validate_mc_scenarios(mc_scenarios) if mc_scenarios is not None else None
        self.snapshot: dict[str, Any] = {}
        self.league: dict[str, Any] = {}
        self.model: dict[str, Any] = {}
        self.team: dict[str, Any] = {}
        self.ctx: UtilityContext | None = None
        self._baseline_cache: tuple[Any, np.ndarray, np.ndarray] | None = None
        self._idealized_active_baseline_cache: tuple[Any, np.ndarray, np.ndarray] | None = None
        self._idealized_baseline_cache: tuple[Any, np.ndarray, np.ndarray] | None = None
        self.reload()

    @staticmethod
    def _validate_mc_scenarios(value: int | None) -> int | None:
        if value is None:
            return None
        n = int(value)
        if n < 128:
            raise SeasonGuiError("MC scenarios must be at least 128")
        if n > 262144:
            raise SeasonGuiError("MC scenarios above 262144 are disabled to prevent accidental runaway local jobs")
        return n

    @property
    def mc_scenarios(self) -> int:
        assert self.ctx is not None
        return int(self.ctx.predictive_scenarios)

    @property
    def mc_options(self) -> list[int]:
        cfg = (self.model.get("transaction_manager") or {}).get("gui_mc_options") or [1024, 4096, 16384, 65536]
        values = sorted({self._validate_mc_scenarios(int(v)) for v in cfg})
        return [int(v) for v in values if v is not None]

    def set_mc_scenarios(self, value: int) -> int:
        """Change in-memory MC size without reloading static league/player data."""
        n = self._validate_mc_scenarios(value)
        assert n is not None
        self.mc_scenarios_override = n
        self.model.setdefault("transaction_manager", {})["predictive_mc_scenarios"] = int(n)
        assert self.ctx is not None
        self.ctx.set_predictive_scenarios(int(n))
        self._baseline_cache = None
        self._idealized_active_baseline_cache = None
        self._idealized_baseline_cache = None
        return self.mc_scenarios

    def _predictive_evaluation_work(self) -> int:
        assert self.ctx is not None
        weeks = max(1, 18 - max(1, self.week))
        return int(2 * weeks * self.ctx.predictive_scenarios)

    @staticmethod
    def _progress_adapter(
        callback: Callable[[int, int, str], None] | None,
        *,
        offset: int,
        total: int,
        label: str,
    ) -> Callable[[int, int, str], None] | None:
        if callback is None:
            return None
        def wrapped(done: int, local_total: int, phase: str) -> None:
            callback(offset + min(int(done), int(local_total)), total, f"{label}: {phase}")
        return wrapped

    @property
    def week(self) -> int:
        return int((self.snapshot.get("espn", self.snapshot).get("week") or 1))

    @property
    def season(self) -> int:
        return int((self.snapshot.get("espn", self.snapshot).get("season") or 2026))

    def reload(self) -> None:
        if not self.snapshot_path.exists():
            raise SeasonGuiError(
                f"Season snapshot not found: {self.snapshot_path}. Run `python fantasy.py season-sync` first."
            )
        if not self.league_path.exists() or not self.model_path.exists():
            raise SeasonGuiError("Missing config/league.json or config/model.json")
        if not self.values_path.exists():
            raise SeasonGuiError(
                f"Player values not found: {self.values_path}. Copy the processed data from the prior working version."
            )
        self.snapshot = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
        self.league = load_league(self.league_path)
        self.model = json.loads(self.model_path.read_text(encoding="utf-8"))
        if self.mc_scenarios_override is not None:
            self.model.setdefault("transaction_manager", {})["predictive_mc_scenarios"] = int(self.mc_scenarios_override)
        configured = self.league.get("user_team_name")
        self.team = resolve_team(
            self.snapshot,
            team_name=self.explicit_team_name or configured,
            team_id=self.explicit_team_id,
        )
        self.ctx = UtilityContext(self.snapshot, self.league, self.model, self.values_path, self.team)
        self._baseline_cache = None
        self._idealized_active_baseline_cache = None
        self._idealized_baseline_cache = None

    def sync_and_reload(self) -> dict[str, Any]:
        snapshot, path = sync_season_snapshot(
            secrets_path=self.secrets_path,
            out_root=self.snapshots_dir,
            week=None,
            include_sleeper=True,
            include_nfl=True,
        )
        self.snapshot_path = self.snapshots_dir / "latest.json"
        self.reload()
        return {
            "snapshot": str(path),
            "latest": str(self.snapshot_path),
            "source_status": snapshot.get("source_status") or {},
        }

    def _baseline(
        self, progress_callback: Callable[[int, int, str], None] | None = None,
        *, progress_offset: int = 0, progress_total: int | None = None,
    ) -> tuple[Any, np.ndarray, np.ndarray]:
        work = self._predictive_evaluation_work()
        total = int(progress_total or (progress_offset + work))
        if self._baseline_cache is None:
            assert self.ctx is not None
            self._baseline_cache = evaluate_roster_predictive(
                self.ctx.roster, self.ctx,
                progress_callback=progress_callback, progress_offset=progress_offset,
                progress_total=total, progress_label="realistic",
            )
        elif progress_callback is not None:
            progress_callback(progress_offset + work, total, "realistic: cached")
        return self._baseline_cache

    def _idealized_active_baseline(
        self, progress_callback: Callable[[int, int, str], None] | None = None,
        *, progress_offset: int = 0, progress_total: int | None = None,
    ) -> tuple[Any, np.ndarray, np.ndarray]:
        work = self._predictive_evaluation_work()
        total = int(progress_total or (progress_offset + work))
        if self._idealized_active_baseline_cache is None:
            assert self.ctx is not None
            self._idealized_active_baseline_cache = evaluate_roster_predictive(
                self.ctx.roster, self.ctx, current_week_policy="idealized_active",
                progress_callback=progress_callback, progress_offset=progress_offset,
                progress_total=total, progress_label="ideal-active",
            )
        elif progress_callback is not None:
            progress_callback(progress_offset + work, total, "ideal-active: cached")
        return self._idealized_active_baseline_cache

    def _idealized_baseline(
        self, progress_callback: Callable[[int, int, str], None] | None = None,
        *, progress_offset: int = 0, progress_total: int | None = None,
    ) -> tuple[Any, np.ndarray, np.ndarray]:
        work = self._predictive_evaluation_work()
        total = int(progress_total or (progress_offset + work))
        if self._idealized_baseline_cache is None:
            assert self.ctx is not None
            self._idealized_baseline_cache = evaluate_roster_predictive(
                self.ctx.roster, self.ctx, current_week_policy="idealized",
                progress_callback=progress_callback, progress_offset=progress_offset,
                progress_total=total, progress_label="ideal-full",
            )
        elif progress_callback is not None:
            progress_callback(progress_offset + work, total, "ideal-full: cached")
        return self._idealized_baseline_cache

    def _team_by_id(self, team_id: int | None) -> dict[str, Any] | None:
        if team_id is None:
            return None
        espn = self.snapshot.get("espn", self.snapshot)
        return next((t for t in espn.get("teams") or [] if _int(t.get("team_id")) == int(team_id)), None)

    def source_health(self) -> list[dict[str, str]]:
        statuses = self.snapshot.get("source_status") or {}
        out: list[dict[str, str]] = []
        labels = [
            ("espn", "ESPN"),
            ("sleeper", "Sleeper"),
            ("nflverse_rosters", "nflverse rosters"),
            ("nflverse_matchups", "nflverse matchups"),
            ("nfl_official_rosters", "NFL.com rosters"),
            ("nfl_official", "NFL.com status/transactions"),
        ]
        for key, label in labels:
            item = statuses.get(key)
            if item is None:
                if key == "espn":
                    ok = True
                    detail = "snapshot present"
                else:
                    continue
            else:
                ok = bool(item.get("ok", item.get("complete", False)))
                if key == "nfl_official_rosters" and item.get("complete") is not None:
                    ok = bool(item.get("complete"))
                detail = str(item.get("error") or "OK")
            out.append({"source": label, "status": "OK" if ok else "CHECK", "detail": detail})

        grid_cfg = self.model.get("interaction_grid") or {}
        if bool(grid_cfg.get("enabled", False)):
            artifact_path = Path(str(grid_cfg.get("artifact_path") or ""))
            manifest = artifact_path / "manifest.json"
            if manifest.exists():
                detail = f"{grid_cfg.get('artifact_id') or artifact_path.name}; commissioned-only={bool(grid_cfg.get('commissioned_only', True))}"
                out.append({"source": "Interaction grids", "status": "OK", "detail": detail})
            else:
                out.append({"source": "Interaction grids", "status": "CHECK", "detail": "artifact missing; neutral correction fallback"})
        return out

    def _operational_roster(self, roster: list[dict[str, Any]]) -> list[dict[str, Any]]:
        assert self.ctx is not None
        rows: list[dict[str, Any]] = []
        for player in roster:
            p = dict(player)
            state = self.ctx.yield_state(p, self.week)
            p["projection_points"] = state.operational_mean_ppg
            p["projection_source"] = f"V028_OPERATIONAL:{state.kinematic_factor_source}:{state.interaction_factor_source}"
            p["kinematic_factor_mean"] = state.kinematic_factor_mean
            p["matchup_opponent"] = state.matchup_opponent
            availability = self.ctx.availability_state(p, self.week)
            p["active_probability"] = availability.p_active
            p["expected_workload_given_active"] = availability.expected_workload_given_active
            rows.append(p)
        return rows

    def _lineup_rows(self, lineup) -> list[dict[str, Any]]:
        assert self.ctx is not None
        out: list[dict[str, Any]] = []
        for row in lineup.rows:
            p = dict(row)
            state = self.ctx.yield_state(p, self.week)
            availability = self.ctx.availability_state(p, self.week)
            timing = self.ctx.lock_timing(p, self.week)
            status, status_source = availability_status(p)
            timing_dict = timing.to_dict()
            out.append({
                "slot": p.get("display_slot") or p.get("assigned_slot"),
                "espn_id": _int(p.get("espn_id")),
                "name": p.get("name"),
                "position": p.get("position"),
                "team": p.get("nfl_team"),
                "opponent": state.matchup_opponent,
                "mean": state.operational_mean_ppg,
                "sd": state.predictive_sd_ppg,
                "p_active": availability.p_active,
                "p_full_given_active": availability.p_full_given_active,
                "p_full": availability.p_full,
                "p_limited": availability.p_limited,
                "p_out": availability.p_out,
                "limited_fraction": availability.limited_workload_fraction,
                "expected_workload_given_active": availability.expected_workload_given_active,
                "base_p_active": availability.base_p_active,
                "base_p_full_given_active": availability.base_p_full_given_active,
                "availability_evidence_level": availability.evidence_level,
                "availability_posterior_method": availability.posterior_method,
                "availability_calibration_status": availability.calibration_status,
                "practice_source": availability.practice_source,
                "practice_sequence": list(availability.practice_sequence),
                "hours_to_kickoff": availability.hours_to_kickoff,
                "availability_evidence": [item.to_dict() for item in availability.evidence],
                "status": status,
                "status_source": status_source,
                "k": state.kinematic_factor_mean,
                "interaction_factor": state.interaction_factor_mean,
                "interaction_delta_ppg": state.interaction_delta_ppg,
                "interaction_sd_ppg": state.interaction_sd_ppg,
                "interaction_source": state.interaction_factor_source,
                "interaction_artifact_id": state.interaction_artifact_id,
                "interaction_baseline_source": state.interaction_baseline_source,
                "interaction_support": state.interaction_support,
                "interaction_components": state.interaction_components,
                "pre_matchup": state.pre_matchup_operational_mean_ppg,
                "matchup_model": state.matchup_model_mean_ppg,
                "espn": state.espn_anchor_ppg,
                "espn_anchor_kind": state.espn_anchor_kind,
                "model": state.model_mean_ppg,
                **timing_dict,
                "lineup_locked": bool(p.get("lineup_locked")),
            })
        return out

    def dashboard_state(
        self, progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        assert self.ctx is not None
        opponent_work = self.ctx.predictive_opponent_work()
        work = self._predictive_evaluation_work()
        total_work = opponent_work + 3 * work
        self.ctx.ensure_predictive_opponent_reference(
            progress_callback, progress_offset=0, progress_total=total_work,
            progress_label="opponent reference",
        )
        baseline, _utility_scenarios, weekly = self._baseline(
            progress_callback, progress_offset=opponent_work, progress_total=total_work
        )
        idealized_active_baseline, _idealized_active_utility, idealized_active_weekly = self._idealized_active_baseline(
            progress_callback, progress_offset=opponent_work + work, progress_total=total_work
        )
        idealized_baseline, _idealized_utility, idealized_weekly = self._idealized_baseline(
            progress_callback, progress_offset=opponent_work + 2 * work, progress_total=total_work
        )
        if progress_callback is not None:
            progress_callback(total_work, total_work, "finalizing dashboard")
        week_ix = self.week - 1
        user_scores = np.asarray(weekly[:, week_ix], dtype=float)
        idealized_active_scores = np.asarray(idealized_active_weekly[:, week_ix], dtype=float)
        idealized_scores = np.asarray(idealized_weekly[:, week_ix], dtype=float)
        opponent_scores = np.asarray(self.ctx.opponent_predictive[:, week_ix], dtype=float)
        margins = user_scores - opponent_scores
        idealized_active_margins = idealized_active_scores - opponent_scores
        idealized_margins = idealized_scores - opponent_scores
        win = float(np.mean((margins > 0).astype(float) + 0.5 * (margins == 0)))
        idealized_active_win = float(np.mean((idealized_active_margins > 0).astype(float) + 0.5 * (idealized_active_margins == 0)))
        idealized_win = float(np.mean((idealized_margins > 0).astype(float) + 0.5 * (idealized_margins == 0)))
        opponent_id = find_week_opponent(self.snapshot, int(self.team.get("team_id")))
        opponent = self._team_by_id(opponent_id)
        opponent_roster = self.ctx.all_team_rosters.get(int(opponent_id), []) if opponent_id is not None else []
        opponent_operational = self._operational_roster(opponent_roster)
        opponent_planning = optimize_lineup(
            opponent_operational, self.league, self.model, use_expected_availability=True
        ) if opponent_operational else None

        operational = self._operational_roster(self.ctx.roster)
        planning = optimize_lineup(operational, self.league, self.model, use_expected_availability=True)
        uncertain_ids = {
            _int(p.get("espn_id"))
            for p in operational
            if availability_status(p)[0] in {"QUESTIONABLE", "DOUBTFUL"}
        }
        uncertain_ids.discard(None)
        nominal = optimize_lineup(
            operational,
            self.league,
            self.model,
            force_active={int(x) for x in uncertain_ids},
            use_expected_availability=False,
        )

        planning_rows = self._lineup_rows(planning)
        opponent_planning_rows = self._lineup_rows(opponent_planning) if opponent_planning is not None else []
        user_by_slot = {str(r.get("slot")): r for r in planning_rows}
        opp_by_slot = {str(r.get("slot")): r for r in opponent_planning_rows}
        slot_deltas: list[dict[str, Any]] = []
        for slot in CANONICAL_SLOTS:
            ours = user_by_slot.get(slot)
            theirs = opp_by_slot.get(slot)
            if ours is None and theirs is None:
                continue
            us_mean = float((ours or {}).get("mean") or 0.0)
            opp_mean = float((theirs or {}).get("mean") or 0.0)
            slot_deltas.append({
                "slot": slot,
                "us_name": (ours or {}).get("name"),
                "opponent_name": (theirs or {}).get("name"),
                "us_mean": us_mean,
                "opponent_mean": opp_mean,
                "delta": us_mean - opp_mean,
            })

        planning_selection = {
            str(r["slot"]): int(r["espn_id"])
            for r in planning_rows
            if r.get("espn_id") is not None
        }
        fixed_planning_win = None
        fixed_planning_summary = None
        if set(planning_selection) == set(CANONICAL_SLOTS):
            fixed_total, _fixed_rows = self._fixed_lineup_samples(planning_selection)
            fixed_margin = fixed_total - opponent_scores
            fixed_planning_win = float(np.mean((fixed_margin > 0).astype(float) + 0.5 * (fixed_margin == 0)))
            fixed_planning_summary = {**_quantiles(fixed_total), "histogram": _histogram(fixed_total)}

        timing_rows = [self.ctx.lock_timing(p, self.week) for p in self.ctx.roster]
        timing_complete = bool(timing_rows) and all(t.kickoff is not None for t in timing_rows)

        return {
            "season": self.season,
            "mc_scenarios": self.ctx.predictive_scenarios,
            "week": self.week,
            "snapshot_utc": self.snapshot.get("snapshot_utc"),
            "team_id": _int(self.team.get("team_id")),
            "team_name": self.team.get("name"),
            "opponent_team_id": opponent_id,
            "opponent_name": opponent.get("name") if opponent else "League reference",
            "waiver_rank": self.team.get("waiver_rank"),
            "baseline": asdict(baseline),
            "idealized_active_baseline": asdict(idealized_active_baseline),
            "idealized_baseline": asdict(idealized_baseline),
            "weekly_win_probability": win,
            "realistic_policy_win_probability": win,
            "idealized_active_policy_win_probability": idealized_active_win,
            "idealized_policy_win_probability": idealized_win,
            "user_week": {**_quantiles(user_scores), "histogram": _histogram(user_scores)},
            "idealized_active_user_week": {**_quantiles(idealized_active_scores), "histogram": _histogram(idealized_active_scores)},
            "idealized_user_week": {**_quantiles(idealized_scores), "histogram": _histogram(idealized_scores)},
            "opponent_week": {**_quantiles(opponent_scores), "histogram": _histogram(opponent_scores)},
            "margin": {**_quantiles(margins), "histogram": _histogram(margins)},
            "planning_lineup": planning_rows,
            "nominal_lineup": self._lineup_rows(nominal),
            "opponent_planning_lineup": opponent_planning_rows,
            "matchup_slot_deltas": slot_deltas,
            "fixed_planning_win_probability": fixed_planning_win,
            "fixed_planning_week": fixed_planning_summary,
            "contingency_policy_value": (win - fixed_planning_win) if fixed_planning_win is not None else None,
            "realistic_backup_policy_value": (win - fixed_planning_win) if fixed_planning_win is not None else None,
            "idealized_active_backup_policy_value": (idealized_active_win - fixed_planning_win) if fixed_planning_win is not None else None,
            "idealized_backup_policy_value": (idealized_win - fixed_planning_win) if fixed_planning_win is not None else None,
            "status_timing_inflation": idealized_active_win - win,
            "workload_information_inflation": idealized_win - idealized_active_win,
            "information_timing_inflation": idealized_win - win,
            "timing_complete": timing_complete,
            "policy_timing_fallback": not timing_complete,
            "source_health": self.source_health(),
        }

    def roster_players(self) -> list[dict[str, Any]]:
        assert self.ctx is not None
        return [self._player_row(p, scope="ROSTER") for p in self.ctx.roster]

    def opponent_players(self) -> list[dict[str, Any]]:
        assert self.ctx is not None
        opponent_id = find_week_opponent(self.snapshot, int(self.team.get("team_id")))
        roster = self.ctx.all_team_rosters.get(int(opponent_id), []) if opponent_id is not None else []
        return [self._player_row(p, scope="OPPONENT") for p in roster]

    def available_players(self) -> list[dict[str, Any]]:
        assert self.ctx is not None
        rows = [self._player_row(p, scope="AVAILABLE") for p in self.ctx.actionable_available]
        rows.sort(key=lambda r: (float(r.get("operational_mean") or 0), float(r.get("season_ppg") or 0)), reverse=True)
        return rows

    def _player_row(self, player: dict[str, Any], scope: str) -> dict[str, Any]:
        assert self.ctx is not None
        state = self.ctx.yield_state(player, self.week)
        availability = self.ctx.availability_state(player, self.week)
        timing = self.ctx.lock_timing(player, self.week)
        status, source = availability_status(player)
        return {
            "scope": scope,
            "espn_id": _int(player.get("espn_id")),
            "name": player.get("name"),
            "position": player.get("position"),
            "team": player.get("nfl_team"),
            "fantasy_status": player.get("fantasy_status"),
            "lineup_slot": player.get("lineup_slot"),
            "droppable": player.get("droppable"),
            "locked": player.get("lineup_locked"),
            "status": status,
            "status_source": source,
            "p_active": availability.p_active,
            "p_full_given_active": availability.p_full_given_active,
            "p_full": availability.p_full,
            "p_limited": availability.p_limited,
            "p_out": availability.p_out,
            "limited_fraction": availability.limited_workload_fraction,
            "expected_workload_given_active": availability.expected_workload_given_active,
            "base_p_active": availability.base_p_active,
            "base_p_full_given_active": availability.base_p_full_given_active,
            "availability_evidence_level": availability.evidence_level,
            "availability_posterior_method": availability.posterior_method,
            "availability_calibration_status": availability.calibration_status,
            "practice_source": availability.practice_source,
            "practice_sequence": list(availability.practice_sequence),
            "hours_to_kickoff": availability.hours_to_kickoff,
            "availability_evidence": [item.to_dict() for item in availability.evidence],
            **timing.to_dict(),
            "operational_mean": state.operational_mean_ppg,
            "predictive_sd": state.predictive_sd_ppg,
            "model_mean": state.model_mean_ppg,
            "espn_anchor": state.espn_anchor_ppg,
            "espn_anchor_kind": state.espn_anchor_kind,
            "delta_model_espn": state.delta_model_minus_espn,
            "k": state.kinematic_factor_mean,
            "k_sd": state.kinematic_sd_ppg,
            "opponent": state.matchup_opponent,
            "home": state.matchup_home,
            "season_ppg": _finite(player.get("season_ppg")),
            "adds24h": _int(player.get("sleeper_trending_add_24h")),
            "percent_owned": _finite(player.get("percent_owned")),
        }

    def player_diagnostic(self, espn_id: int) -> dict[str, Any]:
        assert self.ctx is not None
        pid = int(espn_id)
        pools = [
            ("ROSTER", self.ctx.roster),
            ("AVAILABLE", self.ctx.actionable_available),
        ]
        for tid, roster in self.ctx.all_team_rosters.items():
            if tid != self.ctx.team_id:
                pools.append(("LEAGUE_ROSTER", roster))
        found: dict[str, Any] | None = None
        scope = "UNKNOWN"
        for pool_scope, pool in pools:
            found = next((p for p in pool if _int(p.get("espn_id")) == pid), None)
            if found is not None:
                scope = pool_scope
                break
        if found is None:
            raise SeasonGuiError(f"Player ESPN ID {pid} not found in current snapshot")
        state = self.ctx.yield_state(found, self.week)
        row = self._player_row(found, scope=scope)
        row.update({
            "pre_matchup_mean": state.pre_matchup_operational_mean_ppg,
            "matchup_model_mean": state.matchup_model_mean_ppg,
            "game_sd": state.game_sd_ppg,
            "model_sd": state.model_sd_ppg,
            "kinematic_sd": state.kinematic_sd_ppg,
            "total_sd": state.predictive_sd_ppg,
            "anchor_weight": state.espn_anchor_weight,
            "anchor_z": state.espn_anchor_z,
            "team_implied_points": state.matchup_team_implied_points,
            "defense_current_weight": state.matchup_defense_current_weight,
            "kinematic_source": state.kinematic_factor_source,
            "kinematic_components": state.kinematic_components,
            "kinematic_zscores": state.kinematic_zscores,
            "interaction_factor": state.interaction_factor_mean,
            "interaction_source": state.interaction_factor_source,
            "interaction_delta_ppg": state.interaction_delta_ppg,
            "interaction_sd_ppg": state.interaction_sd_ppg,
            "interaction_artifact_id": state.interaction_artifact_id,
            "interaction_baseline_source": state.interaction_baseline_source,
            "interaction_support": state.interaction_support,
            "interaction_components": state.interaction_components,
            "dst_components": state.dst_component_expectation,
            "projection_source": state.projection_source,
        })
        return row

    def default_lineup_selection(self) -> dict[str, int]:
        assert self.ctx is not None
        operational = self._operational_roster(self.ctx.roster)
        lineup = optimize_lineup(operational, self.league, self.model, use_expected_availability=True)
        out: dict[str, int] = {}
        for row in lineup.rows:
            slot = str(row.get("display_slot") or row.get("assigned_slot"))
            pid = _int(row.get("espn_id"))
            if pid is not None:
                out[slot] = pid
        return out

    def lineup_options(self, slot: str) -> list[dict[str, Any]]:
        assert self.ctx is not None
        eligible = SLOT_POSITIONS.get(slot)
        if not eligible:
            raise SeasonGuiError(f"Unknown lineup slot: {slot}")
        rows = [self._player_row(p, scope="ROSTER") for p in self.ctx.roster if str(p.get("position")) in eligible]
        rows.sort(key=lambda r: float(r.get("operational_mean") or 0), reverse=True)
        return rows

    def _sample_player_week(
        self,
        player: dict[str, Any],
        *,
        mode: str = "MODEL",
        limited_fraction: float = 0.65,
    ) -> np.ndarray:
        assert self.ctx is not None
        pid = _int(player.get("espn_id"))
        if pid is None:
            return np.zeros(self.ctx.predictive_scenarios, dtype=float)
        state = self.ctx.yield_state(player, self.week)
        if state.position == "DST" and state.dst_component_expectation:
            scores = simulate_dst_component_points(
                state.dst_component_expectation,
                scenarios=self.ctx.predictive_scenarios,
                seed=self.ctx.seed + 1000003 * int(pid) + 97 * int(self.week),
                target_mean=state.operational_mean_ppg,
            )
            scores = (
                scores
                + state.model_sd_ppg * self.ctx.epistemic_normals(pid)
                + state.kinematic_sd_ppg * self.ctx.kinematic_normals(pid)[:, self.week - 1]
            )
        else:
            scores = sample_conditional_points(
                state,
                self.ctx.epistemic_normals(pid),
                self.ctx.game_normals(pid)[:, self.week - 1],
                self.ctx.kinematic_normals(pid)[:, self.week - 1],
                self.ctx.interaction_normals(pid)[:, self.week - 1],
            )
        mode = str(mode or "MODEL").upper()
        if mode not in AVAILABILITY_MODES:
            raise SeasonGuiError(f"Unknown availability mode: {mode}")
        if mode == "OUT":
            return np.zeros_like(scores)
        if mode == "FULL":
            return scores
        if mode == "LIMITED":
            frac = min(max(float(limited_fraction), 0.0), 1.0)
            return frac * scores
        availability = self.ctx.availability_state(player, self.week)
        active = self.ctx.predictive_uniforms(pid)[:, self.week - 1] < availability.p_active
        full = self.ctx.workload_uniforms(pid)[:, self.week - 1] < availability.p_full_given_active
        scale = np.where(full, 1.0, availability.limited_workload_fraction)
        return np.where(active, scale * scores, 0.0)

    def _fixed_lineup_samples(
        self,
        selection: dict[str, int],
        *,
        availability_modes: dict[int, str] | None = None,
        limited_fractions: dict[int, float] | None = None,
    ) -> tuple[np.ndarray, list[dict[str, Any]]]:
        """Sample a fixed nine-player lineup without hindsight substitutions.

        This is intentionally distinct from the core contingent policy baseline, which
        can re-optimize after an availability branch is known. It is used by the GUI to
        make the value of contingency/backup planning explicit.
        """
        assert self.ctx is not None
        availability_modes = {int(k): str(v).upper() for k, v in (availability_modes or {}).items()}
        limited_fractions = {int(k): float(v) for k, v in (limited_fractions or {}).items()}
        if set(selection) != set(CANONICAL_SLOTS):
            missing = sorted(set(CANONICAL_SLOTS) - set(selection))
            extra = sorted(set(selection) - set(CANONICAL_SLOTS))
            raise SeasonGuiError(f"Lineup must contain all nine slots; missing={missing}, extra={extra}")
        ids = [int(selection[s]) for s in CANONICAL_SLOTS]
        if len(ids) != len(set(ids)):
            raise SeasonGuiError("A player cannot occupy more than one lineup slot")
        by_id = {_int(p.get("espn_id")): p for p in self.ctx.roster}
        total = np.zeros(self.ctx.predictive_scenarios, dtype=float)
        rows: list[dict[str, Any]] = []
        for slot in CANONICAL_SLOTS:
            pid = int(selection[slot])
            player = by_id.get(pid)
            if player is None:
                raise SeasonGuiError(f"Player {pid} is not on the current roster")
            pos = str(player.get("position") or "")
            if pos not in SLOT_POSITIONS[slot]:
                raise SeasonGuiError(f"{player.get('name')} ({pos}) is not eligible for {slot}")
            mode = availability_modes.get(pid, "MODEL")
            frac = limited_fractions.get(pid, 0.65)
            samples = self._sample_player_week(player, mode=mode, limited_fraction=frac)
            total += samples
            state = self.ctx.yield_state(player, self.week)
            availability = self.ctx.availability_state(player, self.week)
            timing = self.ctx.lock_timing(player, self.week)
            rows.append({
                "slot": slot,
                "espn_id": pid,
                "name": player.get("name"),
                "position": player.get("position"),
                "mode": mode,
                "limited_fraction": frac if mode == "LIMITED" else None,
                "mean": float(np.mean(samples)),
                "conditional_mean": state.operational_mean_ppg,
                "p_active": availability.p_active,
                "p_full_given_active": availability.p_full_given_active,
                "p_full": availability.p_full,
                "p_limited": availability.p_limited,
                "p_out": availability.p_out,
                "k": state.kinematic_factor_mean,
                **timing.to_dict(),
            })
        return total, rows

    def evaluate_hypothetical_lineup(
        self,
        selection: dict[str, int],
        *,
        availability_modes: dict[int, str] | None = None,
        limited_fractions: dict[int, float] | None = None,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        assert self.ctx is not None
        availability_modes = {int(k): str(v).upper() for k, v in (availability_modes or {}).items()}
        limited_fractions = {int(k): float(v) for k, v in (limited_fractions or {}).items()}

        total, rows = self._fixed_lineup_samples(
            selection,
            availability_modes=availability_modes,
            limited_fractions=limited_fractions,
        )

        opponent = np.asarray(self.ctx.opponent_predictive[:, self.week - 1], dtype=float)
        margin = total - opponent
        win = float(np.mean((margin > 0).astype(float) + 0.5 * (margin == 0)))

        # Realistic lock-aware policy baseline.
        work = self._predictive_evaluation_work()
        total_work = 3 * work
        policy_baseline, _u, policy_weekly = self._baseline(
            progress_callback, progress_offset=0, progress_total=total_work
        )
        policy_total = np.asarray(policy_weekly[:, self.week - 1], dtype=float)
        policy_margin = policy_total - opponent
        policy_win = float(np.mean((policy_margin > 0).astype(float) + 0.5 * (policy_margin == 0)))

        # Status-idealized branch: all active/inactive states known before any lock,
        # while FULL/LIMITED workload remains latent.
        idealized_active_baseline, _iau, idealized_active_weekly = self._idealized_active_baseline(
            progress_callback, progress_offset=work, progress_total=total_work
        )
        idealized_active_total = np.asarray(idealized_active_weekly[:, self.week - 1], dtype=float)
        idealized_active_margin = idealized_active_total - opponent
        idealized_active_win = float(np.mean((idealized_active_margin > 0).astype(float) + 0.5 * (idealized_active_margin == 0)))

        # Full idealized upper bound: complete OUT/FULL/LIMITED branch known before any lock.
        idealized_baseline, _iu, idealized_weekly = self._idealized_baseline(
            progress_callback, progress_offset=2 * work, progress_total=total_work
        )
        idealized_total = np.asarray(idealized_weekly[:, self.week - 1], dtype=float)
        idealized_margin = idealized_total - opponent
        idealized_win = float(np.mean((idealized_margin > 0).astype(float) + 0.5 * (idealized_margin == 0)))

        # Fixed default lineup baseline: same nine pregame selections, MODEL availability, no backups.
        default_selection = self.default_lineup_selection()
        fixed_default_total, fixed_default_rows = self._fixed_lineup_samples(default_selection)
        fixed_default_margin = fixed_default_total - opponent
        fixed_default_win = float(np.mean((fixed_default_margin > 0).astype(float) + 0.5 * (fixed_default_margin == 0)))

        fixed_rows_by_slot = {str(r["slot"]): r for r in fixed_default_rows}
        selected_rows_by_slot = {str(r["slot"]): r for r in rows}
        changes: list[dict[str, Any]] = []
        for slot in CANONICAL_SLOTS:
            base = fixed_rows_by_slot[slot]
            sel = selected_rows_by_slot[slot]
            changed_player = int(base["espn_id"]) != int(sel["espn_id"])
            changed_mode = str(sel.get("mode")) != "MODEL"
            changes.append({
                "slot": slot,
                "baseline_espn_id": int(base["espn_id"]),
                "baseline_name": base.get("name"),
                "selected_espn_id": int(sel["espn_id"]),
                "selected_name": sel.get("name"),
                "mode": sel.get("mode"),
                "baseline_mean": float(base.get("mean") or 0.0),
                "selected_mean": float(sel.get("mean") or 0.0),
                "delta_mean": float(sel.get("mean") or 0.0) - float(base.get("mean") or 0.0),
                "changed": bool(changed_player or changed_mode),
            })

        return {
            "rows": rows,
            "changes": changes,
            "team": {**_quantiles(total), "histogram": _histogram(total)},
            "fixed_baseline_team": {**_quantiles(fixed_default_total), "histogram": _histogram(fixed_default_total)},
            "policy_baseline_team": {**_quantiles(policy_total), "histogram": _histogram(policy_total)},
            "idealized_active_policy_team": {**_quantiles(idealized_active_total), "histogram": _histogram(idealized_active_total)},
            "idealized_policy_team": {**_quantiles(idealized_total), "histogram": _histogram(idealized_total)},
            "opponent": {**_quantiles(opponent), "histogram": _histogram(opponent)},
            "margin": {**_quantiles(margin), "histogram": _histogram(margin)},
            "win_probability": win,
            "fixed_baseline_win_probability": fixed_default_win,
            "policy_baseline_win_probability": policy_win,
            "realistic_policy_win_probability": policy_win,
            "idealized_active_policy_win_probability": idealized_active_win,
            "idealized_policy_win_probability": idealized_win,
            "delta_vs_fixed_win_probability": win - fixed_default_win,
            "delta_vs_policy_win_probability": win - policy_win,
            "contingency_policy_value": policy_win - fixed_default_win,
            "realistic_backup_policy_value": policy_win - fixed_default_win,
            "idealized_active_backup_policy_value": idealized_active_win - fixed_default_win,
            "idealized_backup_policy_value": idealized_win - fixed_default_win,
            "status_timing_inflation": idealized_active_win - policy_win,
            "workload_information_inflation": idealized_win - idealized_active_win,
            "information_timing_inflation": idealized_win - policy_win,
            # Backward-compatible aliases used by the original v0.24 GUI/tests.
            "baseline_win_probability": policy_win,
            "delta_win_probability": win - policy_win,
            "baseline_week_mean": float(policy_baseline.current_week_expected_points),
            "mc_scenarios": self.ctx.predictive_scenarios,
        }

    def legal_drop_players(self) -> list[dict[str, Any]]:
        assert self.ctx is not None
        rows = [
            self._player_row(p, scope="ROSTER") for p in self.ctx.roster
            if _legal_drop(p) and str(p.get("position") or "").upper() in PLAYER_POSITIONS
        ]
        rows.sort(key=lambda r: float(r.get("operational_mean") or 0))
        return rows

    def evaluate_single_add_drop(
        self, add_espn_id: int, drop_espn_id: int,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        assert self.ctx is not None
        add_id = int(add_espn_id)
        drop_id = int(drop_espn_id)
        add = next((p for p in self.ctx.actionable_available if _int(p.get("espn_id")) == add_id), None)
        drop = next((p for p in self.ctx.roster if _int(p.get("espn_id")) == drop_id), None)
        if add is None:
            raise SeasonGuiError(f"Add player {add_id} is not in the actionable ESPN pool")
        if str(add.get("position") or "").upper() not in PLAYER_POSITIONS:
            raise SeasonGuiError("v0.31 FA/waiver laboratory is player-channel only; use the defense/kicker channel for specialists")
        if drop is None:
            raise SeasonGuiError(f"Drop player {drop_id} is not on your roster")
        if str(drop.get("position") or "").upper() not in PLAYER_POSITIONS:
            raise SeasonGuiError("v0.31 FA/waiver laboratory cannot exchange a player for a specialist channel asset")
        if not _legal_drop(drop):
            raise SeasonGuiError(f"{drop.get('name')} is not currently a legal drop")
        if not _legal_roster_after_add_drop(self.ctx.roster, add, drop, self.league):
            raise SeasonGuiError("That add/drop would violate roster or position-limit constraints")
        new_roster = [p for p in self.ctx.roster if _int(p.get("espn_id")) != drop_id] + [dict(add)]
        work = self._predictive_evaluation_work()
        total_work = 2 * work
        baseline, baseline_scenario_utility, baseline_weekly = self._baseline(
            progress_callback, progress_offset=0, progress_total=total_work
        )
        utility, scenario_utility, weekly = evaluate_roster_predictive(
            new_roster, self.ctx,
            progress_callback=progress_callback, progress_offset=work,
            progress_total=total_work, progress_label="action roster",
        )
        raw_delta_scenario = np.asarray(scenario_utility) - np.asarray(baseline_scenario_utility)

        # fixed6 authoritative counterfactual: the dropped player re-enters the
        # league state instead of disappearing.  The released-player transition is
        # evaluated with the same predictive football generator at the configured
        # small paired N; v0.36 preserves that order-1 response and adds bounded
        # higher-order player-channel release propagation to the field.
        release_response = released_player_league_state_response(
            drop, self.ctx,
            scenarios=int(self.ctx.cfg.get("league_state_response_scenarios", 256)),
        )
        shift = np.asarray(
            release_response.get("opponent_reference_shift_ppg_by_week") or [0.0] * 17,
            dtype=float,
        )
        if shift.shape != (17,):
            shift = np.zeros(17, dtype=float)
        counterfactual_opponent = np.asarray(self.ctx.opponent_predictive, dtype=float) + shift[None, :]
        league_scenario_utility = _scenario_h2h_utility_against(weekly, counterfactual_opponent, self.ctx)
        delta_scenario = np.asarray(league_scenario_utility) - np.asarray(baseline_scenario_utility)
        utility = replace(
            utility,
            utility=float(np.mean(league_scenario_utility)),
            expected_h2h_win_probability=float(np.mean(league_scenario_utility)),
        )

        # The future-roster ensemble is retained only as a diagnostic response probe.
        before_option = roster_option_scarcity_value(self.ctx.roster, self.ctx)
        after_option = roster_option_scarcity_value(new_roster, self.ctx)
        option_adj = _option_scarcity_utility_adjustment(before_option, after_option, self.ctx)
        option_adj["delta_future_option_utility"] = 0.0
        option_adj["delta_replacement_scarcity_utility"] = 0.0
        option_adj["delta_total_utility"] = 0.0
        raw_p16, raw_p84 = _paired_mean_interval(
            raw_delta_scenario,
            seed=self.ctx.seed + 31 * add_id + 17 * drop_id,
            draws=int(self.ctx.cfg.get("paired_mean_interval_resamples", 1000)),
        )
        p16, p84 = _paired_mean_interval(
            delta_scenario,
            seed=self.ctx.seed + 31 * add_id + 17 * drop_id,
            draws=int(self.ctx.cfg.get("paired_mean_interval_resamples", 1000)),
        )
        classification, raw_classification, combined_classification = _classify_market_action(
            raw_delta_scenario, delta_scenario, self.ctx.cfg,
            raw_p16=raw_p16, adjusted_p16=p16,
        )
        fantasy_status = str(add.get("fantasy_status") or "").upper()
        blocker_rows = [] if fantasy_status == "FREEAGENT" else waiver_blocker_diagnostics(add, self.ctx)
        p_acquire = 1.0 if fantasy_status == "FREEAGENT" else waiver_acquisition_probability(add, self.ctx, blockers=blocker_rows)
        week_delta = np.asarray(weekly[:, self.week - 1]) - np.asarray(baseline_weekly[:, self.week - 1])
        add_state = self.ctx.yield_state(add, self.week)
        return {
            "add": self._player_row(add, scope="AVAILABLE"),
            "drop": self._player_row(drop, scope="ROSTER"),
            "fantasy_status": fantasy_status,
            "delta_h2h_mean": float(np.mean(raw_delta_scenario)),
            "delta_h2h_sd": float(np.std(raw_delta_scenario, ddof=1)) if len(raw_delta_scenario) > 1 else 0.0,
            "delta_h2h_p16": raw_p16,
            "delta_h2h_p84": raw_p84,
            "p_better": float(np.mean(raw_delta_scenario > 0)),
            "p_tie": float(np.mean(raw_delta_scenario == 0)),
            "p_worse": float(np.mean(raw_delta_scenario < 0)),
            "combined_delta_mean": float(np.mean(delta_scenario)),
            "combined_delta_p16": p16,
            "combined_delta_p84": p84,
            "p_combined_better": float(np.mean(delta_scenario > 0)),
            "p_combined_tie": float(np.mean(delta_scenario == 0)),
            "p_combined_worse": float(np.mean(delta_scenario < 0)),
            "league_state_delta_mean": float(np.mean(delta_scenario)),
            "league_state_delta_p16": p16,
            "league_state_delta_p84": p84,
            "p_league_state_better": float(np.mean(delta_scenario > 0)),
            "p_league_state_tie": float(np.mean(delta_scenario == 0)),
            "p_league_state_worse": float(np.mean(delta_scenario < 0)),
            "classification": classification,
            "raw_classification": raw_classification,
            "combined_classification": combined_classification,
            "p_acquire": p_acquire,
            "expected_delta_utility": float(p_acquire * np.mean(delta_scenario)),
            "option_scarcity": option_adj,
            "candidate_option_support": _market_projection_support(add, self.ctx),
            "release_response": release_response,
            "week_delta": float(utility.current_week_expected_points - baseline.current_week_expected_points),
            "season_ppg_delta": float(utility.season_expected_lineup_ppg - baseline.season_expected_lineup_ppg),
            "insurance_delta": float(utility.bench_insurance_ppg - baseline.bench_insurance_ppg),
            "bye_floor_delta": float(utility.bye_floor_points - baseline.bye_floor_points),
            "baseline_utility": asdict(baseline),
            "action_utility": asdict(utility),
            "baseline_week_distribution": {**_quantiles(np.asarray(baseline_weekly[:, self.week - 1])), "histogram": _histogram(np.asarray(baseline_weekly[:, self.week - 1]))},
            "action_week_distribution": {**_quantiles(np.asarray(weekly[:, self.week - 1])), "histogram": _histogram(np.asarray(weekly[:, self.week - 1]))},
            "week_delta_distribution": {**_quantiles(week_delta), "histogram": _histogram(week_delta)},
            "utility_delta_distribution": {**_quantiles(100.0 * delta_scenario), "histogram": _histogram(100.0 * delta_scenario)},
            "raw_h2h_delta_distribution": {**_quantiles(100.0 * raw_delta_scenario), "histogram": _histogram(100.0 * raw_delta_scenario)},
            "candidate_yield": add_state.to_dict(),
            "waiver_blockers": blocker_rows,
            "waiver_response_model": "UNCALIBRATED_MANAGER_CLAIM_UTILITY_V030" if fantasy_status != "FREEAGENT" else None,
            "mc_scenarios": self.ctx.predictive_scenarios,
        }

    def defense_channel(self, mc_scenarios: int | None = None) -> dict[str, Any]:
        return evaluate_defense_channel(
            self.snapshot, self.league, self.model, values_path=self.values_path,
            team_id=int(self.team.get("team_id")), mc_scenarios=mc_scenarios or self.mc_scenarios,
        )

    def kicker_channel(self, mc_scenarios: int | None = None) -> dict[str, Any]:
        return evaluate_kicker_channel(
            self.snapshot, self.league, self.model, values_path=self.values_path,
            team_id=int(self.team.get("team_id")), mc_scenarios=mc_scenarios or self.mc_scenarios,
        )

    def trade_partners(self) -> list[dict[str, Any]]:
        assert self.ctx is not None
        rows = []
        for team in (self.snapshot.get("espn", self.snapshot).get("teams") or []):
            tid = _int(team.get("team_id"))
            if tid is None or tid == self.ctx.team_id:
                continue
            rows.append({
                "team_id": tid,
                "name": team.get("name"),
                "waiver_rank": team.get("waiver_rank"),
            })
        rows.sort(key=lambda r: str(r.get("name") or ""))
        return rows

    def trade_partner_players(self, team_id: int) -> list[dict[str, Any]]:
        assert self.ctx is not None
        roster = self.ctx.all_team_rosters.get(int(team_id))
        if roster is None:
            raise SeasonGuiError(f"Trade partner team {team_id} not found")
        rows = [
            self._player_row(p, scope="TRADE_PARTNER") for p in roster
            if str(p.get("position") or "").upper() in PLAYER_POSITIONS
        ]
        rows.sort(key=lambda r: float(r.get("season_ppg") or 0.0), reverse=True)
        return rows

    def evaluate_trade_offer(
        self,
        partner_team_id: int,
        give_ids: list[int],
        receive_ids: list[int],
        *,
        progress_callback: Callable[[int, int, str], None] | None = None,
        mc_scenarios: int | None = None,
    ) -> dict[str, Any]:
        try:
            return evaluate_trade(
                self.snapshot, self.league, self.model,
                values_path=self.values_path,
                user_team=self.team,
                partner_team_id=int(partner_team_id),
                give_ids=[int(x) for x in give_ids],
                receive_ids=[int(x) for x in receive_ids],
                mc_scenarios=int(mc_scenarios or self.mc_scenarios),
                progress_callback=progress_callback,
            )
        except ValueError as exc:
            raise SeasonGuiError(str(exc)) from None

    def trade_search_screen(self, limit: int = 20) -> list[dict[str, Any]]:
        return screen_one_for_one_trades(
            self.snapshot, self.league, self.model,
            values_path=self.values_path, user_team=self.team, limit=limit,
        )

    def trade_search(
        self, limit: int = 6,
        *,
        progress_callback: Callable[[int, int, str], None] | None = None,
        mc_scenarios: int | None = None,
    ) -> list[dict[str, Any]]:
        return search_trades(
            self.snapshot, self.league, self.model,
            values_path=self.values_path, user_team=self.team, limit=limit,
            mc_scenarios=mc_scenarios, progress_callback=progress_callback,
        )


    def chat_report_payload(
        self,
        *,
        selection: dict[str, int] | None = None,
        availability_modes: dict[int, str] | None = None,
        limited_fraction: float = 0.65,
        action_result: dict[str, Any] | None = None,
        trade_result: dict[str, Any] | None = None,
        add_espn_id: int | None = None,
        drop_espn_id: int | None = None,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        """Build a compact diagnosis from the exact GUI-service model state.

        This intentionally routes through the same dashboard, lineup-laboratory,
        player-diagnostic, action, and closure methods used by the GUI. It does
        not instantiate a separate optimizer or silently re-read external data.
        """
        assert self.ctx is not None
        dashboard = self.dashboard_state(progress_callback=progress_callback)
        ledger = self.prediction_ledger()
        closure = self.prediction_ledger_summary()
        closure["prospective"] = self.prospective_closure_summary()

        lineup = list(dashboard.get("planning_lineup") or [])
        nominal_points = sum(float(r.get("mean") or 0.0) for r in (dashboard.get("nominal_lineup") or []))
        matchup = {
            "policy_win": dashboard.get("weekly_win_probability"),
            "realistic_win": dashboard.get("realistic_policy_win_probability"),
            "idealized_active_win": dashboard.get("idealized_active_policy_win_probability"),
            "idealized_win": dashboard.get("idealized_policy_win_probability"),
            "fixed_win": dashboard.get("fixed_planning_win_probability"),
            "backup_policy_value": dashboard.get("contingency_policy_value"),
            "realistic_backup_policy_value": dashboard.get("realistic_backup_policy_value"),
            "idealized_active_backup_policy_value": dashboard.get("idealized_active_backup_policy_value"),
            "idealized_backup_policy_value": dashboard.get("idealized_backup_policy_value"),
            "status_timing_inflation": dashboard.get("status_timing_inflation"),
            "workload_information_inflation": dashboard.get("workload_information_inflation"),
            "information_timing_inflation": dashboard.get("information_timing_inflation"),
            "timing_complete": dashboard.get("timing_complete"),
            "our_mean": (dashboard.get("user_week") or {}).get("mean"),
            "our_sd": (dashboard.get("user_week") or {}).get("sd"),
            "our_p10": (dashboard.get("user_week") or {}).get("p10"),
            "our_p90": (dashboard.get("user_week") or {}).get("p90"),
            "opp_mean": (dashboard.get("opponent_week") or {}).get("mean"),
            "opp_sd": (dashboard.get("opponent_week") or {}).get("sd"),
            "margin_mean": (dashboard.get("margin") or {}).get("mean"),
            "margin_sd": (dashboard.get("margin") or {}).get("sd"),
            "nominal_points": nominal_points,
        }

        diag_rows: list[dict[str, Any]] = []
        for row in lineup:
            pid = _int(row.get("espn_id"))
            if pid is None:
                continue
            diag = self.player_diagnostic(pid)
            diag_rows.append(diag)
        diag_rows.sort(key=lambda r: float(r.get("total_sd") or 0.0), reverse=True)
        key_uncertainty = [
            {
                "name": r.get("name"),
                "game_sd": r.get("game_sd"),
                "model_sd": r.get("model_sd"),
                "kinematic_sd": r.get("kinematic_sd"),
                "interaction_sd": r.get("interaction_sd_ppg"),
                "total_sd": r.get("total_sd"),
            }
            for r in diag_rows[:4]
        ]

        # Opponent diagnostics intentionally route through the same player_diagnostic
        # method and the same dashboard planning-lineup rows as the user's team.
        # This makes pipeline symmetry inspectable rather than merely assumed.
        opponent_lineup = list(dashboard.get("opponent_planning_lineup") or [])
        opponent_diag_rows: list[dict[str, Any]] = []
        for row in opponent_lineup:
            pid = _int(row.get("espn_id"))
            if pid is None:
                continue
            opponent_diag_rows.append(self.player_diagnostic(pid))
        opponent_diag_rows.sort(key=lambda r: float(r.get("total_sd") or 0.0), reverse=True)
        opponent_key_uncertainty = [
            {
                "name": r.get("name"),
                "game_sd": r.get("game_sd"),
                "model_sd": r.get("model_sd"),
                "kinematic_sd": r.get("kinematic_sd"),
                "interaction_sd": r.get("interaction_sd_ppg"),
                "total_sd": r.get("total_sd"),
            }
            for r in opponent_diag_rows[:4]
        ]
        opponent_anchor_rows = [
            r for r in opponent_diag_rows
            if r.get("model_mean") is not None
            and r.get("espn_anchor") is not None
            and r.get("delta_model_espn") is not None
        ]
        opponent_anchor_rows.sort(
            key=lambda r: abs(float(r.get("delta_model_espn") or 0.0)), reverse=True
        )
        opponent_anchor_flags = [
            {
                "name": r.get("name"),
                "model": r.get("model_mean"),
                "matchup_model": r.get("matchup_model_mean"),
                "espn": r.get("espn_anchor"),
                "espn_kind": r.get("espn_anchor_kind"),
                "delta": r.get("delta_model_espn"),
                "operational": r.get("operational_mean"),
            }
            for r in opponent_anchor_rows[:5]
            if abs(float(r.get("delta_model_espn") or 0.0)) >= 1.0
        ]

        anchor_rows = [
            r for r in ledger
            if r.get("model") is not None and r.get("espn") is not None and r.get("model_minus_espn") is not None
        ]
        anchor_rows.sort(key=lambda r: abs(float(r.get("model_minus_espn") or 0.0)), reverse=True)
        anchor_flags = [
            {
                "name": r.get("name"),
                "model": r.get("model"),
                "espn": r.get("espn"),
                "delta": r.get("model_minus_espn"),
                "operational": r.get("operational"),
            }
            for r in anchor_rows[:5]
            if abs(float(r.get("model_minus_espn") or 0.0)) >= 1.0
        ]

        hypothetical = None
        if selection is not None and set(selection) == set(CANONICAL_SLOTS):
            modes = {int(k): str(v).upper() for k, v in (availability_modes or {}).items()}
            limited_fractions = {
                int(pid): float(limited_fraction)
                for pid, mode in modes.items()
                if str(mode).upper() == "LIMITED"
            }
            hyp = self.evaluate_hypothetical_lineup(
                {str(k): int(v) for k, v in selection.items()},
                availability_modes=modes,
                limited_fractions=limited_fractions,
            )
            changes = [dict(r) for r in hyp.get("changes") or [] if r.get("changed")]
            hypothetical = {
                "changed": bool(changes),
                "selected_fixed_win": hyp.get("win_probability"),
                "default_fixed_win": hyp.get("fixed_baseline_win_probability"),
                "policy_win": hyp.get("policy_baseline_win_probability"),
                "realistic_policy_win": hyp.get("realistic_policy_win_probability"),
                "idealized_active_policy_win": hyp.get("idealized_active_policy_win_probability"),
                "idealized_policy_win": hyp.get("idealized_policy_win_probability"),
                "status_timing_inflation": hyp.get("status_timing_inflation"),
                "workload_information_inflation": hyp.get("workload_information_inflation"),
                "timing_inflation": hyp.get("information_timing_inflation"),
                "delta_vs_default_fixed": hyp.get("delta_vs_fixed_win_probability"),
                "selected_score_mean": (hyp.get("team") or {}).get("mean"),
                "selected_score_sd": (hyp.get("team") or {}).get("sd"),
                "default_score_mean": (hyp.get("fixed_baseline_team") or {}).get("mean"),
                "changes": changes,
            }

        if action_result is None and add_espn_id is not None and drop_espn_id is not None:
            action_result = self.evaluate_single_add_drop(int(add_espn_id), int(drop_espn_id))
        action = None
        if action_result:
            add = action_result.get("add") or {}
            drop = action_result.get("drop") or {}
            action = {
                "add_espn_id": add.get("espn_id"),
                "add_name": add.get("name"),
                "add_position": add.get("position"),
                "drop_espn_id": drop.get("espn_id"),
                "drop_name": drop.get("name"),
                "drop_position": drop.get("position"),
                "delta_h2h_mean": action_result.get("delta_h2h_mean"),
                "delta_h2h_p16": action_result.get("delta_h2h_p16"),
                "delta_h2h_p84": action_result.get("delta_h2h_p84"),
                "p_better": action_result.get("p_better"),
                "p_tie": action_result.get("p_tie"),
                "p_worse": action_result.get("p_worse"),
                "p_acquire": action_result.get("p_acquire"),
                "expected_delta_utility": action_result.get("expected_delta_utility"),
                "week_delta": action_result.get("week_delta"),
                "season_ppg_delta": action_result.get("season_ppg_delta"),
                "classification": action_result.get("classification"),
            }

        trade = None
        if trade_result:
            response = trade_result.get("response") or {}
            user_delta = ((trade_result.get("user") or {}).get("delta_season_ppg") or {})
            partner_delta = ((trade_result.get("partner") or {}).get("delta_season_ppg") or {})
            trade = {
                "partner_team_id": (trade_result.get("partner_team") or {}).get("team_id"),
                "partner_name": (trade_result.get("partner_team") or {}).get("name"),
                "give": [x.get("name") for x in trade_result.get("give") or []],
                "receive": [x.get("name") for x in trade_result.get("receive") or []],
                "user_auto_drops": [x.get("name") for x in trade_result.get("user_auto_drops") or []],
                "partner_auto_drops": [x.get("name") for x in trade_result.get("partner_auto_drops") or []],
                "user_auto_adds": [x.get("name") for x in trade_result.get("user_auto_adds") or []],
                "partner_auto_adds": [x.get("name") for x in trade_result.get("partner_auto_adds") or []],
                "our_delta_season_ppg": user_delta.get("mean"),
                "our_p_better": user_delta.get("p_better"),
                "partner_delta_season_ppg": partner_delta.get("mean"),
                "partner_p_better": partner_delta.get("p_better"),
                "p_accept": response.get("p_accept"),
                "p_counter": response.get("p_counter"),
                "p_reject": response.get("p_reject"),
                "response_model": response.get("model"),
                "expected_offer_value": trade_result.get("expected_offer_value"),
                "classification": trade_result.get("classification"),
                "mc_scenarios": trade_result.get("mc_scenarios"),
            }

        flags: list[str] = []
        uncertain = [r for r in lineup if r.get("p_active") is not None and 0.0 < float(r["p_active"]) < 0.95]
        if uncertain:
            flags.append(
                f"{len(uncertain)} planning starters have sub-95% modeled availability: "
                + ", ".join(f"{r.get('name')}={100*float(r['p_active']):.0f}%" for r in uncertain)
            )
        opponent_uncertain = [
            r for r in opponent_lineup
            if r.get("p_active") is not None and 0.0 < float(r["p_active"]) < 0.95
        ]
        if opponent_uncertain:
            flags.append(
                f"opponent has {len(opponent_uncertain)} planning starters with sub-95% modeled availability: "
                + ", ".join(
                    f"{r.get('name')}={100*float(r['p_active']):.0f}%" for r in opponent_uncertain
                )
            )
        contingency = dashboard.get("contingency_policy_value")
        if contingency is not None and abs(float(contingency)) >= 0.05:
            flags.append(f"realistic backup-policy value is large at {100*float(contingency):+.2f} pp; inspect availability assumptions")
        timing_inflation = dashboard.get("information_timing_inflation")
        if timing_inflation is not None and abs(float(timing_inflation)) >= 0.02:
            flags.append(f"total idealized-information advantage is {100*float(timing_inflation):+.2f} pp over the lock-aware policy")
        if not bool(dashboard.get("timing_complete")):
            flags.append("kickoff timing is incomplete; realistic policy fell back to pre-lock active/inactive knowledge with workload still latent")
        boundary = [r for r in lineup if float(r.get("k") or 1.0) >= 1.119 or float(r.get("k") or 1.0) <= 0.881]
        if boundary:
            flags.append("K near configured bound: " + ", ".join(f"{r.get('name')}={float(r.get('k')):.3f}" for r in boundary))
        opponent_boundary = [
            r for r in opponent_lineup
            if float(r.get("k") or 1.0) >= 1.119 or float(r.get("k") or 1.0) <= 0.881
        ]
        if opponent_boundary:
            flags.append(
                "opponent K near configured bound: "
                + ", ".join(f"{r.get('name')}={float(r.get('k')):.3f}" for r in opponent_boundary)
            )
        interaction_rows = [r for r in lineup + opponent_lineup if r.get("interaction_source") == "DATA_MC_INTERACTION_GRID_V028"]
        if not interaction_rows:
            flags.append("v0.28 interaction grid is missing/unavailable for current starters; base MC/K fallback is active")
        else:
            low_support = [r for r in interaction_rows if float(r.get("interaction_support") or 0.0) < 10.0]
            if low_support:
                flags.append("low interaction-grid support: " + ", ".join(f"{r.get('name')}[N~{float(r.get('interaction_support') or 0):.0f}]" for r in low_support[:8]))
            material = [r for r in interaction_rows if abs(float(r.get("interaction_delta_ppg") or 0.0)) >= 1.0]
            if material:
                flags.append("material v0.28 interaction corrections: " + ", ".join(f"{r.get('name')}={float(r.get('interaction_delta_ppg') or 0):+.2f}pt" for r in material[:8]))

        source_checks = [r for r in dashboard.get("source_health") or [] if r.get("status") != "OK"]
        if source_checks:
            flags.append("source checks: " + ", ".join(f"{r.get('source')}={r.get('status')}" for r in source_checks))
        weak_user = [
            r for r in lineup
            if r.get("availability_evidence_level") in {"STATUS_ONLY", "DEFAULT_PRIOR"}
            and 0.0 < float(r.get("p_active") or 0.0) < 1.0
        ]
        weak_opp = [
            r for r in opponent_lineup
            if r.get("availability_evidence_level") in {"STATUS_ONLY", "DEFAULT_PRIOR"}
            and 0.0 < float(r.get("p_active") or 0.0) < 1.0
        ]
        if weak_user:
            flags.append(
                "weak/default availability evidence for starters: "
                + ", ".join(f"{r.get('name')}[{r.get('availability_evidence_level')}]" for r in weak_user)
            )
        if weak_opp:
            flags.append(
                "opponent weak/default availability evidence for starters: "
                + ", ".join(f"{r.get('name')}[{r.get('availability_evidence_level')}]" for r in weak_opp)
            )
        nfl_status = (self.snapshot.get("source_status") or {}).get("nfl_official") or {}
        injury_rows = nfl_status.get("injury_rows")
        if injury_rows == 0:
            flags.append("NFL.com injury-page rows=0; official practice evidence is unavailable from that feed, so status/Sleeper fallback may be used")
        prospective = closure.get("prospective") or {}
        availability_closure = prospective.get("availability") or {}
        if int(availability_closure.get("n") or 0) == 0:
            flags.append("v0.27 practice likelihood ratios remain uncalibrated priors; no explicit active/inactive truth has entered v0.29 closure yet")
        fantasy_closure = prospective.get("fantasy") or {}
        if int(fantasy_closure.get("n") or 0) == 0:
            flags.append("no completed prospective v0.29 fantasy-yield closure observations yet")

        return {
            "version": "v0.36",
            "snapshot_utc": dashboard.get("snapshot_utc"),
            "season": dashboard.get("season"),
            "week": dashboard.get("week"),
            "team_name": dashboard.get("team_name"),
            "opponent_name": dashboard.get("opponent_name"),
            "waiver_rank": dashboard.get("waiver_rank"),
            "mc_scenarios": self.ctx.predictive_scenarios,
            "matchup": matchup,
            "lineup": lineup,
            "opponent_lineup": opponent_lineup,
            "pipeline_symmetry": {
                "shared": True,
                "yield_builder": "build_weekly_yield_state",
                "availability_builder": "availability_state_model:v0.27-evidence",
                "interaction_builder": "Data/MC grid interpolation:v0.28",
                "timing_builder": "player_lock_timing",
                "lineup_optimizer": "optimize_lineup",
            },
            "key_uncertainty": key_uncertainty,
            "opponent_key_uncertainty": opponent_key_uncertainty,
            "anchor_flags": anchor_flags,
            "opponent_anchor_flags": opponent_anchor_flags,
            "hypothetical": hypothetical,
            "action": action,
            "trade": trade,
            "closure": closure,
            "model_flags": flags,
            "source_health": dashboard.get("source_health") or [],
        }

    def generate_chat_report(self, **kwargs: Any) -> dict[str, Any]:
        payload = self.chat_report_payload(**kwargs)
        return {"payload": payload, "text": format_chat_report(payload)}

    def write_chat_report(
        self,
        *,
        out_dir: str | Path = "data/chat_reports",
        **kwargs: Any,
    ) -> dict[str, Any]:
        report = self.generate_chat_report(**kwargs)
        root = Path(out_dir)
        root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = root / f"chat_report_{stamp}"
        suffix = 1
        while stem.with_suffix(".txt").exists() or stem.with_suffix(".json").exists():
            suffix += 1
            stem = root / f"chat_report_{stamp}_{suffix}"
        txt_path = stem.with_suffix(".txt")
        json_path = stem.with_suffix(".json")
        txt_path.write_text(report["text"], encoding="utf-8")
        json_path.write_text(json.dumps(report["payload"], indent=2, sort_keys=True), encoding="utf-8")
        return {
            **report,
            "text_path": str(txt_path),
            "json_path": str(json_path),
        }

    def capture_pregame_closure(self, out_dir: str | Path = "data/season_predictions/closure") -> dict[str, Any]:
        """Persist the exact in-memory GUI/service pregame state for later prospective closure."""
        assert self.ctx is not None
        capture = build_pregame_capture_from_context(self.snapshot, self.model, self.ctx, self.team)
        path = save_pregame_capture(capture, out_dir)
        from ..prospective_measurement_v034 import capture_summary
        measurement = capture_summary(capture)
        return {
            "path": str(path),
            "season": capture.get("season"),
            "week": capture.get("week"),
            "players": len(capture.get("players") or []),
            "components": sum(len(row.get("component_predictions") or {}) for row in capture.get("players") or []),
            "league_players": measurement.get("league_players"),
            "specialists": measurement.get("specialists"),
            "dst": measurement.get("dst"),
            "kickers": measurement.get("kickers"),
            "behavior_teams": measurement.get("behavior_teams"),
            "market_players": measurement.get("market_players"),
            "measurement_contract": measurement.get("measurement_contract"),
            "integrity_ok": measurement.get("integrity_ok"),
        }

    def prospective_closure_summary(self) -> dict[str, Any]:
        """Load the accumulated postgame v0.29 closure summary, if present."""
        return load_closure_summary("data/season_closure/summary.json")

    def prospective_closure_rows(self) -> list[dict[str, Any]]:
        frame = load_closure_ledger("data/season_closure/ledger.csv")
        if frame.empty:
            return []
        rows: list[dict[str, Any]] = []
        for record in frame.where(frame.notna(), None).to_dict("records"):
            rows.append(record)
        return rows

    def component_closure_summary_rows(self) -> list[dict[str, Any]]:
        summary = self.prospective_closure_summary()
        rows: list[dict[str, Any]] = []
        for key, metric in sorted((summary.get("components") or {}).items()):
            if ":" in key:
                position, component = key.split(":", 1)
            else:
                position, component = "?", key
            if int(metric.get("n") or 0) <= 0:
                continue
            rows.append({
                "position": position,
                "component": component,
                "n": int(metric.get("n") or 0),
                "bias": metric.get("bias"),
                "mae": metric.get("mae"),
                "rmse": metric.get("rmse"),
                "base_rmse": metric.get("base_rmse"),
                "interaction_rmse_improvement": metric.get("interaction_rmse_improvement"),
                "mean_data_over_mc": metric.get("mean_data_over_mc"),
            })
        return rows

    def prediction_ledger_summary(self) -> dict[str, Any]:
        rows = self.prediction_ledger()
        anchor_rows = [r for r in rows if r.get("model") is not None and r.get("espn") is not None]
        observed_rows = [r for r in rows if r.get("observed") is not None and r.get("operational") is not None]
        model_espn_abs = [abs(float(r["model_minus_espn"])) for r in anchor_rows if r.get("model_minus_espn") is not None]
        out: dict[str, Any] = {
            "players": len(rows),
            "anchor_coverage": len(anchor_rows),
            "observed_coverage": len(observed_rows),
            "mean_abs_model_minus_espn": float(np.mean(model_espn_abs)) if model_espn_abs else None,
            "max_abs_model_minus_espn": max(model_espn_abs) if model_espn_abs else None,
        }
        if observed_rows:
            data = np.asarray([float(r["observed"]) for r in observed_rows], dtype=float)
            mc = np.asarray([float(r["operational"]) for r in observed_rows], dtype=float)
            out["data_mc_bias"] = float(np.mean(data - mc))
            out["data_mc_rmse"] = float(np.sqrt(np.mean((data - mc) ** 2)))
            ratios = [float(r["data_over_mc"]) for r in observed_rows if r.get("data_over_mc") is not None]
            out["mean_data_over_mc"] = float(np.mean(ratios)) if ratios else None
            base_rows = [r for r in observed_rows if r.get("base_mc") is not None]
            if base_rows:
                base_data = np.asarray([float(r["observed"]) for r in base_rows], dtype=float)
                base_mc = np.asarray([float(r["base_mc"]) for r in base_rows], dtype=float)
                out["base_mc_bias"] = float(np.mean(base_data - base_mc))
                out["base_mc_rmse"] = float(np.sqrt(np.mean((base_data - base_mc) ** 2)))
                out["interaction_rmse_improvement"] = float(out["base_mc_rmse"] - out["data_mc_rmse"])
        else:
            out["data_mc_bias"] = None
            out["data_mc_rmse"] = None
            out["mean_data_over_mc"] = None
            out["base_mc_bias"] = None
            out["base_mc_rmse"] = None
            out["interaction_rmse_improvement"] = None
        return out

    def prediction_ledger(self) -> list[dict[str, Any]]:
        rows = self.roster_players()
        out: list[dict[str, Any]] = []
        assert self.ctx is not None
        by_id = {_int(p.get("espn_id")): p for p in self.ctx.roster}
        for row in rows:
            pid = int(row["espn_id"])
            raw = by_id.get(pid) or {}
            observed = None
            for key in ("actual_points", "scoring_period_points", "fantasy_points"):
                observed = _finite(raw.get(key))
                if observed is not None:
                    break
            model = _finite(row.get("model_mean"))
            espn = _finite(row.get("espn_anchor"))
            op = _finite(row.get("operational_mean"))
            interaction_delta = _finite(row.get("interaction_delta_ppg")) or 0.0
            base_mc = (op - interaction_delta) if op is not None else None
            out.append({
                "espn_id": pid,
                "name": row.get("name"),
                "position": row.get("position"),
                "observed": observed,
                "operational": op,
                "base_mc": base_mc,
                "interaction_delta_ppg": interaction_delta,
                "interaction_factor": row.get("interaction_factor"),
                "interaction_source": row.get("interaction_source"),
                "interaction_support": row.get("interaction_support"),
                "model": model,
                "espn": espn,
                "data_over_mc": (observed / op) if observed is not None and op not in (None, 0) else None,
                "data_over_base_mc": (observed / base_mc) if observed is not None and base_mc not in (None, 0) else None,
                "model_minus_espn": (model - espn) if model is not None and espn is not None else None,
                "k": row.get("k"),
                "p_active": row.get("p_active"),
            })
        return out
