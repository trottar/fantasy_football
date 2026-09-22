from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import random
import shutil
from unittest.mock import patch

import numpy as np

import src.specialist_policy_v032 as specialist_policy
from src.observability.adapters import CORE_ADAPTER_REGISTRY
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.context import RunContext
from src.observability.dst_shadow import (
    clear_dst_shadow_events,
    last_dst_shadow_events,
)
import src.observability.dst_shadow as dst_shadow


PRIVATE_ARG = "PRIVATE_PROBE_DST_ARG_DO_NOT_CAPTURE"
PRIVATE_RESULT = "PRIVATE_PROBE_DST_RESULT_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_PROBE_DST_ERROR_DO_NOT_CAPTURE"
BOUNDARY = "subsystem.dst.channel"


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

    return StateProbe("dst_inputs", capture, restore)


def _call(payload, *, mode="PROBE"):
    return specialist_policy.evaluate_defense_channel(payload, mode=mode)


def _direct(payload, *, mode="PROBE"):
    return specialist_policy.evaluate_defense_channel.__wrapped__(
        payload,
        mode=mode,
    )


def run_probe() -> dict[str, object]:
    clear_dst_shadow_events()
    payload = {"private": PRIVATE_ARG}
    mutable = {"calls": 0, "positions": []}

    def success_policy(*args, position, **kwargs):
        if position != "DST":
            raise AssertionError(f"unexpected position {position!r}")
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

    with patch.object(
        specialist_policy,
        "_evaluate_policy_channel",
        success_policy,
    ):
        random.seed(20260922)
        np.random.seed(20260922)

        initial_py = random.getstate()
        np_probe = _numpy_random_probe()
        initial_np = np_probe.capture()
        initial_payload = copy.deepcopy(payload)
        initial_mutable = copy.deepcopy(mutable)

        observed = _call(payload)

        random.setstate(initial_py)
        np_probe.restore(initial_np)
        payload.clear()
        payload.update(copy.deepcopy(initial_payload))
        mutable.clear()
        mutable.update(copy.deepcopy(initial_mutable))

        direct = _direct(payload)
        success_ok = observed == direct

        events = last_dst_shadow_events()
        rendered = _event_json(events[-2:])
        event_shape_ok = (
            [event.event_name for event in events[-2:]]
            == ["action.start", "action.complete"]
            and all(event.context.subsystem == "dst" for event in events[-2:])
            and BOUNDARY in rendered
            and '"boundary_kind":"subsystem"' in rendered
        )
        privacy_success_ok = (
            PRIVATE_ARG not in rendered and PRIVATE_RESULT not in rendered
        )

        clear_dst_shadow_events()
        random.seed(20260922)
        np.random.seed(20260922)
        payload = {"private": PRIVATE_ARG}
        mutable = {"calls": 0, "positions": []}
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

    clear_dst_shadow_events()

    def fail_policy(*_args, position, **_kwargs):
        if position != "DST":
            raise AssertionError(f"unexpected position {position!r}")
        random.random()
        np.random.random()
        raise ValueError(PRIVATE_ERROR)

    direct_exc = observed_exc = None
    with patch.object(
        specialist_policy,
        "_evaluate_policy_channel",
        fail_policy,
    ):
        try:
            _direct({"private": PRIVATE_ARG}, mode="ERROR")
        except Exception as exc:
            direct_exc = exc
        try:
            _call({"private": PRIVATE_ARG}, mode="ERROR")
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
    error_rendered = _event_json(last_dst_shadow_events())
    privacy_error_ok = PRIVATE_ERROR not in error_rendered

    with patch.object(
        specialist_policy,
        "_evaluate_policy_channel",
        lambda *_args, position, **_kwargs: {"position": position},
    ):
        clear_dst_shadow_events()
        before = len(last_dst_shadow_events())
        kicker_result = specialist_policy.evaluate_kicker_channel(
            {"private": PRIVATE_ARG}
        )
        after = len(last_dst_shadow_events())
    kicker_noninterference = kicker_result == {"position": "K"} and before == after

    with patch.object(
        specialist_policy,
        "_evaluate_policy_channel",
        success_policy,
    ):
        class FailingRecorder(dst_shadow.ShadowRecorder):
            def _emit(self, event):
                raise RuntimeError("observer-only failure")

        recorder = FailingRecorder(root_subsystem="observability")
        payload = {"private": PRIVATE_ARG}
        random.seed(20260922)
        np.random.seed(20260922)
        py_state = random.getstate()
        np_probe = _numpy_random_probe()
        np_state = np_probe.capture()
        mutable_state = copy.deepcopy(mutable)

        direct = _direct(payload, mode="OBSERVER_FAILURE")
        random.setstate(py_state)
        np_probe.restore(np_state)
        mutable.clear()
        mutable.update(copy.deepcopy(mutable_state))
        observed = recorder.call_subsystem(
            BOUNDARY,
            specialist_policy.evaluate_defense_channel.__wrapped__,
            payload,
            mode="OBSERVER_FAILURE",
            subsystem="dst",
        )
        observer_failure_fallthrough = (
            direct == observed and recorder.observer_failures >= 1
        )

    player_context = RunContext.create(subsystem="player")
    try:
        CORE_ADAPTER_REGISTRY.require("dst").begin(player_context, BOUNDARY)
    except ValueError:
        cross_channel_guard = True
    else:
        cross_channel_guard = False

    result = {
        "schema": 1,
        "boundary": BOUNDARY,
        "subsystem": "dst",
        "success_behavior_preserved": success_ok,
        "event_shape_ok": event_shape_ok,
        "privacy_success_ok": privacy_success_ok,
        "error_type_equal": error_type_equal,
        "error_message_preserved_to_caller": error_message_preserved,
        "privacy_error_ok": privacy_error_ok,
        "kicker_noninterference": kicker_noninterference,
        "observer_failure_fallthrough": observer_failure_fallthrough,
        "pdk_cross_channel_guard": cross_channel_guard,
        "python_random_state_preserved": gate.states_equal,
        "numpy_random_state_preserved": gate.states_equal,
        "mutable_state_preserved": gate.states_equal,
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
        and kicker_noninterference
        and observer_failure_fallthrough
        and cross_channel_guard
        and gate.passed
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", default=".probe_dst_shadow")
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
            Path(args.json_out).write_text(
                text + "\n",
                encoding="utf-8",
                newline="\n",
            )
        return 0 if result["passed"] else 1
    finally:
        if root.exists():
            shutil.rmtree(root)


if __name__ == "__main__":
    raise SystemExit(main())
