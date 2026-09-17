from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CORE_POSITIONS = ("QB", "RB", "WR", "TE")
FLEX_POSITIONS = {"RB", "WR", "TE"}
SPECIAL_POSITIONS = ("K", "DST")

HARD_UNAVAILABLE_STATUSES = {
    "OUT", "IR", "PUP", "SUSPENDED", "EXEMPT",
    "COMMISSIONER_EXEMPT", "COMMISSIONERS_EXEMPT", "RESERVE",
    "NFI_RESERVE",
}
KNOWN_AVAILABILITY_STATUSES = {
    "ACTIVE", "NORMAL", "PROBABLE", "QUESTIONABLE", "DOUBTFUL",
    *HARD_UNAVAILABLE_STATUSES,
}
_STATUS_SEVERITY = {
    "ACTIVE": 0, "NORMAL": 0, "PROBABLE": 1,
    "QUESTIONABLE": 2, "DOUBTFUL": 3,
    "OUT": 4, "IR": 4, "PUP": 4, "SUSPENDED": 4, "EXEMPT": 4,
    "COMMISSIONER_EXEMPT": 4, "COMMISSIONERS_EXEMPT": 4,
    "RESERVE": 4, "NFI_RESERVE": 4,
}


@dataclass(frozen=True)
class LineupResult:
    rows: list[dict[str, Any]]
    total_projection: float
    total_expected: float
    missing_slots: list[str]


def load_snapshot(path: str | Path = "data/season_snapshots/latest.json") -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Season snapshot not found: {path}. Run `python fantasy.py season-sync` first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_team(snapshot: dict[str, Any], team_name: str | None = None,
                 team_id: int | None = None) -> dict[str, Any]:
    teams = snapshot.get("espn", {}).get("teams") or snapshot.get("teams") or []
    if team_id is not None:
        for team in teams:
            if int(team.get("team_id")) == int(team_id):
                return team
        raise ValueError(f"ESPN team_id {team_id} not present in snapshot")

    if team_name:
        wanted = " ".join(str(team_name).casefold().split())
        exact = [
            team for team in teams
            if " ".join(str(team.get("name") or "").casefold().split()) == wanted
        ]
        if len(exact) == 1:
            return exact[0]
        partial = [team for team in teams if wanted in str(team.get("name") or "").casefold()]
        if len(partial) == 1:
            return partial[0]
        if len(exact) > 1 or len(partial) > 1:
            raise ValueError(f"Team name is ambiguous: {team_name}")
        raise ValueError(f"Team not found in ESPN snapshot: {team_name}")

    if len(teams) == 1:
        return teams[0]
    names = ", ".join(f'{t.get("team_id")}:{t.get("name")}' for t in teams)
    raise ValueError(f"Specify --team or configure user_team_name. Available teams: {names}")


def _status_key(value: Any) -> str:
    text = str(value or "ACTIVE").strip().upper().replace(" ", "_")
    aliases = {
        "QUESTIONABLE": "QUESTIONABLE",
        "Q": "QUESTIONABLE",
        "DOUBTFUL": "DOUBTFUL",
        "D": "DOUBTFUL",
        "OUT": "OUT",
        "O": "OUT",
        "INJURY_RESERVE": "IR",
        "INJURED_RESERVE": "IR",
        "RESERVE_INJURED": "IR",
        "SUSPENDED": "SUSPENDED",
        "SUSPENSION": "SUSPENDED",
        "PUP": "PUP",
        "PROBABLE": "PROBABLE",
        "HEALTHY": "ACTIVE",
        "INACTIVE": "OUT",
        "COMMISSIONER'S_EXEMPT": "COMMISSIONER_EXEMPT",
        "COMMISSIONERS_EXEMPT_LIST": "COMMISSIONERS_EXEMPT",
        "COMMISSIONER_EXEMPT_LIST": "COMMISSIONER_EXEMPT",
        "NFI-R": "NFI_RESERVE",
        "NFI_R": "NFI_RESERVE",
        "RESERVE/NFI": "NFI_RESERVE",
    }
    return aliases.get(text, text)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    text = str(value).strip()
    return bool(text and text.casefold() not in {"nan", "none", "null", "-"})


def _known_status(value: Any) -> str | None:
    """Normalize only statuses that have an explicit availability meaning.

    Secondary feeds sometimes emit administrative/free-text values in injury fields.
    Those must never silently replace a recognized ESPN OUT/IR/etc. status.
    """
    if not _present(value):
        return None
    raw = str(value).strip().upper()
    if raw in {"NA", "N/A", "NOT_APPLICABLE", "NOT APPLICABLE", "NONE", "NULL", "-"}:
        return None
    status = _status_key(value)
    return status if status in KNOWN_AVAILABILITY_STATUSES else None


