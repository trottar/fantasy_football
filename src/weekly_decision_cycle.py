from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .weekly_operational_health import (
    BLOCKED as HEALTH_BLOCKED,
    PASS as HEALTH_PASS,
    OperationalHealthReceipt,
    build_operational_health_receipt,
    capture_integrity_state,
)


CONTRACT = "WEEKLY_DECISION_COMPLETION_GATE_B2A_IR_ROSTER_STATE_V001"
SCHEMA_VERSION = 1

STATE_ACTION = "COMPLETE / ACTION_REQUIRED"
STATE_NO_ACTION = "COMPLETE / NO_ACTION"
STATE_INCOMPLETE = "INCOMPLETE_COVERAGE"
STATE_BLOCKED_HEALTH = "BLOCKED_HEALTH"
STATE_CAPTURE_REQUIRED = "CAPTURE_REQUIRED"

STATUS_ACTION = "PASS / ACTION"

LINEUP = "lineup_availability"
PLAYER = "player_waiver_free_agent"
DST = "dst_waiver_free_agent"
KICKER = "kicker_waiver_free_agent"
IR = "ir_reserve_open_slot_injury_replacement"
TRADE_1X1 = "trade_one_for_one_player"
TRADE_MULTI = "trade_multi_player_unequal"
TRADE_SPECIALIST = "trade_specialist_inclusive"
PROVENANCE = "prospective_capture_provenance"

REQUIRED_CHANNELS = (
    LINEUP,
    PLAYER,
    DST,
    KICKER,
    IR,
    TRADE_1X1,
    TRADE_MULTI,
    TRADE_SPECIALIST,
    PROVENANCE,
)


@dataclass(frozen=True)
class ChannelReceipt:
    key: str
    label: str
    status: str
    authority: str
    evidence: dict[str, Any] = field(default_factory=dict)
    scope: str | None = None
    gap: str | None = None
    action: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WeeklyDecisionReceipt:
    schema_version: int
    contract: str
    generated_utc: str
    season: int | None
    week: int | None
    team_id: int | None
    team_name: str | None
    overall_state: str
    reason: str
    channels: tuple[ChannelReceipt, ...]
    operational_health: OperationalHealthReceipt
    authorized_actions: tuple[dict[str, Any], ...]
    unsupported_or_missing: tuple[str, ...]
    stale_or_missing_health: tuple[str, ...]
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "contract": self.contract,
            "generated_utc": self.generated_utc,
            "season": self.season,
            "week": self.week,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "overall_state": self.overall_state,
            "reason": self.reason,
            "channels": [row.to_dict() for row in self.channels],
            "operational_health": self.operational_health.to_dict(),
            "authorized_actions": list(self.authorized_actions),
            "unsupported_or_missing": list(self.unsupported_or_missing),
            "stale_or_missing_health": list(self.stale_or_missing_health),
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True)
class WeeklyAuthorities:
    lineup: Callable[..., Mapping[str, Any]]
    player_actions: Callable[..., Mapping[str, Any]]
    defense: Callable[..., Mapping[str, Any]]
    kicker: Callable[..., Mapping[str, Any]]
    trade_search: Callable[..., Sequence[Mapping[str, Any]]]
    persistence_state: Callable[[], Any]
    ir_state: Callable[..., Mapping[str, Any]] | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _sha256_file(path: str | Path) -> str | None:
    p = Path(path)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def observed_dependency_identities(
    *, league_path: str | Path, model_path: str | Path, values_path: str | Path
) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, path in (
        ("league_config", league_path),
        ("model_config", model_path),
        ("player_values", values_path),
    ):
        digest = _sha256_file(path)
        if digest:
            out[key] = digest
    return out


def load_json_evidence(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"JSON evidence must be an object: {p}")
    return obj


def observed_runtime_version(version_path: str | Path = "VERSION") -> str | None:
    p = Path(version_path)
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8").strip()
    return text or None


