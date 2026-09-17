from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .league import team_slot_for_overall_pick, user_overall_picks
from .live_draft import add_dynamic_values, available_board, is_user_pick
from .roster_utility import add_roster_marginal_values, diversified_candidate_pool
from .full_rollout import evaluate_candidates_full_rollout

SIM_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DST"]
POS_TO_CODE = {p: i for i, p in enumerate(SIM_POSITIONS)}


@dataclass(frozen=True)
class FastTurnGeometry:
    current_pick: int
    next_user_pick: int | None
    opponent_picks: tuple[int, ...]

    @property
    def gap(self) -> int:
        return len(self.opponent_picks)

    @property
    def is_short(self) -> bool:
        return self.gap <= 2


def turn_geometry(state) -> FastTurnGeometry:
    if not is_user_pick(state):
        raise ValueError(f"Next pick {state.next_overall} is not the user's pick.")
    user_picks = user_overall_picks(
        state.num_teams, state.rounds, state.user_draft_slot
    )
    future = [p for p in user_picks if p > state.next_overall]
    nxt = min(future) if future else None
    if nxt is None:
        return FastTurnGeometry(state.next_overall, None, tuple())
    return FastTurnGeometry(
        state.next_overall,
        nxt,
        tuple(range(state.next_overall + 1, nxt)),
    )


def _copy_state(state):
    from .draft_state import DraftState
    return DraftState.from_dict(state.to_dict())


def _record_candidate(state, row: pd.Series):
    state.record_pick(
        str(int(row["espn_id"])),
        str(row["name"]),
        str(row["position"]),
        str(row.get("nfl_team") or ""),
        espn_id=int(row["espn_id"]),
    )


def _normal_survival_array(x: float, means: np.ndarray, sigmas: np.ndarray) -> np.ndarray:
    # N is only a few hundred. math.erfc is more portable than depending on scipy.
    out = np.empty_like(means, dtype=float)
    root2 = math.sqrt(2.0)
    for i, (m, s) in enumerate(zip(means, sigmas)):
        if not np.isfinite(m) or not np.isfinite(s) or s <= 0:
            out[i] = np.nan
        else:
            out[i] = 0.5 * math.erfc((x - float(m)) / (float(s) * root2))
    return out


def hazard_array(means: np.ndarray, sigmas: np.ndarray, pick: int, floor: float) -> np.ndarray:
    lo = _normal_survival_array(float(pick) - 0.5, means, sigmas)
    hi = _normal_survival_array(float(pick) + 0.5, means, sigmas)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = 1.0 - hi / lo
    h = np.where(np.isfinite(h), h, 0.0)
    h = np.clip(h, 0.0, 1.0)
    return np.maximum(h, float(floor))


def _slot_position_counts(state, slot: int) -> np.ndarray:
    counts = np.zeros(len(SIM_POSITIONS), dtype=float)
    for p in state.roster_for_slot(slot):
        code = POS_TO_CODE.get(p.get("position"))
        if code is not None:
            counts[code] += 1.0
    return counts


def _need_vector(
    state,
    slot: int,
    pos_codes: np.ndarray,
    league: dict,
    strength: float,
    extra_position_code: int | None = None,
) -> np.ndarray:
    counts = _slot_position_counts(state, slot)
    if extra_position_code is not None:
        counts[int(extra_position_code)] += 1.0

    maxima_cfg = league.get("position_maximums", {})
    roster_cfg = league.get("roster", {})
    weights_by_pos = np.ones(len(SIM_POSITIONS), dtype=float)
    for pos, code in POS_TO_CODE.items():
        maximum = float(maxima_cfg.get(pos, 99))
        current = counts[code]
        if current >= maximum:
            weights_by_pos[code] = 0.0
            continue
        target = float(roster_cfg.get(pos, 0))
        if pos in {"RB", "WR", "TE"}:
            target += 0.35 * float(roster_cfg.get("FLEX", 0))
        deficit = max(target - current, 0.0)
        weights_by_pos[code] = max(0.05, 1.0 + float(strength) * deficit)
    return weights_by_pos[pos_codes]


