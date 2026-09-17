from __future__ import annotations

from io import TextIOBase
import json
from pathlib import Path
import threading
from typing import Iterable, Protocol, TextIO

from .events import StructuredEvent


class EventSink(Protocol):
    """Minimal sink protocol; emission is explicit and caller-owned."""

    def emit(self, event: StructuredEvent) -> None:
        ...


def _require_event(event: StructuredEvent) -> StructuredEvent:
    if not isinstance(event, StructuredEvent):
        raise TypeError("event must be a StructuredEvent")
    return event


def format_human_event(
    event: StructuredEvent,
    *,
    include_payload: bool = False,
) -> str:
    """Render one concise line.

    Payload is omitted by default so the human sink does not become an accidental
    private-data disclosure path before the redaction layer is commissioned.
    """
    event = _require_event(event)
    row = event.to_dict()
    parts = [
        str(row["timestamp"]),
        f"[{row['level']}]",
        str(row["event_name"]),
        f"subsystem={row['subsystem']}",
        f"run={row['run_id']}",
        f"correlation={row['correlation_id']}",
    ]
    if include_payload:
        payload = json.dumps(
            row["payload"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        parts.append(f"payload={payload}")
    return " ".join(parts)


class MemorySink:
    """Thread-safe in-process sink for tests, bounded adapters, and diagnostics."""

    def __init__(self) -> None:
        self._events: list[StructuredEvent] = []
        self._lock = threading.Lock()

    def emit(self, event: StructuredEvent) -> None:
        event = _require_event(event)
        with self._lock:
            self._events.append(event)

    def snapshot(self) -> tuple[StructuredEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)


class JsonlSink:
    """Thread-safe JSONL machine sink with one complete event per line."""

    def __init__(
        self,
        path: str | Path,
        *,
        create_parents: bool = True,
        flush: bool = True,
    ) -> None:
        self.path = Path(path)
        self.create_parents = bool(create_parents)
        self.flush = bool(flush)
        self._lock = threading.Lock()

    def emit(self, event: StructuredEvent) -> None:
        event = _require_event(event)
        line = event.to_json() + "\n"
        with self._lock:
            if self.create_parents:
                self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line)
                if self.flush:
                    handle.flush()


class HumanTextSink:
    """Thread-safe concise text sink backed by a caller-owned text stream."""

    def __init__(
        self,
        stream: TextIO,
        *,
        include_payload: bool = False,
        flush: bool = True,
    ) -> None:
        if not hasattr(stream, "write"):
            raise TypeError("stream must provide write()")
        self.stream = stream
        self.include_payload = bool(include_payload)
        self.flush = bool(flush)
        self._lock = threading.Lock()

    def emit(self, event: StructuredEvent) -> None:
        line = format_human_event(
            _require_event(event),
            include_payload=self.include_payload,
        )
        with self._lock:
            self.stream.write(line + "\n")
            if self.flush and hasattr(self.stream, "flush"):
                self.stream.flush()


class FanoutSink:
    """Explicitly emit the same immutable event to multiple sinks in order."""

    def __init__(self, sinks: Iterable[EventSink]) -> None:
        self.sinks = tuple(sinks)
        if not self.sinks:
            raise ValueError("FanoutSink requires at least one sink")
        for sink in self.sinks:
            if not hasattr(sink, "emit"):
                raise TypeError("all sinks must provide emit()")

    def emit(self, event: StructuredEvent) -> None:
        event = _require_event(event)
        for sink in self.sinks:
            sink.emit(event)


def emit_all(sink: EventSink, events: Iterable[StructuredEvent]) -> int:
    """Emit an iterable explicitly and return the number of emitted events."""
    if not hasattr(sink, "emit"):
        raise TypeError("sink must provide emit()")
    count = 0
    for event in events:
        sink.emit(_require_event(event))
        count += 1
    return count
