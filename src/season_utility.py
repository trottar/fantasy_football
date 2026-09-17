from __future__ import annotations

import math
from collections import Counter

import numpy as np

CORE = ("QB", "RB", "WR", "TE")
FLEX = {"RB", "WR", "TE"}
SPECIAL = ("K", "DST")


def week_weights(league: dict) -> tuple[np.ndarray, np.ndarray]:
    fcfg = league.get("fantasy_season", {})
    regular = {int(w) for w in fcfg.get("regular_season_weeks", range(1, 14))}
    playoff = {int(k): float(v) for k, v in fcfg.get("playoff_week_participation_prior", {}).items()}
    weeks = np.arange(1, 18, dtype=int)
    weights = np.array([
        1.0 if int(w) in regular else float(playoff.get(int(w), 0.0))
        for w in weeks
    ], dtype=float)
    if weights.sum() <= 0:
        weights[:] = 1.0
    return weeks, weights


def _best_lineup(prep, roster: list[int], active: np.ndarray, league: dict) -> tuple[float, set[int]]:
    """Best legal weekly lineup in VORP units; missing slots stream replacement (0 VORP)."""
    roster_cfg = league.get("roster", {})
    selected: set[int] = set()
    total = 0.0
    by_pos = {p: [] for p in CORE}
    for idx in roster:
        if not bool(active[idx]):
            continue
        pos = str(prep.positions[idx])
        if pos in CORE:
            by_pos[pos].append((float(prep.vorp[idx]), int(idx)))
    for pos in CORE:
        by_pos[pos].sort(reverse=True)
        for val, idx in by_pos[pos][:int(roster_cfg.get(pos, 0))]:
            selected.add(idx)
            total += max(val, 0.0)

    flex_n = int(roster_cfg.get("FLEX", 0))
    if flex_n:
        flex = []
        for pos in FLEX:
            for val, idx in by_pos[pos]:
                if idx not in selected:
                    flex.append((float(val), int(idx)))
        flex.sort(reverse=True)
        for val, idx in flex[:flex_n]:
            selected.add(idx)
            total += max(val, 0.0)

    for pos in SPECIAL:
        n = int(roster_cfg.get(pos, 0))
        if n <= 0:
            continue
        cand = [
            (float(prep.vorp[idx]), int(idx))
            for idx in roster
            if bool(active[idx]) and str(prep.positions[idx]) == pos
        ]
        cand.sort(reverse=True)
        for val, idx in cand[:n]:
            selected.add(idx)
            total += max(val, 0.0)
    return float(total), selected


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    return float(np.sum(values * weights) / max(float(np.sum(weights)), 1e-12))


def deterministic_bye_profile(prep, roster: list[int], league: dict) -> dict:
    weeks, weights = week_weights(league)
    nplayers = len(prep.ids)
    weekly = np.zeros(len(weeks), dtype=float)
    starter_weekly = []
    for j, week in enumerate(weeks):
        active = np.ones(nplayers, dtype=bool)
        active[np.asarray(prep.bye_weeks, dtype=int) == int(week)] = False
        weekly[j], _ = _best_lineup(prep, roster, active, league)

    no_bye_active = np.ones(nplayers, dtype=bool)
    healthy, healthy_ids = _best_lineup(prep, roster, no_bye_active, league)
    healthy_profile = np.full(len(weeks), healthy, dtype=float)

    bye_loss = _weighted_mean(healthy_profile - weekly, weights)
    min_idx = int(np.argmin(weekly)) if len(weekly) else 0
    healthy_byes = [int(prep.bye_weeks[i]) for i in healthy_ids if int(prep.bye_weeks[i]) > 0]
    counts = Counter(healthy_byes)
    max_conflict = max(counts.values()) if counts else 0
    playoff_bye_starters = sum(1 for w in healthy_byes if w >= 14)
    return {
        "healthy_value": float(healthy),
        "healthy_ids": set(int(i) for i in healthy_ids),
        "weighted_bye_value": _weighted_mean(weekly, weights),
        "bye_loss_ppg": float(bye_loss),
        "weekly_values": weekly,
        "weekly_floor_ppg": float(np.min(weekly)) if len(weekly) else 0.0,
        "weekly_std_ppg": float(np.std(weekly)) if len(weekly) else 0.0,
        "worst_bye_week": int(weeks[min_idx]) if len(weeks) else 0,
        "max_starter_bye_conflict": int(max_conflict),
        "playoff_bye_starters": int(playoff_bye_starters),
    }



def _typical_opponent_reference(prep, league: dict) -> float:
    """Approximate league-average healthy starter VORP from the full player pool."""
    teams = int(league.get("teams", 12))
    roster_cfg = league.get("roster", {})
    positions = np.asarray(prep.positions).astype(str)
    vorp = np.asarray(prep.vorp, dtype=float)
    eligible = np.asarray(getattr(prep, "eligible", np.ones(len(vorp), dtype=bool)), dtype=bool)
    selected: set[int] = set()
    total = 0.0

    for pos in CORE:
        need = int(roster_cfg.get(pos, 0)) * teams
        idx = np.flatnonzero(eligible & (positions == pos))
        if need > 0 and len(idx):
            order = idx[np.argsort(-vorp[idx])][:need]
            selected.update(int(i) for i in order)
            total += float(np.maximum(vorp[order], 0.0).sum())

    flex_need = int(roster_cfg.get("FLEX", 0)) * teams
    if flex_need:
        idx = np.flatnonzero(eligible & np.isin(positions, list(FLEX)))
        idx = np.asarray([i for i in idx if int(i) not in selected], dtype=int)
        if len(idx):
            order = idx[np.argsort(-vorp[idx])][:flex_need]
            selected.update(int(i) for i in order)
            total += float(np.maximum(vorp[order], 0.0).sum())

    for pos in SPECIAL:
        need = int(roster_cfg.get(pos, 0)) * teams
        idx = np.flatnonzero(eligible & (positions == pos))
        if need > 0 and len(idx):
            order = idx[np.argsort(-vorp[idx])][:need]
            total += float(np.maximum(vorp[order], 0.0).sum())

    return float(total / max(teams, 1))


