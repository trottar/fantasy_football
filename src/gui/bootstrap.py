from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..draft_state import DraftState
from ..league import load_league


class GuiStartupError(RuntimeError):
    """Concise startup error intended for the local GUI user."""


@dataclass
class GuiBootstrapResult:
    board_built: bool = False
    state_initialized: bool = False
    specialists_refreshed: int = 0

    @property
    def messages(self) -> list[str]:
        out = []
        if self.board_built:
            out.append("Built missing live board from existing processed player data.")
        if self.state_initialized:
            out.append("Initialized a new empty draft state because none existed.")
        if self.specialists_refreshed:
            out.append(f"Loaded/refreshed {self.specialists_refreshed} K/DST specialist rows.")
        return out


def ensure_gui_runtime(
    board_path: str | Path,
    state_path: str | Path,
    league_path: str | Path,
    model_path: str | Path,
) -> GuiBootstrapResult:
    """Ensure the files required by the draft cockpit exist.

    The release ZIP intentionally does not ship the user's current downloaded
    ESPN/nflverse data or live draft state. For a migrated working directory:

    * preserve an existing draft_state.json exactly;
    * rebuild live_board_2026.csv automatically when player_values_2026.csv
      is already present;
    * initialize a new state only when no state file exists;
    * otherwise raise a short migration error rather than exposing a pandas
      FileNotFoundError traceback.
    """
    board_path = Path(board_path)
    state_path = Path(state_path)
    league_path = Path(league_path)
    model_path = Path(model_path)

    missing_config = [
        p for p in (league_path, model_path)
        if not p.exists()
    ]
    if missing_config:
        names = ", ".join(str(p) for p in missing_config)
        raise GuiStartupError(
            f"GUI startup is missing configuration file(s): {names}"
        )

    result = GuiBootstrapResult()

    if not board_path.exists():
        processed = board_path.parent
        player_values = processed / "player_values_2026.csv"

        if not player_values.exists():
            raise GuiStartupError(
                "The live draft board is missing and this v0.11 directory "
                "does not contain your processed player data.\n\n"
                "Copy the entire `data` directory from your working v0.10 "
                "directory into this directory, preserving:\n"
                "  data\\draft_state.json\n"
                "  data\\processed\\player_values_2026.csv\n"
                "  data\\raw\\...\n\n"
                "Then rerun:\n"
                "  python fantasy.py gui\n\n"
                "If you intentionally want a clean rebuild instead, run the "
                "data pipeline through `build-values` first."
            )

        from ..pipeline import build_live_board

        processed.mkdir(parents=True, exist_ok=True)
        build_live_board(
            player_values_path=player_values,
            league_path=league_path,
            model_path=model_path,
            market_pre_path=processed / "player_market_2026.csv",
            draft_values_path=processed / "draft_values_2026.csv",
            live_board_path=board_path,
            market_diag_path=processed / "draft_market_diagnostics.json",
            draft_diag_path=processed / "draft_value_diagnostics.json",
        )
        result.board_built = True

    processed = board_path.parent
    specialist_source = processed / "player_master.csv"
    if specialist_source.exists() and board_path.exists():
        from ..specialists import ensure_specialists_in_live_board
        result.specialists_refreshed = ensure_specialists_in_live_board(
            board_path, specialist_source, model_path
        )

    # Do not overwrite a migrated/active state.
    if not state_path.exists():
        league = load_league(league_path)
        draft = league["draft"]
        state = DraftState(
            int(league["teams"]),
            int(draft["rounds"]),
            int(draft["user_draft_slot"]),
        )
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state.save(state_path)
        result.state_initialized = True

    return result
