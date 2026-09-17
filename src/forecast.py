from __future__ import annotations

import time
from collections import defaultdict

import numpy as np
import pandas as pd

from .draft_state import DraftState

from .fast_recommend import sample_conditional_draft_times
from .league import team_slot_for_overall_pick, user_overall_picks
from .full_rollout import (
    _choose_opponent_pick,
    _market_order_ids_to_indices,
    _prepare_rollout,
    _team_position_counts,
)
from .live_draft import drafted_espn_ids
from .roster_utility import add_roster_marginal_values, diversified_candidate_pool
from .live_draft import (
    add_dynamic_values,
    available_board,
    is_user_pick,
    simulate_to_next_user_pick,
)


def next_user_pick_from_state(state) -> int | None:
    picks = user_overall_picks(
        state.num_teams, state.rounds, state.user_draft_slot
    )
    future = [p for p in picks if p >= state.next_overall]
    return min(future) if future else None


def _current_dynamic(board: pd.DataFrame, state, league: dict, model: dict) -> pd.DataFrame:
    available = available_board(board, state)
    dcfg = model["draft_value"]
    lcfg = model["live_draft"]
    dyn, _ = add_dynamic_values(
        available,
        state,
        dcfg["expected_rostered_counts"],
        scarcity_lookahead=int(dcfg["scarcity_lookahead_players"]),
        scarcity_weight=float(lcfg["scarcity_weight"]),
    )
    return add_roster_marginal_values(dyn, board, state, league, model)


def _candidate_rows(dyn: pd.DataFrame, limit: int, model: dict) -> pd.DataFrame:
    return diversified_candidate_pool(dyn, int(limit), model).copy()


def forecast_next_user_pick_fast(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    simulations: int = 5000,
    seed: int | None = None,
    candidate_limit: int = 20,
) -> pd.DataFrame:
    """Vectorized off-turn forecast of the user's next draft board.

    This function is intentionally only for opponent turns. It conditions every
    market draft-time distribution on the player already being available at the
    current state, samples the intervening opponent selections, and aggregates:

      * P(available at target user pick)
      * P(best modeled option at target user pick)
      * current dynamic value as a fast target-value approximation

    Dynamic replacement values are frozen across the short forecast horizon in
    FAST mode. DEEP mode recomputes them after sequential opponent simulations.
    """
    started = time.perf_counter()
    if is_user_pick(state):
        raise ValueError("Fast forecast is for opponent turns; use recommendation mode on your turn.")

    target = next_user_pick_from_state(state)
    if target is None:
        return pd.DataFrame()

    gap = int(target - state.next_overall)
    if gap <= 0:
        raise ValueError("No opponent picks remain before the next user turn.")

    live_cfg = model["live_draft"]
    seed = int(live_cfg["random_seed"] if seed is None else seed)
    rng = np.random.default_rng(seed)
    nsim = max(int(simulations), 1)

    dyn = _current_dynamic(board, state, league, model)
    valid = (
        dyn["market_pick_mean"].notna()
        & dyn["market_pick_sigma"].notna()
        & dyn["roster_marginal_value"].notna()
    )
    g = dyn[valid].copy().reset_index(drop=True)
    if len(g) == 0:
        return pd.DataFrame()

    means = g["market_pick_mean"].to_numpy(float)
    sigmas = g["market_pick_sigma"].to_numpy(float)
    values = g["roster_marginal_value"].to_numpy(float)

    # Current next_overall is itself an opponent pick. If target=74 and
    # next_overall=72, opponent selections are 72 and 73 => gap=2.
    k = min(gap, max(len(g) - 1, 1))

    draws = sample_conditional_draft_times(
        rng, means, sigmas, state.next_overall, nsim
    )
    selected = np.argpartition(draws, kth=k - 1, axis=1)[:, :k]

    survives = np.ones((nsim, len(g)), dtype=bool)
    sim_rows = np.arange(nsim)[:, None]
    survives[sim_rows, selected] = False

    p_available = survives.mean(axis=0)

    future_values = np.broadcast_to(values, (nsim, len(g))).copy()
    future_values[~survives] = -np.inf
    best_idx = np.argmax(future_values, axis=1)
    best_counts = np.bincount(best_idx, minlength=len(g))
    p_best = best_counts / nsim

    candidates = _candidate_rows(g, candidate_limit, model)
    idx_by_id = {int(row["espn_id"]): i for i, row in g.iterrows()}

    records = []
    for _, row in candidates.iterrows():
        j = idx_by_id[int(row["espn_id"])]
        records.append({
            "analysis_mode": "forecast",
            "engine": "SHORT-FORECAST" if gap <= 2 else "FAST-FORECAST",
            "target_pick": int(target),
            "opponent_picks_to_target": gap,
            "espn_id": int(row["espn_id"]),
            "name": row["name"],
            "position": row["position"],
            "nfl_team": row.get("nfl_team"),
            "espn_adp": row.get("espn_adp"),
            "tier": row.get("tier"),
            "latent_mean_ppg": row.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": row.get("latent_mean_sd_ppg"),
            "target_value_estimate": float(row["roster_marginal_value"]),
            "p_available_target": float(p_available[j]),
            "p_best_target": float(p_best[j]),
            "forecast_score": float(p_available[j] * row["roster_marginal_value"]),
            "simulations": nsim,
        })

    out = pd.DataFrame(records)
    if len(out):
        out = out.sort_values(
            ["p_best_target", "forecast_score", "target_value_estimate"],
            ascending=[False, False, False],
        )
        out["elapsed_seconds"] = time.perf_counter() - started
    return out



