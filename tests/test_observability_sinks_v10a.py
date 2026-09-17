from datetime import datetime, timezone
from io import StringIO
import json
import random

from src.observability.context import RunContext
from src.observability.events import make_event
from src.observability.sinks import (
    FanoutSink,
    HumanTextSink,
    JsonlSink,
    MemorySink,
    emit_all,
    format_human_event,
)

UTC = timezone.utc


def _event(name="gui.notification", payload=None):
    context = RunContext.create(
        subsystem="gui",
        run_id="run:sinks",
        timestamp=datetime(2026, 9, 17, 12, 30, tzinfo=UTC),
        release_version="0.36",
        source_commit="f" * 40,
    ).for_action(action_id="action:sinks")
    return make_event(
        context,
        name,
        timestamp=datetime(2026, 9, 17, 12, 31, tzinfo=UTC),
        payload={} if payload is None else payload,
    )


def test_memory_sink_snapshot_is_immutable_tuple_and_clear_is_explicit():
    sink = MemorySink()
    event = _event(payload={"message": "ok"})
    sink.emit(event)

    snapshot = sink.snapshot()
    assert snapshot == (event,)
    assert len(sink) == 1

    sink.clear()
    assert sink.snapshot() == ()
    assert snapshot == (event,)


def test_jsonl_sink_writes_one_deterministic_event_per_line(tmp_path):
    path = tmp_path / "nested" / "events.jsonl"
    sink = JsonlSink(path)
    events = [
        _event(payload={"sequence": 1}),
        _event(payload={"sequence": 2}),
    ]
    assert emit_all(sink, events) == 2

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines == [event.to_json() for event in events]
    assert [json.loads(line)["payload"]["sequence"] for line in lines] == [1, 2]


def test_human_sink_omits_payload_by_default_and_can_include_it_explicitly():
    event = _event(payload={"private_like_value": "do-not-print-by-default"})
    safe = format_human_event(event)
    assert "private_like_value" not in safe
    assert "do-not-print-by-default" not in safe
    assert "gui.notification" in safe
    assert "correlation=action:sinks" in safe

    stream = StringIO()
    sink = HumanTextSink(stream, include_payload=True)
    sink.emit(event)
    rendered = stream.getvalue()
    assert 'payload={"private_like_value":"do-not-print-by-default"}' in rendered


def test_fanout_delivers_same_immutable_event_to_each_sink():
    first = MemorySink()
    second = MemorySink()
    fanout = FanoutSink([first, second])
    event = _event(payload={"value": 7})
    fanout.emit(event)

    assert first.snapshot()[0] is event
    assert second.snapshot()[0] is event


def test_sink_emission_does_not_advance_python_random_state(tmp_path):
    random.seed(31337)
    before = random.getstate()

    event = _event(payload={"value": 1})
    FanoutSink(
        [
            MemorySink(),
            JsonlSink(tmp_path / "events.jsonl"),
            HumanTextSink(StringIO()),
        ]
    ).emit(event)

    after = random.getstate()
    assert after == before
