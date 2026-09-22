from __future__ import annotations

from functools import wraps
import threading
from typing import Any, Callable

from .events import StructuredEvent
from .shadow_pilot import ShadowRecorder


_K_LOCK = threading.Lock()
_K_RECORDER: ShadowRecorder | None = None


def _k_shadow_recorder() -> ShadowRecorder | None:
    global _K_RECORDER
    with _K_LOCK:
        if _K_RECORDER is None:
            try:
                _K_RECORDER = ShadowRecorder(
                    root_subsystem="observability",
                )
            except Exception:
                return None
        return _K_RECORDER


def last_k_shadow_events() -> tuple[StructuredEvent, ...]:
    with _K_LOCK:
        recorder = _K_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def clear_k_shadow_events() -> None:
    with _K_LOCK:
        recorder = _K_RECORDER
    if recorder is not None:
        recorder.clear()


def shadow_k_call(
    name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Observe one K boundary without retaining arguments or results."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            recorder = _k_shadow_recorder()
            if recorder is None:
                return fn(*args, **kwargs)
            return recorder.call_subsystem(
                name,
                fn,
                *args,
                subsystem="k",
                **kwargs,
            )

        return wrapped

    return decorate
