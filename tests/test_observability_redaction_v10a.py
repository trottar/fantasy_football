from types import SimpleNamespace
import random

import pytest

from src.observability.redaction import (
    BINARY_REPLACEMENT,
    DEPTH_REPLACEMENT,
    RedactionPolicy,
    is_sensitive_key,
    pseudonymize_text,
    redact,
    redact_event,
    redact_value,
    redacted_event_json,
)


def test_sensitive_key_detection_is_conservative_but_keeps_run_id():
    assert is_sensitive_key("password")
    assert is_sensitive_key("access-token")
    assert is_sensitive_key("espn_s2")
    assert is_sensitive_key("SWID")
    assert is_sensitive_key("session_id")
    assert is_sensitive_key("client-id")
    assert is_sensitive_key("league_id")
    assert not is_sensitive_key("run_id")
    assert not is_sensitive_key("event_name")
    assert not is_sensitive_key("week")


def test_recursive_redaction_does_not_mutate_input():
    source = {
        "run_id": "run:test",
        "payload": {
            "password": "hunter2",
            "nested": [{"access_token": "abc123"}],
        },
    }
    result = redact(source)
    row = result.to_value()
    assert row["run_id"] == "run:test"
    assert row["payload"]["password"] == "[REDACTED]"
    assert row["payload"]["nested"][0]["access_token"] == "[REDACTED]"
    assert source["payload"]["password"] == "hunter2"
    assert source["payload"]["nested"][0]["access_token"] == "abc123"
    assert result.redacted_fields == 2


def test_inline_headers_assignments_and_exact_values_are_redacted():
    policy = RedactionPolicy(
        sensitive_exact_values=("EXACT_SECRET_123",),
    )
    text = (
        "Authorization: Bearer abc.def\n"
        "espn_s2=COOKIEVALUE; swid={ABC}; "
        "note=EXACT_SECRET_123"
    )
    redacted = redact_value(text, policy=policy)
    assert "abc.def" not in redacted
    assert "COOKIEVALUE" not in redacted
    assert "{ABC}" not in redacted
    assert "EXACT_SECRET_123" not in redacted
    assert "[REDACTED]" in redacted


def test_binary_and_depth_limits_are_conservative():
    result = redact({"blob": b"private-bytes"})
    assert result.to_value()["blob"] == BINARY_REPLACEMENT
    assert result.binary_replacements == 1

    policy = RedactionPolicy(max_depth=2)
    nested = {"a": {"b": {"c": {"d": 1}}}}
    row = redact_value(nested, policy=policy)
    assert DEPTH_REPLACEMENT in str(row)


def test_event_redaction_accepts_mapping_or_to_dict_without_mutating_event():
    raw = {
        "event_name": "gui.notification",
        "run_id": "run:test",
        "payload": {
            "cookie": "private",
            "message": "safe",
        },
    }

    class FakeEvent:
        def to_dict(self):
            return raw

    result = redact_event(FakeEvent())
    row = result.to_value()
    assert row["event_name"] == "gui.notification"
    assert row["payload"]["cookie"] == "[REDACTED]"
    assert raw["payload"]["cookie"] == "private"
    text = redacted_event_json(FakeEvent())
    assert "private" not in text
    assert "safe" in text


def test_pseudonymization_is_keyed_deterministic_and_namespace_scoped():
    key = b"0123456789abcdef0123456789abcdef"
    first = pseudonymize_text("client-123", key=key, namespace="client")
    second = pseudonymize_text("client-123", key=key, namespace="client")
    other = pseudonymize_text("client-123", key=key, namespace="session")
    assert first == second
    assert first.startswith("client:")
    assert other.startswith("session:")
    assert first != other
    assert "client-123" not in first


def test_pseudonymization_rejects_weak_key():
    with pytest.raises(ValueError, match="at least 16 bytes"):
        pseudonymize_text("x", key=b"short", namespace="id")


def test_redaction_rejects_non_finite_float():
    with pytest.raises(ValueError, match="non-finite"):
        redact_value({"value": float("nan")})


def test_redaction_does_not_advance_random_state():
    random.seed(4242)
    before = random.getstate()
    redact(
        {
            "password": "secret",
            "run_id": "run:test",
        },
        policy=RedactionPolicy(
            sensitive_exact_values=("secret",),
        ),
    )
    assert random.getstate() == before
