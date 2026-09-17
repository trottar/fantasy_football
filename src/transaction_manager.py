from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from .season_utility import week_weights
from .weekly_yield import build_weekly_yield_state, sample_conditional_points
from .matchup_model import simulate_dst_component_points
from .availability_timing import availability_state_model, player_lock_timing, sample_availability_state
from .weekly_manager import (
    HARD_UNAVAILABLE_STATUSES,
    active_probability,
    availability_status,
    enrich_roster_projections,
    find_week_opponent,
    optimize_lineup,
    resolve_team,
)

FLEX_POSITIONS = {"RB", "WR", "TE"}
POSITIONS = ("QB", "RB", "WR", "TE", "K", "DST")
PLAYER_POSITIONS = ("QB", "RB", "WR", "TE")
SPECIALIST_POSITIONS = ("K", "DST")
NFL_FREE_AGENT_TEAM = "FA"
NFL_OFFICIAL_NORMAL_ACTION_STATUSES = {"ACT"}
NFL_OFFICIAL_STASH_ONLY_STATUSES = {"PUP", "RES", "IR", "RSR", "INA", "SUS", "EXE", "RLS", "NFI"}
NFL_OFFICIAL_NOT_ROSTERED_STATUSES = {"CUT", "RET", "UFA"}
NFLVERSE_NORMAL_ACTION_STATUSES = {"ACT"}
NFLVERSE_STASH_ONLY_STATUSES = {"INA", "PUP", "RES", "RSN", "SUS", "EXE", "E14", "DEV"}
NFLVERSE_NOT_ROSTERED_STATUSES = {"CUT", "RET", "UFA", "NWT", "RFA", "RSR", "TRC", "TRD", "TRT"}


McProgressCallback = Callable[[int, int, str], None]


def _mc_batches(total: int, batch_size: int):
    """Yield deterministic scenario-index batches without changing RNG streams."""
    n = max(0, int(total))
    step = max(1, int(batch_size))
    for start in range(0, n, step):
        yield start, min(start + step, n)


def _emit_mc_progress(callback: McProgressCallback | None, done: int, total: int, phase: str) -> None:
    if callback is not None:
        callback(int(done), max(1, int(total)), str(phase))


@dataclass(frozen=True)
class RosterUtilityResult:
    utility: float
    expected_h2h_win_probability: float
    current_week_expected_points: float
    current_week_nominal_points: float
    season_expected_lineup_ppg: float
    bench_insurance_ppg: float
    bye_floor_points: float
    weighted_bye_loss_points: float
    mc_scenarios: int = 0
    current_week_sd_points: float = 0.0
    season_lineup_sd_ppg: float = 0.0


@dataclass(frozen=True)
class ActionResult:
    add_espn_id: int
    add_name: str
    add_position: str
    add_team: str | None
    fantasy_status: str
    drop_espn_id: int
    drop_name: str
    drop_position: str
    delta_utility: float
    delta_expected_h2h_win_probability: float
    delta_current_week_points: float
    delta_season_lineup_ppg: float
    delta_bench_insurance_ppg: float
    delta_bye_floor_points: float
    p_acquire: float
    expected_delta_utility: float
    percent_owned: float | None
    sleeper_adds_24h: int | None
    candidate_projection_points: float
    candidate_projection_source: str
    candidate_season_ppg: float
    candidate_season_ppg_source: str
    delta_h2h_sd: float = 0.0
    delta_h2h_p16: float = 0.0
    delta_h2h_p84: float = 0.0
    p_utility_better_if_acquired: float = 0.5
    p_utility_worse_if_acquired: float = 0.5
    p_utility_tie_if_acquired: float = 0.0
    action_classification: str = "UNASSESSED"
    raw_action_classification: str = "UNASSESSED"
    combined_action_classification: str = "UNASSESSED"
    p_raw_h2h_better_if_acquired: float = 0.5
    p_raw_h2h_worse_if_acquired: float = 0.5
    p_raw_h2h_tie_if_acquired: float = 0.0
    delta_total_utility_p16: float = 0.0
    delta_total_utility_p84: float = 0.0
    candidate_option_support: float = 1.0
    mc_scenarios: int = 0
    screen_delta_utility: float = 0.0
    candidate_operational_mean_ppg: float | None = None
    candidate_model_mean_ppg: float | None = None
    candidate_espn_anchor_ppg: float | None = None
    candidate_espn_anchor_kind: str | None = None
    candidate_delta_model_minus_espn: float | None = None
    candidate_espn_anchor_z: float | None = None
    candidate_pre_matchup_mean_ppg: float | None = None
    candidate_matchup_model_mean_ppg: float | None = None
    candidate_kinematic_factor: float = 1.0
    candidate_kinematic_source: str = "UNKNOWN"
    candidate_matchup_opponent: str | None = None
    candidate_matchup_home: bool | None = None
    candidate_kinematic_sd_ppg: float = 0.0
    waiver_blockers: list[dict[str, Any]] | None = None
    waiver_response_model: str | None = None
    delta_h2h_only: float = 0.0
    delta_future_option_ppg: float = 0.0
    delta_replacement_scarcity_ppg: float = 0.0
    delta_future_option_utility: float = 0.0
    delta_replacement_scarcity_utility: float = 0.0
    delta_league_state_utility: float = 0.0
    release_p_claimed: float = 0.0
    release_expected_recipient_gain_ppg: float = 0.0
    release_field_shift_ppg: float = 0.0
    release_first_order_field_shift_ppg: float = 0.0
    release_higher_order_field_shift_ppg: float = 0.0
    release_current_opponent_shift_ppg: float = 0.0
    release_response_scenarios: int = 0
    release_higher_order_scenarios: int = 0
    release_response_model: str | None = None
    release_first_order_model: str | None = None
    release_cascade_orders: list[dict[str, Any]] | None = None
    release_cascade_stop_reasons: list[str] | None = None
    release_top_destinations: list[dict[str, Any]] | None = None
    mc_stage: str = "FINAL"
    mc_futility_stop: bool = False
    mc_stage_history: list[dict[str, Any]] | None = None