def _candidate_dynamic_board(board: pd.DataFrame, state, candidate: pd.Series, model: dict):
    candidate_state = _copy_state(state)
    _record_candidate(candidate_state, candidate)
    avail = available_board(board, candidate_state)
    dcfg = model["draft_value"]
    lcfg = model["live_draft"]
    dyn, _ = add_dynamic_values(
        avail,
        candidate_state,
        dcfg["expected_rostered_counts"],
        scarcity_lookahead=int(dcfg["scarcity_lookahead_players"]),
        scarcity_weight=float(lcfg["scarcity_weight"]),
    )
    return candidate_state, dyn


def _array_view(df: pd.DataFrame):
    value_col = (
        "roster_marginal_value"
        if "roster_marginal_value" in df.columns
        else "dynamic_draft_value"
    )
    valid = (
        df["position"].isin(SIM_POSITIONS)
        & df["market_pick_mean"].notna()
        & df["market_pick_sigma"].notna()
        & df[value_col].notna()
    )
    g = df[valid].copy().reset_index(drop=True)
    return g, {
        "ids": g["espn_id"].astype(int).to_numpy(),
        "names": g["name"].astype(str).to_numpy(),
        "positions": g["position"].astype(str).to_numpy(),
        "pos_codes": np.array([POS_TO_CODE[p] for p in g["position"]], dtype=int),
        "means": g["market_pick_mean"].to_numpy(float),
        "sigmas": g["market_pick_sigma"].to_numpy(float),
        "values": g[value_col].to_numpy(float),
    }


