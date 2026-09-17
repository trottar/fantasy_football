from __future__ import annotations

from collections import deque
from contextvars import ContextVar
from functools import wraps
import threading
import time
from typing import Any, Callable

from .context import RunContext
from .correlation import begin_cli_action, begin_service_action
from .events import StructuredEvent


DEFAULT_SHADOW_MAX_EVENTS = 256


class ShadowRecorder:
    """Bounded in-memory observer for narrow production shadow pilots.

    The recorder owns no persistent sink. It records boundary metadata,
    correlation, duration, and exception *type* only. Function arguments,
    returned values, exception messages, and private payloads are never stored.
    Observer failures are swallowed and counted so diagnostics cannot alter the
    wrapped production result or exception.
    """

    def __init__(
        self,
        *,
        root_subsystem: str,
        max_events: int = DEFAULT_SHADOW_MAX_EVENTS,
        root_context: RunContext | None = None,
    ) -> None:
        if isinstance(max_events, bool) or not isinstance(max_events, int):
            raise TypeError("max_events must be an integer")
        if max_events < 2:
            raise ValueError("max_events must be >= 2")
        if root_context is not None and not isinstance(root_context, RunContext):
            raise TypeError("root_context must be a RunContext or None")

        self.root_context = (
            RunContext.create(subsystem=root_subsystem)
            if root_context is None
            else root_context
        )
        self.max_events = max_events
        self._events: deque[StructuredEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._observer_failures = 0
        self._current_context: ContextVar[RunContext | None] = ContextVar(
            f"fantasy_shadow_context_{id(self)}",
            default=None,
        )

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)

    @property
    def observer_failures(self) -> int:
        with self._lock:
            return self._observer_failures

    def snapshot(self) -> tuple[StructuredEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def _note_observer_failure(self) -> None:
        with self._lock:
            self._observer_failures += 1

    def _emit(self, event: StructuredEvent) -> None:
        if not isinstance(event, StructuredEvent):
            raise TypeError("event must be a StructuredEvent")
        with self._lock:
            self._events.append(event)

    def _parent(self) -> RunContext:
        return self._current_context.get() or self.root_context

    def _run_boundary(
        self,
        boundary_factory: Callable[[], Any],
        fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        try:
            boundary = boundary_factory()
            self._emit(boundary.start_event)
        except Exception:
            self._note_observer_failure()
            return fn(*args, **kwargs)

        token = self._current_context.set(boundary.context)
        started = time.perf_counter_ns()
        try:
            result = fn(*args, **kwargs)
        except BaseException as exc:
            elapsed = max(0, time.perf_counter_ns() - started)
            try:
                self._emit(
                    boundary.fail(
                        exc,
                        payload={"duration_ns": elapsed},
                    )
                )
            except Exception:
                self._note_observer_failure()
            raise
        else:
            elapsed = max(0, time.perf_counter_ns() - started)
            try:
                self._emit(
                    boundary.complete(
                        {"duration_ns": elapsed},
                    )
                )
            except Exception:
                self._note_observer_failure()
            return result
        finally:
            self._current_context.reset(token)

    def call_cli(
        self,
        name: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not callable(fn):
            raise TypeError("fn must be callable")
        return self._run_boundary(
            lambda: begin_cli_action(
                self._parent(),
                name,
            ),
            fn,
            args,
            kwargs,
        )

    def call_service(
        self,
        name: str,
        fn: Callable[..., Any],
        *args: Any,
        subsystem: str = "gui",
        **kwargs: Any,
    ) -> Any:
        if not callable(fn):
            raise TypeError("fn must be callable")
        return self._run_boundary(
            lambda: begin_service_action(
                self._parent(),
                name,
                subsystem=subsystem,
            ),
            fn,
            args,
            kwargs,
        )


_LAST_CLI_LOCK = threading.Lock()
_LAST_CLI_RECORDER: ShadowRecorder | None = None


def dispatch_cli_shadow(
    fn: Callable[[Any], Any],
    args: Any,
) -> Any:
    """Run one CLI command through a fresh bounded in-memory shadow recorder."""
    global _LAST_CLI_RECORDER

    if not callable(fn):
        raise TypeError("fn must be callable")

    try:
        recorder = ShadowRecorder(root_subsystem="observability")
    except Exception:
        return fn(args)

    with _LAST_CLI_LOCK:
        _LAST_CLI_RECORDER = recorder

    name = getattr(fn, "__name__", None)
    if not isinstance(name, str) or not name.strip():
        name = "cli_command"

    return recorder.call_cli(name, fn, args)


def last_cli_shadow_events() -> tuple[StructuredEvent, ...]:
    with _LAST_CLI_LOCK:
        recorder = _LAST_CLI_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()


def shadow_service_call(
    name: str,
    *,
    subsystem: str = "gui",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorate a service method without changing behavior when no recorder exists."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(fn):
            raise TypeError("decorated value must be callable")

        @wraps(fn)
        def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
            recorder = getattr(self, "_observability_shadow", None)
            if not isinstance(recorder, ShadowRecorder):
                return fn(self, *args, **kwargs)
            return recorder.call_service(
                name,
                fn,
                self,
                *args,
                subsystem=subsystem,
                **kwargs,
            )

        return wrapped

    return decorate
