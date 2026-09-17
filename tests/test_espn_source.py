from src.data_sources.espn import normalize_espn_players


def test_normalize_espn_players():
    payload = {
        "players": [{
            "id": 123,
            "player": {
                "fullName": "Test Receiver",
                "defaultPositionId": 3,
                "proTeamId": 23,
                "active": True,
                "injuryStatus": "ACTIVE",
                "ownership": {
                    "averageDraftPosition": 22.5,
                    "percentOwned": 99.1,
                    "percentStarted": 88.0,
                },
                "draftRanksByRankType": {
                    "PPR": {"rank": 18}
                },
            },
            "playerPoolEntry": {
                "stats": [{
                    "seasonId": 2026,
                    "scoringPeriodId": 0,
                    "statSourceId": 1,
                    "statSplitTypeId": 0,
                    "appliedTotal": 250.4,
                }]
            }
        }]
    }
    df = normalize_espn_players(payload, season=2026)
    row = df.iloc[0]
    assert int(row["espn_id"]) == 123
    assert row["position"] == "WR"
    assert row["nfl_team"] == "PIT"
    assert row["espn_adp"] == 22.5
    assert row["espn_rank"] == 18
    assert row["espn_proj_points"] == 250.4


def test_projection_prefers_projected_season_total():
    payload = {
        "players": [{
            "id": 456,
            "player": {
                "fullName": "Projection Test",
                "defaultPositionId": 2,
                "proTeamId": 8,
                "stats": [
                    {
                        "seasonId": 2026,
                        "scoringPeriodId": 1,
                        "statSourceId": 1,
                        "statSplitTypeId": 1,
                        "appliedTotal": 18.5,
                    },
                    {
                        "seasonId": 2026,
                        "scoringPeriodId": 0,
                        "statSourceId": 1,
                        "statSplitTypeId": 0,
                        "appliedTotal": 287.2,
                    },
                    {
                        "seasonId": 2026,
                        "scoringPeriodId": 0,
                        "statSourceId": 0,
                        "statSplitTypeId": 0,
                        "appliedTotal": 999.0,
                    },
                ],
            },
        }]
    }
    df = normalize_espn_players(payload, season=2026)
    assert df.iloc[0]["espn_proj_points"] == 287.2
