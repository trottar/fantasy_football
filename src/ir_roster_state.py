from __future__ import annotations

from typing import Any, Mapping

from .weekly_manager import resolve_team


ESPN_IR_RULE_SOURCE = "ESPN_FAN_SUPPORT_UPDATED_2026-08-18"
ESPN_IR_RULE = "OUT_OR_INJURY_RESERVE_ONLY"
IR_SLOT_NAMES = {"IR", "RESERVE"}
IR_MOVE_ELIGIBLE_STATUSES = {
    "OUT",
    "IR",
    "INJURY_RESERVE",
    "INJURED_RESERVE",
    "INJURED_RESERVE_IR",
}
# ESPN allows an already-stashed player upgraded from OUT/IR to Q or D to remain
# in the IR slot and does not block acquisitions. A player with no injury
# designation in IR makes the roster invalid for new additions.
IR_INCUMBENT_ALLOWED_STATUSES = IR_MOVE_ELIGIBLE_STATUSES | {"QUESTIONABLE", "DOUBTFUL"}


def _finite_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalized_status(value: Any) -> str:
    text = str(value or "").strip().upper()
    for token in ("/", "-", " "):
        text = text.replace(token, "_")
    while "__" in text:
        text = text.replace("__", "_")
    return text or "MISSING"


def _lineup_slot(player: Mapping[str, Any]) -> str:
    return str(player.get("lineup_slot") or "").strip().upper()


def _is_ir_slot(player: Mapping[str, Any]) -> bool:
    return _lineup_slot(player) in IR_SLOT_NAMES


def _active_capacity(league: Mapping[str, Any]) -> int:
    roster = league.get("roster") if isinstance(league, Mapping) else None
    if not isinstance(roster, Mapping):
        return 0
    total = 0
    for key, value in roster.items():
        if str(key).strip().upper() in IR_SLOT_NAMES:
            continue
        count = _finite_int(value)
        if count is not None and count > 0:
            total += count
    return total


def _ir_capacity(league: Mapping[str, Any]) -> int:
    roster = league.get("roster") if isinstance(league, Mapping) else None
    if not isinstance(roster, Mapping):
        return 0
    total = 0
    for key, value in roster.items():
        if str(key).strip().upper() not in IR_SLOT_NAMES:
            continue
        count = _finite_int(value)
        if count is not None and count > 0:
            total += count
    return total