def _short_turn_distribution(
    dyn: pd.DataFrame,
    candidate_state,
    opponent_picks: tuple[int, ...],
    league: dict,
    model: dict,
) -> dict:
    """Exact/near-exact short-turn contingency using at most two opponent picks.

    Dynamic player values are frozen over the 1-2 pick horizon after the user's
    candidate is selected. Opponent selection probabilities remain sequential
    and team-need aware. With only two intervening picks, the best option at the
    next user turn can only be among the top three current dynamic values.
    """
    g, a = _array_view(dyn)
    n = len(g)
    if n == 0:
        return {
            "option_mean": 0.0,
            "option_sd": 0.0,
            "best_name": None,
            "best_prob": 0.0,
            "contingencies": [],
        }

    order = np.argsort(-a["values"])
    top = order[: min(len(opponent_picks) + 1, n)]

    if len(opponent_picks) == 0:
        idx = int(top[0])
        return {
            "option_mean": float(a["values"][idx]),
            "option_sd": 0.0,
            "best_name": str(a["names"][idx]),
            "best_prob": 1.0,
            "contingencies": [(str(a["names"][idx]), 1.0)],
        }

    lcfg = model["live_draft"]
    strength = float(lcfg["opponent_need_strength"])
    floor = float(lcfg["market_hazard_floor"])

    p1 = int(opponent_picks[0])
    _, _, slot1 = team_slot_for_overall_pick(p1, candidate_state.num_teams)
    w1 = hazard_array(a["means"], a["sigmas"], p1, floor)
    w1 *= _need_vector(candidate_state, slot1, a["pos_codes"], league, strength)
    total1 = float(w1.sum())
    if total1 <= 0:
        w1 = np.ones(n, dtype=float) / n
    else:
        w1 /= total1

    best_probs: dict[int, float] = {int(t): 0.0 for t in top}

    if len(opponent_picks) == 1:
        top0 = int(top[0])
        top1 = int(top[1]) if len(top) > 1 else top0
        for i in range(n):
            pi = float(w1[i])
            if i == top0:
                best_probs[top1] = best_probs.get(top1, 0.0) + pi
            else:
                best_probs[top0] = best_probs.get(top0, 0.0) + pi
    else:
        p2 = int(opponent_picks[1])
        _, _, slot2 = team_slot_for_overall_pick(p2, candidate_state.num_teams)
        h2 = hazard_array(a["means"], a["sigmas"], p2, floor)

        # Need vectors for the second pick depend only on the first selected
        # player's position if the same fantasy team owns both picks.
        need2_by_first_pos = {}
        for first_pos_code in range(len(SIM_POSITIONS)):
            extra = first_pos_code if slot1 == slot2 else None
            need2_by_first_pos[first_pos_code] = _need_vector(
                candidate_state, slot2, a["pos_codes"], league, strength,
                extra_position_code=extra,
            )

        # At most two removals => next-turn best must be among top three.
        top_list = [int(x) for x in top]
        if len(top_list) < 3:
            top_list.extend([top_list[-1]] * (3 - len(top_list)))

        for i in range(n):
            pi = float(w1[i])
            if pi <= 0:
                continue
            first_pos = int(a["pos_codes"][i])
            w2 = h2 * need2_by_first_pos[first_pos]
            denom = float(w2.sum() - w2[i])
            remaining_top = [t for t in top_list if t != i]
            if not remaining_top:
                continue
            best0 = int(remaining_top[0])
            best1 = int(remaining_top[1]) if len(remaining_top) > 1 else best0
            if denom <= 0:
                best_probs[best0] = best_probs.get(best0, 0.0) + pi
                continue
            p_remove_best0 = float(w2[best0] / denom) if best0 != i else 0.0
            p_remove_best0 = float(np.clip(p_remove_best0, 0.0, 1.0))
            best_probs[best0] = best_probs.get(best0, 0.0) + pi * (1.0 - p_remove_best0)
            best_probs[best1] = best_probs.get(best1, 0.0) + pi * p_remove_best0

    # Normalize tiny floating-point drift.
    total = sum(best_probs.values())
    if total > 0:
        best_probs = {k: v / total for k, v in best_probs.items()}

    pairs = sorted(best_probs.items(), key=lambda kv: kv[1], reverse=True)
    vals = np.array([a["values"][idx] for idx, _ in pairs], dtype=float)
    probs = np.array([p for _, p in pairs], dtype=float)
    option_mean = float(np.sum(vals * probs)) if len(vals) else 0.0
    option_var = float(np.sum(((vals - option_mean) ** 2) * probs)) if len(vals) else 0.0
    best_idx, best_prob = pairs[0] if pairs else (None, 0.0)
    contingencies = [
        (str(a["names"][idx]), float(prob))
        for idx, prob in pairs[:3]
    ]
    return {
        "option_mean": option_mean,
        "option_sd": math.sqrt(max(option_var, 0.0)),
        "best_name": str(a["names"][best_idx]) if best_idx is not None else None,
        "best_prob": float(best_prob),
        "contingencies": contingencies,
    }


# Acklam inverse-normal approximation, vectorized with NumPy.
def _norm_ppf(u: np.ndarray) -> np.ndarray:
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


def _norm_cdf_scalar(z: float) -> float:
    return 0.5 * (1.0 + math.erf(float(z) / math.sqrt(2.0)))


def _sample_standard_normal_lower_tail(
    rng: np.random.Generator,
    a: float,
    size: int,
) -> np.ndarray:
    """Sample Z~N(0,1) conditional on Z>=a without scipy.

    Inverse-CDF sampling is used in the ordinary range. For extreme positive
    truncation, where floating-point CDF values round to 1, use Robert's
    exponential rejection sampler for the normal tail.
    """
    if a <= 5.0:
        f = _norm_cdf_scalar(a)
        f = min(max(f, 0.0), 1.0 - 1e-15)
        u = f + (1.0 - f) * rng.random(size)
        return _norm_ppf(u)

    alpha = 0.5 * (a + math.sqrt(a * a + 4.0))
    out = np.empty(size, dtype=float)
    filled = 0
    while filled < size:
        batch = max((size - filled) * 2, 32)
        z = a + rng.exponential(scale=1.0 / alpha, size=batch)
        accept = rng.random(batch) <= np.exp(-0.5 * (z - alpha) ** 2)
        accepted = z[accept]
        take = min(len(accepted), size - filled)
        if take:
            out[filled:filled + take] = accepted[:take]
            filled += take
    return out


