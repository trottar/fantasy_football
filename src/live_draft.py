from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .draft_market import conditional_survival_probability
from .league import team_slot_for_overall_pick, user_overall_picks


CORE_POSITIONS = ["QB", "RB", "WR", "TE"]


def _norm_name(name: str) -> str:
    s = str(name).lower().strip()
    s = re.sub(r"[^a-z0-9]+", "", s)
    for suffix in ("jr", "sr", "ii", "iii", "iv"):
        if s.endswith(suffix) and len(s) > len(suffix) + 2:
            s = s[:-len(suffix)]
            break
    return s


def load_board(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    if "espn_id" not in df.columns:
        raise ValueError("Live board requires an espn_id column.")
    df["espn_id"] = pd.to_numeric(df["espn_id"], errors="coerce").astype("Int64")
    for c in [
        "latent_mean_ppg", "latent_mean_sd_ppg", "espn_adp", "espn_rank",
        "market_pick_mean", "market_pick_sigma", "draft_value_score",
        "vorp_ppg", "scarcity_gap_next_n_ppg",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def resolve_player(df: pd.DataFrame, query: str) -> pd.Series:
    """Resolve an ESPN player by exact ESPN ID or normalized exact name.

    We intentionally do not silently fuzzy-match live draft picks.
    """
    q = str(query).strip()
    if q.isdigit() or (q.startswith("-") and q[1:].isdigit()):
        rows = df[df["espn_id"].eq(int(q))]
        if len(rows) == 1:
            return rows.iloc[0]
        if len(rows) > 1:
            raise ValueError(f"Multiple rows found for ESPN ID {q}.")
        raise ValueError(f"No player found for ESPN ID {q}.")

    nq = _norm_name(q)
    matches = df[df["name"].map(_norm_name).eq(nq)]
    if len(matches) == 1:
        return matches.iloc[0]
    if len(matches) == 0:
        raise ValueError(
            f'No exact normalized player match for "{query}". '
            "Use the ESPN ID if the displayed name differs."
        )

    labels = ", ".join(
        f'{r["name"]} ({r.get("position")}, {r.get("nfl_team")}, ESPN {r["espn_id"]})'
        for _, r in matches.iterrows()
    )
    raise ValueError(f'Ambiguous player "{query}": {labels}')


def drafted_espn_ids(state) -> set[int]:
    """Canonical drafted ESPN IDs with legacy ``player_id`` fallback.

    Older state rows may contain an explicit ``espn_id`` key whose value is
    ``None``. ``dict.get(key, fallback)`` does not use the fallback in that
    case, so we must test the value explicitly.
    """
    ids = set()
    for pick in state.picks:
        raw = pick.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = pick.get("player_id")
        try:
            ids.add(int(raw))
        except (TypeError, ValueError):
            continue
    return ids


def drafted_legacy_identities(state) -> set[tuple[str, str]]:
    """Name/position fallback for state rows without a usable ESPN ID."""
    identities: set[tuple[str, str]] = set()
    for pick in state.picks:
        raw = pick.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = pick.get("player_id")
        try:
            int(raw)
            continue  # canonical numeric identity already handled above
        except (TypeError, ValueError):
            pass

        name = pick.get("player_name") or pick.get("name")
        pos = pick.get("position") or ""
        if name:
            identities.add((_norm_name(str(name)), str(pos).upper()))
    return identities


def draft_state_signature(state) -> tuple:
    """Stable in-memory fingerprint for stale-analysis detection."""
    pick_sig = []
    for pick in state.picks:
        raw = pick.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = pick.get("player_id")
        pick_sig.append((
            int(pick.get("overall", 0)),
            str(raw),
            _norm_name(str(pick.get("player_name") or pick.get("name") or "")),
            str(pick.get("position") or "").upper(),
        ))
    return (int(state.next_overall), tuple(pick_sig))


def available_board(df: pd.DataFrame, state) -> pd.DataFrame:
    drafted = drafted_espn_ids(state)
    legacy = drafted_legacy_identities(state)
    elig = (
        df["draft_eligible"].astype(str).str.lower().isin(["true", "1", "yes"])
        if "draft_eligible" in df.columns
        else pd.Series(True, index=df.index)
    )

    id_available = ~df["espn_id"].astype("Int64").isin(drafted)
    if legacy:
        identities = pd.Series(
            [
                (_norm_name(str(name)), str(pos).upper())
                for name, pos in zip(df["name"], df["position"])
            ],
            index=df.index,
        )
        legacy_available = ~identities.isin(legacy)
    else:
        legacy_available = pd.Series(True, index=df.index)

    return df[
        elig
        & df["espn_id"].notna()
        & id_available
        & legacy_available
    ].copy()


def drafted_position_counts(state) -> dict[str, int]:
    out = {p: 0 for p in CORE_POSITIONS}
    for pick in state.picks:
        pos = pick.get("position")
        if pos in out:
            out[pos] += 1
    return out


def dynamic_replacement_levels(
    available: pd.DataFrame,
    state,
    expected_rostered_counts: dict[str, int],
) -> dict[str, dict]:
    drafted = drafted_position_counts(state)
    result = {}
    for pos in CORE_POSITIONS:
        g = available[
            available["position"].eq(pos)
            & available["latent_mean_ppg"].notna()
        ].sort_values("latent_mean_ppg", ascending=False)

        remaining_to_roster = max(
            int(expected_rostered_counts[pos]) - int(drafted[pos]),
            0,
        )

        if len(g) == 0:
            result[pos] = {
                "drafted": int(drafted[pos]),
                "remaining_expected_rostered": remaining_to_roster,
                "replacement_ppg": float("nan"),
                "replacement_player": None,
            }
            continue

        idx = min(remaining_to_roster, len(g) - 1)
        row = g.iloc[idx]
        result[pos] = {
            "drafted": int(drafted[pos]),
            "remaining_expected_rostered": remaining_to_roster,
            "replacement_ppg": float(row["latent_mean_ppg"]),
            "replacement_player": row.get("name"),
        }
    return result


def add_dynamic_values(
    available: pd.DataFrame,
    state,
    expected_rostered_counts: dict[str, int],
    scarcity_lookahead: int = 5,
    scarcity_weight: float = 0.25,
) -> tuple[pd.DataFrame, dict]:
    out = available.copy()
    repl = dynamic_replacement_levels(
        out, state, expected_rostered_counts
    )
    core_mask = out["position"].isin(CORE_POSITIONS)
    if "dynamic_replacement_ppg" not in out.columns:
        out["dynamic_replacement_ppg"] = np.nan
    else:
        out["dynamic_replacement_ppg"] = pd.to_numeric(out["dynamic_replacement_ppg"], errors="coerce").astype(float)
    if "dynamic_vorp_ppg" not in out.columns:
        out["dynamic_vorp_ppg"] = np.nan
    else:
        out["dynamic_vorp_ppg"] = pd.to_numeric(out["dynamic_vorp_ppg"], errors="coerce").astype(float)
    repl_map = {p: repl[p]["replacement_ppg"] for p in CORE_POSITIONS}
    out.loc[core_mask, "dynamic_replacement_ppg"] = out.loc[core_mask, "position"].map(repl_map)
    out.loc[core_mask, "dynamic_vorp_ppg"] = (
        out.loc[core_mask, "latent_mean_ppg"] - out.loc[core_mask, "dynamic_replacement_ppg"]
    )

    if "dynamic_scarcity_gap_ppg" not in out.columns:
        out["dynamic_scarcity_gap_ppg"] = 0.0
    out.loc[core_mask, "dynamic_scarcity_gap_ppg"] = 0.0
    for pos in CORE_POSITIONS:
        g = out[
            out["position"].eq(pos)
            & out["latent_mean_ppg"].notna()
        ].sort_values("latent_mean_ppg", ascending=False)
        vals = g["latent_mean_ppg"].to_numpy(float)
        for i, idx in enumerate(g.index):
            j = min(i + int(scarcity_lookahead), len(g) - 1)
            out.loc[idx, "dynamic_scarcity_gap_ppg"] = float(vals[i] - vals[j])

    if "dynamic_draft_value" not in out.columns:
        out["dynamic_draft_value"] = np.nan
    out.loc[core_mask, "dynamic_draft_value"] = (
        out.loc[core_mask, "dynamic_vorp_ppg"]
        + float(scarcity_weight) * out.loc[core_mask, "dynamic_scarcity_gap_ppg"]
    )
    return out, repl


def next_user_pick_after(state) -> int | None:
    picks = user_overall_picks(
        state.num_teams, state.rounds, state.user_draft_slot
    )
    future = [p for p in picks if p > state.next_overall]
    return min(future) if future else None


def is_user_pick(state, overall: int | None = None) -> bool:
    p = state.next_overall if overall is None else int(overall)
    _, _, slot = team_slot_for_overall_pick(p, state.num_teams)
    return slot == state.user_draft_slot


def _position_count_for_slot(state, slot: int, position: str) -> int:
    return sum(
        1 for p in state.roster_for_slot(slot)
        if p.get("position") == position
    )


def _opponent_need_weight(
    state,
    slot: int,
    position: str,
    league: dict,
    strength: float,
) -> float:
    """Mild team-need modifier; market hazard remains the dominant signal."""
    maxima = league.get("position_maximums", {})
    max_pos = int(maxima.get(position, 99))
    current = _position_count_for_slot(state, slot, position)
    if current >= max_pos:
        return 0.0

    starters = league.get("roster", {})
    target = int(starters.get(position, 0))

    # FLEX gives RB/WR/TE a little additional demand.
    if position in {"RB", "WR", "TE"}:
        target += 0.35 * int(starters.get("FLEX", 0))

    deficit = max(float(target) - float(current), 0.0)
    return max(0.05, 1.0 + float(strength) * deficit)


def _hazard_at_pick(mean: float, sigma: float, pick: int) -> float:
    """Approximate conditional probability of selection during this pick."""
    if not np.isfinite(mean) or not np.isfinite(sigma) or sigma <= 0:
        return 0.0

    # P(X < p+0.5 | X >= p-0.5)
    p_survive_current = conditional_survival_probability(
        mean, sigma, pick, pick
    )
    # The helper returns exactly 1 for equal picks, so compute directly.
    def surv(x):
        z = (x - mean) / (sigma * math.sqrt(2.0))
        return 0.5 * math.erfc(z)

    denom = surv(pick - 0.5)
    numer = surv(pick + 0.5)
    if denom <= 1e-12:
        return 1.0
    return float(np.clip(1.0 - numer / denom, 0.0, 1.0))


def _sample_opponent_pick(
    rng: np.random.Generator,
    available: pd.DataFrame,
    pick_number: int,
    team_slot: int,
    state,
    league: dict,
    cfg: dict,
) -> int:
    """Return row index selected by one simulated opponent."""
    weights = []
    idxs = []

    for idx, row in available.iterrows():
        mean = row.get("market_pick_mean")
        sigma = row.get("market_pick_sigma")
        if pd.isna(mean) or pd.isna(sigma):
            continue

        hazard = _hazard_at_pick(
            float(mean), float(sigma), int(pick_number)
        )
        hazard = max(hazard, float(cfg["market_hazard_floor"]))

        need = _opponent_need_weight(
            state, team_slot, str(row["position"]),
            league, float(cfg["opponent_need_strength"])
        )
        w = hazard * need
        if w > 0:
            idxs.append(idx)
            weights.append(w)

    if not idxs:
        # Fallback: earliest market center.
        g = available.sort_values(
            ["market_pick_mean", "espn_rank"], na_position="last"
        )
        return int(g.index[0])

    w = np.asarray(weights, dtype=float)
    w /= w.sum()
    return int(rng.choice(np.asarray(idxs), p=w))


def _state_copy(state):
    from .draft_state import DraftState
    return DraftState.from_dict(state.to_dict())


def simulate_to_next_user_pick(
    board: pd.DataFrame,
    state,
    league: dict,
    cfg: dict,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, object]:
    """Simulate opponent picks until it is the user's turn again."""
    sim_state = _state_copy(state)
    available = available_board(board, sim_state)

    while not sim_state.complete and not is_user_pick(sim_state):
        overall = sim_state.next_overall
        _, _, slot = sim_state.expected_slot_for_pick(overall)
        if len(available) == 0:
            break

        idx = _sample_opponent_pick(
            rng, available, overall, slot,
            sim_state, league, cfg
        )
        row = available.loc[idx]
        sim_state.record_pick(
            str(int(row["espn_id"])),
            str(row["name"]),
            str(row["position"]),
            str(row.get("nfl_team") or ""),
            espn_id=int(row["espn_id"]),
        )
        available = available.drop(index=idx)

    return available, sim_state


def evaluate_candidates(
    board: pd.DataFrame,
    state,
    league: dict,
    model: dict,
    simulations: int | None = None,
    seed: int | None = None,
    candidate_limit: int | None = None,
) -> pd.DataFrame:
    """Monte Carlo one-pick lookahead at the user's current turn.

    For each candidate:
      1. add candidate to the user's roster;
      2. simulate all opponent picks until the user's next turn;
      3. measure best dynamic draft value expected to remain then;
      4. combine immediate dynamic value, option value, and risk penalty.

    This is the first live-draft objective; later versions will simulate the
    complete final roster rather than only one turn ahead.
    """
    if not is_user_pick(state):
        raise ValueError(
            f"Next pick {state.next_overall} belongs to another draft slot."
        )

    live_cfg = model["live_draft"]
    draft_cfg = model["draft_value"]

    nsim = int(simulations or live_cfg["simulations"])
    seed = int(live_cfg["random_seed"] if seed is None else seed)
    limit = int(candidate_limit or live_cfg["candidate_limit"])
    rng = np.random.default_rng(seed)

    from .roster_utility import add_roster_marginal_values, diversified_candidate_pool

    available = available_board(board, state)
    available, repl = add_dynamic_values(
        available,
        state,
        draft_cfg["expected_rostered_counts"],
        scarcity_lookahead=int(draft_cfg["scarcity_lookahead_players"]),
        scarcity_weight=float(live_cfg["scarcity_weight"]),
    )
    available = add_roster_marginal_values(
        available, board, state, league, model
    )

    # Cross-position, user-roster-aware candidate pool.
    candidates = diversified_candidate_pool(available, limit, model)

    records = []
    for _, cand in candidates.iterrows():
        future_best = []
        survival_counts = {}

        for _ in range(nsim):
            sim_state = _state_copy(state)
            sim_state.record_pick(
                str(int(cand["espn_id"])),
                str(cand["name"]),
                str(cand["position"]),
                str(cand.get("nfl_team") or ""),
                espn_id=int(cand["espn_id"]),
            )

            remaining, future_state = simulate_to_next_user_pick(
                board, sim_state, league, live_cfg, rng
            )
            if len(remaining) == 0:
                future_best.append(0.0)
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
            best = dyn.sort_values(
                "roster_marginal_value", ascending=False
            ).iloc[0]
            future_best.append(float(best["roster_marginal_value"]))
            bid = int(best["espn_id"])
            survival_counts[bid] = survival_counts.get(bid, 0) + 1

        immediate = float(cand["roster_marginal_value"])
        option_mean = float(np.mean(future_best)) if future_best else 0.0
        option_sd = float(np.std(future_best, ddof=1)) if len(future_best) > 1 else 0.0
        risk = float(cand.get("latent_mean_sd_ppg") or 0.0)

        objective = (
            float(live_cfg["replacement_weight"]) * immediate
            + float(live_cfg["survival_option_weight"]) * option_mean
            - float(live_cfg["risk_penalty"]) * risk
        )

        # Most common best player remaining next turn.
        common_id = None
        common_prob = 0.0
        common_name = None
        if survival_counts:
            common_id, n = max(survival_counts.items(), key=lambda kv: kv[1])
            common_prob = n / nsim
            rows = board[board["espn_id"].eq(common_id)]
            if len(rows):
                common_name = rows.iloc[0]["name"]

        records.append({
            "espn_id": int(cand["espn_id"]),
            "name": cand["name"],
            "position": cand["position"],
            "nfl_team": cand.get("nfl_team"),
            "espn_adp": cand.get("espn_adp"),
            "tier": cand.get("tier"),
            "latent_mean_ppg": cand.get("latent_mean_ppg"),
            "latent_mean_sd_ppg": cand.get("latent_mean_sd_ppg"),
            "dynamic_replacement_ppg": cand.get("dynamic_replacement_ppg"),
            "dynamic_vorp_ppg": cand.get("dynamic_vorp_ppg"),
            "dynamic_scarcity_gap_ppg": cand.get("dynamic_scarcity_gap_ppg"),
            "league_dynamic_value": cand.get("dynamic_draft_value"),
            "roster_lineup_gain_ppg": cand.get("roster_lineup_gain_ppg"),
            "roster_bench_option_value": cand.get("roster_bench_option_value"),
            "roster_marginal_value": cand.get("roster_marginal_value"),
            "candidate_in_best_lineup": cand.get("candidate_in_best_lineup"),
            "user_position_count": cand.get("user_position_count"),
            "immediate_draft_value": immediate,
            "next_turn_option_mean": option_mean,
            "next_turn_option_sd": option_sd,
            "most_common_best_next": common_name,
            "p_most_common_best_next": common_prob,
            "mc_objective": objective,
            "simulations": nsim,
        })

    return pd.DataFrame(records).sort_values(
        ["mc_objective", "immediate_draft_value"],
        ascending=[False, False],
    )