def _position_counts(roster: list[Mapping[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for player in roster:
        position = str(player.get("position") or "").strip().upper()
        if position:
            out[position] = out.get(position, 0) + 1
    return dict(sorted(out.items()))


def _position_headroom(roster: list[Mapping[str, Any]], league: Mapping[str, Any]) -> dict[str, int | None]:
    counts = _position_counts(roster)
    maxima = league.get("position_maximums") if isinstance(league, Mapping) else None
    if not isinstance(maxima, Mapping):
        return {position: None for position in counts}
    positions = set(counts) | {str(key).strip().upper() for key in maxima}
    out: dict[str, int | None] = {}
    for position in sorted(p for p in positions if p):
        maximum = _finite_int(maxima.get(position))
        if maximum is None:
            out[position] = None
        else:
            out[position] = max(0, maximum - counts.get(position, 0))
    return out


def _move_candidate(player: Mapping[str, Any]) -> dict[str, Any] | None:
    if _is_ir_slot(player) or bool(player.get("lineup_locked")):
        return None
    status = _normalized_status(player.get("injury_status"))
    if status not in IR_MOVE_ELIGIBLE_STATUSES:
        return None
    return {
        "espn_id": _finite_int(player.get("espn_id")),
        "name": player.get("name"),
        "position": player.get("position"),
        "injury_status": status,
        "lineup_slot": _lineup_slot(player),
        "lineup_locked": bool(player.get("lineup_locked")),
    }


def build_ir_roster_state(team: Mapping[str, Any], league: Mapping[str, Any]) -> dict[str, Any]:
    """Represent ESPN IR/open-roster legality without inferring recovery timing.

    `eligible_slots` is deliberately ignored for IR eligibility. ESPN exposes IR in
    that compatibility list for healthy players too; current move eligibility is
    instead determined from ESPN's normalized `injury_status` designation.
    """
    roster = [dict(player) for player in (team.get("roster") or []) if isinstance(player, Mapping)]
    active_capacity = _active_capacity(league)
    ir_capacity = _ir_capacity(league)
    current_ir = [player for player in roster if _is_ir_slot(player)]
    active = [player for player in roster if not _is_ir_slot(player)]
    open_active = max(0, active_capacity - len(active))
    open_ir = max(0, ir_capacity - len(current_ir))

    move_candidates = [row for player in active if (row := _move_candidate(player)) is not None]
    move_candidates.sort(key=lambda row: (int(row.get("espn_id") or 10**12), str(row.get("name") or "")))

    incumbent_status_counts: dict[str, int] = {}
    invalid_incumbents: list[dict[str, Any]] = []
    for player in current_ir:
        status = _normalized_status(player.get("injury_status"))
        incumbent_status_counts[status] = incumbent_status_counts.get(status, 0) + 1
        if status not in IR_INCUMBENT_ALLOWED_STATUSES:
            invalid_incumbents.append({
                "espn_id": _finite_int(player.get("espn_id")),
                "name": player.get("name"),
                "position": player.get("position"),
                "injury_status": status,
            })

    blockers: list[str] = []
    if active_capacity <= 0:
        blockers.append("ACTIVE_ROSTER_CAPACITY_MISSING_OR_ZERO")
    if len(active) > active_capacity:
        blockers.append("ACTIVE_ROSTER_OVER_CAPACITY")
    if len(current_ir) > ir_capacity:
        blockers.append("IR_ROSTER_OVER_CAPACITY")
    if invalid_incumbents:
        blockers.append("INELIGIBLE_CURRENT_IR_OCCUPANT_BLOCKS_ACQUISITIONS")

    add_allowed = not blockers
    move_capacity = min(open_ir, len(move_candidates)) if add_allowed else 0
    direct_capacity = open_active if add_allowed else 0
    potential_add_capacity = direct_capacity + move_capacity

    compatible_count = sum(
        1
        for player in roster
        if any(str(slot).strip().upper() in IR_SLOT_NAMES for slot in (player.get("eligible_slots") or []))
    )

    return {
        "schema_version": 1,
        "authority": "ESPN_IR_ROSTER_STATE_V001",
        "platform_rule_source": ESPN_IR_RULE_SOURCE,
        "platform_ir_rule": ESPN_IR_RULE,
        "roster_rows": len(roster),
        "active_roster_capacity": active_capacity,
        "active_roster_occupancy": len(active),
        "open_active_roster_slots": open_active,
        "ir_capacity": ir_capacity,
        "current_ir_occupancy": len(current_ir),
        "open_ir_slots": open_ir,
        "current_ir_status_counts": dict(sorted(incumbent_status_counts.items())),
        "invalid_current_ir_occupants": invalid_incumbents,
        "new_acquisitions_blocked_by_ir_state": bool(invalid_incumbents),
        "ir_move_candidates": move_candidates,
        "ir_move_candidate_count": len(move_candidates),
        "direct_open_slot_add_capacity": direct_capacity,
        "ir_move_plus_add_capacity": move_capacity,
        "potential_add_capacity": potential_add_capacity,
        "direct_open_slot_available": bool(direct_capacity > 0),
        "ir_move_plus_add_available": bool(move_capacity > 0),
        "position_counts_total_roster": _position_counts(roster),
        "position_headroom_total_roster": _position_headroom(roster, league),
        "ir_compatible_roster_players": compatible_count,
        "eligible_slots_used_for_ir_eligibility": False,
        "multiweek_absence_horizon_supported": False,
        "blockers": blockers,
        "status": "PASS" if not blockers else "BLOCKED",
        "notes": [
            "IR slot compatibility is not current IR eligibility.",
            "Current move-to-IR eligibility uses normalized ESPN injury_status only.",
            "Current IR occupants with QUESTIONABLE/DOUBTFUL may remain stashed under ESPN rules; a healthy/no-designation IR occupant blocks new acquisitions.",
            "This authority represents current roster capacity and legal state transitions only; it does not infer return week or authorize season-value recommendations.",
        ],
    }


def evaluate_ir_roster_state(
    snapshot: Mapping[str, Any],
    league: Mapping[str, Any],
    *,
    team_name: str | None = None,
    team_id: int | None = None,
) -> dict[str, Any]:
    team = resolve_team(dict(snapshot), team_name=team_name, team_id=team_id)
    out = build_ir_roster_state(team, league)
    out["team_id"] = _finite_int(team.get("team_id"))
    out["team_name"] = team.get("name")
    return out