def forecast_next_user_pick_conditioned(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    market_order_ids: np.ndarray,
    bank_info: dict,
    seed: int | None = None,
    candidate_limit: int = 20,
) -> pd.DataFrame:
    """Off-turn FAST forecast using the conditioned DEEP particle bank.

    The DEEP posterior supplies latent market-order scenarios. From the current
    *actual* state, each scenario advances only the intervening opponent picks;
    user-roster marginal values are frozen over this short forecast horizon for
    draft-clock latency, matching the FAST approximation.
    """
    started = time.perf_counter()
    if is_user_pick(state):
        raise ValueError("Conditioned forecast is for opponent turns.")
    target = next_user_pick_from_state(state)
    if target is None:
        return pd.DataFrame()
    gap = int(target - state.next_overall)
    if gap <= 0:
        return pd.DataFrame()

    prep, _ = _prepare_rollout(board, state, league, model)
    market_orders = _market_order_ids_to_indices(prep, market_order_ids)
    nsim = int(len(market_orders))
    if nsim <= 0:
        return pd.DataFrame()

    dyn = _current_dynamic(board, state, league, model)
    candidates = _candidate_rows(dyn, candidate_limit, model)
    if len(candidates) == 0:
        return pd.DataFrame()
    candidate_ids = [int(x) for x in candidates["espn_id"]]
    values = {
        int(r["espn_id"]): float(r["roster_marginal_value"])
        for _, r in candidates.iterrows()
    }
    meta = {int(r["espn_id"]): r for _, r in candidates.iterrows()}

    drafted = drafted_espn_ids(state)
    base_available = prep.eligible.copy()
    for pid in drafted:
        idx = prep.id_to_index.get(int(pid))
        if idx is not None:
            base_available[idx] = False
    base_counts = _team_position_counts(state)
    rng = np.random.default_rng(
        int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    )

    avail_counts = {pid: 0 for pid in candidate_ids}
    best_counts = {pid: 0 for pid in candidate_ids}
    for s in range(nsim):
        available = base_available.copy()
        team_counts = base_counts.copy()
        for overall in range(state.next_overall, target):
            _, _, slot = team_slot_for_overall_pick(overall, state.num_teams)
            idx = _choose_opponent_pick(
                prep, available, market_orders[s], team_counts, slot,
                league, model, rng, deep=False,
            )
            if idx is None:
                continue
            available[idx] = False
            team_counts[slot, int(prep.pos_codes[idx])] += 1

        survivors = []
        for pid in candidate_ids:
            idx = prep.id_to_index.get(pid)
            if idx is not None and available[idx]:
                avail_counts[pid] += 1
                survivors.append(pid)
        if survivors:
            best = max(survivors, key=lambda pid: values[pid])
            best_counts[best] += 1

    records = []
    for pid in candidate_ids:
        row = meta[pid]
        p_available = avail_counts[pid] / nsim
        p_best = best_counts[pid] / nsim
        rec = {
            "analysis_mode": "forecast",
            "engine": "SHORT-CONDITIONED-FORECAST" if gap <= 2 else "FAST-CONDITIONED-FORECAST",
            "target_pick": int(target),
            "opponent_picks_to_target": gap,
            "espn_id": pid,
            "name": row["name"],
            "position": row["position"],
            "nfl_team": row.get("nfl_team"),
            "espn_adp": row.get("espn_adp"),
            "tier": row.get("tier"),
            "latent_mean_ppg": row.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": row.get("latent_mean_sd_ppg"),
            "target_value_estimate": values[pid],
            "p_available_target": float(p_available),
            "p_best_target": float(p_best),
            "forecast_score": float(p_available * values[pid]),
            "simulations": nsim,
            "deep_bank_particles": bank_info.get("particles"),
            "deep_bank_ess": bank_info.get("ess"),
            "deep_bank_ess_fraction": bank_info.get("ess_fraction"),
            "deep_bank_anchor_pick": bank_info.get("anchor_pick"),
            "deep_bank_conditioned_through": bank_info.get("conditioned_through"),
            "deep_bank_selected_branch_name": bank_info.get("selected_branch_name"),
            "deep_bank_degraded": bank_info.get("degraded"),
            "deep_bank_fresh_fraction": bank_info.get("fresh_fraction"),
        }
        records.append(rec)
    out = pd.DataFrame(records)
    if len(out):
        out = out.sort_values(
            ["p_best_target", "forecast_score", "target_value_estimate"],
            ascending=[False, False, False],
        )
        out["elapsed_seconds"] = time.perf_counter() - started
    return out



