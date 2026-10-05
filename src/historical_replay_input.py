from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .counterfactual_replay import (
    PROVENANCE_FROZEN,
    PROVENANCE_RECONSTRUCTED,
    RECONSTRUCTED_RETROSPECTIVE_REPLAY,
    DependencyProvenance,
    ReplayContractError,
    classify_replay_mode,
)

WEEK3_REPLAY_INPUT_CONTRACT = "WEEK3_MIXED_PROVENANCE_REPLAY_INPUT_V001"
WEEK3_RECONSTRUCTED_VALUES_SHA256 = (
    "4fd32728f43aab9f10182a942e4147d774c1f45ef3a3021f032dd6a519c7183d"
)

PLAYER_POSITIONS = frozenset({"QB", "RB", "WR", "TE"})
SPECIALIST_POSITIONS = frozenset({"DST", "K"})
EXPECTED_ROSTERED_PLAYER_COUNT = 174
EXPECTED_OWNED_SPECIALIST_COUNT = 24
EXPECTED_MARKET_PLAYER_COUNT = 780
EXPECTED_MARKET_SPECIALIST_COUNT = 66
EXPECTED_ACTIONABLE_SPECIALIST_COUNT = 40

REQUIRED_RECONSTRUCTED_VALUE_FIELDS = (
    "latent_mean_ppg",
    "latent_mean_sd_ppg",
    "predictive_weekly_sd_ppg",
)
_CAPTURE_PREDICTION_FIELDS = (
    "operational_mean_ppg",
    "predictive_sd_ppg",
)
_FORBIDDEN_ARTIFACT_TOKENS = (
    "postgame",
    "outcome",
    "observed_result",
    "final_score",
)


