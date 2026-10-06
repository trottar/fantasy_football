from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from .counterfactual_replay import (
    PROVENANCE_FROZEN,
    DependencyProvenance,
    PhaseACandidate,
    PhaseAReceipt,
    freeze_phase_a_receipt,
)
from .historical_replay_input import Week3ReplayInput, build_week3_replay_input


WEEK3_PHASE_A_EVALUATOR_CONTRACT = "WEEK3_HISTORICAL_PHASE_A_EVALUATOR_V001"

LINEUP = "lineup_availability"
PLAYER = "player_waiver_free_agent"
DST = "dst_waiver_free_agent"
KICKER = "kicker_waiver_free_agent"
IR = "ir_reserve_open_slot_injury_replacement"
TRADE_1X1 = "trade_one_for_one_player"
TRADE_MULTI = "trade_multi_player_unequal"
TRADE_SPECIALIST = "trade_specialist_inclusive"

ACTION_FAMILY_ORDER = (
    LINEUP,
    PLAYER,
    DST,
    KICKER,
    IR,
    TRADE_1X1,
    TRADE_MULTI,
    TRADE_SPECIALIST,
)

_PLAYER_FIELDS = (
    "add_espn_id", "add_name", "add_position", "add_team",
    "drop_espn_id", "drop_name", "drop_position",
    "fantasy_status", "p_acquire",
    "delta_utility", "expected_delta_utility",
    "delta_current_week_points", "delta_season_lineup_ppg",
    "delta_expected_h2h_win_probability",
    "delta_future_option_utility", "delta_replacement_scarcity_utility",
    "delta_league_state_utility",
    "action_classification", "raw_action_classification",
    "combined_action_classification",
    "mc_scenarios", "mc_stage", "mc_futility_stop",
)
_SPECIALIST_FIELDS = (
    "action", "position", "add_espn_id", "add_name", "add_team",
    "drop_espn_id", "drop_name", "fantasy_status", "p_acquire",
    "legal", "reason", "classification",
    "expected_complete_state_delta_mean",
    "activation_week", "effective_activation_week", "current_activation",
    "acquisition_state",
)
_TRADE_FIELDS = (
    "partner_team_id", "partner_name", "package_family",
    "specialist_channels",
    "give_id", "give_ids", "give_name", "give_names",
    "give_position", "give_positions",
    "receive_id", "receive_ids", "receive_name", "receive_names",
    "receive_position", "receive_positions",
    "classification", "our_delta_season_ppg", "our_p_better",
    "our_delta_complete_state_utility",
    "partner_delta_season_ppg", "partner_p_better",
    "partner_delta_complete_state_utility",
    "p_accept", "p_counter", "p_reject", "expected_offer_value",
    "user_auto_drop_ids", "partner_auto_drop_ids",
    "user_auto_add_ids", "partner_auto_add_ids",
    "mc_scenarios",
)


class Week3PhaseAEvaluationError(RuntimeError):
    """Week 3 Phase-A evaluation cannot satisfy the replay contract."""


@dataclass(frozen=True)
class Week3PhaseAEvaluation:
    contract: str
    receipt: PhaseAReceipt
    coverage: Mapping[str, Any]
    channel_selections: tuple[Mapping[str, Any], ...]
    metadata: Mapping[str, Any]

    def verify(self) -> None:
        if self.contract != WEEK3_PHASE_A_EVALUATOR_CONTRACT:
            raise Week3PhaseAEvaluationError("unsupported Phase-A evaluator contract")
        self.receipt.verify()
        covered = tuple(self.coverage.get("required_action_families") or ())
        if covered != ACTION_FAMILY_ORDER:
            raise Week3PhaseAEvaluationError(
                f"Phase-A family coverage mismatch: {covered}"
            )
        if self.coverage.get("coverage_complete") is not True:
            raise Week3PhaseAEvaluationError("Phase-A coverage is not complete")


def _deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _deep_thaw(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_deep_thaw(nested) for nested in value]
    if isinstance(value, list):
        return [_deep_thaw(nested) for nested in value]
    return value


def _finite_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _finite_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise Week3PhaseAEvaluationError(f"JSON object required: {p}")
    return obj


