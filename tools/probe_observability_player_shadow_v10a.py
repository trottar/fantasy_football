from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import random

import numpy as np

from src.observability.benchmark_gate import OverheadBudget, StateProbe, benchmark_pair, python_random_probe
from src.observability.player_shadow import clear_player_shadow_events, last_player_shadow_events, shadow_player_call

PRIVATE_ARG = "PRIVATE_PLAYER_PROBE_ARG_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_PLAYER_PROBE_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_PLAYER_PROBE_ERROR_DO_NOT_CAPTURE"


def numpy_probe() -> StateProbe:
    def capture():
        name, keys, pos, has_gauss, cached = np.random.get_state()
        return (str(name), tuple(int(x) for x in keys.tolist()), int(pos), int(has_gauss), float(cached))
    def restore(state):
        name, keys, pos, has_gauss, cached = state
        np.random.set_state((name, np.array(keys, dtype="uint32"), int(pos), int(has_gauss), float(cached)))
    return StateProbe("numpy_random", capture, restore)


def mutable_probe(payload, mutable, label) -> StateProbe:
    def capture(): return copy.deepcopy((payload, mutable))
    def restore(state):
        p, m = copy.deepcopy(state)
        payload.clear(); payload.update(p)
        mutable.clear(); mutable.update(m)
    return StateProbe(label, capture, restore)


def structure_ok() -> bool:
    tm = ast.parse(Path("src/transaction_manager.py").read_text(encoding="utf-8"))
    gui = ast.parse(Path("src/gui/season_service.py").read_text(encoding="utf-8"))
    tm_funcs = {n.name: n for n in tm.body if isinstance(n, ast.FunctionDef)}
    season_cls = next(n for n in gui.body if isinstance(n, ast.ClassDef) and n.name == "SeasonGuiService")
    methods = {n.name: n for n in season_cls.body if isinstance(n, ast.FunctionDef)}
    def has(fn, label):
        return len(fn.decorator_list) == 1 and isinstance(fn.decorator_list[0], ast.Call) and isinstance(fn.decorator_list[0].func, ast.Name) and fn.decorator_list[0].func.id == "shadow_player_call" and len(fn.decorator_list[0].args) == 1 and isinstance(fn.decorator_list[0].args[0], ast.Constant) and fn.decorator_list[0].args[0].value == label
    complete_roster_clean = all(not (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "shadow_player_call") for d in tm_funcs["evaluate_roster_predictive"].decorator_list)
    return has(tm_funcs["evaluate_actions"], "subsystem.player.evaluate_actions") and has(methods["evaluate_single_add_drop"], "subsystem.player.evaluate_single_add_drop") and complete_roster_clean


def run_gate(label: str) -> dict:
    payload = {"private": PRIVATE_ARG}
    mutable = {"calls": 0}
    def direct():
        mutable["calls"] += 1
        return {"private": PRIVATE_RESULT, "python": random.random(), "numpy": float(np.random.random()), "arg": payload["private"]}
    observed = shadow_player_call(label)(direct)
    random.seed(20260922); np.random.seed(20260922)
    gate = benchmark_pair(direct, observed, budget=OverheadBudget(), probes=(python_random_probe(), numpy_probe(), mutable_probe(payload, mutable, label)))
    return gate.to_dict()


def main() -> int:
    clear_player_shadow_events()
    labels = ["subsystem.player.evaluate_actions", "subsystem.player.evaluate_single_add_drop"]
    gates = {label: run_gate(label) for label in labels}

    @shadow_player_call(labels[0])
    def fail(): raise ValueError(PRIVATE_ERROR)
    try: fail()
    except ValueError: pass

    rendered = "\n".join(e.to_json() for e in last_player_shadow_events())
    privacy = PRIVATE_ARG not in rendered and PRIVATE_RESULT not in rendered and PRIVATE_ERROR not in rendered
    result = {
        "structure_ok": structure_ok(),
        "gates": gates,
        "privacy_ok": privacy,
        "persistent_sink": False,
        "passed": structure_ok() and privacy and all(g["passed"] for g in gates.values()),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