class ReplayInputError(ReplayContractError):
    """Historical replay input cannot satisfy its frozen/reconstructed contract."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value


def _canonical_jsonable(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value):
            return {"__nonfinite_float__": "NaN"}
        if math.isinf(value):
            return {
                "__nonfinite_float__": "+Inf" if value > 0 else "-Inf"
            }
        return value
    if isinstance(value, Mapping):
        return {
            str(k): _canonical_jsonable(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_jsonable(v) for v in value]
    return value


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        _canonical_jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayInputError(f"cannot load JSON artifact {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReplayInputError(f"JSON artifact must be an object: {path}")
    return payload


def _finite_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _finite_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _assert_phase_a_artifact_path(path: Path, *, label: str) -> None:
    folded = path.as_posix().casefold()
    if any(token in folded for token in _FORBIDDEN_ARTIFACT_TOKENS):
        raise ReplayInputError(
            f"{label} path is not Phase-A-safe: {path.as_posix()}"
        )


def _capture_integrity_ok(capture: Mapping[str, Any]) -> bool:
    integrity = capture.get("integrity")
    if not isinstance(integrity, Mapping):
        return False
    expected = str(integrity.get("canonical_payload_sha256") or "").strip().lower()
    if len(expected) != 64:
        return False
    core = dict(capture)
    core.pop("integrity", None)
    return canonical_json_sha256(core) == expected


def _indexed_records(
    rows: Sequence[Any],
    *,
    label: str,
) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ReplayInputError(f"{label} rows must be objects")
        row = dict(raw)
        pid = _finite_int(row.get("espn_id"))
        if pid is None:
            raise ReplayInputError(f"{label} row missing espn_id")
        if pid in out:
            raise ReplayInputError(f"duplicate {label} espn_id: {pid}")
        out[pid] = row
    return out


def _snapshot_rosters(
    snapshot: Mapping[str, Any],
) -> tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]]]:
    espn = snapshot.get("espn", snapshot)
    if not isinstance(espn, Mapping):
        raise ReplayInputError("snapshot ESPN payload must be an object")
    players: dict[int, dict[str, Any]] = {}
    specialists: dict[int, dict[str, Any]] = {}
    for team in espn.get("teams") or []:
        if not isinstance(team, Mapping):
            continue
        for raw in team.get("roster") or []:
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            pid = _finite_int(row.get("espn_id"))
            if pid is None:
                raise ReplayInputError("snapshot roster row missing espn_id")
            pos = str(row.get("position") or "").strip().upper()
            target = (
                players
                if pos in PLAYER_POSITIONS
                else specialists
                if pos in SPECIALIST_POSITIONS
                else None
            )
            if target is None:
                continue
            if pid in target:
                raise ReplayInputError(f"duplicate snapshot roster espn_id: {pid}")
            target[pid] = row
    return players, specialists


def _snapshot_available(
    snapshot: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    espn = snapshot.get("espn", snapshot)
    if not isinstance(espn, Mapping):
        raise ReplayInputError("snapshot ESPN payload must be an object")
    players: list[dict[str, Any]] = []
    specialists: list[dict[str, Any]] = []
    for raw in espn.get("available_players") or []:
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        pos = str(row.get("position") or "").strip().upper()
        if pos in PLAYER_POSITIONS:
            players.append(row)
        elif pos in SPECIALIST_POSITIONS:
            specialists.append(row)
    return players, specialists


def _actionable_available_ids(
    rows: Sequence[dict[str, Any]],
) -> tuple[set[int], dict[str, int]]:
    from .transaction_manager import nfl_candidate_eligibility

    eligible: set[int] = set()
    excluded: dict[str, int] = {}
    for row in rows:
        pid = _finite_int(row.get("espn_id"))
        if pid is None:
            raise ReplayInputError("available-market row missing espn_id")
        allowed, reason = nfl_candidate_eligibility(dict(row))
        if allowed:
            eligible.add(pid)
        else:
            label = str(reason or "UNKNOWN")
            excluded[label] = excluded.get(label, 0) + 1
    return eligible, dict(sorted(excluded.items()))


def _load_values(
    path: Path,
) -> tuple[dict[int, dict[str, str]], tuple[str, ...]]:
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise ReplayInputError(f"cannot open reconstructed values: {path}") from exc
    with handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [
            field
            for field in REQUIRED_RECONSTRUCTED_VALUE_FIELDS
            if field not in fields
        ]
        if missing:
            raise ReplayInputError(
                "reconstructed values missing required fields: "
                + ", ".join(missing)
            )
        out: dict[int, dict[str, str]] = {}
        for raw in reader:
            pid = _finite_int(raw.get("espn_id"))
            if pid is None:
                continue
            if pid in out:
                raise ReplayInputError(
                    f"duplicate reconstructed player-values espn_id: {pid}"
                )
            out[pid] = dict(raw)
    return out, fields


def _validate_capture_prediction_fields(
    rows: Mapping[int, Mapping[str, Any]],
    *,
    label: str,
) -> None:
    for pid, row in rows.items():
        missing = [
            field for field in _CAPTURE_PREDICTION_FIELDS
            if row.get(field) is None
        ]
        if missing:
            raise ReplayInputError(
                f"{label} {pid} missing frozen prediction fields: "
                + ", ".join(missing)
            )


@dataclass(frozen=True)
class Week3ReplayInput:
    contract: str
    season: int
    week: int
    snapshot_utc: str
    captured_utc: str
    replay_mode: str
    dependencies: tuple[DependencyProvenance, ...]
    snapshot: Mapping[str, Any]
    league: Mapping[str, Any]
    model: Mapping[str, Any]
    rostered_player_predictions: Mapping[int, Mapping[str, Any]]
    owned_specialist_predictions: Mapping[int, Mapping[str, Any]]
    actionable_specialist_predictions: Mapping[int, Mapping[str, Any]]
    reconstructed_player_values: Mapping[int, Mapping[str, Any]]
    actionable_player_ids: tuple[int, ...]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract != WEEK3_REPLAY_INPUT_CONTRACT:
            raise ReplayInputError("unsupported Week 3 replay-input contract")
        if (int(self.season), int(self.week)) != (2026, 3):
            raise ReplayInputError("Week3ReplayInput requires season=2026 week=3")
        classification = classify_replay_mode(self.dependencies)
        if classification.replay_mode != self.replay_mode:
            raise ReplayInputError("replay mode does not match dependency provenance")
        if self.replay_mode != RECONSTRUCTED_RETROSPECTIVE_REPLAY:
            raise ReplayInputError(
                "Week 3 replay must remain reconstructed retrospective"
            )

    def summary(self) -> dict[str, Any]:
        classification = classify_replay_mode(self.dependencies)
        return {
            "contract": self.contract,
            "season": int(self.season),
            "week": int(self.week),
            "snapshot_utc": self.snapshot_utc,
            "captured_utc": self.captured_utc,
            "replay_mode": self.replay_mode,
            "reconstructed_dependencies": list(classification.reconstructed),
            "missing_dependencies": list(classification.missing),
            "counts": {
                "rostered_player_predictions": len(self.rostered_player_predictions),
                "owned_specialist_predictions": len(self.owned_specialist_predictions),
                "actionable_specialist_predictions": len(
                    self.actionable_specialist_predictions
                ),
                "actionable_player_ids": len(self.actionable_player_ids),
                "reconstructed_player_values": len(
                    self.reconstructed_player_values
                ),
                "snapshot_projection_fallback_actionable_players": len(
                    self.metadata.get(
                        "snapshot_projection_fallback_actionable_player_ids",
                        (),
                    )
                ),
            },
            "metadata": _thaw(self.metadata),
        }


def build_week3_replay_input(
    *,
    snapshot_path: str | Path,
    capture_path: str | Path,
    league_path: str | Path,
    model_path: str | Path,
    values_path: str | Path,
) -> Week3ReplayInput:
    snapshot_path = Path(snapshot_path)
    capture_path = Path(capture_path)
    league_path = Path(league_path)
    model_path = Path(model_path)
    values_path = Path(values_path)

    for label, path in (
        ("snapshot", snapshot_path),
        ("capture", capture_path),
        ("league config", league_path),
        ("model config", model_path),
        ("reconstructed player values", values_path),
    ):
        if not path.is_file():
            raise ReplayInputError(f"{label} artifact missing: {path}")
        _assert_phase_a_artifact_path(path, label=label)

    snapshot = _load_json_object(snapshot_path)
    capture = _load_json_object(capture_path)
    league = _load_json_object(league_path)
    model = _load_json_object(model_path)

    espn = snapshot.get("espn", snapshot)
    if not isinstance(espn, Mapping):
        raise ReplayInputError("snapshot ESPN payload must be an object")
    season = _finite_int(espn.get("season"))
    week = _finite_int(espn.get("week"))
    if (season, week) != (2026, 3):
        raise ReplayInputError(
            f"historical snapshot is not 2026 Week 3: season={season} week={week}"
        )
    if (_finite_int(capture.get("season")), _finite_int(capture.get("week"))) != (
        2026,
        3,
    ):
        raise ReplayInputError("prospective capture is not 2026 Week 3")
    if not _capture_integrity_ok(capture):
        raise ReplayInputError("prospective capture integrity check failed")

    snapshot_utc = str(
        snapshot.get("snapshot_utc")
        or espn.get("snapshot_utc")
        or ""
    )
    captured_utc = str(capture.get("captured_utc") or "")
    if not snapshot_utc or not captured_utc:
        raise ReplayInputError("snapshot/capture timestamps are required")
    if str(capture.get("snapshot_utc") or "") != snapshot_utc:
        raise ReplayInputError("capture snapshot_utc does not match snapshot")

    behavior = capture.get("behavioral_observation_state")
    if not isinstance(behavior, Mapping):
        raise ReplayInputError(
            "capture behavioral_observation_state is required"
        )
    snapshot_canonical = canonical_json_sha256(snapshot)
    if str(behavior.get("snapshot_sha256") or "") != snapshot_canonical:
        raise ReplayInputError("capture canonical snapshot identity mismatch")
    if str(behavior.get("captured_from_snapshot_utc") or "") != snapshot_utc:
        raise ReplayInputError("behavior state snapshot timestamp mismatch")

    firewall = capture.get("pre_data_firewall")
    if not isinstance(firewall, Mapping):
        raise ReplayInputError("capture pre_data_firewall is required")
    if firewall.get("2026_game_outcomes_used_for_tuning") is not False:
        raise ReplayInputError("capture pre-data firewall is not closed")
    if firewall.get("automatic_refit") is not False:
        raise ReplayInputError("capture automatic_refit must be false")
    if firewall.get("automatic_calibration") is not False:
        raise ReplayInputError("capture automatic_calibration must be false")

    league_canonical = canonical_json_sha256(league)
    model_canonical = canonical_json_sha256(model)
    if str(behavior.get("league_config_sha256") or "") != league_canonical:
        raise ReplayInputError("league config does not match captured identity")
    if str(behavior.get("model_config_sha256") or "") != model_canonical:
        raise ReplayInputError("model config does not match captured identity")

    roster_players, roster_specialists = _snapshot_rosters(snapshot)
    if len(roster_players) != EXPECTED_ROSTERED_PLAYER_COUNT:
        raise ReplayInputError(
            f"Week 3 rostered-player count expected={EXPECTED_ROSTERED_PLAYER_COUNT} "
            f"actual={len(roster_players)}"
        )
    if len(roster_specialists) != EXPECTED_OWNED_SPECIALIST_COUNT:
        raise ReplayInputError(
            f"Week 3 owned-specialist count expected={EXPECTED_OWNED_SPECIALIST_COUNT} "
            f"actual={len(roster_specialists)}"
        )

    player_block = capture.get("league_player_predictions")
    if not isinstance(player_block, Mapping):
        raise ReplayInputError("capture league_player_predictions is required")
    captured_players = _indexed_records(
        player_block.get("records") or [],
        label="rostered player prediction",
    )
    if set(captured_players) != set(roster_players):
        missing = sorted(set(roster_players) - set(captured_players))
        extra = sorted(set(captured_players) - set(roster_players))
        raise ReplayInputError(
            f"frozen rostered-player coverage mismatch missing={missing} extra={extra}"
        )
    _validate_capture_prediction_fields(
        captured_players,
        label="rostered player prediction",
    )

    specialist_block = capture.get("specialist_predictions")
    if not isinstance(specialist_block, Mapping):
        raise ReplayInputError("capture specialist_predictions is required")
    captured_specialists = _indexed_records(
        specialist_block.get("records") or [],
        label="specialist prediction",
    )
    captured_owned = {
        pid: row
        for pid, row in captured_specialists.items()
        if _finite_int(row.get("owner_team_id")) is not None
    }
    captured_market = {
        pid: row
        for pid, row in captured_specialists.items()
        if _finite_int(row.get("owner_team_id")) is None
    }
    if set(captured_owned) != set(roster_specialists):
        raise ReplayInputError("frozen owned-specialist coverage mismatch")
    _validate_capture_prediction_fields(
        captured_owned,
        label="owned specialist prediction",
    )
    _validate_capture_prediction_fields(
        captured_market,
        label="actionable specialist prediction",
    )

    available_players, available_specialists = _snapshot_available(snapshot)
    if len(available_players) != EXPECTED_MARKET_PLAYER_COUNT:
        raise ReplayInputError(
            f"Week 3 broad player-market count expected={EXPECTED_MARKET_PLAYER_COUNT} "
            f"actual={len(available_players)}"
        )
    if len(available_specialists) != EXPECTED_MARKET_SPECIALIST_COUNT:
        raise ReplayInputError(
            f"Week 3 market-specialist count expected={EXPECTED_MARKET_SPECIALIST_COUNT} "
            f"actual={len(available_specialists)}"
        )

    actionable_specialist_ids, specialist_excluded = _actionable_available_ids(
        available_specialists
    )
    if len(actionable_specialist_ids) != EXPECTED_ACTIONABLE_SPECIALIST_COUNT:
        raise ReplayInputError(
            f"Week 3 actionable-specialist count "
            f"expected={EXPECTED_ACTIONABLE_SPECIALIST_COUNT} "
            f"actual={len(actionable_specialist_ids)}"
        )
    if actionable_specialist_ids != set(captured_market):
        missing = sorted(actionable_specialist_ids - set(captured_market))
        extra = sorted(set(captured_market) - actionable_specialist_ids)
        raise ReplayInputError(
            f"captured specialist frontier mismatch missing={missing} extra={extra}"
        )

    behavior_market = [
        dict(row)
        for row in behavior.get("market_players") or []
        if isinstance(row, Mapping)
        and str(row.get("position") or "").strip().upper() in PLAYER_POSITIONS
    ]
    if len(behavior_market) != EXPECTED_MARKET_PLAYER_COUNT:
        raise ReplayInputError(
            "frozen behavioral player-market count does not match Week 3 contract"
        )
    leaked_fields = sorted(
        {
            field
            for row in behavior_market
            for field in REQUIRED_RECONSTRUCTED_VALUE_FIELDS
            if row.get(field) is not None
        }
    )
    if leaked_fields:
        raise ReplayInputError(
            "frozen player market unexpectedly contains reconstructed predictive "
            "fields: " + ", ".join(leaked_fields)
        )

    values_sha = _sha256_file(values_path)
    if values_sha != WEEK3_RECONSTRUCTED_VALUES_SHA256:
        raise ReplayInputError(
            "reconstructed player-values identity mismatch "
            f"expected={WEEK3_RECONSTRUCTED_VALUES_SHA256} actual={values_sha}"
        )
    values, value_fields = _load_values(values_path)

    actionable_player_ids, player_excluded = _actionable_available_ids(
        available_players
    )

    # Mirror the commissioned UtilityContext.enrich_season_values contract exactly:
    # use the reconstructed latent mean only when a positive finite latent_mean_ppg
    # exists; otherwise the evaluator falls back to the frozen ESPN season projection
    # divided by 17, then to the frozen weekly projection. Missing CSV membership is
    # therefore not a missing replay dependency.
    reconstructed_latent_ids: set[int] = set()
    snapshot_projection_fallback_ids: set[int] = set()
    for pid in actionable_player_ids:
        value_row = values.get(pid)
        latent = (
            _finite_float(value_row.get("latent_mean_ppg"))
            if value_row is not None
            else None
        )
        if latent is not None and latent > 0.0:
            reconstructed_latent_ids.add(pid)
        else:
            snapshot_projection_fallback_ids.add(pid)

    snapshot_sha = _sha256_file(snapshot_path)
    capture_sha = _sha256_file(capture_path)
    league_sha = _sha256_file(league_path)
    model_sha = _sha256_file(model_path)

    dependencies = (
        DependencyProvenance(
            key="historical_snapshot_state",
            channel="state_legality",
            status=PROVENANCE_FROZEN,
            artifact=str(snapshot_path),
            sha256=snapshot_sha,
            captured_utc=snapshot_utc,
            note=f"canonical_snapshot_sha256={snapshot_canonical}",
        ),
        DependencyProvenance(
            key="historical_transaction_state",
            channel="transaction_timing",
            status=PROVENANCE_FROZEN,
            artifact=str(snapshot_path),
            sha256=snapshot_sha,
            captured_utc=snapshot_utc,
        ),
        DependencyProvenance(
            key="rostered_player_predictions",
            channel="player_roster_trade",
            status=PROVENANCE_FROZEN,
            artifact=str(capture_path),
            sha256=capture_sha,
            captured_utc=captured_utc,
        ),
        DependencyProvenance(
            key="availability_lock_prediction_state",
            channel="lineup_availability",
            status=PROVENANCE_FROZEN,
            artifact=str(capture_path),
            sha256=capture_sha,
            captured_utc=captured_utc,
        ),
        DependencyProvenance(
            key="owned_specialist_predictions",
            channel="specialist",
            status=PROVENANCE_FROZEN,
            artifact=str(capture_path),
            sha256=capture_sha,
            captured_utc=captured_utc,
        ),
        DependencyProvenance(
            key="specialist_actionable_frontier",
            channel="specialist",
            status=PROVENANCE_FROZEN,
            artifact=str(capture_path),
            sha256=capture_sha,
            captured_utc=captured_utc,
        ),
        DependencyProvenance(
            key="league_config",
            channel="state_legality",
            status=PROVENANCE_FROZEN,
            artifact=str(league_path),
            sha256=league_sha,
            captured_utc=captured_utc,
            note=f"captured_canonical_sha256={league_canonical}",
        ),
        DependencyProvenance(
            key="model_config",
            channel="engine_config",
            status=PROVENANCE_FROZEN,
            artifact=str(model_path),
            sha256=model_sha,
            captured_utc=captured_utc,
            note=f"captured_canonical_sha256={model_canonical}",
        ),
        DependencyProvenance(
            key="player_values_for_available_market",
            channel="player_waiver_free_agent",
            status=PROVENANCE_RECONSTRUCTED,
            artifact=str(values_path),
            sha256=values_sha,
            note=(
                "surviving 2026 player-values identity; exact pre-earliest-Week-3 "
                "decision-time authority is unproven. Commissioned evaluator uses a "
                "positive reconstructed latent mean when available and otherwise "
                "falls back to frozen ESPN season/weekly projection state."
            ),
        ),
    )
    classification = classify_replay_mode(dependencies)
    if classification.replay_mode != RECONSTRUCTED_RETROSPECTIVE_REPLAY:
        raise ReplayInputError("Week 3 provenance classification unexpectedly changed")
    expected_reconstructed = (
        "player_waiver_free_agent:player_values_for_available_market",
    )
    if classification.reconstructed != expected_reconstructed:
        raise ReplayInputError(
            "Week 3 reconstructed dependency set changed: "
            f"{classification.reconstructed}"
        )
    if classification.missing:
        raise ReplayInputError(
            "Week 3 replay input has missing material dependencies: "
            + ", ".join(classification.missing)
        )

    metadata = {
        "snapshot_artifact": str(snapshot_path),
        "snapshot_sha256": snapshot_sha,
        "snapshot_canonical_sha256": snapshot_canonical,
        "capture_artifact": str(capture_path),
        "capture_sha256": capture_sha,
        "league_artifact": str(league_path),
        "league_sha256": league_sha,
        "league_canonical_sha256": league_canonical,
        "model_artifact": str(model_path),
        "model_sha256": model_sha,
        "model_canonical_sha256": model_canonical,
        "values_artifact": str(values_path),
        "values_sha256": values_sha,
        "values_columns": list(value_fields),
        "frozen_market_player_count": len(behavior_market),
        "snapshot_market_specialist_count": len(available_specialists),
        "actionable_specialist_count": len(actionable_specialist_ids),
        "actionable_player_count": len(actionable_player_ids),
        "reconstructed_latent_actionable_player_count": len(
            reconstructed_latent_ids
        ),
        "snapshot_projection_fallback_actionable_player_count": len(
            snapshot_projection_fallback_ids
        ),
        "snapshot_projection_fallback_actionable_player_ids": sorted(
            snapshot_projection_fallback_ids
        ),
        "player_value_source_contract": (
            "POSITIVE_MODEL_LATENT_ELSE_FROZEN_ESPN_SEASON_DIV17_ELSE_"
            "FROZEN_WEEKLY_FALLBACK"
        ),
        "player_eligibility_exclusions": player_excluded,
        "specialist_eligibility_exclusions": specialist_excluded,
        "pre_data_firewall": dict(firewall),
        "outcomes_available_to_adapter": False,
    }

    return Week3ReplayInput(
        contract=WEEK3_REPLAY_INPUT_CONTRACT,
        season=2026,
        week=3,
        snapshot_utc=snapshot_utc,
        captured_utc=captured_utc,
        replay_mode=classification.replay_mode,
        dependencies=dependencies,
        snapshot=_freeze(snapshot),
        league=_freeze(league),
        model=_freeze(model),
        rostered_player_predictions=_freeze(captured_players),
        owned_specialist_predictions=_freeze(captured_owned),
        actionable_specialist_predictions=_freeze(captured_market),
        reconstructed_player_values=_freeze(values),
        actionable_player_ids=tuple(sorted(actionable_player_ids)),
        metadata=_freeze(metadata),
    )
