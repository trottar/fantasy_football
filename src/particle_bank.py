from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .draft_state import DraftState
from .full_rollout import (
    POS_TO_CODE,
    SIM_POSITIONS,
    _opponent_need_weight,
    _opponent_position_max,
    _prepare_rollout,
    sample_market_orders,
)
from .league import team_slot_for_overall_pick


BANK_SCHEMA_VERSION = 1


@dataclass
class BankStatus:
    exists: bool = False
    valid: bool = False
    source: str = "none"
    anchor_pick: int | None = None
    conditioned_through: int | None = None
    particles: int = 0
    ess: float = 0.0
    ess_fraction: float = 0.0
    observed_opponent_picks: int = 0
    selected_branch_id: int | None = None
    selected_branch_name: str | None = None
    degraded: bool = False
    message: str = "No DEEP bank yet."
    inherited_fraction: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_bank_path(state_path: str | Path) -> Path:
    return Path(state_path).parent / "deep_particle_bank.npz"


def _pick_identity(pick: dict) -> str:
    raw = pick.get("espn_id")
    if raw is None or str(raw).strip() == "":
        raw = pick.get("player_id")
    if raw is not None and str(raw).strip() != "":
        return str(raw)
    return f'{pick.get("player_name", "")}::{pick.get("position", "")}'


def _anchor_prefix(state: DraftState) -> list[str]:
    return [_pick_identity(p) for p in state.picks]


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _metadata_array(meta: dict) -> np.ndarray:
    return np.asarray(json.dumps(meta, separators=(",", ":"), default=_json_default))


