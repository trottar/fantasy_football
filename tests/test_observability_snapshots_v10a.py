from datetime import datetime, timezone
import random

import pytest

from src.observability.context import RunContext
from src.observability.events import make_event
from src.observability.redaction import RedactionPolicy
from src.observability.snapshots import (
    BUNDLE_MANIFEST_FILE,
    CORE_MEMBER_FILES,
    write_snapshot_bundle,
)


UTC = timezone.utc


def _context():
    return RunContext.create(
        subsystem="observability",
        run_id="run:snapshot",
        timestamp=datetime(2026, 9, 17, 13, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="c" * 40,
        week=2,
        config_hash="a" * 64,
        input_snapshot_hash="b" * 64,
    )


def _event(context):
    return make_event(
        context,
        "run.start",
        timestamp=datetime(2026, 9, 17, 13, 1, tzinfo=UTC),
        payload={"Authorization": "Bearer super-secret", "value": 3},
    )


def test_snapshot_bundle_is_fixed_atomic_redacted_and_deterministic(tmp_path):
    context = _context()
    inputs = {"source": "fixture", "account_id": "private-account"}
    config = {"threshold": 2, "api_key": "private-key"}
    decision = {"choice": "hold", "cookie": "session=private"}
    summary = {"note": "Authorization: Bearer abcdef"}

    first = tmp_path / "first"
    second = tmp_path / "second"

    policy = RedactionPolicy(sensitive_exact_values=("super-secret",))
    manifest1 = write_snapshot_bundle(
        first,
        context=context,
        inputs_manifest=inputs,
        config_snapshot=config,
        decision_snapshot=decision,
        events=[_event(context)],
        summary=summary,
        policy=policy,
    )
    manifest2 = write_snapshot_bundle(
        second,
        context=context,
        inputs_manifest=inputs,
        config_snapshot=config,
        decision_snapshot=decision,
        events=[_event(context)],
        summary=summary,
        policy=policy,
    )

    assert set(p.name for p in first.iterdir()) == {
        *CORE_MEMBER_FILES,
        BUNDLE_MANIFEST_FILE,
    }
    assert manifest1.to_dict() == manifest2.to_dict()
    for name in (*CORE_MEMBER_FILES, BUNDLE_MANIFEST_FILE):
        assert (first / name).read_bytes() == (second / name).read_bytes()

    combined = b"".join((first / name).read_bytes() for name in CORE_MEMBER_FILES)
    assert b"private-account" not in combined
    assert b"private-key" not in combined
    assert b"super-secret" not in combined
    assert b"[REDACTED]" in combined

    assert inputs["account_id"] == "private-account"
    assert config["api_key"] == "private-key"


def test_snapshot_refuses_existing_destination(tmp_path):
    destination = tmp_path / "bundle"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        write_snapshot_bundle(
            destination,
            context=_context(),
            inputs_manifest={},
            config_snapshot={},
            decision_snapshot={},
            events=[],
            summary={},
        )


def test_snapshot_creation_does_not_advance_python_rng(tmp_path):
    random.seed(10101)
    before = random.getstate()
    write_snapshot_bundle(
        tmp_path / "bundle",
        context=_context(),
        inputs_manifest={},
        config_snapshot={},
        decision_snapshot={},
        events=[],
        summary={},
    )
    assert random.getstate() == before
