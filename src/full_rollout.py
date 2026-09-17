from __future__ import annotations

import math
import time
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .league import team_slot_for_overall_pick, user_overall_picks
from .live_draft import add_dynamic_values, available_board, drafted_espn_ids, is_user_pick
from .season_utility import season_roster_utility
from .roster_utility import (
    CORE_POSITIONS,
    FLEX_POSITIONS,
    SPECIALIST_POSITIONS,
    add_roster_marginal_values,
    diversified_candidate_pool,
    replacement_map_from_dynamic,
)

SIM_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DST"]
POS_TO_CODE = {p: i for i, p in enumerate(SIM_POSITIONS)}
CODE_TO_POS = {i: p for p, i in POS_TO_CODE.items()}


@dataclass
class PreparedRollout:
    ids: np.ndarray
    names: np.ndarray
    positions: np.ndarray
    pos_codes: np.ndarray
    ppg: np.ndarray
    sd: np.ndarray
    vorp: np.ndarray
    means: np.ndarray
    sigmas: np.ndarray
    adp: np.ndarray
    eligible: np.ndarray
    id_to_index: dict[int, int]
    replacement: dict[str, float]
    teams: np.ndarray = field(default_factory=lambda: np.array([], dtype=object))
    bye_weeks: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.int8))


def _norm_cdf(z: float) -> float:
    return 0.5 * math.erfc(-float(z) / math.sqrt(2.0))


