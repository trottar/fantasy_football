from __future__ import annotations

from functools import wraps
import threading
from typing import Any, Callable

from .events import StructuredEvent
from .shadow_pilot import ShadowRecorder


_CLOSURE_LOCK = threading.Lock()
_CLOSURE_RECORDER: ShadowRecorder | None = None


def _closure_shadow_recorder() -> ShadowRecorder | None:
    global _CLOSURE_RECORDER
    with _CLOSURE_LOCK:
        if _CLOSURE_RECORDER is None:
            try:
                _CLOSURE_RECORDER = ShadowRecorder(
                    root_subsystem="observability",
                )
            except Exception:
                return None
        return _CLOSURE_RECORDER


def last_closure_shadow_events() -> tuple[StructuredEvent, ...]:
    with _CLOSURE_LOCK:
        recorder = _CLOSURE_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def clear_closure_shadow_events() -> None:
    with _CLOSURE_LOCK:
        recorder = _CLOSURE_RECORDER
    if recorder is not None:
        recorder.clear()


def shadow_closure_call(
    name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Observe one closure boundary without retaining arguments or results."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            recorder = _closure_shadow_recorder()
            if recorder is None:
                return fn(*args, **kwargs)
            return recorder.call_subsystem(
                name,
                fn,
                *args,
                subsystem="closure",
                **kwargs,
            )

        return wrapped

    return decorate
