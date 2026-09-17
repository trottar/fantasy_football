from __future__ import annotations

import pandas as pd

from src.transaction_manager import UtilityContext, evaluate_actions, waiver_acquisition_probability


def league_cfg():
    return {
        "teams": 3,
        "roster": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
        "position_maximums": {"QB": 4, "RB": 8, "WR": 8, "TE": 3, "K": 3, "DST": 3},
        "fantasy_season": {
            "regular_season_weeks": list(range(1, 14)),
            "playoff_week_participation_prior": {"14": 0.5, "15": 0.33, "16": 0.17, "17": 0.17},
        },
        "bye_weeks_2026": {},
    }


def model_cfg():
    return {
        "weekly_manager": {
            "status_active_probability": {
                "ACTIVE": 0.995, "QUESTIONABLE": 0.75, "DOUBTFUL": 0.15, "OUT": 0.0
            }
        },
        "season_utility": {
            "active_probability_nonbye": {"QB": 0.97, "RB": 0.92, "WR": 0.94, "TE": 0.94, "K": 0.995, "DST": 1.0}
        },
        "transaction_manager": {
            "availability_scenarios": 4,
            "random_seed": 7,
            "candidate_limit": 20,
            "candidate_floor_per_position": 2,
            "replacement_available_rank": {"QB": 2, "RB": 2, "WR": 2, "TE": 2, "K": 2, "DST": 2},
            "h2h_matchup_scale_points": 18.0,
            "waiver_claim_logit_intercept": -4.0,
            "waiver_improvement_logit_per_ppg": 0.15,
            "waiver_owned_logit_per_pct": 0.015,
            "waiver_trend_logit_weight": 0.08,
            "waiver_need_logit_bonus": 0.6,
            "waiver_p_acquire_default": 0.35,
            "waiver_p_acquire_floor": 0.02,
            "opponent_roster_target": {"QB": 2, "RB": 4, "WR": 4, "TE": 2, "K": 1, "DST": 1},
        },
    }


def p(pid, name, pos, pts, status="ACTIVE", fantasy_status="ROSTERED", droppable=True, rank=20.0):
    return {
        "espn_id": pid,
        "name": name,
        "position": pos,
        "nfl_team": "X",
        "weekly_projection": pts,
        "season_projection": pts * 17,
        "injury_status": status,
        "fantasy_status": fantasy_status,
        "droppable": droppable,
        "lineup_locked": False,
        "percent_owned": rank,
    }


def base_roster(start=1):
    return [
        p(start+0, "QB A", "QB", 20), p(start+1, "QB B", "QB", 12),
        p(start+2, "RB A", "RB", 18), p(start+3, "RB B", "RB", 16), p(start+4, "RB C", "RB", 8),
        p(start+5, "WR A", "WR", 17), p(start+6, "WR B", "WR", 15), p(start+7, "WR C", "WR", 7),
        p(start+8, "TE A", "TE", 11), p(start+9, "TE B", "TE", 5),
        p(start+10, "K A", "K", 8), p(start+11, "DST A", "DST", 7),
    ]


def snapshot(user_rank=2, available=None):
    available = available or []
    return {
        "snapshot_utc": "2026-08-31T05:00:00+00:00",
        "espn": {
            "season": 2026,
            "week": 1,
            "league_name": "Test",
            "teams": [
                {"team_id": 1, "name": "Us", "waiver_rank": user_rank, "roster": base_roster(1)},
                {"team_id": 2, "name": "Them", "waiver_rank": 1, "roster": base_roster(101)},
                {"team_id": 3, "name": "Other", "waiver_rank": 3, "roster": base_roster(201)},
            ],
            "matchups": [{"week": 1, "home_team_id": 1, "away_team_id": 2}],
            "available_players": available,
        },
    }


def write_values(tmp_path, players):
    path = tmp_path / "values.csv"
    pd.DataFrame([
        {"espn_id": x[0], "latent_mean_ppg": x[1], "latent_mean_sd_ppg": 1.0, "predictive_weekly_sd_ppg": 5.0}
        for x in players
    ]).to_csv(path, index=False)
    return path


