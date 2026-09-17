from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import pandas as pd

from ..draft_market import conditional_survival_probability
from ..draft_state import DraftState
from ..league import load_league, user_overall_picks
from ..fast_recommend import evaluate_candidates_fast
from ..full_rollout import evaluate_candidates_full_rollout
from ..particle_bank import (
    bank_status as get_bank_status,
    build_offturn_bank,
    conditioned_orders_for_fast,
    default_bank_path,
    orders_for_deep_refresh,
    refresh_bank_from_deep,
)
from ..forecast import (
    forecast_next_user_pick_conditioned,
    forecast_next_user_pick_deep,
    forecast_next_user_pick_deep_conditioned,
    forecast_next_user_pick_fast,
)
from ..live_draft import (
    add_dynamic_values,
    available_board,
    draft_state_signature,
    drafted_espn_ids,
    evaluate_candidates,
    is_user_pick,
    load_board,
    resolve_player,
)
from .paste_parser import (
    PastePreviewRow,
    preview_is_committable,
    preview_pasted_picks,
    remove_already_recorded,
)


@dataclass
class TurnInfo:
    next_overall: int
    next_user_pick: int | None
    later_user_pick: int | None
    opponent_picks_until_user: int
    opponent_picks_after_user: int | None
    user_on_clock: bool
    mode: str


