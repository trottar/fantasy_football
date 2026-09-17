from __future__ import annotations

from src.data_sources.espn_league import (
    infer_scoring_period,
    normalize_available_players,
    normalize_league,
)


def player_entry(pid=10, name="Test Runner", pos=2, team=1, slot=2, status=None):
    player = {
        "id": pid,
        "fullName": name,
        "defaultPositionId": pos,
        "proTeamId": team,
        "active": True,
        "injuryStatus": "QUESTIONABLE",
        "droppable": False,
        "eligibleSlots": [2, 20, 23],
        "ownership": {"percentOwned": 90.0, "percentStarted": 50.0},
        "stats": [
            {"seasonId": 2026, "scoringPeriodId": 1, "statSplitTypeId": 1, "statSourceId": 1, "appliedTotal": 14.5},
            {"seasonId": 2026, "scoringPeriodId": 1, "statSplitTypeId": 1, "statSourceId": 0, "appliedTotal": 12.0},
            {"seasonId": 2026, "scoringPeriodId": 0, "statSplitTypeId": 0, "statSourceId": 1, "appliedTotal": 230.0},
        ],
    }
    out = {"lineupSlotId": slot, "playerPoolEntry": {"id": pid, "player": player, "lineupLocked": True, "onTeamId": 2}}
    if status is not None:
        out["status"] = status
    return out


def test_normalize_private_league_roster_and_matchup():
    payload = {
        "id": 123,
        "settings": {"name": "Hail to Pitt"},
        "status": {"currentScoringPeriod": 1, "currentMatchupPeriod": 1},
        "teams": [
            {"id": 2, "name": "I'm sorry Wilson!", "waiverRank": 4,
             "record": {"overall": {"wins": 0, "losses": 0, "ties": 0}},
             "transactionCounter": {"acquisitions": 0, "drops": 0, "trades": 0},
             "roster": {"entries": [player_entry()]}},
            {"id": 3, "name": "Opponent", "roster": {"entries": []}},
        ],
        "schedule": [{"id": 1, "matchupPeriodId": 1,
                      "home": {"teamId": 2, "totalPoints": 0},
                      "away": {"teamId": 3, "totalPoints": 0}}],
    }
    out = normalize_league(payload, 2026, 1)
    assert out["league_name"] == "Hail to Pitt"
    assert out["teams"][0]["roster"][0]["weekly_projection"] == 14.5
    assert out["teams"][0]["roster"][0]["season_projection"] == 230.0
    assert out["teams"][0]["roster"][0]["droppable"] is False
    assert out["teams"][0]["roster"][0]["lineup_locked"] is True
    assert out["teams"][0]["roster"][0]["on_team_id"] == 2
    assert out["matchups"][0]["away_team_id"] == 3
    assert infer_scoring_period(payload) == 1


def test_normalize_available_player_status():
    payload = {"players": [player_entry(status="FREEAGENT")]}
    out = normalize_available_players(payload, 2026, 1)
    assert out[0]["fantasy_status"] == "FREEAGENT"
    assert out[0]["position"] == "RB"


def test_sleeper_missing_scalar_cleanup():
    import math
    from src.season_snapshot import _clean_scalar

    assert _clean_scalar(float("nan")) is None
    assert _clean_scalar(None) is None
    assert _clean_scalar("Limited") == "Limited"


def test_available_weekly_projection_never_falls_through_to_season_total():
    entry = player_entry(pid=77, name="Season Only K", pos=5, team=11, slot=17, status="WAIVERS")
    stats = entry["playerPoolEntry"]["player"]["stats"]
    # Simulate the live kona available-player case that exposed v0.21: ESPN returns
    # a projected season aggregate but no exact current-week split row.
    entry["playerPoolEntry"]["player"]["stats"] = [
        s for s in stats if int(s.get("statSplitTypeId", -1)) == 0
    ]
    entry["playerPoolEntry"]["player"]["stats"][0]["appliedTotal"] = 153.0
    out = normalize_available_players({"players": [entry]}, 2026, 1)[0]
    assert out["weekly_projection"] is None
    assert out["season_projection"] == 153.0


def test_season_projection_never_uses_weekly_split_when_aggregate_missing():
    entry = player_entry(pid=78, name="Week Only", pos=3, team=11, slot=4, status="FREEAGENT")
    entry["playerPoolEntry"]["player"]["stats"] = [
        {"seasonId": 2026, "scoringPeriodId": 1, "statSplitTypeId": 1,
         "statSourceId": 1, "appliedTotal": 12.5}
    ]
    out = normalize_available_players({"players": [entry]}, 2026, 1)[0]
    assert out["weekly_projection"] == 12.5
    assert out["season_projection"] is None
