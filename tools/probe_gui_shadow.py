from __future__ import annotations

import asyncio
import json

from src.observability.benchmark_gate import (
    OverheadBudget,
    benchmark_pair,
    python_random_probe,
)
from src.observability.gui_shadow import GuiShadowRecorder


BUDGET = OverheadBudget(
    max_incremental_ns=2_000_000,
    max_relative_fraction=0.20,
    relative_floor_ns=5_000_000,
    trials=30,
    warmups=5,
)


def _run(coro):
    return asyncio.run(coro)


async def _value():
    await asyncio.sleep(0)
    return 11


def main() -> int:
    recorder = GuiShadowRecorder()
    page = recorder.open_page()
    page.client_connect()

    gate = benchmark_pair(
        lambda: _run(_value()),
        lambda: _run(
            page.observe_background_task(
                "season.apply_mc_size",
                _value(),
            )
        ),
        budget=BUDGET,
        probes=(python_random_probe(),),
    )
    gate.require_pass()

    async def cancellation_probe():
        blocker = asyncio.Event()

        async def wait():
            await blocker.wait()

        task = asyncio.create_task(
            page.observe_background_task(
                "season.mc_progress_pump",
                wait(),
            )
        )
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return True
        return False

    if not _run(cancellation_probe()):
        raise RuntimeError("cancellation propagation probe failed")

    async def stale_probe():
        await asyncio.sleep(0)
        return 19

    stale = page.observe_background_task("season.stale_probe", stale_probe())
    page.page_unmount()
    if _run(stale) != 19:
        raise RuntimeError("stale-page result changed")

    events = recorder.snapshot()
    names = [event.event_name for event in events]
    if "gui.task.cancel" not in names:
        raise RuntimeError("missing task cancellation event")
    if "gui.lifecycle.violation" not in names:
        raise RuntimeError("missing stale-page lifecycle evidence")

    print(
        json.dumps(
            {
                "schema": 1,
                "pilot": "gui_background_task_lifecycle",
                "gate": gate.to_dict(),
                "event_count": len(events),
                "observer_failures": recorder.observer_failures,
                "persistent": False,
                "captures_client_id": False,
                "captures_results": False,
                "captures_exception_messages": False,
                "cancellation_preserved": True,
                "stale_result_preserved": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
