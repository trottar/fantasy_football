from __future__ import annotations

import asyncio
import random
from pathlib import Path

import pytest

from src.observability.benchmark_gate import (
    OverheadBudget,
    benchmark_pair,
    python_random_probe,
)
from src.observability.gui_shadow import (
    GuiShadowRecorder,
    create_gui_shadow_recorder,
    last_gui_shadow_events,
)


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


def test_gui_page_lifecycle_uses_generated_correlation_only():
    recorder = create_gui_shadow_recorder()
    page = recorder.open_page()
    page.client_connect()
    page.client_disconnect()
    page.page_unmount()

    events = recorder.snapshot()
    names = [event.event_name for event in events]
    assert names == [
        "gui.page.mount",
        "gui.client.connect",
        "gui.client.disconnect",
        "gui.page.unmount",
    ]
    assert tuple(events) == last_gui_shadow_events()
    rendered = _event_json(events)
    assert page.session_id in rendered
    assert page.page_id in rendered
    assert "client_id" not in rendered


def test_gui_background_task_preserves_result_and_parent_lineage():
    recorder = GuiShadowRecorder()
    page = recorder.open_page()
    marker = {"private": "DO_NOT_CAPTURE"}

    async def work():
        return marker

    result = asyncio.run(
        page.observe_background_task("season.apply_mc_size", work())
    )
    assert result is marker

    events = recorder.snapshot()
    start = next(event for event in events if event.event_name == "action.start")
    assert start.context.parent_action_id == page.page_id
    assert start.context.run_id == page.context.run_id
    rendered = _event_json(events)
    assert "DO_NOT_CAPTURE" not in rendered
    assert "duration_ns" in rendered


def test_gui_background_task_error_message_is_not_recorded():
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def fail():
        raise ValueError("PRIVATE_GUI_ERROR")

    with pytest.raises(ValueError, match="PRIVATE_GUI_ERROR"):
        asyncio.run(
            page.observe_background_task("season.failure", fail())
        )

    rendered = _event_json(recorder.snapshot())
    assert "PRIVATE_GUI_ERROR" not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_gui_background_task_cancellation_is_preserved():
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def run_cancel():
        gate = asyncio.Event()

        async def wait_forever():
            await gate.wait()

        task = asyncio.create_task(
            page.observe_background_task(
                "season.progress_pump",
                wait_forever(),
            )
        )
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_cancel())
    assert "gui.task.cancel" in [
        event.event_name for event in recorder.snapshot()
    ]


def test_gui_stale_page_terminal_is_evidence_not_control_flow():
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def work():
        await asyncio.sleep(0)
        return 23

    observed = page.observe_background_task("season.stale", work())
    page.page_unmount()
    assert asyncio.run(observed) == 23

    events = recorder.snapshot()
    violations = [
        event
        for event in events
        if event.event_name == "gui.lifecycle.violation"
    ]
    assert len(violations) == 1
    assert (
        violations[0].payload["invariant"]
        == "gui.no_task_terminal_after_page_delete"
    )


def test_gui_observer_failure_falls_back_to_original_awaitable(monkeypatch):
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def work():
        return 31

    def broken_emit(_event):
        raise RuntimeError("observer-only")

    monkeypatch.setattr(recorder, "_emit", broken_emit)
    awaitable = work()
    wrapped = page.observe_background_task("season.fallback", awaitable)
    assert wrapped is awaitable
    assert asyncio.run(wrapped) == 31
    assert recorder.observer_failures >= 1


def test_gui_shadow_does_not_advance_python_random_state():
    random.seed(20260917)
    before = random.getstate()
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def work():
        return 5

    assert asyncio.run(
        page.observe_background_task("season.rng", work())
    ) == 5
    assert random.getstate() == before


def test_gui_task_pair_passes_non_interference_overhead_gate():
    recorder = GuiShadowRecorder()
    page = recorder.open_page()

    async def work():
        await asyncio.sleep(0)
        return 7

    gate = benchmark_pair(
        lambda: asyncio.run(work()),
        lambda: asyncio.run(
            page.observe_background_task("season.benchmark", work())
        ),
        budget=OverheadBudget(
            max_incremental_ns=2_000_000,
            max_relative_fraction=0.20,
            relative_floor_ns=5_000_000,
            trials=20,
            warmups=3,
        ),
        probes=(python_random_probe(),),
    )
    assert gate.passed


def test_season_app_wires_only_selected_mc_and_progress_pump_tasks():
    source = Path("src/gui/season_app.py").read_text(encoding="utf-8")
    for token in (
        "create_gui_shadow_recorder",
        "shadow_page = gui_shadow.open_page()",
        "page_shadow = shadow_page",
        "client.on_connect",
        "client.on_disconnect",
        "client.on_delete",
        "def observe_task(name: str, awaitable)",
        "season.apply_mc_size",
        "season.mc_progress_pump",
        "_apply_mc_size_observed_body",
        "_progress_pump_observed_body",
        "background_tasks.create(apply_mc_size(new_n))",
        "asyncio.create_task(progress_pump())",
    ):
        assert token in source
    assert "gui_shadow.client_id" not in source