def _normalized_transaction_settings(raw_payload: Mapping[str, Any]) -> dict[str, Any]:
    settings = raw_payload.get("settings") or {}
    if not isinstance(settings, Mapping):
        raise Week3PhaseAEvaluationError("raw ESPN settings block is missing")
    trade = settings.get("tradeSettings") or {}
    roster = settings.get("rosterSettings") or {}
    acquisition = settings.get("acquisitionSettings") or {}
    if not all(isinstance(row, Mapping) for row in (trade, roster, acquisition)):
        raise Week3PhaseAEvaluationError("raw ESPN transaction settings are malformed")

    def integer(value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    out = {
        "trade_review_hours": integer(trade.get("revisionHours")),
        "trade_veto_votes_required": integer(trade.get("vetoVotesRequired")),
        "trade_deadline_date": integer(trade.get("deadlineDate")),
        "trade_max": integer(trade.get("max")),
        "lineup_locktime_type": roster.get("lineupLocktimeType"),
        "roster_locktime_type": roster.get("rosterLocktimeType"),
        "transaction_locking_enabled": acquisition.get(
            "transactionLockingEnabled"
        ),
    }
    review = out["trade_review_hours"]
    if review is None or int(review) < 0:
        raise Week3PhaseAEvaluationError(
            "frozen raw ESPN trade_review_hours is missing or invalid"
        )
    if not str(out["lineup_locktime_type"] or "").strip():
        raise Week3PhaseAEvaluationError(
            "frozen raw ESPN lineup_locktime_type is missing"
        )
    if not str(out["roster_locktime_type"] or "").strip():
        raise Week3PhaseAEvaluationError(
            "frozen raw ESPN roster_locktime_type is missing"
        )
    return out


def _bind_frozen_transaction_settings(
    snapshot: dict[str, Any],
    snapshot_path: str | Path,
    snapshot_utc: str,
) -> DependencyProvenance:
    raw_path = Path(snapshot_path).parent / "espn" / "espn_league_raw.json"
    if not raw_path.is_file():
        raise Week3PhaseAEvaluationError(
            f"frozen raw ESPN league payload missing: {raw_path}"
        )
    raw = _load_json(raw_path)
    settings = _normalized_transaction_settings(raw)
    espn = snapshot.get("espn", snapshot)
    if not isinstance(espn, dict):
        raise Week3PhaseAEvaluationError("mutable ESPN snapshot block is missing")
    espn["transaction_settings"] = dict(settings)
    return DependencyProvenance(
        key="raw_espn_transaction_settings",
        channel="transaction_timing",
        status=PROVENANCE_FROZEN,
        artifact=str(raw_path),
        sha256=_sha256_file(raw_path),
        captured_utc=str(snapshot_utc),
        note=(
            "normalized from decision-time raw ESPN mSettings stored beside the "
            "historical snapshot; no current ESPN read"
        ),
    )


def _record_maps(
    state: Week3ReplayInput,
) -> tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]]]:
    players = {
        int(pid): _deep_thaw(row)
        for pid, row in state.rostered_player_predictions.items()
    }
    specialists = {
        int(pid): _deep_thaw(row)
        for source in (
            state.owned_specialist_predictions,
            state.actionable_specialist_predictions,
        )
        for pid, row in source.items()
    }
    return players, specialists


def _captured_base_mean(record: Mapping[str, Any]) -> float:
    """Return the frozen base coordinate without inventing a positivity contract.

    Week3ReplayInput requires the frozen operational prediction to be present, not
    positive. A legitimate captured zero must remain zero rather than being replaced
    by a later reconstructed/player-value surface.
    """
    for key in (
        "model_mean_ppg",
        "pre_matchup_mean_ppg",
        "pre_matchup_operational_mean_ppg",
        "operational_mean_ppg",
    ):
        value = _finite_float(record.get(key))
        if value is not None and value >= 0.0:
            return float(value)
    raise Week3PhaseAEvaluationError(
        f"frozen capture record missing nonnegative model/base mean: "
        f"{record.get('espn_id')}"
    )


def _captured_model_sd(record: Mapping[str, Any]) -> float:
    value = _finite_float(record.get("model_sd_ppg"))
    if value is None or value < 0.0:
        raise Week3PhaseAEvaluationError(
            f"frozen capture record missing model_sd_ppg: {record.get('espn_id')}"
        )
    return float(value)


def _captured_predictive_sd(record: Mapping[str, Any]) -> float:
    value = _finite_float(record.get("predictive_sd_ppg"))
    if value is None or value < 0.0:
        raise Week3PhaseAEvaluationError(
            f"frozen capture record missing nonnegative predictive_sd_ppg: "
            f"{record.get('espn_id')}"
        )
    return float(value)


def _overlay_enriched_row(
    player: dict[str, Any],
    record: Mapping[str, Any],
) -> None:
    base_mean = _captured_base_mean(record)
    model_sd = _captured_model_sd(record)
    predictive_sd = _captured_predictive_sd(record)
    operational = _finite_float(record.get("operational_mean_ppg"))
    if operational is None:
        raise Week3PhaseAEvaluationError(
            f"frozen capture record missing operational_mean_ppg: "
            f"{record.get('espn_id')}"
        )

    player["latent_mean_ppg"] = base_mean
    player["season_ppg"] = base_mean
    player["season_ppg_source"] = "FROZEN_CAPTURE_MODEL_MEAN"
    player["latent_mean_sd_ppg"] = model_sd
    player["predictive_weekly_sd_ppg"] = predictive_sd
    player["projection_points"] = float(operational)
    player["projection_source"] = "FROZEN_CAPTURE_OPERATIONAL_MEAN"

    p_active = _finite_float(record.get("p_active"))
    if p_active is not None:
        player["active_probability"] = min(max(p_active, 0.0), 1.0)
    workload = _finite_float(record.get("expected_workload_factor"))
    if workload is not None:
        player["expected_workload_given_active"] = min(
            max(workload, 0.0), 1.0
        )


