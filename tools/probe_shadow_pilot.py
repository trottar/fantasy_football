from __future__ import annotations

from argparse import Namespace
import copy
from contextlib import redirect_stdout
from io import StringIO
import json

import fantasy
from src.gui.season_service import SeasonGuiService
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.shadow_pilot import (
    ShadowRecorder,
    dispatch_cli_shadow,
    last_cli_shadow_events,
)


BUDGET = OverheadBudget(
    max_incremental_ns=1_000_000,
    max_relative_fraction=0.10,
    relative_floor_ns=5_000_000,
    trials=30,
    warmups=5,
)


def _capture_score(fn, args):
    buffer = StringIO()
    with redirect_stdout(buffer):
        result = fn(args)
    return result, buffer.getvalue()


def _cli_probe():
    args = Namespace(
        func=fantasy.cmd_score,
        kind="offense",
        stats='{"passing_yards":250,"passing_tds":2,"interceptions":1}',
    )

    def capture_args():
        return copy.deepcopy(vars(args))

    def restore_args(state):
        vars(args).clear()
        vars(args).update(copy.deepcopy(state))

    gate = benchmark_pair(
        lambda: _capture_score(fantasy.cmd_score, args),
        lambda: _capture_score(
            fantasy.dispatch_command,
            args,
        ),
        budget=BUDGET,
        probes=(
            python_random_probe(),
            StateProbe("cli_args", capture_args, restore_args),
        ),
    )
    gate.require_pass()
    return {
        "gate": gate.to_dict(),
        "shadow_event_count": len(last_cli_shadow_events()),
        "persistent": False,
    }


def _service_probe():
    service = SeasonGuiService.__new__(SeasonGuiService)
    service.snapshot = {
        "source_status": {
            "espn": {"ok": True},
            "sleeper": {"ok": True},
        }
    }
    service.model = {}
    service._observability_shadow = ShadowRecorder(root_subsystem="gui")

    def capture_state():
        return (
            copy.deepcopy(service.snapshot),
            copy.deepcopy(service.model),
        )

    def restore_state(state):
        service.snapshot = copy.deepcopy(state[0])
        service.model = copy.deepcopy(state[1])

    gate = benchmark_pair(
        lambda: SeasonGuiService.source_health.__wrapped__(service),
        lambda: service.source_health(),
        budget=BUDGET,
        probes=(
            python_random_probe(),
            StateProbe(
                "season_service_state",
                capture_state,
                restore_state,
            ),
        ),
    )
    gate.require_pass()
    return {
        "gate": gate.to_dict(),
        "shadow_event_count": len(service.observability_events()),
        "persistent": False,
    }


def main() -> int:
    result = {
        "schema": 1,
        "pilot": "cli_and_season_gui_service",
        "cli": _cli_probe(),
        "season_service": _service_probe(),
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
