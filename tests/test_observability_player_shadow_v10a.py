from __future__ import annotations

import ast
import copy
from pathlib import Path
import random

import numpy as np
import pytest

from src.observability.benchmark_gate import OverheadBudget, StateProbe, benchmark_pair, python_random_probe
from src.observability.player_shadow import (
    clear_player_shadow_events,
    last_player_shadow_events,
    shadow_player_call,
)
import src.observability.player_shadow as player_shadow


PRIVATE_ARG = "PRIVATE_PLAYER_ARG_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_PLAYER_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_PLAYER_ERROR_DO_NOT_CAPTURE"


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


def _numpy_random_probe() -> StateProbe:
    def capture():
        name, keys, pos, has_gauss, cached = np.random.get_state()
        return (str(name), tuple(int(x) for x in keys.tolist()), int(pos), int(has_gauss), float(cached))

    def restore(state):
        name, keys, pos, has_gauss, cached = state
        np.random.set_state((name, np.array(keys, dtype="uint32"), int(pos), int(has_gauss), float(cached)))

    return StateProbe("numpy_random", capture, restore)


def _mutable_probe(payload: dict, mutable: dict, name: str) -> StateProbe:
    def capture():
        return copy.deepcopy((payload, mutable))

    def restore(state):
        payload_state, mutable_state = copy.deepcopy(state)
        payload.clear(); payload.update(payload_state)
        mutable.clear(); mutable.update(mutable_state)

    return StateProbe(name, capture, restore)


def _decorator_name(node: ast.FunctionDef) -> tuple[str, str] | None:
    if len(node.decorator_list) != 1:
        return None
    dec = node.decorator_list[0]
    if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name) or len(dec.args) != 1:
        return None
    arg = dec.args[0]
    if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
        return None
    return dec.func.id, arg.value


def test_exact_two_player_boundaries_are_instrumented_and_complete_roster_boundary_is_not():
    tm_path = Path("src/transaction_manager.py")
    gui_path = Path("src/gui/season_service.py")
    tm = ast.parse(tm_path.read_text(encoding="utf-8"))
    gui = ast.parse(gui_path.read_text(encoding="utf-8"))

    tm_funcs = {n.name: n for n in tm.body if isinstance(n, ast.FunctionDef)}
    assert _decorator_name(tm_funcs["evaluate_actions"]) == (
        "shadow_player_call", "subsystem.player.evaluate_actions"
    )
    assert all(
        not (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "shadow_player_call")
        for d in tm_funcs["evaluate_roster_predictive"].decorator_list
    )

    season_cls = next(n for n in gui.body if isinstance(n, ast.ClassDef) and n.name == "SeasonGuiService")
    methods = {n.name: n for n in season_cls.body if isinstance(n, ast.FunctionDef)}
    assert _decorator_name(methods["evaluate_single_add_drop"]) == (
        "shadow_player_call", "subsystem.player.evaluate_single_add_drop"
    )

    tm_imports = {(n.module, a.name) for n in tm.body if isinstance(n, ast.ImportFrom) for a in n.names}
    gui_imports = {(n.module, a.name) for n in gui.body if isinstance(n, ast.ImportFrom) for a in n.names}
    assert ("observability.player_shadow", "shadow_player_call") in tm_imports
    assert ("observability.player_shadow", "shadow_player_call") in gui_imports


def test_player_shadow_success_privacy_and_shared_dual_surface_recorder():
    clear_player_shadow_events()

    @shadow_player_call("subsystem.player.evaluate_actions")
    def cli(payload):
        return {"private": PRIVATE_RESULT, "seen": payload["private"]}

    @shadow_player_call("subsystem.player.evaluate_single_add_drop")
    def gui(payload):
        return {"private": PRIVATE_RESULT, "seen": payload["private"]}

    payload = {"private": PRIVATE_ARG}
    assert cli(payload) == cli.__wrapped__(payload)
    assert gui(payload) == gui.__wrapped__(payload)
    events = last_player_shadow_events()
    assert [e.event_name for e in events[-4:]] == ["action.start", "action.complete", "action.start", "action.complete"]
    assert all(e.context.subsystem == "player" for e in events[-4:])
    rendered = _event_json(events[-4:])
    assert "subsystem.player.evaluate_actions" in rendered
    assert "subsystem.player.evaluate_single_add_drop" in rendered
    assert PRIVATE_ARG not in rendered
    assert PRIVATE_RESULT not in rendered
    assert "duration_ns" in rendered


def test_player_shadow_error_omits_message_and_preserves_exception_type():
    clear_player_shadow_events()

    @shadow_player_call("subsystem.player.evaluate_actions")
    def fail(_payload):
        raise ValueError(PRIVATE_ERROR)

    with pytest.raises(ValueError, match=PRIVATE_ERROR):
        fail({"private": PRIVATE_ARG})
    rendered = _event_json(last_player_shadow_events())
    assert PRIVATE_ERROR not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_player_observer_emit_failure_is_non_interfering(monkeypatch):
    clear_player_shadow_events()
    recorder = player_shadow._player_shadow_recorder()
    assert recorder is not None

    @shadow_player_call("subsystem.player.evaluate_single_add_drop")
    def fn(value):
        return value + 1

    monkeypatch.setattr(recorder, "_emit", lambda _event: (_ for _ in ()).throw(RuntimeError("observer-only")))
    assert fn(4) == 5
    assert recorder.observer_failures >= 1


@pytest.mark.parametrize("boundary", [
    "subsystem.player.evaluate_actions",
    "subsystem.player.evaluate_single_add_drop",
])
def test_each_player_surface_passes_paired_rng_mutable_state_and_overhead_gate(boundary):
    clear_player_shadow_events()
    payload = {"private": PRIVATE_ARG}
    mutable = {"calls": 0}

    def direct():
        mutable["calls"] += 1
        return {
            "private": PRIVATE_RESULT,
            "python": random.random(),
            "numpy": float(np.random.random()),
            "arg": payload["private"],
        }

    observed_fn = shadow_player_call(boundary)(direct)
    random.seed(20260922)
    np.random.seed(20260922)
    gate = benchmark_pair(
        direct,
        observed_fn,
        budget=OverheadBudget(),
        probes=(python_random_probe(), _numpy_random_probe(), _mutable_probe(payload, mutable, boundary)),
    )
    assert gate.passed, gate.to_dict()
    rendered = _event_json(last_player_shadow_events())
    assert PRIVATE_ARG not in rendered
    assert PRIVATE_RESULT not in rendered