class DraftController:
    """Pure-Python state controller used by both GUI and tests."""

    def __init__(
        self,
        board_path: str | Path,
        state_path: str | Path,
        league_path: str | Path,
        model_path: str | Path,
    ):
        self.board_path = Path(board_path)
        self.state_path = Path(state_path)
        self.league_path = Path(league_path)
        self.model_path = Path(model_path)
        self.bank_path = default_bank_path(self.state_path)
        self.league = load_league(self.league_path)
        self.model = json.loads(self.model_path.read_text())
        self.board = load_board(self.board_path)
        self._preview: list[PastePreviewRow] = []

    def state(self) -> DraftState:
        return DraftState.load(self.state_path)

    def state_signature(self) -> tuple:
        return draft_state_signature(self.state())

    def deep_bank_status(self) -> dict:
        status = get_bank_status(
            self.bank_path, self.board, self.state(), self.league, self.model
        )
        return status.to_dict()

    def recommendation_rows_match_current_state(
        self, rows: list[dict]
    ) -> tuple[bool, list[str]]:
        """Defensive invariant check before GUI results are displayed."""
        if not rows:
            return True, []
        available, _ = self.available_dynamic()
        available_ids = set(int(x) for x in available["espn_id"].dropna().astype(int))
        stale = []
        for row in rows:
            raw = row.get("espn_id")
            try:
                pid = int(raw)
            except (TypeError, ValueError):
                stale.append(str(row.get("name") or raw or "unknown"))
                continue
            if pid not in available_ids:
                stale.append(str(row.get("name") or pid))
        return len(stale) == 0, stale

    def reload_board(self) -> None:
        self.board = load_board(self.board_path)

    def turn_info(self, state: DraftState | None = None) -> TurnInfo:
        state = state or self.state()
        picks = user_overall_picks(
            state.num_teams, state.rounds, state.user_draft_slot
        )
        current = state.next_overall
        user_future = [p for p in picks if p >= current]
        next_user = user_future[0] if user_future else None
        later_user = user_future[1] if len(user_future) > 1 else None
        on_clock = next_user == current
        until_user = max((next_user or current) - current, 0)
        after_user = (
            later_user - next_user - 1
            if next_user is not None and later_user is not None
            else None
        )

        if on_clock and after_user is not None and after_user <= 2:
            mode = "SHORT TURN"
        elif on_clock and after_user is not None and after_user >= 10:
            mode = "LONG TURN"
        elif on_clock:
            mode = "USER TURN"
        elif until_user <= 2:
            mode = "IMMINENT"
        else:
            mode = "WAITING"

        return TurnInfo(
            next_overall=current,
            next_user_pick=next_user,
            later_user_pick=later_user,
            opponent_picks_until_user=until_user,
            opponent_picks_after_user=after_user,
            user_on_clock=on_clock,
            mode=mode,
        )

    def available_dynamic(self, state: DraftState | None = None) -> tuple[pd.DataFrame, dict]:
        state = state or self.state()
        avail = available_board(self.board, state)
        dcfg = self.model["draft_value"]
        lcfg = self.model["live_draft"]
        return add_dynamic_values(
            avail,
            state,
            dcfg["expected_rostered_counts"],
            scarcity_lookahead=int(dcfg["scarcity_lookahead_players"]),
            scarcity_weight=float(lcfg["scarcity_weight"]),
        )

    def quick_player_options(self, limit: int = 500) -> dict[int, str]:
        avail, _ = self.available_dynamic()
        avail = avail.sort_values(
            ["espn_adp", "dynamic_draft_value"],
            ascending=[True, False],
            na_position="last",
        ).head(limit)
        return {
            int(row["espn_id"]): (
                f'{row["name"]} — {row["position"]} {row.get("nfl_team", "")} '
                f'(ADP {row.get("espn_adp", float("nan")):.1f})'
            )
            for _, row in avail.iterrows()
        }

    def record_player(self, query: str | int) -> dict:
        state = self.state()
        row = resolve_player(self.board, str(query))
        espn_id = int(row["espn_id"])
        pick = state.record_pick(
            str(espn_id),
            str(row["name"]),
            str(row["position"]),
            str(row.get("nfl_team") or ""),
            espn_id=espn_id,
        )
        state.save(self.state_path)
        return pick

    def undo_last_pick(self) -> dict | None:
        state = self.state()
        pick = state.undo_last_pick()
        state.save(self.state_path)
        return pick

    def reset_draft(self) -> dict:
        """Start a clean mock without touching downloaded/model data.

        Clears only the live draft history and the state-conditioned DEEP
        particle bank. Processed/raw player data, mock calibration samples,
        and configuration are intentionally preserved.
        """
        previous = self.state()
        previous_picks = len(previous.picks)

        draft_cfg = self.league["draft"]
        fresh = DraftState(
            int(self.league["teams"]),
            int(draft_cfg["rounds"]),
            int(draft_cfg["user_draft_slot"]),
        )
        fresh.save(self.state_path)

        bank_removed = False
        if self.bank_path.exists():
            self.bank_path.unlink()
            bank_removed = True

        self._preview = []
        return {
            "previous_picks": int(previous_picks),
            "bank_removed": bool(bank_removed),
            "next_overall": int(fresh.next_overall),
        }

    def preview_paste(self, text: str) -> list[PastePreviewRow]:
        state = self.state()
        pick_map = {
            int(p["espn_id"]): int(p["overall"])
            for p in state.picks
            if p.get("espn_id") is not None
        }
        self._preview = preview_pasted_picks(
            text,
            self.board,
            start_overall=state.next_overall,
            num_teams=state.num_teams,
            drafted_espn_ids=drafted_espn_ids(state),
            drafted_picks_by_espn_id=pick_map,
        )
        return list(self._preview)

    def remove_already_picked_from_preview(self) -> tuple[list[PastePreviewRow], int]:
        self._preview, removed = remove_already_recorded(self._preview)
        return list(self._preview), removed

    def commit_preview(self) -> list[dict]:
        if not preview_is_committable(self._preview):
            raise ValueError("Paste preview contains unresolved/error rows.")
        state = self.state()
        committed = []
        for row in self._preview:
            # Harmless overlap from a copied recent-picks window. It has
            # already been canonicalized/verified and is intentionally ignored.
            if row.status == "already_recorded":
                continue
            if state.next_overall != row.overall:
                raise ValueError(
                    f"State moved before commit: expected pick {row.overall}, "
                    f"current state is {state.next_overall}."
                )
            pick = state.record_pick(
                str(row.espn_id),
                str(row.name),
                str(row.position or ""),
                str(row.nfl_team or ""),
                espn_id=int(row.espn_id),
            )
            committed.append(pick)
        state.save(self.state_path)
        self._preview = []
        return committed

    def recommendation_inputs(self) -> tuple[dict, dict]:
        return self.league, self.model

    def survival_frame(self, top_n: int = 50) -> tuple[pd.DataFrame, int | None]:
        state = self.state()
        info = self.turn_info(state)
        target = info.later_user_pick if info.user_on_clock else info.next_user_pick
        dyn, _ = self.available_dynamic(state)
        if target is None:
            dyn["p_survive"] = 0.0
            return dyn.head(top_n), None

        probs = []
        for _, row in dyn.iterrows():
            mean = row.get("market_pick_mean")
            sigma = row.get("market_pick_sigma")
            if pd.isna(mean) or pd.isna(sigma):
                probs.append(float("nan"))
            else:
                probs.append(conditional_survival_probability(
                    float(mean), float(sigma), state.next_overall, int(target)
                ))
        dyn["p_survive"] = probs
        dyn = dyn.sort_values(
            ["dynamic_draft_value", "espn_adp"],
            ascending=[False, True],
            na_position="last",
        ).head(top_n)
        return dyn, target

    def tier_frame(self, per_position: int = 12) -> pd.DataFrame:
        dyn, _ = self.available_dynamic()
        parts = []
        for pos in ["RB", "WR", "TE", "QB"]:
            g = dyn[dyn["position"].eq(pos)].sort_values(
                "dynamic_draft_value", ascending=False
            ).head(per_position).copy()
            g["visual_rank"] = range(1, len(g) + 1)
            parts.append(g)
        return pd.concat(parts, ignore_index=True) if parts else dyn.iloc[0:0]

    def user_roster(self) -> list[dict]:
        state = self.state()
        return state.roster_for_slot(state.user_draft_slot)

    def recent_picks(self, n: int = 10) -> list[dict]:
        return self.state().picks[-n:]


