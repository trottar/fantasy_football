from datetime import datetime, timezone
import json
import random

import pytest

from src.observability.context import RunContext
from src.observability.events import make_event
from src.observability.failure_bundle import (
    FAILURE_MEMBER_FILES,
    OMITTED_EXCEPTION_MESSAGE,
    load_failure_bundle,
    summarize_exception,
    verify_failure_bundle,
    write_failure_bundle,
)
from src.observability.invariants import CORE_INVARIANT_REGISTRY
from src.observability.redaction import RedactionPolicy

UTC = timezone.utc


def _context():
    return RunContext.create(
        subsystem="observability",
        run_id="run:failure-test",
        timestamp=datetime(2026, 9, 17, 18, 0, tzinfo=UTC),
        release_version="0.36",
        source_commit="304f84c4deb8557e759afc6ebb10daf501bfe01e",
        config_hash="a" * 64,
        input_snapshot_hash="b" * 64,
    )


def _error(secret="super-secret-token"):
    try:
        raise RuntimeError(f"Authorization: Bearer {secret}")
    except RuntimeError as exc:
        return exc


def test_exception_summary_omits_message_and_full_paths_by_default():
    row = summarize_exception(_error())
    assert row["error_type"] == "RuntimeError"
    assert row["message"] == OMITTED_EXCEPTION_MESSAGE
    assert row["frames"]
    assert all(
        "/" not in frame["file"] and "\\" not in frame["file"]
        for frame in row["frames"]
    )
    assert all("source" not in frame for frame in row["frames"])


def test_opt_in_exception_message_is_redacted():
    row = summarize_exception(_error("abc123"), include_message=True)
    text = json.dumps(row)
    assert "abc123" not in text
    assert "[REDACTED]" in text


def test_failure_bundle_is_bounded_redacted_verified_and_loadable(tmp_path):
    context = _context()
    events = [
        make_event(
            context,
            "action.start",
            payload={"sequence": i, "espn_s2": f"secret-{i}"},
        )
        for i in range(5)
    ]
    invariants = [
        CORE_INVARIANT_REGISTRY.result(
            "authority.screen_not_authority",
            passed=(i % 2 == 0),
            context=context,
            details={"sequence": i, "session_id": f"private-{i}"},
        )
        for i in range(5)
    ]

    destination = tmp_path / "failure"
    manifest = write_failure_bundle(
        destination,
        context=context,
        error=_error("message-secret"),
        events=events,
        invariants=invariants,
        state_summary={"authorization": "Bearer raw-secret", "safe": 7},
        reproduction={"command": "python fantasy.py test", "cookie": "sensitive"},
        project_modification_state={
            "project_files_modified": False,
            "path": "safe/path",
        },
        runtime_side_effects={
            "temp_dir_created": True,
            "account_id": "private",
        },
        include_exception_message=True,
        max_events=2,
        max_invariants=2,
    )

    assert {row.path for row in manifest.members} == set(FAILURE_MEMBER_FILES)
    assert verify_failure_bundle(destination).ok

    loaded = load_failure_bundle(destination)
    assert loaded.run_id == context.run_id
    assert len(loaded.events) == 2
    assert [row["payload"]["sequence"] for row in loaded.events] == [3, 4]
    assert len(loaded.invariants) == 2
    assert (
        loaded.effects["project_modification_state"]["project_files_modified"]
        is False
    )
    assert loaded.effects["runtime_side_effects"]["temp_dir_created"] is True

    joined = b"\n".join(path.read_bytes() for path in destination.iterdir())
    for secret in (
        b"message-secret",
        b"raw-secret",
        b"sensitive",
        b"private-4",
        b"secret-4",
    ):
        assert secret not in joined


def test_failure_bundle_does_not_mutate_callers(tmp_path):
    state = {"nested": {"espn_s2": "secret"}}
    reproduction = {"args": ["--league", "123"]}
    original_state = json.loads(json.dumps(state))
    original_reproduction = json.loads(json.dumps(reproduction))

    write_failure_bundle(
        tmp_path / "bundle",
        context=_context(),
        error=_error(),
        state_summary=state,
        reproduction=reproduction,
    )

    assert state == original_state
    assert reproduction == original_reproduction


def test_existing_destination_is_not_overwritten(tmp_path):
    destination = tmp_path / "failure"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_failure_bundle(
            destination,
            context=_context(),
            error=_error(),
        )

    assert marker.read_text(encoding="utf-8") == "keep"


def test_tampering_is_detected(tmp_path):
    destination = tmp_path / "failure"
    write_failure_bundle(
        destination,
        context=_context(),
        error=_error(),
    )

    (destination / "state_summary.json").write_text(
        '{"tampered":true}\n',
        encoding="utf-8",
    )
    result = verify_failure_bundle(destination)
    assert not result.ok
    assert any("state_summary.json" in problem for problem in result.problems)

    with pytest.raises(ValueError, match="integrity failure"):
        load_failure_bundle(destination)


def test_effect_categories_remain_distinct(tmp_path):
    destination = tmp_path / "failure"
    write_failure_bundle(
        destination,
        context=_context(),
        error=_error(),
        project_modification_state={"modified": False},
        runtime_side_effects={"temporary_socket": True},
    )
    loaded = load_failure_bundle(destination)
    assert loaded.effects == {
        "project_modification_state": {"modified": False},
        "runtime_side_effects": {"temporary_socket": True},
    }


def test_invalid_bounds_rejected(tmp_path):
    with pytest.raises(ValueError):
        write_failure_bundle(
            tmp_path / "x",
            context=_context(),
            error=_error(),
            max_events=0,
        )

    with pytest.raises(TypeError):
        write_failure_bundle(
            tmp_path / "y",
            context=_context(),
            error=_error(),
            max_invariants=True,
        )


def test_custom_exact_secret_policy_applies_to_failure_message(tmp_path):
    secret = "private-nonstandard-value"
    policy = RedactionPolicy(sensitive_exact_values=(secret,))
    destination = tmp_path / "failure"

    write_failure_bundle(
        destination,
        context=_context(),
        error=ValueError(f"unsafe={secret}"),
        include_exception_message=True,
        policy=policy,
    )

    text = (destination / "failure.json").read_text(encoding="utf-8")
    assert secret not in text
    assert "[REDACTED]" in text


def test_failure_bundle_does_not_advance_python_random_state(tmp_path):
    random.seed(10101)
    before = random.getstate()

    write_failure_bundle(
        tmp_path / "failure",
        context=_context(),
        error=_error(),
    )

    after = random.getstate()
    assert after == before