def status_observations(player: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, label in (
        ("official_injury_status", "NFL_OFFICIAL"),
        ("official_roster_availability_status", "NFL_OFFICIAL_ROSTER"),
        ("nflverse_availability_status", "NFLVERSE_ROSTER"),
        ("sleeper_injury_status", "SLEEPER"),
        ("injury_status", "ESPN"),
    ):
        status = _known_status(player.get(key))
        if status is not None:
            out[label] = status
    return out


def availability_status(player: dict[str, Any]) -> tuple[str, str]:
    """Return resolved availability status and provenance.

    NFL official status is authoritative. Until that feed is integrated, ESPN and
    Sleeper are reconciled conservatively: if recognized statuses disagree, use the
    more restrictive status rather than allowing an unknown/healthier secondary value
    to resurrect an OUT/IR/PUP/etc. player. Conflicts are surfaced by data-quality
    diagnostics instead of being hidden.
    """
    obs = status_observations(player)
    official = obs.get("NFL_OFFICIAL")
    if official is not None:
        return official, "NFL_OFFICIAL"

    official_roster = obs.get("NFL_OFFICIAL_ROSTER")
    if official_roster is not None:
        return official_roster, "NFL_OFFICIAL_ROSTER"

    # nflverse roster statuses such as PUP/RES/SUS/EXE are current NFL roster-state
    # observations. ACT is deliberately not mapped here because active-roster status
    # does not mean healthy for a specific week.
    roster_status = obs.get("NFLVERSE_ROSTER")
    if roster_status is not None:
        return roster_status, "NFLVERSE_ROSTER"

    sleeper = obs.get("SLEEPER")
    espn = obs.get("ESPN")
    if sleeper is not None and espn is not None:
        if sleeper == espn:
            return sleeper, "SLEEPER+ESPN"
        chosen_source, chosen = max(
            (("SLEEPER", sleeper), ("ESPN", espn)),
            key=lambda item: _STATUS_SEVERITY.get(item[1], -1),
        )
        return chosen, chosen_source
    if sleeper is not None:
        return sleeper, "SLEEPER"
    if espn is not None:
        return espn, "ESPN"
    return "ACTIVE", "DEFAULT"


def active_probability(player: dict[str, Any], model: dict[str, Any]) -> float:
    cfg = model.get("weekly_manager", {}).get("status_active_probability", {})
    status, _source = availability_status(player)
    defaults = {
        "ACTIVE": 0.995,
        "NORMAL": 0.995,
        "PROBABLE": 0.95,
        "QUESTIONABLE": 0.75,
        "DOUBTFUL": 0.15,
        "OUT": 0.0,
        "IR": 0.0,
        "PUP": 0.0,
        "SUSPENDED": 0.0,
        "EXEMPT": 0.0,
        "COMMISSIONER_EXEMPT": 0.0,
        "COMMISSIONERS_EXEMPT": 0.0,
        "RESERVE": 0.0,
    }
    if status in HARD_UNAVAILABLE_STATUSES:
        return 0.0
    try:
        value = float(cfg.get(status, defaults.get(status, 0.95)))
    except (TypeError, ValueError):
        value = defaults.get(status, 0.95)
    return min(max(value, 0.0), 1.0)


def _load_model_values(path: str | Path) -> dict[int, float]:
    path = Path(path)
    if not path.exists():
        return {}
    df = pd.read_csv(path, low_memory=False)
    if "espn_id" not in df.columns or "latent_mean_ppg" not in df.columns:
        return {}
    ids = pd.to_numeric(df["espn_id"], errors="coerce")
    vals = pd.to_numeric(df["latent_mean_ppg"], errors="coerce")
    out: dict[int, float] = {}
    for pid, val in zip(ids, vals):
        if pd.notna(pid) and pd.notna(val):
            out[int(pid)] = float(val)
    return out


def enrich_roster_projections(
    roster: list[dict[str, Any]],
    values_path: str | Path = "data/processed/player_values_2026.csv",
    league: dict[str, Any] | None = None,
    week: int | None = None,
) -> list[dict[str, Any]]:
    """Attach a usable weekly projection while preserving ESPN provenance.

    ESPN sometimes emits a literal 0.0 placeholder before a weekly projection is
    available for an otherwise eligible player.  Zero remains authoritative for a
    known bye or hard-unavailable player; otherwise we fall back to our latent PPG
    (then ESPN season/17) and flag the fallback explicitly.
    """
    model_values = _load_model_values(values_path)
    bye_weeks = (league or {}).get("bye_weeks_2026", {})
    enriched: list[dict[str, Any]] = []
    for raw in roster:
        p = dict(raw)
        weekly = p.get("weekly_projection")
        try:
            weekly_value = float(weekly) if weekly is not None else None
        except (TypeError, ValueError):
            weekly_value = None
        p["espn_weekly_projection_raw"] = weekly_value

        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            pid = -1

        status, status_source = availability_status(p)
        p["availability_status"] = status
        p["availability_status_source"] = status_source
        hard_unavailable = status in HARD_UNAVAILABLE_STATUSES
        is_bye = False
        if week is not None and p.get("nfl_team") in bye_weeks:
            try:
                is_bye = int(bye_weeks[p.get("nfl_team")]) == int(week)
            except (TypeError, ValueError):
                is_bye = False
        p["is_bye_week"] = is_bye

        projection: float | None = weekly_value
        source = "ESPN_WEEKLY" if weekly_value is not None else "MISSING"
        suspicious_zero = weekly_value is not None and weekly_value <= 0.0 and not hard_unavailable and not is_bye

        if weekly_value is None or suspicious_zero:
            suffix = "ZERO_FALLBACK" if suspicious_zero else "FALLBACK"
            if pid in model_values and float(model_values[pid]) > 0.0:
                projection = float(model_values[pid])
                source = f"MODEL_LATENT_PPG_{suffix}"
            else:
                season = p.get("season_projection")
                try:
                    season_value = float(season) if season is not None else None
                except (TypeError, ValueError):
                    season_value = None
                if season_value is not None and season_value > 0.0:
                    projection = season_value / 17.0
                    source = f"ESPN_SEASON_DIV17_{suffix}"
                elif weekly_value is not None:
                    projection = weekly_value
                    source = "ESPN_WEEKLY_ZERO_UNRESOLVED"
                else:
                    projection = 0.0
                    source = "MISSING"

        if hard_unavailable or is_bye:
            # Keep projection as a conditional-on-playing talent estimate if ESPN supplies
            # one; availability handling zeroes expected value separately.  For a true bye,
            # however, there is no legal game outcome this week.
            if is_bye:
                projection = 0.0
                source = "BYE"

        p["projection_points"] = float(projection or 0.0)
        p["projection_source"] = source
        enriched.append(p)
    return enriched


def optimize_lineup(roster: list[dict[str, Any]], league: dict[str, Any], model: dict[str, Any],
                    force_active: set[int] | None = None,
                    force_inactive: set[int] | None = None,
                    use_expected_availability: bool = True) -> LineupResult:
    force_active = set(force_active or set())
    force_inactive = set(force_inactive or set())
    cfg = league.get("roster", {})

    pool: list[dict[str, Any]] = []
    for p0 in roster:
        p = dict(p0)
        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            pid = -1
        status, status_source = availability_status(p)
        p["availability_status"] = status
        p["availability_status_source"] = status_source
        # v0.27 operational rosters may already carry an evidence-conditioned
        # current-week P(active). Preserve that posterior rather than silently
        # reverting to the generic status prior inside the lineup optimizer.
        try:
            enriched_prob = float(p.get("active_probability")) if p.get("active_probability") is not None else None
        except (TypeError, ValueError):
            enriched_prob = None
        prob = min(max(enriched_prob, 0.0), 1.0) if enriched_prob is not None else active_probability(p, model)
        # A scenario may force Q/D active, but it must never resurrect a hard OUT/IR/etc.
        # A bye is also a true weekly unavailability state, not a zero-point starter.
        hard_unavailable = status in HARD_UNAVAILABLE_STATUSES or bool(p.get("is_bye_week"))
        if pid in force_active and not hard_unavailable:
            prob = 1.0
        if pid in force_inactive or hard_unavailable:
            prob = 0.0
        projection = float(p.get("projection_points") or 0.0)
        try:
            workload_factor = float(p.get("expected_workload_given_active", 1.0))
        except (TypeError, ValueError):
            workload_factor = 1.0
        workload_factor = min(max(workload_factor, 0.0), 1.0)
        p["active_probability"] = prob
        p["expected_workload_given_active"] = workload_factor
        p["expected_points"] = (
            projection * prob * workload_factor
            if use_expected_availability
            else projection * (1.0 if prob > 0 else 0.0)
        )
        p["ranking_points"] = p["expected_points"] if use_expected_availability else projection
        pool.append(p)

    selected_ids: set[int] = set()
    rows: list[dict[str, Any]] = []
    missing: list[str] = []

    def candidates(position: str) -> list[dict[str, Any]]:
        return sorted(
            [p for p in pool if p.get("position") == position and int(p.get("espn_id") or -1) not in selected_ids
             and float(p.get("active_probability") or 0.0) > 0.0],
            key=lambda x: (float(x.get("ranking_points") or 0.0), float(x.get("projection_points") or 0.0)),
            reverse=True,
        )

    def choose(slot: str, eligible_positions: set[str] | None = None) -> None:
        if eligible_positions is None:
            eligible_positions = {slot}
        cand = sorted(
            [p for p in pool if p.get("position") in eligible_positions
             and int(p.get("espn_id") or -1) not in selected_ids
             and float(p.get("active_probability") or 0.0) > 0.0],
            key=lambda x: (float(x.get("ranking_points") or 0.0), float(x.get("projection_points") or 0.0)),
            reverse=True,
        )
        if not cand:
            missing.append(slot)
            return
        p = dict(cand[0])
        selected_ids.add(int(p.get("espn_id") or -1))
        p["assigned_slot"] = slot
        rows.append(p)

    for pos in CORE_POSITIONS:
        for _ in range(int(cfg.get(pos, 0))):
            choose(pos)
    for _ in range(int(cfg.get("FLEX", 0))):
        choose("FLEX", FLEX_POSITIONS)
    for pos in SPECIAL_POSITIONS:
        for _ in range(int(cfg.get(pos, 0))):
            choose(pos)

    # Preserve the canonical assigned_slot values used by existing code/tests while
    # adding unique display labels so a nine-slot lineup can never visually hide a
    # repeated RB/WR slot.  Completeness is also asserted whenever no slot is missing.
    seen: dict[str, int] = {}
    multiplicity = {
        pos: int(cfg.get(pos, 0))
        for pos in (*CORE_POSITIONS, *SPECIAL_POSITIONS)
    }
    multiplicity["FLEX"] = int(cfg.get("FLEX", 0))
    for row in rows:
        slot = str(row.get("assigned_slot") or "?")
        seen[slot] = seen.get(slot, 0) + 1
        row["display_slot"] = f"{slot}{seen[slot]}" if multiplicity.get(slot, 0) > 1 else slot

    expected_slots = sum(int(cfg.get(pos, 0)) for pos in (*CORE_POSITIONS, "FLEX", *SPECIAL_POSITIONS))
    if not missing and len(rows) != expected_slots:
        raise AssertionError(f"Lineup completeness failure: selected {len(rows)} of {expected_slots} required slots")

    return LineupResult(
        rows=rows,
        total_projection=float(sum(float(r.get("projection_points") or 0.0) for r in rows)),
        total_expected=float(sum(float(r.get("expected_points") or 0.0) for r in rows)),
        missing_slots=missing,
    )


def uncertain_players(roster: list[dict[str, Any]]) -> list[dict[str, Any]]:
    uncertain = {"QUESTIONABLE", "DOUBTFUL"}
    return [p for p in roster if availability_status(p)[0] in uncertain]


def build_lineup_scenarios(roster: list[dict[str, Any]], league: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    expected = optimize_lineup(roster, league, model, use_expected_availability=True)
    uncertain = uncertain_players(roster)
    uncertain_ids = {int(p["espn_id"]) for p in uncertain if p.get("espn_id") is not None}
    all_active = optimize_lineup(
        roster, league, model, force_active=uncertain_ids, use_expected_availability=False
    )

    contingencies: list[dict[str, Any]] = []
    for p in uncertain:
        try:
            pid = int(p.get("espn_id"))
        except (TypeError, ValueError):
            continue
        lineup = optimize_lineup(
            roster,
            league,
            model,
            force_active=uncertain_ids - {pid},
            force_inactive={pid},
            use_expected_availability=False,
        )
        contingencies.append({
            "player": p.get("name"),
            "espn_id": pid,
            "injury_status": p.get("official_injury_status") or p.get("injury_status"),
            "if_inactive": lineup,
        })
    return {
        "expected": expected,
        "all_uncertain_active": all_active,
        "contingencies": contingencies,
    }



def lineup_data_quality(roster: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for p in roster:
        source = str(p.get("projection_source") or "")
        if "ZERO_FALLBACK" in source:
            warnings.append(
                f'{p.get("name")}: ESPN weekly projection was 0.00; using {source}={float(p.get("projection_points") or 0):.2f}'
            )
        elif source in {"MISSING", "ESPN_WEEKLY_ZERO_UNRESOLVED"}:
            warnings.append(f'{p.get("name")}: no reliable weekly projection available')

        obs = status_observations(p)
        non_official = {k: v for k, v in obs.items() if k != "NFL_OFFICIAL"}
        if "NFL_OFFICIAL" not in obs and len(set(non_official.values())) > 1:
            resolved, resolved_source = availability_status(p)
            detail = ", ".join(f"{k}={v}" for k, v in non_official.items())
            warnings.append(
                f'{p.get("name")}: injury-status conflict ({detail}); using '
                f'{resolved}[{resolved_source}] until NFL official status is integrated'
            )
    return warnings

def find_week_opponent(snapshot: dict[str, Any], team_id: int) -> int | None:
    espn = snapshot.get("espn", snapshot)
    for matchup in espn.get("matchups") or []:
        home = matchup.get("home_team_id")
        away = matchup.get("away_team_id")
        if home == team_id:
            return away
        if away == team_id:
            return home
    return None
