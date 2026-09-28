from datetime import datetime, timezone
import json
import random

import pytest

from src.observability import RedactingJsonlSink, RedactionPolicy, RunContext, make_event

UTC = timezone.utc


def event(payload):
    ctx = RunContext.create(
        subsystem="gui",
        run_id="run:persistent_sink",
        timestamp=datetime(2026, 9, 24, 17, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="9af4df1bcc848b525c1565ea6d054c9fb313cc89",
    ).for_action(action_id="action:persistent_sink")
    return make_event(
        ctx,
        "gui.notification",
        timestamp=datetime(2026, 9, 24, 17, 1, tzinfo=UTC),
        payload=payload,
    )


def test_sensitive_bytes_removed_and_event_unchanged(tmp_path):
    e = event({
        "password": "hunter2",
        "Authorization": "Bearer abc.def",
        "cookie": "espn_s2=COOKIEVALUE; SWID={PRIVATE}",
        "note": "EXACT_SECRET_123",
        "safe": "retained",
    })
    path = tmp_path / "events.jsonl"
    RedactingJsonlSink(
        path,
        policy=RedactionPolicy(sensitive_exact_values=("EXACT_SECRET_123",)),
    ).emit(e)
    data = path.read_bytes()
    for secret in (
        b"hunter2", b"abc.def", b"COOKIEVALUE", b"{PRIVATE}", b"EXACT_SECRET_123"
    ):
        assert secret not in data
    row = json.loads(data.decode("utf-8"))
    assert row["payload"]["password"] == "[REDACTED]"
    assert row["payload"]["Authorization"] == "[REDACTED]"
    assert row["payload"]["cookie"] == "[REDACTED]"
    assert row["payload"]["safe"] == "retained"
    assert e.payload["password"] == "hunter2"
    assert e.payload["safe"] == "retained"


def test_private_id_keys_redacted_generated_run_id_kept(tmp_path):
    e = event({
        "client_id": "private-client",
        "league_id": "private-league",
        "session_id": "private-session",
        "value": 7,
    })
    path = tmp_path / "events.jsonl"
    RedactingJsonlSink(path).emit(e)
    data = path.read_bytes()
    assert b"private-client" not in data
    assert b"private-league" not in data
    assert b"private-session" not in data
    row = json.loads(data.decode("utf-8"))
    assert row["payload"]["client_id"] == "[REDACTED]"
    assert row["payload"]["league_id"] == "[REDACTED]"
    assert row["payload"]["session_id"] == "[REDACTED]"
    assert row["run_id"] == "run:persistent_sink"


def test_one_event_per_line(tmp_path):
    path = tmp_path / "events.jsonl"
    sink = RedactingJsonlSink(path)
    sink.emit(event({"sequence": 1}))
    sink.emit(event({"sequence": 2}))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert [json.loads(line)["payload"]["sequence"] for line in lines] == [1, 2]


def test_invalid_policy_rejected(tmp_path):
    with pytest.raises(TypeError, match="policy must be a RedactionPolicy or None"):
        RedactingJsonlSink(tmp_path / "events.jsonl", policy=object())


def test_rng_state_unchanged(tmp_path):
    random.seed(90924)
    before = random.getstate()
    RedactingJsonlSink(tmp_path / "events.jsonl").emit(event({"value": 1}))
    assert random.getstate() == before
