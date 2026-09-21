from __future__ import annotations

import argparse
import copy
from datetime import datetime as RealDateTime, timezone
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
from unittest.mock import patch

from src import season_snapshot
from src.observability.benchmark_gate import (
    OverheadBudget,
    StateProbe,
    benchmark_pair,
    python_random_probe,
)
from src.observability.shadow_pilot import (
    clear_data_source_shadow_events,
    last_data_source_shadow_events,
)

PRIVATE_PATH = "PRIVATE_PROBE_SECRET_PATH_DO_NOT_CAPTURE"
PRIVATE_PAYLOAD = "PRIVATE_PROBE_PAYLOAD_DO_NOT_CAPTURE"
PRIVATE_ERROR = "PRIVATE_PROBE_ERROR_DO_NOT_CAPTURE"


class FrozenDateTime:
    @classmethod
    def now(cls, tz=None):
        value = RealDateTime(2026, 9, 24, 0, 0, 0, tzinfo=timezone.utc)
        return value if tz is None else value.astimezone(tz)


def _event_json(events) -> str:
    return "\n".join(event.to_json() for event in events)


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


def _success_patches():
    def fake_espn(_secrets, _out_dir, week=None):
        return {
            "season": 2026,
            "week": int(week or 3),
            "teams": [],
            "available_players": [],
            "private_marker": PRIVATE_PAYLOAD,
        }

    return (
        patch.object(season_snapshot, "datetime", FrozenDateTime),
        patch.object(
            season_snapshot,
            "load_espn_secrets",
            lambda _path: SimpleNamespace(season=2026),
        ),
        patch.object(
            season_snapshot,
            "sync_private_league_snapshot",
            fake_espn,
        ),
        patch.object(
            season_snapshot,
            "sync_nflverse_rosters",
            lambda _out_dir, _season: ({}, {"ok": True, "role": "probe_stub"}),
        ),
        patch.object(
            season_snapshot,
            "sync_nflverse_matchups",
            lambda **_kwargs: {
                "source": {"current_pbp": {"rows": 0}},
                "prior_season": 2025,
                "defense_profiles": {},
                "offense_profiles": {},
                "team_week": {},
            },
        ),
    )


def _call(out_root: Path):
    return season_snapshot.sync_season_snapshot(
        secrets_path=PRIVATE_PATH,
        out_root=out_root,
        week=3,
        include_sleeper=False,
        include_nfl=False,
    )


def _direct(out_root: Path):
    return season_snapshot.sync_season_snapshot.__wrapped__(
        secrets_path=PRIVATE_PATH,
        out_root=out_root,
        week=3,
        include_sleeper=False,
        include_nfl=False,
    )


def run_probe(work_root: Path) -> dict[str, object]:
    work_root.mkdir(parents=True, exist_ok=True)
    clear_data_source_shadow_events()
    managers = _success_patches()
    for manager in managers:
        manager.start()
    try:
        success_root = work_root / "success"
        observed = _call(success_root)
        events = last_data_source_shadow_events()
        rendered = _event_json(events[-2:])
        privacy_ok = all(
            marker not in rendered
            for marker in (PRIVATE_PATH, PRIVATE_PAYLOAD, "snapshot.json")
        )
        event_shape_ok = (
            [event.event_name for event in events[-2:]]
            == ["action.start", "action.complete"]
            and all(event.context.subsystem == "data_source" for event in events[-2:])
            and "subsystem.data_source.season_sync" in rendered
        )
        success_ok = (
            observed[0]["espn"]["private_marker"] == PRIVATE_PAYLOAD
            and observed[1].is_file()
        )

        paired_root = work_root / "paired"
        clear_data_source_shadow_events()
        gate = benchmark_pair(
            lambda: _direct(paired_root),
            lambda: _call(paired_root),
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
                    lambda: copy.deepcopy(_capture_tree(paired_root)),
                    lambda state: _restore_tree(paired_root, copy.deepcopy(state)),
                ),
            ),
        )
    finally:
        for manager in reversed(managers):
            manager.stop()

    clear_data_source_shadow_events()
    error_type_equal = False
    error_message_preserved = False
    with patch.object(
        season_snapshot,
        "load_espn_secrets",
        side_effect=ValueError(PRIVATE_ERROR),
    ):
        direct_exc = observed_exc = None
        try:
            season_snapshot.sync_season_snapshot.__wrapped__(
                secrets_path=PRIVATE_PATH,
                out_root=work_root / "error_direct",
                week=3,
                include_sleeper=False,
                include_nfl=False,
            )
        except Exception as exc:
            direct_exc = exc
        try:
            _call(work_root / "error_observed")
        except Exception as exc:
            observed_exc = exc
        error_type_equal = (
            direct_exc is not None
            and observed_exc is not None
            and type(direct_exc) is type(observed_exc)
        )
        error_message_preserved = (
            observed_exc is not None and str(observed_exc) == PRIVATE_ERROR
        )
    error_rendered = _event_json(last_data_source_shadow_events())
    error_privacy_ok = PRIVATE_ERROR not in error_rendered

    result = {
        "schema": 1,
        "boundary": "subsystem.data_source.season_sync",
        "success_behavior_preserved": success_ok,
        "event_shape_ok": event_shape_ok,
        "privacy_success_ok": privacy_ok,
        "error_type_equal": error_type_equal,
        "error_message_preserved_to_caller": error_message_preserved,
        "privacy_error_ok": error_privacy_ok,
        "persistent_sink": False,
        "arguments_captured": False,
        "return_values_captured": False,
        "exception_messages_captured": False,
        "benchmark": gate.to_dict(),
    }
    result["passed"] = bool(
        success_ok
        and event_shape_ok
        and privacy_ok
        and error_type_equal
        and error_message_preserved
        and error_privacy_ok
        and gate.passed
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", default=".probe_data_source_shadow")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    root = Path(args.work_root).resolve()
    if root.exists():
        shutil.rmtree(root)
    try:
        result = run_probe(root)
        text = json.dumps(result, indent=2, sort_keys=True)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        return 0 if result["passed"] else 1
    finally:
        if root.exists():
            shutil.rmtree(root)


if __name__ == "__main__":
    raise SystemExit(main())
