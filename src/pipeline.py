from __future__ import annotations

from pathlib import Path

from .draft_market import build_market_values
from .draft_value import build_draft_values
from .specialists import ensure_specialists_in_live_board


def build_live_board(
    player_values_path,
    league_path,
    model_path,
    market_pre_path,
    draft_values_path,
    live_board_path,
    market_diag_path,
    draft_diag_path,
):
    # 1. Attach current market eligibility and pick model to player values.
    market_pre, _ = build_market_values(
        player_values_path,
        league_path,
        model_path,
        market_pre_path,
        diagnostics_path=market_diag_path,
    )

    # 2. Recompute replacement / tiers using only draft_eligible rows.
    draft_values, draft_diag = build_draft_values(
        market_pre_path,
        league_path,
        model_path,
        draft_values_path,
        diagnostics_path=draft_diag_path,
    )

    # 3. Market columns are already preserved by build_draft_values, so the
    # final live board is just a copy with an explicit filename.
    Path(live_board_path).parent.mkdir(parents=True, exist_ok=True)
    draft_values.to_csv(live_board_path, index=False)
    specialist_source = Path(player_values_path).parent / "player_master.csv"
    if specialist_source.exists():
        ensure_specialists_in_live_board(live_board_path, specialist_source, model_path)
    import pandas as pd
    return pd.read_csv(live_board_path, low_memory=False), draft_diag
