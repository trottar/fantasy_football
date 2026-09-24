from __future__ import annotations

from functools import wraps
import threading
from typing import Any, Callable

from .events import StructuredEvent
from .shadow_pilot import ShadowRecorder


_BEHAVIOR_LOCK = threading.Lock()
_BEHAVIOR_RECORDER: ShadowRecorder | None = None


def _behavior_shadow_recorder() -> ShadowRecorder | None:
    global _BEHAVIOR_RECORDER
    with _BEHAVIOR_LOCK:
        if _BEHAVIOR_RECORDER is None:
            try:
                _BEHAVIOR_RECORDER = ShadowRecorder(root_subsystem="observability")
            except Exception:
                return None
        return _BEHAVIOR_RECORDER


def last_behavior_shadow_events() -> tuple[StructuredEvent, ...]:
    with _BEHAVIOR_LOCK:
        recorder = _BEHAVIOR_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def clear_behavior_shadow_events() -> None:
    with _BEHAVIOR_LOCK:
        recorder = _BEHAVIOR_RECORDER
    if recorder is not None:
        recorder.clear()


def shadow_behavior_call(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Observe one manager-behavior boundary without retaining inputs/results."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            recorder = _behavior_shadow_recorder()
            if recorder is None:
                return fn(*args, **kwargs)
            return recorder.call_subsystem(
                name,
                fn,
                *args,
                subsystem="behavior",
                **kwargs,
            )

        return wrapped

    return decorate