def compute_recommendations_from_paths(
    board_path: str,
    state_path: str,
    league_path: str,
    model_path: str,
    simulations: int,
    candidates: int,
    seed: int | None = None,
) -> list[dict]:
    """Deep full-rollout worker which refreshes the persistent particle bank."""
    board = load_board(board_path)
    state = DraftState.load(state_path)
    league = load_league(league_path)
    model = json.loads(Path(model_path).read_text())
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    bank_path = default_bank_path(state_path)

    scenario_ids, prior_status, reused_fraction = orders_for_deep_refresh(
        bank_path, board, state, league, model, int(simulations), seed
    )
    result, used_scenarios = evaluate_candidates_full_rollout(
        board,
        state,
        league,
        model,
        simulations=int(simulations),
        seed=seed,
        candidate_limit=int(candidates),
        deep=True,
        market_order_ids=scenario_ids,
        return_scenarios=True,
    )
    rows = result.to_dict("records")
    status = refresh_bank_from_deep(
        bank_path, board, state, league, model, used_scenarios, rows, seed, reused_fraction
    )
    for row in rows:
        row.update({
            "deep_bank_particles": status.particles,
            "deep_bank_ess": status.ess,
            "deep_bank_ess_fraction": status.ess_fraction,
            "deep_bank_anchor_pick": status.anchor_pick,
            "deep_bank_conditioned_through": status.conditioned_through,
            "deep_bank_degraded": status.degraded,
            "deep_bank_reused_fraction": reused_fraction,
            "deep_prior_bank_ess_fraction": prior_status.ess_fraction if prior_status.valid else 0.0,
        })
    return rows