def _default_lineup(
    snapshot: Mapping[str, Any], league: Mapping[str, Any], model: Mapping[str, Any], *,
    values_path: str | Path, team_name: str | None, team_id: int | None,
) -> Mapping[str, Any]:
    from .transaction_manager import UtilityContext
    from .weekly_manager import optimize_lineup, resolve_team

    team = resolve_team(dict(snapshot), team_name=team_name, team_id=team_id)
    ctx = UtilityContext(dict(snapshot), dict(league), dict(model), values_path, team)
    result = optimize_lineup(ctx.roster, dict(league), dict(model))
    selected = sorted(
        int(row["espn_id"])
        for row in result.rows
        if _finite_int(row.get("espn_id")) is not None
    )
    current = sorted(
        int(player["espn_id"])
        for player in team.get("roster") or []
        if _finite_int(player.get("espn_id")) is not None
        and str(player.get("lineup_slot") or "").upper() not in {"BENCH", "BE", "IR", "RESERVE", ""}
    )
    locked = sorted(
        int(player["espn_id"])
        for player in team.get("roster") or []
        if _finite_int(player.get("espn_id")) is not None and bool(player.get("lineup_locked"))
    )
    return {
        "missing_slots": list(result.missing_slots),
        "selected_espn_ids": selected,
        "current_starter_espn_ids": current,
        "locked_espn_ids": locked,
        "action_required": bool(selected != current),
        "total_expected": float(result.total_expected),
    }


def default_authorities() -> WeeklyAuthorities:
    from .ir_roster_state import evaluate_ir_roster_state
    from .market_manager import search_trades
    from .observability.persistence import shadow_persistence_state
    from .specialist_policy_v032 import evaluate_defense_channel, evaluate_kicker_channel
    from .transaction_manager import evaluate_actions

    return WeeklyAuthorities(
        lineup=_default_lineup,
        player_actions=evaluate_actions,
        defense=evaluate_defense_channel,
        kicker=evaluate_kicker_channel,
        trade_search=search_trades,
        persistence_state=shadow_persistence_state,
        ir_state=evaluate_ir_roster_state,
    )


def _hold(scope: str) -> str:
    return f"PASS / HOLD:{scope}"


def classify_weekly_decision(
    channels: Sequence[ChannelReceipt],
    health: OperationalHealthReceipt,
    *, capture_required: bool,
) -> tuple[str, str]:
    by_key = {row.key: row for row in channels}
    missing = [key for key in REQUIRED_CHANNELS if key not in by_key]
    if capture_required:
        return STATE_CAPTURE_REQUIRED, "prospective capture is missing, stale, or fails the pre-data firewall"
    if health.status != HEALTH_PASS:
        return STATE_BLOCKED_HEALTH, "weekly operational-health gate is blocked"
    if missing:
        return STATE_INCOMPLETE, "required receipt rows missing: " + ", ".join(missing)
    blocked_rows = [row.key for row in channels if row.status.startswith("BLOCKED_HEALTH")]
    if blocked_rows:
        return STATE_BLOCKED_HEALTH, "channel health blocked: " + ", ".join(blocked_rows)
    incomplete = [row.key for row in channels if row.status.startswith("INCOMPLETE_COVERAGE")]
    if incomplete:
        return STATE_INCOMPLETE, "unsupported or incomplete action families: " + ", ".join(incomplete)
    if any(row.status == STATUS_ACTION for row in channels):
        return STATE_ACTION, "all required coverage and health receipts pass; at least one authority requires action"
    return STATE_NO_ACTION, "all required coverage and health receipts pass; no authority requires action"


def _lineup_receipt(report: Mapping[str, Any]) -> ChannelReceipt:
    missing = [str(x) for x in report.get("missing_slots") or []]
    if missing:
        return ChannelReceipt(
            LINEUP,
            "Lineup / availability",
            "INCOMPLETE_COVERAGE:LINEUP_MISSING_SLOTS",
            "weekly_manager.optimize_lineup",
            evidence=dict(report),
            gap="missing legal lineup slots: " + ", ".join(missing),
        )
    action_required = bool(report.get("action_required"))
    return ChannelReceipt(
        LINEUP,
        "Lineup / availability",
        STATUS_ACTION if action_required else _hold("LINEUP_AVAILABILITY"),
        "weekly_manager.optimize_lineup",
        evidence=dict(report),
        scope="complete legal current lineup",
        action={"kind": "LINEUP_REVIEW", "selected_espn_ids": list(report.get("selected_espn_ids") or [])}
        if action_required else None,
    )