def _frozen_yield_state(
    player: Mapping[str, Any],
    record: Mapping[str, Any],
    week: int,
):
    from .weekly_yield import WeeklyYieldState

    pid = _finite_int(record.get("espn_id"))
    operational = _finite_float(record.get("operational_mean_ppg"))
    predictive_sd = _captured_predictive_sd(record)
    model_sd = _captured_model_sd(record)
    game_sd = _finite_float(record.get("game_sd_ppg")) or 0.0
    kinematic_sd = _finite_float(record.get("kinematic_sd_ppg")) or 0.0
    interaction_sd = _finite_float(record.get("interaction_sd_ppg"))
    if interaction_sd is None:
        remaining = (
            predictive_sd * predictive_sd
            - model_sd * model_sd
            - game_sd * game_sd
            - kinematic_sd * kinematic_sd
        )
        interaction_sd = math.sqrt(max(remaining, 0.0))
    if operational is None:
        raise Week3PhaseAEvaluationError(
            f"frozen capture record missing operational mean: {pid}"
        )

    pre_matchup = _finite_float(
        record.get("pre_matchup_mean_ppg")
        if record.get("pre_matchup_mean_ppg") is not None
        else record.get("pre_matchup_operational_mean_ppg")
    )
    if pre_matchup is None:
        pre_matchup = float(operational)

    model_mean = _finite_float(record.get("model_mean_ppg"))
    matchup_model_mean = _finite_float(record.get("matchup_model_mean_ppg"))
    anchor = _finite_float(record.get("espn_anchor_ppg"))
    kinematic_factor = _finite_float(record.get("kinematic_factor"))
    interaction_factor = _finite_float(record.get("interaction_factor"))
    interaction_delta = _finite_float(record.get("interaction_delta_ppg"))
    p_active = _finite_float(record.get("p_active"))
    if p_active is None:
        p_active = 1.0

    component_predictions = record.get("component_predictions")
    dst_components = (
        dict(component_predictions)
        if isinstance(component_predictions, Mapping)
        and str(record.get("position") or player.get("position") or "").upper()
        == "DST"
        else None
    )

    return WeeklyYieldState(
        espn_id=pid,
        name=str(record.get("name") or player.get("name") or pid or "?"),
        position=str(
            record.get("position") or player.get("position") or ""
        ).upper(),
        nfl_team=record.get("nfl_team") or player.get("nfl_team"),
        week=int(week),
        operational_mean_ppg=float(operational),
        pre_matchup_operational_mean_ppg=float(pre_matchup),
        model_mean_ppg=model_mean,
        matchup_model_mean_ppg=matchup_model_mean,
        espn_anchor_ppg=anchor,
        espn_anchor_kind=record.get("espn_anchor_kind"),
        espn_anchor_weight=0.0,
        espn_anchor_acceptance_specific=False,
        delta_model_minus_espn=(
            model_mean - anchor
            if model_mean is not None and anchor is not None
            else None
        ),
        ratio_model_to_espn=(
            model_mean / anchor
            if model_mean is not None and anchor not in (None, 0.0)
            else None
        ),
        anchor_pull_ppg=0.0,
        game_sd_ppg=float(game_sd),
        model_sd_ppg=float(model_sd),
        kinematic_sd_ppg=float(kinematic_sd),
        interaction_sd_ppg=float(interaction_sd),
        predictive_sd_ppg=float(predictive_sd),
        espn_anchor_sigma_ppg=None,
        espn_anchor_z=None,
        availability_probability=min(max(float(p_active), 0.0), 1.0),
        kinematic_factor_mean=float(kinematic_factor or 1.0),
        kinematic_factor_source=str(
            record.get("kinematic_source") or "FROZEN_CAPTURE"
        ),
        interaction_factor_mean=float(interaction_factor or 1.0),
        interaction_factor_source="FROZEN_CAPTURE",
        interaction_delta_ppg=float(interaction_delta or 0.0),
        interaction_artifact_id=record.get("interaction_artifact_id"),
        interaction_baseline_source="FROZEN_CAPTURE",
        interaction_support=0.0,
        interaction_components={},
        matchup_opponent=record.get("matchup_opponent"),
        matchup_home=record.get("matchup_home"),
        matchup_team_implied_points=_finite_float(
            record.get("team_implied_points")
        ),
        matchup_defense_current_weight=0.0,
        kinematic_components={},
        kinematic_zscores={},
        dst_component_expectation=dst_components,
        projection_source="FROZEN_WEEK3_CAPTURE",
    )


def _frozen_availability_state(record: Mapping[str, Any]):
    from .availability_timing import AvailabilityStateModel

    p_active = _finite_float(record.get("p_active"))
    p_full_given_active = _finite_float(record.get("p_full_given_active"))
    p_out = _finite_float(record.get("p_out"))
    p_limited = _finite_float(record.get("p_limited"))
    p_full = _finite_float(record.get("p_full"))
    limited = _finite_float(record.get("limited_workload_fraction"))
    if any(
        value is None
        for value in (
            p_active,
            p_full_given_active,
            p_out,
            p_limited,
            p_full,
            limited,
        )
    ):
        return None

    sequence = record.get("practice_sequence") or ()
    return AvailabilityStateModel(
        status=str(record.get("availability_status") or "ACTIVE"),
        status_source=str(
            record.get("availability_status_source") or "FROZEN_CAPTURE"
        ),
        p_active=float(p_active),
        p_full_given_active=float(p_full_given_active),
        p_out=float(p_out),
        p_limited=float(p_limited),
        p_full=float(p_full),
        limited_workload_fraction=float(limited),
        base_p_active=float(p_active),
        base_p_full_given_active=float(p_full_given_active),
        evidence_level=str(
            record.get("availability_evidence_level") or "FROZEN_CAPTURE"
        ),
        posterior_method=str(
            record.get("availability_posterior_method") or "FROZEN_CAPTURE"
        ),
        calibration_status=str(
            record.get("availability_calibration_status") or "FROZEN_CAPTURE"
        ),
        practice_source=record.get("practice_source"),
        practice_sequence=tuple(str(item) for item in sequence),
        hours_to_kickoff=None,
        evidence=(),
    )


