from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .data_sources.nflverse_matchups import normalize_team


DEFAULT_COMPONENTS: dict[str, dict[str, str]] = {
    "QB": {
        "attempts": "plays_per_game",
        "passing_yards_per_attempt": "pass_epa_per_play",
        "rushing_attempts": "sack_rate",
        "rushing_yards_per_attempt": "rush_epa_per_play",
    },
    "RB": {
        "carries": "rush_epa_per_play",
        "rushing_yards_per_attempt": "rush_epa_per_play",
        "targets": "target_share_rb",
        "catch_rate": "pass_epa_per_play",
        "receiving_yards_per_target": "pass_epa_per_play",
    },
    "WR": {
        "targets": "target_share_wr",
        "catch_rate": "pass_epa_per_play",
        "receiving_yards_per_target": "explosive_pass_rate",
    },
    "TE": {
        "targets": "target_share_te",
        "catch_rate": "pass_epa_per_play",
        "receiving_yards_per_target": "pass_epa_per_play",
    },
}


@dataclass(frozen=True)
class InteractionComponent:
    component: str
    defense_feature: str
    baseline_value: float
    correction: float
    correction_sd: float
    corrected_value: float
    support: float
    defense_z: float
    commissioned: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InteractionCorrection:
    factor: float
    delta_points: float
    uncertainty_ppg: float
    source: str
    artifact_id: str | None
    baseline_source: str
    support: float
    opponent: str | None
    components: dict[str, InteractionComponent]

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["components"] = {k: v.to_dict() for k, v in self.components.items()}
        return out


def _finite(value: Any) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _artifact_path(model: dict[str, Any]) -> Path | None:
    cfg = model.get("interaction_grid") or {}
    raw = str(cfg.get("artifact_path") or "").strip()
    if not raw:
        return None
    return Path(raw)


class InteractionGridStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        manifest_path = self.root / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(manifest_path)
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.artifact_id = str(self.manifest.get("artifact_id") or self.root.name)
        self.validation = {}
        validation_path = self.root / "validation.json"
        if validation_path.exists():
            self.validation = json.loads(validation_path.read_text(encoding="utf-8"))
        self.player_baselines = {}
        player_path = self.root / "player_baselines.json"
        if player_path.exists():
            payload = json.loads(player_path.read_text(encoding="utf-8"))
            self.player_baselines = payload.get("players") or payload
        self.position_baselines = {}
        position_path = self.root / "position_baselines.json"
        if position_path.exists():
            payload = json.loads(position_path.read_text(encoding="utf-8"))
            self.position_baselines = payload.get("positions") or payload
        self._grids: dict[tuple[str, str], dict[str, np.ndarray | str | bool]] = {}

    def player_baseline(self, player: dict[str, Any], position: str) -> tuple[dict[str, float], str]:
        candidates = (
            player.get("nflverse_gsis_id"),
            player.get("gsis_id"),
            player.get("player_id"),
        )
        for candidate in candidates:
            key = str(candidate or "").strip()
            if key and key in self.player_baselines:
                row = self.player_baselines[key]
                return {
                    str(k): float(v)
                    for k, v in row.items()
                    if k not in {"position", "games", "name"} and _finite(v) is not None
                }, "PLAYER_HISTORY"
        row = self.position_baselines.get(position) or {}
        return {
            str(k): float(v)
            for k, v in row.items()
            if k not in {"position", "games"} and _finite(v) is not None
        }, "POSITION_FALLBACK"

    def grid(self, position: str, component: str) -> dict[str, Any] | None:
        key = (position, component)
        if key in self._grids:
            return self._grids[key]
        path = self.root / position / f"{component}.npz"
        if not path.exists():
            return None
        with np.load(path, allow_pickle=False) as npz:
            grid = {name: np.asarray(npz[name]) for name in npz.files}
        meta_path = self.root / position / f"{component}.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        grid["defense_feature"] = str(meta.get("defense_feature") or "")
        grid["commissioned"] = bool(meta.get("commissioned", True))
        grid["validation"] = meta.get("validation") or {}
        self._grids[key] = grid
        return grid


@lru_cache(maxsize=8)
def _load_store_cached(path_text: str, manifest_mtime_ns: int) -> InteractionGridStore:
    del manifest_mtime_ns
    return InteractionGridStore(path_text)


def load_interaction_store(model: dict[str, Any]) -> InteractionGridStore | None:
    path = _artifact_path(model)
    if path is None:
        return None
    manifest = path / "manifest.json"
    if not manifest.exists():
        return None
    return _load_store_cached(str(path.resolve()), manifest.stat().st_mtime_ns)