def _player_receipt(report: Mapping[str, Any]) -> ChannelReceipt:
    rows = list(report.get("free_agent_actions") or []) + list(report.get("waiver_actions") or [])
    actionable = [
        dict(row) for row in rows
        if str(row.get("combined_action_classification") or row.get("action_classification") or "") == "ACTIONABLE_EDGE"
    ]
    evidence = {
        "candidate_pool_evaluated": report.get("candidate_pool_evaluated"),
        "legal_drop_players": report.get("legal_drop_players"),
        "free_agent_reported": len(report.get("free_agent_actions") or []),
        "waiver_reported": len(report.get("waiver_actions") or []),
        "actionable_edges": len(actionable),
        "market_channel": report.get("market_channel"),
    }
    return ChannelReceipt(
        PLAYER,
        "Player waiver / free-agent (QB/RB/WR/TE)",
        STATUS_ACTION if actionable else _hold("PLAYER_WAIVER_FREE_AGENT"),
        "transaction_manager.evaluate_actions",
        evidence=evidence,
        scope="whole actionable QB/RB/WR/TE pool x legal player drops",
        action={"kind": "PLAYER_ADD_DROP", "candidates": actionable} if actionable else None,
    )


def _specialist_receipt(key: str, label: str, report: Mapping[str, Any], authority: str) -> ChannelReceipt:
    block = report.get("one_slot_policy") if isinstance(report.get("one_slot_policy"), Mapping) else {}
    excluded = int((block or {}).get("excluded_current_waivers") or 0)
    modeled = int((block or {}).get("modeled_current_waivers") or 0)
    coverage_complete = bool((block or {}).get("current_waiver_coverage_complete")) if excluded > 0 else True
    recommendation = dict((block or {}).get("recommended_current_action") or {"action": "HOLD"})
    authoritative = bool((block or {}).get("authoritative_current_action"))

    carry_rows = [
        dict(row) for row in (report.get("dynamic_carry_actions") or [])
        if isinstance(row, Mapping) and bool(row.get("current_activation"))
    ]
    carry_rows.sort(
        key=lambda row: (
            float(row.get("expected_complete_state_delta_mean") or -999.0),
            float(((row.get("complete_state_delta") or {}).get("mean") or -999.0)),
        ),
        reverse=True,
    )
    current_carry = carry_rows[0] if carry_rows else None
    carry_class = str((current_carry or {}).get("classification") or "")
    carry_action = carry_class in {"CARRY2_ACTIONABLE_EDGE", "CARRY2_POSSIBLE_EDGE"}

    one_slot_action = authoritative and str(recommendation.get("action") or "HOLD").upper() != "HOLD"
    authorized_actions: list[dict[str, Any]] = []
    if one_slot_action:
        authorized_actions.append({
            "policy": "ONE_SLOT",
            "recommendation": recommendation,
        })
    if carry_action:
        authorized_actions.append({
            "policy": "CARRY2",
            "recommendation": dict(current_carry or {}),
        })

    evidence = {
        "excluded_current_waivers": excluded,
        "modeled_current_waivers": modeled,
        "current_waiver_coverage_complete": coverage_complete,
        "current_waiver_one_slot_coverage_complete": (block or {}).get("current_waiver_one_slot_coverage_complete"),
        "current_waiver_carry2_coverage_complete": (block or {}).get("current_waiver_carry2_coverage_complete"),
        "guaranteed_free_agents_initial": (block or {}).get("guaranteed_free_agents_initial"),
        "recommended_current_action": recommendation,
        "authoritative_current_action": authoritative,
        "complete_state_delta": dict((block or {}).get("complete_state_delta") or {}),
        "current_waiver_actions": list((block or {}).get("current_waiver_actions") or []),
        "current_carry_action": dict(current_carry or {}),
        "carry2_current_recommendation": report.get("carry2_current_recommendation"),
    }
    if excluded > 0 and not coverage_complete:
        return ChannelReceipt(
            key,
            label,
            "INCOMPLETE_COVERAGE:CURRENT_SPECIALIST_WAIVERS_UNSUPPORTED",
            authority,
            evidence=evidence,
            gap=(
                f"{excluded} current waiver specialist(s) exist but only {modeled} "
                "have complete ONE_SLOT/CARRY2 acquisition-response coverage"
            ),
            action={"kind": key.upper(), "authorized_actions": authorized_actions} if authorized_actions else None,
        )

    is_action = bool(authorized_actions)
    return ChannelReceipt(
        key,
        label,
        STATUS_ACTION if is_action else _hold(key.upper()),
        authority,
        evidence=evidence,
        scope="whole actionable specialist FREEAGENT + current WAIVERS market under commissioned same-channel policy",
        action={"kind": key.upper(), "authorized_actions": authorized_actions} if is_action else None,
    )