def _parse_aware_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        out = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if out.tzinfo is None:
        return None
    return out


def _frozen_lock_timing(record: Mapping[str, Any]):
    from .availability_timing import LockTiming

    kickoff = _parse_aware_datetime(record.get("kickoff_utc"))
    reveal = _parse_aware_datetime(
        record.get("reveal_utc")
        if record.get("reveal_utc") is not None
        else record.get("inactive_reveal_utc")
    )
    lock_group = str(record.get("lock_group") or "")
    source = str(
        record.get("source")
        if record.get("source") is not None
        else record.get("lock_source")
        or "FROZEN_CAPTURE"
    )
    if kickoff is None and not lock_group:
        return None
    return LockTiming(
        kickoff=kickoff,
        reveal_time=reveal,
        lock_group=lock_group or "FROZEN_CAPTURE",
        source=source,
    )


@contextmanager
def frozen_week3_authority_overlay(
    state: Week3ReplayInput,
) -> Iterator[dict[str, Any]]:
    """Inject frozen current-week capture states into unchanged production authority.

    The context patches only shared UtilityContext hooks plus its enrichment helper.
    Every patch is restored in ``finally``. Uncaptured QB/RB/WR/TE market players
    continue through the reconstructed values layer validated by Week3ReplayInput.
    """
    from . import transaction_manager as tm

    player_records, specialist_records = _record_maps(state)
    frozen_records = {**specialist_records, **player_records}

    original_enrich = tm.enrich_season_values
    original_yield = tm.UtilityContext.yield_state
    original_availability = tm.UtilityContext.availability_state
    original_lock = tm.UtilityContext.lock_timing

    def replay_enrich(
        players,
        values_path,
        league,
        week,
        value_index=None,
    ):
        out = original_enrich(
            players,
            values_path,
            league,
            week,
            value_index,
        )
        for player in out:
            pid = _finite_int(player.get("espn_id"))
            record = frozen_records.get(pid) if pid is not None else None
            if record is not None:
                _overlay_enriched_row(player, record)
        return out

    def replay_yield(self, player, week):
        pid = _finite_int(player.get("espn_id"))
        record = frozen_records.get(pid) if pid is not None else None
        if record is not None and int(week) == int(self.week):
            key = (pid, int(week))
            cached = self._yield_state_cache.get(key)
            if cached is None:
                cached = _frozen_yield_state(player, record, int(week))
                self._yield_state_cache[key] = cached
            return cached
        return original_yield(self, player, week)

    def replay_availability(self, player, week):
        pid = _finite_int(player.get("espn_id"))
        record = player_records.get(pid) if pid is not None else None
        if record is not None and int(week) == int(self.week):
            key = (pid, int(week))
            cached = self._availability_state_cache.get(key)
            if cached is None:
                cached = _frozen_availability_state(record)
                if cached is None:
                    return original_availability(self, player, week)
                self._availability_state_cache[key] = cached
            return cached
        return original_availability(self, player, week)

    def replay_lock(self, player, week):
        pid = _finite_int(player.get("espn_id"))
        record = frozen_records.get(pid) if pid is not None else None
        if record is not None and int(week) == int(self.week):
            key = (pid, int(week))
            cached = self._lock_timing_cache.get(key)
            if cached is None:
                cached = _frozen_lock_timing(record)
                if cached is None:
                    return original_lock(self, player, week)
                self._lock_timing_cache[key] = cached
            return cached
        return original_lock(self, player, week)

    tm.enrich_season_values = replay_enrich
    tm.UtilityContext.yield_state = replay_yield
    tm.UtilityContext.availability_state = replay_availability
    tm.UtilityContext.lock_timing = replay_lock
    zero_base_player_ids = tuple(
        sorted(
            pid
            for pid, record in player_records.items()
            if _captured_base_mean(record) == 0.0
        )
    )
    zero_base_specialist_ids = tuple(
        sorted(
            pid
            for pid, record in specialist_records.items()
            if _captured_base_mean(record) == 0.0
        )
    )
    try:
        yield {
            "frozen_rostered_player_count": len(player_records),
            "frozen_specialist_count": len(specialist_records),
            "zero_base_rostered_player_count": len(zero_base_player_ids),
            "zero_base_rostered_player_ids": list(zero_base_player_ids),
            "zero_base_specialist_count": len(zero_base_specialist_ids),
            "zero_base_specialist_ids": list(zero_base_specialist_ids),
            "reconstructed_market_contract": (
                state.metadata.get("player_value_source_contract")
            ),
        }
    finally:
        tm.enrich_season_values = original_enrich
        tm.UtilityContext.yield_state = original_yield
        tm.UtilityContext.availability_state = original_availability
        tm.UtilityContext.lock_timing = original_lock


def _compact(row: Mapping[str, Any], fields: Sequence[str]) -> dict[str, Any]:
    return {
        key: _deep_thaw(row.get(key))
        for key in fields
        if key in row
    }


