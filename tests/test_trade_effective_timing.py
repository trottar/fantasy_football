from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import numpy as np
import pytest

from src.trade_timing import (
    TradeTimingCoverageError,
    require_trade_settings,
    resolve_trade_timing,
    season_ppg_from_weekly,
    splice_effective_week,
)


def snapshot(review_hours=48):
    return {
        "snapshot_utc": "2026-10-05T01:26:55.901034+00:00",
        "espn": {
            "season": 2026,
            "week": 4,
            "transaction_settings": {
                "trade_review_hours": review_hours,
                "trade_veto_votes_required": 4,
                "trade_deadline_date": 1796371200000,
                "trade_max": -1,
                "lineup_locktime_type": "INDIVIDUAL_GAME",
                "roster_locktime_type": "INDIVIDUAL_GAME",
                "transaction_locking_enabled": False,
            },
        },
    }


class FakeCtx:
    def __init__(self, kickoff):
        self.kickoff = kickoff

    def lock_timing(self, player, week):
        return SimpleNamespace(kickoff=self.kickoff, source="TEST_SCHEDULE")


def player(pid=1, *, locked=False):
    return {
        "espn_id": pid,
        "name": f"P{pid}",
        "position": "RB",
        "lineup_locked": locked,
    }


def test_positive_review_window_defers_without_assuming_commissioner_override():
    class MustNotBeCalled:
        def lock_timing(self, player, week):
            raise AssertionError("review-window deferral must not require asset timing")

    result = resolve_trade_timing(
        snapshot(48), 4, [("give", player(), MustNotBeCalled())]
    )
    assert result.effective_week == 5
    assert result.current_week_effective is False
    assert result.trade_review_hours == 48
    assert result.lock_evidence == ()
    assert result.reasons == ("ESPN_TRADE_REVIEW_WINDOW_HOURS=48",)


def test_zero_review_all_unlocked_can_affect_current_week():
    result = resolve_trade_timing(
        snapshot(0),
        4,
        [("give", player(), FakeCtx(datetime.fromisoformat("2026-10-06T00:15:00+00:00")))],
    )
    assert result.effective_week == 4
    assert result.current_week_effective is True
    assert result.lock_evidence[0]["state"] == "UNLOCKED"


def test_zero_review_locked_asset_defers_to_next_week():
    result = resolve_trade_timing(
        snapshot(0),
        4,
        [("receive", player(2, locked=True), FakeCtx(None))],
    )
    assert result.effective_week == 5
    assert result.current_week_effective is False
    assert result.lock_evidence[0]["state"] == "LOCKED"


def test_zero_review_unknown_timing_fails_closed():
    with pytest.raises(TradeTimingCoverageError, match="unresolved"):
        resolve_trade_timing(
            snapshot(0), 4, [("give", player(), FakeCtx(None))]
        )


def test_missing_normalized_settings_fail_closed():
    bad = {"snapshot_utc": snapshot()["snapshot_utc"], "espn": {"week": 4}}
    with pytest.raises(TradeTimingCoverageError, match="fresh snapshot required"):
        require_trade_settings(bad)


def test_temporal_splice_preserves_current_week_and_applies_future():
    baseline = np.ones((2, 17))
    after = np.full((2, 17), 3.0)
    out = splice_effective_week(baseline, after, 5)
    assert np.array_equal(out[:, :4], baseline[:, :4])
    assert np.array_equal(out[:, 4:], after[:, 4:])
    assert np.all(out[:, 3] - baseline[:, 3] == 0.0)


def test_season_ppg_respects_current_week_and_temporal_splice():
    baseline = np.ones((2, 17))
    after = np.full((2, 17), 2.0)
    temporal = splice_effective_week(baseline, after, 5)
    league = {
        "fantasy_season": {
            "regular_season_weeks": list(range(1, 14)),
            "playoff_week_participation_prior": {
                "14": 0.5, "15": 1 / 3, "16": 1 / 6, "17": 1 / 6
            },
        }
    }
    season = season_ppg_from_weekly(temporal, league, 4)
    assert np.all(season > 1.0)
    assert np.all(season < 2.0)
