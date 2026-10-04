from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from src.weekly_decision_cycle import _default_lineup, _lineup_receipt


def _player(
    pid: int,
    name: str,
    position: str,
    points: float,
    slot: str,
    *,
    locked: bool = False,
    kickoff: str | None = "2026-10-04T22:00:00+00:00",
):
    return {
        "espn_id": pid,
        "name": name,
        "position": position,
        "projection_points": points,
        "injury_status": "ACTIVE",
        "lineup_slot": slot,
        "lineup_locked": locked,
        "_test_kickoff": kickoff,
    }


def _snapshot(roster):
    return {
        "snapshot_utc": "2026-10-04T21:30:24+00:00",
        "espn": {
            "season": 2026,
            "week": 4,
            "teams": [{"team_id": 1, "name": "Us", "roster": roster}],
        },
    }


def _model():
    return {
        "weekly_manager": {
            "status_active_probability": {"ACTIVE": 1.0},
        }
    }


class _FakeContext:
    def __init__(self, snapshot, league, model, values_path, team):
        self.roster = [dict(row) for row in team.get("roster") or []]
        self.week = int((snapshot.get("espn") or snapshot).get("week") or 1)

    def lock_timing(self, player, week):
        raw = player.get("_test_kickoff")
        if raw is None:
            return SimpleNamespace(kickoff=None, source="NO_SCHEDULE")
        return SimpleNamespace(
            kickoff=datetime.fromisoformat(raw),
            source="TEST_SCHEDULE",
        )


def _install_fake_context(monkeypatch):
    import src.transaction_manager as transaction_manager
    monkeypatch.setattr(transaction_manager, "UtilityContext", _FakeContext)


def test_locked_bench_cannot_enter_and_locked_starter_is_frozen(monkeypatch, tmp_path):
    _install_fake_context(monkeypatch)
    roster = [
        _player(1, "Locked Bench WR", "WR", 50.0, "BENCH", locked=True, kickoff=None),
        _player(2, "Locked FLEX RB", "RB", 5.0, "FLEX", locked=True, kickoff=None),
        _player(3, "Current WR", "WR", 10.0, "WR"),
        _player(4, "Better Unlocked WR", "WR", 20.0, "BENCH"),
    ]
    report = _default_lineup(
        _snapshot(roster),
        {"roster": {"WR": 1, "FLEX": 1}},
        _model(),
        values_path=tmp_path / "unused.csv",
        team_id=1,
        team_name=None,
    )
    assert report["lineup_legality_complete"] is True
    assert report["locked_starter_espn_ids"] == [2]
    assert report["locked_bench_espn_ids"] == [1]
    assert report["selected_espn_ids"] == [2, 4]
    assert report["current_starter_espn_ids"] == [2, 3]
    assert 1 not in report["selected_espn_ids"]
    assert report["action_required"] is True
    assert report["total_expected"] == 25.0


def test_kickoff_locked_bench_without_espn_flag_stays_bench(monkeypatch, tmp_path):
    _install_fake_context(monkeypatch)
    roster = [
        _player(
            1, "Kickoff Locked Bench", "WR", 50.0, "BENCH",
            kickoff="2026-10-04T20:00:00+00:00",
        ),
        _player(2, "Current WR", "WR", 10.0, "WR"),
    ]
    report = _default_lineup(
        _snapshot(roster),
        {"roster": {"WR": 1}},
        _model(),
        values_path=tmp_path / "unused.csv",
        team_id=1,
        team_name=None,
    )
    assert report["lineup_legality_complete"] is True
    assert report["locked_bench_espn_ids"] == [1]
    assert report["selected_espn_ids"] == [2]
    assert report["action_required"] is False


def test_unknown_lock_state_fails_closed(monkeypatch, tmp_path):
    _install_fake_context(monkeypatch)
    roster = [
        _player(1, "Unknown Timing WR", "WR", 20.0, "WR", kickoff=None),
    ]
    report = _default_lineup(
        _snapshot(roster),
        {"roster": {"WR": 1}},
        _model(),
        values_path=tmp_path / "unused.csv",
        team_id=1,
        team_name=None,
    )
    assert report["lineup_legality_complete"] is False
    assert report["unresolved_lock_espn_ids"] == [1]
    assert report["action_required"] is False
    receipt = _lineup_receipt(report)
    assert receipt.status == "INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY"
    assert receipt.action is None


def test_unsupported_current_slot_fails_closed(monkeypatch, tmp_path):
    _install_fake_context(monkeypatch)
    roster = [
        _player(1, "Unsupported Slot", "WR", 20.0, "MYSTERY"),
    ]
    report = _default_lineup(
        _snapshot(roster),
        {"roster": {"WR": 1}},
        _model(),
        values_path=tmp_path / "unused.csv",
        team_id=1,
        team_name=None,
    )
    assert report["lineup_legality_complete"] is False
    assert any(
        gap.startswith("unsupported_current_lineup_slot:1:")
        for gap in report["lineup_legality_gaps"]
    )
    assert _lineup_receipt(report).status == "INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY"
