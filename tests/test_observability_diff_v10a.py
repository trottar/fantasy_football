from datetime import datetime, timezone
import random

from src.observability.context import RunContext
from src.observability.diff import diff_replay_bundles, diff_values
from src.observability.snapshots import write_snapshot_bundle


UTC = timezone.utc


def test_structural_diff_is_bounded_and_redacts_by_default():
    before = {
        "a": 1,
        "nested": {"token": "secret-left", "x": 1},
        "items": [1, 2],
    }
    after = {
        "a": 2,
        "nested": {"token": "secret-right", "x": "1"},
        "items": [1, 3, 4],
        "new": True,
    }

    result = diff_values(before, after)
    rows = [entry.to_dict() for entry in result.entries]
    assert any(row["path"] == "$.a" and row["kind"] == "CHANGED" for row in rows)
    assert any(
        row["path"] == "$.nested.x" and row["kind"] == "TYPE_CHANGED"
        for row in rows
    )
    assert any(row["path"] == "$.new" and row["kind"] == "ADDED" for row in rows)

    serialized = repr(rows)
    assert "secret-left" not in serialized
    assert "secret-right" not in serialized

    capped = diff_values(
        {"a": 1, "b": 1, "c": 1},
        {"a": 2, "b": 2, "c": 2},
        max_differences=2,
    )
    assert len(capped.entries) == 2
    assert capped.truncated


def _write(path, run_id, decision):
    context = RunContext.create(
        subsystem="observability",
        run_id=run_id,
        timestamp=datetime(2026, 9, 17, 15, 0, tzinfo=UTC),
    )
    write_snapshot_bundle(
        path,
        context=context,
        inputs_manifest={"input": 1},
        config_snapshot={"config": 1},
        decision_snapshot=decision,
        events=[],
        summary={"status": "ok"},
    )


def test_replay_bundle_diff_uses_verified_loaded_evidence(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    _write(left, "run:left", {"choice": "hold"})
    _write(right, "run:right", {"choice": "add"})

    result = diff_replay_bundles(left, right)
    paths = {entry.path for entry in result.entries}
    assert "$.decision_snapshot.choice" in paths
    assert "$.run_manifest.context.run_id" in paths


def test_diff_does_not_advance_python_rng():
    random.seed(30303)
    before = random.getstate()
    result = diff_values({"x": 1}, {"x": 2})
    assert result.changed
    assert random.getstate() == before
