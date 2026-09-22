from __future__ import annotations

import ast
import copy
from pathlib import Path
import random
from types import SimpleNamespace

import pytest

from src import closure
from src import prospective_measurement_v034 as measurement
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.closure_shadow import (
    clear_closure_shadow_events,
    last_closure_shadow_events,
)
import src.observability.closure_shadow as closure_shadow


PRIVATE_SNAPSHOT = "PRIVATE_CLOSURE_SNAPSHOT_DO_NOT_CAPTURE"
PRIVATE_MODEL = "PRIVATE_CLOSURE_MODEL_DO_NOT_CAPTURE"
PRIVATE_TEAM = "PRIVATE_CLOSURE_TEAM_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_CLOSURE_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_CLOSURE_ERROR_DO_NOT_CAPTURE"
CAPTURED_UTC = "2026-09-22T16:00:00+00:00"


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


def _inputs():
    snapshot = {
        "espn": {"season": 2026, "week": 3},
        "private_marker": PRIVATE_SNAPSHOT,
    }
    model = {"private_marker": PRIVATE_MODEL}
    ctx = SimpleNamespace(
        all_team_rosters={},
        espn={"teams": []},
    )
    team = {"team_id": 1, "name": PRIVATE_TEAM}
    return snapshot, model, ctx, team


def _install_success_stubs(monkeypatch):
    def fake_base(snapshot, model, ctx, team, *, captured_utc=None):
        return {
            "captured_utc": captured_utc,
            "private_result": PRIVATE_RESULT,
            "team_name": team["name"],
            "snapshot_marker": snapshot["private_marker"],
            "model_marker": model["private_marker"],
        }

    def fake_enrich(base, snapshot, model, ctx, team):
        out = dict(base)
        out["enriched"] = True
        return out

    monkeypatch.setattr(
        closure,
        "_build_pregame_capture_from_context_pre_v034",
        fake_base,
    )
    monkeypatch.setattr(measurement, "enrich_pregame_capture", fake_enrich)


def _call(snapshot, model, ctx, team):
    return closure.build_pregame_capture_from_context(
        snapshot,
        model,
        ctx,
        team,
        captured_utc=CAPTURED_UTC,
    )


def _direct(snapshot, model, ctx, team):
    return closure.build_pregame_capture_from_context.__wrapped__(
        snapshot,
        model,
        ctx,
        team,
        captured_utc=CAPTURED_UTC,
    )


def _state_probe(snapshot, model, ctx, team) -> StateProbe:
    def capture():
        return copy.deepcopy(
            (
                snapshot,
                model,
                team,
                ctx.all_team_rosters,
                ctx.espn,
            )
        )

    def restore(state):
        snapshot_state, model_state, team_state, all_rosters_state, espn_state = copy.deepcopy(state)
        snapshot.clear()
        snapshot.update(snapshot_state)
        model.clear()
        model.update(model_state)
        team.clear()
        team.update(team_state)
        ctx.all_team_rosters = all_rosters_state
        ctx.espn = espn_state

    return StateProbe("closure_inputs", capture, restore)


def test_final_v034_boundary_is_the_only_decorated_closure_definition():
    source = Path("src/closure.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    funcs = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "build_pregame_capture_from_context"
    ]
    assert len(funcs) == 2
    assert not funcs[0].decorator_list
    assert len(funcs[1].decorator_list) == 1
    decorator = funcs[1].decorator_list[0]
    assert isinstance(decorator, ast.Call)
    assert isinstance(decorator.func, ast.Name)
    assert decorator.func.id == "shadow_closure_call"
    assert len(decorator.args) == 1
    assert isinstance(decorator.args[0], ast.Constant)
    assert decorator.args[0].value == "subsystem.closure.capture"

    aliases = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "_build_pregame_capture_from_context_pre_v034"
            for target in node.targets
        )
    ]
    assert len(aliases) == 1
    assert funcs[0].lineno < aliases[0].lineno < funcs[1].lineno

    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "observability.closure_shadow"
        and any(alias.name == "shadow_closure_call" for alias in node.names)
    ]
    assert len(imports) == 1


def test_closure_shadow_success_preserves_output_and_omits_private_data(monkeypatch):
    _install_success_stubs(monkeypatch)
    clear_closure_shadow_events()
    snapshot, model, ctx, team = _inputs()

    observed = _call(snapshot, model, ctx, team)
    direct = _direct(snapshot, model, ctx, team)

    assert observed == direct
    assert observed["private_result"] == PRIVATE_RESULT
    events = last_closure_shadow_events()
    assert [event.event_name for event in events[-2:]] == [
        "action.start",
        "action.complete",
    ]
    assert all(event.context.subsystem == "closure" for event in events[-2:])
    rendered = _event_json(events[-2:])
    assert "subsystem.closure.capture" in rendered
    assert '"boundary_kind":"subsystem"' in rendered
    for private in (
        PRIVATE_SNAPSHOT,
        PRIVATE_MODEL,
        PRIVATE_TEAM,
        PRIVATE_RESULT,
    ):
        assert private not in rendered
    assert "duration_ns" in rendered


def test_closure_shadow_error_preserves_exception_and_omits_message(monkeypatch):
    clear_closure_shadow_events()

    def fail(*_args, **_kwargs):
        raise ValueError(PRIVATE_ERROR)

    monkeypatch.setattr(
        closure,
        "_build_pregame_capture_from_context_pre_v034",
        fail,
    )

    snapshot, model, ctx, team = _inputs()
    with pytest.raises(ValueError, match=PRIVATE_ERROR):
        _call(snapshot, model, ctx, team)

    rendered = _event_json(last_closure_shadow_events())
    assert PRIVATE_ERROR not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_closure_observer_emit_failure_does_not_change_production_result(monkeypatch):
    _install_success_stubs(monkeypatch)
    clear_closure_shadow_events()
    recorder = closure_shadow._closure_shadow_recorder()
    assert recorder is not None

    def broken_emit(_event):
        raise RuntimeError("observer-only failure")

    monkeypatch.setattr(recorder, "_emit", broken_emit)
    snapshot, model, ctx, team = _inputs()
    observed = _call(snapshot, model, ctx, team)
    direct = _direct(snapshot, model, ctx, team)
    assert observed == direct
    assert recorder.observer_failures >= 1


def test_closure_shadow_does_not_advance_python_random_state(monkeypatch):
    _install_success_stubs(monkeypatch)
    clear_closure_shadow_events()
    snapshot, model, ctx, team = _inputs()
    random.seed(20260922)
    before = random.getstate()
    _call(snapshot, model, ctx, team)
    assert random.getstate() == before


def test_closure_shadow_passes_paired_state_rng_and_overhead_gate(monkeypatch):
    _install_success_stubs(monkeypatch)
    clear_closure_shadow_events()
    snapshot, model, ctx, team = _inputs()

    gate = benchmark_pair(
        lambda: _direct(snapshot, model, ctx, team),
        lambda: _call(snapshot, model, ctx, team),
        budget=OverheadBudget(
            max_incremental_ns=2_000_000,
            max_relative_fraction=0.20,
            relative_floor_ns=50_000_000,
            trials=25,
            warmups=3,
        ),
        probes=(
            python_random_probe(),
            _state_probe(snapshot, model, ctx, team),
        ),
    )
    assert gate.passed, gate.to_dict()
