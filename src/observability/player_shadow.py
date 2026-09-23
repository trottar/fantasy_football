from __future__ import annotations

from functools import wraps
import threading
from typing import Any, Callable

from .events import StructuredEvent
from .shadow_pilot import ShadowRecorder


_PLAYER_LOCK = threading.Lock()
_PLAYER_RECORDER: ShadowRecorder | None = None


def _player_shadow_recorder() -> ShadowRecorder | None:
    global _PLAYER_RECORDER
    with _PLAYER_LOCK:
        if _PLAYER_RECORDER is None:
            try:
                _PLAYER_RECORDER = ShadowRecorder(root_subsystem="observability")
            except Exception:
                return None
        return _PLAYER_RECORDER


def last_player_shadow_events() -> tuple[StructuredEvent, ...]:
    with _PLAYER_LOCK:
        recorder = _PLAYER_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def clear_player_shadow_events() -> None:
    with _PLAYER_LOCK:
        recorder = _PLAYER_RECORDER
    if recorder is not None:
        recorder.clear()


def shadow_player_call(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Observe one QB/RB/WR/TE perturbation boundary without retaining payloads."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            recorder = _player_shadow_recorder()
            if recorder is None:
                return fn(*args, **kwargs)
            return recorder.call_subsystem(
                name,
                fn,
                *args,
                subsystem="player",
                **kwargs,
            )

        return wrapped

    return decorate
