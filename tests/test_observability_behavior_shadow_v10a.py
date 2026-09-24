from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import random

import numpy as np
import pytest

from src.market_manager import (
    TRADE_RESPONSE_MODEL,
    trade_response_probabilities,
)
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.behavior_shadow import (
    clear_behavior_shadow_events,
    last_behavior_shadow_events,
    shadow_behavior_call,
)
import src.observability.behavior_shadow as behavior_shadow
from src.observability.integration_plan import DEFAULT_INTEGRATION_PLAN


BOUNDARY = "subsystem.behavior.trade_response_probabilities"
PRIVATE_ARG = "PRIVATE_BEHAVIOR_ARG_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_BEHAVIOR_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_BEHAVIOR_ERROR_DO_NOT_CAPTURE"


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
            (name, np.array(keys, dtype="uint32"), int(pos), int(has_gauss), float(cached))
        )

    return StateProbe("numpy_random", capture, restore)


def _cfg_probe(cfg: dict, name: str) -> StateProbe:
    def capture():
        return copy.deepcopy(cfg)

    def restore(state):
        cfg.clear()
        cfg.update(copy.deepcopy(state))

    return StateProbe(name, capture, restore)


def _decorator(node: ast.FunctionDef) -> tuple[str, str] | None:
    if len(node.decorator_list) != 1:
        return None
    dec = node.decorator_list[0]
    if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name):
        return None
    if len(dec.args) != 1:
        return None
    arg = dec.args[0]
    if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
        return None
    return dec.func.id, arg.value


def test_only_narrow_trade_response_kernel_is_behavior_instrumented():
    tree = ast.parse(Path("src/market_manager.py").read_text(encoding="utf-8"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    assert _decorator(funcs["trade_response_probabilities"]) == (
        "shadow_behavior_call",
        BOUNDARY,
    )

    for name in ("search_trades", "evaluate_trade", "perceived_market_value"):
        assert all(
            not (
                isinstance(d, ast.Call)
                and isinstance(d.func, ast.Name)
                and d.func.id == "shadow_behavior_call"
            )
            for d in funcs[name].decorator_list
        )

    imports = {
        (node.module, alias.name)
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert ("observability.behavior_shadow", "shadow_behavior_call") in imports


def test_integration_plan_names_behavior_kernel_not_mixed_trade_search():
    assert BOUNDARY in DEFAULT_INTEGRATION_PLAN.names
    assert "subsystem.trade.search" not in DEFAULT_INTEGRATION_PLAN.names
    point = DEFAULT_INTEGRATION_PLAN.require(BOUNDARY)
    assert point.subsystem == "behavior"
    assert point.source_path == "src/market_manager.py"
    assert point.symbol == "trade_response_probabilities"
    assert point.automatic_emit is False
    assert point.persistent is False


def test_behavior_shadow_success_privacy_and_model_contract():
    clear_behavior_shadow_events()
    cfg = {"private": PRIVATE_ARG}
    result = trade_response_probabilities(
        partner_delta_season_ppg=0.5,
        partner_p_better=0.7,
        partner_market_delta=0.2,
        package_size=2,
        cfg=cfg,
    )
    baseline = trade_response_probabilities.__wrapped__(
        partner_delta_season_ppg=0.5,
        partner_p_better=0.7,
        partner_market_delta=0.2,
        package_size=2,
        cfg=cfg,
    )
    assert result == baseline
    assert result.model == TRADE_RESPONSE_MODEL == "UNCALIBRATED_TRADE_RESPONSE_V030"
    assert abs(result.p_accept + result.p_counter + result.p_reject - 1.0) < 1e-12
    events = last_behavior_shadow_events()
    assert [e.event_name for e in events[-2:]] == ["action.start", "action.complete"]
    assert all(e.context.subsystem == "behavior" for e in events[-2:])
    rendered = _event_json(events[-2:])
    assert BOUNDARY in rendered
    assert PRIVATE_ARG not in rendered
    assert PRIVATE_RESULT not in rendered
    assert "duration_ns" in rendered


def test_behavior_shadow_error_omits_message_and_preserves_exception_type():
    clear_behavior_shadow_events()
    cfg = {"private": PRIVATE_ARG}
    with pytest.raises(ValueError):
        trade_response_probabilities(
            partner_delta_season_ppg=0.0,
            partner_p_better=0.5,
            partner_market_delta=0.0,
            package_size=PRIVATE_ERROR,
            cfg=cfg,
        )
    rendered = _event_json(last_behavior_shadow_events())
    assert PRIVATE_ERROR not in rendered
    assert PRIVATE_ARG not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_behavior_observer_emit_failure_is_non_interfering(monkeypatch):
    clear_behavior_shadow_events()
    recorder = behavior_shadow._behavior_shadow_recorder()
    assert recorder is not None
    kwargs = dict(
        partner_delta_season_ppg=0.4,
        partner_p_better=0.6,
        partner_market_delta=0.2,
        package_size=2,
        cfg={},
    )
    expected = trade_response_probabilities.__wrapped__(**kwargs)
    monkeypatch.setattr(
        recorder,
        "_emit",
        lambda _event: (_ for _ in ()).throw(RuntimeError("observer-only")),
    )
    assert trade_response_probabilities(**kwargs) == expected
    assert recorder.observer_failures >= 1


@pytest.mark.parametrize(
    "label,kwargs",
    [
        (
            "favorable",
            dict(
                partner_delta_season_ppg=0.8,
                partner_p_better=0.72,
                partner_market_delta=0.4,
                package_size=2,
            ),
        ),
        (
            "boundary",
            dict(
                partner_delta_season_ppg=0.0,
                partner_p_better=0.5,
                partner_market_delta=0.0,
                package_size=2,
            ),
        ),
        (
            "adverse_complex",
            dict(
                partner_delta_season_ppg=-0.8,
                partner_p_better=0.3,
                partner_market_delta=-0.5,
                package_size=4,
            ),
        ),
    ],
)
def test_behavior_boundary_passes_paired_rng_config_and_overhead_gate(label, kwargs):
    clear_behavior_shadow_events()
    cfg = {"private": PRIVATE_ARG}
    call = dict(kwargs, cfg=cfg)

    def baseline():
        return trade_response_probabilities.__wrapped__(**call)

    def observed():
        return trade_response_probabilities(**call)

    random.seed(20260923)
    np.random.seed(20260923)
    gate = benchmark_pair(
        baseline,
        observed,
        budget=OverheadBudget(trials=30, warmups=3),
        probes=(
            python_random_probe(),
            _numpy_random_probe(),
            _cfg_probe(cfg, f"cfg_{label}"),
        ),
    )
    assert gate.passed, gate.to_dict()
    rendered = _event_json(last_behavior_shadow_events())
    assert PRIVATE_ARG not in rendered
