from __future__ import annotations

from functools import wraps
import threading
from typing import Any, Callable

from .events import StructuredEvent
from .shadow_pilot import ShadowRecorder


_DST_LOCK = threading.Lock()
_DST_RECORDER: ShadowRecorder | None = None


def _dst_shadow_recorder() -> ShadowRecorder | None:
    global _DST_RECORDER
    with _DST_LOCK:
        if _DST_RECORDER is None:
            try:
                _DST_RECORDER = ShadowRecorder(
                    root_subsystem="observability",
                )
            except Exception:
                return None
        return _DST_RECORDER


def last_dst_shadow_events() -> tuple[StructuredEvent, ...]:
    with _DST_LOCK:
        recorder = _DST_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def clear_dst_shadow_events() -> None:
    with _DST_LOCK:
        recorder = _DST_RECORDER
    if recorder is not None:
        recorder.clear()


def shadow_dst_call(
    name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Observe one DST boundary without retaining arguments or results."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            recorder = _dst_shadow_recorder()
            if recorder is None:
                return fn(*args, **kwargs)
            return recorder.call_subsystem(
                name,
                fn,
                *args,
                subsystem="dst",
                **kwargs,
            )

        return wrapped

    return decorate