class UtilityContext:
    def __init__(
        self,
        snapshot: dict[str, Any],
        league: dict[str, Any],
        model: dict[str, Any],
        values_path: str | Path,
        team: dict[str, Any],
    ) -> None:
        self.snapshot = snapshot
        self.espn = snapshot.get("espn", snapshot)
        self.league = league
        self.model = model
        self.values_path = Path(values_path)
        self.week = int(self.espn.get("week") or 1)
        self.team = team
        self.team_id = int(team.get("team_id"))
        self.cfg = model.get("transaction_manager", {})
        self.scenarios = max(1, int(self.cfg.get("availability_scenarios", 16)))
        self.predictive_scenarios = max(8, int(self.cfg.get("predictive_mc_scenarios", 128)))
        self.seed = int(self.cfg.get("random_seed", 20260831))
        self.matchup_scale = float(self.cfg.get("h2h_matchup_scale_points", 18.0))
        self._model_values = _load_model_value_index(self.values_path)

        self.roster = enrich_season_values(
            team.get("roster") or [], self.values_path, league, self.week, self._model_values
        )
        self.available = enrich_season_values(
            self.espn.get("available_players") or [], self.values_path, league, self.week, self._model_values
        )
        self.actionable_available: list[dict[str, Any]] = []
        self.excluded_available: list[dict[str, Any]] = []
        for player in self.available:
            eligible, reason = nfl_candidate_eligibility(player)
            row = dict(player)
            row["nfl_candidate_eligibility"] = reason
            if eligible:
                self.actionable_available.append(row)
            else:
                self.excluded_available.append(row)
        self.all_team_rosters: dict[int, list[dict[str, Any]]] = {}
        for other in self.espn.get("teams") or []:
            try:
                oid = int(other.get("team_id"))
            except (TypeError, ValueError):
                continue
            self.all_team_rosters[oid] = enrich_season_values(
                other.get("roster") or [], self.values_path, league, self.week, self._model_values
            )

        # Replacement players must themselves be on an NFL roster. Unsigned NFL free
        # agents can remain in ESPN's fantasy player universe and may retain stale/model
        # talent priors, but they cannot provide current replacement production.
        self.replacement_current, self.replacement_season = replacement_levels(
            self.actionable_available, self.cfg
        )
        self._uniforms: dict[int, np.ndarray] = {}
        self._predictive_uniforms: dict[int, np.ndarray] = {}
        self._workload_uniforms: dict[int, np.ndarray] = {}
        self._epistemic_normals: dict[int, np.ndarray] = {}
        self._game_normals: dict[int, np.ndarray] = {}
        self._kinematic_normals: dict[int, np.ndarray] = {}
        self._interaction_normals: dict[int, np.ndarray] = {}
        self._yield_state_cache: dict[tuple[int, int], Any] = {}
        self._availability_state_cache: dict[tuple[int, int], Any] = {}
        self._lock_timing_cache: dict[tuple[int, int], Any] = {}
        self._waiver_interest_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self._waiver_roster_score_cache: dict[tuple[int, ...], tuple[float, float]] = {}
        # Small-N future-roster-state streams used only by the market option layer.
        # They are player-keyed so HOLD and every add/drop alternative use identical
        # latent role / availability states (common random numbers).
        self._contingent_role_normals: dict[tuple[int, int], np.ndarray] = {}
        self._contingent_active_uniforms: dict[tuple[int, int], np.ndarray] = {}
        self._contingent_limited_uniforms: dict[tuple[int, int], np.ndarray] = {}
        # First-order counterfactual league-state response caches.  These use the
        # same commissioned predictive player generator as the main action MC, but
        # at a deliberately small N and without constructing another H2H opponent
        # reference.  The released-player response is keyed by (N, player id).
        self._league_response_baseline_cache: dict[tuple[int, int], np.ndarray] = {}
        self._league_release_response_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self.matchup_context = snapshot.get("matchup_context") or {}
        self.opponent_reference = self._build_opponent_reference()
        # Predictive opponent MC is intentionally lazy. At large N this is a substantial
        # whole-league simulation and must be part of visible MC progress, not hidden
        # inside UtilityContext construction / GUI MC-size changes.
        self._opponent_predictive: np.ndarray | None = None

    def set_predictive_scenarios(self, value: int) -> int:
        """Resize predictive MC streams without rebuilding static league/player state.

        The random streams are deterministic functions of ``predictive_scenarios`` and
        player id, so changing N only requires clearing arrays whose shape depends on N.
        Yield/availability/lock-timing states are independent of N and are retained.
        """
        n = max(8, int(value))
        self.predictive_scenarios = n
        self.cfg["predictive_mc_scenarios"] = n
        self._predictive_uniforms.clear()
        self._workload_uniforms.clear()
        self._epistemic_normals.clear()
        self._game_normals.clear()
        self._kinematic_normals.clear()
        self._interaction_normals.clear()
        self._opponent_predictive = None
        return n

    def predictive_opponent_work(self) -> int:
        """Return scenario-week work needed to build the lazy opponent reference."""
        if self._opponent_predictive is not None:
            return 0
        other_teams = sum(1 for team_id in self.all_team_rosters if team_id != self.team_id)
        weeks_count = max(0, 18 - max(1, self.week))
        return int(other_teams * weeks_count * self.predictive_scenarios)

    @property
    def opponent_predictive(self) -> np.ndarray:
        return self.ensure_predictive_opponent_reference()

    def ensure_predictive_opponent_reference(
        self,
        progress_callback: McProgressCallback | None = None,
        *,
        progress_offset: int = 0,
        progress_total: int | None = None,
        progress_label: str = "opponent reference",
    ) -> np.ndarray:
        if self._opponent_predictive is not None:
            return self._opponent_predictive
        self._opponent_predictive = self._build_predictive_opponent_reference(
            progress_callback=progress_callback,
            progress_offset=progress_offset,
            progress_total=progress_total,
            progress_label=progress_label,
        )
        return self._opponent_predictive

    def uniforms(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._uniforms.get(player_id)
        if cached is not None:
            return cached
        # Player-keyed streams make common random numbers stable across add/drop alternatives.
        seed_seq = np.random.SeedSequence([self.seed, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.random((self.scenarios, 17))
        self._uniforms[player_id] = arr
        return arr

    def predictive_uniforms(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._predictive_uniforms.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0xA11A, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.random((self.predictive_scenarios, 17))
        self._predictive_uniforms[player_id] = arr
        return arr

    def release_predictive_streams(self, player_ids) -> None:
        """Release N-dependent RNG arrays for players no longer needed in memory.

        Streams are deterministic functions of seed, player id, and N, so regenerating
        a released stream later produces the identical universe values.  This is used
        after each opponent roster is folded into the league reference to prevent
        large-N runs from retaining several N x 17 arrays for every league player.
        """
        ids = {int(pid) for pid in player_ids if pid is not None}
        for cache in (
            self._predictive_uniforms,
            self._workload_uniforms,
            self._epistemic_normals,
            self._game_normals,
            self._kinematic_normals,
            self._interaction_normals,
        ):
            for pid in ids:
                cache.pop(pid, None)

    def workload_uniforms(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._workload_uniforms.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0xF011, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.random((self.predictive_scenarios, 17))
        self._workload_uniforms[player_id] = arr
        return arr

    def epistemic_normals(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._epistemic_normals.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0xE915, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        # One latent-mean draw per universe, shared across weeks for this player.
        arr = rng.standard_normal(self.predictive_scenarios)
        self._epistemic_normals[player_id] = arr
        return arr

    def game_normals(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._game_normals.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0x6A4E, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.standard_normal((self.predictive_scenarios, 17))
        self._game_normals[player_id] = arr
        return arr

    def kinematic_normals(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._kinematic_normals.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0xB17A, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.standard_normal((self.predictive_scenarios, 17))
        self._kinematic_normals[player_id] = arr
        return arr

    def interaction_normals(self, player_id: int) -> np.ndarray:
        player_id = int(player_id)
        cached = self._interaction_normals.get(player_id)
        if cached is not None:
            return cached
        seed_seq = np.random.SeedSequence([self.seed, 0x1A7E, player_id & 0xFFFFFFFF])
        rng = np.random.default_rng(seed_seq)
        arr = rng.standard_normal((self.predictive_scenarios, 17))
        self._interaction_normals[player_id] = arr
        return arr

    def yield_state(self, player: dict[str, Any], week: int):
        pid = _finite_int(player.get("espn_id"))
        key = (pid if pid is not None else id(player), int(week))
        cached = self._yield_state_cache.get(key)
        if cached is not None:
            return cached
        week = int(week)
        availability_probability = (
            self.availability_state(player, week).p_active
            if week == self.week
            else _player_probability(player, self, week)
        )
        state = build_weekly_yield_state(
            player,
            week=week,
            current_week=self.week,
            model=self.model,
            availability_probability=availability_probability,
            matchup_context=self.matchup_context,
            league=self.league,
        )
        self._yield_state_cache[key] = state
        return state

    def availability_state(self, player: dict[str, Any], week: int):
        pid = _finite_int(player.get("espn_id"))
        key = (pid if pid is not None else id(player), int(week))
        cached = self._availability_state_cache.get(key)
        if cached is not None:
            return cached
        week = int(week)
        if week == self.week:
            timing = self.lock_timing(player, week)
            snapshot_text = self.snapshot.get("snapshot_utc") or self.espn.get("snapshot_utc")
            hours_to_kickoff = None
            if timing.kickoff is not None and snapshot_text:
                try:
                    snapshot_dt = datetime.fromisoformat(str(snapshot_text).replace("Z", "+00:00"))
                    if snapshot_dt.tzinfo is None:
                        snapshot_dt = snapshot_dt.replace(tzinfo=timezone.utc)
                    hours_to_kickoff = (timing.kickoff.astimezone(timezone.utc) - snapshot_dt.astimezone(timezone.utc)).total_seconds() / 3600.0
                except (TypeError, ValueError):
                    hours_to_kickoff = None
            state = availability_state_model(
                player,
                self.model,
                hours_to_kickoff=hours_to_kickoff,
            )
        else:
            state = availability_state_model(
                player,
                self.model,
                p_active_override=_player_probability(player, self, week),
            )
        self._availability_state_cache[key] = state
        return state

    def lock_timing(self, player: dict[str, Any], week: int):
        pid = _finite_int(player.get("espn_id"))
        key = (pid if pid is not None else id(player), int(week))
        cached = self._lock_timing_cache.get(key)
        if cached is not None:
            return cached
        timing = player_lock_timing(
            player, week=int(week), matchup_context=self.matchup_context, model=self.model
        )
        self._lock_timing_cache[key] = timing
        return timing

    def _build_opponent_reference(self) -> np.ndarray:
        refs: list[np.ndarray] = []
        for team_id, roster in self.all_team_rosters.items():
            if team_id == self.team_id:
                continue
            refs.append(self._simulate_weekly_points(roster))
        if refs:
            generic = np.mean(np.stack(refs, axis=0), axis=(0, 1))
        else:
            generic = np.full(17, 110.0, dtype=float)

        opponent_id = find_week_opponent(self.snapshot, self.team_id)
        if opponent_id is not None and int(opponent_id) in self.all_team_rosters:
            opp = self._simulate_weekly_points(self.all_team_rosters[int(opponent_id)])
            generic[self.week - 1] = float(np.mean(opp[:, self.week - 1]))
        return generic

    def _build_predictive_opponent_reference(
        self,
        *,
        progress_callback: McProgressCallback | None = None,
        progress_offset: int = 0,
        progress_total: int | None = None,
        progress_label: str = "opponent reference",
    ) -> np.ndarray:
        """Build the league/opponent predictive reference with visible progress.

        v0.26-fixed6 removes the former duplicate simulation of the actual weekly
        opponent. We accumulate the league reference in-place and retain that team's
        already-computed array for the current-week override.
        """
        other = [(team_id, roster) for team_id, roster in self.all_team_rosters.items() if team_id != self.team_id]
        if not other:
            out = np.full((self.predictive_scenarios, 17), 110.0, dtype=float)
            _emit_mc_progress(progress_callback, progress_offset, progress_total or max(1, progress_offset), f"{progress_label}: generic fallback")
            return out

        weeks_count = max(0, 18 - max(1, self.week))
        per_team_work = max(1, weeks_count * self.predictive_scenarios)
        local_work = len(other) * per_team_work
        reported_total = int(progress_total) if progress_total is not None else int(progress_offset + local_work)
        running = np.zeros((self.predictive_scenarios, 17), dtype=float)
        opponent_id = find_week_opponent(self.snapshot, self.team_id)
        opponent_weekly: np.ndarray | None = None
        names = {
            int(t.get("team_id")): str(t.get("name") or f"team {t.get('team_id')}")
            for t in (self.espn.get("teams") or [])
            if _finite_int(t.get("team_id")) is not None
        }

        for index, (team_id, roster) in enumerate(other):
            label = f"{progress_label} {index + 1}/{len(other)} {names.get(int(team_id), f'team {team_id}')}"
            team_offset = progress_offset + index * per_team_work
            arr = _simulate_predictive_weekly_points(
                roster, self, self.replacement_current, self.replacement_season,
                progress_callback=progress_callback,
                progress_offset=team_offset,
                progress_total=reported_total,
                progress_label=label,
            )
            running += arr
            if opponent_id is not None and int(team_id) == int(opponent_id):
                # Only the current-week vector is needed for the actual-opponent
                # override.  Retaining the full N x 17 opponent array at N=65k is
                # unnecessary memory pressure.
                opponent_weekly = np.asarray(arr[:, self.week - 1], dtype=float).copy()

            # Opponent-player random streams are not needed after this team's weekly
            # output has been accumulated.  Keeping five large player-keyed caches
            # across all 11 opponent rosters made 65k runs page heavily on Windows.
            # Regeneration is bitwise deterministic if a later diagnostic needs one.
            self.release_predictive_streams(
                _finite_int(player.get("espn_id")) for player in roster
            )
            _emit_mc_progress(
                progress_callback, team_offset + per_team_work, reported_total,
                f"{label}: complete",
            )

        generic = running / float(len(other))
        if opponent_weekly is not None:
            generic[:, self.week - 1] = opponent_weekly
        _emit_mc_progress(progress_callback, progress_offset + local_work, reported_total, f"{progress_label}: complete")
        return generic

    def _simulate_weekly_points(self, roster: list[dict[str, Any]]) -> np.ndarray:
        return _simulate_weekly_points(
            roster,
            self,
            self.replacement_current,
            self.replacement_season,
        )


def _load_model_value_index(path: str | Path) -> dict[int, dict[str, float]]:
    path = Path(path)
    if not path.exists():
        return {}
    df = pd.read_csv(path, low_memory=False)
    if "espn_id" not in df.columns:
        return {}
    out: dict[int, dict[str, float]] = {}
    for row in df.to_dict("records"):
        try:
            pid = int(float(row.get("espn_id")))
        except (TypeError, ValueError):
            continue
        vals: dict[str, float] = {}
        for col in ("latent_mean_ppg", "latent_mean_sd_ppg", "predictive_weekly_sd_ppg"):
            try:
                value = float(row.get(col))
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                vals[col] = value
        out[pid] = vals
    return out


def enrich_season_values(
    players: list[dict[str, Any]],
    values_path: str | Path,
    league: dict[str, Any],
    week: int,
    value_index: dict[int, dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    value_index = value_index if value_index is not None else _load_model_value_index(values_path)
    out = enrich_roster_projections(players, values_path, league=league, week=week)
    for p in out:
        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            pid = -1
        vals = value_index.get(pid, {})
        latent = vals.get("latent_mean_ppg")
        season = _finite_float(p.get("season_projection"))
        weekly = _finite_float(p.get("projection_points")) or 0.0
        if latent is not None and latent > 0:
            season_ppg = latent
            season_source = "MODEL_LATENT_PPG"
        elif season is not None and season > 0:
            season_ppg = season / 17.0
            season_source = "ESPN_SEASON_DIV17"
        else:
            season_ppg = weekly
            season_source = "WEEKLY_FALLBACK"
        p["season_ppg"] = float(max(season_ppg, 0.0))
        p["season_ppg_source"] = season_source
        p["latent_mean_ppg"] = float(latent) if latent is not None else None
        p["latent_mean_sd_ppg"] = float(vals.get("latent_mean_sd_ppg", 0.0))
        p["predictive_weekly_sd_ppg"] = float(vals.get("predictive_weekly_sd_ppg", 0.0))
    return out


def _finite_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _finite_int(value: Any) -> int | None:
    try:
        out = int(float(value))
    except (TypeError, ValueError):
        return None
    return out


def _official_unknown_status_counts(players: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    prefix = "NFL_OFFICIAL_STATUS_UNKNOWN_"
    for player in players:
        reason = str(player.get("nfl_candidate_eligibility") or "")
        if not reason.startswith(prefix):
            continue
        status = reason[len(prefix):] or "EMPTY"
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def nfl_candidate_eligibility(player: dict[str, Any]) -> tuple[bool, str]:
    """Whether an ESPN available player belongs in ordinary FA/waiver valuation.

    Current NFL roster membership is checked in this order:
      1. NFL.com current team roster status (authoritative when matched);
      2. nflverse daily roster status joined by ESPN ID;
      3. Sleeper current team/status as a structured fallback;
      4. ESPN proTeamId/team as a final fallback.

    Only a normal active-roster state is allowed into ordinary add/drop valuation.
    PUP/reserve/suspended/practice-squad/etc. players are *stash-only* until the
    dedicated stash/return-probability model exists. This prevents stale preseason
    latent PPG from being interpreted as normal weekly production.
    """
    position = str(player.get("position") or "").strip().upper()
    team = str(player.get("nfl_team") or "").strip().upper()
    pro_team_id = _finite_int(player.get("pro_team_id"))

    # ESPN D/ST pseudo-players do not have individual NFL roster rows.
    if position == "DST":
        if pro_team_id == 0 or team == NFL_FREE_AGENT_TEAM or not team:
            return False, "NFL_TEAM_UNKNOWN"
        return True, "NFL_TEAM_ENTITY"

    official_status = str(player.get("official_roster_status") or "").strip().upper()
    official_team = str(player.get("official_roster_team") or "").strip().upper()
    if official_status:
        if official_status in NFL_OFFICIAL_NORMAL_ACTION_STATUSES:
            if not official_team:
                return False, "NFL_OFFICIAL_TEAM_UNKNOWN"
            return True, f"NFL_OFFICIAL_{official_status}"
        if official_status in NFL_OFFICIAL_STASH_ONLY_STATUSES:
            return False, f"NFL_OFFICIAL_STASH_ONLY_{official_status}"
        if official_status in NFL_OFFICIAL_NOT_ROSTERED_STATUSES:
            return False, f"NFL_OFFICIAL_NOT_ROSTERED_{official_status}"
        return False, f"NFL_OFFICIAL_STATUS_UNKNOWN_{official_status}"

    nflverse_status = str(player.get("nflverse_roster_status") or "").strip().upper()
    nflverse_team = str(player.get("nflverse_roster_team") or "").strip().upper()
    if nflverse_status:
        if nflverse_status in NFLVERSE_NORMAL_ACTION_STATUSES:
            if not nflverse_team:
                return False, "NFLVERSE_TEAM_UNKNOWN"
            return True, f"NFLVERSE_{nflverse_status}"
        if nflverse_status in NFLVERSE_STASH_ONLY_STATUSES:
            return False, f"NFLVERSE_STASH_ONLY_{nflverse_status}"
        if nflverse_status in NFLVERSE_NOT_ROSTERED_STATUSES:
            return False, f"NFLVERSE_NOT_ROSTERED_{nflverse_status}"
        # Unknown roster codes fail safe; the raw status remains in the snapshot/audit.
        return False, f"NFLVERSE_STATUS_UNKNOWN_{nflverse_status}"

    sleeper_status = str(player.get("sleeper_status") or "").strip().upper()
    sleeper_team = str(player.get("sleeper_team") or "").strip().upper()
    if sleeper_status or player.get("sleeper_id"):
        if sleeper_status in {"RETIRED", "INACTIVE"}:
            return False, f"SLEEPER_{sleeper_status}"
        if sleeper_status == "ACTIVE" and sleeper_team:
            return True, "SLEEPER_ACTIVE_FALLBACK"
        if not sleeper_team:
            return False, "SLEEPER_TEAM_MISSING"

    # Final fallback for players missing from the current external roster sources.
    if pro_team_id == 0 or team == NFL_FREE_AGENT_TEAM:
        return False, "NFL_FREE_AGENT_UNSIGNED"
    if not team:
        return False, "NFL_TEAM_UNKNOWN"
    return True, "ESPN_TEAM_FALLBACK"


def replacement_levels(
    available: list[dict[str, Any]], cfg: dict[str, Any]
) -> tuple[dict[str, float], dict[str, float]]:
    rank_cfg = cfg.get("replacement_available_rank", {})
    current: dict[str, float] = {}
    season: dict[str, float] = {}
    for pos in POSITIONS:
        rows = [p for p in available if str(p.get("position")) == pos]
        cur_vals = sorted(
            [
                float(p.get("projection_points") or 0.0) * active_probability(p, {"weekly_manager": cfg.get("weekly_manager_override", {})})
                for p in rows
                if availability_status(p)[0] not in HARD_UNAVAILABLE_STATUSES
            ],
            reverse=True,
        )
        season_vals = sorted(
            [
                float(p.get("season_ppg") or 0.0)
                for p in rows
                if float(p.get("season_ppg") or 0.0) > 0
                and availability_status(p)[0] not in HARD_UNAVAILABLE_STATUSES
            ],
            reverse=True,
        )
        rank = max(1, int(rank_cfg.get(pos, 3 if pos in {"QB", "TE", "K", "DST"} else 6)))
        current[pos] = cur_vals[min(rank - 1, len(cur_vals) - 1)] if cur_vals else 0.0
        season[pos] = season_vals[min(rank - 1, len(season_vals) - 1)] if season_vals else current[pos]
    return current, season


def _player_probability(player: dict[str, Any], ctx: UtilityContext, week: int) -> float:
    if int(week) == int(ctx.week):
        return float(ctx.availability_state(player, int(week)).p_active)
    probs = ctx.model.get("season_utility", {}).get("active_probability_nonbye", {})
    pos = str(player.get("position") or "")
    return min(max(float(probs.get(pos, 0.95)), 0.0), 1.0)


def _player_points(player: dict[str, Any], ctx: UtilityContext, week: int) -> float:
    bye = ctx.league.get("bye_weeks_2026", {}).get(player.get("nfl_team"))
    try:
        if bye is not None and int(bye) == int(week):
            return 0.0
    except (TypeError, ValueError):
        pass
    # The fast availability-only screener now uses the same pregame operational
    # yield coordinate as the final predictive MC. It still omits score variance,
    # but it no longer screens out a candidate merely because the matchup layer was
    # absent from the v0.21/v0.22 point estimate.
    return float(ctx.yield_state(player, int(week)).operational_mean_ppg)


def _best_lineup_points(
    roster: list[dict[str, Any]],
    active: dict[int, bool],
    scores: dict[int, float],
    league: dict[str, Any],
    replacement: dict[str, float],
) -> tuple[float, set[int]]:
    roster_cfg = league.get("roster", {})
    selected: set[int] = set()
    total = 0.0
    by_pos: dict[str, list[tuple[float, int]]] = {p: [] for p in POSITIONS}
    for p in roster:
        pid = _finite_int(p.get("espn_id"))
        pos = str(p.get("position") or "")
        if pid is None or pos not in by_pos or not active.get(pid, False):
            continue
        by_pos[pos].append((float(scores.get(pid, 0.0)), pid))
    for pos in by_pos:
        by_pos[pos].sort(reverse=True)

    for pos in ("QB", "RB", "WR", "TE"):
        need = int(roster_cfg.get(pos, 0))
        chosen = by_pos[pos][:need]
        for value, pid in chosen:
            total += value
            selected.add(pid)
        if len(chosen) < need:
            total += (need - len(chosen)) * float(replacement.get(pos, 0.0))

    flex_need = int(roster_cfg.get("FLEX", 0))
    flex = []
    for pos in FLEX_POSITIONS:
        flex.extend((value, pid) for value, pid in by_pos[pos] if pid not in selected)
    flex.sort(reverse=True)
    chosen_flex = flex[:flex_need]
    for value, pid in chosen_flex:
        total += value
        selected.add(pid)
    if len(chosen_flex) < flex_need:
        flex_replacement = max(float(replacement.get(pos, 0.0)) for pos in FLEX_POSITIONS)
        total += (flex_need - len(chosen_flex)) * flex_replacement

    for pos in ("K", "DST"):
        need = int(roster_cfg.get(pos, 0))
        chosen = by_pos[pos][:need]
        for value, pid in chosen:
            total += value
            selected.add(pid)
        if len(chosen) < need:
            total += (need - len(chosen)) * float(replacement.get(pos, 0.0))
    return float(total), selected


def _best_lineup_realized_points(
    roster: list[dict[str, Any]],
    active: dict[int, bool],
    decision_scores: dict[int, float],
    realized_scores: dict[int, float],
    league: dict[str, Any],
    replacement: dict[str, float],
) -> tuple[float, set[int]]:
    """Select a legal lineup using only pregame information, then score outcomes.

    ``decision_scores`` are the means available when the lineup decision is made.
    ``realized_scores`` are the subsequently sampled fantasy yields.  Keeping these
    separate prevents perfect-hindsight optimization over realized game outcomes.
    Availability can still define a contingent branch because the current v0.23
    timing approximation assumes active/inactive status is known before the relevant
    lineup choice; late-swap timing is a later model layer.
    """
    roster_cfg = league.get("roster", {})
    selected: set[int] = set()
    total = 0.0
    by_pos: dict[str, list[tuple[float, int]]] = {p: [] for p in POSITIONS}
    for p in roster:
        pid = _finite_int(p.get("espn_id"))
        pos = str(p.get("position") or "")
        if pid is None or pos not in by_pos or not active.get(pid, False):
            continue
        by_pos[pos].append((float(decision_scores.get(pid, 0.0)), pid))
    for pos in by_pos:
        by_pos[pos].sort(reverse=True)

    for pos in ("QB", "RB", "WR", "TE"):
        need = int(roster_cfg.get(pos, 0))
        chosen = by_pos[pos][:need]
        for _decision_value, pid in chosen:
            total += float(realized_scores.get(pid, 0.0))
            selected.add(pid)
        if len(chosen) < need:
            total += (need - len(chosen)) * float(replacement.get(pos, 0.0))

    flex_need = int(roster_cfg.get("FLEX", 0))
    flex: list[tuple[float, int]] = []
    for pos in FLEX_POSITIONS:
        flex.extend((value, pid) for value, pid in by_pos[pos] if pid not in selected)
    flex.sort(reverse=True)
    chosen_flex = flex[:flex_need]
    for _decision_value, pid in chosen_flex:
        total += float(realized_scores.get(pid, 0.0))
        selected.add(pid)
    if len(chosen_flex) < flex_need:
        flex_replacement = max(float(replacement.get(pos, 0.0)) for pos in FLEX_POSITIONS)
        total += (flex_need - len(chosen_flex)) * flex_replacement

    for pos in ("K", "DST"):
        need = int(roster_cfg.get(pos, 0))
        chosen = by_pos[pos][:need]
        for _decision_value, pid in chosen:
            total += float(realized_scores.get(pid, 0.0))
            selected.add(pid)
        if len(chosen) < need:
            total += (need - len(chosen)) * float(replacement.get(pos, 0.0))
    return float(total), selected



def _lineup_slot_definitions(league: dict[str, Any]) -> list[tuple[str, set[str]]]:
    cfg = league.get("roster", {})
    slots: list[tuple[str, set[str]]] = []
    for pos in ("QB", "RB", "WR", "TE"):
        need = int(cfg.get(pos, 0))
        for i in range(need):
            label = pos if need == 1 else f"{pos}{i + 1}"
            slots.append((label, {pos}))
    for i in range(int(cfg.get("FLEX", 0))):
        label = "FLEX" if int(cfg.get("FLEX", 0)) == 1 else f"FLEX{i + 1}"
        slots.append((label, set(FLEX_POSITIONS)))
    for pos in ("K", "DST"):
        need = int(cfg.get(pos, 0))
        for i in range(need):
            label = pos if need == 1 else f"{pos}{i + 1}"
            slots.append((label, {pos}))
    return slots


def _optimal_lineup_assignment(
    roster: list[dict[str, Any]],
    eligible_ids: set[int],
    decision_scores: dict[int, float],
    league: dict[str, Any],
    *,
    fixed_slots: dict[str, int] | None = None,
    avoid_flex_ids: set[int] | None = None,
) -> dict[str, int]:
    """Maximum-score legal slot assignment with optional already-locked slots.

    The dynamic program is tiny (at most 2^9 ordinary lineup masks) and explicitly
    preserves slot identity.  That is important for late FLEX optionality: a locked
    RB in FLEX is not equivalent to a locked RB in RB1 once later WR/RB choices remain.
    """
    fixed_slots = dict(fixed_slots or {})
    avoid_flex_ids = set(avoid_flex_ids or set())
    slots = _lineup_slot_definitions(league)
    slot_index = {name: i for i, (name, _eligible) in enumerate(slots)}
    used_fixed = set(fixed_slots.values())
    open_slots = [(name, eligible) for name, eligible in slots if name not in fixed_slots]
    open_index = {name: i for i, (name, _eligible) in enumerate(open_slots)}

    # mask -> (score, flex_tiebreak, assignment of open slots).  The secondary
    # objective is used only for score ties: players locking now should occupy a
    # dedicated RB/WR/TE slot rather than FLEX when both assignments are legal.
    dp: dict[int, tuple[float, int, dict[str, int]]] = {0: (0.0, 0, {})}
    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None or pid not in eligible_ids or pid in used_fixed:
            continue
        pos = str(player.get("position") or "")
        value = float(decision_scores.get(pid, 0.0))
        previous = list(dp.items())
        for mask, (score, flex_tiebreak, assignment) in previous:
            for slot_name, slot_eligible in open_slots:
                bit = 1 << open_index[slot_name]
                if mask & bit or pos not in slot_eligible:
                    continue
                new_mask = mask | bit
                new_score = score + value
                new_flex_tiebreak = flex_tiebreak - int(pid in avoid_flex_ids and slot_name.startswith("FLEX"))
                old = dp.get(new_mask)
                if old is None or (new_score, new_flex_tiebreak) > (old[0], old[1]):
                    new_assignment = dict(assignment)
                    new_assignment[slot_name] = pid
                    dp[new_mask] = (new_score, new_flex_tiebreak, new_assignment)

    # Prefer filling the largest number of legal slots; for equal completeness,
    # maximize pregame decision value. Replacement is only a missing-slot fallback,
    # not a freely selectable player, matching the commissioned lineup engine.
    best_mask, (_best_score, _best_flex_tiebreak, best_open) = max(
        dp.items(), key=lambda item: (int(item[0]).bit_count(), item[1][0], item[1][1])
    )
    del best_mask, slot_index
    return {**fixed_slots, **best_open}


def _replacement_for_slot(slot: str, replacement: dict[str, float]) -> float:
    if slot.startswith("RB"):
        return float(replacement.get("RB", 0.0))
    if slot.startswith("WR"):
        return float(replacement.get("WR", 0.0))
    if slot.startswith("QB"):
        return float(replacement.get("QB", 0.0))
    if slot.startswith("TE"):
        return float(replacement.get("TE", 0.0))
    if slot.startswith("K"):
        return float(replacement.get("K", 0.0))
    if slot.startswith("DST"):
        return float(replacement.get("DST", 0.0))
    if slot.startswith("FLEX"):
        return max(float(replacement.get(pos, 0.0)) for pos in FLEX_POSITIONS)
    return 0.0


def _score_assignment(
    assignment: dict[str, int],
    realized_scores: dict[int, float],
    league: dict[str, Any],
    replacement: dict[str, float],
) -> float:
    total = 0.0
    for slot, _eligible in _lineup_slot_definitions(league):
        pid = assignment.get(slot)
        if pid is None:
            total += _replacement_for_slot(slot, replacement)
        else:
            total += float(realized_scores.get(pid, 0.0))
    return float(total)


def _current_week_state_samples(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    week: int,
) -> tuple[
    dict[int, np.ndarray],
    dict[int, np.ndarray],
    dict[int, Any],
    dict[int, float],
]:
    """Sample realized yields and explicit workload states for the current week."""
    player_scores: dict[int, np.ndarray] = {}
    state_codes: dict[int, np.ndarray] = {}
    state_models: dict[int, Any] = {}
    base_means: dict[int, float] = {}
    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        state = ctx.yield_state(player, week)
        availability = ctx.availability_state(player, week)
        state_models[pid] = availability
        base_means[pid] = float(state.operational_mean_ppg)
        bye = ctx.league.get("bye_weeks_2026", {}).get(player.get("nfl_team"))
        try:
            is_bye = bye is not None and int(bye) == int(week)
        except (TypeError, ValueError):
            is_bye = False
        if is_bye or availability.p_active <= 0.0:
            player_scores[pid] = np.zeros(ctx.predictive_scenarios, dtype=float)
            state_codes[pid] = np.zeros(ctx.predictive_scenarios, dtype=np.int8)  # 0=OUT
            continue
        if state.position == "DST" and state.dst_component_expectation:
            full_scores = simulate_dst_component_points(
                state.dst_component_expectation,
                scenarios=ctx.predictive_scenarios,
                seed=ctx.seed + 1000003 * int(pid) + 97 * int(week),
                target_mean=state.operational_mean_ppg,
            )
            full_scores = (
                full_scores
                + state.model_sd_ppg * ctx.epistemic_normals(pid)
                + state.kinematic_sd_ppg * ctx.kinematic_normals(pid)[:, week - 1]
            )
        else:
            full_scores = sample_conditional_points(
                state,
                ctx.epistemic_normals(pid),
                ctx.game_normals(pid)[:, week - 1],
                ctx.kinematic_normals(pid)[:, week - 1],
                ctx.interaction_normals(pid)[:, week - 1],
            )
        active = ctx.predictive_uniforms(pid)[:, week - 1] < availability.p_active
        full = ctx.workload_uniforms(pid)[:, week - 1] < availability.p_full_given_active
        codes = np.where(~active, 0, np.where(full, 2, 1)).astype(np.int8)  # 1=LIMITED, 2=FULL
        scale = np.where(codes == 2, 1.0, np.where(codes == 1, availability.limited_workload_fraction, 0.0))
        player_scores[pid] = np.asarray(full_scores, dtype=float) * scale
        state_codes[pid] = codes
    return player_scores, state_codes, state_models, base_means


def _simulate_current_week_idealized_policy(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    replacement: dict[str, float],
    week: int,
    player_scores: dict[int, np.ndarray],
    state_codes: dict[int, np.ndarray],
    state_models: dict[int, Any],
    base_means: dict[int, float],
    *,
    reveal_workload: bool = True,
    progress_callback: McProgressCallback | None = None,
    progress_phase: str = "current-week idealized",
) -> np.ndarray:
    """Idealized pre-lock policy with optional FULL/LIMITED state revelation."""
    out = np.zeros(ctx.predictive_scenarios, dtype=float)
    pids = [pid for pid in (_finite_int(p.get("espn_id")) for p in roster) if pid is not None]
    batch_size = int(ctx.cfg.get("mc_progress_batch_size", 512))
    for start, stop in _mc_batches(ctx.predictive_scenarios, batch_size):
        for scenario in range(start, stop):
            active: dict[int, bool] = {}
            decision: dict[int, float] = {}
            realized: dict[int, float] = {}
            for pid in pids:
                code = int(state_codes[pid][scenario])
                active[pid] = code != 0
                if code == 0:
                    decision[pid] = 0.0
                    realized[pid] = 0.0
                    continue
                if reveal_workload:
                    frac = 1.0 if code == 2 else float(state_models[pid].limited_workload_fraction)
                else:
                    frac = float(state_models[pid].expected_workload_given_active)
                decision[pid] = float(base_means.get(pid, 0.0)) * frac
                realized[pid] = float(player_scores[pid][scenario])
            out[scenario], _ = _best_lineup_realized_points(
                roster, active, decision, realized, ctx.league, replacement
            )
        _emit_mc_progress(progress_callback, stop, ctx.predictive_scenarios, progress_phase)
    return out


def _snapshot_time(ctx: UtilityContext):
    raw = ctx.snapshot.get("snapshot_utc")
    if not raw:
        return None
    try:
        text = str(raw).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def _snapshot_locked_state(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    week: int,
    timing_by_id: dict[int, Any],
) -> tuple[dict[str, int], set[int]]:
    """Anchor already-locked ESPN starters/bench players at the snapshot time."""
    snapshot_time = _snapshot_time(ctx)
    slots = _lineup_slot_definitions(ctx.league)
    fixed: dict[str, int] = {}
    expired: set[int] = set()

    def pick_slot(player: dict[str, Any]) -> str | None:
        raw = str(player.get("lineup_slot") or "").strip().upper()
        pos = str(player.get("position") or "").strip().upper()
        if raw in {"", "BENCH", "BE", "IR", "RESERVE"}:
            return None
        if raw == "FLEX":
            for name, eligible in slots:
                if name.startswith("FLEX") and name not in fixed and pos in eligible:
                    return name
            return None
        wanted = raw if raw in POSITIONS else pos
        for name, eligible in slots:
            if name in fixed or name.startswith("FLEX"):
                continue
            if wanted in eligible and pos in eligible:
                return name
        return None

    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        timing = timing_by_id.get(pid)
        past_kickoff = bool(
            snapshot_time is not None
            and timing is not None
            and timing.kickoff is not None
            and timing.kickoff <= snapshot_time
        )
        locked = bool(player.get("lineup_locked")) or past_kickoff
        if not locked:
            continue
        expired.add(pid)
        slot = pick_slot(player)
        if slot is not None:
            fixed[slot] = pid
    return fixed, expired


def _simulate_current_week_realistic_policy(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    replacement: dict[str, float],
    week: int,
    player_scores: dict[int, np.ndarray],
    state_codes: dict[int, np.ndarray],
    state_models: dict[int, Any],
    base_means: dict[int, float],
    *,
    progress_callback: McProgressCallback | None = None,
    progress_phase: str = "current-week realistic",
) -> tuple[np.ndarray, bool]:
    """Sequential lock-aware policy using only information available by each kickoff.

    Active/inactive is revealed at ``kickoff - inactive_reveal_lead_minutes``.
    FULL versus LIMITED remains latent: an active player's decision value is the
    conditional expectation over workload states, not the sampled eventual workload.
    """
    timing_by_id: dict[int, Any] = {}
    relevant_ids: list[int] = []
    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        relevant_ids.append(pid)
        timing_by_id[pid] = ctx.lock_timing(player, week)
    if not relevant_ids or any(timing_by_id[pid].kickoff is None for pid in relevant_ids):
        return np.zeros(ctx.predictive_scenarios, dtype=float), False

    kickoff_groups: dict[Any, set[int]] = {}
    for pid in relevant_ids:
        kickoff_groups.setdefault(timing_by_id[pid].kickoff, set()).add(pid)
    kickoffs = sorted(kickoff_groups)
    out = np.zeros(ctx.predictive_scenarios, dtype=float)

    snapshot_fixed, snapshot_expired = _snapshot_locked_state(roster, ctx, week, timing_by_id)
    snapshot_time = _snapshot_time(ctx)

    batch_size = int(ctx.cfg.get("mc_progress_batch_size", 512))
    for start, stop in _mc_batches(ctx.predictive_scenarios, batch_size):
        for scenario in range(start, stop):
            locked_slots: dict[str, int] = dict(snapshot_fixed)
            expired: set[int] = set(snapshot_expired)
            for decision_time in kickoffs:
                if snapshot_time is not None and decision_time <= snapshot_time:
                    continue
                known_out: set[int] = set()
                decision_scores: dict[int, float] = {}
                eligible_ids: set[int] = set()
                for pid in relevant_ids:
                    if pid in expired or pid in locked_slots.values():
                        continue
                    timing = timing_by_id[pid]
                    model_state = state_models[pid]
                    reveal = timing.reveal_time
                    status_known = reveal is not None and reveal <= decision_time
                    code = int(state_codes[pid][scenario])
                    if status_known and code == 0:
                        known_out.add(pid)
                        continue
                    active_conditional_mean = (
                        float(base_means.get(pid, 0.0)) * model_state.expected_workload_given_active
                    )
                    if status_known:
                        value = active_conditional_mean
                    else:
                        value = model_state.p_active * active_conditional_mean
                    eligible_ids.add(pid)
                    decision_scores[pid] = float(value)

                current_ids = kickoff_groups[decision_time]
                assignment = _optimal_lineup_assignment(
                    roster,
                    eligible_ids,
                    decision_scores,
                    ctx.league,
                    fixed_slots=locked_slots,
                    avoid_flex_ids=current_ids,
                )
                for slot, pid in assignment.items():
                    if pid in current_ids and slot not in locked_slots:
                        locked_slots[slot] = pid
                expired.update(current_ids)

            realized = {pid: float(player_scores[pid][scenario]) for pid in relevant_ids}
            out[scenario] = _score_assignment(locked_slots, realized, ctx.league, replacement)
        _emit_mc_progress(progress_callback, stop, ctx.predictive_scenarios, progress_phase)
    return out, True


def _simulate_weekly_points(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    replacement_current: dict[str, float],
    replacement_season: dict[str, float],
) -> np.ndarray:
    out = np.zeros((ctx.scenarios, 17), dtype=float)
    for week in range(max(1, ctx.week), 18):
        scores: dict[int, float] = {}
        probabilities: dict[int, float] = {}
        for p in roster:
            pid = _finite_int(p.get("espn_id"))
            if pid is None:
                continue
            scores[pid] = _player_points(p, ctx, week)
            probabilities[pid] = _player_probability(p, ctx, week)

        repl = replacement_current if week == ctx.week else replacement_season
        for scenario in range(ctx.scenarios):
            active: dict[int, bool] = {}
            for p in roster:
                pid = _finite_int(p.get("espn_id"))
                if pid is None:
                    continue
                score = scores.get(pid, 0.0)
                if score <= 0.0:
                    active[pid] = False
                    continue
                active[pid] = bool(ctx.uniforms(pid)[scenario, week - 1] < probabilities.get(pid, 0.0))
            out[scenario, week - 1], _ = _best_lineup_points(roster, active, scores, ctx.league, repl)
    return out


def _simulate_predictive_weekly_points(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    replacement_current: dict[str, float],
    replacement_season: dict[str, float],
    *,
    current_week_policy: str = "realistic",
    progress_callback: McProgressCallback | None = None,
    progress_offset: int = 0,
    progress_total: int | None = None,
    progress_label: str = "predictive MC",
) -> np.ndarray:
    """Generate predictive weekly lineup yields with common random numbers.

    v0.26 changes only the current-week decision layer. The current week samples
    explicit OUT / ACTIVE_LIMITED / ACTIVE_FULL states. ``realistic`` processes
    kickoff locks sequentially and reveals active/inactive only when the inactive
    deadline has passed; FULL/LIMITED remains latent. ``idealized`` is an upper-bound
    branch policy that knows the complete workload state before any game locks.

    Future weeks retain the commissioned v0.23 availability-branch approximation
    until future-week status/timing forecasts are separately calibrated.
    """
    policy = str(current_week_policy or "realistic").lower()
    if policy not in {"realistic", "idealized_active", "idealized"}:
        raise ValueError(f"Unknown current_week_policy={current_week_policy!r}")

    out = np.zeros((ctx.predictive_scenarios, 17), dtype=float)
    first_week = max(1, ctx.week)
    weeks_count = max(0, 18 - first_week)
    local_total = max(1, weeks_count * ctx.predictive_scenarios)
    reported_total = int(progress_total) if progress_total is not None else int(progress_offset + local_total)
    completed = 0

    def report_week_progress(done_in_week: int, phase: str) -> None:
        done = min(local_total, completed + int(done_in_week))
        _emit_mc_progress(progress_callback, progress_offset + done, reported_total, f"{progress_label}: {phase}")

    for week in range(first_week, 18):
        repl = replacement_current if week == ctx.week else replacement_season

        if week == ctx.week:
            player_scores, state_codes, state_models, base_means = _current_week_state_samples(
                roster, ctx, week
            )
            if policy == "realistic":
                realistic, timing_ok = _simulate_current_week_realistic_policy(
                    roster,
                    ctx,
                    repl,
                    week,
                    player_scores,
                    state_codes,
                    state_models,
                    base_means,
                    progress_callback=lambda d, _t, phase: report_week_progress(d, phase),
                    progress_phase=f"week {week} realistic locks",
                )
                if timing_ok:
                    out[:, week - 1] = realistic
                else:
                    # Fail safe when schedule timing is missing: do not invent kickoff
                    # windows. Fall back to pre-lock active/inactive knowledge while
                    # keeping FULL/LIMITED workload latent; surface timing incompleteness
                    # through GUI/chat diagnostics.
                    out[:, week - 1] = _simulate_current_week_idealized_policy(
                        roster,
                        ctx,
                        repl,
                        week,
                        player_scores,
                        state_codes,
                        state_models,
                        base_means,
                        reveal_workload=False,
                        progress_callback=lambda d, _t, phase: report_week_progress(d, phase),
                        progress_phase=f"week {week} active/inactive fallback",
                    )
            elif policy == "idealized_active":
                out[:, week - 1] = _simulate_current_week_idealized_policy(
                    roster,
                    ctx,
                    repl,
                    week,
                    player_scores,
                    state_codes,
                    state_models,
                    base_means,
                    reveal_workload=False,
                    progress_callback=lambda d, _t, phase: report_week_progress(d, phase),
                    progress_phase=f"week {week} ideal-active",
                )
            else:
                out[:, week - 1] = _simulate_current_week_idealized_policy(
                    roster,
                    ctx,
                    repl,
                    week,
                    player_scores,
                    state_codes,
                    state_models,
                    base_means,
                    reveal_workload=True,
                    progress_callback=lambda d, _t, phase: report_week_progress(d, phase),
                    progress_phase=f"week {week} ideal-full",
                )
            completed += ctx.predictive_scenarios
            _emit_mc_progress(progress_callback, progress_offset + completed, reported_total, f"{progress_label}: week {week} complete")
            continue

        # Future weeks: preserve the commissioned binary availability policy.
        player_scores: dict[int, np.ndarray] = {}
        player_active: dict[int, np.ndarray] = {}
        decision_scores: dict[int, float] = {}
        for player in roster:
            pid = _finite_int(player.get("espn_id"))
            if pid is None:
                continue
            bye = ctx.league.get("bye_weeks_2026", {}).get(player.get("nfl_team"))
            try:
                is_bye = bye is not None and int(bye) == int(week)
            except (TypeError, ValueError):
                is_bye = False
            state = ctx.yield_state(player, week)
            decision_scores[pid] = float(state.operational_mean_ppg)
            if is_bye or state.availability_probability <= 0.0:
                player_scores[pid] = np.zeros(ctx.predictive_scenarios, dtype=float)
                player_active[pid] = np.zeros(ctx.predictive_scenarios, dtype=bool)
                continue
            if state.position == "DST" and state.dst_component_expectation:
                scores = simulate_dst_component_points(
                    state.dst_component_expectation,
                    scenarios=ctx.predictive_scenarios,
                    seed=ctx.seed + 1000003 * int(pid) + 97 * int(week),
                    target_mean=state.operational_mean_ppg,
                )
                scores = (
                    scores
                    + state.model_sd_ppg * ctx.epistemic_normals(pid)
                    + state.kinematic_sd_ppg * ctx.kinematic_normals(pid)[:, week - 1]
                )
            else:
                scores = sample_conditional_points(
                    state,
                    ctx.epistemic_normals(pid),
                    ctx.game_normals(pid)[:, week - 1],
                    ctx.kinematic_normals(pid)[:, week - 1],
                    ctx.interaction_normals(pid)[:, week - 1],
                )
            active = ctx.predictive_uniforms(pid)[:, week - 1] < state.availability_probability
            player_scores[pid] = scores
            player_active[pid] = active

        batch_size = int(ctx.cfg.get("mc_progress_batch_size", 512))
        for start, stop in _mc_batches(ctx.predictive_scenarios, batch_size):
            for scenario in range(start, stop):
                active_map = {pid: bool(values[scenario]) for pid, values in player_active.items()}
                score_map = {pid: float(values[scenario]) for pid, values in player_scores.items()}
                out[scenario, week - 1], _ = _best_lineup_realized_points(
                    roster, active_map, decision_scores, score_map, ctx.league, repl
                )
            report_week_progress(stop, f"week {week}")
        completed += ctx.predictive_scenarios
        _emit_mc_progress(progress_callback, progress_offset + completed, reported_total, f"{progress_label}: week {week} complete")
    return out

def _scenario_h2h_utility_against(
    weekly: np.ndarray, opponent: np.ndarray, ctx: UtilityContext
) -> np.ndarray:
    """Scenario H2H utility against an explicit opponent/field state.

    fixed6 makes the opponent state an explicit coordinate so an add/drop can
    perturb the *league* initial condition rather than changing only our roster.
    """
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    opponent = np.asarray(opponent, dtype=float)
    weekly = np.asarray(weekly, dtype=float)
    if opponent.shape != weekly.shape:
        raise ValueError(f"Opponent MC shape {opponent.shape} != roster MC shape {weekly.shape}")
    wins = (weekly > opponent).astype(float)
    wins[weekly == opponent] = 0.5
    return np.sum(wins * weights[None, :], axis=1) / norm


def _scenario_h2h_utility(weekly: np.ndarray, ctx: UtilityContext) -> np.ndarray:
    return _scenario_h2h_utility_against(weekly, np.asarray(ctx.opponent_predictive, dtype=float), ctx)


def evaluate_roster_predictive(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    *,
    current_week_policy: str = "realistic",
    progress_callback: McProgressCallback | None = None,
    progress_offset: int = 0,
    progress_total: int | None = None,
    progress_label: str | None = None,
    include_diagnostics: bool = True,
) -> tuple[RosterUtilityResult, np.ndarray, np.ndarray]:
    first_week = max(1, ctx.week)
    pass_work = max(1, (18 - first_week) * ctx.predictive_scenarios)
    local_total = (2 if include_diagnostics else 1) * pass_work
    reported_total = int(progress_total) if progress_total is not None else int(progress_offset + local_total)
    label = progress_label or str(current_week_policy)
    weekly = _simulate_predictive_weekly_points(
        roster, ctx, ctx.replacement_current, ctx.replacement_season,
        current_week_policy=current_week_policy,
        progress_callback=progress_callback,
        progress_offset=progress_offset,
        progress_total=reported_total,
        progress_label=f"{label} roster",
    )
    scenario_utility = _scenario_h2h_utility(weekly, ctx)
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)

    mean_week = np.mean(weekly, axis=0)
    scenario_lineup_ppg = np.sum(weekly * weights[None, :], axis=1) / norm
    season_expected = float(np.mean(scenario_lineup_ppg))
    current_expected = float(mean_week[ctx.week - 1])
    current_sd = float(np.std(weekly[:, ctx.week - 1], ddof=1)) if ctx.predictive_scenarios > 1 else 0.0
    season_sd = float(np.std(scenario_lineup_ppg, ddof=1)) if ctx.predictive_scenarios > 1 else 0.0
    current_nominal = _nominal_current_lineup(roster, ctx)

    insurance = 0.0
    if include_diagnostics:
        starter_ids = _healthy_starter_ids(roster, ctx)
        starter_only = [p for p in roster if _finite_int(p.get("espn_id")) in starter_ids]
        starter_weekly = _simulate_predictive_weekly_points(
            starter_only, ctx, ctx.replacement_current, ctx.replacement_season,
            current_week_policy=current_week_policy,
            progress_callback=progress_callback,
            progress_offset=progress_offset + pass_work,
            progress_total=reported_total,
            progress_label=f"{label} starter-only",
        )
        starter_ppg = np.sum(starter_weekly * weights[None, :], axis=1) / norm
        insurance = max(season_expected - float(np.mean(starter_ppg)), 0.0)
    _emit_mc_progress(progress_callback, progress_offset + local_total, reported_total, f"{label}: complete")

    bye = _deterministic_bye_profile(roster, ctx)
    relevant = bye[weights > 0]
    healthy_score = max(float(np.max(relevant)) if len(relevant) else 0.0, 0.0)
    bye_loss = float(np.sum((healthy_score - bye) * weights) / norm)
    bye_floor = float(np.min(relevant)) if len(relevant) else 0.0

    result = RosterUtilityResult(
        utility=float(np.mean(scenario_utility)),
        expected_h2h_win_probability=float(np.mean(scenario_utility)),
        current_week_expected_points=current_expected,
        current_week_nominal_points=current_nominal,
        season_expected_lineup_ppg=season_expected,
        bench_insurance_ppg=insurance,
        bye_floor_points=bye_floor,
        weighted_bye_loss_points=bye_loss,
        mc_scenarios=ctx.predictive_scenarios,
        current_week_sd_points=current_sd,
        season_lineup_sd_ppg=season_sd,
    )
    return result, scenario_utility, weekly


def _paired_mean_interval(
    delta: np.ndarray, *, seed: int, draws: int = 1000
) -> tuple[float, float]:
    """Return a deterministic 68% paired-resample interval for the mean effect.

    The per-universe season-win delta is necessarily discrete because weekly wins
    are Bernoulli outcomes.  Reporting its raw 16th/84th percentiles therefore gave
    misleading repeated intervals such as [0, 1/season].  Resampling the paired
    universes targets uncertainty in the *mean action effect* instead.
    """
    arr = np.asarray(delta, dtype=float)
    if len(arr) == 0:
        return 0.0, 0.0
    if len(arr) == 1:
        return float(arr[0]), float(arr[0])
    # Add/drop identifiers can include ESPN DST IDs, which are negative.  Preserve
    # deterministic pairing by mapping any signed seed onto the uint64 domain NumPy
    # accepts rather than failing on a valid defense action.
    normalized_seed = int(seed) & 0xFFFFFFFFFFFFFFFF
    rng = np.random.default_rng(normalized_seed)
    ix = rng.integers(0, len(arr), size=(max(int(draws), 100), len(arr)))
    means = np.mean(arr[ix], axis=1)
    return float(np.quantile(means, 0.16)), float(np.quantile(means, 0.84))


def _classify_paired_delta(
    delta: np.ndarray, cfg: dict[str, Any], *, mean_p16: float | None = None
) -> str:
    if len(delta) == 0:
        return "UNASSESSED"
    mean = float(np.mean(delta))
    p_better = float(np.mean(delta > 0.0))
    lower = float(mean_p16) if mean_p16 is not None else float(np.quantile(delta, 0.16))
    actionable_p = float(cfg.get("actionable_p_better", 0.90))
    lean_p = float(cfg.get("lean_p_better", 0.67))
    if mean > 0.0 and lower > 0.0 and p_better >= actionable_p:
        return "ACTIONABLE_EDGE"
    if mean > 0.0 and p_better >= lean_p:
        return "POSSIBLE_EDGE"
    return "NO_RESOLVED_EDGE"


def _nominal_current_lineup(roster: list[dict[str, Any]], ctx: UtilityContext) -> float:
    """Best legal all-available current lineup using v0.23 operational means."""
    scores: dict[int, float] = {}
    active: dict[int, bool] = {}
    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        state = ctx.yield_state(player, ctx.week)
        scores[pid] = float(state.operational_mean_ppg)
        status = availability_status(player)[0]
        active[pid] = status not in HARD_UNAVAILABLE_STATUSES and state.availability_probability > 0.0
    total, _ = _best_lineup_points(roster, active, scores, ctx.league, ctx.replacement_current)
    return float(total)


def _healthy_starter_ids(roster: list[dict[str, Any]], ctx: UtilityContext) -> set[int]:
    scores = {
        int(p["espn_id"]): float(p.get("season_ppg") or 0.0)
        for p in roster
        if p.get("espn_id") is not None
    }
    active = {pid: True for pid in scores}
    _total, selected = _best_lineup_points(roster, active, scores, ctx.league, {p: 0.0 for p in POSITIONS})
    return selected


def _market_projection_support(player: dict[str, Any], ctx: UtilityContext) -> float:
    """Confidence used only by the auxiliary market-option layer.

    The commissioned player mean is never changed here.  This support factor only
    prevents a weak/fallback projection from generating a large *additional* stash
    premium on top of the predictive model.  It combines explicit projection
    provenance with ESPN/model agreement when an anchor exists.
    """
    cfg = ctx.cfg
    default_source_support = {
        "ESPN_WEEKLY": 0.95,
        "ESPN_SEASON_DIV17": 0.65,
        "MODEL_LATENT_PPG_ZERO_FALLBACK": 0.25,
        "MODEL_LATENT_PPG_FALLBACK": 0.45,
        "MODEL_LATENT_PPG": 0.75,
        "WEEKLY_FALLBACK": 0.45,
    }
    source_cfg = dict(default_source_support)
    source_cfg.update(cfg.get("market_projection_source_support", {}))
    week_source = str(player.get("projection_source") or "UNKNOWN").upper()
    season_source = str(player.get("season_ppg_source") or "UNKNOWN").upper()

    def source_support(source: str, default: float) -> float:
        # Most-specific configured substring wins.
        best = None
        for key, value in source_cfg.items():
            key_u = str(key).upper()
            if key_u in source:
                if best is None or len(key_u) > best[0]:
                    best = (len(key_u), float(value))
        return float(best[1]) if best is not None else float(default)

    week_q = source_support(week_source, float(cfg.get("market_projection_unknown_support", 0.50)))
    season_q = source_support(season_source, float(cfg.get("market_projection_unknown_support", 0.50)))
    q = math.sqrt(max(week_q, 0.0) * max(season_q, 0.0))

    try:
        state = ctx.yield_state(player, ctx.week)
        z = state.espn_anchor_z
    except Exception:
        z = None
    if z is not None and math.isfinite(float(z)):
        # Agreement is a confidence coordinate, not an ESPN-forcing correction.
        # Large disagreement widens our epistemic concern and therefore reduces only
        # the auxiliary option premium; the commissioned predictive mean is untouched.
        agreement = 1.0 / math.sqrt(1.0 + 0.5 * float(z) * float(z))
        agreement = max(float(cfg.get("market_projection_agreement_floor", 0.45)), agreement)
        q *= agreement

    floor = float(cfg.get("market_projection_support_floor", 0.20))
    return min(max(float(q), floor), 1.0)


def _contingent_player_stream(
    ctx: UtilityContext, player_id: int, scenarios: int, *, kind: str
) -> np.ndarray:
    """Deterministic player-keyed stream for the small market-contingency ensemble."""
    key = (int(scenarios), int(player_id))
    if kind == "role":
        cache = ctx._contingent_role_normals
        code = 0xC041
        normal = True
    elif kind == "active":
        cache = ctx._contingent_active_uniforms
        code = 0xC0A1
        normal = False
    elif kind == "limited":
        cache = ctx._contingent_limited_uniforms
        code = 0xC0B1
        normal = False
    else:
        raise ValueError(f"Unknown contingent stream kind: {kind}")
    cached = cache.get(key)
    if cached is not None:
        return cached
    seed_seq = np.random.SeedSequence([ctx.seed, code, int(player_id) & 0xFFFFFFFF])
    rng = np.random.default_rng(seed_seq)
    arr = rng.standard_normal(int(scenarios)) if normal else rng.random(int(scenarios))
    cache[key] = arr
    return arr


def _contingent_active_probability(position: str, ctx: UtilityContext) -> float:
    defaults = {"QB": 0.92, "RB": 0.84, "WR": 0.87, "TE": 0.87}
    configured = dict(defaults)
    configured.update(ctx.cfg.get("contingent_active_probability", {}))
    return min(max(float(configured.get(position, 0.88)), 0.05), 0.995)


def _contingent_role_sd_floor(position: str, ctx: UtilityContext) -> float:
    defaults = {"QB": 0.8, "RB": 1.4, "WR": 1.4, "TE": 1.2}
    configured = dict(defaults)
    configured.update(ctx.cfg.get("contingent_role_sd_floor_ppg", {}))
    return max(float(configured.get(position, 1.0)), 0.0)


def roster_option_scarcity_value(
    roster: list[dict[str, Any]],
    ctx: UtilityContext,
    *,
    scenarios: int | None = None,
) -> dict[str, Any]:
    """Paired future-roster-state value for bench option and replacement depth.

    fixed4 replaces the deterministic upside / one-starter-out probes with a small,
    separate Monte Carlo over *future roster states*.  It is intentionally not a
    fantasy-score simulation.  For each player-keyed common-random-number state we
    sample future availability, LIMITED workload, and latent role/mean uncertainty,
    then optimize the legal lineup.  HOLD and every add/drop alternative therefore
    see the same football/availability state for every shared player.

    ``future_option_ppg`` is the mean lineup advantage of the full roster over the
    current starter core under those sampled future states.  This makes deep bench
    value non-zero when multiple starters can be unavailable or roles can move, while
    preserving diminishing returns because only a legal optimal lineup scores.

    ``replacement_scarcity_ppg`` is the same bench-depth advantage conditional on a
    state where at least one current skill-position starter is unavailable/limited.
    It is a diagnostic in fixed4; the default utility weight is zero to avoid double
    counting the same contingent depth already represented by future_option_ppg.
    """
    n = max(32, int(scenarios or ctx.cfg.get("contingent_roster_scenarios", 512)))
    skill = {"QB", "RB", "WR", "TE"}
    starter_ids = _healthy_starter_ids(roster, ctx)
    starter_core = [p for p in roster if _finite_int(p.get("espn_id")) in starter_ids]

    full_scores: dict[int, np.ndarray] = {}
    full_active: dict[int, np.ndarray] = {}
    support_values: list[float] = []
    stressed_starter = np.zeros(n, dtype=bool)
    limited_prob = min(max(float(ctx.cfg.get("contingent_limited_probability", 0.10)), 0.0), 0.50)
    limited_factor = min(max(float(ctx.cfg.get("contingent_limited_workload_factor", 0.62)), 0.10), 1.0)

    for player in roster:
        pid = _finite_int(player.get("espn_id"))
        if pid is None:
            continue
        pos = str(player.get("position") or "")
        mu = max(float(player.get("season_ppg") or 0.0), 0.0)
        if pos not in skill:
            full_scores[pid] = np.full(n, mu, dtype=float)
            full_active[pid] = np.ones(n, dtype=bool)
            continue

        support = _market_projection_support(player, ctx)
        support_values.append(support)
        replacement = max(float(ctx.replacement_season.get(pos, 0.0)), 0.0)
        # Auxiliary market value is deliberately shrunk toward the actual free-agent
        # replacement coordinate when projection provenance is weak.  The commissioned
        # player projection used by the main predictive model is not changed.
        supported_mu = replacement + support * (mu - replacement)
        latent_sd = max(float(player.get("latent_mean_sd_ppg") or 0.0), _contingent_role_sd_floor(pos, ctx))
        latent_sd *= support
        role_z = _contingent_player_stream(ctx, pid, n, kind="role")
        scores = np.maximum(supported_mu + latent_sd * role_z, 0.0)

        active_u = _contingent_player_stream(ctx, pid, n, kind="active")
        limited_u = _contingent_player_stream(ctx, pid, n, kind="limited")
        active = active_u < _contingent_active_probability(pos, ctx)
        limited = active & (limited_u < limited_prob)
        scores = np.where(limited, scores * limited_factor, scores)
        full_scores[pid] = scores
        full_active[pid] = active
        if pid in starter_ids:
            stressed_starter |= (~active) | limited

    full_lineup = np.zeros(n, dtype=float)
    core_lineup = np.zeros(n, dtype=float)
    for scenario in range(n):
        active_map = {pid: bool(values[scenario]) for pid, values in full_active.items()}
        score_map = {pid: float(values[scenario]) for pid, values in full_scores.items()}
        full_lineup[scenario], _ = _best_lineup_points(
            roster, active_map, score_map, ctx.league, ctx.replacement_season
        )
        core_lineup[scenario], _ = _best_lineup_points(
            starter_core, active_map, score_map, ctx.league, ctx.replacement_season
        )

    depth = np.maximum(full_lineup - core_lineup, 0.0)
    future_option = float(np.mean(depth)) if len(depth) else 0.0
    scarcity = float(np.mean(depth[stressed_starter])) if np.any(stressed_starter) else 0.0
    return {
        "future_option_ppg": future_option,
        "replacement_scarcity_ppg": scarcity,
        "contingent_lineup_ppg": float(np.mean(full_lineup)) if len(full_lineup) else 0.0,
        "contingent_stress_fraction": float(np.mean(stressed_starter)) if len(stressed_starter) else 0.0,
        "projection_support_mean": float(np.mean(support_values)) if support_values else 1.0,
        "contingent_scenarios": int(n),
        "portfolio_method": "PAIRED_FUTURE_ROSTER_STATES_V030_FIXED4",
    }


def _option_scarcity_utility_adjustment(
    before: dict[str, Any], after: dict[str, Any], ctx: UtilityContext
) -> dict[str, float]:
    cfg = ctx.cfg
    d_option = float(after["future_option_ppg"] - before["future_option_ppg"])
    d_scarcity = float(after["replacement_scarcity_ppg"] - before["replacement_scarcity_ppg"])
    denom = max(4.0 * float(ctx.matchup_scale), 1e-6)
    option_u = float(cfg.get("future_option_utility_weight", 0.35)) * d_option / denom
    # fixed4 treats scarcity as a diagnostic decomposition of the same contingent
    # bench-depth ensemble.  Its default utility weight is zero to avoid double
    # counting future-option value; a non-zero config remains available for research.
    scarcity_u = float(cfg.get("replacement_scarcity_utility_weight", 0.0)) * d_scarcity / denom
    return {
        "delta_future_option_ppg": d_option,
        "delta_replacement_scarcity_ppg": d_scarcity,
        "delta_future_option_utility": option_u,
        "delta_replacement_scarcity_utility": scarcity_u,
        "delta_total_utility": option_u + scarcity_u,
        "before_projection_support_mean": float(before.get("projection_support_mean", 1.0)),
        "after_projection_support_mean": float(after.get("projection_support_mean", 1.0)),
    }


def _classify_market_action(
    raw_delta: np.ndarray,
    adjusted_delta: np.ndarray,
    cfg: dict[str, Any],
    *,
    raw_p16: float,
    adjusted_p16: float,
) -> tuple[str, str, str]:
    """Classify direct-roster and full counterfactual league-state responses.

    ``raw_delta`` is the paired response if only our roster is changed.
    ``adjusted_delta`` is the authoritative fixed6 response after the released
    player is propagated into the league state.  The legacy ``combined`` field
    name is retained in the JSON schema, but no auxiliary option coefficient is
    added to it.
    """
    raw_class = _classify_paired_delta(raw_delta, cfg, mean_p16=raw_p16)
    league_class = _classify_paired_delta(adjusted_delta, cfg, mean_p16=adjusted_p16)
    return league_class, raw_class, league_class

def _deterministic_bye_profile(roster: list[dict[str, Any]], ctx: UtilityContext) -> np.ndarray:
    weekly = np.zeros(17, dtype=float)
    for week in range(max(1, ctx.week), 18):
        scores: dict[int, float] = {}
        active: dict[int, bool] = {}
        for p in roster:
            pid = _finite_int(p.get("espn_id"))
            if pid is None:
                continue
            score = _player_points(p, ctx, week)
            scores[pid] = score
            if week == ctx.week and availability_status(p)[0] in HARD_UNAVAILABLE_STATUSES:
                active[pid] = False
            else:
                active[pid] = score > 0.0
        repl = ctx.replacement_current if week == ctx.week else ctx.replacement_season
        weekly[week - 1], _ = _best_lineup_points(roster, active, scores, ctx.league, repl)
    return weekly


def evaluate_roster_utility(roster: list[dict[str, Any]], ctx: UtilityContext) -> RosterUtilityResult:
    weekly = ctx._simulate_weekly_points(roster)
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)

    mean_week = np.mean(weekly, axis=0)
    season_expected = float(np.sum(mean_week * weights) / norm)
    current_expected = float(mean_week[ctx.week - 1])
    current_nominal = _nominal_current_lineup(roster, ctx)

    refs = np.asarray(ctx.opponent_reference, dtype=float)
    z = (weekly - refs[None, :]) / max(ctx.matchup_scale, 1e-6)
    win = 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))
    scenario_utility = np.sum(win * weights[None, :], axis=1) / norm
    expected_h2h = float(np.mean(scenario_utility))

    starter_ids = _healthy_starter_ids(roster, ctx)
    starter_only = [p for p in roster if _finite_int(p.get("espn_id")) in starter_ids]
    starter_weekly = ctx._simulate_weekly_points(starter_only)
    starter_mean = np.mean(starter_weekly, axis=0)
    starter_expected = float(np.sum(starter_mean * weights) / norm)
    insurance = max(season_expected - starter_expected, 0.0)

    bye = _deterministic_bye_profile(roster, ctx)
    relevant = bye[weights > 0]
    healthy_score = max(float(np.max(relevant)) if len(relevant) else 0.0, 0.0)
    bye_loss = float(np.sum((healthy_score - bye) * weights) / norm)
    bye_floor = float(np.min(relevant)) if len(relevant) else 0.0

    return RosterUtilityResult(
        utility=expected_h2h,
        expected_h2h_win_probability=expected_h2h,
        current_week_expected_points=current_expected,
        current_week_nominal_points=current_nominal,
        season_expected_lineup_ppg=season_expected,
        bench_insurance_ppg=insurance,
        bye_floor_points=bye_floor,
        weighted_bye_loss_points=bye_loss,
    )


def _legal_drop(player: dict[str, Any]) -> bool:
    if player.get("droppable") is False:
        return False
    if player.get("lineup_locked") is True:
        return False
    return True


def _position_counts(roster: list[dict[str, Any]]) -> dict[str, int]:
    out = {p: 0 for p in POSITIONS}
    for player in roster:
        pos = str(player.get("position") or "")
        if pos in out:
            out[pos] += 1
    return out


def _legal_roster_after_add_drop(
    roster: list[dict[str, Any]], add: dict[str, Any], drop: dict[str, Any], league: dict[str, Any]
) -> bool:
    counts = _position_counts(roster)
    dpos = str(drop.get("position") or "")
    apos = str(add.get("position") or "")
    if dpos in counts:
        counts[dpos] -= 1
    if apos in counts:
        counts[apos] += 1
    maxima = league.get("position_maximums", {})
    for pos, maximum in maxima.items():
        if pos in counts and counts[pos] > int(maximum):
            return False
    # Evaluate one-step add/drop actions as a complete roster state. Do not give an
    # action a free phantom streamer by allowing it to remove the roster's only QB,
    # TE, K, DST, etc. Random injury scenarios may still use replacement-level fills.
    starters = league.get("roster", {})
    for pos in ("QB", "RB", "WR", "TE", "K", "DST"):
        if counts.get(pos, 0) < int(starters.get(pos, 0)):
            return False
    return apos in POSITIONS


def preselect_candidates(
    available: list[dict[str, Any]], cfg: dict[str, Any], position: str | None = None
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in available:
        status = str(p.get("fantasy_status") or "").upper()
        pos = str(p.get("position") or "")
        if status not in {"FREEAGENT", "WAIVERS", "WAIVER"} or pos not in PLAYER_POSITIONS:
            continue
        if position and pos != position:
            continue
        current = float(p.get("projection_points") or 0.0)
        season = float(p.get("season_ppg") or 0.0)
        owned = _finite_float(p.get("percent_owned")) or 0.0
        adds = _finite_int(p.get("sleeper_trending_add_24h")) or 0
        drops = _finite_int(p.get("sleeper_trending_drop_24h")) or 0
        trend = math.log1p(max(adds, 0)) - 0.5 * math.log1p(max(drops, 0))
        p = dict(p)
        p["_preselect_score"] = 0.45 * current + 0.55 * season + 0.012 * owned + 0.08 * trend
        rows.append(p)

    rows.sort(key=lambda x: float(x.get("_preselect_score") or 0.0), reverse=True)
    total_limit = max(1, int(cfg.get("candidate_limit", 80)))
    floor = max(0, int(cfg.get("candidate_floor_per_position", 8)))
    selected: dict[int, dict[str, Any]] = {}
    for pos in PLAYER_POSITIONS:
        for p in [r for r in rows if r.get("position") == pos][:floor]:
            pid = _finite_int(p.get("espn_id"))
            if pid is not None:
                selected[pid] = p
    for p in rows:
        if len(selected) >= total_limit:
            break
        pid = _finite_int(p.get("espn_id"))
        if pid is not None:
            selected[pid] = p
    return sorted(selected.values(), key=lambda x: float(x.get("_preselect_score") or 0.0), reverse=True)


def _manager_claim_probability(candidate: dict[str, Any], roster: list[dict[str, Any]], cfg: dict[str, Any]) -> float:
    pos = str(candidate.get("position") or "")
    cand = float(candidate.get("season_ppg") or 0.0)
    same = sorted([float(p.get("season_ppg") or 0.0) for p in roster if p.get("position") == pos])
    weakest = same[0] if same else 0.0
    improvement = max(cand - weakest, 0.0)
    counts = _position_counts(roster)
    target = cfg.get("opponent_roster_target", {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1})
    need_bonus = float(cfg.get("waiver_need_logit_bonus", 0.6)) if counts.get(pos, 0) < int(target.get(pos, 0)) else 0.0
    owned = _finite_float(candidate.get("percent_owned")) or 0.0
    adds = _finite_int(candidate.get("sleeper_trending_add_24h")) or 0
    drops = _finite_int(candidate.get("sleeper_trending_drop_24h")) or 0
    trend = math.log1p(max(adds, 0)) - 0.5 * math.log1p(max(drops, 0))
    logit = (
        float(cfg.get("waiver_claim_logit_intercept", -4.0))
        + float(cfg.get("waiver_improvement_logit_per_ppg", 0.15)) * improvement
        + float(cfg.get("waiver_owned_logit_per_pct", 0.015)) * owned
        + float(cfg.get("waiver_trend_logit_weight", 0.08)) * trend
        + need_bonus
    )
    return float(1.0 / (1.0 + math.exp(-max(min(logit, 20.0), -20.0))))


def _deterministic_manager_roster_score(
    roster: list[dict[str, Any]], ctx: UtilityContext
) -> tuple[float, float]:
    """Fast modeled lineup score for waiver-manager behavior.

    This uses the same player yield states, future season values, byes, positional
    constraints, and replacement levels as the season model, but deliberately avoids
    a full stochastic roster MC for every higher-priority manager/candidate pair.
    """
    key = tuple(sorted(pid for pid in (_finite_int(p.get("espn_id")) for p in roster) if pid is not None))
    cached = ctx._waiver_roster_score_cache.get(key)
    if cached is not None:
        return cached
    weekly = np.zeros(17, dtype=float)
    for week in range(max(1, ctx.week), 18):
        scores: dict[int, float] = {}
        active: dict[int, bool] = {}
        for player in roster:
            pid = _finite_int(player.get("espn_id"))
            if pid is None:
                continue
            score = _player_points(player, ctx, week)
            scores[pid] = float(score)
            if week == ctx.week and availability_status(player)[0] in HARD_UNAVAILABLE_STATUSES:
                active[pid] = False
            else:
                active[pid] = score > 0.0
        repl = ctx.replacement_current if week == ctx.week else ctx.replacement_season
        weekly[week - 1], _ = _best_lineup_points(roster, active, scores, ctx.league, repl)
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    season = float(np.sum(weekly * weights) / norm)
    current = float(weekly[ctx.week - 1])
    out = (season, current)
    ctx._waiver_roster_score_cache[key] = out
    return out


def _best_manager_add_drop_interest(
    candidate: dict[str, Any], roster: list[dict[str, Any]], ctx: UtilityContext
) -> dict[str, Any]:
    """Fast modeled claim interest for another manager.

    This is intentionally a behavior feature, not our action valuation.  It asks how
    much the candidate improves that manager's modeled season lineup after their best
    legal release, using the same player-yield/bye/availability state already present
    in the shared season model.
    """
    baseline_season, baseline_current = _deterministic_manager_roster_score(roster, ctx)
    best = None
    best_score = -float("inf")
    for drop in roster:
        if not _legal_drop(drop):
            continue
        if not _legal_roster_after_add_drop(roster, candidate, drop, ctx.league):
            continue
        drop_id = _finite_int(drop.get("espn_id"))
        new_roster = [p for p in roster if _finite_int(p.get("espn_id")) != drop_id] + [dict(candidate)]
        season_score, current_score = _deterministic_manager_roster_score(new_roster, ctx)
        score = float(season_score)
        if score > best_score:
            best_score = score
            best = (drop, season_score, current_score)
    if best is None:
        return {
            "legal": False,
            "drop_espn_id": None,
            "drop_name": None,
            "delta_season_ppg": -99.0,
            "delta_current_week": -99.0,
            "delta_insurance_ppg": 0.0,
        }
    drop, season_score, current_score = best
    return {
        "legal": True,
        "drop_espn_id": _finite_int(drop.get("espn_id")),
        "drop_name": drop.get("name"),
        "delta_season_ppg": float(season_score - baseline_season),
        "delta_current_week": float(current_score - baseline_current),
        "delta_insurance_ppg": 0.0,
    }




def _release_claim_probability(
    candidate: dict[str, Any], roster: list[dict[str, Any]], interest: dict[str, Any], ctx: UtilityContext
) -> float:
    """Behavior probability that another manager claims a released player.

    This is only the stochastic state-transition kernel.  Player/roster value is
    supplied separately by the commissioned predictive football model below.
    """
    if not bool(interest.get("legal")):
        return 0.0
    gain = float(interest.get("delta_season_ppg") or 0.0)
    if gain < float(ctx.cfg.get("league_response_claim_min_season_ppg", 0.02)):
        return 0.0
    pos = str(candidate.get("position") or "")
    counts = _position_counts(roster)
    target = ctx.cfg.get("opponent_roster_target", {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1})
    need = counts.get(pos, 0) < int(target.get(pos, 0))
    owned = _finite_float(candidate.get("percent_owned")) or 0.0
    adds = _finite_int(candidate.get("sleeper_trending_add_24h")) or 0
    drops = _finite_int(candidate.get("sleeper_trending_drop_24h")) or 0
    trend = math.log1p(max(adds, 0)) - 0.5 * math.log1p(max(drops, 0))
    logit = (
        float(ctx.cfg.get("league_response_claim_logit_intercept", ctx.cfg.get("waiver_claim_utility_logit_intercept", -2.6)))
        + float(ctx.cfg.get("league_response_claim_season_ppg_weight", ctx.cfg.get("waiver_claim_season_ppg_weight", 1.10))) * gain
        + float(ctx.cfg.get("league_response_claim_current_week_weight", ctx.cfg.get("waiver_claim_current_week_weight", 0.12))) * float(interest.get("delta_current_week") or 0.0)
        + float(ctx.cfg.get("waiver_owned_logit_per_pct", 0.015)) * owned
        + float(ctx.cfg.get("waiver_trend_logit_weight", 0.08)) * trend
        + (float(ctx.cfg.get("waiver_need_logit_bonus", 0.6)) if need else 0.0)
    )
    return float(1.0 / (1.0 + math.exp(-max(min(logit, 20.0), -20.0))))


def _season_lineup_from_weekly(weekly: np.ndarray, ctx: UtilityContext) -> np.ndarray:
    weeks, weights = week_weights(ctx.league)
    weights = np.asarray(weights, dtype=float)
    weights[weeks < ctx.week] = 0.0
    if float(weights.sum()) <= 0:
        weights[weeks >= ctx.week] = 1.0
    norm = max(float(weights.sum()), 1e-12)
    return np.sum(np.asarray(weekly, dtype=float) * weights[None, :], axis=1) / norm


def _league_response_team_baseline(team_id: int, roster: list[dict[str, Any]], ctx: UtilityContext, scenarios: int) -> np.ndarray:
    key = (int(scenarios), int(team_id))
    cached = ctx._league_response_baseline_cache.get(key)
    if cached is not None:
        return cached
    arr = _simulate_predictive_weekly_points(
        roster, ctx, ctx.replacement_current, ctx.replacement_season,
        current_week_policy="realistic",
    )
    ctx._league_response_baseline_cache[key] = np.asarray(arr, dtype=float)
    return ctx._league_response_baseline_cache[key]


def released_player_league_state_response(
    candidate: dict[str, Any], ctx: UtilityContext, *, scenarios: int | None = None
) -> dict[str, Any]:
    """First-order paired counterfactual response when a dropped player re-enters waivers.

    The discrete claimant/release state is chosen cheaply.  Crucially, *value* is not:
    every plausible recipient roster is propagated through the same commissioned
    predictive player/availability/lineup model before and after the claim with common
    random numbers.  Claim probabilities are then conditioned on that modeled roster
    response and waiver priority determines the winner distribution.

    This function computes the commissioned order-1 response exactly, then v0.36
    augments it with a bounded order-2+ player-channel cascade.
    """
    pid = _finite_int(candidate.get("espn_id"))
    n = max(16, int(scenarios or ctx.cfg.get("league_state_response_scenarios", 32)))
    empty = {
        "model": "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V031_FIRST_ORDER",
        "scenarios": n,
        "p_claimed": 0.0,
        "p_unclaimed": 1.0,
        "expected_recipient_gain_ppg": 0.0,
        "field_shift_ppg": 0.0,
        "current_opponent_shift_ppg": 0.0,
        "opponent_reference_shift_ppg_by_week": [0.0] * 17,
        "destinations": [],
    }
    if pid is None:
        return empty
    cache_key = (n, int(pid))
    cached = ctx._league_release_response_cache.get(cache_key)
    if cached is not None:
        return dict(cached)

    old_n = int(ctx.predictive_scenarios)
    ctx.set_predictive_scenarios(n)
    try:
        team_meta = {
            int(t.get("team_id")): t
            for t in (ctx.espn.get("teams") or [])
            if _finite_int(t.get("team_id")) is not None
        }
        candidates: list[dict[str, Any]] = []
        for tid, roster in ctx.all_team_rosters.items():
            if int(tid) == int(ctx.team_id):
                continue
            # The discrete claimant roster transition is selected with the same
            # deterministic lineup response already used by the waiver-manager
            # model.  The authoritative magnitude is still evaluated below with
            # paired predictive MC; this step only chooses which legal player exits.
            transition_interest = _best_manager_add_drop_interest(candidate, roster, ctx)
            if not bool(transition_interest.get("legal")):
                continue
            drop_id = _finite_int(transition_interest.get("drop_espn_id"))
            if drop_id is None:
                continue
            drop = next(
                (p for p in roster if _finite_int(p.get("espn_id")) == int(drop_id)),
                None,
            )
            if drop is None:
                continue
            after = [p for p in roster if _finite_int(p.get("espn_id")) != drop_id] + [dict(candidate)]
            baseline_weekly = _league_response_team_baseline(int(tid), roster, ctx, n)
            after_weekly = _simulate_predictive_weekly_points(
                after, ctx, ctx.replacement_current, ctx.replacement_season,
                current_week_policy="realistic",
            )
            delta_weekly = np.asarray(after_weekly, dtype=float) - np.asarray(baseline_weekly, dtype=float)
            delta_weekly_mean = np.mean(delta_weekly, axis=0)
            delta_season = _season_lineup_from_weekly(after_weekly, ctx) - _season_lineup_from_weekly(baseline_weekly, ctx)
            delta_season_mean = float(np.mean(delta_season))
            interest = {
                "legal": True,
                "drop_espn_id": int(drop_id),
                "drop_name": drop.get("name"),
                "delta_season_ppg": delta_season_mean,
                "delta_current_week": float(delta_weekly_mean[ctx.week - 1]),
            }
            claim = _release_claim_probability(candidate, roster, interest, ctx)
            meta = team_meta.get(int(tid)) or {}
            candidates.append({
                "team_id": int(tid),
                "team_name": str(meta.get("name") or f"team {tid}"),
                "waiver_rank": _finite_int(meta.get("waiver_rank")),
                "claim_probability": float(claim),
                "drop_espn_id": int(drop_id),
                "drop_name": drop.get("name"),
                "delta_weekly_mean": np.asarray(delta_weekly_mean, dtype=float),
                "delta_season_ppg": delta_season_mean,
                "delta_current_week": float(delta_weekly_mean[ctx.week - 1]),
            })

        candidates.sort(key=lambda r: (int(r["waiver_rank"] or 999), int(r["team_id"])))
        survival = 1.0
        for row in candidates:
            claim = min(max(float(row["claim_probability"]), 0.0), 1.0)
            row["winner_probability"] = float(survival * claim)
            survival *= 1.0 - claim

        # The predictive opponent reference is the mean over *all* other league
        # teams, including teams that cannot make this particular claim.  Therefore
        # the field perturbation denominator must match that system boundary.
        other_count = max(1, sum(1 for tid in ctx.all_team_rosters if int(tid) != int(ctx.team_id)))
        field_shift = np.zeros(17, dtype=float)
        current_opponent_shift = 0.0
        expected_recipient_gain = 0.0
        opponent_id = find_week_opponent(ctx.snapshot, ctx.team_id)
        destination_rows: list[dict[str, Any]] = []
        for row in candidates:
            winner_p = float(row["winner_probability"])
            delta_weekly_mean = np.asarray(row["delta_weekly_mean"], dtype=float)
            expected_recipient_gain += winner_p * float(row["delta_season_ppg"])
            field_shift += (winner_p / float(other_count)) * delta_weekly_mean
            if opponent_id is not None and int(row["team_id"]) == int(opponent_id):
                current_opponent_shift += winner_p * float(row["delta_current_week"])
            destination_rows.append({
                "team_id": row["team_id"], "team_name": row["team_name"],
                "waiver_rank": row["waiver_rank"], "winner_probability": winner_p,
                "claim_probability": row["claim_probability"],
                "best_drop_espn_id": row["drop_espn_id"], "best_drop_name": row["drop_name"],
                "delta_season_ppg": row["delta_season_ppg"],
                "delta_current_week": row["delta_current_week"],
            })

        reference_shift = np.asarray(field_shift, dtype=float).copy()
        reference_shift[ctx.week - 1] = float(current_opponent_shift)
        season_field = _season_lineup_from_weekly(reference_shift[None, :], ctx)[0]
        destination_rows.sort(key=lambda r: float(r.get("winner_probability") or 0.0), reverse=True)
        first_order = {
            "model": "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V031_FIRST_ORDER",
            "scenarios": int(n),
            "p_claimed": float(1.0 - survival),
            "p_unclaimed": float(survival),
            "expected_recipient_gain_ppg": float(expected_recipient_gain),
            "field_shift_ppg": float(season_field),
            "current_opponent_shift_ppg": float(current_opponent_shift),
            "opponent_reference_shift_ppg_by_week": [float(x) for x in reference_shift],
            "destinations": destination_rows[: int(ctx.cfg.get("league_response_report_destinations", 5))],
        }
        from .league_response_v036 import extend_release_response
        result = extend_release_response(candidate, ctx, first_order, start_week=int(ctx.week))
        ctx._league_release_response_cache[cache_key] = dict(result)
        return result
    finally:
        ctx.set_predictive_scenarios(old_n)


def waiver_screen_acquisition_probability(candidate: dict[str, Any], ctx: UtilityContext) -> float:
    """Cheap waiver acquisition estimate used only by the broad action screener.

    v0.30-fixed defers the expensive modeled best-add/drop analysis for every
    higher-priority manager until a waiver candidate survives the broad action
    screen.  This helper intentionally uses the older inexpensive roster-need
    signal only for pruning.  Final displayed P(acquire) always comes from
    ``waiver_blocker_diagnostics`` / ``waiver_acquisition_probability``.
    """
    user_rank = _finite_int(ctx.team.get("waiver_rank"))
    if user_rank is None:
        return float(ctx.cfg.get("waiver_p_acquire_default", 0.35))
    claims: list[float] = []
    for team in ctx.espn.get("teams") or []:
        tid = _finite_int(team.get("team_id"))
        rank = _finite_int(team.get("waiver_rank"))
        if tid is None or tid == ctx.team_id or rank is None or rank >= user_rank:
            continue
        roster = ctx.all_team_rosters.get(tid, [])
        claims.append(_manager_claim_probability(candidate, roster, ctx.cfg))
    if not claims:
        return 1.0
    p = float(np.prod([1.0 - x for x in claims]))
    return float(max(float(ctx.cfg.get("waiver_p_acquire_floor", 0.02)), min(1.0, p)))


def waiver_blocker_diagnostics(candidate: dict[str, Any], ctx: UtilityContext) -> list[dict[str, Any]]:
    user_rank = _finite_int(ctx.team.get("waiver_rank"))
    if user_rank is None:
        return []
    candidate_id = _finite_int(candidate.get("espn_id"))
    rows: list[dict[str, Any]] = []
    for team in ctx.espn.get("teams") or []:
        tid = _finite_int(team.get("team_id"))
        rank = _finite_int(team.get("waiver_rank"))
        if tid is None or tid == ctx.team_id or rank is None or rank >= user_rank:
            continue
        cache_key = (int(tid), int(candidate_id or -1))
        interest = ctx._waiver_interest_cache.get(cache_key)
        roster = ctx.all_team_rosters.get(tid, [])
        if interest is None:
            interest = _best_manager_add_drop_interest(candidate, roster, ctx)
            ctx._waiver_interest_cache[cache_key] = dict(interest)
        pos = str(candidate.get("position") or "")
        counts = _position_counts(roster)
        target = ctx.cfg.get("opponent_roster_target", {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1})
        need = counts.get(pos, 0) < int(target.get(pos, 0))
        owned = _finite_float(candidate.get("percent_owned")) or 0.0
        adds = _finite_int(candidate.get("sleeper_trending_add_24h")) or 0
        drops = _finite_int(candidate.get("sleeper_trending_drop_24h")) or 0
        trend = math.log1p(max(adds, 0)) - 0.5 * math.log1p(max(drops, 0))
        if interest.get("legal"):
            logit = (
                float(ctx.cfg.get("waiver_claim_utility_logit_intercept", -2.6))
                + float(ctx.cfg.get("waiver_claim_season_ppg_weight", 1.10)) * float(interest.get("delta_season_ppg") or 0.0)
                + float(ctx.cfg.get("waiver_claim_current_week_weight", 0.12)) * float(interest.get("delta_current_week") or 0.0)
                + float(ctx.cfg.get("waiver_owned_logit_per_pct", 0.015)) * owned
                + float(ctx.cfg.get("waiver_trend_logit_weight", 0.08)) * trend
                + (float(ctx.cfg.get("waiver_need_logit_bonus", 0.6)) if need else 0.0)
            )
            claim = float(1.0 / (1.0 + math.exp(-max(min(logit, 20.0), -20.0))))
        else:
            claim = 0.0
        rows.append({
            "team_id": tid,
            "team_name": team.get("name"),
            "waiver_rank": rank,
            "claim_probability": claim,
            "need": bool(need),
            "best_drop_espn_id": interest.get("drop_espn_id"),
            "best_drop_name": interest.get("drop_name"),
            "delta_season_ppg": interest.get("delta_season_ppg"),
            "delta_current_week": interest.get("delta_current_week"),
            "model": "UNCALIBRATED_MANAGER_CLAIM_UTILITY_V030",
        })
    rows.sort(key=lambda r: int(r.get("waiver_rank") or 999))
    return rows


def waiver_acquisition_probability(
    candidate: dict[str, Any],
    ctx: UtilityContext,
    blockers: list[dict[str, Any]] | None = None,
) -> float:
    user_rank = _finite_int(ctx.team.get("waiver_rank"))
    if user_rank is None:
        return float(ctx.cfg.get("waiver_p_acquire_default", 0.35))
    blocker_rows = waiver_blocker_diagnostics(candidate, ctx) if blockers is None else blockers
    if not blocker_rows:
        return 1.0
    p = float(np.prod([1.0 - float(row.get("claim_probability") or 0.0) for row in blocker_rows]))
    return min(max(p, float(ctx.cfg.get("waiver_p_acquire_floor", 0.02))), 1.0)


def _prediction_rows(roster: list[dict[str, Any]], ctx: UtilityContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for player in roster:
        for week in range(max(1, ctx.week), 18):
            state = ctx.yield_state(player, week)
            row = state.to_dict()
            row["fantasy_status"] = player.get("fantasy_status")
            row["availability_status"] = availability_status(player)[0] if week == ctx.week else "MODELED_NONBYE"
            if week == ctx.week:
                availability = ctx.availability_state(player, week)
                row.update({f"availability_{k}": v for k, v in availability.to_dict().items()})
                row.update(ctx.lock_timing(player, week).to_dict())
            rows.append(row)
    return rows


def _action_stage_prune(
    rows: list[dict[str, Any]], *, per_status_limit: int, min_expected_delta: float | None = None,
    require_classification_plausible: bool = False,
) -> list[dict[str, Any]]:
    """Keep a small, status-balanced frontier for the next MC stage."""
    out: list[dict[str, Any]] = []
    for status in ("FREEAGENT", "WAIVERS"):
        group = [r for r in rows if r.get("fantasy_status") == status]
        group.sort(key=lambda r: float(r.get("stage_expected_delta", -999.0)), reverse=True)
        if require_classification_plausible:
            group = [r for r in group if bool(r.get("stage_classification_plausible", False))]
        if min_expected_delta is not None:
            plausible = [r for r in group if float(r.get("stage_expected_delta", -999.0)) >= float(min_expected_delta)]
            group = plausible
        out.extend(group[:max(1, int(per_status_limit))])
    return out


def _wilson_upper(successes: int, total: int, *, z: float = 3.09) -> float:
    """Conservative one-sided Wilson upper bound for a Bernoulli probability."""
    n = max(int(total), 1)
    x = min(max(int(successes), 0), n)
    phat = x / n
    z2 = float(z) * float(z)
    denom = 1.0 + z2 / n
    centre = phat + z2 / (2.0 * n)
    radius = float(z) * math.sqrt((phat * (1.0 - phat) + z2 / (4.0 * n)) / n)
    return min(max((centre + radius) / denom, 0.0), 1.0)


def _classification_plausibility(
    raw_delta: np.ndarray, adjusted_delta: np.ndarray, cfg: dict[str, Any]
) -> dict[str, float | bool]:
    """Can more football MC plausibly change the counterfactual league-state class?

    fixed6 no longer adds a separate roster-option utility coefficient to the action
    distribution.  ``adjusted_delta`` is itself the paired response of the same
    predictive model after perturbing the league initial state, so it is the proper
    channel for MC escalation.  ``raw_delta`` remains the direct-our-roster response
    diagnostic with the field held fixed.
    """
    raw = np.asarray(raw_delta, dtype=float)
    adjusted = np.asarray(adjusted_delta, dtype=float)
    z = float(cfg.get("action_mc_futility_z", 3.09))
    lean = float(cfg.get("lean_p_better", 0.67))
    raw_upper = _wilson_upper(int(np.sum(raw > 0.0)), len(raw), z=z) if len(raw) else 0.0
    adjusted_upper = _wilson_upper(int(np.sum(adjusted > 0.0)), len(adjusted), z=z) if len(adjusted) else 0.0
    plausible = adjusted_upper >= lean
    return {
        "plausible": bool(plausible),
        "raw_plausible": bool(raw_upper >= lean),
        "league_state_plausible": bool(plausible),
        "raw_p_better_upper": float(raw_upper),
        "combined_p_better_upper": float(adjusted_upper),
        "league_state_p_better_upper": float(adjusted_upper),
    }


def _run_action_mc_stage(
    rows: list[dict[str, Any]],
    ctx: UtilityContext,
    *,
    mc_scenarios: int,
    stage_name: str,
    progress_callback: McProgressCallback | None = None,
    include_diagnostics: bool = False,
) -> tuple[RosterUtilityResult, np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """Evaluate a paired-MC action frontier at one deterministic scenario count."""
    ctx.set_predictive_scenarios(int(mc_scenarios))
    opponent_work = ctx.predictive_opponent_work()
    if opponent_work:
        _emit_mc_progress(
            progress_callback, 0, max(1, opponent_work),
            f"{stage_name} opponent reference queued · {mc_scenarios:,} universes",
        )
        ctx.ensure_predictive_opponent_reference(
            progress_callback=progress_callback,
            progress_label=f"{stage_name} opponent reference",
        )
    baseline, baseline_scenario, baseline_weekly = evaluate_roster_predictive(
        ctx.roster, ctx, progress_callback=progress_callback,
        progress_label=f"{stage_name} HOLD baseline",
        include_diagnostics=include_diagnostics,
    )
    evaluated: list[dict[str, Any]] = []
    for action_ix, src in enumerate(rows, start=1):
        row = dict(src)
        add = row["add"]
        drop = row["drop"]
        add_name = str(add.get("name") or "?")
        drop_name = str(drop.get("name") or "?")

        def action_progress(done: int, total: int, phase: str, *, _ix=action_ix) -> None:
            _emit_mc_progress(
                progress_callback, done, total,
                f"{stage_name} action {_ix}/{len(rows)} · ADD {add_name} / DROP {drop_name} · {phase}",
            )

        utility, direct_scenario_utility, weekly = evaluate_roster_predictive(
            row["new_roster"], ctx, progress_callback=action_progress,
            progress_label=f"{stage_name} action {action_ix}/{len(rows)}",
            include_diagnostics=include_diagnostics,
        )
        # Direct response: change our roster while holding the field fixed.
        raw_delta = np.asarray(direct_scenario_utility) - np.asarray(baseline_scenario)

        # Counterfactual league-state response: the released player does not vanish.
        # Its small-N paired response supplies a first-order perturbation to the same
        # opponent/field reference used by the main predictive H2H calculation.
        league_response = dict(row.get("league_state_response") or {})
        shift = np.asarray(league_response.get("opponent_reference_shift_ppg_by_week") or [0.0] * 17, dtype=float)
        if shift.shape != (17,):
            shift = np.zeros(17, dtype=float)
        counterfactual_opponent = np.asarray(ctx.opponent_predictive, dtype=float) + shift[None, :]
        league_scenario_utility = _scenario_h2h_utility_against(weekly, counterfactual_opponent, ctx)
        adjusted_delta = np.asarray(league_scenario_utility) - np.asarray(baseline_scenario)

        # The fixed4/fixed5 contingent option probe remains diagnostic/screening-only.
        # It no longer contributes an additive term to the authoritative action value.
        option_adj = dict(row.get("contingent_option_adjustment") or {})
        plausibility = _classification_plausibility(raw_delta, adjusted_delta, ctx.cfg)
        p_acquire = float(row.get("p_acquire", 1.0))
        mean = float(np.mean(adjusted_delta))
        utility = replace(
            utility,
            utility=float(np.mean(league_scenario_utility)),
            expected_h2h_win_probability=float(np.mean(league_scenario_utility)),
        )
        row.update({
            "stage_mc": int(ctx.predictive_scenarios),
            "stage_name": str(stage_name),
            "stage_raw_delta": raw_delta,
            "stage_adjusted_delta": adjusted_delta,
            "stage_mean": mean,
            "stage_expected_delta": float(p_acquire * mean),
            "stage_utility": utility,
            "stage_baseline_utility": baseline,
            "stage_weekly": weekly,
            "stage_option_adjustment": option_adj,
            "stage_league_state_response": league_response,
            "stage_classification_plausible": bool(plausibility["plausible"]),
            "stage_raw_p_better_upper": float(plausibility["raw_p_better_upper"]),
            "stage_combined_p_better_upper": float(plausibility["combined_p_better_upper"]),
            "stage_league_state_p_better_upper": float(plausibility.get("league_state_p_better_upper", plausibility.get("combined_p_better_upper", 0.0))),
        })
        history = list(row.get("mc_stage_history") or [])
        history.append({
            "stage": str(stage_name),
            "mc_scenarios": int(ctx.predictive_scenarios),
            "mean_delta_utility": mean,
            "raw_h2h_delta": float(np.mean(raw_delta)),
            "expected_delta_utility": float(p_acquire * mean),
            "raw_p_better": float(np.mean(raw_delta > 0.0)),
            "raw_p_better_upper": float(plausibility["raw_p_better_upper"]),
            "combined_p_better": float(np.mean(adjusted_delta > 0.0)),
            "combined_p_better_upper": float(plausibility["combined_p_better_upper"]),
            "league_state_p_better": float(np.mean(adjusted_delta > 0.0)),
            "league_state_p_better_upper": float(plausibility.get("league_state_p_better_upper", plausibility.get("combined_p_better_upper", 0.0))),
            "raw_classification_plausible": bool(plausibility.get("raw_plausible", plausibility.get("plausible", False))),
            "classification_plausible": bool(plausibility["plausible"]),
        })
        row["mc_stage_history"] = history
        evaluated.append(row)
    return baseline, baseline_scenario, baseline_weekly, evaluated


def evaluate_actions(
    snapshot: dict[str, Any],
    league: dict[str, Any],
    model: dict[str, Any],
    values_path: str | Path = "data/processed/player_values_2026.csv",
    team_name: str | None = None,
    team_id: int | None = None,
    position: str | None = None,
    *,
    predictive_mc_scenarios: int | None = None,
    progress_callback: McProgressCallback | None = None,
) -> dict[str, Any]:
    _emit_mc_progress(progress_callback, 0, 1, "initializing roster-action context")
    team = resolve_team(snapshot, team_name=team_name, team_id=team_id)
    ctx = UtilityContext(snapshot, league, model, values_path, team)
    if predictive_mc_scenarios is not None:
        ctx.set_predictive_scenarios(int(predictive_mc_scenarios))
    _emit_mc_progress(progress_callback, 1, 1, f"context ready · MC={ctx.predictive_scenarios:,}")

    # Fast availability-only utility is retained solely as a broad action screener.
    # The reported baseline and final action deltas come from the stochastic v0.26
    # decision layer on top of the commissioned v0.23 predictive-yield model.
    _emit_mc_progress(progress_callback, 0, 1, "fast HOLD screen baseline")
    screen_baseline = evaluate_roster_utility(ctx.roster, ctx)
    screen_contingent_n = max(32, int(ctx.cfg.get("contingent_roster_screen_scenarios", 64)))
    screen_baseline_option = roster_option_scarcity_value(
        ctx.roster, ctx, scenarios=screen_contingent_n
    )
    _emit_mc_progress(progress_callback, 1, 1, "fast HOLD screen baseline complete")
    if position is not None and str(position).upper() not in PLAYER_POSITIONS:
        raise ValueError(
            "v0.31 player market evaluates QB/RB/WR/TE only; use the defense or kicker channel for specialists"
        )
    candidates = preselect_candidates(ctx.actionable_available, ctx.cfg, position=position)
    drops = [
        p for p in ctx.roster
        if _legal_drop(p) and str(p.get("position") or "").upper() in PLAYER_POSITIONS
    ]

    screened: list[dict[str, Any]] = []
    candidate_total = max(1, len(candidates))
    for candidate_ix, add in enumerate(candidates, start=1):
        add_id = _finite_int(add.get("espn_id"))
        if add_id is None:
            continue
        fantasy_status_raw = str(add.get("fantasy_status") or "").upper()
        fantasy_status = "WAIVERS" if fantasy_status_raw in {"WAIVER", "WAIVERS"} else "FREEAGENT"
        # Broad screening must stay cheap.  The full v0.30 manager-by-manager
        # best-drop waiver model is deferred until a candidate survives this stage.
        p_acquire = 1.0 if fantasy_status == "FREEAGENT" else waiver_screen_acquisition_probability(add, ctx)
        for drop in drops:
            drop_id = _finite_int(drop.get("espn_id"))
            if drop_id is None or drop_id == add_id:
                continue
            if not _legal_roster_after_add_drop(ctx.roster, add, drop, league):
                continue
            new_roster = [p for p in ctx.roster if _finite_int(p.get("espn_id")) != drop_id] + [dict(add)]
            quick = evaluate_roster_utility(new_roster, ctx)
            screen_option_after = roster_option_scarcity_value(
                new_roster, ctx, scenarios=screen_contingent_n
            )
            screen_option_adj = _option_scarcity_utility_adjustment(
                screen_baseline_option, screen_option_after, ctx
            )
            raw_screen_delta = float(quick.utility - screen_baseline.utility)
            option_screen_delta = float(screen_option_adj["delta_total_utility"])
            screen_delta = float(raw_screen_delta + option_screen_delta)
            # The fixed5 asymmetric screen is preserved as a cheap pre-MC guard:
            # contingent *losses* protect valuable drops immediately, while positive
            # diagnostic option value does not buy extra football-MC budget.  fixed6
            # authoritative classification is applied later from the league-state
            # counterfactual, not from this screening coordinate.
            predictive_rank_delta = float(raw_screen_delta + min(option_screen_delta, 0.0))
            screened.append({
                "add": add,
                "drop": drop,
                "new_roster": new_roster,
                "fantasy_status": fantasy_status,
                "p_acquire": float(p_acquire),
                "screen_raw_delta": raw_screen_delta,
                "screen_delta": screen_delta,
                "screen_expected_delta": float(p_acquire * screen_delta),
                "screen_predictive_rank_delta": predictive_rank_delta,
                "screen_predictive_rank_expected_delta": float(p_acquire * predictive_rank_delta),
                "screen_option_delta": option_screen_delta,
                "screen_option_expected_delta": float(p_acquire * option_screen_delta),
                "screen_option_adjustment": screen_option_adj,
                "waiver_blockers": [],
                "screen_p_acquire": float(p_acquire),
                "screen_utility": quick,
            })
        _emit_mc_progress(
            progress_callback, candidate_ix, candidate_total,
            f"broad action screen · {candidate_ix}/{len(candidates)} candidates",
        )

    mc_limit = max(1, int(ctx.cfg.get("predictive_mc_screen_per_status", 36)))
    option_probe_keep = max(0, int(ctx.cfg.get("action_option_screen_keep_per_status", 4)))
    selected: list[dict[str, Any]] = []
    for status in ("FREEAGENT", "WAIVERS"):
        group = [row for row in screened if row["fantasy_status"] == status]
        pred_key = "screen_predictive_rank_delta" if status == "FREEAGENT" else "screen_predictive_rank_expected_delta"
        option_key = "screen_option_delta" if status == "FREEAGENT" else "screen_option_expected_delta"
        group.sort(key=lambda row: float(row[pred_key]), reverse=True)
        predictive_cap = max(0, mc_limit - min(option_probe_keep, mc_limit))
        chosen = list(group[:predictive_cap])
        chosen_keys = {
            (str(r["fantasy_status"]), _finite_int(r["add"].get("espn_id")), _finite_int(r["drop"].get("espn_id")))
            for r in chosen
        }
        option_group = [r for r in group if float(r.get(option_key) or 0.0) > 0.0]
        option_group.sort(key=lambda row: float(row[option_key]), reverse=True)
        for row in option_group:
            key = (str(row["fantasy_status"]), _finite_int(row["add"].get("espn_id")), _finite_int(row["drop"].get("espn_id")))
            if key in chosen_keys:
                continue
            chosen.append(row)
            chosen_keys.add(key)
            if len(chosen) >= mc_limit:
                break
        if len(chosen) < mc_limit:
            for row in group:
                key = (str(row["fantasy_status"]), _finite_int(row["add"].get("espn_id")), _finite_int(row["drop"].get("espn_id")))
                if key in chosen_keys:
                    continue
                chosen.append(row)
                chosen_keys.add(key)
                if len(chosen) >= mc_limit:
                    break
        selected.extend(chosen[:mc_limit])

    # Compute the higher-quality small-N contingent roster-state adjustment exactly
    # once for the selected frontier.  It is independent of the fantasy-score MC N,
    # so re-running it at every 1k/4k/16k predictive stage only wastes time and can
    # create accidental stage-to-stage market-utility drift.
    contingent_n = max(32, int(ctx.cfg.get("contingent_roster_scenarios", 512)))
    contingent_baseline = roster_option_scarcity_value(
        ctx.roster, ctx, scenarios=contingent_n
    )
    for row in selected:
        contingent_after = roster_option_scarcity_value(
            row["new_roster"], ctx, scenarios=contingent_n
        )
        row["contingent_option_adjustment"] = _option_scarcity_utility_adjustment(
            contingent_baseline, contingent_after, ctx
        )

    # fixed6 changes the system boundary from "our roster" to "the league".  The
    # dropped asset is propagated into the waiver state and likely recipient rosters
    # with the same predictive player model at small paired N.  This response depends
    # only on the released player, so calculate it once per unique drop and reuse it
    # across every candidate added for that drop.
    # Missing config is deliberately neutral for backward-compatible synthetic/test
    # contexts; the distributed fixed6 model explicitly enables this at N=256.
    response_n = max(0, int(ctx.cfg.get("league_state_response_scenarios", 0)))
    drop_rows: dict[int, dict[str, Any]] = {}
    for row in selected:
        drop_id = _finite_int(row["drop"].get("espn_id"))
        if drop_id is not None:
            drop_rows.setdefault(int(drop_id), row["drop"])
    release_responses: dict[int, dict[str, Any]] = {}
    response_total = max(1, len(drop_rows))
    if response_n > 0:
        for response_ix, (drop_id, drop_player) in enumerate(drop_rows.items(), start=1):
            _emit_mc_progress(
                progress_callback, response_ix - 1, response_total,
                f"counterfactual league-state response · {response_ix}/{len(drop_rows)} releases · {drop_player.get('name') or drop_id}",
            )
            release_responses[int(drop_id)] = released_player_league_state_response(
                drop_player, ctx, scenarios=response_n
            )
            _emit_mc_progress(
                progress_callback, response_ix, response_total,
                f"counterfactual league-state response · {response_ix}/{len(drop_rows)} releases complete",
            )
    for row in selected:
        drop_id = _finite_int(row["drop"].get("espn_id"))
        row["league_state_response"] = dict(release_responses.get(int(drop_id or -1), {}))

    # v0.31 player channel preserves hierarchical paired MC. Escalation follows the
    # counterfactual league-state response because that response is itself produced
    # by the same football model; the old contingent option probe is diagnostic only.
    # Non-advancing rows are parked at their actual predictive stage for reporting.
    final_mc = int(ctx.predictive_scenarios)
    stage_cfg = ctx.cfg.get("action_mc_stages", [1024, 4096])
    stages = []
    for value in stage_cfg:
        try:
            n = int(value)
        except (TypeError, ValueError):
            continue
        if 8 <= n < final_mc and n not in stages:
            stages.append(n)
    stages = sorted(stages)
    stages.append(final_mc)
    stage_keep = ctx.cfg.get("action_mc_stage_keep_per_status", [8, 4])
    final_keep = max(1, int(ctx.cfg.get("action_mc_final_keep_per_status", 4)))
    final_min_pp = float(ctx.cfg.get("action_mc_final_min_expected_pp", 0.05))
    futility_enabled = bool(ctx.cfg.get("action_mc_futility_enabled", True))

    frontier = list(selected)
    stages_run: list[int] = []
    stopped_for_futility = False
    parked: dict[tuple[str, int, int], dict[str, Any]] = {}

    def row_key(row: dict[str, Any]) -> tuple[str, int, int]:
        return (
            str(row.get("fantasy_status") or ""),
            int(_finite_int(row.get("add", {}).get("espn_id")) or -1),
            int(_finite_int(row.get("drop", {}).get("espn_id")) or -1),
        )

    def park_nonadvancing(
        rows: list[dict[str, Any]], advancing: list[dict[str, Any]], *, include_nonpositive: bool = False
    ) -> None:
        advancing_keys = {row_key(r) for r in advancing}
        for status in ("FREEAGENT", "WAIVERS"):
            group = [
                r for r in rows
                if r.get("fantasy_status") == status
                and row_key(r) not in advancing_keys
                and (include_nonpositive or float(r.get("stage_mean") or 0.0) > 0.0)
            ]
            group.sort(key=lambda r: float(r.get("stage_expected_delta") or -999.0), reverse=True)
            for r in group[:final_keep]:
                r["stage_futility_stop"] = True
                key = row_key(r)
                previous = parked.get(key)
                if previous is None or int(r.get("stage_mc") or 0) >= int(previous.get("stage_mc") or 0):
                    parked[key] = r

    _emit_mc_progress(
        progress_callback, 0, max(1, len(frontier)),
        f"paired action MC queued · hierarchical {' -> '.join(f'{n:,}' for n in stages)} · {len(frontier)} initial actions",
    )
    stage_baseline: RosterUtilityResult | None = None
    stage_baseline_scenario: np.ndarray | None = None
    stage_baseline_weekly: np.ndarray | None = None
    reached_final = False
    for stage_ix, stage_n in enumerate(stages):
        is_final = stage_ix == len(stages) - 1
        stage_name = "FINAL" if is_final else f"SCREEN{stage_ix + 1}"
        _emit_mc_progress(
            progress_callback, 0, max(1, len(frontier)),
            f"hierarchical MC {stage_name} queued · {len(frontier)} actions @ {stage_n:,} universes",
        )
        stage_baseline, stage_baseline_scenario, stage_baseline_weekly, evaluated = _run_action_mc_stage(
            frontier, ctx, mc_scenarios=stage_n, stage_name=stage_name,
            progress_callback=progress_callback, include_diagnostics=is_final,
        )
        stages_run.append(int(stage_n))
        if is_final:
            reached_final = True
            frontier = evaluated
            break
        keep = int(stage_keep[min(stage_ix, len(stage_keep) - 1)]) if stage_keep else 4
        min_delta = None
        if stage_ix == len(stages) - 2:
            min_delta = None if futility_enabled else final_min_pp / 100.0
            keep = final_keep
        next_frontier = _action_stage_prune(
            evaluated,
            per_status_limit=keep,
            min_expected_delta=min_delta,
            require_classification_plausible=futility_enabled,
        )
        # Preserve useful diagnostics at the predictive N where league-state
        # futility was established; only league-state-plausible rows advance.
        if futility_enabled:
            park_nonadvancing(evaluated, next_frontier)
        if futility_enabled and not next_frontier:
            # Preserve a small diagnostic frontier even when every combined mean is
            # non-positive; this keeps audit/show-negative behavior from earlier
            # releases while still avoiding larger predictive stages.
            park_nonadvancing(evaluated, [], include_nonpositive=True)
            stopped_for_futility = True
            frontier = []
            _emit_mc_progress(
                progress_callback, 1, 1,
                f"hierarchical MC stopped after {stage_name} · no league-state-classification-plausible actions",
            )
            break
        frontier = next_frontier

    # Final-stage rows and parked futility rows are both reportable. A final-stage
    # row wins on duplicate key; parked rows retain their true SCREEN1/SCREEN2 N.
    report_rows: dict[tuple[str, int, int], dict[str, Any]] = dict(parked)
    for row in frontier:
        row["stage_futility_stop"] = False
        report_rows[row_key(row)] = row
    report_frontier = list(report_rows.values())

    assert stage_baseline is not None and stage_baseline_scenario is not None and stage_baseline_weekly is not None
    baseline = stage_baseline
    baseline_scenario_utility = stage_baseline_scenario
    baseline_weekly = stage_baseline_weekly

    # SCREEN stages intentionally skip the costly starter-only insurance simulation.
    # Restore display-only diagnostics for any parked SCREEN row from the already
    # computed fast utility, without rerunning predictive MC.
    if not reached_final:
        baseline = replace(
            baseline,
            bench_insurance_ppg=float(screen_baseline.bench_insurance_ppg),
            bye_floor_points=float(screen_baseline.bye_floor_points),
            weighted_bye_loss_points=float(screen_baseline.weighted_bye_loss_points),
        )
    for row in report_frontier:
        if str(row.get("stage_name") or "") == "FINAL":
            continue
        quick = row.get("screen_utility")
        if isinstance(quick, RosterUtilityResult):
            row["stage_utility"] = replace(
                row["stage_utility"],
                bench_insurance_ppg=float(quick.bench_insurance_ppg),
                bye_floor_points=float(quick.bye_floor_points),
                weighted_bye_loss_points=float(quick.weighted_bye_loss_points),
            )
        stage_base = row.get("stage_baseline_utility")
        if isinstance(stage_base, RosterUtilityResult):
            row["stage_baseline_utility"] = replace(
                stage_base,
                bench_insurance_ppg=float(screen_baseline.bench_insurance_ppg),
                bye_floor_points=float(screen_baseline.bye_floor_points),
                weighted_bye_loss_points=float(screen_baseline.weighted_bye_loss_points),
            )

    # Only final-stage waiver candidates pay the expensive manager-by-manager
    # best-add/drop blocker model.  Their final displayed P(acquire) is never the
    # cheap screen probability.
    selected_waiver_adds: dict[int, dict[str, Any]] = {}
    for row in report_frontier:
        if row["fantasy_status"] != "WAIVERS":
            continue
        pid = _finite_int(row["add"].get("espn_id"))
        if pid is not None:
            selected_waiver_adds[pid] = row["add"]
    detailed_waivers: dict[int, tuple[list[dict[str, Any]], float]] = {}
    waiver_total = max(1, len(selected_waiver_adds))
    for waiver_ix, (pid, add) in enumerate(selected_waiver_adds.items(), start=1):
        blockers = waiver_blocker_diagnostics(add, ctx)
        detailed_p = waiver_acquisition_probability(add, ctx, blockers=blockers)
        detailed_waivers[pid] = (blockers, detailed_p)
        _emit_mc_progress(
            progress_callback, waiver_ix, waiver_total,
            f"final waiver manager model · {waiver_ix}/{len(selected_waiver_adds)} candidates",
        )

    results: list[ActionResult] = []
    for row in report_frontier:
        add = row["add"]
        drop = row["drop"]
        raw_delta = np.asarray(row["stage_raw_delta"], dtype=float)
        option_adj = dict(row.get("stage_option_adjustment") or {})
        league_response = dict(row.get("stage_league_state_response") or row.get("league_state_response") or {})
        adjusted_delta = np.asarray(row["stage_adjusted_delta"], dtype=float)

        blockers: list[dict[str, Any]] = []
        p_acquire = float(row.get("p_acquire", 1.0))
        if row["fantasy_status"] == "WAIVERS":
            pid = _finite_int(add.get("espn_id"))
            blockers, p_acquire = detailed_waivers.get(int(pid or -1), ([], p_acquire))

        delta = float(np.mean(adjusted_delta))
        raw_h2h = float(np.mean(raw_delta))
        sd = float(np.std(adjusted_delta, ddof=1)) if len(adjusted_delta) > 1 else 0.0
        add_id_for_seed = _finite_int(add.get("espn_id")) or 0
        drop_id_for_seed = _finite_int(drop.get("espn_id")) or 0
        raw_p16, raw_p84 = _paired_mean_interval(
            raw_delta,
            seed=ctx.seed + 31 * int(add_id_for_seed) + 17 * int(drop_id_for_seed),
            draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)),
        )
        total_p16, total_p84 = _paired_mean_interval(
            adjusted_delta,
            seed=ctx.seed + 31 * int(add_id_for_seed) + 17 * int(drop_id_for_seed),
            draws=int(ctx.cfg.get("paired_mean_interval_resamples", 1000)),
        )
        p_better = float(np.mean(adjusted_delta > 0.0))
        p_worse = float(np.mean(adjusted_delta < 0.0))
        p_tie = float(np.mean(adjusted_delta == 0.0))
        p_raw_better = float(np.mean(raw_delta > 0.0))
        p_raw_worse = float(np.mean(raw_delta < 0.0))
        p_raw_tie = float(np.mean(raw_delta == 0.0))
        classification, raw_classification, combined_classification = _classify_market_action(
            raw_delta, adjusted_delta, ctx.cfg, raw_p16=raw_p16, adjusted_p16=total_p16
        )
        add_state = ctx.yield_state(add, ctx.week)
        candidate_option_support = _market_projection_support(add, ctx)
        utility = row["stage_utility"]
        row_baseline = row.get("stage_baseline_utility")
        if not isinstance(row_baseline, RosterUtilityResult):
            row_baseline = baseline

        add_id = _finite_int(add.get("espn_id"))
        drop_id = _finite_int(drop.get("espn_id"))
        assert add_id is not None and drop_id is not None
        results.append(ActionResult(
            add_espn_id=add_id,
            add_name=str(add.get("name") or add_id),
            add_position=str(add.get("position") or "?"),
            add_team=add.get("nfl_team"),
            fantasy_status=str(row["fantasy_status"]),
            drop_espn_id=drop_id,
            drop_name=str(drop.get("name") or drop_id),
            drop_position=str(drop.get("position") or "?"),
            delta_utility=delta,
            delta_expected_h2h_win_probability=raw_h2h,
            delta_current_week_points=float(utility.current_week_expected_points - row_baseline.current_week_expected_points),
            delta_season_lineup_ppg=float(utility.season_expected_lineup_ppg - row_baseline.season_expected_lineup_ppg),
            delta_bench_insurance_ppg=float(utility.bench_insurance_ppg - row_baseline.bench_insurance_ppg),
            delta_bye_floor_points=float(utility.bye_floor_points - row_baseline.bye_floor_points),
            p_acquire=float(p_acquire),
            expected_delta_utility=float(p_acquire * delta),
            percent_owned=_finite_float(add.get("percent_owned")),
            sleeper_adds_24h=_finite_int(add.get("sleeper_trending_add_24h")),
            candidate_projection_points=float(add.get("projection_points") or 0.0),
            candidate_projection_source=str(add.get("projection_source") or "UNKNOWN"),
            candidate_season_ppg=float(add.get("season_ppg") or 0.0),
            candidate_season_ppg_source=str(add.get("season_ppg_source") or "UNKNOWN"),
            delta_h2h_sd=sd,
            delta_h2h_p16=raw_p16,
            delta_h2h_p84=raw_p84,
            p_utility_better_if_acquired=p_better,
            p_utility_worse_if_acquired=p_worse,
            p_utility_tie_if_acquired=p_tie,
            action_classification=classification,
            raw_action_classification=raw_classification,
            combined_action_classification=combined_classification,
            p_raw_h2h_better_if_acquired=p_raw_better,
            p_raw_h2h_worse_if_acquired=p_raw_worse,
            p_raw_h2h_tie_if_acquired=p_raw_tie,
            delta_total_utility_p16=total_p16,
            delta_total_utility_p84=total_p84,
            candidate_option_support=candidate_option_support,
            mc_scenarios=int(row.get("stage_mc") or ctx.predictive_scenarios),
            screen_delta_utility=float(row["screen_delta"]),
            candidate_operational_mean_ppg=add_state.operational_mean_ppg,
            candidate_model_mean_ppg=add_state.model_mean_ppg,
            candidate_espn_anchor_ppg=add_state.espn_anchor_ppg,
            candidate_espn_anchor_kind=add_state.espn_anchor_kind,
            candidate_delta_model_minus_espn=add_state.delta_model_minus_espn,
            candidate_espn_anchor_z=add_state.espn_anchor_z,
            candidate_pre_matchup_mean_ppg=add_state.pre_matchup_operational_mean_ppg,
            candidate_matchup_model_mean_ppg=add_state.matchup_model_mean_ppg,
            candidate_kinematic_factor=add_state.kinematic_factor_mean,
            candidate_kinematic_source=add_state.kinematic_factor_source,
            candidate_matchup_opponent=add_state.matchup_opponent,
            candidate_matchup_home=add_state.matchup_home,
            candidate_kinematic_sd_ppg=add_state.kinematic_sd_ppg,
            waiver_blockers=list(blockers),
            waiver_response_model="UNCALIBRATED_MANAGER_CLAIM_UTILITY_V030" if str(row["fantasy_status"]) == "WAIVERS" else None,
            delta_h2h_only=raw_h2h,
            delta_future_option_ppg=float(option_adj.get("delta_future_option_ppg", 0.0)),
            delta_replacement_scarcity_ppg=float(option_adj.get("delta_replacement_scarcity_ppg", 0.0)),
            # fixed6 keeps the old option/stress ensemble as a diagnostic only.
            delta_future_option_utility=0.0,
            delta_replacement_scarcity_utility=0.0,
            delta_league_state_utility=delta,
            release_p_claimed=float(league_response.get("p_claimed") or 0.0),
            release_expected_recipient_gain_ppg=float(league_response.get("expected_recipient_gain_ppg") or 0.0),
            release_field_shift_ppg=float(league_response.get("field_shift_ppg") or 0.0),
            release_first_order_field_shift_ppg=float(league_response.get("first_order_field_shift_ppg") or league_response.get("field_shift_ppg") or 0.0),
            release_higher_order_field_shift_ppg=float(league_response.get("higher_order_field_shift_ppg") or 0.0),
            release_current_opponent_shift_ppg=float(league_response.get("current_opponent_shift_ppg") or 0.0),
            release_response_scenarios=int(league_response.get("scenarios") or 0),
            release_higher_order_scenarios=int(league_response.get("higher_order_scenarios") or 0),
            release_response_model=str(league_response.get("model") or "") or None,
            release_first_order_model=str(league_response.get("first_order_model") or "") or None,
            release_cascade_orders=list(league_response.get("cascade_orders") or []),
            release_cascade_stop_reasons=list(league_response.get("cascade_stop_reasons") or []),
            release_top_destinations=list(league_response.get("destinations") or []),
            mc_stage=str(row.get("stage_name") or "FINAL"),
            mc_futility_stop=bool(row.get("stage_futility_stop", False)),
            mc_stage_history=list(row.get("mc_stage_history") or []),
        ))

    rows = [asdict(r) for r in results]
    rows.sort(key=lambda r: (float(r["expected_delta_utility"]), float(r["delta_utility"])), reverse=True)
    free_agents = [r for r in rows if r["fantasy_status"] == "FREEAGENT"]
    waivers = [r for r in rows if r["fantasy_status"] == "WAIVERS"]

    opponent_id = find_week_opponent(snapshot, ctx.team_id)
    opponent_roster = ctx.all_team_rosters.get(int(opponent_id), []) if opponent_id is not None else []
    current_ix = ctx.week - 1
    prediction_snapshot = {
        "schema_version": 1,
        "model_version": "0.23",
        "decision_policy_version": "0.28",
        "current_week_policy": "REALISTIC_LOCK_AWARE_V026",
        "availability_state_model": "OUT_ACTIVE_LIMITED_ACTIVE_FULL_V026",
        "snapshot_utc": snapshot.get("snapshot_utc"),
        "season": ctx.espn.get("season"),
        "week": ctx.week,
        "team_id": ctx.team_id,
        "team_name": ctx.team.get("name"),
        "opponent_team_id": opponent_id,
        "mc_scenarios": ctx.predictive_scenarios,
        "kinematic_model": "NFLVERSE_SHRUNK_ACCEPTANCE_V023",
        "interaction_model": "DATA_MC_INTERACTION_GRID_V028",
        "user_player_week_states": _prediction_rows(ctx.roster, ctx),
        "opponent_player_week_states": _prediction_rows(opponent_roster, ctx),
        "team_week_mc": {
            "current_mean": float(np.mean(baseline_weekly[:, current_ix])),
            "current_sd": float(np.std(baseline_weekly[:, current_ix], ddof=1)) if ctx.predictive_scenarios > 1 else 0.0,
            "current_p10": float(np.quantile(baseline_weekly[:, current_ix], 0.10)),
            "current_p50": float(np.quantile(baseline_weekly[:, current_ix], 0.50)),
            "current_p90": float(np.quantile(baseline_weekly[:, current_ix], 0.90)),
        },
        "notes": [
            "ESPN weekly/season projections are retained as external predicted-yield anchors with explicit provenance.",
            "Operational player means weakly anchor the internal latent model to ESPN where a valid anchor exists; weights are configurable.",
            "Epistemic latent-mean draws are correlated across weeks; game-to-game draws are independent by week.",
            "v0.27 evidence-conditions current-week P(active) and P(full workload | active) while retaining OUT/ACTIVE_LIMITED/ACTIVE_FULL sampling and sequential kickoff locks.",
            "v0.28 applies only chronologically commissioned football-stat Data/MC interaction grids as a higher-order correction; missing/uncommissioned grids are neutral.",
            "The realistic policy observes active/inactive only at the modeled inactive deadline; sampled FULL versus LIMITED workload remains latent to the pregame decision.",
            "v0.23 stores the nflverse-derived opponent acceptance coordinates, K factor, and current-season shrinkage weight for data/MC closure.",
            "Current-week ESPN projections are treated as already evaluated at ESPN's implicit matchup point; our K is applied to the internal model branch before anchoring to avoid double-counting acceptance.",
            "v0.31 player-market actions are restricted to QB/RB/WR/TE. DST and K are managed in separate specialist channels and enter only the complete lineup state.",
            "DST outcomes may still contribute to complete-lineup scoring/opponent references, but they are not player-market assets.",
        ],
    }

    _emit_mc_progress(progress_callback, 1, 1, "roster-actions complete")
    return {
        "schema_version": 12,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_utc": snapshot.get("snapshot_utc"),
        "season": ctx.espn.get("season"),
        "week": ctx.week,
        "team_id": ctx.team_id,
        "team_name": ctx.team.get("name"),
        "waiver_rank": ctx.team.get("waiver_rank"),
        "available_players_total": len(ctx.available),
        "available_players_nfl_eligible": len(ctx.actionable_available),
        "available_players_excluded": len(ctx.excluded_available),
        "official_unknown_status_counts": _official_unknown_status_counts(ctx.excluded_available),
        "excluded_available_examples": [
            {
                "espn_id": _finite_int(p.get("espn_id")),
                "name": p.get("name"),
                "position": p.get("position"),
                "nfl_team": p.get("nfl_team"),
                "official_roster_team": p.get("official_roster_team"),
                "official_roster_status": p.get("official_roster_status"),
                "nflverse_roster_team": p.get("nflverse_roster_team"),
                "nflverse_roster_status": p.get("nflverse_roster_status"),
                "sleeper_team": p.get("sleeper_team"),
                "sleeper_status": p.get("sleeper_status"),
                "reason": p.get("nfl_candidate_eligibility"),
            }
            for p in ctx.excluded_available[:20]
        ],
        "candidate_pool_evaluated": len(candidates),
        "legal_drop_players": len(drops),
        "screen_actions_total": len(screened),
        "predictive_actions_evaluated": len(report_frontier),
        "predictive_actions_final_stage": len(frontier) if reached_final else 0,
        "predictive_actions_futility_parked": len(parked),
        "predictive_actions_initial_frontier": len(selected),
        "predictive_mc_scenarios": int(stages_run[-1] if stages_run else ctx.predictive_scenarios),
        "predictive_mc_stages": stages_run,
        "predictive_mc_requested_stages": stages,
        "predictive_mc_stopped_for_futility": bool(stopped_for_futility),
        "baseline": asdict(baseline),
        "baseline_option_scarcity": contingent_baseline,
        "counterfactual_league_state_model": "PAIRED_COUNTERFACTUAL_PLAYER_CHANNEL_V036_BOUNDED_CASCADE",
        "market_channel": "PLAYER_QB_RB_WR_TE_V031",
        "league_state_response_scenarios": int(response_n),
        "screen_baseline": asdict(screen_baseline),
        "replacement_current": ctx.replacement_current,
        "replacement_season": ctx.replacement_season,
        "free_agent_actions": free_agents,
        "waiver_actions": waivers,
        "prediction_snapshot": prediction_snapshot,
        "notes": [
            "HOLD is the zero-delta baseline.",
            "Final displayed action deltas use paired predictive-yield Monte Carlo with common random numbers; the older availability-only utility is only a broad action screener.",
            "P(utility better) and the paired delta interval are conditional on acquiring the player; waiver acquisition probability is modeled separately.",
            "Waiver acquisition probabilities remain provisional manager-behavior estimates, not observed pending claims.",
            "v0.31 player-channel add/drop actions preserve the fixed6 counterfactual release response while excluding K/DST from the player market.",
            "v0.31 keeps the player-channel counterfactual paired distribution—not an additive option/scarcity coefficient—for action classification and predictive-MC escalation.",
            "The fixed4/fixed5 contingent option/stress ensemble remains available only as a screening and diagnostic response probe; its utility contribution is zero in fixed6.",
            "v0.36 preserves the commissioned first-order released-player response and adds bounded order-2+ player-channel cascade corrections with explicit perturbative stopping and next-week release timing.",
            "v0.30-fixed4 exposes the lazy whole-league opponent-reference build as explicit progress and skips starter-only diagnostics in non-final screening stages.",
            "v0.30-fixed4 uses a small paired future-roster-state ensemble for contingent bench value; replacement scarcity is a diagnostic decomposition and is not double-counted by default.",
            "v0.30-fixed4 uses a cheap waiver acquisition estimate only during pruning; final displayed P(acquire) always uses the detailed v0.30 higher-priority-manager best-add/drop model.",
            "ESPN projections are explicit external yield anchors, not ground truth; model-minus-ESPN residuals are retained for later closure/calibration.",
            "v0.23 separates latent-model, matchup/acceptance, and game-to-game fantasy-yield uncertainty components.",
            "Offensive matchup acceptance is derived from aggressively shrunk nflverse defense observables rather than a defense-vs-position rank multiplier.",
            "DST uses a separate component simulation because ESPN points-allowed and yards-allowed scoring is nonlinear.",
        ],
    }

def save_action_report(report: dict[str, Any], out_dir: str | Path = "data/season_decisions") -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"roster_actions_{stamp}.json"
    suffix = 1
    while path.exists():
        path = out_dir / f"roster_actions_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def save_prediction_report(
    prediction: dict[str, Any], out_dir: str | Path = "data/season_predictions"
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"prediction_{stamp}.json"
    suffix = 1
    while path.exists():
        path = out_dir / f"prediction_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(prediction, indent=2), encoding="utf-8")
    return path