def save_bank(
    path: str | Path,
    market_order_ids: np.ndarray,
    state: DraftState,
    weights: np.ndarray | None = None,
    *,
    source: str,
    summary_rows: list[dict] | None = None,
    conditioned_through: int | None = None,
    inherited_fraction: float = 0.0,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    orders = np.asarray(market_order_ids, dtype=np.int64)
    if orders.ndim != 2:
        raise ValueError("market_order_ids must be a 2D array")
    n = int(len(orders))
    if n <= 0:
        raise ValueError("Cannot save an empty DEEP bank")
    if weights is None:
        weights = np.full(n, 1.0 / n, dtype=float)
    else:
        weights = np.asarray(weights, dtype=float)
        if len(weights) != n:
            raise ValueError("Particle weight length mismatch")
        total = float(np.sum(weights))
        weights = weights / total if total > 0 else np.full(n, 1.0 / n)

    meta = {
        "schema_version": BANK_SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "anchor_next_overall": int(state.next_overall),
        "conditioned_through": int(conditioned_through or (state.next_overall - 1)),
        "num_teams": int(state.num_teams),
        "rounds": int(state.rounds),
        "user_draft_slot": int(state.user_draft_slot),
        "anchor_prefix": _anchor_prefix(state),
        "summary_rows": summary_rows or [],
        "inherited_fraction": float(inherited_fraction),
    }
    np.savez_compressed(
        path,
        market_order_ids=orders,
        weights=weights,
        metadata=_metadata_array(meta),
    )
    return path


def load_bank(path: str | Path) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as z:
        orders = np.asarray(z["market_order_ids"], dtype=np.int64)
        weights = np.asarray(z["weights"], dtype=float)
        raw = z["metadata"]
        text = str(raw.item() if raw.ndim == 0 else raw.tolist())
        meta = json.loads(text)
    return {"orders": orders, "weights": weights, "meta": meta}


def _prefix_valid(meta: dict, state: DraftState) -> bool:
    anchor_prefix = list(meta.get("anchor_prefix", []))
    if len(state.picks) < len(anchor_prefix):
        return False
    current = [_pick_identity(p) for p in state.picks[:len(anchor_prefix)]]
    return current == anchor_prefix


def _board_maps(board: pd.DataFrame):
    work = board[board["espn_id"].notna()].copy()
    work["espn_id"] = pd.to_numeric(work["espn_id"], errors="coerce")
    work = work[work["espn_id"].notna()].drop_duplicates("espn_id", keep="first")
    id_to_pos = {int(r["espn_id"]): str(r["position"]) for _, r in work.iterrows()}
    if "draft_eligible" in work.columns:
        eligible = {
            int(r["espn_id"])
            for _, r in work.iterrows()
            if str(r.get("draft_eligible", True)).lower() in {"true", "1", "yes"}
        }
    else:
        eligible = set(id_to_pos)
    return id_to_pos, eligible


def _actual_context_before(state: DraftState, overall: int):
    drafted: set[int] = set()
    counts = np.zeros((state.num_teams + 1, len(SIM_POSITIONS)), dtype=np.int16)
    for p in state.picks:
        if int(p.get("overall", 0)) >= int(overall):
            break
        raw = p.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = p.get("player_id")
        try:
            drafted.add(int(raw))
        except (TypeError, ValueError):
            pass
        pos = str(p.get("position") or "")
        slot = int(p.get("fantasy_team_slot") or 0)
        code = POS_TO_CODE.get(pos)
        if code is not None and 1 <= slot <= state.num_teams:
            counts[slot, code] += 1
    return drafted, counts


def _scenario_pick_probability(
    order_ids: np.ndarray,
    observed_id: int,
    observed_slot: int,
    drafted_before: set[int],
    team_counts: np.ndarray,
    id_to_pos: dict[int, str],
    eligible_ids: set[int],
    league: dict,
    model: dict,
) -> float:
    rcfg = model.get("full_rollout", {})
    pcfg = model.get("particle_bank", {})
    lookahead = int(rcfg.get("deep_market_queue_lookahead", 12))
    temperature = float(rcfg.get("deep_queue_temperature", 5.0))
    strength = float(model.get("live_draft", {}).get("opponent_need_strength", 0.35))
    floor = float(pcfg.get("conditioning_likelihood_floor", 0.002))

    candidates: list[int] = []
    for raw in order_ids:
        pid = int(raw)
        if pid in drafted_before or pid not in eligible_ids:
            continue
        pos = id_to_pos.get(pid)
        if pos not in POS_TO_CODE:
            continue
        code = POS_TO_CODE[pos]
        if int(team_counts[observed_slot, code]) >= _opponent_position_max(pos, league, model):
            continue
        candidates.append(pid)
        if len(candidates) >= lookahead:
            break

    if not candidates:
        return floor

    weights = []
    for rank, pid in enumerate(candidates):
        pos = id_to_pos[pid]
        need = _opponent_need_weight(pos, team_counts[observed_slot], league, strength)
        market = math.exp(-float(rank) / max(temperature, 1e-6))
        weights.append(max(need * market, 1e-12))
    w = np.asarray(weights, dtype=float)
    w /= float(w.sum())
    try:
        j = candidates.index(int(observed_id))
        return max(float(w[j]), floor)
    except ValueError:
        return floor


def condition_bank(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    *,
    persist: bool = True,
) -> tuple[dict | None, BankStatus]:
    loaded = load_bank(path)
    if loaded is None:
        return None, BankStatus()

    orders = loaded["orders"]
    meta = dict(loaded["meta"])
    n = int(len(orders))
    status = BankStatus(
        exists=True,
        valid=False,
        source=str(meta.get("source", "DEEP")),
        anchor_pick=int(meta.get("anchor_next_overall", 0)) or None,
        conditioned_through=int(meta.get("conditioned_through", 0)) or None,
        particles=n,
        inherited_fraction=float(meta.get("inherited_fraction", 0.0)),
    )

    if int(meta.get("schema_version", -1)) != BANK_SCHEMA_VERSION:
        status.message = "DEEP bank schema is from another version; rerun DEEP."
        return loaded, status
    if not _prefix_valid(meta, state):
        status.message = "Draft history changed before the DEEP anchor; rerun DEEP."
        return loaded, status

    id_to_pos, eligible_ids = _board_maps(board)
    anchor = int(meta.get("anchor_next_overall", 1))
    user_slot = int(meta.get("user_draft_slot", state.user_draft_slot))
    actual = [
        p for p in state.picks
        if int(p.get("overall", 0)) >= anchor
        and int(p.get("fantasy_team_slot", 0)) != user_slot
    ]

    logw = np.zeros(n, dtype=float)
    observed = 0
    last_overall = anchor - 1
    temperature = max(float(model.get("particle_bank", {}).get("conditioning_temperature", 1.5)), 1e-6)

    for p in actual:
        raw = p.get("espn_id")
        if raw is None or str(raw).strip() == "":
            raw = p.get("player_id")
        try:
            observed_id = int(raw)
        except (TypeError, ValueError):
            continue
        overall = int(p["overall"])
        slot = int(p["fantasy_team_slot"])
        drafted_before, team_counts = _actual_context_before(state, overall)
        probs = np.empty(n, dtype=float)
        for i in range(n):
            probs[i] = _scenario_pick_probability(
                orders[i], observed_id, slot, drafted_before, team_counts,
                id_to_pos, eligible_ids, league, model,
            )
        logw += np.log(np.clip(probs, 1e-300, None)) / temperature
        observed += 1
        last_overall = max(last_overall, overall)

    if n:
        logw -= float(np.max(logw))
        weights = np.exp(logw)
        total = float(weights.sum())
        weights = weights / total if total > 0 else np.full(n, 1.0 / n)
        ess = float(1.0 / np.sum(weights * weights))
    else:
        weights = np.asarray([], dtype=float)
        ess = 0.0
    ess_fraction = ess / n if n else 0.0
    threshold = float(model.get("particle_bank", {}).get("degraded_ess_fraction", 0.25))

    summary_rows = list(meta.get("summary_rows", []))
    selected_id = None
    selected_name = None
    if len(state.picks) >= anchor:
        anchor_pick = state.picks[anchor - 1] if anchor - 1 < len(state.picks) else None
        if anchor_pick and int(anchor_pick.get("fantasy_team_slot", 0)) == user_slot:
            raw = anchor_pick.get("espn_id")
            try:
                selected_id = int(raw)
            except (TypeError, ValueError):
                selected_id = None
            if selected_id is not None:
                for row in summary_rows:
                    try:
                        if int(row.get("espn_id")) == selected_id:
                            selected_name = str(row.get("name"))
                            break
                    except (TypeError, ValueError):
                        pass

    meta["conditioned_through"] = int(last_overall)
    loaded["weights"] = weights
    loaded["meta"] = meta

    status.valid = True
    status.conditioned_through = int(last_overall)
    status.ess = ess
    status.ess_fraction = ess_fraction
    status.observed_opponent_picks = observed
    status.selected_branch_id = selected_id
    status.selected_branch_name = selected_name
    status.degraded = bool(ess_fraction < threshold)
    status.message = (
        f"Conditioned on {observed} opponent picks; ESS {ess:.1f}/{n}."
        if observed else f"Fresh DEEP bank; ESS {ess:.1f}/{n}."
    )

    if persist:
        save_bank(
            path, orders, state=DraftState.from_dict({
                "num_teams": int(meta["num_teams"]),
                "rounds": int(meta["rounds"]),
                "user_draft_slot": int(meta["user_draft_slot"]),
                "picks": state.picks[:len(meta.get("anchor_prefix", []))],
            }),
            weights=weights,
            source=str(meta.get("source", "DEEP")),
            summary_rows=summary_rows,
            conditioned_through=int(last_overall),
            inherited_fraction=float(meta.get("inherited_fraction", 0.0)),
        )
    return loaded, status


def _fresh_market_order_ids(
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    count: int,
    seed: int,
    *,
    after_user_selection: bool,
) -> np.ndarray:
    if count <= 0:
        return np.empty((0, 0), dtype=np.int64)
    prep, _ = _prepare_rollout(board, state, league, model)
    cutoff = state.next_overall + 1 if after_user_selection else state.next_overall
    rng = np.random.default_rng(int(seed))
    orders = sample_market_orders(
        rng, prep.means, prep.sigmas,
        current_pick_after_selection=int(cutoff),
        simulations=int(count),
    )
    return prep.ids[orders]


def conditioned_orders_for_fast(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    simulations: int,
    seed: int,
    *,
    after_user_selection: bool = True,
) -> tuple[np.ndarray | None, BankStatus, float]:
    loaded, status = condition_bank(path, board, state, league, model, persist=True)
    if loaded is None or not status.valid or not len(loaded["orders"]):
        return None, status, 1.0

    pcfg = model.get("particle_bank", {})
    fresh_fraction = float(pcfg.get("fast_fresh_fraction", 0.25))
    if status.degraded:
        fresh_fraction = max(fresh_fraction, float(pcfg.get("degraded_fast_fresh_fraction", 0.50)))
    fresh_n = int(round(simulations * fresh_fraction))
    bank_n = max(int(simulations) - fresh_n, 0)

    rng = np.random.default_rng(int(seed) + 8123)
    if bank_n:
        picks = rng.choice(
            len(loaded["orders"]), size=bank_n, replace=True,
            p=np.asarray(loaded["weights"], dtype=float),
        )
        inherited = loaded["orders"][picks]
    else:
        inherited = np.empty((0, loaded["orders"].shape[1]), dtype=np.int64)

    fresh = _fresh_market_order_ids(
        board, state, league, model, fresh_n, seed + 991,
        after_user_selection=after_user_selection,
    )
    if len(inherited) and len(fresh):
        orders = np.concatenate([inherited, fresh], axis=0)
    elif len(inherited):
        orders = inherited
    else:
        orders = fresh
    return orders, status, fresh_fraction


def orders_for_deep_refresh(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    simulations: int,
    seed: int,
    *,
    after_user_selection: bool = True,
) -> tuple[np.ndarray, BankStatus, float]:
    loaded, status = condition_bank(path, board, state, league, model, persist=True)
    pcfg = model.get("particle_bank", {})
    reuse_fraction = float(pcfg.get("deep_reuse_fraction", 0.50))
    if loaded is None or not status.valid or not len(loaded["orders"]):
        reuse_fraction = 0.0
    elif status.degraded:
        reuse_fraction = min(reuse_fraction, float(pcfg.get("degraded_deep_reuse_fraction", 0.25)))

    reused_n = int(round(int(simulations) * reuse_fraction))
    fresh_n = int(simulations) - reused_n
    rng = np.random.default_rng(int(seed) + 11731)
    if reused_n:
        picks = rng.choice(
            len(loaded["orders"]), size=reused_n, replace=True,
            p=np.asarray(loaded["weights"], dtype=float),
        )
        reused = loaded["orders"][picks]
    else:
        reused = None

    fresh = _fresh_market_order_ids(
        board, state, league, model, fresh_n, seed + 1831,
        after_user_selection=after_user_selection,
    )
    if reused is not None and len(fresh):
        return np.concatenate([reused, fresh], axis=0), status, reuse_fraction
    if reused is not None:
        return reused, status, reuse_fraction
    return fresh, status, reuse_fraction


def refresh_bank_from_deep(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    deep_market_order_ids: np.ndarray,
    summary_rows: list[dict],
    seed: int,
    inherited_fraction: float,
) -> BankStatus:
    """Re-anchor the bank after DEEP without forgetting the old posterior."""
    pcfg = model.get("particle_bank", {})
    target = max(int(pcfg.get("bank_particles", 160)), len(deep_market_order_ids))
    deep_orders = np.asarray(deep_market_order_ids, dtype=np.int64)

    old, old_status = condition_bank(path, board, state, league, model, persist=False)
    retain_fraction = float(pcfg.get("bank_refresh_retain_fraction", 0.50))
    if old is None or not old_status.valid:
        retain_fraction = 0.0
    elif old_status.degraded:
        retain_fraction = min(
            retain_fraction, float(pcfg.get("degraded_bank_refresh_retain_fraction", 0.25))
        )

    rng = np.random.default_rng(int(seed) + 33103)
    retain_n = min(int(round(target * retain_fraction)), max(target - len(deep_orders), 0))
    if retain_n > 0:
        idx = rng.choice(
            len(old["orders"]), size=retain_n, replace=True,
            p=np.asarray(old["weights"], dtype=float),
        )
        retained = old["orders"][idx]
    else:
        retained = np.empty((0, deep_orders.shape[1]), dtype=np.int64)

    current = [deep_orders]
    if len(retained):
        current.append(retained)
    used = sum(len(x) for x in current)
    extra_n = max(target - used, 0)
    fresh = _fresh_market_order_ids(
        board, state, league, model, extra_n, seed + 4421,
        after_user_selection=True,
    )
    if len(fresh):
        current.append(fresh)
    orders = np.concatenate(current, axis=0)
    effective_inherited = min(1.0, (retain_n + inherited_fraction * len(deep_orders)) / max(len(orders), 1))
    save_bank(
        path, orders, state, source="DEEP-FULL",
        summary_rows=summary_rows,
        inherited_fraction=float(effective_inherited),
    )
    _, status = condition_bank(path, board, state, league, model, persist=False)
    return status


def build_offturn_bank(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
    seed: int,
    source: str = "DEEP-FORECAST",
) -> BankStatus:
    """Re-anchor an off-turn bank, retaining the conditioned prior bank."""
    pcfg = model.get("particle_bank", {})
    target = int(pcfg.get("bank_particles", 160))
    old, old_status = condition_bank(path, board, state, league, model, persist=False)
    retain_fraction = float(pcfg.get("bank_refresh_retain_fraction", 0.50))
    if old is None or not old_status.valid:
        retain_fraction = 0.0
    elif old_status.degraded:
        retain_fraction = min(
            retain_fraction, float(pcfg.get("degraded_bank_refresh_retain_fraction", 0.25))
        )

    retain_n = int(round(target * retain_fraction))
    fresh_n = target - retain_n
    rng = np.random.default_rng(int(seed) + 55109)
    pieces = []
    if retain_n:
        idx = rng.choice(
            len(old["orders"]), size=retain_n, replace=True,
            p=np.asarray(old["weights"], dtype=float),
        )
        pieces.append(old["orders"][idx])
    fresh = _fresh_market_order_ids(
        board, state, league, model, fresh_n, seed + 5521,
        after_user_selection=False,
    )
    if len(fresh):
        pieces.append(fresh)
    orders = np.concatenate(pieces, axis=0)
    save_bank(
        path, orders, state, source=source, summary_rows=[],
        inherited_fraction=float(retain_fraction),
    )
    _, status = condition_bank(path, board, state, league, model, persist=False)
    return status


def bank_status(
    path: str | Path,
    board: pd.DataFrame,
    state: DraftState,
    league: dict,
    model: dict,
) -> BankStatus:
    _, status = condition_bank(path, board, state, league, model, persist=True)
    return status
