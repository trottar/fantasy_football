from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
import inspect
import threading
import time
from typing import Any, Awaitable

from .context import RunContext, new_correlation_id
from .correlation import CorrelationBoundary, begin_background_task
from .events import StructuredEvent, make_event


DEFAULT_GUI_SHADOW_MAX_EVENTS = 512


class GuiShadowRecorder:
    """Bounded in-memory GUI lifecycle/task observer.

    The recorder never owns a persistent sink and never stores NiceGUI client
    identifiers, task arguments/results, authenticated payloads, or exception
    messages. Observer failures are counted and swallowed.
    """

    def __init__(
        self,
        *,
        max_events: int = DEFAULT_GUI_SHADOW_MAX_EVENTS,
        root_context: RunContext | None = None,
    ) -> None:
        if isinstance(max_events, bool) or not isinstance(max_events, int):
            raise TypeError("max_events must be an integer")
        if max_events < 8:
            raise ValueError("max_events must be >= 8")
        if root_context is not None and not isinstance(root_context, RunContext):
            raise TypeError("root_context must be a RunContext or None")

        self.root_context = (
            RunContext.create(subsystem="gui")
            if root_context is None
            else root_context
        )
        self.max_events = max_events
        self._events: deque[StructuredEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._observer_failures = 0

    def _note_observer_failure(self) -> None:
        with self._lock:
            self._observer_failures += 1

    @property
    def observer_failures(self) -> int:
        with self._lock:
            return self._observer_failures

    def snapshot(self) -> tuple[StructuredEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def _emit(self, event: StructuredEvent) -> None:
        if not isinstance(event, StructuredEvent):
            raise TypeError("event must be a StructuredEvent")
        with self._lock:
            self._events.append(event)

    def emit(
        self,
        context: RunContext,
        event_name: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        try:
            self._emit(
                make_event(
                    context,
                    event_name,
                    payload={} if payload is None else payload,
                )
            )
        except Exception:
            self._note_observer_failure()

    def open_page(self) -> "GuiPageShadow":
        session_id = new_correlation_id("session")
        page_id = new_correlation_id("page")
        session_context = self.root_context.for_action(
            subsystem="gui",
            action_id=session_id,
        )
        page_context = session_context.for_action(
            subsystem="gui",
            action_id=page_id,
        )
        page = GuiPageShadow(
            recorder=self,
            session_id=session_id,
            page_id=page_id,
            context=page_context,
        )
        page.mount()
        return page


@dataclass
class GuiPageShadow:
    recorder: GuiShadowRecorder
    session_id: str
    page_id: str
    context: RunContext

    def __post_init__(self) -> None:
        self._deleted = False
        self._mounted = False

    @property
    def deleted(self) -> bool:
        return self._deleted

    def _base(self) -> dict[str, str]:
        return {
            "session_id": self.session_id,
            "page_id": self.page_id,
        }

    def mount(self) -> None:
        if self._mounted:
            return
        self._mounted = True
        self.recorder.emit(
            self.context,
            "gui.page.mount",
            self._base(),
        )

    def client_connect(self) -> None:
        self.recorder.emit(
            self.context,
            "gui.client.connect",
            self._base(),
        )

    def client_disconnect(self) -> None:
        self.recorder.emit(
            self.context,
            "gui.client.disconnect",
            self._base(),
        )

    def page_unmount(self) -> None:
        if self._deleted:
            return
        self._deleted = True
        self.recorder.emit(
            self.context,
            "gui.page.unmount",
            self._base(),
        )

    def _task_payload(
        self,
        boundary: CorrelationBoundary,
        name: str,
    ) -> dict[str, str]:
        return {
            **self._base(),
            "task_id": boundary.action_id,
            "task_name": name,
        }

    def _lifecycle_violation(
        self,
        boundary: CorrelationBoundary,
        name: str,
    ) -> None:
        if not self._deleted:
            return
        self.recorder.emit(
            boundary.context,
            "gui.lifecycle.violation",
            {
                **self._task_payload(boundary, name),
                "invariant": "gui.no_task_terminal_after_page_delete",
            },
        )

    def observe_background_task(
        self,
        name: str,
        awaitable: Awaitable[Any],
    ) -> Awaitable[Any]:
        """Wrap one background awaitable without changing its result semantics."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not inspect.isawaitable(awaitable):
            raise TypeError("awaitable must be awaitable")
        clean_name = name.strip()

        try:
            boundary = begin_background_task(
                self.context,
                clean_name,
                subsystem="gui",
                attributes=self._base(),
            )
            self.recorder._emit(boundary.start_event)
            self.recorder.emit(
                boundary.context,
                "gui.task.spawn",
                self._task_payload(boundary, clean_name),
            )
        except Exception:
            self.recorder._note_observer_failure()
            return awaitable

        async def observed() -> Any:
            started = time.perf_counter_ns()
            try:
                result = await awaitable
            except asyncio.CancelledError:
                elapsed = max(0, time.perf_counter_ns() - started)
                self.recorder.emit(
                    boundary.context,
                    "gui.task.cancel",
                    {
                        **self._task_payload(boundary, clean_name),
                        "duration_ns": elapsed,
                    },
                )
                self._lifecycle_violation(boundary, clean_name)
                raise
            except BaseException as exc:
                elapsed = max(0, time.perf_counter_ns() - started)
                try:
                    self.recorder._emit(
                        boundary.fail(
                            exc,
                            payload={"duration_ns": elapsed},
                        )
                    )
                except Exception:
                    self.recorder._note_observer_failure()
                self._lifecycle_violation(boundary, clean_name)
                raise
            else:
                elapsed = max(0, time.perf_counter_ns() - started)
                try:
                    self.recorder._emit(
                        boundary.complete(
                            {"duration_ns": elapsed},
                        )
                    )
                except Exception:
                    self.recorder._note_observer_failure()
                self._lifecycle_violation(boundary, clean_name)
                return result

        return observed()


_LAST_GUI_LOCK = threading.Lock()
_LAST_GUI_RECORDER: GuiShadowRecorder | None = None


def create_gui_shadow_recorder(
    *,
    max_events: int = DEFAULT_GUI_SHADOW_MAX_EVENTS,
) -> GuiShadowRecorder:
    global _LAST_GUI_RECORDER
    recorder = GuiShadowRecorder(max_events=max_events)
    with _LAST_GUI_LOCK:
        _LAST_GUI_RECORDER = recorder
    return recorder


def last_gui_shadow_events() -> tuple[StructuredEvent, ...]:
    with _LAST_GUI_LOCK:
        recorder = _LAST_GUI_RECORDER
    if recorder is None:
        return ()
    return recorder.snapshot()
