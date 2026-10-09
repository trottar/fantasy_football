"""Week 5 known-bye versus unknown-schedule lineup authorization regression."""
from datetime import datetime
from types import SimpleNamespace

from src.weekly_decision_cycle import _default_lineup, _lineup_receipt


def _player(pid, name, position, slot, *, nfl_team="KC", bye=False, locked=False, kickoff=None, source="NO_SCHEDULE"):
    return {
        "espn_id": pid,
        "name": name,
        "position": position,
        "nfl_team": nfl_team,
        "lineup_slot": slot,
        "lineup_locked": locked,
        "injury_status": "ACTIVE",
        "projection_points": 7.0,
        "is_bye_week": bye,
        "_kickoff": kickoff,
        "_source": source,
    }


class _FakeContext:
    def __init__(self, snapshot, league, model, values_path, team):
        self.roster = [dict(p) for p in team["roster"]]
        self.week = int(snapshot["espn"]["week"])

    def lock_timing(self, player, week):
        raw = player.get("_kickoff")
        return SimpleNamespace(
            kickoff=datetime.fromisoformat(raw) if raw else None,
            source=str(player.get("_source") or "NO_SCHEDULE"),
        )


def _report(monkeypatch, tmp_path, roster, *, byes=None):
    import src.transaction_manager as tm

    monkeypatch.setattr(tm, "UtilityContext", _FakeContext)
    snapshot = {
        "snapshot_utc": "2026-10-08T23:39:07+00:00",
        "espn": {"week": 5, "season": 2026, "teams": [{"team_id": 5, "name": "Test", "roster": roster}]},
    }
    league = {"roster": {"K": 1}, "bye_weeks_2026": byes or {}}
    return _default_lineup(snapshot, league, {"weekly_manager": {}}, values_path=tmp_path / "unused.csv", team_id=5, team_name=None)


def test_confirmed_bye_k_no_schedule_reports_missing_k_not_lock_failure(monkeypatch, tmp_path):
    roster = [_player(1, "Bye kicker", "K", "K", bye=True)]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is True
    assert report["unresolved_lock_espn_ids"] == []
    assert report["missing_slots"] == ["K"]
    assert report["lock_evidence"][0]["source"] == "CONFIGURED_BYE_NO_SCHEDULE"
    assert report["lock_evidence"][0]["state"] == "UNLOCKED"
    assert _lineup_receipt(report).status == "INCOMPLETE_COVERAGE:LINEUP_MISSING_SLOTS"


def test_nonbye_no_schedule_remains_fail_closed(monkeypatch, tmp_path):
    roster = [_player(1, "Unknown kickoff", "K", "K", nfl_team="LAR")]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is False
    assert report["unresolved_lock_espn_ids"] == [1]
    assert _lineup_receipt(report).status == "INCOMPLETE_COVERAGE:LINEUP_LOCK_LEGALITY"


def test_bye_wrong_week_remains_fail_closed(monkeypatch, tmp_path):
    roster = [_player(1, "Different bye week", "K", "K", bye=False)]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 6})
    assert report["lineup_legality_complete"] is False


def test_bye_unparsed_kickoff_remains_fail_closed(monkeypatch, tmp_path):
    roster = [_player(1, "Malformed schedule", "K", "K", bye=True, source="NFLVERSE_SCHEDULE_UNPARSED")]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is False


def test_explicit_espn_lock_outranks_known_bye(monkeypatch, tmp_path):
    roster = [_player(1, "Locked bye player", "K", "K", bye=True, locked=True)]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is True
    assert report["locked_starter_espn_ids"] == [1]
    assert report["selected_espn_ids"] == [1]
    assert report["missing_slots"] == []
    assert report["lock_evidence"][0]["source"] == "ESPN_LINEUP_LOCKED"
    assert report["action_required"] is False


def test_bye_bench_cannot_fill_missing_k(monkeypatch, tmp_path):
    roster = [_player(1, "Bye kicker", "K", "BENCH", bye=True)]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is True
    assert report["missing_slots"] == ["K"]
    assert report["action_required"] is False


def test_alternative_healthy_k_can_fill_bye_slot(monkeypatch, tmp_path):
    roster = [
        _player(1, "Bye kicker", "K", "K", bye=True),
        _player(2, "Available kicker", "K", "BENCH", nfl_team="DEN", kickoff="2026-10-11T17:00:00+00:00", source="NFLVERSE_SCHEDULE"),
    ]
    report = _report(monkeypatch, tmp_path, roster, byes={"KC": 5})
    assert report["lineup_legality_complete"] is True
    assert report["missing_slots"] == []
    assert report["selected_espn_ids"] == [2]
    assert report["action_required"] is True
    assert _lineup_receipt(report).status == "PASS / ACTION"