def forecast_next_user_pick_deep_conditioned(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    market_order_ids: np.ndarray,
    bank_info: dict,
    seed: int | None = None,
    candidate_limit: int = 20,
) -> pd.DataFrame:
    """Team-aware off-turn DEEP forecast using posterior market scenarios."""
    started = time.perf_counter()
    if is_user_pick(state):
        raise ValueError("Conditioned deep forecast is for opponent turns.")
    target = next_user_pick_from_state(state)
    if target is None:
        return pd.DataFrame()
    gap = int(target - state.next_overall)
    if gap <= 0:
        return pd.DataFrame()

    live_cfg = model["live_draft"]
    draft_cfg = model["draft_value"]
    seed = int(live_cfg["random_seed"] if seed is None else seed)
    rng = np.random.default_rng(seed)

    prep, _ = _prepare_rollout(board, state, league, model)
    market_orders = _market_order_ids_to_indices(prep, market_order_ids)
    nsim = int(len(market_orders))
    if nsim <= 0:
        return pd.DataFrame()

    current_dyn = _current_dynamic(board, state, league, model)
    candidates = _candidate_rows(current_dyn, candidate_limit, model)
    candidate_ids = [int(x) for x in candidates["espn_id"]]
    candidate_meta = {int(r["espn_id"]): r for _, r in candidates.iterrows()}

    available_counts = defaultdict(int)
    best_counts = defaultdict(int)
    value_sums = defaultdict(float)
    value_counts = defaultdict(int)

    drafted = drafted_espn_ids(state)
    base_available = prep.eligible.copy()
    for pid in drafted:
        idx = prep.id_to_index.get(int(pid))
        if idx is not None:
            base_available[idx] = False
    base_counts = _team_position_counts(state)

    for s in range(nsim):
        available = base_available.copy()
        team_counts = base_counts.copy()
        future_state = DraftState.from_dict(state.to_dict())
        scenario_rng = np.random.default_rng(seed + 100003 + s)
        for overall in range(state.next_overall, target):
            _, _, slot = team_slot_for_overall_pick(overall, state.num_teams)
            idx = _choose_opponent_pick(
                prep, available, market_orders[s], team_counts, slot,
                league, model, scenario_rng, deep=True,
            )
            if idx is None:
                continue
            available[idx] = False
            team_counts[slot, int(prep.pos_codes[idx])] += 1
            future_state.record_pick(
                str(int(prep.ids[idx])), str(prep.names[idx]),
                str(prep.positions[idx]), "", espn_id=int(prep.ids[idx]),
            )

        remaining = available_board(board, future_state)
        if len(remaining) == 0:
            continue
        dyn, _ = add_dynamic_values(
            remaining, future_state,
            draft_cfg["expected_rostered_counts"],
            scarcity_lookahead=int(draft_cfg["scarcity_lookahead_players"]),
            scarcity_weight=float(live_cfg["scarcity_weight"]),
        )
        dyn = add_roster_marginal_values(dyn, board, future_state, league, model)
        dyn = dyn[dyn["roster_marginal_value"].notna()].copy()
        if len(dyn) == 0:
            continue

        ids_present = set(int(x) for x in dyn["espn_id"].dropna().astype(int))
        by_id = dyn.set_index(dyn["espn_id"].astype(int))
        for pid in candidate_ids:
            if pid in ids_present:
                available_counts[pid] += 1
                r = by_id.loc[pid]
                if isinstance(r, pd.DataFrame):
                    r = r.iloc[0]
                value_sums[pid] += float(r["roster_marginal_value"])
                value_counts[pid] += 1

        best = dyn.sort_values(
            ["roster_marginal_value", "espn_adp"],
            ascending=[False, True], na_position="last",
        ).iloc[0]
        best_counts[int(best["espn_id"])] += 1

    records = []
    for pid in candidate_ids:
        row = candidate_meta[pid]
        p_available = available_counts[pid] / nsim
        p_best = best_counts[pid] / nsim
        mean_value = (
            value_sums[pid] / value_counts[pid]
            if value_counts[pid] else float(row["roster_marginal_value"])
        )
        records.append({
            "analysis_mode": "forecast",
            "engine": "DEEP-CONDITIONED-FORECAST",
            "target_pick": int(target),
            "opponent_picks_to_target": gap,
            "espn_id": pid,
            "name": row["name"],
            "position": row["position"],
            "nfl_team": row.get("nfl_team"),
            "espn_adp": row.get("espn_adp"),
            "tier": row.get("tier"),
            "latent_mean_ppg": row.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": row.get("latent_mean_sd_ppg"),
            "target_value_estimate": float(mean_value),
            "p_available_target": float(p_available),
            "p_best_target": float(p_best),
            "forecast_score": float(p_available * mean_value),
            "simulations": nsim,
            "deep_bank_particles": bank_info.get("particles"),
            "deep_bank_ess": bank_info.get("ess"),
            "deep_bank_ess_fraction": bank_info.get("ess_fraction"),
            "deep_bank_anchor_pick": bank_info.get("anchor_pick"),
            "deep_bank_conditioned_through": bank_info.get("conditioned_through"),
            "deep_bank_selected_branch_name": bank_info.get("selected_branch_name"),
            "deep_bank_degraded": bank_info.get("degraded"),
            "deep_bank_reused_fraction": bank_info.get("reused_fraction"),
        })
    out = pd.DataFrame(records)
    if len(out):
        out = out.sort_values(
            ["p_best_target", "forecast_score", "target_value_estimate"],
            ascending=[False, False, False],
        )
        out["elapsed_seconds"] = time.perf_counter() - started
    return out


