from __future__ import annotations

from datetime import datetime, timezone
import json
import random
import re

from src.observability.context import RunContext
from src.observability.events import make_event
from src.observability.persistence import (
    PersistenceController,
    PersistencePolicy,
)
from src.observability.redaction import RedactionPolicy
from src.observability.shadow_pilot import ShadowRecorder
from src.observability.gui_shadow import GuiShadowRecorder


UTC = timezone.utc
SAFE_SEGMENT = re.compile(
    r"^events-[0-9]{8}T[0-9]{6}Z-p[0-9]+-s[0-9]{4}\.jsonl$"
)


def event(*, day: int = 28, payload=None):
    ctx = RunContext.create(
        subsystem="gui",
        run_id="run:persistence_controller",
        timestamp=datetime(2026, 9, day, 12, 0, tzinfo=UTC),
    ).for_action(action_id=f"action:persistence_{day}")
    return make_event(
        ctx,
        "gui.notification",
        timestamp=datetime(2026, 9, day, 12, 1, tzinfo=UTC),
        payload={} if payload is None else payload,
    )


def test_controller_is_disabled_by_default_and_creates_nothing(tmp_path):
    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(root)
    assert controller.emit(event()) is None
    assert not root.exists()
    state = controller.state()
    assert state.enabled is False
    assert state.segments == 0
    assert state.total_bytes == 0


def test_enabled_controller_redacts_before_write_and_uses_windows_safe_name(tmp_path):
    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(
        root,
        policy=PersistencePolicy(enabled=True),
        redaction_policy=RedactionPolicy(
            sensitive_exact_values=("EXACT_SECRET_123",)
        ),
    )
    e = event(
        payload={
            "password": "hunter2",
            "cookie": "espn_s2=COOKIEVALUE; SWID={PRIVATE}",
            "client_id": "PRIVATE_CLIENT",
            "note": "EXACT_SECRET_123",
            "safe": "retained",
        }
    )
    assert controller.emit(e) is True

    files = list(root.iterdir())
    assert len(files) == 1
    assert SAFE_SEGMENT.fullmatch(files[0].name)
    assert ":" not in files[0].name
    raw = files[0].read_bytes()
    for secret in (
        b"hunter2",
        b"COOKIEVALUE",
        b"{PRIVATE}",
        b"PRIVATE_CLIENT",
        b"EXACT_SECRET_123",
    ):
        assert secret not in raw
    row = json.loads(raw.decode("utf-8"))
    assert row["payload"]["safe"] == "retained"
    assert e.payload["password"] == "hunter2"


def test_rotation_occurs_by_size_without_deleting_prior_segment(tmp_path):
    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(
        root,
        policy=PersistencePolicy(
            enabled=True,
            rotate_bytes=1,
            max_total_bytes=10_000_000,
        ),
    )
    assert controller.emit(event(payload={"sequence": 1})) is True
    assert controller.emit(event(payload={"sequence": 2})) is True
    files = sorted(root.iterdir())
    assert len(files) == 2
    assert all(path.exists() for path in files)


def test_rotation_occurs_at_utc_day_boundary(tmp_path):
    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(
        root,
        policy=PersistencePolicy(enabled=True, max_total_bytes=10_000_000),
    )
    assert controller.emit(event(day=28)) is True
    assert controller.emit(event(day=29)) is True
    assert len(list(root.iterdir())) == 2


def test_storage_limit_disables_future_writes_without_deleting_evidence(tmp_path):
    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(
        root,
        policy=PersistencePolicy(
            enabled=True,
            rotate_bytes=10_000_000,
            max_total_bytes=1,
        ),
    )
    assert controller.emit(event(payload={"sequence": 1})) is True
    before = tuple(sorted(path.name for path in root.iterdir()))
    state = controller.state()
    assert state.enabled is False
    assert state.disabled_reason == "storage_limit"
    assert controller.emit(event(payload={"sequence": 2})) is None
    assert tuple(sorted(path.name for path in root.iterdir())) == before


def test_disk_failure_is_fail_open_and_disables_controller(tmp_path, monkeypatch):
    from src.observability import persistence as persistence_module

    root = tmp_path / "logs" / "observability"
    controller = PersistenceController(
        root,
        policy=PersistencePolicy(enabled=True),
    )

    def broken_emit(self, event):
        raise OSError("PRIVATE_DISK_FAILURE")

    monkeypatch.setattr(persistence_module.RedactingJsonlSink, "emit", broken_emit)
    assert controller.emit(event()) is False
    state = controller.state()
    assert state.enabled is False
    assert state.failed is True
    assert state.failures == 1
    assert state.disabled_reason == "disk_error:OSError"
    assert "PRIVATE_DISK_FAILURE" not in state.disabled_reason


def test_shadow_recorder_result_survives_persistence_failure(monkeypatch):
    import src.observability.shadow_pilot as shadow_module

    monkeypatch.setattr(shadow_module, "persist_shadow_event", lambda _event: False)
    recorder = ShadowRecorder(root_subsystem="observability")
    marker = object()
    assert recorder.call_cli("unit.persistence_failure", lambda: marker) is marker
    assert recorder.observer_failures >= 1


def test_gui_recorder_survives_persistence_failure(monkeypatch):
    import src.observability.gui_shadow as gui_module

    monkeypatch.setattr(gui_module, "persist_shadow_event", lambda _event: False)
    recorder = GuiShadowRecorder()
    page = recorder.open_page()
    assert page.deleted is False
    assert recorder.observer_failures >= 1
    assert recorder.snapshot()


def test_controller_does_not_advance_python_random_state(tmp_path):
    controller = PersistenceController(
        tmp_path / "logs" / "observability",
        policy=PersistencePolicy(enabled=True),
    )
    random.seed(20260928)
    before = random.getstate()
    assert controller.emit(event(payload={"value": 1})) is True
    assert random.getstate() == before