def _paired_uncertainty(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: row.get(key)
        for key in (
            "p_utility_better_if_acquired",
            "p_utility_worse_if_acquired",
            "p_utility_tie_if_acquired",
            "delta_total_utility_p16",
            "delta_total_utility_p84",
            "delta_h2h_sd",
            "delta_h2h_p16",
            "delta_h2h_p84",
            "mc_scenarios",
        )
        if key in row
    }


def _delta_uncertainty(row: Mapping[str, Any]) -> dict[str, Any]:
    delta = row.get("conditional_complete_state_delta")
    if not isinstance(delta, Mapping):
        delta = row.get("complete_state_delta")
    out = {}
    if isinstance(delta, Mapping):
        out["complete_state_delta"] = {
            key: delta.get(key)
            for key in (
                "mean", "mean_p16", "mean_p84",
                "p_better", "p_tie", "p_worse", "classification",
            )
            if key in delta
        }
    if "p_acquire" in row:
        out["p_acquire"] = row.get("p_acquire")
    return out


def _candidate_token(
    action_family: str,
    prediction: Mapping[str, Any],
    uncertainty: Mapping[str, Any],
) -> str:
    payload = json.dumps(
        {
            "action_family": action_family,
            "prediction": prediction,
            "uncertainty": uncertainty,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:20]


def _make_candidate(
    *,
    action_family: str,
    channel_rank: int,
    prediction: Mapping[str, Any],
    uncertainty: Mapping[str, Any],
    authorized: bool,
) -> dict[str, Any]:
    pred = {
        "channel_rank": int(channel_rank),
        "rank_scope": "CHANNEL_LOCAL",
        "authorized_by_weekly_authority": bool(authorized),
        **dict(prediction),
    }
    unc = dict(uncertainty)
    return {
        "candidate_id": (
            f"{action_family}:{_candidate_token(action_family, pred, unc)}"
        ),
        "action_family": action_family,
        "prediction": pred,
        "uncertainty": unc,
        "authorized": bool(authorized),
    }


def _hold_candidate(
    family: str,
    *,
    channel_rank: int,
    reason: str,
) -> dict[str, Any]:
    return _make_candidate(
        action_family=family,
        channel_rank=channel_rank,
        prediction={
            "action": "HOLD",
            "hold_reason": str(reason),
        },
        uncertainty={},
        authorized=False,
    )


def _lineup_candidates(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    action_required = bool(report.get("action_required"))
    return [
        _make_candidate(
            action_family=LINEUP,
            channel_rank=1,
            prediction={
                "action": "SET_LINEUP" if action_required else "HOLD_LINEUP",
                "action_required": action_required,
                "lineup_legality_complete": bool(
                    report.get("lineup_legality_complete")
                ),
                "lineup_legality_gaps": list(
                    report.get("lineup_legality_gaps") or []
                ),
                "selected_espn_ids": list(
                    report.get("selected_espn_ids") or []
                ),
                "current_starter_espn_ids": list(
                    report.get("current_starter_espn_ids") or []
                ),
                "locked_espn_ids": list(
                    report.get("locked_espn_ids") or []
                ),
                "unresolved_lock_espn_ids": list(
                    report.get("unresolved_lock_espn_ids") or []
                ),
                "total_expected": report.get("total_expected"),
            },
            uncertainty={
                "authority": "EXPECTED_VALUE_LINEUP_OPTIMIZER",
                "lock_evidence_complete": not bool(
                    report.get("unresolved_lock_espn_ids")
                ),
            },
            authorized=action_required,
        )
    ]


def _player_candidates(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [
        dict(row)
        for row in (
            list(report.get("free_agent_actions") or [])
            + list(report.get("waiver_actions") or [])
        )
        if isinstance(row, Mapping)
    ]
    out: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        classification = str(
            row.get("combined_action_classification")
            or row.get("action_classification")
            or ""
        )
        out.append(
            _make_candidate(
                action_family=PLAYER,
                channel_rank=index,
                prediction=_compact(row, _PLAYER_FIELDS),
                uncertainty=_paired_uncertainty(row),
                authorized=classification == "ACTIONABLE_EDGE",
            )
        )
    out.append(
        _hold_candidate(
            PLAYER,
            channel_rank=len(out) + 1,
            reason="PLAYER_WEEKLY_AUTHORITY_BASELINE",
        )
    )
    return out


def _specialist_candidates(
    family: str,
    report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    block = (
        report.get("one_slot_policy")
        if isinstance(report.get("one_slot_policy"), Mapping)
        else {}
    )
    rows: list[tuple[dict[str, Any], bool, str]] = []

    for item in (block.get("authorized_current_actions") or []):
        if not isinstance(item, Mapping):
            continue
        action = item.get("action")
        if not isinstance(action, Mapping):
            continue
        row = dict(action)
        row["acquisition_state"] = item.get("acquisition_state")
        rows.append((row, True, "AUTHORIZED_CURRENT"))

    for row in block.get("current_waiver_actions") or []:
        if isinstance(row, Mapping):
            rows.append((dict(row), False, "CURRENT_WAIVER_FRONTIER"))

    for row in report.get("swap_actions") or []:
        if isinstance(row, Mapping):
            rows.append((dict(row), False, "STATIC_SAME_CHANNEL_FRONTIER"))

    for row in report.get("dynamic_carry_actions") or []:
        if isinstance(row, Mapping):
            rows.append((dict(row), False, "DYNAMIC_CARRY_FRONTIER"))

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row, authorized, source in rows:
        prediction = {
            "frontier_source": source,
            **_compact(row, _SPECIALIST_FIELDS),
        }
        uncertainty = _delta_uncertainty(row)
        token = _candidate_token(family, prediction, uncertainty)
        if token in seen:
            # Preserve the strongest authorization when the same row is present
            # in both the complete frontier and authorized-current list.
            for existing in out:
                if existing["candidate_id"].endswith(token) and authorized:
                    existing["authorized"] = True
                    existing["prediction"][
                        "authorized_by_weekly_authority"
                    ] = True
            continue
        seen.add(token)
        out.append(
            _make_candidate(
                action_family=family,
                channel_rank=len(out) + 1,
                prediction=prediction,
                uncertainty=uncertainty,
                authorized=authorized,
            )
        )

    out.append(
        _hold_candidate(
            family,
            channel_rank=len(out) + 1,
            reason=f"{family.upper()}_WEEKLY_AUTHORITY_BASELINE",
        )
    )
    return out


def _ir_candidates(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    recommended = report.get("recommended_action")
    recommended_add = None
    if isinstance(recommended, Mapping):
        add = recommended.get("add")
        if isinstance(add, Mapping):
            recommended_add = _finite_int(add.get("add_espn_id"))

    out: list[dict[str, Any]] = []
    for index, raw in enumerate(report.get("candidate_rows") or [], 1):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        add_id = _finite_int(row.get("add_espn_id"))
        authorized = (
            recommended_add is not None
            and add_id == recommended_add
            and str(row.get("classification") or "") == "ACTIONABLE_EDGE"
        )
        prediction = _compact(
            row,
            (
                "channel", "add_espn_id", "add_name", "add_position",
                "add_team", "drop_espn_id", "drop_name",
                "fantasy_status", "p_acquire", "classification",
                "expected_complete_state_delta_mean",
                "future_capacity_credit", "information_policy",
            ),
        )
        out.append(
            _make_candidate(
                action_family=IR,
                channel_rank=index,
                prediction=prediction,
                uncertainty=_delta_uncertainty(row),
                authorized=authorized,
            )
        )
    out.append(
        _hold_candidate(
            IR,
            channel_rank=len(out) + 1,
            reason=str(
                report.get("coverage_reason")
                or "IR_WEEKLY_AUTHORITY_BASELINE"
            ),
        )
    )
    return out


def _trade_candidates(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    one: list[dict[str, Any]] = []
    multi: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        family = str(row.get("package_family") or "1x1")
        target = one if family == "1x1" else multi
        action_family = TRADE_1X1 if family == "1x1" else TRADE_MULTI
        authorized = str(row.get("classification") or "") == "ACTIONABLE_OFFER"
        target.append(
            _make_candidate(
                action_family=action_family,
                channel_rank=len(target) + 1,
                prediction=_compact(row, _TRADE_FIELDS),
                uncertainty={
                    key: row.get(key)
                    for key in (
                        "our_p_better", "partner_p_better",
                        "p_accept", "p_counter", "p_reject",
                        "mc_scenarios",
                    )
                    if key in row
                },
                authorized=authorized,
            )
        )
    one.append(
        _hold_candidate(
            TRADE_1X1,
            channel_rank=len(one) + 1,
            reason="ONE_FOR_ONE_PLAYER_TRADE_BASELINE",
        )
    )
    multi.append(
        _hold_candidate(
            TRADE_MULTI,
            channel_rank=len(multi) + 1,
            reason="MULTI_ASSET_PLAYER_TRADE_BASELINE",
        )
    )
    return one, multi


def _specialist_trade_candidates(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(rows, 1):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        out.append(
            _make_candidate(
                action_family=TRADE_SPECIALIST,
                channel_rank=index,
                prediction=_compact(row, _TRADE_FIELDS),
                uncertainty={
                    key: row.get(key)
                    for key in (
                        "our_p_better", "partner_p_better",
                        "p_accept", "p_counter", "p_reject",
                        "mc_scenarios",
                    )
                    if key in row
                },
                authorized=(
                    str(row.get("classification") or "")
                    == "ACTIONABLE_OFFER"
                ),
            )
        )
    out.append(
        _hold_candidate(
            TRADE_SPECIALIST,
            channel_rank=len(out) + 1,
            reason="SPECIALIST_INCLUSIVE_TRADE_BASELINE",
        )
    )
    return out


def _coverage(
    reports: Mapping[str, Any],
    candidates_by_family: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    specialist_coverage: dict[str, Any] = {}
    for family in (DST, KICKER):
        report = reports[family]
        block = (
            report.get("one_slot_policy")
            if isinstance(report.get("one_slot_policy"), Mapping)
            else {}
        )
        specialist_coverage[family] = {
            "current_waiver_coverage_complete": bool(
                block.get("current_waiver_coverage_complete", True)
            ),
            "current_waiver_one_slot_coverage_complete": block.get(
                "current_waiver_one_slot_coverage_complete"
            ),
            "current_waiver_carry2_coverage_complete": block.get(
                "current_waiver_carry2_coverage_complete"
            ),
            "current_waiver_candidates_total": block.get(
                "current_waiver_candidates_total"
            ),
            "modeled_current_waivers": block.get("modeled_current_waivers"),
        }

    lineup_ok = bool(
        reports[LINEUP].get("lineup_legality_complete")
    ) and not bool(reports[LINEUP].get("lineup_legality_gaps"))
    ir_ok = bool(reports[IR].get("coverage_complete"))
    specialist_ok = all(
        row["current_waiver_coverage_complete"]
        for row in specialist_coverage.values()
    )
    required = ACTION_FAMILY_ORDER
    counts = {
        family: len(candidates_by_family.get(family) or ())
        for family in required
    }

    return {
        "required_action_families": list(required),
        "coverage_complete": bool(lineup_ok and ir_ok and specialist_ok),
        "lineup_legality_complete": lineup_ok,
        "ir_coverage_complete": ir_ok,
        "specialist_coverage": specialist_coverage,
        "candidate_counts": counts,
        "player_screen_actions_total": reports[PLAYER].get(
            "screen_actions_total"
        ),
        "player_predictive_actions_evaluated": reports[PLAYER].get(
            "predictive_actions_evaluated"
        ),
        "player_trade_supported_package_families": [
            "1x1", "1x2", "2x1", "2x2"
        ],
        "specialist_trade_supported_package_families": [
            "1x1", "1x2", "2x1", "2x2"
        ],
        "trade_search_contract": (
            "BOUNDED_FAMILY_BALANCED_SCREEN_TO_PAIRED_PREDICTIVE_MC"
        ),
    }


def _freeze_candidates_and_selection(
    candidates_by_family: Mapping[str, Sequence[dict[str, Any]]],
) -> tuple[list[PhaseACandidate], tuple[dict[str, Any], ...], dict[str, Any]]:
    frozen: list[PhaseACandidate] = []
    selections: list[dict[str, Any]] = []
    global_rank = 1

    for family in ACTION_FAMILY_ORDER:
        rows = list(candidates_by_family.get(family) or [])
        if not rows:
            raise Week3PhaseAEvaluationError(
                f"Phase-A family produced no candidates: {family}"
            )
        authorized_ids: list[str] = []
        hold_ids: list[str] = []
        for row in rows:
            candidate = PhaseACandidate(
                candidate_id=str(row["candidate_id"]),
                action_family=family,
                rank=global_rank,
                prediction=row["prediction"],
                uncertainty=row["uncertainty"],
            )
            frozen.append(candidate)
            if bool(row.get("authorized")):
                authorized_ids.append(candidate.candidate_id)
            if str(candidate.prediction.get("action") or "").upper().startswith(
                "HOLD"
            ):
                hold_ids.append(candidate.candidate_id)
            global_rank += 1

        selected_ids = authorized_ids or hold_ids[:1]
        if not selected_ids:
            raise Week3PhaseAEvaluationError(
                f"Phase-A family lacks authorized action or HOLD: {family}"
            )
        selections.append(
            {
                "action_family": family,
                "status": (
                    "PASS / ACTION" if authorized_ids
                    else f"PASS / HOLD:{family}"
                ),
                "candidate_ids": selected_ids,
            }
        )

    model_action = {
        "selection_semantics": (
            "PER_CHANNEL_WEEKLY_AUTHORITY_SET_NO_CROSS_CHANNEL_ASSET_RANKING"
        ),
        "overall_state": (
            "ACTION_REQUIRED"
            if any(row["status"] == "PASS / ACTION" for row in selections)
            else "NO_ACTION"
        ),
        "channel_selections": selections,
        "authorized_candidate_ids": [
            candidate_id
            for row in selections
            if row["status"] == "PASS / ACTION"
            for candidate_id in row["candidate_ids"]
        ],
    }
    return frozen, tuple(selections), model_action


def evaluate_week3_phase_a(
    *,
    snapshot_path: str | Path,
    capture_path: str | Path,
    league_path: str | Path,
    model_path: str | Path,
    values_path: str | Path,
    frozen_utc: str,
    engine_identities: Mapping[str, Any],
    player_mc_scenarios: int | None = None,
    specialist_mc_scenarios: int | None = None,
    trade_mc_scenarios: int | None = None,
    trade_limit: int = 6,
) -> Week3PhaseAEvaluation:
    """Evaluate one Week 3 historical decision point behind the Phase-A firewall."""
    from .weekly_decision_cycle import default_authorities
    from .weekly_manager import resolve_team

    state = build_week3_replay_input(
        snapshot_path=snapshot_path,
        capture_path=capture_path,
        league_path=league_path,
        model_path=model_path,
        values_path=values_path,
    )
    snapshot = _deep_thaw(state.snapshot)
    league = _deep_thaw(state.league)
    model = _deep_thaw(state.model)
    transaction_dependency = _bind_frozen_transaction_settings(
        snapshot,
        snapshot_path,
        state.snapshot_utc,
    )

    capture = _load_json(capture_path)
    team_id = _finite_int(capture.get("team_id"))
    if team_id is None:
        raise Week3PhaseAEvaluationError(
            "Week 3 prospective capture is missing team_id"
        )
    team = resolve_team(snapshot, team_id=team_id)
    authorities = default_authorities()

    with frozen_week3_authority_overlay(state) as overlay_metadata:
        lineup_report = dict(
            authorities.lineup(
                snapshot,
                league,
                model,
                values_path=values_path,
                team_name=None,
                team_id=team_id,
            )
        )
        player_report = dict(
            authorities.player_actions(
                snapshot,
                league,
                model,
                values_path=values_path,
                team_name=None,
                team_id=team_id,
                position=None,
                predictive_mc_scenarios=player_mc_scenarios,
            )
        )
        dst_report = dict(
            authorities.defense(
                snapshot,
                league,
                model,
                values_path=values_path,
                team_name=None,
                team_id=team_id,
                mc_scenarios=specialist_mc_scenarios,
            )
        )
        kicker_report = dict(
            authorities.kicker(
                snapshot,
                league,
                model,
                values_path=values_path,
                team_name=None,
                team_id=team_id,
                mc_scenarios=specialist_mc_scenarios,
            )
        )
        if authorities.ir_replacement is None:
            raise Week3PhaseAEvaluationError(
                "IR replacement authority is not commissioned"
            )
        ir_report = dict(
            authorities.ir_replacement(
                snapshot,
                league,
                model,
                values_path=values_path,
                team_name=None,
                team_id=team_id,
                player_mc_scenarios=player_mc_scenarios,
                specialist_mc_scenarios=specialist_mc_scenarios,
            )
        )
        trade_rows = [
            dict(row)
            for row in authorities.trade_search(
                snapshot,
                league,
                model,
                values_path=values_path,
                user_team=team,
                limit=int(trade_limit),
                mc_scenarios=trade_mc_scenarios,
            )
        ]
        if authorities.specialist_trade_search is None:
            raise Week3PhaseAEvaluationError(
                "specialist-inclusive trade authority is not commissioned"
            )
        specialist_trade_rows = [
            dict(row)
            for row in authorities.specialist_trade_search(
                snapshot,
                league,
                model,
                values_path=values_path,
                user_team=team,
                limit=int(trade_limit),
                mc_scenarios=trade_mc_scenarios,
            )
        ]

    reports = {
        LINEUP: lineup_report,
        PLAYER: player_report,
        DST: dst_report,
        KICKER: kicker_report,
        IR: ir_report,
    }
    trade_one, trade_multi = _trade_candidates(trade_rows)
    candidates_by_family: dict[str, list[dict[str, Any]]] = {
        LINEUP: _lineup_candidates(lineup_report),
        PLAYER: _player_candidates(player_report),
        DST: _specialist_candidates(DST, dst_report),
        KICKER: _specialist_candidates(KICKER, kicker_report),
        IR: _ir_candidates(ir_report),
        TRADE_1X1: trade_one,
        TRADE_MULTI: trade_multi,
        TRADE_SPECIALIST: _specialist_trade_candidates(
            specialist_trade_rows
        ),
    }

    coverage = _coverage(reports, candidates_by_family)
    if coverage["coverage_complete"] is not True:
        raise Week3PhaseAEvaluationError(
            "required Phase-A action coverage is incomplete"
        )

    candidates, selections, model_action = _freeze_candidates_and_selection(
        candidates_by_family
    )
    dependencies = tuple(state.dependencies) + (transaction_dependency,)
    classification = state.summary()

    receipt = freeze_phase_a_receipt(
        frozen_utc=str(frozen_utc),
        season=2026,
        week=3,
        dependencies=dependencies,
        engine_identities=dict(engine_identities),
        candidates=candidates,
        model_action=model_action,
        metadata={
            "evaluator_contract": WEEK3_PHASE_A_EVALUATOR_CONTRACT,
            "snapshot_utc": state.snapshot_utc,
            "captured_utc": state.captured_utc,
            "team_id": int(team_id),
            "team_name": team.get("name"),
            "coverage": coverage,
            "rank_semantics": (
                "GLOBAL_RANK_IS_DETERMINISTIC_SERIALIZATION_ORDER; "
                "PREFERENCE_RANKING_IS_CHANNEL_LOCAL"
            ),
            "channel_selection_semantics": model_action[
                "selection_semantics"
            ],
            "frozen_overlay": dict(overlay_metadata),
            "input_counts": classification["counts"],
            "trade_settings_dependency": transaction_dependency.to_dict(),
            "trade_limit": int(trade_limit),
            "player_mc_scenarios_requested": player_mc_scenarios,
            "specialist_mc_scenarios_requested": specialist_mc_scenarios,
            "trade_mc_scenarios_requested": trade_mc_scenarios,
            "outcomes_available_to_evaluator": False,
            "phase_b_attachment": "NONE",
        },
    )

    result = Week3PhaseAEvaluation(
        contract=WEEK3_PHASE_A_EVALUATOR_CONTRACT,
        receipt=receipt,
        coverage=coverage,
        channel_selections=selections,
        metadata={
            "snapshot_utc": state.snapshot_utc,
            "captured_utc": state.captured_utc,
            "team_id": int(team_id),
            "candidate_count": len(candidates),
            "authorized_candidate_count": len(
                model_action["authorized_candidate_ids"]
            ),
            "transaction_settings_sha256": transaction_dependency.sha256,
            "replay_mode": receipt.replay_mode,
        },
    )
    result.verify()
    return result