def forecast_next_user_pick_deep(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    simulations: int = 300,
    seed: int | None = None,
    candidate_limit: int = 20,
) -> pd.DataFrame:
    """Sequential team-need-aware off-turn forecast.

    Unlike FAST forecast, each rollout simulates opponent picks sequentially and
    recomputes dynamic replacement/scarcity at the target user pick.
    """
    started = time.perf_counter()
    if is_user_pick(state):
        raise ValueError("Deep forecast is for opponent turns; use recommendation mode on your turn.")

    target = next_user_pick_from_state(state)
    if target is None:
        return pd.DataFrame()

    gap = int(target - state.next_overall)
    if gap <= 0:
        raise ValueError("No opponent picks remain before the next user turn.")

    live_cfg = model["live_draft"]
    draft_cfg = model["draft_value"]
    seed = int(live_cfg["random_seed"] if seed is None else seed)
    rng = np.random.default_rng(seed)
    nsim = max(int(simulations), 1)

    current_dyn = _current_dynamic(board, state, league, model)
    candidates = _candidate_rows(current_dyn, candidate_limit, model)
    candidate_ids = [int(x) for x in candidates["espn_id"]]
    candidate_meta = {
        int(row["espn_id"]): row
        for _, row in candidates.iterrows()
    }

    available_counts = defaultdict(int)
    best_counts = defaultdict(int)
    value_sums = defaultdict(float)
    value_counts = defaultdict(int)

    for _ in range(nsim):
        remaining, future_state = simulate_to_next_user_pick(
            board, state, league, live_cfg, rng
        )
        if len(remaining) == 0:
            continue

        dyn, _ = add_dynamic_values(
            remaining,
            future_state,
            draft_cfg["expected_rostered_counts"],
            scarcity_lookahead=int(draft_cfg["scarcity_lookahead_players"]),
            scarcity_weight=float(live_cfg["scarcity_weight"]),
        )
        dyn = add_roster_marginal_values(
            dyn, board, future_state, league, model
        )
        if len(dyn) == 0:
            continue

        dyn = dyn[dyn["roster_marginal_value"].notna()].copy()
        if len(dyn) == 0:
            continue

        ids_present = set(int(x) for x in dyn["espn_id"].dropna().astype(int))
        for pid in candidate_ids:
            if pid in ids_present:
                available_counts[pid] += 1

        by_id = dyn.set_index(dyn["espn_id"].astype(int))
        for pid in candidate_ids:
            if pid in by_id.index:
                r = by_id.loc[pid]
                # Defensive against accidental duplicate index.
                if isinstance(r, pd.DataFrame):
                    r = r.iloc[0]
                value_sums[pid] += float(r["roster_marginal_value"])
                value_counts[pid] += 1

        best = dyn.sort_values(
            ["roster_marginal_value", "espn_adp"],
            ascending=[False, True],
            na_position="last",
        ).iloc[0]
        best_counts[int(best["espn_id"])] += 1

    records = []
    for pid in candidate_ids:
        row = candidate_meta[pid]
        navail = available_counts[pid]
        p_available = navail / nsim
        p_best = best_counts[pid] / nsim
        mean_value = (
            value_sums[pid] / value_counts[pid]
            if value_counts[pid] > 0
            else float(row["roster_marginal_value"])
        )
        records.append({
            "analysis_mode": "forecast",
            "engine": "DEEP-FORECAST",
            "target_pick": int(target),
            "opponent_picks_to_target": gap,
            "espn_id": pid,
            "name": row["name"],
            "position": row["position"],
            "nfl_team": row.get("nfl_team"),
            "espn_adp": row.get("espn_adp"),
            "tier": row.get("tier"),
            "latent_mean_ppg": row.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": row.get("latent_mean_sd_ppg"),
            "target_value_estimate": float(mean_value),
            "p_available_target": float(p_available),
            "p_best_target": float(p_best),
            "forecast_score": float(p_available * mean_value),
            "simulations": nsim,
        })

    out = pd.DataFrame(records)
    if len(out):
        out = out.sort_values(
            ["p_best_target", "forecast_score", "target_value_estimate"],
            ascending=[False, False, False],
        )
        out["elapsed_seconds"] = time.perf_counter() - started
    return out