def _interp_axis(values: np.ndarray, x: float) -> tuple[int, int, float]:
    values = np.asarray(values, dtype=float)
    if len(values) <= 1:
        return 0, 0, 0.0
    if x <= values[0]:
        return 0, 0, 0.0
    if x >= values[-1]:
        idx = len(values) - 1
        return idx, idx, 0.0
    hi = int(np.searchsorted(values, x, side="right"))
    lo = hi - 1
    denom = float(values[hi] - values[lo])
    t = 0.0 if abs(denom) < 1e-12 else float((x - values[lo]) / denom)
    return lo, hi, min(max(t, 0.0), 1.0)


def _bilinear(surface: np.ndarray, x_centers: np.ndarray, z_centers: np.ndarray, x: float, z: float) -> float:
    arr = np.asarray(surface, dtype=float)
    ix0, ix1, tx = _interp_axis(np.asarray(x_centers, dtype=float), float(x))
    iz0, iz1, tz = _interp_axis(np.asarray(z_centers, dtype=float), float(z))
    q00 = float(arr[ix0, iz0])
    q10 = float(arr[ix1, iz0])
    q01 = float(arr[ix0, iz1])
    q11 = float(arr[ix1, iz1])
    a = q00 * (1.0 - tx) + q10 * tx
    b = q01 * (1.0 - tx) + q11 * tx
    return float(a * (1.0 - tz) + b * tz)


def interpolate_grid(grid: dict[str, Any], baseline: float, defense_z: float) -> tuple[float, float, float]:
    x_centers = np.asarray(grid["baseline_centers"], dtype=float)
    z_centers = np.asarray(grid["defense_z_centers"], dtype=float)
    correction = _bilinear(np.asarray(grid["correction"], dtype=float), x_centers, z_centers, baseline, defense_z)
    uncertainty = _bilinear(np.asarray(grid["uncertainty"], dtype=float), x_centers, z_centers, baseline, defense_z)
    support = _bilinear(np.asarray(grid["support"], dtype=float), x_centers, z_centers, baseline, defense_z)
    return float(correction), max(float(uncertainty), 0.0), max(float(support), 0.0)


def _partial_points(position: str, values: dict[str, float], league: dict[str, Any] | None) -> float:
    scoring = (league or {}).get("scoring") or {}
    pass_yard = float((scoring.get("passing") or {}).get("yards", 0.04))
    rush_yard = float((scoring.get("rushing") or {}).get("yards", 0.10))
    rec_yard = float((scoring.get("receiving") or {}).get("yards", 0.10))
    reception = float((scoring.get("receiving") or {}).get("reception", 1.0))

    if position == "QB":
        attempts = max(float(values.get("attempts", 0.0)), 0.0)
        ypa = max(float(values.get("passing_yards_per_attempt", 0.0)), 0.0)
        rushes = max(float(values.get("rushing_attempts", 0.0)), 0.0)
        rypa = max(float(values.get("rushing_yards_per_attempt", 0.0)), 0.0)
        return pass_yard * attempts * ypa + rush_yard * rushes * rypa

    carries = max(float(values.get("carries", 0.0)), 0.0)
    rypa = max(float(values.get("rushing_yards_per_attempt", 0.0)), 0.0)
    targets = max(float(values.get("targets", 0.0)), 0.0)
    catch_rate = min(max(float(values.get("catch_rate", 0.0)), 0.0), 1.0)
    rypt = max(float(values.get("receiving_yards_per_target", 0.0)), 0.0)
    return rush_yard * carries * rypa + reception * targets * catch_rate + rec_yard * targets * rypt


