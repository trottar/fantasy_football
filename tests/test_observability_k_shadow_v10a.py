from __future__ import annotations

import ast
import copy
from pathlib import Path
import random

import numpy as np
import pytest

import src.specialist_policy_v032 as specialist_policy
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.dst_shadow import (
    clear_dst_shadow_events,
    last_dst_shadow_events,
)
from src.observability.k_shadow import (
    clear_k_shadow_events,
    last_k_shadow_events,
)
import src.observability.k_shadow as k_shadow


PRIVATE_ARG = "PRIVATE_K_ARG_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_K_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_K_ERROR_DO_NOT_CAPTURE"


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


def _numpy_random_probe() -> StateProbe:
    def capture():
        name, keys, pos, has_gauss, cached = np.random.get_state()
        return (
            str(name),
            tuple(int(x) for x in keys.tolist()),
            int(pos),
            int(has_gauss),
            float(cached),
        )

    def restore(state):
        name, keys, pos, has_gauss, cached = state
        np.random.set_state(
            (
                name,
                np.array(keys, dtype="uint32"),
                int(pos),
                int(has_gauss),
                float(cached),
            )
        )

    return StateProbe("numpy_random", capture, restore)


def _input_probe(payload: dict, mutable: dict) -> StateProbe:
    def capture():
        return copy.deepcopy((payload, mutable))

    def restore(state):
        payload_state, mutable_state = copy.deepcopy(state)
        payload.clear()
        payload.update(payload_state)
        mutable.clear()
        mutable.update(mutable_state)

    return StateProbe("k_inputs", capture, restore)


def _call(payload, *, mode="TEST"):
    return specialist_policy.evaluate_kicker_channel(payload, mode=mode)


def _direct(payload, *, mode="TEST"):
    return specialist_policy.evaluate_kicker_channel.__wrapped__(
        payload,
        mode=mode,
    )


def _decorator_contract(fn_node, *, decorator_name: str, boundary: str) -> None:
    assert len(fn_node.decorator_list) == 1
    decorator = fn_node.decorator_list[0]
    assert isinstance(decorator, ast.Call)
    assert isinstance(decorator.func, ast.Name)
    assert decorator.func.id == decorator_name
    assert len(decorator.args) == 1
    assert isinstance(decorator.args[0], ast.Constant)
    assert decorator.args[0].value == boundary


def test_dst_and_k_wrappers_have_separate_shadow_decorators():
    source = Path("src/specialist_policy_v032.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    funcs = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in {"evaluate_defense_channel", "evaluate_kicker_channel"}
    }
    assert set(funcs) == {"evaluate_defense_channel", "evaluate_kicker_channel"}

    _decorator_contract(
        funcs["evaluate_defense_channel"],
        decorator_name="shadow_dst_call",
        boundary="subsystem.dst.channel",
    )
    _decorator_contract(
        funcs["evaluate_kicker_channel"],
        decorator_name="shadow_k_call",
        boundary="subsystem.k.channel",
    )

    imports = {
        (node.module, alias.name)
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert ("observability.dst_shadow", "shadow_dst_call") in imports
    assert ("observability.k_shadow", "shadow_k_call") in imports


def test_k_shadow_success_preserves_output_and_omits_private_data(monkeypatch):
    clear_k_shadow_events()
    payload = {"private": PRIVATE_ARG}

    def fake_policy(*args, position, **kwargs):
        assert position == "K"
        return {
            "position": position,
            "private_result": PRIVATE_RESULT,
            "private_arg": args[0]["private"],
            "mode": kwargs.get("mode"),
        }

    monkeypatch.setattr(specialist_policy, "_evaluate_policy_channel", fake_policy)

    observed = _call(payload)
    direct = _direct(payload)

    assert observed == direct
    assert observed["private_result"] == PRIVATE_RESULT

    events = last_k_shadow_events()
    assert [event.event_name for event in events[-2:]] == [
        "action.start",
        "action.complete",
    ]
    assert all(event.context.subsystem == "k" for event in events[-2:])
    rendered = _event_json(events[-2:])
    assert "subsystem.k.channel" in rendered
    assert '"boundary_kind":"subsystem"' in rendered
    assert PRIVATE_ARG not in rendered
    assert PRIVATE_RESULT not in rendered
    assert "duration_ns" in rendered


def test_k_shadow_error_preserves_exception_and_omits_message(monkeypatch):
    clear_k_shadow_events()

    def fail(*_args, position, **_kwargs):
        assert position == "K"
        raise ValueError(PRIVATE_ERROR)

    monkeypatch.setattr(specialist_policy, "_evaluate_policy_channel", fail)

    with pytest.raises(ValueError, match=PRIVATE_ERROR):
        _call({"private": PRIVATE_ARG})

    rendered = _event_json(last_k_shadow_events())
    assert PRIVATE_ERROR not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_k_observer_emit_failure_does_not_change_production_result(monkeypatch):
    clear_k_shadow_events()

    def fake_policy(*args, position, **kwargs):
        assert position == "K"
        return {
            "position": position,
            "private_result": PRIVATE_RESULT,
            "private_arg": args[0]["private"],
            "mode": kwargs.get("mode"),
        }

    monkeypatch.setattr(specialist_policy, "_evaluate_policy_channel", fake_policy)
    recorder = k_shadow._k_shadow_recorder()
    assert recorder is not None

    def broken_emit(_event):
        raise RuntimeError("observer-only failure")

    monkeypatch.setattr(recorder, "_emit", broken_emit)

    payload = {"private": PRIVATE_ARG}
    observed = _call(payload)
    direct = _direct(payload)
    assert observed == direct
    assert recorder.observer_failures >= 1


def test_defense_wrapper_emits_no_k_shadow_events(monkeypatch):
    clear_k_shadow_events()
    clear_dst_shadow_events()

    def fake_policy(*_args, position, **_kwargs):
        return {"position": position}

    monkeypatch.setattr(specialist_policy, "_evaluate_policy_channel", fake_policy)

    before = len(last_k_shadow_events())
    result = specialist_policy.evaluate_defense_channel({"private": PRIVATE_ARG})
    after = len(last_k_shadow_events())

    assert result == {"position": "DST"}
    assert after == before
    assert len(last_dst_shadow_events()) >= 2


def test_k_shadow_passes_paired_python_numpy_state_and_overhead_gate(monkeypatch):
    clear_k_shadow_events()
    payload = {"private": PRIVATE_ARG}
    mutable = {"calls": 0, "positions": []}

    def fake_policy(*args, position, **kwargs):
        assert position == "K"
        mutable["calls"] += 1
        mutable["positions"].append(position)
        return {
            "position": position,
            "private_result": PRIVATE_RESULT,
            "private_arg": args[0]["private"],
            "mode": kwargs.get("mode"),
            "python_random": random.random(),
            "numpy_random": float(np.random.random()),
        }

    monkeypatch.setattr(specialist_policy, "_evaluate_policy_channel", fake_policy)

    random.seed(20260922)
    np.random.seed(20260922)

    gate = benchmark_pair(
        lambda: _direct(payload, mode="PAIRED"),
        lambda: _call(payload, mode="PAIRED"),
        budget=OverheadBudget(),
        probes=(
            python_random_probe(),
            _numpy_random_probe(),
            _input_probe(payload, mutable),
        ),
    )
    assert gate.passed, gate.to_dict()
