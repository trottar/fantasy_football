from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import random

import numpy as np

from src.market_manager import TRADE_RESPONSE_MODEL, trade_response_probabilities
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.behavior_shadow import (
    clear_behavior_shadow_events,
    last_behavior_shadow_events,
)
from src.observability.integration_plan import DEFAULT_INTEGRATION_PLAN


BOUNDARY = "subsystem.behavior.trade_response_probabilities"
PRIVATE_ARG = "PRIVATE_BEHAVIOR_PROBE_ARG_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_BEHAVIOR_PROBE_ERROR_DO_NOT_CAPTURE"


def numpy_probe() -> StateProbe:
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


def cfg_probe(cfg: dict, label: str) -> StateProbe:
    def capture():
        return copy.deepcopy(cfg)

    def restore(state):
        cfg.clear()
        cfg.update(copy.deepcopy(state))

    return StateProbe(label, capture, restore)


def structure_ok() -> bool:
    tree = ast.parse(Path("src/market_manager.py").read_text(encoding="utf-8"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    target = funcs["trade_response_probabilities"]
    if len(target.decorator_list) != 1:
        return False
    dec = target.decorator_list[0]
    if not (
        isinstance(dec, ast.Call)
        and isinstance(dec.func, ast.Name)
        and dec.func.id == "shadow_behavior_call"
        and len(dec.args) == 1
        and isinstance(dec.args[0], ast.Constant)
        and dec.args[0].value == BOUNDARY
    ):
        return False

    for name in ("search_trades", "evaluate_trade", "perceived_market_value"):
        if any(
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Name)
            and d.func.id == "shadow_behavior_call"
            for d in funcs[name].decorator_list
        ):
            return False

    if BOUNDARY not in DEFAULT_INTEGRATION_PLAN.names:
        return False
    if "subsystem.trade.search" in DEFAULT_INTEGRATION_PLAN.names:
        return False
    point = DEFAULT_INTEGRATION_PLAN.require(BOUNDARY)
    return (
        point.subsystem == "behavior"
        and point.source_path == "src/market_manager.py"
        and point.symbol == "trade_response_probabilities"
        and point.automatic_emit is False
        and point.persistent is False
    )


def run_gate(label: str, kwargs: dict) -> dict:
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
        budget=OverheadBudget(trials=60, warmups=10),
        probes=(python_random_probe(), numpy_probe(), cfg_probe(cfg, label)),
    )
    return gate.to_dict()


def main() -> int:
    clear_behavior_shadow_events()
    cases = {
        "favorable": dict(
            partner_delta_season_ppg=0.8,
            partner_p_better=0.72,
            partner_market_delta=0.4,
            package_size=2,
        ),
        "boundary": dict(
            partner_delta_season_ppg=0.0,
            partner_p_better=0.5,
            partner_market_delta=0.0,
            package_size=2,
        ),
        "adverse_complex": dict(
            partner_delta_season_ppg=-0.8,
            partner_p_better=0.3,
            partner_market_delta=-0.5,
            package_size=4,
        ),
    }
    gates = {label: run_gate(label, kwargs) for label, kwargs in cases.items()}

    cfg = {"private": PRIVATE_ARG}
    error_call = dict(
        partner_delta_season_ppg=0.0,
        partner_p_better=0.5,
        partner_market_delta=0.0,
        package_size=PRIVATE_ERROR,
        cfg=cfg,
    )

    def error_baseline():
        return trade_response_probabilities.__wrapped__(**error_call)

    def error_observed():
        return trade_response_probabilities(**error_call)

    random.seed(20260924)
    np.random.seed(20260924)
    error_gate = benchmark_pair(
        error_baseline,
        error_observed,
        budget=OverheadBudget(trials=60, warmups=10),
        probes=(python_random_probe(), numpy_probe(), cfg_probe(cfg, "error")),
    ).to_dict()

    rendered = "\n".join(event.to_json() for event in last_behavior_shadow_events())
    privacy_ok = PRIVATE_ARG not in rendered and PRIVATE_ERROR not in rendered
    event_subsystems_ok = all(
        event.context.subsystem == "behavior"
        for event in last_behavior_shadow_events()
    )
    model_ok = TRADE_RESPONSE_MODEL == "UNCALIBRATED_TRADE_RESPONSE_V030"
    structure = structure_ok()
    passed = (
        structure
        and privacy_ok
        and event_subsystems_ok
        and model_ok
        and all(g["passed"] for g in gates.values())
        and error_gate["passed"]
    )
    result = {
        "boundary": BOUNDARY,
        "model": TRADE_RESPONSE_MODEL,
        "structure_ok": structure,
        "privacy_ok": privacy_ok,
        "event_subsystems_ok": event_subsystems_ok,
        "persistent_sink": False,
        "gates": gates,
        "controlled_error_gate": error_gate,
        "passed": passed,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