def _trade_receipt(rows: Sequence[Mapping[str, Any]]) -> ChannelReceipt:
    actionable = [dict(row) for row in rows if str(row.get("classification") or "") == "ACTIONABLE_OFFER"]
    return ChannelReceipt(
        TRADE_1X1,
        "One-for-one player trades",
        STATUS_ACTION if actionable else _hold("ONE_FOR_ONE_PLAYER_TRADE"),
        "market_manager.search_trades",
        evidence={"evaluated_reported": len(rows), "actionable_offers": len(actionable)},
        scope="automated one-for-one QB/RB/WR/TE offers",
        action={"kind": "ONE_FOR_ONE_PLAYER_TRADE", "offers": actionable} if actionable else None,
    )


def _legacy_ir_receipt() -> ChannelReceipt:
    return ChannelReceipt(
        IR,
        "IR / reserve / open-slot / injury replacement",
        "INCOMPLETE_COVERAGE:GATE_B_IR_AND_INJURY_STATE",
        "Gate A capability inventory",
        gap="explicit IR-move-plus-add and decision-time multiweek absence state are not commissioned",
    )


def _ir_receipt(report: Mapping[str, Any]) -> ChannelReceipt:
    evidence = dict(report)
    if str(report.get("status") or "").upper() != "PASS":
        blockers = [str(item) for item in (report.get("blockers") or [])]
        return ChannelReceipt(
            IR,
            "IR / reserve / open-slot / injury replacement",
            "INCOMPLETE_COVERAGE:GATE_B_IR_ROSTER_STATE_BLOCKED",
            "ir_roster_state.evaluate_ir_roster_state",
            evidence=evidence,
            scope="current ESPN roster-capacity and IR-legality state",
            gap=(
                "current IR/open-slot state is invalid or incomplete"
                + (": " + ", ".join(blockers) if blockers else "")
            ),
        )
    return ChannelReceipt(
        IR,
        "IR / reserve / open-slot / injury replacement",
        "INCOMPLETE_COVERAGE:GATE_B_IR_REPLACEMENT_VALUE_AND_ABSENCE_HORIZON",
        "ir_roster_state.evaluate_ir_roster_state",
        evidence=evidence,
        scope="current ESPN roster capacity, IR eligibility, and move-to-IR-plus-add legality",
        gap=(
            "IR/open-slot legality is represented, but authoritative replacement value, "
            "specialist capacity coupling, and decision-time multiweek absence/capacity propagation "
            "are not yet commissioned"
        ),
    )


def _gate_b_receipts() -> list[ChannelReceipt]:
    return [
        ChannelReceipt(
            TRADE_MULTI,
            "Supported multi-player / unequal trades",
            "INCOMPLETE_COVERAGE:GATE_B_MULTI_ASSET_TRADE_SEARCH",
            "Gate A capability inventory",
            gap="evaluator supports bounded packages but automated search is one-for-one only",
        ),
        ChannelReceipt(
            TRADE_SPECIALIST,
            "DST/K-inclusive trades when league-legal",
            "INCOMPLETE_COVERAGE:GATE_B_SPECIALIST_TRADE_COMPOSITION",
            "Gate A capability inventory",
            gap="specialist-inclusive trade evaluator is not commissioned",
        ),
    ]