def evaluate_interaction_correction(
    player: dict[str, Any],
    *,
    week: int,
    matchup_context: dict[str, Any] | None,
    model: dict[str, Any],
    league: dict[str, Any] | None,
    reference_points: float,
) -> InteractionCorrection:
    cfg = model.get("interaction_grid") or {}
    position = str(player.get("position") or "").upper()
    if not bool(cfg.get("enabled", False)) or position not in DEFAULT_COMPONENTS:
        return InteractionCorrection(1.0, 0.0, 0.0, "INTERACTION_DISABLED", None, "NONE", 0.0, None, {})
    store = load_interaction_store(model)
    if store is None:
        return InteractionCorrection(1.0, 0.0, 0.0, "INTERACTION_GRID_MISSING", None, "NONE", 0.0, None, {})
    team = normalize_team(player.get("nfl_team"))
    game = ((matchup_context or {}).get("team_week") or {}).get(team or "", {}).get(str(int(week)))
    opponent = normalize_team((game or {}).get("opponent"))
    if not opponent:
        return InteractionCorrection(1.0, 0.0, 0.0, "INTERACTION_NO_OPPONENT", store.artifact_id, "NONE", 0.0, None, {})
    defense_z = ((matchup_context or {}).get("defense_zscores") or {}).get(opponent, {})
    if not defense_z:
        return InteractionCorrection(1.0, 0.0, 0.0, "INTERACTION_NO_DEFENSE_STATE", store.artifact_id, "NONE", 0.0, opponent, {})

    baseline, baseline_source = store.player_baseline(player, position)
    components: dict[str, InteractionComponent] = {}
    corrected_values = dict(baseline)
    support_values: list[float] = []
    for component, default_feature in DEFAULT_COMPONENTS[position].items():
        value = _finite(baseline.get(component))
        if value is None:
            continue
        grid = store.grid(position, component)
        if not grid:
            continue
        feature = str(grid.get("defense_feature") or default_feature)
        z = _finite(defense_z.get(feature))
        if z is None:
            continue
        correction, correction_sd, support = interpolate_grid(grid, value, z)
        commissioned = bool(grid.get("commissioned", True))
        if not commissioned:
            if bool(cfg.get("commissioned_only", True)):
                # v0.28-fixed4: shadow grids remain diagnostic-only. They must not
                # perturb either the operational mean or the operational variance.
                # The raw grid artifact still retains its fitted correction and
                # uncertainty for offline validation/inspection.
                correction = 1.0
                correction_sd = 0.0
            else:
                # Explicit exploratory mode may apply an uncommissioned surface; in
                # that non-default case retain a conservative uncertainty floor.
                correction_sd = max(correction_sd, float(cfg.get("uncommissioned_uncertainty_floor", 0.05)))
        correction = min(max(correction, float(cfg.get("correction_min", 0.75))), float(cfg.get("correction_max", 1.25)))
        corrected = float(value * correction)
        corrected_values[component] = corrected
        support_values.append(support)
        components[component] = InteractionComponent(
            component=component,
            defense_feature=feature,
            baseline_value=float(value),
            correction=float(correction),
            correction_sd=float(correction_sd),
            corrected_value=corrected,
            support=float(support),
            defense_z=float(z),
            commissioned=commissioned,
        )

    if not components:
        return InteractionCorrection(1.0, 0.0, 0.0, "INTERACTION_NO_COMPONENTS", store.artifact_id, baseline_source, 0.0, opponent, {})

    base_partial = _partial_points(position, baseline, league)
    corrected_partial = _partial_points(position, corrected_values, league)
    delta_points = float(corrected_partial - base_partial)

    # Propagate finite-grid uncertainty through the downstream fantasy response with
    # a local one-component-at-a-time finite difference. The grids were trained on
    # football observables only; scoring enters here solely as the detector response.
    variance = 0.0
    for name, comp in components.items():
        if comp.correction_sd <= 0 or abs(comp.baseline_value) <= 1e-12:
            continue
        shifted = dict(corrected_values)
        shifted[name] = comp.baseline_value * (comp.correction + comp.correction_sd)
        dp = _partial_points(position, shifted, league) - corrected_partial
        variance += float(dp * dp)
    uncertainty = math.sqrt(max(variance, 0.0))

    max_abs_delta = float(cfg.get("max_absolute_delta_ppg", 4.0))
    if max_abs_delta > 0:
        delta_points = min(max(delta_points, -max_abs_delta), max_abs_delta)
    factor = (reference_points + delta_points) / reference_points if reference_points > 1e-9 else 1.0
    factor = min(max(factor, float(cfg.get("yield_factor_min", 0.90))), float(cfg.get("yield_factor_max", 1.10)))
    # Keep delta and factor internally consistent if the outer factor bound clips.
    delta_points = float(reference_points * (factor - 1.0)) if reference_points > 1e-9 else 0.0
    support = float(min(support_values)) if support_values else 0.0
    return InteractionCorrection(
        factor=float(factor),
        delta_points=delta_points,
        uncertainty_ppg=float(uncertainty),
        source="DATA_MC_INTERACTION_GRID_V028",
        artifact_id=store.artifact_id,
        baseline_source=baseline_source,
        support=support,
        opponent=opponent,
        components=components,
    )