def _win_probability(values: np.ndarray, opponent_reference: float, scale: float) -> np.ndarray:
    z = (np.asarray(values, dtype=float) - float(opponent_reference)) / max(float(scale), 1e-6)
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


def season_roster_utility(
    prep,
    roster: list[int],
    league: dict,
    model: dict,
    availability_uniforms: np.ndarray | None = None,
) -> dict:
    """Expected weekly best-lineup value under deterministic byes + availability shocks.

    All values are above position replacement. If no drafted player can fill a
    slot, an unlimited-waiver replacement contributes zero VORP rather than
    turning the slot into an artificial zero-point player.
    """
    scfg = model.get("season_utility", {})
    weeks, weights = week_weights(league)
    nplayers = len(prep.ids)
    nscen = int(scfg.get("availability_scenarios", 8))
    probs = {str(k): float(v) for k, v in scfg.get("active_probability_nonbye", {}).items()}

    if availability_uniforms is None:
        rng = np.random.default_rng(20260830)
        availability_uniforms = rng.random((nscen, len(weeks), nplayers))
    else:
        u = np.asarray(availability_uniforms, dtype=float)
        nscen = min(nscen, int(u.shape[0]))
        availability_uniforms = u[:nscen, :len(weeks), :nplayers]

    deterministic = deterministic_bye_profile(prep, roster, league)
    healthy_ids = deterministic["healthy_ids"]
    starter_only = sorted(healthy_ids)

    scenario_means = np.zeros(nscen, dtype=float)
    starter_only_means = np.zeros(nscen, dtype=float)
    all_week_values = np.zeros((nscen, len(weeks)), dtype=float)

    pos_prob = np.array([probs.get(str(p), 0.95) for p in prep.positions], dtype=float)
    bye_arr = np.asarray(prep.bye_weeks, dtype=int)
    for s in range(nscen):
        for j, week in enumerate(weeks):
            active = availability_uniforms[s, j] < pos_prob
            active &= bye_arr != int(week)
            val, _ = _best_lineup(prep, roster, active, league)
            start_val, _ = _best_lineup(prep, starter_only, active, league)
            all_week_values[s, j] = val
            # Compute weighted scenario mean after weekly loop.
            starter_only_means[s] += float(weights[j]) * start_val
        scenario_means[s] = _weighted_mean(all_week_values[s], weights)
        starter_only_means[s] /= max(float(weights.sum()), 1e-12)

    season_value = float(np.mean(scenario_means)) if nscen else deterministic["weighted_bye_value"]
    insurance = season_value - (float(np.mean(starter_only_means)) if nscen else 0.0)

    # H2H is nonlinear: one severe bye week is not equivalent to two moderate
    # deficits. Convert each weekly lineup to a win probability against a
    # generic league-strength opponent, then average with the fantasy-season
    # participation weights. This lets the model decide whether bye clustering
    # or spreading is preferable for the roster at hand.
    opponent_reference = float(
        scfg.get("opponent_reference_vorp", _typical_opponent_reference(prep, league))
    )
    matchup_scale = float(scfg.get("generic_opponent_matchup_scale_ppg", 10.0))
    if nscen:
        scenario_win = np.array([
            _weighted_mean(_win_probability(all_week_values[s], opponent_reference, matchup_scale), weights)
            for s in range(nscen)
        ], dtype=float)
        expected_win_probability = float(np.mean(scenario_win))
    else:
        expected_win_probability = _weighted_mean(
            _win_probability(deterministic["weekly_values"], opponent_reference, matchup_scale),
            weights,
        )

    # Epistemic uncertainty remains a very small probability-space tie-breaker.
    risk_sq = sum(float(prep.sd[i]) ** 2 for i in healthy_ids)
    risk_penalty = float(scfg.get("epistemic_probability_penalty", 0.002)) * math.sqrt(max(risk_sq, 0.0))

    return {
        "utility": float(expected_win_probability - risk_penalty),
        "season_value": float(season_value),
        "expected_h2h_win_probability": float(expected_win_probability),
        "opponent_reference_vorp": float(opponent_reference),
        "healthy_starter_value": float(deterministic["healthy_value"]),
        "bench_insurance_value": float(max(insurance, 0.0)),
        "bye_loss_ppg": float(deterministic["bye_loss_ppg"]),
        "weekly_floor_ppg": float(deterministic["weekly_floor_ppg"]),
        "weekly_std_ppg": float(deterministic["weekly_std_ppg"]),
        "worst_bye_week": int(deterministic["worst_bye_week"]),
        "max_starter_bye_conflict": int(deterministic["max_starter_bye_conflict"]),
        "playoff_bye_starters": int(deterministic["playoff_bye_starters"]),
        "starter_ids": [int(prep.ids[i]) for i in healthy_ids],
        "risk_penalty": float(risk_penalty),
    }
