from __future__ import annotations

import copy
from datetime import datetime as RealDateTime, timezone
from pathlib import Path
import random
import shutil
from types import SimpleNamespace

import pytest

from src import season_snapshot
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.shadow_pilot import (
    ShadowRecorder,
    clear_data_source_shadow_events,
    last_data_source_shadow_events,
)
import src.observability.shadow_pilot as shadow_pilot


PRIVATE_PATH = "PRIVATE_ESPN_SECRET_PATH_DO_NOT_CAPTURE"
PRIVATE_PAYLOAD = "PRIVATE_ESPN_PAYLOAD_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_ESPN_ERROR_DO_NOT_CAPTURE"


class FrozenDateTime:
    @classmethod
    def now(cls, tz=None):
        value = RealDateTime(2026, 9, 24, 0, 0, 0, tzinfo=timezone.utc)
        return value if tz is None else value.astimezone(tz)


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


def _install_success_stubs(monkeypatch):
    monkeypatch.setattr(season_snapshot, "datetime", FrozenDateTime)
    monkeypatch.setattr(
        season_snapshot,
        "load_espn_secrets",
        lambda _path: SimpleNamespace(season=2026),
    )

    def fake_espn(_secrets, _out_dir, week=None):
        return {
            "season": 2026,
            "week": int(week or 3),
            "teams": [],
            "available_players": [],
            "private_marker": PRIVATE_PAYLOAD,
        }

    monkeypatch.setattr(
        season_snapshot,
        "sync_private_league_snapshot",
        fake_espn,
    )
    monkeypatch.setattr(
        season_snapshot,
        "sync_nflverse_rosters",
        lambda _out_dir, _season: (
            {},
            {"ok": True, "role": "test_stub"},
        ),
    )
    monkeypatch.setattr(
        season_snapshot,
        "sync_nflverse_matchups",
        lambda **_kwargs: {
            "source": {"current_pbp": {"rows": 0}},
            "prior_season": 2025,
            "defense_profiles": {},
            "offense_profiles": {},
            "team_week": {},
        },
    )


def _snapshot_call(out_root: Path):
    return season_snapshot.sync_season_snapshot(
        secrets_path=PRIVATE_PATH,
        out_root=out_root,
        week=3,
        include_sleeper=False,
        include_nfl=False,
    )


def _snapshot_direct(out_root: Path):
    return season_snapshot.sync_season_snapshot.__wrapped__(
        secrets_path=PRIVATE_PATH,
        out_root=out_root,
        week=3,
        include_sleeper=False,
        include_nfl=False,
    )


def _capture_tree(root: Path):
    if not root.exists():
        return None
    rows = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        rel = path.relative_to(root).as_posix()
        if path.is_dir():
            rows.append((rel, "dir", None))
        else:
            rows.append((rel, "file", path.read_bytes()))
    return tuple(rows)


def _restore_tree(root: Path, state) -> None:
    if root.exists():
        shutil.rmtree(root)
    if state is None:
        return
    root.mkdir(parents=True, exist_ok=True)
    for rel, kind, payload in state:
        path = root / rel
        if kind == "dir":
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)


def test_shadow_recorder_subsystem_boundary_preserves_result_and_channel():
    recorder = ShadowRecorder(root_subsystem="observability")
    marker = object()
    result = recorder.call_subsystem(
        "subsystem.data_source.unit",
        lambda: marker,
        subsystem="data_source",
    )
    assert result is marker
    events = recorder.snapshot()
    assert [event.event_name for event in events] == [
        "action.start",
        "action.complete",
    ]
    assert all(event.context.subsystem == "data_source" for event in events)
    rendered = _event_json(events)
    assert '"boundary_kind":"subsystem"' in rendered


def test_season_sync_shadow_success_preserves_output_and_omits_private_data(
    monkeypatch,
    tmp_path,
):
    _install_success_stubs(monkeypatch)
    clear_data_source_shadow_events()

    snapshot, path = _snapshot_call(tmp_path / "season_snapshots")

    assert snapshot["espn"]["private_marker"] == PRIVATE_PAYLOAD
    assert path.is_file()
    events = last_data_source_shadow_events()
    assert [event.event_name for event in events[-2:]] == [
        "action.start",
        "action.complete",
    ]
    assert all(event.context.subsystem == "data_source" for event in events[-2:])
    rendered = _event_json(events[-2:])
    assert "subsystem.data_source.season_sync" in rendered
    assert PRIVATE_PATH not in rendered
    assert PRIVATE_PAYLOAD not in rendered
    assert "snapshot.json" not in rendered
    assert "duration_ns" in rendered


def test_season_sync_shadow_error_preserves_exception_and_omits_message(
    monkeypatch,
    tmp_path,
):
    clear_data_source_shadow_events()

    def fail(_path):
        raise ValueError(PRIVATE_ERROR)

    monkeypatch.setattr(season_snapshot, "load_espn_secrets", fail)

    with pytest.raises(ValueError, match=PRIVATE_ERROR):
        _snapshot_call(tmp_path / "season_snapshots")

    rendered = _event_json(last_data_source_shadow_events())
    assert PRIVATE_ERROR not in rendered
    assert '"error_type":"ValueError"' in rendered


def test_data_source_observer_emit_failure_does_not_change_production_result(
    monkeypatch,
    tmp_path,
):
    _install_success_stubs(monkeypatch)
    clear_data_source_shadow_events()
    recorder = shadow_pilot._data_source_shadow_recorder()
    assert recorder is not None

    def broken_emit(_event):
        raise RuntimeError("observer-only failure")

    monkeypatch.setattr(recorder, "_emit", broken_emit)
    snapshot, path = _snapshot_call(tmp_path / "season_snapshots")
    assert snapshot["espn"]["private_marker"] == PRIVATE_PAYLOAD
    assert path.is_file()
    assert recorder.observer_failures >= 1


def test_data_source_shadow_does_not_advance_python_random_state(
    monkeypatch,
    tmp_path,
):
    _install_success_stubs(monkeypatch)
    clear_data_source_shadow_events()
    random.seed(20260921)
    before = random.getstate()
    _snapshot_call(tmp_path / "season_snapshots")
    assert random.getstate() == before


def test_season_sync_shadow_passes_paired_filesystem_rng_and_overhead_gate(
    monkeypatch,
    tmp_path,
):
    _install_success_stubs(monkeypatch)
    clear_data_source_shadow_events()
    out_root = tmp_path / "paired_snapshots"

    gate = benchmark_pair(
        lambda: _snapshot_direct(out_root),
        lambda: _snapshot_call(out_root),
        budget=OverheadBudget(
            max_incremental_ns=2_000_000,
            max_relative_fraction=0.20,
            relative_floor_ns=50_000_000,
            trials=15,
            warmups=3,
        ),
        probes=(
            python_random_probe(),
            StateProbe(
                "snapshot_tree",
                lambda: copy.deepcopy(_capture_tree(out_root)),
                lambda state: _restore_tree(out_root, copy.deepcopy(state)),
            ),
        ),
    )

    assert gate.passed, gate.to_dict()


def test_season_snapshot_wires_only_outer_sync_boundary():
    source = Path("src/season_snapshot.py").read_text(encoding="utf-8")
    assert (
        '@shadow_data_source_call("subsystem.data_source.season_sync")\n'
        "def sync_season_snapshot("
    ) in source
    assert source.count("shadow_data_source_call") == 2
    assert "last_data_source_shadow_events" not in source
    assert "source_status[" in source