def compute_fast_recommendations_from_paths(
    board_path: str,
    state_path: str,
    league_path: str,
    model_path: str,
    simulations: int,
    candidates: int,
    seed: int | None = None,
) -> list[dict]:
    """Low-latency FAST, conditioned on the latest reusable DEEP bank when valid."""
    board = load_board(board_path)
    state = DraftState.load(state_path)
    league = load_league(league_path)
    model = json.loads(Path(model_path).read_text())
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    bank_path = default_bank_path(state_path)
    orders, status, fresh_fraction = conditioned_orders_for_fast(
        bank_path, board, state, league, model, int(simulations), seed
    )
    info = status.to_dict()
    info["fresh_fraction"] = float(fresh_fraction)
    result = evaluate_candidates_fast(
        board, state, league, model,
        simulations=int(simulations),
        seed=seed,
        candidate_limit=int(candidates),
        market_order_ids=orders,
        bank_info=info if orders is not None else None,
    )
    return result.to_dict("records")

def compute_fast_forecast_from_paths(
    board_path: str,
    state_path: str,
    league_path: str,
    model_path: str,
    simulations: int,
    candidates: int,
    seed: int | None = None,
) -> list[dict]:
    """Off-turn FAST, conditioned on the DEEP bank whenever available."""
    board = load_board(board_path)
    state = DraftState.load(state_path)
    league = load_league(league_path)
    model = json.loads(Path(model_path).read_text())
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    bank_path = default_bank_path(state_path)
    conditioned_n = min(
        int(simulations),
        int(model.get("particle_bank", {}).get("conditioned_forecast_simulations", 1200)),
    )
    orders, status, fresh_fraction = conditioned_orders_for_fast(
        bank_path, board, state, league, model, conditioned_n, seed,
        after_user_selection=False,
    )
    if orders is not None:
        info = status.to_dict()
        info["fresh_fraction"] = float(fresh_fraction)
        result = forecast_next_user_pick_conditioned(
            board, state, league, model, orders, info,
            seed=seed, candidate_limit=int(candidates),
        )
    else:
        result = forecast_next_user_pick_fast(
            board, state, league, model,
            simulations=int(simulations),
            seed=seed,
            candidate_limit=int(candidates),
        )
    return result.to_dict("records")

def compute_deep_forecast_from_paths(
    board_path: str,
    state_path: str,
    league_path: str,
    model_path: str,
    simulations: int,
    candidates: int,
    seed: int | None = None,
) -> list[dict]:
    """Team-aware off-turn forecast which reuses and re-anchors the DEEP bank."""
    board = load_board(board_path)
    state = DraftState.load(state_path)
    league = load_league(league_path)
    model = json.loads(Path(model_path).read_text())
    seed = int(model.get("live_draft", {}).get("random_seed", 20260830) if seed is None else seed)
    bank_path = default_bank_path(state_path)
    orders, prior_status, reused_fraction = orders_for_deep_refresh(
        bank_path, board, state, league, model, int(simulations), seed,
        after_user_selection=False,
    )
    info = prior_status.to_dict()
    info["reused_fraction"] = float(reused_fraction)
    result = forecast_next_user_pick_deep_conditioned(
        board, state, league, model, orders, info,
        seed=seed, candidate_limit=int(candidates),
    )
    status = build_offturn_bank(
        bank_path, board, state, league, model, seed,
        source="DEEP-CONDITIONED-FORECAST",
    )
    rows = result.to_dict("records")
    for row in rows:
        row.update({
            "deep_bank_particles": status.particles,
            "deep_bank_ess": status.ess,
            "deep_bank_ess_fraction": status.ess_fraction,
            "deep_bank_anchor_pick": status.anchor_pick,
            "deep_bank_conditioned_through": status.conditioned_through,
            "deep_bank_degraded": status.degraded,
            "deep_bank_reused_fraction": reused_fraction,
            "deep_prior_bank_ess_fraction": prior_status.ess_fraction if prior_status.valid else 0.0,
        })
    return rows

