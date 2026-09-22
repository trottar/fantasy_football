from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import random
import shutil
from types import SimpleNamespace
from unittest.mock import patch

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


PRIVATE_SNAPSHOT = "PRIVATE_PROBE_CLOSURE_SNAPSHOT_DO_NOT_CAPTURE"
PRIVATE_MODEL = "PRIVATE_PROBE_CLOSURE_MODEL_DO_NOT_CAPTURE"
PRIVATE_TEAM = "PRIVATE_PROBE_CLOSURE_TEAM_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_PROBE_CLOSURE_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_PROBE_CLOSURE_ERROR_DO_NOT_CAPTURE"
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


def _success_patches():
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

    return (
        patch.object(
            closure,
            "_build_pregame_capture_from_context_pre_v034",
            fake_base,
        ),
        patch.object(measurement, "enrich_pregame_capture", fake_enrich),
    )


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


def run_probe() -> dict[str, object]:
    clear_closure_shadow_events()
    snapshot, model, ctx, team = _inputs()

    managers = _success_patches()
    for manager in managers:
        manager.start()
    try:
        observed = _call(snapshot, model, ctx, team)
        direct = _direct(snapshot, model, ctx, team)
        success_ok = observed == direct and observed.get("private_result") == PRIVATE_RESULT

        events = last_closure_shadow_events()
        rendered = _event_json(events[-2:])
        event_shape_ok = (
            [event.event_name for event in events[-2:]]
            == ["action.start", "action.complete"]
            and all(event.context.subsystem == "closure" for event in events[-2:])
            and "subsystem.closure.capture" in rendered
            and '"boundary_kind":"subsystem"' in rendered
        )
        privacy_success_ok = all(
            marker not in rendered
            for marker in (
                PRIVATE_SNAPSHOT,
                PRIVATE_MODEL,
                PRIVATE_TEAM,
                PRIVATE_RESULT,
            )
        )

        clear_closure_shadow_events()
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
    finally:
        for manager in reversed(managers):
            manager.stop()

    clear_closure_shadow_events()
    snapshot, model, ctx, team = _inputs()

    def fail(*_args, **_kwargs):
        raise ValueError(PRIVATE_ERROR)

    direct_exc = observed_exc = None
    with patch.object(
        closure,
        "_build_pregame_capture_from_context_pre_v034",
        fail,
    ):
        try:
            _direct(snapshot, model, ctx, team)
        except Exception as exc:
            direct_exc = exc
        try:
            _call(snapshot, model, ctx, team)
        except Exception as exc:
            observed_exc = exc

    error_type_equal = (
        direct_exc is not None
        and observed_exc is not None
        and type(direct_exc) is type(observed_exc)
    )
    error_message_preserved = (
        observed_exc is not None and str(observed_exc) == PRIVATE_ERROR
    )
    error_rendered = _event_json(last_closure_shadow_events())
    privacy_error_ok = PRIVATE_ERROR not in error_rendered

    managers = _success_patches()
    for manager in managers:
        manager.start()
    try:
        snapshot, model, ctx, team = _inputs()
        random.seed(20260922)
        before = random.getstate()
        _call(snapshot, model, ctx, team)
        rng_preserved = random.getstate() == before
    finally:
        for manager in reversed(managers):
            manager.stop()

    result = {
        "schema": 1,
        "boundary": "subsystem.closure.capture",
        "instrumented_definition": "FINAL_V034_OVERRIDE",
        "success_behavior_preserved": success_ok,
        "event_shape_ok": event_shape_ok,
        "privacy_success_ok": privacy_success_ok,
        "error_type_equal": error_type_equal,
        "error_message_preserved_to_caller": error_message_preserved,
        "privacy_error_ok": privacy_error_ok,
        "python_random_state_preserved": rng_preserved,
        "persistent_sink": False,
        "arguments_captured": False,
        "return_values_captured": False,
        "exception_messages_captured": False,
        "benchmark": gate.to_dict(),
    }
    result["passed"] = bool(
        success_ok
        and event_shape_ok
        and privacy_success_ok
        and error_type_equal
        and error_message_preserved
        and privacy_error_ok
        and rng_preserved
        and gate.passed
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", default=".probe_closure_shadow")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    root = Path(args.work_root).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    try:
        result = run_probe()
        text = json.dumps(result, indent=2, sort_keys=True)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        return 0 if result["passed"] else 1
    finally:
        if root.exists():
            shutil.rmtree(root)


if __name__ == "__main__":
    raise SystemExit(main())
