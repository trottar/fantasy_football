from datetime import datetime, timezone
import random

import pytest

from src.observability.adapters import (
    CORE_ADAPTER_REGISTRY,
    AdapterRegistry,
    SubsystemAdapter,
)
from src.observability.context import RunContext
from src.observability.correlation import (
    BoundaryKind,
    begin_background_task,
    begin_cli_action,
    begin_service_action,
)
from src.observability.sinks import MemorySink

UTC = timezone.utc


def _root():
    return RunContext.create(
        subsystem="observability",
        run_id="run:adapter-test",
        timestamp=datetime(2026, 9, 17, 19, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="2c5d34c7961cdbd651d1cdb9539c9bb768757a65",
        config_hash="a" * 64,
        input_snapshot_hash="b" * 64,
    )


def test_cli_service_background_chain_preserves_run_and_parentage():
    cli = begin_cli_action(_root(), "week-report", action_id="action:cli")
    service = begin_service_action(
        cli.context,
        "project-player-channel",
        subsystem="player",
        action_id="action:service",
    )
    task = begin_background_task(
        service.context,
        "mc-worker",
        action_id="action:task",
    )

    assert cli.run_id == service.run_id == task.run_id == "run:adapter-test"
    assert cli.parent_action_id is None
    assert service.parent_action_id == "action:cli"
    assert task.parent_action_id == "action:service"
    assert service.context.subsystem == "player"
    assert task.context.subsystem == "player"


def test_boundary_events_are_correlated_and_do_not_include_error_message():
    boundary = begin_service_action(
        _root(),
        "values-service",
        subsystem="player",
        action_id="action:values",
        attributes={"source": "unit-test"},
    )
    complete = boundary.complete({"rows": 12})
    failure = boundary.fail(RuntimeError("secret should not appear"))

    assert boundary.start_event.event_name == "action.start"
    assert complete.event_name == "action.complete"
    assert failure.event_name == "action.error"
    assert {
        boundary.start_event.correlation_id,
        complete.correlation_id,
        failure.correlation_id,
    } == {"action:values"}
    assert failure.payload["error_type"] == "RuntimeError"
    assert "secret should not appear" not in failure.to_json()


def test_boundary_attributes_are_copied_and_deeply_immutable():
    source = {"nested": {"values": [1, 2]}}
    boundary = begin_cli_action(
        _root(),
        "cli",
        action_id="action:cli",
        attributes=source,
    )
    source["nested"]["values"].append(3)

    assert boundary.base_payload()["attributes"] == {
        "nested": {"values": [1, 2]}
    }
    with pytest.raises(TypeError):
        boundary.attributes["new"] = 1
    with pytest.raises(TypeError):
        boundary.attributes["nested"]["x"] = 1


def test_subsystem_adapter_sets_identity_without_emitting_to_sink():
    sink = MemorySink()
    adapter = CORE_ADAPTER_REGISTRY.require("dst")
    boundary = adapter.begin(
        _root(),
        "dst-projection",
        action_id="action:dst",
    )

    assert boundary.context.subsystem == "dst"
    assert boundary.kind is BoundaryKind.SUBSYSTEM
    assert len(sink) == 0


def test_direct_player_dst_k_cross_channel_nesting_is_rejected():
    player = CORE_ADAPTER_REGISTRY.require("player").begin(
        _root(),
        "player",
        action_id="action:player",
    )

    with pytest.raises(ValueError, match="cross-channel"):
        CORE_ADAPTER_REGISTRY.require("dst").begin(
            player.context,
            "dst",
            action_id="action:dst",
        )

    nested_player = CORE_ADAPTER_REGISTRY.require("player").begin(
        player.context,
        "player-child",
        action_id="action:player-child",
    )
    assert nested_player.context.subsystem == "player"


def test_root_can_enter_each_specialist_channel_independently():
    root = _root()
    assert CORE_ADAPTER_REGISTRY.require("player").begin(
        root, "p", action_id="action:p"
    ).context.subsystem == "player"
    assert CORE_ADAPTER_REGISTRY.require("dst").begin(
        root, "d", action_id="action:d"
    ).context.subsystem == "dst"
    assert CORE_ADAPTER_REGISTRY.require("k").begin(
        root, "k", action_id="action:k"
    ).context.subsystem == "k"


def test_adapter_registry_is_explicit_and_validated():
    assert {"player", "dst", "k", "gui", "closure"}.issubset(
        set(CORE_ADAPTER_REGISTRY.names)
    )
    with pytest.raises(KeyError, match="not registered"):
        CORE_ADAPTER_REGISTRY.require("unknown")
    with pytest.raises(ValueError, match="does not match"):
        AdapterRegistry({"player": SubsystemAdapter("dst")})
    with pytest.raises(ValueError, match="unsupported"):
        SubsystemAdapter("not-a-subsystem")


def test_invalid_boundary_names_are_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        begin_cli_action(_root(), "   ")


def test_correlation_contract_does_not_advance_python_random_state():
    random.seed(777)
    before = random.getstate()

    cli = begin_cli_action(_root(), "cli")
    service = CORE_ADAPTER_REGISTRY.require("player").begin(
        cli.context,
        "player-service",
    )
    service.complete({"ok": True})

    assert random.getstate() == before
