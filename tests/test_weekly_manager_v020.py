from __future__ import annotations

from src.weekly_manager import build_lineup_scenarios, optimize_lineup, resolve_team


def league_cfg():
    return {
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1}
    }


def model_cfg():
    return {
        "weekly_manager": {
            "status_active_probability": {
                "ACTIVE": 1.0,
                "QUESTIONABLE": 0.75,
                "DOUBTFUL": 0.15,
                "OUT": 0.0,
            }
        }
    }


def p(pid, name, pos, pts, status="ACTIVE"):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "projection_points": pts,
        "injury_status": status,
    }


def roster():
    return [
        p(1, "QB A", "QB", 20), p(2, "QB B", "QB", 15),
        p(3, "RB Q", "RB", 18, "QUESTIONABLE"), p(4, "RB B", "RB", 14),
        p(5, "RB C", "RB", 12), p(6, "RB D", "RB", 8),
        p(7, "WR A", "WR", 17), p(8, "WR B", "WR", 16), p(9, "WR C", "WR", 13),
        p(10, "TE A", "TE", 11), p(11, "TE B", "TE", 6),
        p(12, "K A", "K", 8), p(13, "DST A", "DST", 7),
    ]


def test_weekly_lineup_is_legal_and_uses_best_flex():
    result = optimize_lineup(roster(), league_cfg(), model_cfg())
    slots = [r["assigned_slot"] for r in result.rows]
    assert slots.count("QB") == 1
    assert slots.count("RB") == 2
    assert slots.count("WR") == 2
    assert slots.count("TE") == 1
    assert slots.count("FLEX") == 1
    assert slots.count("K") == 1
    assert slots.count("DST") == 1
    display_slots = [r["display_slot"] for r in result.rows]
    assert len(display_slots) == 9
    assert len(set(display_slots)) == 9
    assert "RB1" in display_slots and "RB2" in display_slots
    assert "WR1" in display_slots and "WR2" in display_slots
    flex = next(r for r in result.rows if r["assigned_slot"] == "FLEX")
    assert flex["name"] == "WR C"
    assert result.missing_slots == []


def test_questionable_out_contingency_reoptimizes():
    scenarios = build_lineup_scenarios(roster(), league_cfg(), model_cfg())
    q = next(x for x in scenarios["contingencies"] if x["player"] == "RB Q")
    names = {r["name"] for r in q["if_inactive"].rows}
    assert "RB Q" not in names
    assert "RB B" in names
    assert "RB C" in names


def test_resolve_team_by_name():
    snapshot = {"espn": {"teams": [
        {"team_id": 1, "name": "Other"},
        {"team_id": 2, "name": "I'm sorry Wilson!"},
    ]}}
    team = resolve_team(snapshot, team_name="I'm sorry Wilson!")
    assert team["team_id"] == 2


def test_zero_weekly_projection_falls_back_for_eligible_player(tmp_path):
    import pandas as pd
    from src.weekly_manager import enrich_roster_projections

    values = tmp_path / "values.csv"
    pd.DataFrame([{"espn_id": 99, "latent_mean_ppg": 12.5}]).to_csv(values, index=False)
    players = [{
        "espn_id": 99,
        "name": "TE Placeholder",
        "position": "TE",
        "nfl_team": "SF",
        "weekly_projection": 0.0,
        "season_projection": 170.0,
        "injury_status": "QUESTIONABLE",
    }]
    out = enrich_roster_projections(players, values, league={"bye_weeks_2026": {"SF": 8}}, week=1)
    assert out[0]["projection_points"] == 12.5
    assert out[0]["projection_source"] == "MODEL_LATENT_PPG_ZERO_FALLBACK"
    assert out[0]["espn_weekly_projection_raw"] == 0.0


def test_zero_weekly_projection_stays_zero_on_bye(tmp_path):
    from src.weekly_manager import enrich_roster_projections

    players = [{
        "espn_id": 99,
        "name": "Bye Player",
        "position": "TE",
        "nfl_team": "SF",
        "weekly_projection": 0.0,
        "season_projection": 170.0,
        "injury_status": "ACTIVE",
    }]
    out = enrich_roster_projections(players, tmp_path / "missing.csv", league={"bye_weeks_2026": {"SF": 8}}, week=8)
    assert out[0]["projection_points"] == 0.0
    assert out[0]["projection_source"] == "BYE"


def test_sleeper_status_precedes_espn_when_present():
    from src.weekly_manager import availability_status

    status, source = availability_status({
        "injury_status": "QUESTIONABLE",
        "sleeper_injury_status": "OUT",
    })
    assert status == "OUT"
    assert source == "SLEEPER"


def test_unrecognized_sleeper_injury_value_cannot_override_espn_out():
    from src.weekly_manager import active_probability, availability_status

    player = {
        "espn_id": 101,
        "injury_status": "OUT",
        "sleeper_injury_status": "NA",
    }
    status, source = availability_status(player)
    assert status == "OUT"
    assert source == "ESPN"
    assert active_probability(player, model_cfg()) == 0.0


def test_conflicting_sleeper_active_and_espn_out_resolves_conservatively():
    from src.weekly_manager import active_probability, availability_status, lineup_data_quality

    player = {
        "espn_id": 102,
        "name": "Conflict Player",
        "injury_status": "OUT",
        "sleeper_injury_status": "ACTIVE",
        "projection_source": "ESPN_WEEKLY",
        "projection_points": 15.0,
    }
    status, source = availability_status(player)
    assert status == "OUT"
    assert source == "ESPN"
    assert active_probability(player, model_cfg()) == 0.0
    warnings = lineup_data_quality([player])
    assert any("injury-status conflict" in w for w in warnings)


def test_official_status_overrides_lower_source_conflict():
    from src.weekly_manager import availability_status

    status, source = availability_status({
        "official_injury_status": "ACTIVE",
        "sleeper_injury_status": "QUESTIONABLE",
        "injury_status": "OUT",
    })
    assert status == "ACTIVE"
    assert source == "NFL_OFFICIAL"


def test_hard_out_never_enters_nominal_lineup_even_if_force_active():
    out_rb = p(99, "RB OUT", "RB", 50, "OUT")
    r = roster() + [out_rb]
    result = optimize_lineup(r, league_cfg(), model_cfg(), force_active={99}, use_expected_availability=False)
    assert "RB OUT" not in {row["name"] for row in result.rows}


def test_bye_player_is_not_a_legal_weekly_starter():
    bye_rb = p(98, "RB BYE", "RB", 50, "ACTIVE")
    bye_rb["is_bye_week"] = True
    r = roster() + [bye_rb]
    result = optimize_lineup(r, league_cfg(), model_cfg(), use_expected_availability=False)
    assert "RB BYE" not in {row["name"] for row in result.rows}


def test_nflverse_pup_roster_status_is_hard_unavailable():
    from src.weekly_manager import active_probability, availability_status

    player = {
        "espn_id": 103,
        "injury_status": "ACTIVE",
        "nflverse_availability_status": "PUP",
    }
    status, source = availability_status(player)
    assert status == "PUP"
    assert source == "NFLVERSE_ROSTER"
    assert active_probability(player, model_cfg()) == 0.0


def test_nfl_official_roster_reserve_status_is_hard_unavailable():
    from src.weekly_manager import active_probability, availability_status

    player = {
        "espn_id": 104,
        "injury_status": "ACTIVE",
        "official_roster_availability_status": "IR",
    }
    status, source = availability_status(player)
    assert status == "IR"
    assert source == "NFL_OFFICIAL_ROSTER"
    assert active_probability(player, model_cfg()) == 0.0