def test_clear_free_agent_upgrade_is_positive(tmp_path):
    fa = p(900, "WR Upgrade", "WR", 16, fantasy_status="FREEAGENT", rank=65)
    values = write_values(tmp_path, [(900, 16.0)])
    report = evaluate_actions(snapshot(available=[fa]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["free_agent_actions"]
    top = report["free_agent_actions"][0]
    assert top["add_name"] == "WR Upgrade"
    assert top["delta_utility"] > 0
    assert top["p_acquire"] == 1.0


def test_undroppable_player_is_never_drop_candidate(tmp_path):
    snap = snapshot(available=[p(901, "RB Upgrade", "RB", 20, fantasy_status="FREEAGENT")])
    snap["espn"]["teams"][0]["roster"][4]["droppable"] = False
    undroppable_name = snap["espn"]["teams"][0]["roster"][4]["name"]
    values = write_values(tmp_path, [(901, 20.0)])
    report = evaluate_actions(snap, league_cfg(), model_cfg(), values, team_name="Us")
    assert all(row["drop_name"] != undroppable_name for row in report["free_agent_actions"])
    assert report["legal_drop_players"] == 9  # v0.31 player channel excludes K/DST drops


def test_position_maximum_forces_same_position_drop(tmp_path):
    snap = snapshot(available=[p(902, "QB Upgrade", "QB", 21, fantasy_status="FREEAGENT")])
    # Make QB max equal current count (2). Adding a QB is legal only if a QB is dropped.
    league = league_cfg()
    league["position_maximums"]["QB"] = 2
    values = write_values(tmp_path, [(902, 21.0)])
    report = evaluate_actions(snap, league, model_cfg(), values, team_name="Us")
    assert report["free_agent_actions"]
    assert all(row["drop_position"] == "QB" for row in report["free_agent_actions"])


def test_waiver_rank_one_has_no_priority_blockers(tmp_path):
    wa = p(903, "Waiver WR", "WR", 14, fantasy_status="WAIVERS", rank=70)
    values = write_values(tmp_path, [(903, 14.0)])
    snap = snapshot(user_rank=1, available=[wa])
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    cand = next(x for x in ctx.available if x["espn_id"] == 903)
    assert waiver_acquisition_probability(cand, ctx) == 1.0


def test_lower_waiver_priority_has_probability_below_one(tmp_path):
    wa = p(904, "Waiver RB", "RB", 16, fantasy_status="WAIVERS", rank=80)
    values = write_values(tmp_path, [(904, 16.0)])
    snap = snapshot(user_rank=3, available=[wa])
    # Team 2 rank1 and user rank3 are blockers; team3 is the user? user is team1, team3 rank3 same rank ignored.
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    cand = next(x for x in ctx.available if x["espn_id"] == 904)
    p_acq = waiver_acquisition_probability(cand, ctx)
    assert 0.0 < p_acq < 1.0


def test_current_out_player_can_retain_future_season_value(tmp_path):
    snap = snapshot(available=[p(905, "Marginal RB", "RB", 9, fantasy_status="FREEAGENT")])
    # RB A is OUT this week but remains a strong latent season player.
    snap["espn"]["teams"][0]["roster"][2]["injury_status"] = "OUT"
    out_id = snap["espn"]["teams"][0]["roster"][2]["espn_id"]
    values = write_values(tmp_path, [(out_id, 18.0), (905, 9.0)])
    report = evaluate_actions(snap, league_cfg(), model_cfg(), values, team_name="Us")
    # The weak add should not make cutting the temporarily OUT star a positive season action.
    star_rows = [r for r in report["free_agent_actions"] if r["drop_espn_id"] == out_id]
    assert star_rows
    assert max(r["delta_utility"] for r in star_rows) <= 0.0

def test_one_step_action_cannot_drop_only_dst_for_bench_player(tmp_path):
    snap = snapshot(available=[p(906, "Bench QB", "QB", 22, fantasy_status="FREEAGENT")])
    values = write_values(tmp_path, [(906, 22.0)])
    report = evaluate_actions(snap, league_cfg(), model_cfg(), values, team_name="Us")
    assert all(row["drop_position"] != "DST" for row in report["free_agent_actions"])
    assert all(row["drop_position"] != "K" for row in report["free_agent_actions"])


def test_season_total_only_candidate_is_scaled_to_weekly_not_used_as_week_score(tmp_path):
    # This is the exact failure mode seen in the first live v0.21 run: an available
    # kicker season total (~153) was accidentally interpreted as Week 1 points.
    wa = p(907, "Season Total K", "K", 0, fantasy_status="WAIVERS", rank=20)
    wa["weekly_projection"] = None
    wa["season_projection"] = 153.0
    snap = snapshot(user_rank=2, available=[wa])
    values = write_values(tmp_path, [(9999, 1.0)])
    ctx = UtilityContext(snap, league_cfg(), model_cfg(), values, snap["espn"]["teams"][0])
    cand = next(x for x in ctx.available if x["espn_id"] == 907)
    assert cand["projection_points"] == 9.0
    assert cand["projection_source"] == "ESPN_SEASON_DIV17_FALLBACK"
    assert cand["season_ppg"] == 9.0


def test_v031_kicker_is_not_a_player_market_candidate(tmp_path):
    wa = p(908, "Season Total K", "K", 0, fantasy_status="WAIVERS", rank=20)
    wa["weekly_projection"] = None
    wa["season_projection"] = 153.0
    report = evaluate_actions(snapshot(user_rank=2, available=[wa]), league_cfg(), model_cfg(), write_values(tmp_path, [(9999, 1.0)]), team_name="Us")
    assert report["free_agent_actions"] == []
    assert report["waiver_actions"] == []
    assert report["market_channel"] == "PLAYER_QB_RB_WR_TE_V031"


def test_unsigned_nfl_free_agent_is_excluded_from_actions_and_replacement(tmp_path):
    unsigned = p(909, "Unsigned Star", "WR", 30, fantasy_status="WAIVERS", rank=99)
    unsigned["nfl_team"] = "FA"
    unsigned["pro_team_id"] = 0
    signed = p(910, "Signed WR", "WR", 10, fantasy_status="FREEAGENT", rank=10)
    signed["nfl_team"] = "NE"
    signed["pro_team_id"] = 17
    values = write_values(tmp_path, [(909, 30.0), (910, 10.0)])
    report = evaluate_actions(snapshot(user_rank=2, available=[unsigned, signed]), league_cfg(), model_cfg(), values, team_name="Us")
    names = {r["add_name"] for r in report["free_agent_actions"] + report["waiver_actions"]}
    assert "Unsigned Star" not in names
    assert report["available_players_excluded"] == 1
    assert report["available_players_nfl_eligible"] == 1
    assert report["excluded_available_examples"][0]["reason"] == "NFL_FREE_AGENT_UNSIGNED"
    # Replacement cannot be inflated by the unsigned player's 30 PPG latent prior.
    assert report["replacement_season"]["WR"] <= 10.0


def test_unknown_nfl_team_candidate_is_fail_safe_excluded(tmp_path):
    unknown = p(911, "Unknown Team", "RB", 25, fantasy_status="FREEAGENT", rank=80)
    unknown["nfl_team"] = None
    unknown["pro_team_id"] = None
    values = write_values(tmp_path, [(911, 25.0)])
    report = evaluate_actions(snapshot(available=[unknown]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["free_agent_actions"] == []
    assert report["available_players_excluded"] == 1
    assert report["excluded_available_examples"][0]["reason"] == "NFL_TEAM_UNKNOWN"


def test_nflverse_retired_status_excludes_stale_espn_team(tmp_path):
    retired = p(912, "Retired WR", "WR", 18, fantasy_status="WAIVERS", rank=90)
    retired["nfl_team"] = "PIT"  # stale ESPN pro team
    retired["pro_team_id"] = 23
    retired["nflverse_roster_team"] = "PIT"
    retired["nflverse_roster_status"] = "RET"
    values = write_values(tmp_path, [(912, 18.0)])
    report = evaluate_actions(snapshot(available=[retired]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["waiver_actions"] == []
    assert report["available_players_excluded"] == 1
    assert report["excluded_available_examples"][0]["reason"] == "NFLVERSE_NOT_ROSTERED_RET"


def test_nflverse_active_status_allows_candidate_and_current_team(tmp_path):
    active = p(913, "Moved WR", "WR", 16, fantasy_status="FREEAGENT", rank=70)
    active["nfl_team"] = "NE"
    active["pro_team_id"] = 17
    active["nflverse_roster_team"] = "NE"
    active["nflverse_roster_status"] = "ACT"
    values = write_values(tmp_path, [(913, 16.0)])
    report = evaluate_actions(snapshot(available=[active]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["available_players_nfl_eligible"] == 1
    assert any(r["add_name"] == "Moved WR" for r in report["free_agent_actions"])


def test_nflverse_pup_is_stash_only_not_normal_action(tmp_path):
    pup = p(914, "PUP RB", "RB", 20, fantasy_status="WAIVERS", rank=80)
    pup["nfl_team"] = "SF"
    pup["pro_team_id"] = 25
    pup["nflverse_roster_team"] = "SF"
    pup["nflverse_roster_status"] = "PUP"
    values = write_values(tmp_path, [(914, 20.0)])
    report = evaluate_actions(snapshot(available=[pup]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["waiver_actions"] == []
    assert report["excluded_available_examples"][0]["reason"] == "NFLVERSE_STASH_ONLY_PUP"


def test_nfl_official_rls_overrides_stale_nflverse_active(tmp_path):
    player = p(915, "Reserve Left Squad", "WR", 22, fantasy_status="WAIVERS", rank=80)
    player["nfl_team"] = "SF"
    player["pro_team_id"] = 25
    # nflverse can lag a same-day official roster move. NFL.com must win.
    player["nflverse_roster_team"] = "SF"
    player["nflverse_roster_status"] = "ACT"
    player["official_roster_team"] = "SF"
    player["official_roster_status"] = "RLS"
    values = write_values(tmp_path, [(915, 22.0)])
    report = evaluate_actions(snapshot(available=[player]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["waiver_actions"] == []
    assert report["available_players_excluded"] == 1
    assert report["excluded_available_examples"][0]["reason"] == "NFL_OFFICIAL_STASH_ONLY_RLS"


def test_nfl_official_active_overrides_nflverse_reserve(tmp_path):
    player = p(916, "Official Active", "RB", 18, fantasy_status="FREEAGENT", rank=70)
    player["nfl_team"] = "ARI"
    player["pro_team_id"] = 22
    player["nflverse_roster_team"] = "ARI"
    player["nflverse_roster_status"] = "RES"
    player["official_roster_team"] = "ARI"
    player["official_roster_status"] = "ACT"
    values = write_values(tmp_path, [(916, 18.0)])
    report = evaluate_actions(snapshot(available=[player]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["available_players_nfl_eligible"] == 1
    assert any(r["add_name"] == "Official Active" for r in report["free_agent_actions"])


def test_nfl_official_rsr_is_stash_only_not_unknown(tmp_path):
    player = p(917, "Designated Return RB", "RB", 18, fantasy_status="WAIVERS", rank=70)
    player["nfl_team"] = "ARI"
    player["pro_team_id"] = 22
    player["official_roster_team"] = "ARI"
    player["official_roster_status"] = "RSR"
    values = write_values(tmp_path, [(917, 18.0)])
    report = evaluate_actions(snapshot(available=[player]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["waiver_actions"] == []
    assert report["excluded_available_examples"][0]["reason"] == "NFL_OFFICIAL_STASH_ONLY_RSR"
    assert report["official_unknown_status_counts"] == {}


def test_unknown_nfl_official_status_is_counted_for_diagnostics(tmp_path):
    player = p(918, "Mystery Status", "WR", 12, fantasy_status="WAIVERS", rank=90)
    player["nfl_team"] = "NE"
    player["pro_team_id"] = 17
    player["official_roster_team"] = "NE"
    player["official_roster_status"] = "XYZ"
    values = write_values(tmp_path, [(918, 12.0)])
    report = evaluate_actions(snapshot(available=[player]), league_cfg(), model_cfg(), values, team_name="Us")
    assert report["waiver_actions"] == []
    assert report["official_unknown_status_counts"] == {"XYZ": 1}