def _norm_ppf(u: np.ndarray) -> np.ndarray:
    """Acklam inverse-normal approximation, vectorized and scipy-free."""
    u = np.clip(np.asarray(u, dtype=float), 1e-12, 1.0 - 1e-12)
    a = np.array([-3.969683028665376e+01, 2.209460984245205e+02,
                  -2.759285104469687e+02, 1.383577518672690e+02,
                  -3.066479806614716e+01, 2.506628277459239e+00])
    b = np.array([-5.447609879822406e+01, 1.615858368580409e+02,
                  -1.556989798598866e+02, 6.680131188771972e+01,
                  -1.328068155288572e+01])
    c = np.array([-7.784894002430293e-03, -3.223964580411365e-01,
                  -2.400758277161838e+00, -2.549732539343734e+00,
                   4.374664141464968e+00, 2.938163982698783e+00])
    d = np.array([7.784695709041462e-03, 3.224671290700398e-01,
                  2.445134137142996e+00, 3.754408661907416e+00])
    plow = 0.02425
    phigh = 1.0 - plow
    x = np.empty_like(u)
    low = u < plow
    high = u > phigh
    mid = ~(low | high)
    if np.any(low):
        q = np.sqrt(-2.0 * np.log(u[low]))
        x[low] = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                 ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    if np.any(high):
        q = np.sqrt(-2.0 * np.log(1.0-u[high]))
        x[high] = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                  ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    if np.any(mid):
        q = u[mid] - 0.5
        r = q*q
        x[mid] = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
                 (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    return x


def _sample_tail_standard_normal(rng: np.random.Generator, lower: float, size: int) -> np.ndarray:
    if lower <= 5.0:
        f = min(max(_norm_cdf(lower), 0.0), 1.0 - 1e-15)
        return _norm_ppf(f + (1.0 - f) * rng.random(size))

    # Robert's exponential rejection sampler for extreme lower-tail truncation.
    alpha = 0.5 * (lower + math.sqrt(lower * lower + 4.0))
    out = np.empty(size, dtype=float)
    filled = 0
    while filled < size:
        batch = max((size - filled) * 2, 32)
        z = lower + rng.exponential(scale=1.0 / alpha, size=batch)
        accept = rng.random(batch) <= np.exp(-0.5 * (z - alpha) ** 2)
        accepted = z[accept]
        take = min(len(accepted), size - filled)
        if take:
            out[filled:filled + take] = accepted[:take]
            filled += take
    return out


def sample_market_orders(
    rng: np.random.Generator,
    means: np.ndarray,
    sigmas: np.ndarray,
    current_pick_after_selection: int,
    simulations: int,
) -> np.ndarray:
    """Sample complete conditional market orders from the current draft state."""
    n = len(means)
    lower_pick = float(current_pick_after_selection) - 0.5
    draws = np.full((simulations, n), np.inf, dtype=float)
    for j, (m, s) in enumerate(zip(means, sigmas)):
        if not np.isfinite(m) or not np.isfinite(s) or s <= 0:
            continue
        a = (lower_pick - float(m)) / float(s)
        z = _sample_tail_standard_normal(rng, a, simulations)
        draws[:, j] = float(m) + float(s) * z
    return np.argsort(draws, axis=1)


def _bool_eligible(series: pd.Series) -> np.ndarray:
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy(bool)


def _prepare_rollout(board: pd.DataFrame, state, league: dict, model: dict) -> tuple[PreparedRollout, pd.DataFrame]:
    # Recompute core replacement from the current state, while preserving K/DST
    # specialist replacement values already present on the live board.
    avail = available_board(board, state)
    dcfg = model["draft_value"]
    lcfg = model["live_draft"]
    dyn, _ = add_dynamic_values(
        avail,
        state,
        dcfg["expected_rostered_counts"],
        scarcity_lookahead=int(dcfg["scarcity_lookahead_players"]),
        scarcity_weight=float(lcfg["scarcity_weight"]),
    )
    dyn = add_roster_marginal_values(dyn, board, state, league, model)

    work = board.copy()
    work = work[work["position"].isin(SIM_POSITIONS) & work["espn_id"].notna()].copy()
    work["espn_id"] = pd.to_numeric(work["espn_id"], errors="coerce").astype("Int64")
    work = work[work["espn_id"].notna()].drop_duplicates("espn_id", keep="first").reset_index(drop=True)

    # Dynamic replacement values come from current available rows. Join them
    # back onto the full board so already-drafted user players can be scored.
    repl_by_pos = replacement_map_from_dynamic(dyn)
    for pos in SPECIALIST_POSITIONS:
        vals = pd.to_numeric(
            dyn.loc[dyn["position"].eq(pos), "dynamic_replacement_ppg"],
            errors="coerce",
        ).dropna()
        if len(vals):
            repl_by_pos[pos] = float(vals.iloc[0])
        else:
            if "dynamic_replacement_ppg" in work.columns:
                raw = pd.to_numeric(
                    work.loc[work["position"].eq(pos), "dynamic_replacement_ppg"],
                    errors="coerce",
                ).dropna()
            else:
                raw = pd.Series(dtype=float)
            repl_by_pos[pos] = float(raw.iloc[0]) if len(raw) else 0.0

    ppg = pd.to_numeric(work.get("latent_mean_ppg"), errors="coerce").to_numpy(float)
    # Specialists created from ESPN projection already use latent_mean_ppg.
    ppg = np.where(np.isfinite(ppg), ppg, 0.0)
    sd = pd.to_numeric(work.get("latent_mean_sd_ppg"), errors="coerce").to_numpy(float)
    sd = np.where(np.isfinite(sd), sd, 0.0)
    positions = work["position"].astype(str).to_numpy()
    vorp = np.array([
        max(float(ppg_i) - float(repl_by_pos.get(pos, 0.0)), 0.0)
        for ppg_i, pos in zip(ppg, positions)
    ], dtype=float)

    means = pd.to_numeric(work.get("market_pick_mean"), errors="coerce").to_numpy(float)
    sigmas = pd.to_numeric(work.get("market_pick_sigma"), errors="coerce").to_numpy(float)
    adp = pd.to_numeric(work.get("espn_adp"), errors="coerce").to_numpy(float)
    eligible = _bool_eligible(work["draft_eligible"]) if "draft_eligible" in work.columns else np.ones(len(work), dtype=bool)
    ids = work["espn_id"].astype(int).to_numpy()
    names = work["name"].astype(str).to_numpy()
    teams = work.get("nfl_team", pd.Series("", index=work.index)).fillna("").astype(str).str.upper().to_numpy()
    bye_map = {str(k).upper(): int(v) for k, v in league.get("bye_weeks_2026", {}).items()}
    bye_weeks = np.array([int(bye_map.get(str(t).upper(), 0)) for t in teams], dtype=np.int8)
    pos_codes = np.array([POS_TO_CODE[p] for p in positions], dtype=np.int8)
    id_to_index = {int(pid): i for i, pid in enumerate(ids)}

    prepared = PreparedRollout(
        ids=ids,
        names=names,
        teams=teams,
        bye_weeks=bye_weeks,
        positions=positions,
        pos_codes=pos_codes,
        ppg=ppg,
        sd=sd,
        vorp=vorp,
        means=means,
        sigmas=sigmas,
        adp=adp,
        eligible=eligible,
        id_to_index=id_to_index,
        replacement=repl_by_pos,
    )
    return prepared, dyn


def _user_roster_indices(prep: PreparedRollout, state) -> list[int]:
    out = []
    for pick in state.roster_for_slot(state.user_draft_slot):
        raw = pick.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = pick.get("player_id")
        try:
            idx = prep.id_to_index.get(int(raw))
        except (TypeError, ValueError):
            idx = None
        if idx is not None:
            out.append(int(idx))
    return out


def _team_position_counts(state) -> np.ndarray:
    counts = np.zeros((state.num_teams + 1, len(SIM_POSITIONS)), dtype=np.int16)
    for pick in state.picks:
        code = POS_TO_CODE.get(str(pick.get("position") or ""))
        slot = int(pick.get("fantasy_team_slot") or 0)
        if code is not None and 1 <= slot <= state.num_teams:
            counts[slot, code] += 1
    return counts


def _required_specialists(model: dict) -> dict[str, int]:
    scfg = model.get("specialists")
    if not scfg:
        return {p: 0 for p in SPECIALIST_POSITIONS}
    return {
        p: int(scfg.get("required_per_roster", {}).get(p, 1))
        for p in SPECIALIST_POSITIONS
    }


def _core_capacity(state, league: dict, model: dict) -> int:
    required = sum(_required_specialists(model).values())
    roster_cfg = league.get("roster", {})
    active = sum(
        int(v) for k, v in roster_cfg.items()
        if str(k).upper() not in {"IR", "RESERVE"}
    )
    total = active if active == state.rounds else state.rounds
    return max(int(total) - int(required), 0)


def _roster_pos_counts(prep: PreparedRollout, roster: list[int]) -> np.ndarray:
    counts = np.zeros(len(SIM_POSITIONS), dtype=np.int16)
    for idx in roster:
        counts[int(prep.pos_codes[idx])] += 1
    return counts


def _legal_user_position(
    pos: str,
    counts: np.ndarray,
    core_count: int,
    core_capacity: int,
    league: dict,
    model: dict,
) -> bool:
    maxima = league.get("position_maximums", {})
    code = POS_TO_CODE[pos]
    if pos in CORE_POSITIONS:
        if not (core_count < core_capacity and counts[code] < int(maxima.get(pos, 99))):
            return False
        required_core = {
            p: int(league.get("roster", {}).get(p, 0))
            for p in CORE_POSITIONS
        }
        if core_capacity < sum(required_core.values()):
            return True  # synthetic/legacy configs with fewer rounds than starter slots
        missing_after = 0
        for req_pos in CORE_POSITIONS:
            req_code = POS_TO_CODE[req_pos]
            after_count = int(counts[req_code]) + (1 if req_pos == pos else 0)
            missing_after += max(required_core[req_pos] - after_count, 0)
        core_open_after = max(core_capacity - (core_count + 1), 0)
        return core_open_after >= missing_after

    required = _required_specialists(model)
    if core_count < core_capacity:
        return False
    return counts[code] < int(required.get(pos, 1))


def _starter_and_bench_utility(
    prep: PreparedRollout,
    roster: list[int],
    league: dict,
    model: dict,
) -> tuple[float, float, float, float, set[int]]:
    """Final/partial roster utility with bench value derived from roster exposure.

    Bench weights are not position-specific constants. They scale from how many
    starting slots each position can cover in this league (mandatory slots plus
    equal FLEX share), then decay for additional same-position depth.
    """
    roster_cfg = league.get("roster", {})
    selected: set[int] = set()
    starter_value = 0.0

    by_pos: dict[str, list[tuple[float, int]]] = {p: [] for p in CORE_POSITIONS}
    for idx in roster:
        pos = str(prep.positions[idx])
        if pos in CORE_POSITIONS:
            by_pos[pos].append((float(prep.vorp[idx]), int(idx)))
    for pos in CORE_POSITIONS:
        by_pos[pos].sort(reverse=True)
        n = int(roster_cfg.get(pos, 0))
        for val, idx in by_pos[pos][:n]:
            selected.add(idx)
            starter_value += max(val, 0.0)

    flex_n = int(roster_cfg.get("FLEX", 0))
    if flex_n > 0:
        flex_candidates = []
        for pos in FLEX_POSITIONS:
            for val, idx in by_pos[pos]:
                if idx not in selected:
                    flex_candidates.append((float(val), int(idx)))
        flex_candidates.sort(reverse=True)
        for val, idx in flex_candidates[:flex_n]:
            selected.add(idx)
            starter_value += max(val, 0.0)

    rcfg = model.get("full_rollout", {})
    bench_base = float(rcfg.get("bench_coverage_weight", 0.35))
    depth_decay = float(rcfg.get("bench_depth_decay", 0.55))

    flex_share = float(flex_n) / max(len(FLEX_POSITIONS), 1)
    exposure = {
        "QB": float(roster_cfg.get("QB", 0)),
        "RB": float(roster_cfg.get("RB", 0)) + flex_share,
        "WR": float(roster_cfg.get("WR", 0)) + flex_share,
        "TE": float(roster_cfg.get("TE", 0)) + flex_share,
    }
    max_exposure = max(max(exposure.values()), 1.0)

    # BENCH is one shared pool, not four independent positional benches.
    # First scale each reserve by how many starting/FLEX slots its position can
    # cover, then apply depth decay globally across the seven shared bench slots.
    # This avoids an artificial reset of the decay when switching positions
    # (which could otherwise make a third TE look better than a superior RB/WR
    # merely because it was "TE depth #2").
    bench_candidates = []
    for pos in CORE_POSITIONS:
        coverage = bench_base * exposure[pos] / max_exposure
        for _val, idx in by_pos[pos]:
            if idx in selected:
                continue
            bench_candidates.append((coverage * max(float(prep.vorp[idx]), 0.0), int(idx)))
    bench_candidates.sort(reverse=True)
    bench_value = 0.0
    for depth, (weighted_value, _idx) in enumerate(bench_candidates):
        bench_value += (depth_decay ** depth) * weighted_value

    specialist_value = 0.0
    for idx in roster:
        if str(prep.positions[idx]) in SPECIALIST_POSITIONS:
            specialist_value += max(float(prep.vorp[idx]), 0.0)

    # A final roster must be able to field every mandatory core starter. This
    # should normally be guaranteed by the rollout policy, but the explicit
    # penalty protects current-candidate edge cases and regression tests.
    counts = Counter(str(prep.positions[idx]) for idx in roster)
    required_total = sum(int(roster_cfg.get(pos, 0)) for pos in CORE_POSITIONS)
    if int(model.get("_rollout_core_capacity", required_total)) >= required_total:
        missing_required = sum(
            max(int(roster_cfg.get(pos, 0)) - int(counts.get(pos, 0)), 0)
            for pos in CORE_POSITIONS
        )
    else:
        missing_required = 0
    missing_penalty = float(rcfg.get("missing_required_starter_penalty", 25.0)) * missing_required

    # Risk is applied primarily to the starting lineup, where uncertainty most
    # directly affects weekly scoring. Specialists are included if rostered.
    risk_sq = 0.0
    for idx in selected:
        risk_sq += float(prep.sd[idx]) ** 2
    for idx in roster:
        if str(prep.positions[idx]) in SPECIALIST_POSITIONS:
            risk_sq += float(prep.sd[idx]) ** 2
    risk = math.sqrt(max(risk_sq, 0.0))
    risk_penalty = float(rcfg.get("starter_risk_penalty", 0.04)) * risk

    total = starter_value + bench_value + specialist_value - risk_penalty - missing_penalty
    return float(total), float(starter_value), float(bench_value), float(specialist_value), selected


def final_roster_utility(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
) -> dict:
    prep, _ = _prepare_rollout(board, state, league, model)
    roster = _user_roster_indices(prep, state)
    season = season_roster_utility(prep, roster, league, model)
    counts = Counter(str(prep.positions[idx]) for idx in roster)
    return {
        "utility": season["utility"],
        "starter_value": season["healthy_starter_value"],
        "bench_value": season["bench_insurance_value"],
        "specialist_value": 0.0,
        "season_value": season["season_value"],
        "expected_h2h_win_probability": season["expected_h2h_win_probability"],
        "bye_loss_ppg": season["bye_loss_ppg"],
        "weekly_floor_ppg": season["weekly_floor_ppg"],
        "weekly_std_ppg": season["weekly_std_ppg"],
        "worst_bye_week": season["worst_bye_week"],
        "max_starter_bye_conflict": season["max_starter_bye_conflict"],
        "playoff_bye_starters": season["playoff_bye_starters"],
        "starter_ids": season["starter_ids"],
        "position_counts": {p: int(counts.get(p, 0)) for p in SIM_POSITIONS},
    }


def _conditional_survival(mean: float, sigma: float, current_pick: int, target_pick: int) -> float:
    if not np.isfinite(mean) or not np.isfinite(sigma) or sigma <= 0 or target_pick <= current_pick:
        return 1.0
    root2 = math.sqrt(2.0)
    def surv(x):
        return 0.5 * math.erfc((float(x) - float(mean)) / (float(sigma) * root2))
    denom = surv(float(current_pick) - 0.5)
    if denom <= 1e-12:
        return 0.0
    return float(np.clip(surv(float(target_pick) - 0.5) / denom, 0.0, 1.0))


def _candidate_search_indices(
    prep: PreparedRollout,
    available: np.ndarray,
    roster: list[int],
    league: dict,
    model: dict,
    max_per_position: int,
) -> list[int]:
    counts = _roster_pos_counts(prep, roster)
    core_count = sum(int(counts[POS_TO_CODE[p]]) for p in CORE_POSITIONS)
    capacity = int(model.get("_rollout_core_capacity", 0))
    if capacity <= 0:
        # Filled by evaluate() before simulation, but retain a safe fallback.
        capacity = max(len(roster), 1)

    result: list[int] = []
    for pos in SIM_POSITIONS:
        if not _legal_user_position(pos, counts, core_count, capacity, league, model):
            continue
        code = POS_TO_CODE[pos]
        idxs = np.flatnonzero(available & (prep.pos_codes == code))
        if not len(idxs):
            continue
        # Static VORP is a cheap pre-filter. The exact partial-roster utility is
        # computed only for this small set.
        order = idxs[np.argsort(-prep.vorp[idxs])]
        result.extend(int(x) for x in order[:max_per_position])
    return result


def _choose_user_pick(
    prep: PreparedRollout,
    available: np.ndarray,
    roster: list[int],
    overall_pick: int,
    next_user_pick: int | None,
    league: dict,
    model: dict,
) -> int | None:
    rcfg = model.get("full_rollout", {})
    per_pos = int(rcfg.get("policy_candidates_per_position", 3))
    candidates = _candidate_search_indices(
        prep, available, roster, league, model, per_pos
    )
    if not candidates:
        return None

    base_total, *_ = _starter_and_bench_utility(prep, roster, league, model)
    urgency_weight = float(rcfg.get("policy_urgency_weight", 0.18))
    best_idx = None
    best_score = -np.inf
    for idx in candidates:
        total, *_ = _starter_and_bench_utility(prep, roster + [idx], league, model)
        gain = float(total - base_total)
        urgency = 0.0
        if next_user_pick is not None:
            p_survive = _conditional_survival(
                float(prep.means[idx]), float(prep.sigmas[idx]),
                int(overall_pick), int(next_user_pick),
            )
            urgency = urgency_weight * max(gain, 0.0) * (1.0 - p_survive)
        score = gain + urgency
        if score > best_score:
            best_score = score
            best_idx = int(idx)
    return best_idx


def _opponent_need_weight(
    pos: str,
    counts: np.ndarray,
    league: dict,
    strength: float,
) -> float:
    code = POS_TO_CODE[pos]
    maximum = int(league.get("position_maximums", {}).get(pos, 99))
    current = int(counts[code])
    if current >= maximum:
        return 0.0
    target = float(league.get("roster", {}).get(pos, 0))
    if pos in FLEX_POSITIONS:
        target += float(league.get("roster", {}).get("FLEX", 0)) / 3.0
    deficit = max(target - current, 0.0)
    return max(0.05, 1.0 + float(strength) * deficit)


def _opponent_position_max(pos: str, league: dict, model: dict) -> int:
    maximum = int(league.get("position_maximums", {}).get(pos, 99))
    if pos in SPECIALIST_POSITIONS and not bool(model.get("specialists", {}).get("backup_default", False)):
        return min(maximum, 1)
    return maximum


def _choose_opponent_pick(
    prep: PreparedRollout,
    available: np.ndarray,
    market_order: np.ndarray,
    team_counts: np.ndarray,
    slot: int,
    league: dict,
    model: dict,
    rng: np.random.Generator,
    deep: bool,
) -> int | None:
    if not deep:
        for idx in market_order:
            if not available[idx]:
                continue
            pos = str(prep.positions[idx])
            code = POS_TO_CODE[pos]
            maximum = _opponent_position_max(pos, league, model)
            if int(team_counts[slot, code]) < maximum:
                return int(idx)
        return None

    rcfg = model.get("full_rollout", {})
    lookahead = int(rcfg.get("deep_market_queue_lookahead", 12))
    temperature = float(rcfg.get("deep_queue_temperature", 5.0))
    strength = float(model.get("live_draft", {}).get("opponent_need_strength", 0.35))

    candidates = []
    queue_rank = []
    for idx in market_order:
        if not available[idx]:
            continue
        pos = str(prep.positions[idx])
        code = POS_TO_CODE[pos]
        if int(team_counts[slot, code]) >= _opponent_position_max(pos, league, model):
            continue
        queue_rank.append(len(candidates))
        candidates.append(int(idx))
        if len(candidates) >= lookahead:
            break
    if not candidates:
        return None

    weights = []
    for rank, idx in zip(queue_rank, candidates):
        pos = str(prep.positions[idx])
        need = _opponent_need_weight(pos, team_counts[slot], league, strength)
        market = math.exp(-float(rank) / max(temperature, 1e-6))
        weights.append(max(need * market, 1e-12))
    w = np.asarray(weights, dtype=float)
    w /= w.sum()
    return int(rng.choice(np.asarray(candidates, dtype=int), p=w))


def _simulate_one(
    prep: PreparedRollout,
    state,
    candidate_idx: int,
    market_order: np.ndarray,
    league: dict,
    model: dict,
    rng: np.random.Generator,
    deep: bool,
    availability_uniforms: np.ndarray | None = None,
) -> tuple[dict, list[int]]:
    drafted = drafted_espn_ids(state)
    available = prep.eligible.copy()
    for pid in drafted:
        idx = prep.id_to_index.get(int(pid))
        if idx is not None:
            available[idx] = False

    roster = _user_roster_indices(prep, state)
    available[candidate_idx] = False
    roster.append(int(candidate_idx))

    team_counts = _team_position_counts(state)
    team_counts[state.user_draft_slot, int(prep.pos_codes[candidate_idx])] += 1

    user_picks = set(user_overall_picks(state.num_teams, state.rounds, state.user_draft_slot))
    future_user = sorted(p for p in user_picks if p > state.next_overall)
    next_user_map = {}
    for i, p in enumerate(future_user):
        next_user_map[p] = future_user[i + 1] if i + 1 < len(future_user) else None

    for overall in range(state.next_overall + 1, state.total_picks + 1):
        _, _, slot = team_slot_for_overall_pick(overall, state.num_teams)
        if slot == state.user_draft_slot:
            idx = _choose_user_pick(
                prep, available, roster, overall, next_user_map.get(overall),
                league, model,
            )
            if idx is None:
                continue
            available[idx] = False
            roster.append(int(idx))
            team_counts[slot, int(prep.pos_codes[idx])] += 1
        else:
            idx = _choose_opponent_pick(
                prep, available, market_order, team_counts, slot,
                league, model, rng, deep,
            )
            if idx is None:
                continue
            available[idx] = False
            team_counts[slot, int(prep.pos_codes[idx])] += 1

    season = season_roster_utility(
        prep, roster, league, model, availability_uniforms=availability_uniforms
    )
    counts = Counter(str(prep.positions[idx]) for idx in roster)
    return {
        "utility": season["utility"],
        "starter_value": season["healthy_starter_value"],
        "bench_value": season["bench_insurance_value"],
        "specialist_value": 0.0,
        "season_value": season["season_value"],
        "expected_h2h_win_probability": season["expected_h2h_win_probability"],
        "bye_loss_ppg": season["bye_loss_ppg"],
        "weekly_floor_ppg": season["weekly_floor_ppg"],
        "weekly_std_ppg": season["weekly_std_ppg"],
        "worst_bye_week": season["worst_bye_week"],
        "max_starter_bye_conflict": season["max_starter_bye_conflict"],
        "playoff_bye_starters": season["playoff_bye_starters"],
        "counts": {p: int(counts.get(p, 0)) for p in SIM_POSITIONS},
        "starter_ids": season["starter_ids"],
    }, roster


def _market_order_ids_to_indices(prep: PreparedRollout, market_order_ids: np.ndarray) -> np.ndarray:
    """Map persisted ESPN-ID market orders into the current prepared array.

    Missing IDs are ignored and any newly-added prepared players are appended at
    the tail so a bank remains usable after harmless live-board refreshes.
    """
    raw = np.asarray(market_order_ids, dtype=np.int64)
    if raw.ndim != 2:
        raise ValueError("market_order_ids must be a 2D array")
    all_indices = np.arange(len(prep.ids), dtype=int)
    rows = []
    for ids in raw:
        seen = set()
        mapped = []
        for pid in ids:
            idx = prep.id_to_index.get(int(pid))
            if idx is not None and idx not in seen:
                mapped.append(int(idx))
                seen.add(int(idx))
        if len(mapped) < len(prep.ids):
            mapped.extend(int(i) for i in all_indices if int(i) not in seen)
        rows.append(mapped)
    return np.asarray(rows, dtype=int)



def evaluate_candidates_full_rollout(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    simulations: int | None = None,
    seed: int | None = None,
    candidate_limit: int | None = None,
    deep: bool = False,
    market_order_ids: np.ndarray | None = None,
    return_scenarios: bool = False,
):
    """Evaluate current-pick candidates by expected utility of the final roster."""
    started = time.perf_counter()
    if not is_user_pick(state):
        raise ValueError(f"Next pick {state.next_overall} belongs to another draft slot.")

    rcfg = model.get("full_rollout", {})
    nsim = int(simulations or (rcfg.get("deep_simulations", 80) if deep else rcfg.get("fast_simulations", 220)))
    limit = int(candidate_limit or rcfg.get("candidate_limit", 10))
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    rng = np.random.default_rng(seed)

    prep, current_dyn = _prepare_rollout(board, state, league, model)
    season_scenarios = int(model.get("season_utility", {}).get("availability_scenarios", 8))
    availability_uniforms = rng.random((season_scenarios, 17, len(prep.ids)))
    if market_order_ids is not None:
        market_orders = _market_order_ids_to_indices(prep, market_order_ids)
        nsim = int(len(market_orders))
        if nsim <= 0:
            raise ValueError("Conditioned market-order bank is empty")
    else:
        market_orders = None
    current_dyn = add_roster_marginal_values(current_dyn, board, state, league, model)
    candidates = diversified_candidate_pool(current_dyn, limit, model)
    if len(candidates) == 0:
        return pd.DataFrame()

    # Make core capacity available to the tight rollout policy without passing
    # another argument through every helper.
    model = dict(model)
    model["_rollout_core_capacity"] = _core_capacity(state, league, model)

    # Common random numbers across candidate branches reduce ranking noise.
    if market_orders is None:
        market_orders = sample_market_orders(
            rng, prep.means, prep.sigmas,
            current_pick_after_selection=state.next_overall + 1,
            simulations=nsim,
        )

    objective_sd_penalty = float(rcfg.get("objective_sd_penalty", 0.08))
    records = []
    for _, cand in candidates.iterrows():
        candidate_idx = prep.id_to_index.get(int(cand["espn_id"]))
        if candidate_idx is None:
            continue

        utilities = np.empty(nsim, dtype=float)
        starter_vals = np.empty(nsim, dtype=float)
        bench_vals = np.empty(nsim, dtype=float)
        spec_vals = np.empty(nsim, dtype=float)
        season_vals = np.empty(nsim, dtype=float)
        h2h_probs = np.empty(nsim, dtype=float)
        bye_losses = np.empty(nsim, dtype=float)
        weekly_floors = np.empty(nsim, dtype=float)
        weekly_stds = np.empty(nsim, dtype=float)
        bye_conflicts = np.empty(nsim, dtype=float)
        playoff_byes = np.empty(nsim, dtype=float)
        worst_weeks = np.empty(nsim, dtype=float)
        count_acc = {p: np.empty(nsim, dtype=float) for p in SIM_POSITIONS}

        # Candidate-specific RNG stream makes deep stochastic queue choices
        # reproducible while preserving shared market scenarios.
        branch_rng = np.random.default_rng(seed + int(cand["espn_id"]) % 1000003)
        for s in range(nsim):
            outcome, _ = _simulate_one(
                prep, state, int(candidate_idx), market_orders[s],
                league, model, branch_rng, deep, availability_uniforms,
            )
            utilities[s] = outcome["utility"]
            starter_vals[s] = outcome["starter_value"]
            bench_vals[s] = outcome["bench_value"]
            spec_vals[s] = outcome["specialist_value"]
            season_vals[s] = outcome["season_value"]
            h2h_probs[s] = outcome["expected_h2h_win_probability"]
            bye_losses[s] = outcome["bye_loss_ppg"]
            weekly_floors[s] = outcome["weekly_floor_ppg"]
            weekly_stds[s] = outcome["weekly_std_ppg"]
            bye_conflicts[s] = outcome["max_starter_bye_conflict"]
            playoff_byes[s] = outcome["playoff_bye_starters"]
            worst_weeks[s] = outcome["worst_bye_week"]
            for pos in SIM_POSITIONS:
                count_acc[pos][s] = outcome["counts"][pos]

        mean_u = float(np.mean(utilities))
        sd_u = float(np.std(utilities, ddof=1)) if nsim > 1 else 0.0
        objective = mean_u - objective_sd_penalty * sd_u
        record = {
            "espn_id": int(cand["espn_id"]),
            "name": cand["name"],
            "position": cand["position"],
            "nfl_team": cand.get("nfl_team"),
            "espn_adp": cand.get("espn_adp"),
            "tier": cand.get("tier"),
            "latent_mean_ppg": cand.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": cand.get("latent_mean_sd_ppg"),
            "dynamic_vorp_ppg": cand.get("dynamic_vorp_ppg"),
            "league_dynamic_value": cand.get("dynamic_draft_value"),
            "roster_lineup_gain_ppg": cand.get("roster_lineup_gain_ppg"),
            "roster_bench_option_value": cand.get("roster_bench_option_value"),
            "roster_marginal_value": cand.get("roster_marginal_value"),
            "candidate_in_best_lineup": cand.get("candidate_in_best_lineup"),
            "user_position_count": cand.get("user_position_count"),
            "immediate_draft_value": float(cand.get("roster_marginal_value", 0.0)),
            "final_roster_utility_mean": mean_u,
            "final_roster_utility_sd": sd_u,
            "final_starter_value_mean": float(np.mean(starter_vals)),
            "final_bench_value_mean": float(np.mean(bench_vals)),
            "final_specialist_value_mean": float(np.mean(spec_vals)),
            "final_season_value_mean": float(np.mean(season_vals)),
            "final_expected_h2h_win_probability_mean": float(np.mean(h2h_probs)),
            "final_bench_insurance_mean": float(np.mean(bench_vals)),
            "final_bye_loss_ppg_mean": float(np.mean(bye_losses)),
            "final_weekly_floor_ppg_mean": float(np.mean(weekly_floors)),
            "final_weekly_std_ppg_mean": float(np.mean(weekly_stds)),
            "final_max_starter_bye_conflict_mean": float(np.mean(bye_conflicts)),
            "final_playoff_bye_starters_mean": float(np.mean(playoff_byes)),
            "final_worst_bye_week_mode": int(Counter(int(x) for x in worst_weeks).most_common(1)[0][0]),
            "mc_objective": objective,
            "simulations": nsim,
            "engine": "DEEP-FULL" if deep else "FAST-FULL",
        }
        for pos in SIM_POSITIONS:
            record[f"expected_final_{pos}"] = float(np.mean(count_acc[pos]))
        records.append(record)

    out = pd.DataFrame(records)
    if len(out):
        out = out.sort_values(
            ["mc_objective", "final_roster_utility_mean", "immediate_draft_value"],
            ascending=[False, False, False],
        )
        out["elapsed_seconds"] = time.perf_counter() - started
    if return_scenarios:
        scenario_ids = prep.ids[market_orders]
        return out, scenario_ids
    return out