def sample_conditional_draft_times(
    rng: np.random.Generator,
    means: np.ndarray,
    sigmas: np.ndarray,
    current_pick: int,
    simulations: int,
) -> np.ndarray:
    """Samples of X|X>=current-0.5 for market draft-time normals."""
    n = len(means)
    lower = float(current_pick) - 0.5
    out = np.empty((simulations, n), dtype=float)
    for j, (m, s) in enumerate(zip(means, sigmas)):
        if not np.isfinite(m) or not np.isfinite(s) or s <= 0:
            out[:, j] = np.inf
            continue
        a = (lower - float(m)) / float(s)
        z = _sample_standard_normal_lower_tail(rng, a, simulations)
        out[:, j] = float(m) + float(s) * z
    return out


def _fast_long_distribution(
    dyn: pd.DataFrame,
    current_pick: int,
    gap: int,
    simulations: int,
    rng: np.random.Generator,
) -> dict:
    """Array-based market rollout for long gaps.

    Each available player's latent future selection pick is sampled from its
    market distribution conditional on already being available now. The next
    `gap` lowest sampled draft times are treated as opponent selections. This
    deliberately omits team-specific need modifiers; Deep mode retains them.
    """
    g, a = _array_view(dyn)
    n = len(g)
    if n == 0 or gap <= 0:
        if n == 0:
            return {"option_mean": 0.0, "option_sd": 0.0, "best_name": None, "best_prob": 0.0}
        idx = int(np.argmax(a["values"]))
        return {"option_mean": float(a["values"][idx]), "option_sd": 0.0,
                "best_name": str(a["names"][idx]), "best_prob": 1.0}

    k = min(int(gap), max(n - 1, 1))
    draws = sample_conditional_draft_times(
        rng, a["means"], a["sigmas"], current_pick, simulations
    )
    selected = np.argpartition(draws, kth=k-1, axis=1)[:, :k]

    # Copying a ~1000x400 matrix is cheap and drastically faster than DataFrame
    # state reconstruction inside nested Python loops.
    future_values = np.broadcast_to(a["values"], (simulations, n)).copy()
    rows = np.arange(simulations)[:, None]
    future_values[rows, selected] = -np.inf
    best_idx = np.argmax(future_values, axis=1)
    best_values = future_values[np.arange(simulations), best_idx]

    valid = np.isfinite(best_values)
    if not np.any(valid):
        return {"option_mean": 0.0, "option_sd": 0.0, "best_name": None, "best_prob": 0.0}
    best_idx = best_idx[valid]
    best_values = best_values[valid]
    uniq, counts = np.unique(best_idx, return_counts=True)
    j = int(np.argmax(counts))
    common_idx = int(uniq[j])
    return {
        "option_mean": float(np.mean(best_values)),
        "option_sd": float(np.std(best_values, ddof=1)) if len(best_values) > 1 else 0.0,
        "best_name": str(a["names"][common_idx]),
        "best_prob": float(counts[j] / len(best_idx)),
    }