def run_weekly_decision_cycle(
    snapshot: Mapping[str, Any],
    league: Mapping[str, Any],
    model: Mapping[str, Any],
    *,
    values_path: str | Path = "data/processed/player_values_2026.csv",
    league_path: str | Path = "config/league.json",
    model_path: str | Path = "config/model.json",
    version_path: str | Path = "VERSION",
    team_name: str | None = None,
    team_id: int | None = None,
    player_mc_scenarios: int | None = None,
    specialist_mc_scenarios: int | None = None,
    trade_mc_scenarios: int | None = None,
    trade_limit: int = 6,
    capture: Mapping[str, Any] | None = None,
    commissioning_identity: Mapping[str, Any] | None = None,
    memory_health: Mapping[str, Any] | None = None,
    unresolved_diagnostics: Sequence[str] = (),
    material_state_change: bool = False,
    authorities: WeeklyAuthorities | None = None,
) -> WeeklyDecisionReceipt:
    authorities = authorities or default_authorities()
    espn = snapshot.get("espn", snapshot)
    season = _finite_int(espn.get("season")) if isinstance(espn, Mapping) else None
    week = _finite_int(espn.get("week")) if isinstance(espn, Mapping) else None

    capture_ok, capture_reasons = capture_integrity_state(capture)
    capture_required = bool(material_state_change or not capture_ok)

    # Resolve the user team once for metadata/trade authority without creating a
    # second completion classifier.
    try:
        from .weekly_manager import resolve_team
        team = resolve_team(dict(snapshot), team_name=team_name, team_id=team_id)
    except Exception:
        team = {"team_id": team_id, "name": team_name}
    resolved_team_id = _finite_int(team.get("team_id"))
    resolved_team_name = str(team.get("name") or team_name or "") or None

    channels: list[ChannelReceipt] = []
    # Gate A intentionally runs the existing authorities independently and only
    # classifies their receipts here. It does not change their football models.
    try:
        lineup = authorities.lineup(
            snapshot, league, model, values_path=values_path,
            team_name=team_name, team_id=team_id,
        )
        channels.append(_lineup_receipt(lineup))
    except Exception as exc:
        channels.append(ChannelReceipt(
            LINEUP, "Lineup / availability",
            "INCOMPLETE_COVERAGE:LINEUP_AUTHORITY_ERROR",
            "weekly_manager.optimize_lineup",
            evidence={"error_type": type(exc).__name__}, gap="lineup authority failed",
        ))

    try:
        player = authorities.player_actions(
            snapshot, league, model, values_path=values_path,
            team_name=team_name, team_id=team_id, position=None,
            predictive_mc_scenarios=player_mc_scenarios,
        )
        channels.append(_player_receipt(player))
    except Exception as exc:
        channels.append(ChannelReceipt(
            PLAYER, "Player waiver / free-agent (QB/RB/WR/TE)",
            "INCOMPLETE_COVERAGE:PLAYER_AUTHORITY_ERROR",
            "transaction_manager.evaluate_actions",
            evidence={"error_type": type(exc).__name__}, gap="player action authority failed",
        ))

    for key, label, fn, authority in (
        (DST, "DST waiver / free-agent", authorities.defense, "specialist_policy_v032.evaluate_defense_channel"),
        (KICKER, "Kicker waiver / free-agent", authorities.kicker, "specialist_policy_v032.evaluate_kicker_channel"),
    ):
        try:
            report = fn(
                snapshot, league, model, values_path=values_path,
                team_name=team_name, team_id=team_id,
                mc_scenarios=specialist_mc_scenarios,
            )
            channels.append(_specialist_receipt(key, label, report, authority))
        except Exception as exc:
            channels.append(ChannelReceipt(
                key, label, f"INCOMPLETE_COVERAGE:{key.upper()}_AUTHORITY_ERROR", authority,
                evidence={"error_type": type(exc).__name__}, gap=f"{label} authority failed",
            ))

    if authorities.ir_state is None:
        channels.append(_legacy_ir_receipt())
    else:
        try:
            ir_report = authorities.ir_state(
                snapshot, league, team_name=team_name, team_id=team_id
            )
            channels.append(_ir_receipt(ir_report))
        except Exception as exc:
            channels.append(ChannelReceipt(
                IR, "IR / reserve / open-slot / injury replacement",
                "INCOMPLETE_COVERAGE:GATE_B_IR_ROSTER_STATE_ERROR",
                "ir_roster_state.evaluate_ir_roster_state",
                evidence={"error_type": type(exc).__name__},
                gap="IR/open-slot roster-state authority failed",
            ))

    try:
        trade_rows = authorities.trade_search(
            snapshot, league, model, values_path=values_path,
            user_team=team, limit=trade_limit, mc_scenarios=trade_mc_scenarios,
        )
        channels.append(_trade_receipt(trade_rows))
    except Exception as exc:
        channels.append(ChannelReceipt(
            TRADE_1X1, "One-for-one player trades",
            "INCOMPLETE_COVERAGE:ONE_FOR_ONE_TRADE_AUTHORITY_ERROR",
            "market_manager.search_trades",
            evidence={"error_type": type(exc).__name__}, gap="one-for-one trade search failed",
        ))

    channels.extend(_gate_b_receipts())
    channels.append(ChannelReceipt(
        PROVENANCE,
        "Prospective capture / provenance",
        _hold("PROSPECTIVE_CAPTURE") if capture_ok and not material_state_change else "INCOMPLETE_COVERAGE:CAPTURE_REQUIRED",
        "prospective_measurement_v034.verify_capture_integrity",
        evidence={
            "capture_present": bool(capture),
            "capture_integrity_ok": bool(capture_ok),
            "material_state_change": bool(material_state_change),
            "reasons": capture_reasons,
        },
        gap="fresh decision-time capture required" if capture_required else None,
    ))

    dependencies = observed_dependency_identities(
        league_path=league_path, model_path=model_path, values_path=values_path
    )
    runtime_version = observed_runtime_version(version_path)
    try:
        persistence = authorities.persistence_state()
    except Exception as exc:
        class _FailedPersistence:
            enabled = False
            failed = True
            failures = 1
            disabled_reason = f"state_error:{type(exc).__name__}"
        persistence = _FailedPersistence()

    health = build_operational_health_receipt(
        snapshot=snapshot,
        capture=capture,
        commissioning_identity=commissioning_identity,
        observed_dependencies=dependencies,
        observed_runtime_version=runtime_version,
        memory_health=memory_health,
        persistence_state=persistence,
        unresolved_diagnostics=unresolved_diagnostics,
        receipt_inventory=[row.key for row in channels],
        required_receipts=REQUIRED_CHANNELS,
    )

    overall, reason = classify_weekly_decision(channels, health, capture_required=capture_required)
    actions = tuple(row.action for row in channels if row.action is not None)
    unsupported = tuple(
        f"{row.key}:{row.gap or row.status}"
        for row in channels if row.status.startswith("INCOMPLETE_COVERAGE")
    )
    provenance = {
        "snapshot_utc": snapshot.get("snapshot_utc") if isinstance(snapshot, Mapping) else None,
        "capture_integrity_ok": bool(capture_ok),
        "capture_reasons": capture_reasons,
        "material_state_change": bool(material_state_change),
        "source_checkpoint": (commissioning_identity or {}).get("source_checkpoint") if isinstance(commissioning_identity, Mapping) else None,
        "runtime_version": runtime_version,
    }
    return WeeklyDecisionReceipt(
        schema_version=SCHEMA_VERSION,
        contract=CONTRACT,
        generated_utc=utc_now(),
        season=season,
        week=week,
        team_id=resolved_team_id,
        team_name=resolved_team_name,
        overall_state=overall,
        reason=reason,
        channels=tuple(channels),
        operational_health=health,
        authorized_actions=actions,
        unsupported_or_missing=unsupported,
        stale_or_missing_health=tuple(health.blockers),
        provenance=provenance,
    )


def save_weekly_decision_receipt(
    receipt: WeeklyDecisionReceipt | Mapping[str, Any],
    out_dir: str | Path = "data/season_decisions",
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = receipt.to_dict() if isinstance(receipt, WeeklyDecisionReceipt) else dict(receipt)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out / f"weekly_decision_receipt_{stamp}.json"
    suffix = 1
    while path.exists():
        path = out / f"weekly_decision_receipt_{stamp}_{suffix:02d}.json"
        suffix += 1
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
