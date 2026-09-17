from datetime import datetime, timezone
import random

import pytest

from src.observability.context import RunContext
from src.observability.events import make_event
from src.observability.replay import load_replay_bundle, verify_replay_bundle
from src.observability.snapshots import write_snapshot_bundle


UTC = timezone.utc


def _bundle(tmp_path):
    context = RunContext.create(
        subsystem="observability",
        run_id="run:replay",
        timestamp=datetime(2026, 9, 17, 14, 0, tzinfo=UTC),
    )
    event = make_event(
        context,
        "run.complete",
        timestamp=datetime(2026, 9, 17, 14, 1, tzinfo=UTC),
        payload={"count": 1},
    )
    path = tmp_path / "bundle"
    write_snapshot_bundle(
        path,
        context=context,
        inputs_manifest={"input": "x"},
        config_snapshot={"config": 1},
        decision_snapshot={"decision": "hold"},
        events=[event],
        summary={"status": "ok"},
    )
    return path


def test_replay_verification_and_load_round_trip(tmp_path):
    path = _bundle(tmp_path)
    result = verify_replay_bundle(path)
    assert result.ok
    assert result.member_count == 6

    bundle = load_replay_bundle(path)
    assert bundle.run_id == "run:replay"
    assert bundle.summary["status"] == "ok"
    assert bundle.events[0]["event_name"] == "run.complete"


def test_replay_verification_detects_tampering(tmp_path):
    path = _bundle(tmp_path)
    summary = path / "summary.json"
    summary.write_text('{"status":"tampered"}\n', encoding="utf-8")

    result = verify_replay_bundle(path)
    assert not result.ok
    assert any("summary.json" in problem for problem in result.problems)

    with pytest.raises(ValueError, match="integrity failure"):
        load_replay_bundle(path)


def test_replay_loader_can_be_explicitly_unverified(tmp_path):
    path = _bundle(tmp_path)
    (path / "summary.json").write_text(
        '{"status":"manual"}\n',
        encoding="utf-8",
    )
    bundle = load_replay_bundle(path, verify=False)
    assert bundle.summary["status"] == "manual"


def test_replay_verification_does_not_advance_python_rng(tmp_path):
    path = _bundle(tmp_path)
    random.seed(20202)
    before = random.getstate()
    verify_replay_bundle(path)
    load_replay_bundle(path)
    assert random.getstate() == before
