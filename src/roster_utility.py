from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .league import user_overall_picks


CORE_POSITIONS = ["QB", "RB", "WR", "TE"]
SPECIALIST_POSITIONS = ["K", "DST"]
DRAFT_POSITIONS = CORE_POSITIONS + SPECIALIST_POSITIONS
FLEX_POSITIONS = {"RB", "WR", "TE"}


def _norm_name(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "", str(name).lower().strip())
    for suffix in ("jr", "sr", "ii", "iii", "iv"):
        if s.endswith(suffix) and len(s) > len(suffix) + 2:
            s = s[:-len(suffix)]
            break
    return s


def replacement_map_from_dynamic(dyn: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    for pos in CORE_POSITIONS:
        g = dyn[dyn["position"].eq(pos)]
        vals = pd.to_numeric(g.get("dynamic_replacement_ppg"), errors="coerce").dropna()
        out[pos] = float(vals.iloc[0]) if len(vals) else 0.0
    return out


def user_roster_rows(board: pd.DataFrame, state) -> pd.DataFrame:
    """Resolve the user's already-drafted core players into model rows."""
    id_lookup = {}
    namepos_lookup = {}
    for _, row in board.iterrows():
        pos = str(row.get("position") or "")
        if pos not in CORE_POSITIONS:
            continue
        try:
            pid = int(row.get("espn_id"))
            id_lookup.setdefault(pid, row)
        except (TypeError, ValueError):
            pass
        namepos_lookup.setdefault((_norm_name(row.get("name", "")), pos), row)

    rows = []
    for pick in state.roster_for_slot(state.user_draft_slot):
        pos = str(pick.get("position") or "")
        if pos not in CORE_POSITIONS:
            continue

        raw = pick.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = pick.get("player_id")
        row = None
        try:
            row = id_lookup.get(int(raw))
        except (TypeError, ValueError):
            row = None

        if row is None:
            name = pick.get("player_name") or pick.get("name") or ""
            row = namepos_lookup.get((_norm_name(name), pos))
        if row is None:
            continue

        try:
            ppg = float(row.get("latent_mean_ppg"))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(ppg):
            continue
        try:
            key = int(row.get("espn_id"))
        except (TypeError, ValueError):
            key = f"legacy:{_norm_name(row.get('name',''))}:{pos}"
        rows.append({
            "key": key,
            "name": str(row.get("name", "")),
            "position": pos,
            "latent_mean_ppg": ppg,
        })

    return pd.DataFrame(rows, columns=["key", "name", "position", "latent_mean_ppg"])


def _lineup_value_entries(entries: list[tuple[object, str, float]], league: dict) -> tuple[float, set[object]]:
    roster_cfg = league.get("roster", {})
    by_pos = {p: [] for p in CORE_POSITIONS}
    for key, pos, advantage in entries:
        if pos in by_pos:
            by_pos[pos].append((float(advantage), key))
    for pos in CORE_POSITIONS:
        by_pos[pos].sort(key=lambda x: x[0], reverse=True)

    selected: set[object] = set()
    total = 0.0
    for pos in CORE_POSITIONS:
        n = int(roster_cfg.get(pos, 0))
        for advantage, key in by_pos[pos][:max(n, 0)]:
            selected.add(key)
            total += max(float(advantage), 0.0)

    flex_n = int(roster_cfg.get("FLEX", 0))
    if flex_n > 0:
        flex = []
        for pos in FLEX_POSITIONS:
            for advantage, key in by_pos[pos]:
                if key not in selected:
                    flex.append((float(advantage), key))
        flex.sort(key=lambda x: x[0], reverse=True)
        for advantage, key in flex[:flex_n]:
            selected.add(key)
            total += max(float(advantage), 0.0)

    return float(total), selected


def lineup_value(roster_rows: pd.DataFrame, replacement: dict[str, float], league: dict) -> tuple[float, set[object]]:
    if roster_rows is None or len(roster_rows) == 0:
        return 0.0, set()
    entries = []
    for row in roster_rows.itertuples(index=False):
        pos = str(row.position)
        if pos not in CORE_POSITIONS:
            continue
        try:
            ppg = float(row.latent_mean_ppg)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(ppg):
            continue
        advantage = max(ppg - float(replacement.get(pos, 0.0)), 0.0)
        entries.append((row.key, pos, advantage))
    return _lineup_value_entries(entries, league)


def _position_counts(roster_rows: pd.DataFrame, state) -> dict[str, int]:
    counts = {p: 0 for p in DRAFT_POSITIONS}
    if roster_rows is not None and len(roster_rows):
        raw = roster_rows["position"].value_counts().to_dict()
        for p in CORE_POSITIONS:
            counts[p] = int(raw.get(p, 0))
    for pick in state.roster_for_slot(state.user_draft_slot):
        pos = str(pick.get("position") or "")
        if pos in SPECIALIST_POSITIONS:
            counts[pos] += 1
    return counts


def _remaining_user_picks(state) -> int:
    picks = user_overall_picks(state.num_teams, state.rounds, state.user_draft_slot)
    return sum(1 for p in picks if p >= state.next_overall)


def _active_roster_capacity(league: dict) -> int:
    """Drafted roster capacity excluding IR/reserve-only slots."""
    roster = league.get("roster", {})
    return int(sum(
        int(v)
        for k, v in roster.items()
        if str(k).upper() not in {"IR", "RESERVE"}
    ))


def _core_roster_capacity(
    league: dict,
    required_specialists: dict[str, int],
    draft_rounds: int | None = None,
) -> int:
    """Number of draftable QB/RB/WR/TE slots.

    The configured active roster size is preferred when it agrees with the
    snake draft length. Some synthetic/legacy configs omit BENCH while the
    draft still correctly declares the full number of rounds, so in a mismatch
    the draft length is the authoritative total number of drafted roster slots.
    """
    configured = _active_roster_capacity(league)
    if draft_rounds is not None and int(draft_rounds) > 0:
        rounds = int(draft_rounds)
        total = configured if configured == rounds else rounds
    else:
        total = configured
    required = int(sum(max(int(v), 0) for v in required_specialists.values()))
    return max(total - required, 0)


def _specialist_state(
    state,
    league: dict,
    model: dict,
    counts: dict[str, int],
):
    scfg = model.get("specialists")
    if not scfg:
        required = {p: 0 for p in SPECIALIST_POSITIONS}
        missing = {p: 0 for p in SPECIALIST_POSITIONS}
        remaining = _remaining_user_picks(state)
        core_capacity = int(state.rounds)
        core_count = int(sum(int(counts.get(p, 0)) for p in CORE_POSITIONS))
        core_open = max(core_capacity - core_count, 0)
        return required, missing, 0, remaining, core_capacity, core_open, False

    required = {
        p: int(scfg.get("required_per_roster", {}).get(p, 1))
        for p in SPECIALIST_POSITIONS
    }
    missing = {
        p: max(required[p] - int(counts.get(p, 0)), 0)
        for p in SPECIALIST_POSITIONS
    }
    unfilled = int(sum(missing.values()))
    remaining = _remaining_user_picks(state)

    core_capacity = _core_roster_capacity(league, required, state.rounds)
    core_count = int(sum(int(counts.get(p, 0)) for p in CORE_POSITIONS))
    core_open = max(core_capacity - core_count, 0)

    if bool(scfg.get("draft_only_when_core_filled", False)):
        # Bench-aware default: K/DST are suppressed until every non-specialist
        # roster slot has been filled. The feasibility constraint below still
        # guarantees the required specialist slots cannot be missed.
        active = core_open == 0
    else:
        active = remaining <= (
            unfilled + int(scfg.get("activation_extra_picks", 0))
        )

    return (
        required, missing, unfilled, remaining,
        core_capacity, core_open, active,
    )


def add_roster_marginal_values(dyn: pd.DataFrame, board: pd.DataFrame, state, league: dict, model: dict) -> pd.DataFrame:
    """Attach user-roster-aware utility, including K/DST endgame feasibility."""
    out = dyn.copy()
    replacement = replacement_map_from_dynamic(out)
    roster = user_roster_rows(board, state)
    counts = _position_counts(roster, state)
    (
        required,
        missing_spec,
        unfilled_spec,
        remaining_user,
        core_capacity,
        core_slots_open,
        specialists_active,
    ) = _specialist_state(state, league, model, counts)
    required_core = {
        p: int(league.get("roster", {}).get(p, 0))
        for p in CORE_POSITIONS
    }
    enforce_core_minimums = core_capacity >= sum(required_core.values())

    base_entries = []
    for row in roster.itertuples(index=False):
        pos = str(row.position)
        advantage = max(float(row.latent_mean_ppg) - float(replacement.get(pos, 0.0)), 0.0)
        base_entries.append((row.key, pos, advantage))
    current_lineup, _ = _lineup_value_entries(base_entries, league)

    rcfg = model.get("roster_utility", {})
    bench_weight = float(rcfg.get("bench_option_weight", 0.25))
    depth_decay = float(rcfg.get("bench_depth_decay", 0.60))
    maxima = league.get("position_maximums", {})
    roster_cfg = league.get("roster", {})

    lineup_gains=[]; bench_values=[]; marginal_values=[]; candidate_starts=[]
    legal=[]; user_counts=[]; feasible_flags=[]; specialist_flags=[]
    core_capacity_values=[]; core_open_values=[]

    for row in out.itertuples(index=False):
        pos = str(row.position)
        count = counts.get(pos, 0)
        user_counts.append(count)
        max_pos = int(maxima.get(pos, 99))

        core_capacity_values.append(core_capacity)
        core_open_values.append(core_slots_open)

        if pos in SPECIALIST_POSITIONS:
            is_legal = (
                specialists_active
                and count < required.get(pos, 1)
                and missing_spec.get(pos, 0) > 0
            )
        else:
            # Core players can only be added while an active non-specialist
            # roster slot remains. This makes BENCH capacity explicit.
            is_legal = (
                pos in CORE_POSITIONS
                and count < max_pos
                and core_slots_open > 0
            )

        missing_after = unfilled_spec - (1 if pos in SPECIALIST_POSITIONS and is_legal else 0)
        picks_after = max(remaining_user - 1, 0)
        specialist_feasible = picks_after >= missing_after

        # Core starter feasibility: never spend so many core roster slots on
        # depth that QB/RB/RB/WR/WR/TE can no longer be completed.
        if pos in CORE_POSITIONS and is_legal and enforce_core_minimums:
            missing_core_after = 0
            for req_pos in CORE_POSITIONS:
                after_count = int(counts.get(req_pos, 0)) + (1 if req_pos == pos else 0)
                missing_core_after += max(required_core[req_pos] - after_count, 0)
            core_open_after = max(core_slots_open - 1, 0)
            core_feasible = core_open_after >= missing_core_after
        else:
            core_feasible = True

        feasible = bool(specialist_feasible and core_feasible)
        feasible_flags.append(feasible)
        specialist_flags.append(bool(pos in SPECIALIST_POSITIONS and specialists_active))
        is_legal = bool(is_legal and feasible)
        legal.append(is_legal)

        if not is_legal:
            lineup_gains.append(float("-inf")); bench_values.append(0.0); marginal_values.append(float("-inf")); candidate_starts.append(False)
            continue

        if pos in SPECIALIST_POSITIONS:
            try:
                specialist_value = max(float(row.dynamic_vorp_ppg), 0.0)
            except (TypeError, ValueError):
                specialist_value = 0.0
            lineup_gains.append(specialist_value); bench_values.append(0.0); marginal_values.append(specialist_value); candidate_starts.append(True)
            continue

        pid = int(row.espn_id)
        ppg = float(row.latent_mean_ppg)
        advantage = max(ppg - float(replacement.get(pos, 0.0)), 0.0)
        after_lineup, selected = _lineup_value_entries(base_entries + [(pid, pos, advantage)], league)
        gain = max(float(after_lineup - current_lineup), 0.0)
        try:
            raw_vorp = max(float(row.dynamic_vorp_ppg), 0.0)
        except (TypeError, ValueError):
            raw_vorp = 0.0
        residual = max(raw_vorp - gain, 0.0)
        base_slots = int(roster_cfg.get(pos, 0))
        bench_depth = max(count - base_slots, 0)
        bench = bench_weight * residual * (depth_decay ** bench_depth)
        marginal = gain + bench
        lineup_gains.append(gain); bench_values.append(bench); marginal_values.append(marginal); candidate_starts.append(pid in selected)

    out["user_position_count"] = user_counts
    out["core_roster_capacity"] = core_capacity_values
    out["core_roster_slots_open"] = core_open_values
    out["roster_future_feasible"] = feasible_flags
    out["specialist_active"] = specialist_flags
    out["roster_candidate_legal"] = legal
    out["roster_lineup_gain_ppg"] = lineup_gains
    out["roster_bench_option_value"] = bench_values
    out["roster_marginal_value"] = marginal_values
    out["candidate_in_best_lineup"] = candidate_starts
    return out


def diversified_candidate_pool(valued: pd.DataFrame, limit: int, model: dict) -> pd.DataFrame:
    g = valued[
        valued["roster_candidate_legal"].astype(bool)
        & pd.to_numeric(valued["roster_marginal_value"], errors="coerce").notna()
        & np.isfinite(pd.to_numeric(valued["roster_marginal_value"], errors="coerce"))
    ].copy()
    if len(g) == 0:
        return g
    g = g.sort_values(["roster_marginal_value","espn_adp"], ascending=[False,True], na_position="last")
    limit=max(int(limit),1)
    floor=int(model.get("roster_utility",{}).get("candidate_floor_per_position",2))

    positions_present=[p for p in CORE_POSITIONS if bool((g["position"]==p).any())]
    if "specialist_active" in g.columns:
        for p in SPECIALIST_POSITIONS:
            if bool((g["position"].eq(p)&g["specialist_active"].astype(bool)).any()):
                positions_present.append(p)

    effective_floor=min(floor,max(limit//len(positions_present),1)) if positions_present else 0
    selected=[]
    for pos in positions_present:
        for idx in g[g["position"].eq(pos)].head(effective_floor).index:
            if idx not in selected and len(selected)<limit:
                selected.append(idx)
    for idx in g.index:
        if len(selected)>=limit: break
        if idx not in selected: selected.append(idx)
    return g.loc[selected].sort_values(["roster_marginal_value","espn_adp"],ascending=[False,True],na_position="last")
