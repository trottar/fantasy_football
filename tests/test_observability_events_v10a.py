from datetime import datetime, timezone
import json
import random

import pytest

from src.observability.context import RunContext
from src.observability.events import EVENT_SCHEMA_VERSION, make_event
from src.observability.registry import (
    CORE_EVENT_REGISTRY,
    EventDefinition,
    EventLevel,
    EventRegistry,
)


UTC = timezone.utc


EXPECTED_GUI_EVENTS = {
    "gui.app.start",
    "gui.app.stop",
    "gui.client.connect",
    "gui.client.disconnect",
    "gui.page.mount",
    "gui.page.unmount",
    "gui.action.start",
    "gui.action.complete",
    "gui.action.error",
    "gui.task.spawn",
    "gui.task.cancel",
    "gui.service.start",
    "gui.service.complete",
    "gui.service.error",
    "gui.state.read",
    "gui.state.write",
    "gui.render.start",
    "gui.render.complete",
    "gui.refresh.request",
    "gui.refresh.complete",
    "gui.notification",
    "gui.lifecycle.violation",
}


def _context(subsystem="gui"):
    return RunContext.create(
        subsystem=subsystem,
        run_id="run:test",
        timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="4e7f5277cd4a3d98378e3bdeaf8f965ab27df14b",
        week=2,
        config_hash="c" * 64,
        input_snapshot_hash="d" * 64,
    )


def test_core_registry_contains_generic_and_architecture_gui_events():
    assert {
        "run.start",
        "run.complete",
        "run.error",
        "action.start",
        "action.complete",
        "action.error",
    }.issubset(set(CORE_EVENT_REGISTRY.names))
    assert EXPECTED_GUI_EVENTS.issubset(set(CORE_EVENT_REGISTRY.names))


def test_event_envelope_contains_context_provenance_and_action_correlation():
    context = _context().for_action(action_id="action:refresh")
    event = make_event(
        context,
        "gui.refresh.request",
        timestamp=datetime(2026, 9, 17, 12, 1, tzinfo=UTC),
        payload={"trigger": "button", "attempt": 1},
    )

    row = event.to_dict()
    assert row["schema_version"] == EVENT_SCHEMA_VERSION == 1
    assert row["timestamp"] == "2026-09-17T12:01:00Z"
    assert row["level"] == "NORMAL"
    assert row["event_name"] == "gui.refresh.request"
    assert row["subsystem"] == "gui"
    assert row["run_id"] == "run:test"
    assert row["correlation_id"] == "action:refresh"
    assert row["action_id"] == "action:refresh"
    assert row["payload"] == {"trigger": "button", "attempt": 1}
    assert row["provenance"]["release_version"] == "0.36"
    assert row["provenance"]["config_hash"] == "c" * 64

    parsed = json.loads(event.to_json())
    assert parsed == row


def test_payload_is_copied_and_deeply_immutable():
    source = {
        "items": [{"name": "alpha"}],
        "tags": {"b", "a"},
    }
    event = make_event(
        _context(),
        "gui.notification",
        payload=source,
    )

    source["items"][0]["name"] = "mutated"
    source["tags"].add("c")

    row = event.to_dict()
    assert row["payload"]["items"][0]["name"] == "alpha"
    assert row["payload"]["tags"] == ["a", "b"]

    with pytest.raises(TypeError):
        event.payload["new"] = 1
    with pytest.raises(TypeError):
        event.payload["items"][0]["name"] = "x"


def test_registry_enforces_required_payload_and_subsystem():
    with pytest.raises(ValueError, match="error_type"):
        make_event(_context(), "gui.action.error", payload={})

    with pytest.raises(ValueError, match="does not allow subsystem"):
        make_event(
            _context("player"),
            "gui.refresh.request",
            payload={},
        )

    event = make_event(
        _context(),
        "gui.lifecycle.violation",
        payload={"invariant": "no-stale-client-write"},
    )
    assert event.level is EventLevel.AUDIT


def test_registry_rejects_duplicate_definitions_and_unknown_events():
    definition = EventDefinition(
        name="test.event",
        default_level=EventLevel.DIAGNOSTIC,
        description="test event",
    )
    with pytest.raises(ValueError, match="duplicate"):
        EventRegistry([definition, definition])

    with pytest.raises(KeyError, match="not registered"):
        make_event(_context(), "unknown.event")


def test_payload_rejects_non_finite_and_unsupported_values():
    with pytest.raises(ValueError, match="non-finite"):
        make_event(
            _context(),
            "gui.notification",
            payload={"value": float("nan")},
        )

    with pytest.raises(TypeError, match="unsupported"):
        make_event(
            _context(),
            "gui.notification",
            payload={"value": object()},
        )


def test_event_creation_does_not_advance_random_state():
    random.seed(424242)
    before = random.getstate()

    make_event(
        _context().for_action(action_id="action:test"),
        "gui.action.start",
        payload={"source": "test"},
    )

    after = random.getstate()
    assert after == before
