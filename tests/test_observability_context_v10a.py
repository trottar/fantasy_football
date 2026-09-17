from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import random

import pytest

from src.observability.context import RunContext


UTC = timezone.utc


def test_context_is_immutable_json_stable_and_utc_normalized():
    context = RunContext.create(
        subsystem="player",
        run_id="run:test",
        timestamp=datetime(2026, 9, 17, 8, 0, tzinfo=timezone(timedelta(hours=-4))),
        release_version="0.36",
        source_commit="4e7f5277cd4a3d98378e3bdeaf8f965ab27df14b",
        week=2,
        decision_time=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
        data_as_of=datetime(2026, 9, 17, 11, 55, tzinfo=UTC),
        random_seed=12345,
        crn_group_id="crn:week2",
        config_hash="a" * 64,
        input_snapshot_hash="b" * 64,
    )

    assert context.timestamp == datetime(2026, 9, 17, 12, 0, tzinfo=UTC)
    assert context.correlation_id == "run:test"
    assert context.as_dict()["timestamp"] == "2026-09-17T12:00:00Z"
    assert context.provenance() == {
        "release_version": "0.36",
        "source_commit": "4e7f5277cd4a3d98378e3bdeaf8f965ab27df14b",
        "config_hash": "a" * 64,
        "input_snapshot_hash": "b" * 64,
    }

    with pytest.raises(FrozenInstanceError):
        context.week = 3


def test_action_context_preserves_run_provenance_and_parent_chain():
    root = RunContext.create(
        subsystem="gui",
        run_id="run:gui",
        timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="4e7f5277",
        week=2,
    )
    first = root.for_action(action_id="action:refresh")
    second = first.for_action(
        action_id="action:service",
        subsystem="gui",
        scenario_id="scenario:baseline",
        random_seed=9001,
        crn_group_id="crn:refresh",
    )

    assert first.run_id == root.run_id
    assert first.parent_action_id is None
    assert second.run_id == root.run_id
    assert second.action_id == "action:service"
    assert second.parent_action_id == "action:refresh"
    assert second.release_version == root.release_version
    assert second.source_commit == root.source_commit
    assert second.week == root.week
    assert second.correlation_id == "action:service"


def test_context_rejects_naive_time_invalid_hash_and_parent_without_action():
    with pytest.raises(ValueError, match="timezone-aware"):
        RunContext.create(
            subsystem="player",
            run_id="run:test",
            timestamp=datetime(2026, 9, 17, 12, 0),
        )

    with pytest.raises(ValueError, match="64-character"):
        RunContext.create(
            subsystem="player",
            run_id="run:test",
            timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
            config_hash="abc",
        )

    with pytest.raises(ValueError, match="requires an action_id"):
        RunContext(
            run_id="run:test",
            timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
            subsystem="player",
            parent_action_id="action:parent",
        )


def test_context_creation_does_not_advance_python_random_state():
    random.seed(8675309)
    before = random.getstate()

    RunContext.create(
        subsystem="observability",
        timestamp=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
    ).for_action()

    after = random.getstate()
    assert after == before