def evaluate_candidates_fast(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    simulations: int | None = None,
    seed: int | None = None,
    candidate_limit: int | None = None,
    market_order_ids: np.ndarray | None = None,
    bank_info: dict | None = None,
) -> pd.DataFrame:
    """Low-latency full-draft recommendation with next-turn explanation.

    The ranking objective is expected FINAL roster utility through round 16.
    The legacy short/long one-turn engines are retained only to explain what is
    likely to remain at the user's next selection.
    """
    started = time.perf_counter()
    if not is_user_pick(state):
        raise ValueError(f"Next pick {state.next_overall} belongs to another draft slot.")

    fast_cfg = model.get("full_rollout", {})
    nsim = int(simulations or fast_cfg.get("fast_simulations", 220))
    limit = int(candidate_limit or fast_cfg.get("candidate_limit", 10))
    seed = int(model["live_draft"]["random_seed"] if seed is None else seed)

    full = evaluate_candidates_full_rollout(
        board, state, league, model,
        simulations=nsim,
        seed=seed,
        candidate_limit=limit,
        deep=False,
        market_order_ids=market_order_ids,
    )
    if len(full) == 0:
        return full

    # Build the current dynamic table once so each full-rollout candidate can
    # get the familiar next-turn contingency explanation.
    draft_cfg = model["draft_value"]
    live_cfg = model["live_draft"]
    available = available_board(board, state)
    current_dyn, _ = add_dynamic_values(
        available,
        state,
        draft_cfg["expected_rostered_counts"],
        scarcity_lookahead=int(draft_cfg["scarcity_lookahead_players"]),
        scarcity_weight=float(live_cfg["scarcity_weight"]),
    )
    current_dyn = add_roster_marginal_values(current_dyn, board, state, league, model)
    by_id = {
        int(row["espn_id"]): row
        for _, row in current_dyn[current_dyn["espn_id"].notna()].iterrows()
    }
    geom = turn_geometry(state)
    explain_rng = np.random.default_rng(seed + 99173)

    rows = []
    for _, full_row in full.iterrows():
        pid = int(full_row["espn_id"])
        cand = by_id.get(pid)
        if cand is None:
            rows.append(dict(full_row))
            continue
        candidate_state, dyn_after_candidate = _candidate_dynamic_board(
            board, state, cand, model
        )
        dyn_after_candidate = add_roster_marginal_values(
            dyn_after_candidate, board, candidate_state, league, model
        )
        if geom.is_short:
            dist = _short_turn_distribution(
                dyn_after_candidate, candidate_state,
                geom.opponent_picks, league, model,
            )
            engine = "SHORT-EXACT+CONDITIONED-FULL" if market_order_ids is not None else "SHORT-EXACT+FULL"
        else:
            # Explanation only: a much smaller market sample is sufficient
            # because it does not drive the ranking objective anymore.
            explain_n = min(max(nsim, 80), 300)
            dist = _fast_long_distribution(
                dyn_after_candidate,
                candidate_state.next_overall,
                geom.gap,
                explain_n,
                explain_rng,
            )
            engine = "FAST-CONDITIONED" if market_order_ids is not None else "FAST-FULL"

        rec = dict(full_row)
        if bank_info:
            rec.update({
                "deep_bank_particles": bank_info.get("particles"),
                "deep_bank_ess": bank_info.get("ess"),
                "deep_bank_ess_fraction": bank_info.get("ess_fraction"),
                "deep_bank_anchor_pick": bank_info.get("anchor_pick"),
                "deep_bank_conditioned_through": bank_info.get("conditioned_through"),
                "deep_bank_selected_branch_name": bank_info.get("selected_branch_name"),
                "deep_bank_degraded": bank_info.get("degraded"),
                "deep_bank_fresh_fraction": bank_info.get("fresh_fraction"),
            })
        rec.update({
            "next_turn_option_mean": float(dist.get("option_mean", 0.0)),
            "next_turn_option_sd": float(dist.get("option_sd", 0.0)),
            "most_common_best_next": dist.get("best_name"),
            "p_most_common_best_next": float(dist.get("best_prob", 0.0)),
            "engine": engine,
            "opponent_picks_to_next": geom.gap,
        })
        for j, (name, prob) in enumerate(dist.get("contingencies", [])[:3], start=1):
            rec[f"contingency_{j}_name"] = name
            rec[f"contingency_{j}_prob"] = float(prob)
        rows.append(rec)

    out = pd.DataFrame(rows).sort_values(
        ["mc_objective", "final_roster_utility_mean", "immediate_draft_value"],
        ascending=[False, False, False],
    )
    out["elapsed_seconds"] = time.perf_counter() - started
    return out

