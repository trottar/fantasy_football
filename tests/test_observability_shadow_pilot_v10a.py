from __future__ import annotations

from argparse import Namespace
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
import random

import pytest

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
    shadow_service_call,
)


def _event_json(events):
    return "\n".join(event.to_json() for event in events)


def test_shadow_success_preserves_result_without_recording_return_value():
    recorder = ShadowRecorder(root_subsystem="observability")
    secret_result = {"private_result": "DO_NOT_CAPTURE"}

    result = recorder.call_cli("unit.success", lambda: secret_result)

    assert result is secret_result
    events = recorder.snapshot()
    assert [event.event_name for event in events] == [
        "action.start",
        "action.complete",
    ]
    rendered = _event_json(events)
    assert "DO_NOT_CAPTURE" not in rendered
    assert "duration_ns" in rendered


def test_shadow_error_preserves_exception_message_but_event_omits_it():
    recorder = ShadowRecorder(root_subsystem="observability")

    def fail():
        raise ValueError("PRIVATE_EXCEPTION_MESSAGE")

    with pytest.raises(ValueError, match="PRIVATE_EXCEPTION_MESSAGE"):
        recorder.call_cli("unit.error", fail)

    rendered = _event_json(recorder.snapshot())
    assert "PRIVATE_EXCEPTION_MESSAGE" not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_observer_failure_cannot_change_wrapped_result(monkeypatch):
    recorder = ShadowRecorder(root_subsystem="observability")

    def broken_emit(_event):
        raise RuntimeError("observer-only failure")

    monkeypatch.setattr(recorder, "_emit", broken_emit)
    assert recorder.call_cli("unit.emit_failure", lambda: 17) == 17
    assert recorder.observer_failures >= 1


def test_shadow_recorder_does_not_advance_python_random_state():
    random.seed(20260917)
    before = random.getstate()

    recorder = ShadowRecorder(root_subsystem="observability")
    recorder.call_cli("unit.rng", lambda: 3)

    assert random.getstate() == before


def test_shadow_buffer_is_bounded():
    recorder = ShadowRecorder(
        root_subsystem="observability",
        max_events=4,
    )
    for index in range(3):
        recorder.call_cli(f"unit.call_{index}", lambda: None)

    events = recorder.snapshot()
    assert len(events) == 4
    assert events[0].event_name == "action.start"
    assert events[-1].event_name == "action.complete"


def test_nested_service_calls_preserve_parent_action_lineage():
    recorder = ShadowRecorder(root_subsystem="gui")

    def inner():
        return recorder.call_service(
            "service.inner",
            lambda: "inner",
        )

    assert recorder.call_service("service.outer", inner) == "inner"

    events = recorder.snapshot()
    starts = [event for event in events if event.event_name == "action.start"]
    assert len(starts) == 2
    outer, inner_start = starts
    assert outer.context.parent_action_id is None
    assert inner_start.context.parent_action_id == outer.context.action_id
    assert inner_start.context.run_id == outer.context.run_id


def _capture_score(fn, args):
    buffer = StringIO()
    with redirect_stdout(buffer):
        result = fn(args)
    return result, buffer.getvalue()


def test_cli_dispatch_shadow_preserves_real_cmd_score_output():
    args = Namespace(
        func=fantasy.cmd_score,
        kind="offense",
        stats=json.dumps(
            {
                "passing_yards": 250,
                "passing_tds": 2,
                "interceptions": 1,
                "private_marker": "CLI_SECRET_SHOULD_NOT_APPEAR",
            }
        ),
    )

    direct = _capture_score(fantasy.cmd_score, args)
    observed = _capture_score(
        fantasy.dispatch_command,
        args,
    )

    assert observed == direct
    rendered = _event_json(last_cli_shadow_events())
    assert "CLI_SECRET_SHOULD_NOT_APPEAR" not in rendered


def test_cli_dispatch_shadow_passes_paired_non_interference_gate():
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
        budget=OverheadBudget(
            max_incremental_ns=1_000_000,
            max_relative_fraction=0.10,
            relative_floor_ns=5_000_000,
            trials=20,
            warmups=3,
        ),
        probes=(
            python_random_probe(),
            StateProbe(
                "cli_args",
                capture_args,
                restore_args,
            ),
        ),
    )

    assert gate.passed


def _service_fixture():
    service = SeasonGuiService.__new__(SeasonGuiService)
    service.snapshot = {
        "source_status": {
            "espn": {"ok": True},
            "sleeper": {"ok": True},
        }
    }
    service.model = {}
    service._observability_shadow = ShadowRecorder(root_subsystem="gui")
    return service


def test_season_service_source_health_shadow_preserves_result():
    service = _service_fixture()

    direct = SeasonGuiService.source_health.__wrapped__(service)
    observed = service.source_health()

    assert observed == direct
    events = service.observability_events()
    assert isinstance(events, tuple)
    assert [event.event_name for event in events[-2:]] == [
        "action.start",
        "action.complete",
    ]
    rendered = _event_json(events)
    assert "source_status" not in rendered
    assert "sleeper" not in rendered


def test_season_service_source_health_passes_paired_gate():
    service = _service_fixture()

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
        budget=OverheadBudget(
            max_incremental_ns=1_000_000,
            max_relative_fraction=0.10,
            relative_floor_ns=5_000_000,
            trials=20,
            warmups=3,
        ),
        probes=(
            python_random_probe(),
            StateProbe(
                "season_service_state",
                capture_state,
                restore_state,
            ),
        ),
    )

    assert gate.passed


def test_service_decorator_falls_back_when_recorder_missing():
    class Service:
        @shadow_service_call("Service.value")
        def value(self):
            return 9

    assert Service().value() == 9
